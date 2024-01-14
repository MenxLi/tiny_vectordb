#include "common.h"
#include "pybind11/attr.h"
#include "pybind11/cast.h"
#include "pybind11/pytypes.h"
#include "searchAlgorithm.hpp"
#include "vecdbImpl.h"
#include <iostream>
#include <string>
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

    addRawBulk(ids, vectors);

    // log modifications
    for (int i = 0; i < ids.size(); i++){
        if (mod_map.find(ids[i]) != mod_map.end()){
            assert(mod_map[ids[i]] == ModificaionType::DELETE && "Impossible error??");
            mod_map[ids[i]] = ModificaionType::UPDATE;
        }
        else{
            mod_map[ids[i]] = ModificaionType::ADD;
        }
    }
}


template <typename NumT>
void VectorCollectionImpl<NumT>::addRawEncBulk(StringVector ids, const std::vector<std::string> enc_vectors){
    std::vector<std::vector<NumT>> vectors = std::vector<std::vector<NumT>>(enc_vectors.size());
    for (int i = 0; i < enc_vectors.size(); i++){
        vectors[i] = VectorStringEncode::decode<NumT>(enc_vectors[i]);
    }
    addRawBulk(ids, vectors);
}

template <typename NumT>
void VectorCollectionImpl<NumT>::addRawBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors){
    int old_size = vector_chunk->rows();

    // re-allocate memory for vector_chunk
    MatrixF* new_chunk = new MatrixF(ids.size() + old_size, FEAT_DIM);
    new_chunk->block(0, 0, old_size, FEAT_DIM) = vector_chunk->block(0, 0, old_size, FEAT_DIM);
    delete vector_chunk;
    this->vector_chunk = new_chunk;

    // update identifiers
    // no need to re-allocate memory
    identifiers -> insert(identifiers->end(), ids.begin(), ids.end());

    // update matrix
    // std::cout << "!! DEBUG: " << vectors[0].size() << " " << FEAT_DIM << std::endl;
    for (int i = 0; i < ids.size(); i++){
        if (vectors[i].size() != FEAT_DIM){
            throw std::runtime_error("vector size not match: " + 
                std::to_string(vectors[i].size()) + " vs. " + std::to_string(FEAT_DIM)
                );
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
void VectorCollectionImpl<NumT>::setBulk(StringVector ids, const std::vector<std::vector<NumT>> vectors){
    if (ids.size() != vectors.size()){
        throw std::runtime_error("ids and vectors size not match");
    }

    // a vector to mark which id need to add
    std::vector<int> to_add_index = std::vector<int>();
    to_add_index.reserve(ids.size());   // reserve memory to avoid re-allocate on push_back

    // duplicate ids check
    std::set<std::string> id_set(ids.begin(), ids.end());
    if (id_set.size() != ids.size()){
        throw std::runtime_error("ids are not unique");
    }
    for (int i = 0; i < ids.size(); i++){
        if (has(ids[i])){
            // if exist, update
            update(ids[i], vectors[i]);
        }
        else{
            // not exist, mark as need to add
            to_add_index.push_back(i);
        }
    }

    // collect ids and vectors to add
    StringVector to_add_ids = StringVector(to_add_index.size());
    std::vector<std::vector<NumT>> to_add_vectors = std::vector<std::vector<NumT>>(to_add_index.size());
    for (int i = 0; i < to_add_index.size(); i++){
        to_add_ids[i] = ids[to_add_index[i]];
        to_add_vectors[i] = vectors[to_add_index[i]];
    }

    // add new vectors
    addBulk(to_add_ids, to_add_vectors);
}

template <typename NumT> 
bool VectorCollectionImpl<NumT>::has(const std::string& id){
    // return std::find(identifiers.begin(), identifiers.end(), id) != identifiers.end();
    return id2idx_.find(id) != id2idx_.end();
}

template <typename NumT>
bool VectorCollectionImpl<NumT>::update(const std::string& id, std::vector<NumT> vec){
    if (vec.size() != FEAT_DIM){
        throw std::runtime_error("vector size not match");
    }
    if (!has(id)){
        return false;
    }

    for (int i = 0; i < FEAT_DIM; i++){
        (*vector_chunk)(id2idx_[id], i) = vec[i];
    }
    // record modification
    if (mod_map.find(id) == mod_map.end()){
        mod_map[id] = ModificaionType::UPDATE;
    }
    else{
        assert(mod_map[id] == ModificaionType::ADD && "Impossible error??");
        // do nothing, it must be a ADD, keep it as ADD
    }
    return true;
}

template <typename NumT> 
std::vector<NumT> VectorCollectionImpl<NumT>::get(const std::string& id){
    auto it = id2idx_.find(id);
    if (it == id2idx_.end()){
        return std::vector<NumT>();
    }
    int idx = it->second;
    return std::vector<NumT>(vector_chunk->row(idx).data(), vector_chunk->row(idx).data() + FEAT_DIM);
}

template <typename NumT>
std::vector<std::vector<NumT>> VectorCollectionImpl<NumT>::getBulk(const StringVector& ids){
    std::vector<std::vector<NumT>> result(ids.size());
    for (int i = 0; i < ids.size(); i++){
        result[i] = get(ids[i]);
    }
    return result;
}

template <typename NumT>
std::vector<std::string> VectorCollectionImpl<NumT>::getAllIds(){
    return std::vector<std::string>(identifiers->begin(), identifiers->end());
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

    // log modifications
    for (int i = 0; i < ids_del.size(); i++){
        if (mod_map.find(ids_del[i]) != mod_map.end()){
            if (mod_map[ids_del[i]] == ModificaionType::ADD){
                mod_map.erase(ids_del[i]);
                continue;
            }
        }
        mod_map[ids_del[i]] = ModificaionType::DELETE;
    }
}

template <typename NumT>
std::vector<float> VectorCollectionImpl<NumT>::score(const std::vector<NumT> &query){
    auto search_scores = SearchAlgorithm::cosineSimilarity(*vector_chunk, query);
    return std::vector<float>(search_scores.data(), search_scores.data() + search_scores.size());
}

template <typename NumT>
py::tuple VectorCollectionImpl<NumT>::search(const std::vector<NumT>& query, int topk){
    if (topk > size() or topk == -1){
        topk = size();
    }
    Eigen::Vector<float, Eigen::Dynamic> search_scores = SearchAlgorithm::cosineSimilarity(*vector_chunk, query);
    std::vector<int> topk_indexes = SearchAlgorithm::topKIndices(search_scores, topk);

    StringVector topk_ids = StringVector(topk);
    std::vector<float> topk_scores = std::vector<float>(topk);
    for (int i = 0; i < topk; i++){
        topk_ids[i] = identifiers->at(topk_indexes[i]);
        topk_scores[i] = search_scores[topk_indexes[i]];
    }
    return py::make_tuple(topk_ids, topk_scores);
}

template <typename NumT>
py::dict VectorCollectionImpl<NumT>::flush(){
    py::dict ret;

    StringVector add_ids;
    // std::vector<std::vector<NumT>> add_values;
    std::vector<std::string> add_values;    // encode vector to string

    StringVector update_ids;
    // std::vector<std::vector<NumT>> update_values;
    std::vector<std::string> update_values; // encode vector to string

    StringVector delete_ids;

    for (auto it = mod_map.begin(); it != mod_map.end(); it++){
        if (it->second == ModificaionType::ADD){
            add_ids.push_back(it->first);
            std::string encoded = VectorStringEncode::encode(get(it->first));
            add_values.push_back(encoded);
        }
        else if (it->second == ModificaionType::UPDATE){
            update_ids.push_back(it->first);
            std::string encoded = VectorStringEncode::encode(get(it->first));
            update_values.push_back(encoded);
        }
        else{
            delete_ids.push_back(it->first);
        }
    }
    // std::cout << "flush: " << add_ids.size() << " " << update_ids.size() << " " << delete_ids.size() << std::endl;

    ret["ADD"] = py::make_tuple(add_ids, add_values);
    ret["UPDATE"] = py::make_tuple(update_ids, update_values);
    ret["DELETE"] = py::make_tuple(delete_ids, py::none());
    mod_map.clear();
    return ret;
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

    py::class_< VectorCollectionImpl<num_t> >(m, "VectorCollectionImpl", py::module_local())
        .def(py::init<>(
            // [](){
            //     std::cout<< "!!! The package is build with FEAT_DIM: " << FEAT_DIM <<std::endl;
            //     return new VectorCollectionImpl<num_t>();
            // }
        ))
        .def("addBulk", &VectorCollectionImpl<num_t>::addBulk)
        .def("addRawEncBulk", &VectorCollectionImpl<num_t>::addRawEncBulk)
        .def("setBulk", &VectorCollectionImpl<num_t>::setBulk)
        .def("size", &VectorCollectionImpl<num_t>::size)
        .def("has", &VectorCollectionImpl<num_t>::has)
        .def("update", &VectorCollectionImpl<num_t>::update)
        .def("get", &VectorCollectionImpl<num_t>::get)
        .def("getBulk", &VectorCollectionImpl<num_t>::getBulk)
        .def("getAllIds", &VectorCollectionImpl<num_t>::getAllIds)
        .def("deleteBulk", &VectorCollectionImpl<num_t>::deleteBulk)
        .def("print", &VectorCollectionImpl<num_t>::print)
        .def("search", &VectorCollectionImpl<num_t>::search)
        .def("score", &VectorCollectionImpl<num_t>::score)
        .def("flush", &VectorCollectionImpl<num_t>::flush);

    // for debug.
    m.attr("FEAT_DIM") = FEAT_DIM;
    
    auto m_enc = m.def_submodule("enc");
    m_enc.def("encode", &VectorStringEncode::encode<num_t>);
    m_enc.def("decode", &VectorStringEncode::decode<num_t>);
}