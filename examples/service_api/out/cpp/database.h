#pragma once

#include <string>

namespace database {

class values
{
public:
    virtual void put() = 0;
        
    virtual std::string get() = 0;
        
};

class files
{
public:
    virtual void upload() = 0;
        
    virtual void download() = 0;
        
};

} // namespace database