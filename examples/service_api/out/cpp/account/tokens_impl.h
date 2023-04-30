#pragma once

#include "../account.h"

namespace account {

class tokens_impl : public tokens
{
public:
    std::string create() override;
        
    void revoke() override;
        
};

} // namespace account