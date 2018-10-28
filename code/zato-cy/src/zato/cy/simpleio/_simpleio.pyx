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
        set exact
        set prefixes
        set suffixes

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
        public unicode prefix_date      # date
        public unicode prefix_date_time # dt
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
SIOServerConfig = _SIOServerConfig()

# ################################################################################################################################

def run():

    # Bunch
    from bunch import Bunch, bunchify

    server_config = Bunch()

    server_config.bool = Bunch()
    server_config.bool.exact  = set()
    server_config.bool.prefix = set(['by_', 'has_', 'is_', 'may_', 'needs_', 'should_'])
    server_config.bool.suffix = set()

    server_config.int = Bunch()
    server_config.int.exact  = set(['id'])
    server_config.int.prefix = set()
    server_config.int.suffix = set(['_count', '_id', '_size', '_timeout'])

    server_config.secret = Bunch()
    server_config.secret.exact  = set(['id'])
    server_config.secret.prefix = set(['auth_data', 'auth_token', 'password', 'password1', 'password2', 'secret_key', 'token'])
    server_config.secret.suffix = set()

    server_config.default = Bunch()

    server_config.default.default_value = None
    server_config.default.default_input_value = None
    server_config.default.default_output_value = None

    server_config.default.response_elem = None

    server_config.default.input_required_name = 'input_required'
    server_config.default.input_optional_name = 'input_optional'
    server_config.default.output_required_name = 'output_required'
    server_config.default.output_optional_name = 'output_optional'

    server_config.default.skip_empty_keys = False
    server_config.default.skip_empty_request_keys = False
    server_config.default.skip_empty_response_keys = False

    server_config.default.prefix_as_is = 'a'
    server_config.default.prefix_bool = 'b'
    server_config.default.prefix_csv = 'c'
    server_config.default.prefix_date = 'date'
    server_config.default.prefix_date_time = 'dt'
    server_config.default.prefix_dict = 'd'
    server_config.default.prefix_dict_list = 'dl'
    server_config.default.prefix_float = 'f'
    server_config.default.prefix_int = 'i'
    server_config.default.prefix_list = 'l'
    server_config.default.prefix_opaque = 'o'
    server_config.default.prefix_text = 't'
    server_config.default.prefix_uuid = 'u'
    server_config.default.prefix_required = '+'
    server_config.default.prefix_optional = '-'

    bool_config = BoolConfig()
    bool_config.exact = server_config.bool.exact
    bool_config.prefixes = server_config.bool.prefix
    bool_config.suffixes = server_config.bool.suffix

    int_config = IntConfig()
    int_config.exact = server_config.int.exact
    int_config.prefixes = server_config.int.prefix
    int_config.suffixes = server_config.int.suffix

    secret_config = SecretConfig()
    secret_config.exact = server_config.secret.exact
    secret_config.prefixes = server_config.secret.prefix
    secret_config.suffixes = server_config.secret.suffix

# ################################################################################################################################

    SIOServerConfig.bool_config = bool_config
    SIOServerConfig.int_config = int_config
    SIOServerConfig.secret_config = secret_config

    SIOServerConfig.input_required_name = server_config.default.input_required_name
    SIOServerConfig.input_optional_name = server_config.default.input_optional_name
    SIOServerConfig.output_required_name = server_config.default.output_required_name
    SIOServerConfig.output_optional_name = server_config.default.output_optional_name
    SIOServerConfig.default_value = server_config.default.default_value
    SIOServerConfig.default_input_value = server_config.default.default_input_value
    SIOServerConfig.default_output_value = server_config.default.default_output_value

    SIOServerConfig.response_elem = server_config.default.response_elem

    SIOServerConfig.skip_empty_keys = server_config.default.skip_empty_keys
    SIOServerConfig.skip_empty_request_keys = server_config.default.skip_empty_request_keys
    SIOServerConfig.skip_empty_response_keys = server_config.default.skip_empty_response_keys

    SIOServerConfig.prefix_as_is = server_config.default.prefix_as_is
    SIOServerConfig.prefix_bool = server_config.default.prefix_bool
    SIOServerConfig.prefix_csv = server_config.default.prefix_csv
    SIOServerConfig.prefix_date = server_config.default.prefix_date
    SIOServerConfig.prefix_date_time = server_config.default.prefix_date_time
    SIOServerConfig.prefix_dict = server_config.default.prefix_dict
    SIOServerConfig.prefix_dict_list = server_config.default.prefix_dict_list
    SIOServerConfig.prefix_float = server_config.default.prefix_float
    SIOServerConfig.prefix_int = server_config.default.prefix_int
    SIOServerConfig.prefix_list = server_config.default.prefix_list
    SIOServerConfig.prefix_opaque = server_config.default.prefix_opaque
    SIOServerConfig.prefix_text = server_config.default.prefix_text
    SIOServerConfig.prefix_uuid = server_config.default.prefix_uuid
    SIOServerConfig.prefix_required = server_config.default.prefix_required
    SIOServerConfig.prefix_optional = server_config.default.prefix_optional

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

    class MySimpleIO:
        input_required = 'abc'

    class MySimpleIO2:
        input = 'a:user_id', '-i:user_type', '-user_name', '+user_profile', Int('-abc'), AsIs('cust_id')
        output = '-d:last_visited', 'i:duration', Float('qqq'), Dict('rrr')

    class MySimpleIO3:
        input = 'a:user_id', '-is_active'
        output = 'd:last_visited', 'i:duration'

    class MySimpleIO4:
        input = SA(MyUser) + ('user_id', 'user_type'), 'is_admin', '-is_staff'
        output = SA(MyUser) - ('is_active', 'is_new'), 'i:user_category'

    sio = SimpleIO(SIOServerConfig, MySimpleIO)
    sio.build()

    print(111, SIOServerConfig.bool_config)

# ################################################################################################################################

if __name__ == '__main__':
    run()

# ################################################################################################################################
