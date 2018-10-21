# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

cdef extern from 'cpp/simpleio.cpp' namespace 'zato::simpleio':
    pass

cdef extern from 'cpp/include/simpleio.hpp' namespace 'zato::simpleio':
    cdef cppclass SIOInputElem:
        SIOInputElem() except +
