#pragma once

#include "../account.h"

namespace account {

class tokens_impl : public tokens
{
public:
    std::string create() override;
        
    void revoke(std::string token) override;
        
};

} // namespace account