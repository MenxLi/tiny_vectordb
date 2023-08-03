import sqlite3
from typing import TYPE_CHECKING, Generic, TypeVar
if TYPE_CHECKING:
    from .wrap import VectorCollection

NumT = TypeVar('NumT', float, int)
class SqliteIO(Generic[NumT]):

    def __init__(self, fpath: str) -> None:
        self.conn = sqlite3.connect(fpath)
        self.cur = self.conn.cursor()
    
    def touchTable(self, name: str, dimension: int) -> None:
        # create if not exists, blob type vector
        ...

    def getTableNames(self) -> list[str]:
        # get all table names
        ret = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [i[0] for i in ret]
    
    def getTableData(self, name: str) -> tuple[list[str], list[NumT]]:
        ...

    def insetToTable(self, name: str, id: str, vector: list[NumT]) -> None:
        ...
    
    def updateTable(self, name: str, id: str, vector: list[NumT]) -> None:
        ...
    
    def deleteFromTable(self, name: str, id: str) -> None:
        # delete one row from table, make sure id exists
        self.cur.execute(f"DELETE FROM {name} WHERE id = ?", (id,))
    
    def commit(self):
        self.conn.commit()

def list2bin(ls: list[float]) -> bytes:
    ...

def bin2list(b: bytes) -> list:
    ...
    
    