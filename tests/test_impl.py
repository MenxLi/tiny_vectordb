
import pytest
import numpy as np
from tiny_vectordb import VectorCollectionT

@pytest.fixture(scope="module")
def cxx_impl():
    from tiny_vectordb import getVectorCollectionBackend
    return getVectorCollectionBackend('cxx')(
        None, 
        quite_loading=True, 
        name="Test", 
        dimension=3
    )

@pytest.fixture(scope="module")
def numpy_impl():
    from tiny_vectordb import getVectorCollectionBackend
    return getVectorCollectionBackend('numpy')(
        None, 
        quite_loading=True, 
        name="Test", 
        dimension=3
    )

def almostEqual(a, b):
    return np.allclose(a, b)
    # return (np.abs(np.array(a) - np.array(b)) < 1e-6).all()

def test_encoding(cxx_impl: VectorCollectionT, numpy_impl: VectorCollectionT):
    enc1 = cxx_impl.encoding
    enc2 = numpy_impl.encoding
    assert enc1.encode([1, 2, 3]) == enc2.encode([1, 2, 3])
    assert enc1.decode(enc1.encode([1, 2, 3])) == enc2.decode(enc2.encode([1, 2, 3]))

def test_add(cxx_impl: VectorCollectionT, numpy_impl: VectorCollectionT):
    cxx_impl.addBlock(["1", "2"], [[1, 2, 3], [4, 5, 6]])
    numpy_impl.addBlock(["1", "2"], [[1, 2, 3], [4, 5, 6]])
    assert cxx_impl["1"] == numpy_impl["1"]
    assert cxx_impl["2"] == numpy_impl["2"]

def test_has(cxx_impl: VectorCollectionT, numpy_impl: VectorCollectionT):
    assert cxx_impl.has("1") == numpy_impl.has("1")
    assert cxx_impl.has("2") == numpy_impl.has("2")
    assert cxx_impl.has("3") == numpy_impl.has("3")

def test_getBlock(cxx_impl: VectorCollectionT, numpy_impl: VectorCollectionT):
    assert cxx_impl.getBlock(["1", "2"]) == numpy_impl.getBlock(["1", "2"])

def test_search(cxx_impl: VectorCollectionT, numpy_impl: VectorCollectionT):
    assert cxx_impl.search([1, 2, 3]) == numpy_impl.search([1, 2, 3])

def test_savenload():
    from tiny_vectordb import VectorDatabase
    import os
    n, LEN_6 = 5, 6

    os.environ["TINY_VECTORDB_BACKEND"] = "cxx"
    test_db_path = os.path.join(os.path.dirname(__file__), "test1.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    database = VectorDatabase(
        test_db_path, 
        [{ "name": "Test", "dimension": LEN_6, }, { "name": "Hello", "dimension": LEN_6 }]
        )
    collection = database.getCollection("Test")
    np.random.seed(0)
    vectors = np.random.rand(n, LEN_6).tolist()
    ids = [str(x) for x in range(n)]

    # breakpoint()
    collection.addBlock(ids, vectors)
    database.commit()

    os.environ["TINY_VECTORDB_BACKEND"] = "numpy"
    database = VectorDatabase(
        test_db_path, 
        [{ "name": "Test", "dimension": LEN_6, }, { "name": "Hello", "dimension": LEN_6 }]
        )
    collection = database.getCollection("Test")
    assert almostEqual(collection.getBlock(ids), vectors)

    os.remove(test_db_path)