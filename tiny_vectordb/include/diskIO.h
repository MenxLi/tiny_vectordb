#pragma once

#include "common.h"
#include <string>


class DiskIOVirtual{
public:
    DiskIOVirtual(std::string path);
    virtual void load(StringVector* identifiers, MatrixF* vector_chunk);
    virtual void save(StringVector* identifiers, MatrixF* vector_chunk);
    void setModMap(std::map<std::string, ModificaionType>* _mod_map_ptr);

protected:
    std::map<std::string, ModificaionType>* mod_map_ptr;
    std::string save_path;
};

class DiskIOVoid: public DiskIOVirtual{
    DiskIOVoid(std::string path);
    void load(StringVector* identifiers, MatrixF* vector_chunk) override;
    void save(StringVector* identifiers, MatrixF* vector_chunk) override;
};

class DiskIOSQLite: public DiskIOVirtual{
    // TO BE IMPLEMENTED
    DiskIOSQLite(std::string path);
    void load(StringVector* identifiers, MatrixF* vector_chunk) override;
    void save(StringVector* identifiers, MatrixF* vector_chunk) override;
};