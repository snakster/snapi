#pragma once

#include "../database.h"

namespace database {

class values_impl : public values
{
public:
    void put() override;
        
    std::string get() override;
        
};

} // namespace database