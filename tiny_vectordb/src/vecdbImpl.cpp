#include "common.h"
#include "searchAlgorithm.hpp"
#include "vecdbImpl.h"
#include <vector>

namespace py = pybind11;

template <typename NumT>
VectorCollectionImpl<NumT>::VectorCollectionImpl(){
    vector_chunk = new MatrixF(0, FEAT_DIM);
    identifiers = new StringVector();
}

template <typename NumT>
VectorCollectionImpl<NumT>::~VectorCollectionImpl(){
    delete vector_chunk;
    delete identifiers;
}

template <typename NumT> 
int VectorCollectionImpl<NumT>::size(){return vector_chunk->rows();}

template <typename NumT>
void VectorCollectionImpl<NumT>::reIndex(){
    id2idx_.clear();
    for (int i = 0; i < identifiers -> size(); i++){
        id2idx_[(*identifiers)[i]] = i;
    }
}

template <typename NumT>
void VectorCollectionImpl<NumT>::addBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors){
    if (ids.size() != vectors.size()){
        throw std::runtime_error("ids and vectors size not match");
    }
    int old_size = vector_chunk->rows();

    // duplicate ids check
    std::set<std::string> id_set(ids.begin(), ids.end());
    if (id_set.size() != ids.size()){
        throw std::runtime_error("ids are not unique");
    }
    for (int i = 0; i < ids.size(); i++){
        if (has(ids[i])){
            throw std::runtime_error("id already exists");
        }
    }

    // re-allocate memory for vector_chunk
    MatrixF* new_chunk = new MatrixF(ids.size() + old_size, FEAT_DIM);
    new_chunk->block(0, 0, old_size, FEAT_DIM) = vector_chunk->block(0, 0, old_size, FEAT_DIM);
    delete vector_chunk;
    this->vector_chunk = new_chunk;

    // update identifiers
    // no need to re-allocate memory
    identifiers -> insert(identifiers->end(), ids.begin(), ids.end());

    // update matrix
    for (int i = 0; i < ids.size(); i++){
        if (vectors[i].size() != FEAT_DIM){
            throw std::runtime_error("vector size not match");
        }
        for (int j = 0; j < FEAT_DIM; j++){
            (*vector_chunk)(i + old_size, j) = vectors[i][j];
        }
    }

    // update index
    for (int i = 0; i < ids.size(); i++){
        id2idx_[ids[i]] = i + old_size;
    }
}

template <typename NumT> 
inline bool VectorCollectionImpl<NumT>::has(std::string& id){
    // return std::find(identifiers.begin(), identifiers.end(), id) != identifiers.end();
    return id2idx_.find(id) != id2idx_.end();

}

template <typename NumT> 
std::vector<NumT> VectorCollectionImpl<NumT>::get(std::string& id){
    auto it = id2idx_.find(id);
    if (it == id2idx_.end()){
        return std::vector<NumT>();
    }
    int idx = it->second;
    return std::vector<NumT>(vector_chunk->row(idx).data(), vector_chunk->row(idx).data() + FEAT_DIM);
}

template <typename NumT>
void VectorCollectionImpl<NumT>::deleteBulk(const StringVector& ids_del){
    // check if all ids exist and gather all indexes to be deleted
    int new_size = vector_chunk->rows() - ids_del.size();
    std::unique_ptr<int> delete_rowIndexes = std::unique_ptr<int>(new int[ids_del.size()]);
    std::unique_ptr<int> keep_rowIndexes = std::unique_ptr<int>(new int[new_size]);
    for (int i = 0; i < ids_del.size(); i++){
        auto it = id2idx_.find(ids_del[i]);
        if (it == id2idx_.end()){
            throw std::runtime_error("id not found");
        }
        delete_rowIndexes.get()[i] = it->second;
    }
    // sort indexes in asending order
    std::sort(delete_rowIndexes.get(), delete_rowIndexes.get() + ids_del.size());
    
    // copy rows to keep to new matrix using double pointers
    int delete_rowIndexes_offset = 0;
    for (int i=0; i < vector_chunk->rows(); i++){
        if (delete_rowIndexes_offset < ids_del.size() && delete_rowIndexes.get()[delete_rowIndexes_offset] == i){
            delete_rowIndexes_offset++;
            continue;
        }
        keep_rowIndexes.get()[i - delete_rowIndexes_offset] = i;
    }

    // allocate new matrix and identifiers
    MatrixF* new_chunk = new MatrixF(new_size, FEAT_DIM);
    StringVector* new_identifiers = new StringVector(new_size);

    for (int i = 0; i < vector_chunk->rows() - ids_del.size(); i++){
        new_chunk->row(i) = vector_chunk->row(keep_rowIndexes.get()[i]);
        new_identifiers->at(i) = identifiers->at(keep_rowIndexes.get()[i]);
    }

    // update and free memory
    delete vector_chunk;
    delete identifiers;
    this->vector_chunk = new_chunk;
    this->identifiers = new_identifiers;
    reIndex();
}

template <typename NumT>
std::vector<float> VectorCollectionImpl<NumT>::score(const std::vector<NumT> &query){
    auto search_scores = SearchAlgorithm::cosineSimilarity(*vector_chunk, query);
    return std::vector<float>(search_scores.data(), search_scores.data() + search_scores.size());
}

template <typename NumT>
void VectorCollectionImpl<NumT>::print(){
    // for debug
    std::cout << "VectorCollectionImpl" << std::endl;
    std::cout << "- size: " << size() << std::endl;
    for (int i=0; i<size(); i++){
        std::cout << "[" << identifiers->at(i) << "] ";
        for (int j=0; j<FEAT_DIM; j++){
            std::cout << (*vector_chunk)(i, j) << " ";
        }
        std::cout << std::endl;
    }
}

PYBIND11_MODULE(MODULE_NAME, m){
    m.doc() = "pybind11 vecdbImpl plugin";

    py::class_< VectorCollectionImpl<num_t> >(m, "VectorCollectionImpl")
        .def(py::init<>())
        .def("addBulk", &VectorCollectionImpl<num_t>::addBulk)
        .def("size", &VectorCollectionImpl<num_t>::size)
        .def("has", &VectorCollectionImpl<num_t>::has)
        .def("get", &VectorCollectionImpl<num_t>::get)
        .def("deleteBulk", &VectorCollectionImpl<num_t>::deleteBulk)
        .def("print", &VectorCollectionImpl<num_t>::print)
        .def("score", &VectorCollectionImpl<num_t>::score);
}