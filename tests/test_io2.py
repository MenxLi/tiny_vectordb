from tiny_vectordb import VectorDatabase
import numpy as np
import os

n, LEN = 5, 6

test_db_path = os.path.join(os.path.dirname(__file__), "test.db")
if os.path.exists(test_db_path):
    os.remove(test_db_path)

database = VectorDatabase(test_db_path, [{ "name": "Test", "dimension": LEN, }, { "name": "Hello", "dimension": LEN }])

collection = database.getCollection("Test")

np.random.seed(0)
vectors = np.random.rand(n, LEN).tolist()
ids = [str(x) for x in range(n)]

collection.addBlock(ids, vectors)
print(collection["1"])
collection.deleteBlock(["1", "2"])
collection._impl.update("3", np.zeros(LEN).tolist())

collection._impl.print()

database.flush()
database.commit()