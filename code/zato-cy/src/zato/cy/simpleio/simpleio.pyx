# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

cdef class Config(object):
    cdef:
        public set exact
        public set prefixes
        public set suffixes

# ################################################################################################################################

cdef class BoolConfig(Config):
    pass

# ################################################################################################################################

cdef class IntConfig(Config):
    pass

# ################################################################################################################################

cdef class SecretConfig(Config):
    pass

# ################################################################################################################################

cdef class Elem(object):
    """ An individual input or output element. May be a ForceType instance or not.
    """
    cdef:
        public unicode name
        public unicode type
        public object default_value
        public bint is_required

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
        public unicode response_elem

# ################################################################################################################################

cdef class SimpleIO(object):
    cdef:
        public BoolConfig bool_config
        public IntConfig int_config
        public SecretConfig secret_config

# ################################################################################################################################

def run():
    sio = SIODefinition()
    print(sio)

# ################################################################################################################################

if __name__ == '__main__':
    run()

# ################################################################################################################################
