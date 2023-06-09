#pragma once

#include <string>
#include <vector>

namespace account {

class tokens
{
public:
    virtual std::string create() = 0;
        
    virtual void revoke(std::string token) = 0;
        
};

} // namespace account