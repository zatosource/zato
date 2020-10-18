#include <pybind11/pybind11.h>

namespace py = pybind11;

int
placeholder(int x, int y)
{
    return x + y;
}

PYBIND11_MODULE(libzato, m) {
    m.doc() = "This is a placeholder";
    m.def("placeholder", &placeholder, "A placeholder function");
}
