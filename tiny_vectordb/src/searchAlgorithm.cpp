#include "common.h"
#include "searchAlgorithm.h"
#include "vecdbImpl.h"

using namespace SearchAlgorithm;

template <typename NumT>
Searcher<NumT>::Searcher(){
    // do nothing
}

template <typename NumT>
Eigen::Vector<float, Eigen::Dynamic> Searcher<NumT>::
cosineSimilarity(MatrixF& target, const std::vector<NumT>& query){
    // target: (N, feat_dim)
    // query: (feat_dim, )
    if (target.cols() != query.size()){
        throw std::runtime_error("query size not match");
    }
    Eigen::Map<const Eigen::Matrix<NumT, FEAT_DIM, 1>> query_vec(query.data(), query.size());
    Eigen::Matrix<NumT, Eigen::Dynamic, 1> scores = target * query_vec.transpose();
    return scores;
}