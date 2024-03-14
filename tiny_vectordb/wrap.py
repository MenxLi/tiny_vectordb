from __future__ import annotations
import os
from typing import Union, TypeVar, Optional, TypedDict, Optional
from .jit import ensureEigen
from .vector_collection import VectorCollection_CXX, VectorCollectionAbstract
from .numpy_impl import VectorCollection_Numpy
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

class VectorDatabase(dict[str, "VectorCollectionAbstract[float]"]):
    VERBOSE: bool = False
    def __init__(self, path: str, collection_configs: list[CollectionConfig], compile_config: Optional[CompileConfig] = None):
        super().__init__()
        self.__database_path = path
        self.__disk_io = SqliteIO(path)
        for config in collection_configs:
            self[config['name']] = getVectorCollectionBackend()(
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
    
    def getCollection(self, name: str) -> VectorCollectionAbstract:
        return self[name]
    
    def getCollectionNames(self) -> list[str]:
        return list(self.keys())
    
    def createCollection(self, collection_config: CollectionConfig) -> VectorCollectionAbstract:
        """ Insert a new collection to database and create a new table in sqlite database """
        _name = collection_config["name"]
        assert not self.keys().__contains__(_name), f"Collection '{_name}' already exists"
        self[_name] = getVectorCollectionBackend()(self, quite_loading=not self.VERBOSE, **collection_config)
        self.disk_io.touchTable(_name)
        return self[_name]
    
    def deleteCollection(self, name: str):
        assert self.keys().__contains__(name), f"Collection '{name}' not exists"
        del self[name]
        self.disk_io.deleteTable(name)

    def commit(self):
        """
        Commit all changes to sqlite database and commit
        """
        for collection in self.values():
            collection.flush()
        self.disk_io.commit()


def getVectorCollectionBackend(backend: str = "") -> type[VectorCollectionAbstract[NumVar]]:
    if not backend:
        __backend = os.getenv("TVDB_BACKEND", 'cxx').lower()
    else:
        __backend = backend.lower()
    
    if __backend == "cxx" or __backend=="jit":
        ensureEigen()
        return VectorCollection_CXX[NumVar]

    elif __backend == "numpy" or __backend == "np":
        return VectorCollection_Numpy[NumVar]

    else:
        raise RuntimeError("Unknown backend")