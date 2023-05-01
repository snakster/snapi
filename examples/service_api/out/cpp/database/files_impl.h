#pragma once

#include "../database.h"

namespace database {

class files_impl : public files
{
public:
    void upload(std::string local_path, std::string remote_path) override;
        
    void download(std::string remote_path, std::string local_path) override;
        
    std::vector<std::string> list_dir(std::string remote_path) override;
        
};

} // namespace database