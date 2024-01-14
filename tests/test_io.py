
from tiny_vectordb import VectorDatabase
import numpy as np
import os
import pytest


n, LEN_6 = 5, 6
test_db_path = os.path.join(os.path.dirname(__file__), "test1.db")

@pytest.fixture(scope="module")
def database():
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    return VectorDatabase(
        test_db_path, 
        [{ "name": "Test", "dimension": LEN_6, }, { "name": "Hello", "dimension": LEN_6 }]
        )

def test_diskio(database: VectorDatabase):
    collection = database.getCollection("Test")

    # from tiny_vectordb import VectorCollection
    # collection = VectorCollection(None, quite_loading=True, name="Test", dimension=LEN_6)

    np.random.seed(0)
    vectors = np.random.rand(n, LEN_6).tolist()
    ids = [str(x) for x in range(n)]

    # breakpoint()
    collection.addBlock(ids, vectors)
    print(collection["1"])
    collection.deleteBlock(["1", "2"])
    # collection._impl.update("3", np.zeros(LEN).tolist())
    # collection._impl.print()
    database.commit()