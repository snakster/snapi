#pragma once

#include <string>
#include <vector>

namespace database {

class values
{
public:
    virtual void put(std::string key, std::string value) = 0;
        
    virtual std::string get(std::string key) = 0;
        
};

class files
{
public:
    virtual void upload(std::string local_path, std::string remote_path) = 0;
        
    virtual void download(std::string remote_path, std::string local_path) = 0;
        
    virtual std::vector<std::string> list_dir(std::string remote_path = ".") = 0;
        
};

} // namespace database