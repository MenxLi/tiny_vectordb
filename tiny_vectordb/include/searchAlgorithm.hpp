#pragma once
#include "common.h"

namespace SearchAlgorithm {

std::vector<int> topKIndices(const Eigen::Vector<float, Eigen::Dynamic> scores, int k);

/* target: (N, feat_dim), query: (feat_dim, ) */
template <typename NumT>
inline Eigen::Vector<float, Eigen::Dynamic> cosineSimilarity(const MatrixF& target, const Eigen::Vector<NumT, FEAT_DIM>& query_matrix){
    const fp32 _eps = 1e-8;
    if (target.cols() != query_matrix.size()){
        throw std::runtime_error("query size not match");
    }
    Eigen::Matrix<NumT, Eigen::Dynamic, 1> search_scores = target * query_matrix;
    float norm_query = query_matrix.norm();
    Eigen::Vector<float, Eigen::Dynamic> norm_collection = target.rowwise().norm();
    search_scores = search_scores.array() / (norm_query * norm_collection.array() + _eps);
    return search_scores;
}
template <typename NumT>
inline Eigen::Vector<float, Eigen::Dynamic> cosineSimilarity(const MatrixF& target, const std::vector<NumT>& query){
    if (target.cols() != query.size()){
        throw std::runtime_error("query size not match");
    }
    Eigen::Matrix<NumT, FEAT_DIM, 1> query_matrix = Eigen::Map<const Eigen::Matrix<NumT, FEAT_DIM, 1>>(query.data());
    return cosineSimilarity(target, query_matrix);
}

}
