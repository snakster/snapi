#pragma once

#include "../database.h"

namespace database {

class values_impl : public values
{
public:
    void put(std::string key, std::string value) override;
        
    std::string get(std::string key) override;
        
};

} // namespace database