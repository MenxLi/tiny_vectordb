#pragma once
#include "common.h"

namespace SearchAlgorithm {

template <typename NumT>
class Searcher{
    Eigen::Vector<float, Eigen::Dynamic> score(MatrixF* target, const std::vector<NumT>& query);
};

}
