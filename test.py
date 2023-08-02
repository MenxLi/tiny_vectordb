import os
from tiny_vectordb import VectorCollection

LEN = 16

collection = VectorCollection[float]("test", LEN)

ids = [str(x) for x in range(2)]
vectors = [[float(x) for x in range(LEN)] for _ in range(2)]

collection.addBulk(ids, vectors)
collection.insert("8", [float(x) for x in range(LEN)])

assert collection.has("8")
assert collection.get("8") == [float(x) for x in range(LEN)]
assert collection.get("9") == None

collection.deleteBulk(["8", "0"])
assert not collection.has("8")
assert not collection.has("0")
assert collection.has("1")

collection._impl.print()