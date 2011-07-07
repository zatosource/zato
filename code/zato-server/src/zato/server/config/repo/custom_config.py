# -*- coding: utf-8 -*-

# Spring Python
from springpython.config import Object
from springpython.config import PythonConfig

class CustomContext(PythonConfig):
    pass

    # Uncomment below to set a custom HTTP port.

    # @Object
    # def http_port(self):
    #     return 9876
