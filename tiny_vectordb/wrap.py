from __future__ import annotations
from typing import Union, TypeVar, Generic, Optional, TypedDict, Optional
from .jit import compile
from .config import BIN_DIR
import sys
from importlib import import_module
from .diskio import SqliteIO

Number = Union[int, float]
NumVar = TypeVar('NumVar', int, float)


class CollectionConfig(TypedDict):
    name: str
    dimension: int

class CompileConfig(TypedDict):
    cxx: str
    additional_compile_flags: list[str]
    additional_link_flags: list[str]

class VectorDatabase(dict[str, "VectorCollection[float]"]):
    VERBOSE: bool = False
    def __init__(self, path: str, collection_configs: list[CollectionConfig], compile_config: Optional[CompileConfig] = None):
        super().__init__()
        self.__database_path = path
        self.__disk_io = SqliteIO(path)
        for config in collection_configs:
            self[config['name']] = VectorCollection[float](
                self, 
                quite_loading=not self.VERBOSE, 
                compile_config=compile_config, 
                **config
                )
        self.__initCollections()
    
    def __initCollections(self):
        """Load collection from disk if exists"""
        table_names = self.disk_io.getTableNames()
        assert set(table_names).issubset(set(self.keys())), \
        f"Database corrupted, existing tables: {table_names}, but only specified collections of: {self.keys()}"
        for name in self.keys():
            if table_names.__contains__(name):
                self.getCollection(name).loadFromDisk()
            self.disk_io.touchTable(name)

    @property
    def disk_io(self):
        return self.__disk_io
    
    @property
    def database_path(self):
        return self.__database_path
    
    def getCollection(self, name: str) -> VectorCollection:
        return self[name]
    
    def getCollectionNames(self) -> list[str]:
        return list(self.keys())
    
    def createCollection(self, collection_config: CollectionConfig) -> VectorCollection:
        """ Insert a new collection to database and create a new table in sqlite database """
        _name = collection_config["name"]
        assert not self.keys().__contains__(_name), f"Collection '{_name}' already exists"
        self[_name] = VectorCollection(self, quite_loading=not self.VERBOSE, **collection_config)
        self.disk_io.touchTable(_name)
        return self[_name]
    
    def deleteCollection(self, name: str):
        assert self.keys().__contains__(name), f"Collection '{name}' not exists"
        del self[name]
        self.disk_io.deleteTable(name)

    def flush(self):
        """
        Flush all changes to sqlite database, but not commit
        """
        for collection in self.values():
            collection.flush()
    
    def commit(self):
        """
        Save all changes to disk
        """
        self.disk_io.commit()

class _VectorCollectionEncoding(Generic[NumVar]):
    def encode(self, vector: list[NumVar]) -> str: ...
    def decode(self, enc_vector: str) -> list[NumVar]: ...

class VectorCollection(Generic[NumVar]):
    COMPILE_CONFIG: CompileConfig = {
        "cxx": "g++",
        "additional_compile_flags": [],     # "-march=native", "-mtune=native",
        "additional_link_flags": []
    }

    def __init__(
            self, parent: Optional[VectorDatabase], 
            name: str, 
            dimension: int, 
            quite_loading = True, 
            compile_config: Optional[CompileConfig] = None
            ):
        """
        set parent to None if you don't want to save changes to disk
        """
        if not sys.path.__contains__(BIN_DIR):
            if not quite_loading:
                print("Adding", BIN_DIR, "to sys.path")
            sys.path.append(BIN_DIR)
        if compile_config is None:
            compile_config = self.__class__.COMPILE_CONFIG

        _m_name = compile(dimension, quite = quite_loading, **compile_config)
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
    @property
    def encoding(self) -> _VectorCollectionEncoding[NumVar]:
        return self.__clib.enc
    
    def addBlock(self, ids: list[str], vectors: list[list[NumVar]]):
        """
        Add a bulk of elements, will raise error if id exists
        """
        self._impl.addBulk(ids, vectors)
    
    def deleteBlock(self, ids: list[str]) -> None:
        """
        Delete a bulk of elements, will raise error if id not exists
        """
        self._impl.deleteBulk(ids)
    
    def setBlock(self, ids: list[str], vectors: list[list[NumVar]]) -> None:
        """
        For every element in ids, set the corresponding vector
        Add if not exists, update if exists
        """
        self._impl.setBulk(ids, vectors)

    def update(self, id: str, vector: list[NumVar]) -> bool:
        """
        Change a vector, will raise error if id not exists
        """
        return self._impl.set(id, vector)

    def has(self, id: str) -> bool:
        """
        Check if id exists
        """
        return self._impl.has(id)
    
    def keys(self) -> list[str]:
        """
        Return all ids in this collection
        """
        return self._impl.getAllIds()

    def get(self, id: str) -> list[NumVar]:
        """
        Get a vector by id, return an empty list if not exists
        """
        return self._impl.get(id)
    
    def getBlock(self, ids: list[str]) -> list[list[NumVar]]:
        """
        Get a bulk of vectors by ids, return list element can be empty if not exists
        """
        return self._impl.getBulk(ids)
    
    def search(self, query: list[NumVar], k: int = -1) -> tuple[list[str], list[float]]:
        """Return a tuple of (ids, scores)"""
        return self._impl.search(query, k)
    
    def loadFromDisk(self) -> None:
        """
        Load all data of the collection from disk, 
        Should be called when the collection is attached to a database and is empty
        """
        if not self.database:
            return 
        if len(self) != 0:
            raise RuntimeError("Collection is not empty, cannot load from disk")
        
        ids, enc_vectors = self.database.disk_io.getTableData(self.name)
        self._impl.addRawEncBulk(ids, enc_vectors)

    def flush(self) -> bool:
        """
        Load all changes to sqlite database memory, but not save to disk,
        If the collection is not attached to a database, return False
        """
        changes = self._impl.flush()
        if not self.database:
            return False
        ids_add, enc_vectors_add = changes["ADD"]
        for identifier, enc_vector in zip(ids_add, enc_vectors_add):
            self.database.disk_io.insetToTable(self.name, identifier, enc_vector)
        ids_update, enc_vectors_update = changes["UPDATE"]
        for identifier, enc_vector in zip(ids_update, enc_vectors_update):
            self.database.disk_io.updateTable(self.name, identifier, enc_vector)
        for identifier in changes["DELETE"][0]:
            self.database.disk_io.deleteFromTable(self.name, identifier)
        return True

    def __len__(self) -> int:
        return self._impl.size()
    
    def __getitem__(self, id: str) -> Optional[list[NumVar]]:
        return self.get(id)
    