#include "diskIO.h"

DiskIOVirtual::DiskIOVirtual(std::string path): mod_map_ptr(nullptr), save_path(path){}
void DiskIOVirtual::DiskIOVirtual::setModMap(std::map<std::string, ModificaionType> *_mod_map_ptr){
    mod_map_ptr = _mod_map_ptr;
}
void DiskIOVirtual::load(StringVector* identifiers, MatrixF* vector_chunk) {}
void DiskIOVirtual::save(StringVector* identifiers, MatrixF* vector_chunk) {}


DiskIOVoid::DiskIOVoid(std::string path): DiskIOVirtual(path){}
void DiskIOVoid::load(StringVector* identifiers, MatrixF* vector_chunk) {}
void DiskIOVoid::save(StringVector* identifiers, MatrixF* vector_chunk) {
    if (mod_map_ptr == nullptr){
        throw std::runtime_error("mod_map_ptr is not set");
    }
    (*mod_map_ptr).clear();
}