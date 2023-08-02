#pragma once
#include "common.h"

namespace SearchAlgorithm {

template <typename NumT>
class Searcher{
public:
    Searcher();
    inline Eigen::Vector<float, Eigen::Dynamic> cosineSimilarity(const MatrixF& target, const std::vector<NumT>& query);
};

template <typename NumT>
Searcher<NumT>::Searcher(){
    // do nothing
}

template <typename NumT>
Eigen::Vector<float, Eigen::Dynamic> Searcher<NumT>::
cosineSimilarity(const MatrixF& target, const std::vector<NumT>& query){
    // target: (N, feat_dim), query: (feat_dim, )
    if (target.cols() != query.size()){
        throw std::runtime_error("query size not match");
    }
    Eigen::Matrix<NumT, FEAT_DIM, 1> query_matrix = Eigen::Map<const Eigen::Matrix<NumT, FEAT_DIM, 1>>(query.data());
    Eigen::Matrix<NumT, Eigen::Dynamic, 1> search_scores = target * query_matrix;
    float norm_query = query_matrix.norm();
    Eigen::Vector<float, Eigen::Dynamic> norm_collection = target.rowwise().norm();
    search_scores = search_scores.array() / (norm_query * norm_collection.array());
    return search_scores;
}

}
