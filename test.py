import time
import numpy as np
from tiny_vectordb import VectorCollection

LEN = 16
N = 16

collection = VectorCollection[float]("test", LEN)
if not collection.has("-1"):
    collection.insert("-1", [float(x) for x in range(LEN)])

np.random.seed(0)
vectors = np.random.rand(N, LEN).tolist()
ids = [str(x) for x in range(N)]

collection.addBulk(ids, vectors)

query = [float(x) for x in range(LEN)]
target = vectors
assert collection.has("-1")
assert collection.get("-1") == [float(x) for x in range(LEN)]

assert collection.get("100") == None

collection.deleteBulk(["-1", "0"])
assert not collection.has("-1")
assert not collection.has("0")
assert collection.has("1")
