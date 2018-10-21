#pragma once

#include <string>

using std::string;

namespace zato {
    namespace simpleio {
        class SIOInputElem {
            public:
                SIOInputElem();
                ~SIOInputElem();
                string name;
        };
    }
}
