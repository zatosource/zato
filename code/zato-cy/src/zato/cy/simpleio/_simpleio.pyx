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
        public unicode _name
        ElemType _type
        object _default
        bint _is_required

    def __str__(self):
        return '<{} at {} {}:{} d:{} r:{}>'.format(self.__class__.__name__, hex(id(self)), self._name, self._type,
            self._default, self._is_required)

    __repr__ = __str__

    def __cmp__(self, other):
        return self._name == other._name

    def __hash__(self):
        return hash(self._name) # Names are always unique

    @property
    def pretty(self):
        out = ''

        if not self._is_required:
            out += '-'

        out += self._name

        return out

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

cdef class Text(Elem):
    def __cinit__(self):
        self._type = ElemType.text

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

cdef class SIOList(object):
    """ Represents one of input/output required/optional.
    """
    cdef:
        list elems

    def __cinit__(self):
        self.elems = []

    def __iter__(self):
        return iter(self.elems)

    def set_elems(self, elems):
        self.elems[:] = elems

# ################################################################################################################################

cdef class SIODefinition(object):
    """ A single SimpleIO definition attached to a service.
    """
    cdef:

        # A list of Elem items required on input
        public SIOList _input_required

        # A list of Elem items optional on input
        public SIOList _input_optional

        # A list of Elem items required on output
        public SIOList _output_required

        # A list of Elem items optional on output
        public SIOList _output_optional

        # Name of the service this definition is for
        unicode _service_name
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

    def __cinit__(self):
        self._input_required = SIOList()
        self._input_optional = SIOList()
        self._output_required = SIOList()
        self._output_optional = SIOList()

    cdef list get_input_pretty(self):
        cdef list required = []
        cdef list optional = []
        cdef list out = []

        for item in self._input_required:
            print(item)

        return out

    cdef list get_output_pretty(self):
        cdef list required = []
        cdef list optional = []
        cdef list out = []

        return out

    def __str__(self):
        return '<{} at {}, input:`{}`, output:`{}`>'.format(self.__class__.__name__, hex(id(self)),
            self.get_input_pretty(), self.get_output_pretty())

# ################################################################################################################################

cdef class SimpleIO(object):
    """ If a service uses SimpleIO then, during deployment, its class will receive an attribute called _simpleio
    based on the service's SimpleIO attribute. The _simpleio one will be an instance of this Cython class.
    """
    cdef:
        # Server-wide configuration
        _SIOServerConfig server_config

        # Current service's configuration, after parsing
        public SIODefinition definition

        # User-provided SimpleIO declaration, before parsing. This is parsed into self.definition.
        object user_declaration

# ################################################################################################################################

    def __cinit__(self, _SIOServerConfig server_config, object user_declaration):
        self.server_config = server_config
        self.definition = SIODefinition()
        self.user_declaration = user_declaration

# ################################################################################################################################

    cpdef build(self):
        """ Parses a user-defined SimpleIO declaration (currently, a Python class)
        and populates all the internal structures as needed.
        """
        self._build_io_elems('input')
        self._build_io_elems('output')

# ################################################################################################################################

    cdef Elem _convert_to_elem_instance(self, elem, is_required):
        cdef Text _elem # For now, we always return Text instances

        _elem = Text()
        _elem._name = elem
        _elem._default = 'QQQ'
        _elem._is_required = is_required

        return _elem

# ################################################################################################################################

    cdef _build_io_elems(self, container):
        """ Returns I/O elems, e.g. input or input_required but first ensures that only correct elements are given in SimpleIO,
        e.g. if input is on input then input_required or input_optional cannot be.
        """
        required_name = '{}_required'.format(container)
        optional_name = '{}_optional'.format(container)

        plain = getattr(self.user_declaration, container, [])
        required = getattr(self.user_declaration, required_name, [])
        optional = getattr(self.user_declaration, optional_name, [])

        # If the plain element alone is given, we cannot have required or optional lists.
        if plain and (required or optional):
            if required and optional:
                details = '{}_required/{}_optional'.format(container, container)
            elif required:
                details = '{}_required'.format(container)
            elif optional:
                details = '{}_optional'.format(container)

            msg = 'Cannot provide {details} if {container} is given'
            msg += ', {container}:`{plain}`, {container}_required:`{required}`, {container}_optional:`{optional}`'

            raise ValueError(msg.format(**{
                'details': details,
                'container': container,
                'plain': plain,
                'required': required,
                'optional': optional
            }))

        # It is possible that nothing is to be given on input or produced, which is fine, we do not reject it
        # but there is no reason to continue either.
        if not (plain or required or optional):
            return

        # Listify all the elements provided
        if isinstance(plain, basestring):
            plain = [plain]

        if isinstance(required, basestring):
            required = [required]

        if isinstance(optional, basestring):
            optional = [optional]

        # At this point we have either a list of plain elements or input_required/input_optional, but not both.
        # In the former case, we need to build required and optional lists manually by extracting
        # all the elements from the plain list.
        if plain:

            prefix_optional = self.server_config.prefix_optional

            for elem in plain:
                if elem.startswith(prefix_optional):
                    optional.append(elem.replace(prefix_optional, ''))
                else:
                    required.append(elem)

        # So that in runtime elements are always checked in the same order
        required = sorted(required)
        optional = sorted(optional)

        # Now, convert all elements to Elem instances
        _required = []
        _optional = []

        elems = (
            (required, True),
            (optional, False),
        )

        for elem_list, is_required in elems:
            for elem in elem_list:
                if not isinstance(elem, Elem):
                    elem = self._convert_to_elem_instance(elem, is_required)
                    if is_required:
                        _required.append(elem)
                    else:
                        _optional.append(elem)

        required = _required
        optional = _optional

        # Confirm that required elements do not overlap with optional ones
        shared_elems = set(elem._name for elem in required) & set(elem._name for elem in optional)

        if shared_elems:
            raise ValueError('Elements in input_required and input_optional cannot be shared, found:`{}`'.format(
                sorted(elem.encode('utf8') for elem in shared_elems)))

        # Everything is validated, we can actually set the lists of elements now

        container_req_name = '_{}_required'.format(container)
        container_required = getattr(self.definition, container_req_name)
        container_required.set_elems(required)

        container_opt_name = '_{}_optional'.format(container)
        container_optional = getattr(self.definition, container_opt_name)
        container_optional.set_elems(optional)

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
