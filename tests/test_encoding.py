from tiny_vectordb import VectorCollection

N = 16
collection = VectorCollection(None, "test", N)

vec = [ float(i) for i in range(N)]
# print("Encoding test:")
enc = collection.encoding.encode(vec)
# print(enc)
dec = collection.encoding.decode(enc)
# print(dec)
assert dec == vec