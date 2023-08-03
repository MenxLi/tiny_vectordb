from __future__ import annotations
from typing import Union, TypeVar, Generic, Optional, TypedDict, Optional
from .jit import BIN_DIR, compile
import sys
from importlib import import_module
from .diskio import SqliteIO

Number = Union[int, float]
NumVar = TypeVar('NumVar', int, float)


class CollectionConfig(TypedDict):
    name: str
    dimension: int

class VectorDatabase:
    VERBOSE = False
    def __init__(self, path: str, collection_configs: list[CollectionConfig]):
        self._collections: dict[str, VectorCollection] = {}
        self.__disk_io = SqliteIO(path)
        for config in collection_configs:
            self._collections[config['name']] = VectorCollection(self, quite_loading=not self.VERBOSE, **config)
        self._initCollections()
    
    @property
    def disk_io(self):
        return self.__disk_io
    
    def _initCollections(self) -> bool:
        """Load collection from disk if exists"""
        table_names = self.disk_io.getTableNames()
        collection_name = self.getCollectionNames()
        for name in collection_name:
            if table_names.__contains__(name):
                self.getCollection(name).loadFromDisk()
            self.disk_io.touchTable(name)
    
    def __getitem__(self, name: str) -> VectorCollection:
        return self.getCollection(name)
    
    def __len__(self) -> int:
        return len(self._collections)

    def getCollection(self, name: str) -> VectorCollection:
        return self._collections[name]
    
    def getCollectionNames(self) -> list[str]:
        return list(self._collections.keys())
    
    def flush(self):
        """Flush all changes to sqlite database"""
        for collection in self._collections.values():
            collection.flush()
    
    def commit(self):
        """Save all changes to disk"""
        self.disk_io.commit()

class VectorCollection(Generic[NumVar]):

    def __init__(self, parent: Optional[VectorDatabase], name: str, dimension: int, quite_loading = True):
        """
        set parent to None if you don't want to save changes to disk
        """
        if not sys.path.__contains__(BIN_DIR):
            if not quite_loading:
                print("Adding", BIN_DIR, "to sys.path")
            sys.path.append(BIN_DIR)
        _m_name = compile(dimension, quite = quite_loading)

        self.__name = name
        self.__database = parent
        self.__clib = import_module(_m_name)
        self.__impl = self.__clib.VectorCollectionImpl()
    
    @property
    def name(self):
        return self.__name
    @property
    def database(self):
        return self.__database
    @property
    def clib(self):
        return self.__clib
    @property
    def _impl(self):
        return self.__impl
    
    def addBulk(self, ids: list[str], vectors: list[list[NumVar]]):
        self._impl.addBulk(ids, vectors)
    
    # def insert(self, id: str, vector: list[NumVar]) -> bool:
    #     # maybe delete this method
    #     self._impl.addBulk([id], [vector])
    
    def has(self, id: str) -> bool:
        return self._impl.has(id)
    
    def update(self, id: str, vector: list[NumVar]) -> bool:
        return self._impl.set(id, vector)

    def get(self, id: str) -> Optional[list[NumVar]]:
        ret = self._impl.get(id)
        if ret:
            return ret
        else:
            return None

    def search(self, query: list[NumVar], k: int = -1) -> tuple[list[str], list[float]]:
        """Return a tuple of (ids, scores)"""
        return self._impl.search(query, k)

    def all(self) -> tuple[list[str], list[list[NumVar]]]:
        ...
    
    def deleteBulk(self, ids: list[str]) -> None:
        self._impl.deleteBulk(ids)
    
    def loadFromDisk(self) -> None:
        if not self.database:
            return 
        ids, enc_vectors = self.database.disk_io.getTableData(self.name)
        self._impl.addRawEncBulk(ids, enc_vectors)

    def flush(self) -> bool:
        chages = self._impl.flush()
        if not self.database:
            return 
        ids_add, enc_vectors_add = chages["ADD"]
        for identifier, enc_vector in zip(ids_add, enc_vectors_add):
            self.database.disk_io.insetToTable(self.name, identifier, enc_vector)
        for identifier in chages["DELETE"][0]:
            self.database.disk_io.deleteFromTable(self.name, identifier)
        ids_update, enc_vectors_update = chages["UPDATE"]
        for identifier, enc_vector in zip(ids_update, enc_vectors_update):
            self.database.disk_io.updateTable(self.name, identifier, enc_vector)

    def __len__(self) -> int:
        return self._impl.size()
    
    def __getitem__(self, id: str) -> Optional[list[NumVar]]:
        return self.get(id)
    