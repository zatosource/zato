# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Cython
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map

# Zato
from sio_input_elem cimport SIOInputElem

# ################################################################################################################################

cdef class SIODefinition(object):
    """ A single SimpleIO definition attached to a service.
    """
    cdef:
        public unicode service_name
        public list input_required
        public list input_optional
        public list output_required
        public list output_optional
        public bint skip_empty_keys

# ################################################################################################################################

def run():
    sio = SIODefinition()
    #input_elem = SIOInputElem()
    print(sio)#, input_elem)

# ################################################################################################################################

if __name__ == '__main__':
    run()

# ################################################################################################################################
