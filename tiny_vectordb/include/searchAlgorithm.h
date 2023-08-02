#pragma once
#include "common.h"

namespace SearchAlgorithm {

template <typename NumT>
class Searcher{
public:
    Searcher();
    Eigen::Vector<float, Eigen::Dynamic> cosineSimilarity(MatrixF& target, const std::vector<NumT>& query);
};

}
