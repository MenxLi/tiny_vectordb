from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal
from .vector_collection import VectorCollectionAbstract, NumVar, _VectorCollectionEncodingAbstract, CollectionChanges
import base64
import numpy as np

if TYPE_CHECKING:
    from .wrap import VectorDatabase


np_dtype = np.float32
class _VectorCollectionEncoding_Numpy(_VectorCollectionEncodingAbstract[NumVar]):
    def encode(self, vectors: list[NumVar]) -> str:
        return base64.b64encode(bytes(
            np.array(vectors, dtype=np_dtype)
        )).decode()
    def decode(self, enc_vectors: str) -> list[NumVar]:
        return list(np.frombuffer(base64.b64decode(enc_vectors), dtype=np_dtype))

class VectorCollection_Numpy(VectorCollectionAbstract[NumVar]):
    def __init__(
            self, parent: Optional[VectorDatabase],
            name: str,
            dimension: int,
            **_
            ):
        self.__name = name
        self.__database = parent
        self._dimension = dimension
        self._ids: np.ndarray = np.array([], dtype = np_dtype)                # dim: (n, dimension)
        self._vec: np.ndarray = np.array([], dtype=str)     # dim: (n, )

        self._changes: dict[str, Literal["ADD", "DELETE", "UPDATE"]] = {}

        self._encoding = _VectorCollectionEncoding_Numpy[NumVar]()

    @property
    def name(self):
        return self.__name
    @property
    def database(self):
        return self.__database
    @property
    def encoding(self) -> _VectorCollectionEncoding_Numpy[NumVar]:
        return self._encoding
    @property
    def dim(self) -> int:
        return self._dimension
    
    def addBlock(self, ids: list[str], vectors: list[list[NumVar]]):
        """
        Add a bulk of elements, will raise error if id exists
        """
        if len(ids) != len(vectors):
            raise ValueError("Length of ids and vectors not match")
        if len(ids) == 0:
            return
        
        # make sure all ids are unique
        if len(ids) != len(set(ids)):
            raise ValueError("Ids are not unique")

        np_ids = np.array(ids, dtype=str)
        np_vectors = np.array(vectors, dtype=np_dtype)

        # make sure all ids are not exists
        if np.isin(self._ids, np_ids).any():
            raise ValueError("Some ids already exists")
        
        if len(self) == 0:
            self._ids = np_ids
            self._vectors = np_vectors
        else:
            self._ids = np.concatenate([self._ids, np_ids])
            self._vectors = np.concatenate([self._vectors, np_vectors])

        # log modifications
        for id in ids:
            if id in self._changes and self._changes[id] == "DELETE":
                self._changes[id] = "UPDATE"
            else:
                self._changes[id] = "ADD"

    def deleteBlock(self, ids: list[str]) -> None:
        """
        Delete a bulk of elements, will raise error if id not exists
        """
        if len(ids) == 0:
            return
        if len(ids) > len(self):
            raise ValueError("Length of ids to delete is larger than length of collection")
        
        np_ids = np.array(ids, dtype=str)

        # make sure all ids exists in self._ids
        if not np.isin(np_ids, self._ids).all():
            raise ValueError("Some ids not exists")

        mask = np.ones(len(self), dtype=bool)
        mask[np.isin(self._ids, np_ids)] = False
    
        self._ids = self._ids[mask]
        self._vectors = self._vectors[mask]

        # log modifications
        for id in ids:
            if id in self._changes and self._changes[id] == "ADD":
                # if id is added and then deleted, remove it from changes
                del self._changes[id]
            else:
                self._changes[id] = "DELETE"

    def setBlock(self, ids: list[str], vectors: list[list[NumVar]]) -> None:
        """
        For every element in ids, set the corresponding vector
        Add if not exists, update if exists
        """
        if len(ids) != len(vectors):
            raise ValueError("Length of ids and vectors not match")
        if len(ids) == 0:
            return

        np_ids = np.array(ids)
        np_vectors = np.array(vectors, dtype = np_dtype)

        # update
        mask = np.isin(self._ids, np_ids)
        self._ids[mask] = np_ids
        self._vectors[mask] = np_vectors
        # log modifications
        for id in np_ids[mask]:
            if id in self._changes and self._changes[id] == "ADD":
                # if id is added and then updated, keep it as "ADD"
                continue
            self._changes[id] = "UPDATE"

        # add
        mask = ~mask
        self._ids = np.concatenate([self._ids, np_ids[mask]])
        self._vectors = np.concatenate([self._vectors, np_vectors[mask]])
        # log modifications
        for id in np_ids[mask]:
            if id in self._changes and self._changes[id] == "DELETE":
                # if id is deleted and then updated, remove it from changes
                del self._changes[id]
            else:
                self._changes.update({id: "UPDATE"})

    def update(self, id: str, vector: list[NumVar]) -> bool:
        """
        Change a vector, will raise error if id not exists
        """
        if not self.has(id):
            return False
        self._vectors[self._ids == id] = np.array(vector, dtype = np_dtype)
        # log modifications
        if id in self._changes and self._changes[id] == "ADD":
            # if id is added and then updated, keep it as "ADD"
            pass
        else:
            self._changes[id] = "UPDATE"
        return True
    
    def has(self, id: str) -> bool:
        """
        Check if id exists
        """
        return bool(np.isin(self._ids, np.array([id])).any())
    
    def keys(self) -> list[str]:
        """
        Return all ids in this collection
        """
        return self._ids.tolist()
    
    def get(self, id: str) -> list[NumVar]:
        """
        Get a vector by id, will raise error if id not exists
        """
        if not self.has(id):
            return []
        return self._vectors[self._ids == id][0].tolist()
    
    def getBlock(self, ids: list[str]) -> list[list[NumVar]]:
        """
        Get a bulk of vectors by ids, will raise error if any id not exists
        """
        if len(ids) == 0:
            return []
        if len(ids) > len(self):
            raise ValueError("Length of ids to get is larger than length of collection")
        if not all(self.has(id) for id in ids):
            raise ValueError("Some ids not exists")

        return self._vectors[np.isin(self._ids, np.array(ids))].tolist()
    
    def search(self, query: list[NumVar], k: int = -1) -> tuple[list[str], list[float]]:
        """
        Search for top-k vectors, return ids and scores
        """
        query_np = np.array(query, dtype = np_dtype)
        scores = np.dot(self._vectors, query_np) / (np.linalg.norm(self._vectors, axis=1) * np.linalg.norm(query_np))
        if k == -1:
            k = len(self)
            
        topk_indices = np.argsort(scores)[::-1][:k]
        return self._ids[topk_indices].tolist(), scores[topk_indices].tolist()
    
    def load(self, ids: list[str], enc_vectors: list[str]) -> None:
        """
        Load a bulk of elements, should be called when the collection is empty
        """
        if len(self) != 0:
            raise RuntimeError("Collection is not empty, cannot load data")
        vectors = np.zeros(shape = (len(ids), self._dimension))
        for i, enc_vector in enumerate(enc_vectors):
            vectors[i] = self.encoding.decode(enc_vector)
        self._ids = np.array(ids)
        self._vectors = vectors
    
    def loadFromDisk(self) -> None:
        """
        Load all data of the collection from disk, 
        Should be called when the collection is attached to a database and is empty
        """
        if not self.database:
            return 
        ids, enc_vectors = self.database.disk_io.getTableData(self.name)
        self.load(ids, enc_vectors)

    def flush(self) -> CollectionChanges:
        """
        Load all changes to sqlite database memory, but not save to disk,
        If the collection is not attached to a database, return False
        """
        # gather changes
        changes: CollectionChanges = {
            "ADD": ([], []),
            "UPDATE": ([], []),
            "DELETE": ([], None)
        }
        for id, change_type in self._changes.items():
            if change_type == "ADD":
                changes["ADD"][0].append(id)
                changes["ADD"][1].append(self.encoding.encode(self._vectors[self._ids == id][0]))
            elif change_type == "UPDATE":
                changes["UPDATE"][0].append(id)
                changes["UPDATE"][1].append(self.encoding.encode(self._vectors[self._ids == id][0]))
            elif change_type == "DELETE":
                changes["DELETE"][0].append(id)
            else:
                raise RuntimeError(f"Unknown change type {change_type}")
        
        self._changes = {}  # reset

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
        return len(self._ids)

    def __getitem__(self, id: str) -> Optional[list[NumVar]]:
        return self.get(id)