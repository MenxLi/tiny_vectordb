#pragma once

#include "common.h"
#include "diskIO.h"
#include <vector>

template <typename NumT>
class VectorCollectionImpl{
public:
    VectorCollectionImpl();
    ~VectorCollectionImpl();
    int size();

    // add vectors to the collection, addBulk will log modification
    // loadBulk will not log modification, and will not check id duplication
    void addBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors);
    void addRawBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors);

    bool has(std::string& id);
    std::vector<NumT> get(std::string& id);

    void deleteBulk(const StringVector& ids);
    // void removeBulk(const StringVector& ids);

    std::vector<float> score(const std::vector<NumT>& query);
    void flush();

    void print();
private:
    static const int dim = FEAT_DIM;
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