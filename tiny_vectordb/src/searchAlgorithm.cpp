#include "searchAlgorithm.hpp"

// std::vector<int> SearchAlgorithm::topKIndices(const Eigen::Vector<float, Eigen::Dynamic> scores, int k){
//     std::vector<int> ret;
//     std::vector<std::pair<float, int>> scores_idx;
//     for (int i = 0; i < scores.size(); i++){
//         scores_idx.push_back(std::make_pair(scores[i], i));
//     }
//     std::sort(scores_idx.begin(), scores_idx.end(), [](const std::pair<float, int>& a, const std::pair<float, int>& b){
//         return a.first > b.first;
//     });
//     for (int i = 0; i < k; i++){
//         ret.push_back(scores_idx[i].second);
//     }
//     return ret;
// }

// sort using std::nth_element
std::vector<int> SearchAlgorithm::topKIndices(const Eigen::Vector<float, Eigen::Dynamic> scores, int k){
    std::vector<int> ret;
    std::vector<std::pair<float, int>> scores_idx;
    scores_idx.reserve(scores.size());
    for (int i = 0; i < scores.size(); i++){
        scores_idx.push_back(std::make_pair(scores[i], i));
    }
    // sort with the k-th element as the pivot
    std::nth_element(scores_idx.begin(), scores_idx.begin() + k, scores_idx.end(), [](const std::pair<float, int>& a, const std::pair<float, int>& b){
        return a.first > b.first;
    });
    // sort the first k elements, the rest are not sorted, make the larger the first
    std::sort(scores_idx.begin(), scores_idx.begin() + k, [](const std::pair<float, int>& a, const std::pair<float, int>& b){
        return a.first > b.first;
    });
    for (int i = 0; i < k; i++){
        ret.push_back(scores_idx[i].second);
    }
    return ret;
}