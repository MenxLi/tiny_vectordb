import random
from tiny_vectordb import VectorDatabase

# VectorDatabase.VERBOSE = True

collection_configs = [
    {
        "name": "hello",
        "dimension": 256,
    },
    {
        "name": "world",
        "dimension": 1000,
    }
]

database = VectorDatabase("test.db", collection_configs)

collection = database["hello"]

# 50 vectors of 256 dimension
vectors = [[random.random() for _ in range(256)] for _ in range(50)]
vector_ids = [f"vector_{i}" for i in range(50)]

# io operations, may encounter duplicate ids if you run this script multiple times
collection.addBlock(vector_ids, vectors)
collection.deleteBlock(vector_ids[:10:2])

search_ids, search_scores = collection.search([random.random() for _ in range(256)], k=10)

database.flush()
database.commit()