from __future__ import annotations
from typing import Union, TypeVar, Generic, Optional
from .jit import BIN_DIR, compile
import sys
from importlib import import_module

Number = Union[int, float]
NumVar = TypeVar('NumVar', int, float)

class VectorDatabase:

    def __init__(self, path: str):
        ...

    def createCollection(self, name: str, dimension: int):
        ...
    
    def getCollection(self, collection: str) -> VectorCollection:
        ...
    
    def getCollectionNames(self) -> list[str]:
        ...
    
    def flush(self):
        """Save all changes to disk"""
        ...

class VectorCollection(Generic[NumVar]):

    def __init__(self, name: str, dimension: int, quite_loading = True):
        if not sys.path.__contains__(BIN_DIR):
            if not quite_loading:
                print("Adding", BIN_DIR, "to sys.path")
            sys.path.append(BIN_DIR)
        _m_name = compile(dimension, quite = quite_loading)

        self.__clib = import_module(_m_name)
        self.__impl = self.__clib.VectorCollectionImpl()
    
    @property
    def clib(self):
        return self.__clib

    @property
    def _impl(self):
        return self.__impl
    
    def addBulk(self, ids: list[str], vectors: list[list[NumVar]]):
        self._impl.addBulk(ids, vectors)
    
    def insert(self, id: str, vector: list[NumVar]) -> bool:
        # maybe delete this method
        self._impl.addBulk([id], [vector])
    
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

    def query(self, vector: list[NumVar], k: int = -1) -> tuple[list[str], list[float]]:
        """Return a tuple of (ids, distances)"""
        ...
    
    def all(self) -> tuple[list[str], list[list[NumVar]]]:
        ...
    
    def deleteBulk(self, ids: list[str]) -> None:
        self._impl.deleteBulk(ids)
    
    def flush(self) -> bool:
        ...

    def __len__(self) -> int:
        return self._impl.size()
    
    def __getitem__(self, id: str) -> Optional[list[NumVar]]:
        return self.get(id)
    