from tiny_vectordb import VectorCollection

def test_encoding():
    N = 16
    collection = VectorCollection(None, "test", N)
    vec = [ float(i) for i in range(N)]
    enc = collection.encoding.encode(vec)
    dec = collection.encoding.decode(enc)
    assert dec == vec