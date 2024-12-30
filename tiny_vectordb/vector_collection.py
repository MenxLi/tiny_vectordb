
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, TYPE_CHECKING, Any, TypedDict
from .jit import compile
from .jit_utils import autoCompileConfig
from .config import BIN_DIR
import sys
import importlib

if TYPE_CHECKING:
    from .wrap import VectorDatabase, CompileConfig


NumVar = TypeVar('NumVar', int, float)
class CollectionChanges(TypedDict):
    ADD: tuple[list[str], list[str]]
    UPDATE: tuple[list[str], list[str]]
    DELETE: tuple[list[str], None]
class _VectorCollectionEncodingAbstract(Generic[NumVar]):
    def encode(self, vectors: list[NumVar]) -> str:...
    def decode(self, enc_vectors: str) -> list[NumVar]:...
class VectorCollectionAbstract(ABC, Generic[NumVar]):
    @abstractmethod
    def __init__(
            self, parent: Optional[VectorDatabase], 
            name: str, 
            dimension: int, 
            quite_loading = True, 
            compile_config: Optional[CompileConfig] = None
            ):
        ...
    
    @property
    @abstractmethod
    def name(self)->str:...
    @property
    def database(self)->Optional[VectorDatabase]:...
    @property
    def _impl(self)->Any:...
    @property
    def encoding(self) -> _VectorCollectionEncodingAbstract[NumVar]:...
    @property
    def dim(self) -> int:...
    def addBlock(self, ids: list[str], vectors: list[list[NumVar]]):...
    def deleteBlock(self, ids: list[str]) -> None:...
    def setBlock(self, ids: list[str], vectors: list[list[NumVar]]) -> None:...
    def update(self, id: str, vector: list[NumVar]) -> bool:...
    def has(self, id: str) -> bool:...
    def keys(self) -> list[str]:...
    def get(self, id: str) -> list[NumVar]:...
    def getBlock(self, ids: list[str]) -> list[list[NumVar]]:...
    def search(self, query: list[NumVar], k: int = -1) -> tuple[list[str], list[float]]:...
    def loadFromDisk(self) -> None:...
    def load(self, ids: list[str], enc_vectors: list[str]) -> None:...
    def flush(self) -> CollectionChanges:...
    def __len__(self) -> int:...
    def __getitem__(self, id: str) -> Optional[list[NumVar]]:...


class _VectorCollectionEncoding(VectorCollectionAbstract[NumVar]):
    def encode(self, vector: list[NumVar]) -> str: ...
    def decode(self, enc_vector: str) -> list[NumVar]: ...

class VectorCollection_CXX(VectorCollectionAbstract[NumVar]):
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
            compile_config = autoCompileConfig()

        self._dimension = dimension

        _m_name = compile(dimension, quite = quite_loading, **compile_config)
        self.__clib = importlib.import_module(_m_name)
        # force reload
        # importlib.reload(self.__clib)
        self.__impl = self.__clib.VectorCollectionImpl()
        if not quite_loading:
            print("\033[1;30m", end="\r")
            print(f"[[ Loaded {_m_name} from {BIN_DIR} ]]")
            print("\033[0m", end="\r")

        self.__name = name
        self.__database = parent
    
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
    @property
    def dim(self) -> int:
        assert self._dimension == self.clib.FEAT_DIM, "Dimension mismatch"
        return self._dimension
    
    def addBlock(self, ids: list[str], vectors: list[list[NumVar]]):
        """
        Add a bulk of elements, will raise error if id exists
        """
        # debug.
        for id, vector in zip(ids, vectors):
            assert len(vector) == self._dimension, f"Vector dimension mismatch, expected {self._dimension}, got {len(vector)}"

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
    
    def load(self, ids: list[str], enc_vectors: list[str]) -> None:
        """
        Load a bulk of elements, should be called when the collection is empty
        """
        if len(self) != 0:
            raise RuntimeError("Collection is not empty, cannot load data")
        self._impl.addRawEncBulk(ids, enc_vectors)
    
    def loadFromDisk(self) -> None:
        """
        Load all data of the collection from disk, 
        Should be called when the collection is attached to a database and is empty
        """
        if not self.database: return 
        ids, enc_vectors = self.database.disk_io.getTableData(self.name)
        self.load(ids, enc_vectors)

    def flush(self) -> CollectionChanges:
        """
        Load all changes to sqlite database memory, but not save to disk,
        If the collection is not attached to a database, return False
        """
        changes: CollectionChanges = self._impl.flush()
        if not self.database:
            return changes
        ids_add, enc_vectors_add = changes["ADD"]
        for identifier, enc_vector in zip(ids_add, enc_vectors_add):
            self.database.disk_io.insetToTable(self.name, identifier, enc_vector)
        ids_update, enc_vectors_update = changes["UPDATE"]
        for identifier, enc_vector in zip(ids_update, enc_vectors_update):
            self.database.disk_io.updateTable(self.name, identifier, enc_vector)
        for identifier in changes["DELETE"][0]:
            self.database.disk_io.deleteFromTable(self.name, identifier)
        return changes

    def __len__(self) -> int:
        return self._impl.size()
    
    def __getitem__(self, id: str) -> Optional[list[NumVar]]:
        return self.get(id)