#pragma once

#include "searchAlgorithm.h"
#include "common.h"
#include <vector>

template <typename NumT>
class VectorCollectionImpl{
public:
    VectorCollectionImpl();
    ~VectorCollectionImpl();
    int size();
    void addBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors);
    bool has(std::string& id);
    std::vector<NumT> get(std::string& id);
    void deleteBulk(const StringVector& ids);

    std::vector<float> cosineSimilarity(const std::vector<NumT>& query);

    void print();   // for debug
private:
    static const int dim = FEAT_DIM;
    StringVector* identifiers;
    MatrixF* vector_chunk;
    std::map<std::string, int> id2idx_;
    void reIndex();

    SearchAlgorithm::Searcher<NumT>* searcher;
};