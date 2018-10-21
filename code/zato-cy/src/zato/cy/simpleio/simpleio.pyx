# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

cdef class Elem(object):
    """ An individual input or output element.
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

# ################################################################################################################################

def run():
    sio = SIODefinition()
    print(sio)

# ################################################################################################################################

if __name__ == '__main__':
    run()

# ################################################################################################################################
