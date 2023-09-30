import os
import numpy as np
from tiny_vectordb import VectorDatabase

LEN = 16
N = 16

VectorDatabase.VERBOSE = True
if os.path.exists("test.db"):
    raise FileExistsError("test.db already exists")
database = VectorDatabase("test.db", [{ "name": "test", "dimension": LEN, }])
collection = database.getCollection("test")
if not collection.has("-1"):
    collection.addBlock(["-1"], [[float(x) for x in range(LEN)]])

np.random.seed(0)
vectors = np.random.rand(N, LEN).tolist()
ids = [str(x) for x in range(N)]

collection.addBlock(ids, vectors)

query = [float(x) for x in range(LEN)]
target = vectors
assert collection.has("-1")
assert collection.get("-1") == [float(x) for x in range(LEN)]

assert not collection.get("100")

collection.deleteBlock(["-1", "0"])
assert not collection.has("-1")
assert not collection.has("0")
assert collection.has("1")

database.createCollection({"name": "hello", "dimension": 128})
assert set(database.keys()) == set(["test", "hello"])
assert set(database.disk_io.getTableNames()) == set(["test", "hello"])

database.deleteCollection("test")
assert list(database.keys()) == ["hello"]
assert database.disk_io.getTableNames() == ["hello"]
database.disk_io.conn.close()
os.remove("test.db")