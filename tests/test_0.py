

import os
import numpy as np
from tiny_vectordb import VectorDatabase, autoCompileConfig

VectorDatabase.VERBOSE = True
LEN_16 = 16
N = 16
__this_dir = os.path.dirname(os.path.abspath(__file__))
_test_db_path = os.path.join(__this_dir, "test.db")

def amostEqual(a, b):
    return (np.abs(np.array(a) - np.array(b)) < 1e-6).all()

if os.path.exists(_test_db_path):
    os.remove(_test_db_path)
database =  VectorDatabase(
    _test_db_path, 
    [{ "name": "test", "dimension": LEN_16, }],
    compile_config=autoCompileConfig()
    )

def test_0():
    collection = database.getCollection("test")
    assert not collection.has("-1")
    collection.addBlock(["-1"], [[float(x) for x in range(LEN_16)]])

    np.random.seed(0)
    vectors = np.random.rand(N, LEN_16).tolist()
    ids = [str(x) for x in range(N)]
    collection.addBlock(ids, vectors)

    assert collection.has("-1")
    assert amostEqual(collection.get("-1"), [float(x) for x in range(LEN_16)])

    assert not collection.get("100")

    collection.deleteBlock(["-1", "0"])
    assert not collection.has("-1")
    assert not collection.has("0")
    assert collection.has("1")

def test_diskio():
    database.createCollection({"name": "hello", "dimension": 128})
    assert set(database.keys()) == set(["test", "hello"])
    assert set(database.disk_io.getTableNames()) == set(["test", "hello"])

    database.deleteCollection("test")
    assert list(database.keys()) == ["hello"]
    assert database.disk_io.getTableNames() == ["hello"]
    database.disk_io.conn.close()

def test_end():
    os.remove(_test_db_path)