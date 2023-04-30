#pragma once

#include "../database.h"

namespace database {

class files_impl : public files
{
public:
    void upload() override;
        
    void download() override;
        
};

} // namespace database