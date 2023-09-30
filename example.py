import random
from tiny_vectordb import VectorDatabase
import os
random.seed(0)

## This will print all compilation and linking commands
# VectorDatabase.VERBOSE = True

## You may need to change these paths to your own python installation, if error occurs, 
## or you may add some additional compile flags for your own environment and optimization
## or you can just remove these lines and use default settings
# from tiny_vectordb import VectorCollection
# VectorCollection.COMPILE_CONFIG["cxx"] = "clang++"
# VectorCollection.COMPILE_CONFIG["additional_compile_flags"] = ["-IC:\\Users\\vuser\\AppData\\Local\\Programs\\Python\\Python311\\include"]
# VectorCollection.COMPILE_CONFIG["additional_link_flags"] = ["-LC:\\Users\\vuser\\AppData\\Local\\Programs\\Python\\Python311\\libs"]

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

if os.path.exists("test.db"):
    if input("test.db exists, delete it? (y/n)") == "y":
        os.remove("test.db")
    else:
        exit("This script will raise error if test.db exists, for duplicate item addition")

# create database will initialize all collections, 
# for each dimension, a shared library will be compiled and loaded.
print("Compiling...")
database = VectorDatabase("test.db", collection_configs)  # type: ignore
collection = database["hello"]

# 100 vectors of 256 dimension
print("Creating vectors...")
N_VECTORS = 20
vectors = [[random.random() for _ in range(256)] for _ in range(N_VECTORS)]
vector_ids = [f"vector_{i}" for i in range(N_VECTORS)]

# io operations, may encounter duplicate ids if you run this script multiple times
print("Adding vectors...")
collection.addBlock(vector_ids, vectors)
collection.deleteBlock(vector_ids[:10:2])

# set block, will have no error if id not exists
collection.setBlock(
    vector_ids[10:20] + [f"addtional{i}" for i in range(3)], 
    [[0. for _ in range(256)] for _ in range(13)]
)

print("Current keys:", collection.keys())

search_ids, search_scores = collection.search([random.random() for _ in range(256)], k=10)
print("Top 10 search results:", search_ids, search_scores)

print("Flushing and commiting...")
database.flush()
database.commit()