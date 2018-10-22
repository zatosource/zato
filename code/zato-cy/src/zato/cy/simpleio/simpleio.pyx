# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

cdef class _NotGiven(object):
    """ Indicates that a particular value was not provided on input or output.
    """
    def __str__(self):
        return '<NotGiven>'

    def __bool__(self):
        return False # Always evaluates to a boolean False

NotGiven = _NotGiven()

# ################################################################################################################################

cdef enum ElemType:
    as_is         = 1000
    bool          = 2000
    csv           = 3000
    date          = 3500
    date_time     = 3750
    dict_         = 4000
    dict_list     = 4500
    float         = 5000
    int           = 6000
    list_         = 7000
    opaque        = 8000
    text          = 9000
    user_defined  = 1_000_000

# ################################################################################################################################

cdef class Config(object):
    cdef:
        set exact
        set prefixes
        set suffixes

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
        ElemType _type
        unicode _name
        object _default_value
        bint _is_required

    def __str__(self):
        return '<{} at {} {}:{} d:{} r:{}>'.format(self.__class__.__name__, hex(id(self)), 1, 2, 3, 4)

cdef class AsIs(Elem):
    def __cinit__(self):
        self._type = ElemType.as_is

# ################################################################################################################################

cdef class SIODefinition(object):
    """ A single SimpleIO definition attached to a service.
    """
    cdef:

        # Name of the service this definition is for
        unicode _service_name

        # A list of Elem items required on input
        list _input_required

        # A list of Elem items optional on input
        list _input_optional

        # A list of Elem items required on output
        list _output_required

        # A list of Elem items optional on output
        list _output_optional

        # Whether non-NotGiven optional output elements should be produced on output or not
        bint _skip_empty_keys

        # Name of the response element, or None if there should be no top-level one
        object _response_elem

        # Default value to use for optional input elements, unless overridden on a per-element basis
        object _default_input_value

        # Default value to use for optional output elements, unless overridden on a per-element basis
        object _default_output_value

        object _default_value # Preserved for backward-compatibility, the same as _default_output_value

# ################################################################################################################################

cdef class SimpleIO(object):
    cdef:
        BoolConfig bool_config
        IntConfig int_config
        SecretConfig secret_config

    cdef bint is_int(self, name):
        pass

    cdef bint is_bool(self, name):
        pass

    cdef bint is_secret(self, name):
        pass

    cdef SIODefinition create_definition(self, dict data):
        pass

# ################################################################################################################################

def run():

    data = {
    }

    sio = SimpleIO()
    definition = sio.create_definition(data)
    print(definition)
    #print(ElemType.integer)

# ################################################################################################################################

if __name__ == '__main__':
    run()

# ################################################################################################################################
