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
typedef std::vector<std::string> StringVector;

#ifndef FEAT_DIM
#define FEAT_DIM 768
#endif

#ifndef MODULE_NAME
#define MODULE_NAME vecdbImpl
#endif


