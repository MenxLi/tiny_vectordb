#pragma once

#include <memory>
#include <vector>
#include <string>
#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h>
// #include <Eigen/Core>

typedef float num_t;
typedef Eigen::Matrix<num_t, Eigen::Dynamic, FEAT_DIM, Eigen::RowMajor> 
MatrixF;

#ifndef FEAT_DIM
#define FEAT_DIM 768
#endif

#ifndef MODULE_NAME
#define MODULE_NAME vecdbImpl
#endif

template <typename NumT>
class VectorCollectionImpl{
public:
    VectorCollectionImpl();
    ~VectorCollectionImpl();
    int size();
    void addBulk(std::vector<std::string> ids, const std::vector<std::vector<NumT>> vectors);
    bool has(std::string& id);
    std::vector<NumT> get(std::string& id);
    void deleteBulk(const std::vector<std::string>& ids);

    void print();   // for debug
private:
    static const int dim = FEAT_DIM;
    std::vector<std::string>* identifiers;
    MatrixF* vector_chunk;
    std::map<std::string, int> id2idx_;
    void reIndex();
};
