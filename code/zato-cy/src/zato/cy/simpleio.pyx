# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Cython
from libcpp.vector cimport vector

# ################################################################################################################################

cdef class SimpleIO:
    pass

# ################################################################################################################################

def run():
    cdef vector[SimpleIO] my_vector
    my_vector.reserve(100)
    print(my_vector)

# ################################################################################################################################

if __name__ == '__main__':
    run()

# ################################################################################################################################
