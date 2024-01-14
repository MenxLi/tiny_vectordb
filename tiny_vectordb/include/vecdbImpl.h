#pragma once

#include "common.h"
#include "pybind11/pytypes.h"
#include "b64enc.h"
#include <string>
#include <vector>

namespace py = pybind11;

template <typename NumT>
class VectorCollectionImpl{
public:
    VectorCollectionImpl();
    ~VectorCollectionImpl();
    static const int dim = FEAT_DIM;
    int size();

    // add vectors to the collection, addBulk will log modification
    // addRaw will not log modification, and will not check id duplication
    void addBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors);
    void addRawEncBulk(StringVector ids, const std::vector<std::string> enc_vectors);
    void addRawBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors);

    // set will add the vector if the id does not exist, otherwise update the vector
    void setBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors);

    inline bool has(const std::string& id);
    inline bool update(const std::string& id, const std::vector<NumT> vec);
    inline std::vector<NumT> get(const std::string& id);
    std::vector<std::vector<NumT>> getBulk(const StringVector& id);
    StringVector getAllIds();

    void deleteBulk(const StringVector& ids);
    // void removeBulk(const StringVector& ids);

    // return the topk ids and scores
    py::tuple search(const std::vector<NumT>& query, int topk = -1);
    std::vector<float> score(const std::vector<NumT>& query);

    // return the gathered modifications in python dict and set mod_map to empty
    // the python dict is in the form of 
    // {update / add: ([id1, id2, ...], [vector1, vector2, ...]) }
    // or {delete: ([id1, id2, ...], )}
    // the actual disk IO will be done in python
    py::dict flush();

    void print();
private:
    // identifiers and vector_chunk should have the same size
    // these two variables are used to store the data
    StringVector* identifiers;
    MatrixF* vector_chunk;

    // id2idx_ is used to store the mapping from id to index for fast retrieval
    std::map<std::string, int> id2idx_;
    void reIndex();

    // mod_map is used to store the modification of the vector collection
    // the modification will be applied to the vector collection when flush() is called
    std::map<std::string, ModificaionType> mod_map;

    // DiskIOVirtual *diskIO;
};


namespace VectorStringEncode {
    template <typename NumT>
    inline std::string encode(const std::vector<NumT>& vec){
        std::vector<uchar> vec_uchar((uchar*)vec.data(), (uchar*)vec.data() + vec.size() * sizeof(NumT));
        return base64_encode(vec_uchar);
    }

    template <typename NumT>
    inline std::vector<NumT> decode(const std::string& encoded){
        if (encoded.size() % 4 != 0){
            throw std::runtime_error("invalid encoded string");
        }
        std::vector<uchar> vec_uchar = base64_decode(encoded);

        // will this be unsafe?
        std::vector<NumT> vec((NumT*)vec_uchar.data(), (NumT*)vec_uchar.data() + vec_uchar.size() / sizeof(NumT));
        return vec;
    }
}