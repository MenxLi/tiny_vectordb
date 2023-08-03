#include "searchAlgorithm.hpp"

std::vector<int> SearchAlgorithm::topKIndexes(const Eigen::Vector<float, Eigen::Dynamic> scores, int k){
    std::vector<int> ret;
    std::vector<std::pair<float, int>> scores_idx;
    for (int i = 0; i < scores.size(); i++){
        scores_idx.push_back(std::make_pair(scores[i], i));
    }
    std::sort(scores_idx.begin(), scores_idx.end(), [](const std::pair<float, int>& a, const std::pair<float, int>& b){
        return a.first > b.first;
    });
    for (int i = 0; i < k; i++){
        ret.push_back(scores_idx[i].second);
    }
    return ret;
}