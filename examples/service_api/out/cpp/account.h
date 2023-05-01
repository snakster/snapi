#pragma once

#include <string>
#include <vector>

namespace account {

class tokens
{
public:
    virtual std::string create() = 0;
        
    virtual void revoke() = 0;
        
};

} // namespace account