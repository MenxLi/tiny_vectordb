
/*
Code from https://stackoverflow.com/questions/180947/base64-decode-snippet-in-c
*/

#include "common.h"
#include <iostream>

// static inline bool is_base64(BYTE c);
// std::string base64_encode(BYTE const* buf, unsigned int bufLen);
std::string base64_encode(std::vector<uchar> const& in);
std::vector<uchar> base64_decode(std::string const& encoded_string);

// init pybind11

namespace py = pybind11;
void init_b64enc(py::module &m);