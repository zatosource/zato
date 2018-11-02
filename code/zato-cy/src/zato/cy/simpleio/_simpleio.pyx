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

# ################################################################################################################################

cdef enum ElemType:
    as_is         =  1
    bool          =  2
    csv           =  3
    date          =  4
    date_time     =  5
    dict_         =  6
    dict_list     =  7
    float         =  8
    int           =  9
    list_         = 10
    opaque        = 11
    text          = 12
    uuid          = 13
    user_defined  = 1_000_000

# ################################################################################################################################

cdef class Elem(object):
    """ An individual input or output element. May be a ForceType instance or not.
    """
    cdef:
        ElemType _type
        unicode _name
        object _default
        bint _is_required

    def __str__(self):
        return '<{} at {} {}:{} d:{} r:{}>'.format(self.__class__.__name__, hex(id(self)), self._name, self._type,
            self._default, self._is_required)

# ################################################################################################################################

cdef class AsIs(Elem):
    def __cinit__(self):
        self._type = ElemType.as_is

# ################################################################################################################################

cdef class Bool(Elem):
    def __cinit__(self):
        self._type = ElemType.bool

# ################################################################################################################################

cdef class CSV(Elem):
    def __cinit__(self):
        self._type = ElemType.csv

# ################################################################################################################################

cdef class Date(Elem):
    def __cinit__(self):
        self._type = ElemType.date

# ################################################################################################################################

cdef class DateTime(Elem):
    def __cinit__(self):
        self._type = ElemType.date_time

# ################################################################################################################################

cdef class Dict(Elem):
    def __cinit__(self):
        self._type = ElemType.dict_

# ################################################################################################################################

cdef class DictList(Elem):
    def __cinit__(self):
        self._type = ElemType.dict_list

# ################################################################################################################################

cdef class Float(Elem):
    def __cinit__(self):
        self._type = ElemType.float

# ################################################################################################################################

cdef class Int(Elem):
    def __cinit__(self):
        self._type = ElemType.int

# ################################################################################################################################

cdef class List(Elem):
    def __cinit__(self):
        self._type = ElemType.list_

# ################################################################################################################################

cdef class Opaque(Elem):
    def __cinit__(self):
        self._type = ElemType.opaque

# ################################################################################################################################

cdef class UUID(Elem):
    def __cinit__(self):
        self._type = ElemType.uuid

# ################################################################################################################################

cdef class ConfigItem(object):
    """ An individual instance of server-wide SimpleIO configuration. Each subclass covers
    a particular set of exact values, prefixes or suffixes.
    """
    cdef:
        public set exact
        public set prefixes
        public set suffixes

    def __str__(self):
        return '<{} at {} e:{}, p:{}, s:{}>'.format(self.__class__.__name__, hex(id(self)),
            sorted(self.exact), sorted(self.prefixes), sorted(self.suffixes))

# ################################################################################################################################

cdef class BoolConfig(ConfigItem):
    """ SIO configuration for boolean values.
    """

# ################################################################################################################################

cdef class IntConfig(ConfigItem):
    """ SIO configuration for integer values.
    """

# ################################################################################################################################

cdef class SecretConfig(ConfigItem):
    """ SIO configuration for secret values, passwords, tokens, API keys etc.
    """

# ################################################################################################################################

cdef class _SIOServerConfig(object):
    """ Contains global SIO configuration. Each service's _simpleio attribute
    will refer to this object so as to have only one place where all the global configuration is kept.
    """
    cdef:
        public BoolConfig bool_config
        public IntConfig int_config
        public SecretConfig secret_config

        # Names in SimpleIO declarations that can be overridden by users
        public unicode input_required_name
        public unicode input_optional_name
        public unicode output_required_name
        public unicode output_optional_name
        public unicode default_value
        public unicode default_input_value
        public unicode default_output_value
        public unicode response_elem

        public unicode prefix_as_is     # a
        public unicode prefix_bool      # b
        public unicode prefix_csv       # c
        public unicode prefix_date      # dt
        public unicode prefix_date_time # dtm
        public unicode prefix_dict      # d
        public unicode prefix_dict_list # dl
        public unicode prefix_float     # f
        public unicode prefix_int       # i
        public unicode prefix_list      # l
        public unicode prefix_opaque    # o
        public unicode prefix_text      # t
        public unicode prefix_uuid      # u
        public unicode prefix_required  # +
        public unicode prefix_optional  # -

        # Global variables, can be always overridden on a per-declaration basis
        public object skip_empty_keys
        public object skip_empty_request_keys
        public object skip_empty_response_keys

    cdef bint is_int(self, name):
        """ Returns True if input name should be treated like ElemType.int.
        """

    cdef bint is_bool(self, name):
        """ Returns True if input name should be treated like ElemType.bool.
        """

    cdef bint is_secret(self, name):
        """ Returns True if input name should be treated like ElemType.secret.
        """

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

        # Whether all non-NotGiven optional input elements should be skipped or not
        bint _skip_all_empty_request_keys

        # A list of non-NotGiven optional input elements to skip
        list _skip_empty_request_keys

        # Whether all non-NotGiven optional output elements should be skipped or not
        bint _skip_all_empty_response_keys

        # A list of non-NotGiven optional output elements to skip
        list _skip_empty_response_keys

        # Name of the response element, or None if there should be no top-level one
        object _response_elem

        # Default value to use for optional input elements, unless overridden on a per-element basis
        object _default_input_value

        # Default value to use for optional output elements, unless overridden on a per-element basis
        object _default_output_value

        object _default_value # Preserved for backward-compatibility, the same as _default_output_value

# ################################################################################################################################

cdef class SimpleIO(object):
    """ If a service uses SimpleIO then, during deployment, its class will receive an attribute called _simpleio
    based on the service's SimpleIO attribute. The _simpleio one will be an instance of this Cython class.
    """
    cdef:
        # Server-wide configuration
        _SIOServerConfig server_config

        # Current service's configuration, after parsing
        SIODefinition definition

        # User-provided SimpleIO declaration, before parsing. This is parsed into self.definition.
        object declaration

# ################################################################################################################################

    def __cinit__(self, _SIOServerConfig server_config, object declaration):
        self.server_config = server_config
        self.definition = SIODefinition()
        self.declaration = declaration

# ################################################################################################################################

    cpdef build(self):
        """ Parses a user-defined SimpleIO declaration (currently, a Python class)
        and populates all the internal structures as needed.
        """
        self.build_input()
        self.build_output()

# ################################################################################################################################

    cdef build_input(self):
        """ Builds structures responsible for data that is to be provided on input.
        """

    cdef build_output(self):
        """ Builds structures responsible for data that is to be produced on output.
        """

# ################################################################################################################################

# Create server/process-wide singletons
NotGiven = _NotGiven()

# ################################################################################################################################

def run():

    # Bunch
    from bunch import Bunch, bunchify

    # Dummy SQLAlchemy classes
    class SA:
        def __init__(self, *ignored):
            pass

        def __add__(self, other):
            print(222, other)

        __radd__ = __add__

        def __sub__(self, other):
            print(333, other)

        __rsub__ = __sub__

    class MyUser:
        pass

# ################################################################################################################################

    class MySimpleIO:
        input_required = 'abc'

    class MySimpleIO:
        input_optional = 'abc'

    class MySimpleIO:
        output_required = 'abc'

    class MySimpleIO:
        output_optional = 'abc'

# ################################################################################################################################

    class MySimpleIO:
        input_required = 'abc', 'zxc'

    class MySimpleIO:
        input_optional = 'abc', 'zxc'

    class MySimpleIO:
        output_required = 'abc', 'zxc'

    class MySimpleIO:
        output_optional = 'abc', 'zxc'

# ################################################################################################################################

    class MySimpleIO:
        input = 'a:user_id', '-i:user_type', '-user_name', '+user_profile', Int('-abc'), AsIs('cust_id')
        output = '-d:last_visited', 'i:duration', Float('qqq'), Dict('rrr')

    class MySimpleIO:
        input = 'a:user_id', '-is_active'
        output = 'd:last_visited', 'i:duration'

    class MySimpleIO:
        input = SA(MyUser) + ('user_id', 'user_type'), 'is_admin', '-is_staff'
        output = SA(MyUser) - ('is_active', 'is_new'), 'i:user_category'

# ################################################################################################################################
