import sqlite3
from threading import Lock

def lockRequire(lock):
    def _func(func):
        def wrapper(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()
        return wrapper
    return _func

class SqliteIO:
    _lock = Lock()

    def __init__(self, fpath: str) -> None:
        self.conn = sqlite3.connect(fpath)
        self.cur = self.conn.cursor()
    
    @lockRequire(_lock)
    def touchTable(self, name: str) -> None:
        # create if not exists, save string
        self.cur.execute(f"CREATE TABLE IF NOT EXISTS {name} (id TEXT PRIMARY KEY, vector TEXT)")
    
    @lockRequire(_lock)
    def deleteTable(self, name: str) -> None:
        # delete table
        self.cur.execute(f"DROP TABLE {name}")

    def getTableNames(self) -> list[str]:
        # get all table names
        ret = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [i[0] for i in ret]
    
    def getTableData(self, name: str) -> tuple[list[str], list[str]]:
        # get all data in table
        res = self.cur.execute(f"SELECT * FROM {name}")
        ret = ([], [])
        for i in res:
            ret[0].append(i[0])
            ret[1].append(i[1])
        return ret

    @lockRequire(_lock)
    def insetToTable(self, name: str, id: str, enc_vector: str) -> None:
        # insert one row to table, make sure id not exists
        self.cur.execute(f"INSERT INTO {name} VALUES (?, ?)", (id, enc_vector))
    
    @lockRequire(_lock)
    def updateTable(self, name: str, id: str, enc_vector: str) -> None:
        # update one row to table, make sure id exists
        self.cur.execute(f"UPDATE {name} SET vector = ? WHERE id = ?", (enc_vector, id))
    
    @lockRequire(_lock)
    def deleteFromTable(self, name: str, id: str) -> None:
        # delete one row from table, make sure id exists
        self.cur.execute(f"DELETE FROM {name} WHERE id = ?", (id,))
    
    @lockRequire(_lock)
    def commit(self):
        self.conn.commit()