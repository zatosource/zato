# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import types
from decimal import Decimal as decimal_Decimal
from itertools import chain
from logging import getLogger
from traceback import format_exc
from uuid import UUID as uuid_UUID

# datetutil
from dateutil.parser import parse as dt_parse

# Zato
from zato.common import DATA_FORMAT
from zato.util_convert import to_bool

# Zato - Cython
from zato.bunch import Bunch, bunchify

# Python 2/3 compatibility
from past.builtins import basestring, str as past_str, unicode as past_unicode

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

_builtin_float = float
_builtin_int = int
_list_like = (list, tuple)

# Default value added for backward-compatibility with SimpleIO definitions created before the rewrite in Cython.
backward_compat_default_value = ''

prefix_optional = '-'

# ################################################################################################################################

cdef class _ForceEmptyKeyMarker(object):
    pass

# ################################################################################################################################

cdef class _NotGiven(object):
    """ Indicates that a particular value was not provided on input or output.
    """
    def __str__(self):
        return '<NotGiven>'

    def __bool__(self):
        return False # Always evaluates to a boolean False

cdef class _InternalNotGiven(_NotGiven):
    """ Like _NotGiven but used only internally.
    """

# ################################################################################################################################

cdef class SIODefault(object):

    cdef:
        public input_value
        public output_value

    def __init__(self, input_value, output_value, default_value):

        if input_value is InternalNotGiven:
            input_value = backward_compat_default_value if default_value is InternalNotGiven else default_value

        if output_value is InternalNotGiven:
            output_value = backward_compat_default_value if output_value is InternalNotGiven else default_value

        self.input_value = input_value
        self.output_value = output_value

# ################################################################################################################################

cdef class SIOSkipEmpty(object):

    cdef:
        public empty_output_value
        public set skip_input_set
        public set skip_output_set
        public set force_empty_input_set
        public set force_empty_output_set
        public bint skip_all_empty_input
        public bint skip_all_empty_output

    def __init__(self, input_def, output_def, force_empty_input_set, force_empty_output_set, empty_output_value):

        cdef bint skip_all_empty_input = False
        cdef bint skip_all_empty_output = False
        cdef set skip_input_set = set()
        cdef set skip_output_set = set()

        # Construct configuration for empty input values

        if input_def is not NotGiven:
            if input_def is True:
                skip_all_empty_input = True
            else:
                skip_input_set.update(set(input_def))

        # Likewise, for output values

        if output_def is not NotGiven:
            if output_def is True:
                skip_all_empty_output = True
            else:
                skip_output_set.update(set(output_def))

        # Assign all computed values for runtime usage

        self.empty_output_value = empty_output_value
        self.force_empty_input_set = set(force_empty_input_set or [])
        self.force_empty_output_set = set(force_empty_output_set or [])

        self.skip_input_set = skip_input_set
        self.skip_all_empty_input = skip_all_empty_input

        self.skip_output_set = skip_output_set
        self.skip_all_empty_output = skip_all_empty_output

# ################################################################################################################################

cdef class ParsingError(Exception):
    pass

# ################################################################################################################################

cdef enum ElemType:
    as_is         =  100
    bool          =  200
    csv           =  300
    date          =  400
    date_time     =  500
    decimal       =  500
    dict_         =  600
    dict_list     =  700
    float_         =  800
    int_           =  900
    list_         = 1000
    opaque        = 1100
    text          = 1200
    utc           = 1250 # Deprecated, do not use
    uuid          = 1300
    user_defined  = 1_000_000

# ################################################################################################################################

cdef class Elem(object):
    """ An individual input or output element. May be a ForceType instance or not.
    """
    cdef:
        ElemType _type
        unicode _name
        public object user_default_value
        public object default_value
        public bint is_required

        public dict parse_from # From external formats to Python objects
        public dict parse_to   # From Python objects to external formats

# ################################################################################################################################

    def __cinit__(self):
        self._type = ElemType.as_is
        self.parse_from = {}
        self.parse_to = {}

        self.parse_from[DATA_FORMAT.JSON] = self.from_json
        self.parse_from[DATA_FORMAT.XML] = self.from_xml
        self.parse_from[DATA_FORMAT.CSV] = self.from_csv

        self.parse_to[DATA_FORMAT.JSON] = self.to_json
        self.parse_to[DATA_FORMAT.XML] = self.to_xml
        self.parse_to[DATA_FORMAT.CSV] = self.to_csv

# ################################################################################################################################

    def __init__(self, name, **kwargs):

        if name.startswith(prefix_optional):
            name = name[1:]
            is_required = False
        else:
            is_required = True

        self.name = self._get_unicode_name(name)
        self.is_required = is_required
        self.user_default_value = self.default_value = kwargs.get('default', NotGiven)

    def __lt__(self, other):
        if isinstance(other, Elem):
            return self.name < other.name
        else:
            return self.name < other

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = self._get_unicode_name(name)

# ################################################################################################################################

    cdef unicode _get_unicode_name(self, object name):
        if name:
            if not isinstance(name, basestring):
                logger.warn('Name `%s` should be a str/bytes/unicode object rather than `%s`', name, type(name))
            if not isinstance(name, unicode):
                name = name.decode('utf8')

        return name

# ################################################################################################################################

    def set_default_value(self, sio_default_value):

        # If user did not provide a default value, we will use the one that is default for the SimpleIO class ..
        if self.user_default_value is NotGiven:
            self.default_value = sio_default_value

        # .. otherwise, user-defined default has priority.
        else:
            self.default_value = self.user_default_value

# ################################################################################################################################

    def __repr__(self):
        return '<{} at {} {}:{} d:{} r:{}>'.format(self.__class__.__name__, hex(id(self)), self.name, self._type,
            self.default_value, self.is_required)

# ################################################################################################################################

    __str__ = __repr__

# ################################################################################################################################

    def __cmp__(self, other):
        return self.name == other.name

# ################################################################################################################################

    def __hash__(self):
        return hash(self.name) # Names are always unique

# ################################################################################################################################

    @property
    def pretty(self):
        out = ''

        if not self.is_required:
            out += '-'

        out += self.name

        return out

# ################################################################################################################################

    @staticmethod
    def _not_implemented():
        raise NotImplementedError()

    from_json = _not_implemented
    to_json   = _not_implemented

    from_xml  = _not_implemented
    to_xml    = _not_implemented

    from_csv  = _not_implemented
    to_csv    = _not_implemented

# ################################################################################################################################

cdef class AsIs(Elem):
    def __cinit__(self):
        self._type = ElemType.as_is

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value

    def from_json(self, value):
        return AsIs.from_json_static(value)

    to_json = from_json

# ################################################################################################################################

cdef class Bool(Elem):
    def __cinit__(self):
        self._type = ElemType.bool

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return to_bool(value)

    def from_json(self, value):
        return Bool.from_json_static(value)

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

cdef class CSV(Elem):
    def __cinit__(self):
        self._type = ElemType.csv

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value.split(',')

    def from_json(self, value):
        return CSV.from_json_static(value)

    from_xml = from_json

    def to_json(self, value, *ignored):
        return ','.join(value) if isinstance(value, (list, tuple)) else value

    to_xml = to_json

# ################################################################################################################################

cdef class Date(Elem):

    def __cinit__(self):
        self._type = ElemType.date

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        try:
            return dt_parse(value)
        except ValueError as e:
            # This is the only way to learn about what kind of exception we caught
            raise ValueError('Could not parse `{}` as a {} object ({})'.format(value, kwargs['class_name'], e.args[0]))

    def from_json(self, value):
        return Date.from_json_static(value, class_name=self.__class__.__name__)

# ################################################################################################################################

cdef class DateTime(Date):
    def __cinit__(self):
        self._type = ElemType.date_time

# ################################################################################################################################

cdef class Decimal(Elem):
    def __cinit__(self):
        self._type = ElemType.decimal

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return decimal_Decimal(value)

    def from_json(self, value):
        return Decimal.from_json_static(value)

# ################################################################################################################################

cdef class Dict(Elem):

    cdef:
        public set _keys_required
        public set _keys_optional
        public SIOSkipEmpty skip_empty

    def __cinit__(self):
        self._type = ElemType.dict_
        self._keys_required = set()
        self._keys_optional = set()

    def __init__(self, name, *args, **kwargs):
        super(Dict, self).__init__(name, **kwargs)

        for arg in args:
            if isinstance(arg, Elem):
                is_required = arg.is_required
                to_add = arg
            else:
                is_required = not arg.startswith(prefix_optional)
                to_add = arg if is_required else arg[1:]

            if is_required:
                self._keys_required.add(to_add)
            else:
                self._keys_optional.add(to_add)

# ################################################################################################################################

    def set_default_value(self, sio_default_value):
        super(Dict, self).set_default_value(sio_default_value)

        for key in chain(self._keys_required, self._keys_optional):
            if isinstance(key, Elem):
                key.set_default_value(sio_default_value)

# ################################################################################################################################

    def set_skip_empty(self, skip_empty):
        self.skip_empty = skip_empty

# ################################################################################################################################

    @staticmethod
    def from_json_static(data, keys_required, keys_optional, default_value, *args, **kwargs):

        if not isinstance(data, dict):
            raise ValueError('Expected a dict instead of `{!r}` ({})'.format(data, type(data).__name__))

        # Do we have any keys required or optional to check?
        if keys_required or keys_optional:

            # Output we will return
            out = {}

            # All the required and optional keys
            for keys, is_required in ((keys_required, True), (keys_optional, False)):
                for elem in keys:
                    is_elem = isinstance(elem, Elem)
                    key = elem.name if is_elem else elem
                    value = data.get(key, NotGiven)

                    # If we did not have such a key on input ..
                    if value is NotGiven:

                        # .. raise an exception if it was one one of required ones ..
                        if is_required:
                            raise ValueError('Key `{}` not found in `{}`'.format(key, data))

                        # .. but if it was an optional key, provide a default value in lieu of it.
                        else:
                            out[key] = default_value

                    # Right, we found this key on input, what to do next ..
                    else:
                        # .. enter into the nested element if it is a SimpleIO one ..
                        if is_elem:

                            # Various Elem subclasses will required various parameters on input to from_json_static
                            args = []
                            dict_keys = [elem._keys_required, elem._keys_optional] if isinstance(elem, Dict) else [None, None]
                            args.extend(dict_keys)
                            args.append(elem.default_value)

                            out[key] = elem.from_json_static(value, *args, class_name=elem.__class__.__name__)

                        # .. otherwise, simply assign the value to key.
                        else:
                            out[key] = value

            return out

        # No keys required nor optional found, we return data as is
        else:
            return data

# ################################################################################################################################

    def from_json(self, value):
        return Dict.from_json_static(value, self._keys_required, self._keys_optional, self.default_value)

# ################################################################################################################################

cdef class DictList(Dict):
    def __cinit__(self):
        self._type = ElemType.dict_list

    @staticmethod
    def from_json_static(value, keys_required, keys_optional, default_value, *args, **kwargs):
        out = []
        for elem in value:
            out.append(Dict.from_json_static(elem, keys_required, keys_optional, default_value))
        return out

    def from_json(self, value):
        return DictList.from_json_static(value, self._keys_required, self._keys_optional, self.default_value)

# ################################################################################################################################

cdef class Float(Elem):
    def __cinit__(self):
        self._type = ElemType.float_

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return _builtin_float(value)

    def from_json(self, value):
        return Float.from_json_static(value)

# ################################################################################################################################

cdef class Int(Elem):
    def __cinit__(self):
        self._type = ElemType.int_

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return _builtin_int(value)

    def from_json(self, value):
        return Int.from_json_static(value)

# ################################################################################################################################

cdef class List(Elem):
    def __cinit__(self):
        self._type = ElemType.list_

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value if isinstance(value, _list_like) else [value]

    def from_json(self, value):
        return List.from_json_static(value)

# ################################################################################################################################

cdef class Opaque(Elem):
    def __cinit__(self):
        self._type = ElemType.opaque

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value

    def from_json(self, value):
        return Opaque.from_json_static(value)

    from_xml = to_xml = from_json

# ################################################################################################################################

cdef class Text(Elem):

    cdef:
        public str encoding

    def __cinit__(self):
        self._type = ElemType.text

    def __init__(self, name, **kwargs):
        super(Text, self).__init__(name, **kwargs)
        self.encoding = kwargs.get('encoding', 'utf8')

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        if isinstance(value, basestring):
            return value
        else:
            if isinstance(value, past_unicode):
                return value
            else:
                if isinstance(value, past_str):
                    encoding = kwargs.get('encoding') or 'utf8'
                    return past_unicode(value, encoding)
                else:
                    return past_unicode(value)

    def from_json(self, value):
        return Text.from_json_static(value, encoding=self.encoding)

# ################################################################################################################################

cdef class UTC(Elem):
    def __cinit__(self):
        self._type = ElemType.utc

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value.replace('+00:00', '')

    def from_json(self, value):
        return Opaque.from_json_static(value)

    from_xml = to_xml = from_json

# ################################################################################################################################

cdef class UUID(Elem):

    def __cinit__(self):
        self._type = ElemType.uuid

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return uuid_UUID(value)

    def from_json(self, value):
        return UUID.from_json_static(value)

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

cdef class SIOServerConfig(object):
    """ Contains global SIO configuration. Each service's _sio attribute
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

        # Python 2/3 compatibility
        public unicode bytes_to_str_encoding

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

    def get_elem_names(self, use_sorted=False):
        out = [elem.name for elem in self.elems]
        return sorted(out) if use_sorted else out

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

        # Default values to use for optional elements, unless overridden on a per-element basis
        public SIODefault sio_default

        # Which empty values should not be prodcued from input / sent on output, unless overridden by each element
        public SIOSkipEmpty skip_empty

        # Name of the service this definition is for
        unicode _service_name

        # Name of the response element, or None if there should be no top-level one
        object _response_elem

    def __cinit__(self):
        self._input_required = SIOList()
        self._input_optional = SIOList()
        self._output_required = SIOList()
        self._output_optional = SIOList()

    def __init__(self, SIODefault sio_default, SIOSkipEmpty skip_empty):
        self.sio_default = sio_default
        self.skip_empty = skip_empty

    cdef unicode get_elems_pretty(self, SIOList required_list, SIOList optional_list):
        cdef unicode out = ''

        if required_list.elems:
            out += ', '.join(required_list.get_elem_names())

        if optional_list.elems:
            # Separate with a semicolon only if there is some required part to separate it from
            if required_list.elems:
                out += '; '
            out += ', '.join('-' + elem for elem in optional_list.get_elem_names())

        return out

    cdef unicode get_input_pretty(self):
        return self.get_elems_pretty(self._input_required, self._input_optional)

    cdef unicode get_output_pretty(self):
        return self.get_elems_pretty(self._output_required, self._output_optional)

    def __str__(self):
        return '<{} at {}, input:`{}`, output:`{}`>'.format(self.__class__.__name__, hex(id(self)),
            self.get_input_pretty(), self.get_output_pretty())

# ################################################################################################################################

cdef class CySimpleIO(object):
    """ If a service uses SimpleIO then, during deployment, its class will receive an attribute called _sio
    based on the service's SimpleIO attribute. The _sio one will be an instance of this Cython class.
    """
    cdef:
        # Server-wide configuration
        SIOServerConfig server_config

        # Current service's configuration, after parsing
        public SIODefinition definition

        # User-provided SimpleIO declaration, before parsing. This is parsed into self.definition.
        object user_declaration

        # Kept for backward compatibility with 3.0
        bint has_bool_force_empty_keys

# ################################################################################################################################

    def __cinit__(self, SIOServerConfig server_config, object user_declaration):

        input_value = getattr(user_declaration, 'default_input_value', InternalNotGiven)
        output_value = getattr(user_declaration, 'default_output_value', InternalNotGiven)
        default_value = getattr(user_declaration, 'default_value', InternalNotGiven)

        cpdef SIODefault sio_default = SIODefault(input_value, output_value, default_value)

        raw_skip_empty = getattr(user_declaration, 'skip_empty_keys', NotGiven)
        class_skip_empty = getattr(user_declaration, 'SkipEmpty', NotGiven)

        # Quick input validation - we cannot have both kinds of configuration
        if (raw_skip_empty is not NotGiven) and (class_skip_empty is not NotGiven):
            raise ValueError('Cannot specify both skip_empty_input and SkipEmpty in a SimpleIO definition')

        # Note that to retain backward compatibility, it is force_empty_keys instead of force_empty_output_set
        raw_force_empty_output_set = getattr(user_declaration, 'force_empty_keys', NotGiven)
        if raw_force_empty_output_set in (True, False):
            self.has_bool_force_empty_keys = True
        else:
            self.has_bool_force_empty_keys = False # Initialize it explicitly

        # Again, quick input validation
        if (raw_force_empty_output_set is not NotGiven) and (class_skip_empty is not NotGiven):
            raise ValueError('Cannot specify both force_empty_keys and SkipEmpty in a SimpleIO definition')

        if class_skip_empty is NotGiven:
            empty_output_value = NotGiven
            input_def = raw_skip_empty if raw_skip_empty is not NotGiven else NotGiven
            output_def = NotGiven
            force_empty_input_set = NotGiven
            force_empty_output_set = raw_force_empty_output_set if raw_force_empty_output_set is not NotGiven else NotGiven

        else:
            empty_output_value = getattr(class_skip_empty, 'empty_output_value', InternalNotGiven)

            # We cannot have NotGiven as the default output value, it cannot be serialized in a meaningful way
            if empty_output_value is NotGiven:
                raise ValueError('NotGiven cannot be used as empty_output_value')

            input_def = getattr(class_skip_empty, 'input', NotGiven)
            output_def = getattr(class_skip_empty, 'output_def', NotGiven)
            force_empty_input_set = getattr(class_skip_empty, 'force_empty_input', NotGiven)
            force_empty_output_set = getattr(class_skip_empty, 'force_empty_output', NotGiven)

        if isinstance(input_def, basestring):
            input_def = [input_def]

        if isinstance(output_def, basestring):
            output_def = [output_def]

        if isinstance(force_empty_input_set, basestring):
            force_empty_input_set = [force_empty_input_set]

        if isinstance(force_empty_output_set, basestring):
            force_empty_output_set = [force_empty_output_set]

        elif self.has_bool_force_empty_keys:
            force_empty_output_set = [_ForceEmptyKeyMarker()]

        cpdef SIOSkipEmpty sio_skip_empty = SIOSkipEmpty(input_def, output_def, force_empty_input_set,
            force_empty_output_set, empty_output_value)

        self.definition = SIODefinition(sio_default, sio_skip_empty)
        self.server_config = server_config
        self.user_declaration = user_declaration

# ################################################################################################################################

    cdef _resolve_bool_force_empty_keys(self):
        self.definition.skip_empty.force_empty_output_set = set(self.definition._output_optional.get_elem_names())

# ################################################################################################################################

    cpdef build(self, object class_):
        """ Parses a user-defined SimpleIO declaration (currently, a Python class)
        and populates all the internal structures as needed.
        """
        self._build_io_elems('input', class_)
        self._build_io_elems('output', class_)

        # Now that we have all the elements, and if we have a definition using 'force_empty_keys = True' (or False),
        # we need to turn the _ForceEmptyKeyMarker into an acutal list of elements to force into empty keys.
        if self.has_bool_force_empty_keys:
            self._resolve_bool_force_empty_keys()

# ################################################################################################################################

    cdef Elem _convert_to_elem_instance(self, elem, container, is_required):

        # By default, we always return Text instances for elements that do not specify an SIO type
        cdef Text _elem

        _elem = Text(elem)
        _elem.name = elem
        _elem.is_required = is_required

        return _elem

# ################################################################################################################################

    cdef _build_io_elems(self, container, class_):
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
        if isinstance(plain, (basestring, Elem)):
            plain = [plain]

        if isinstance(required, (basestring, Elem)):
            required = [required]

        if isinstance(optional, (basestring, Elem)):
            optional = [optional]

        # At this point we have either a list of plain elements or input_required/input_optional, but not both.
        # In the former case, we need to build required and optional lists manually by extracting
        # all the elements from the plain list.
        if plain:

            for elem in plain:

                is_sio_elem = isinstance(elem, Elem)
                elem_name = elem.name if is_sio_elem else elem

                if elem_name.startswith(prefix_optional):
                    elem_name_no_prefix = elem_name.replace(prefix_optional, '')
                    optional.append(elem if is_sio_elem else elem_name_no_prefix)
                else:
                    required.append(elem if is_sio_elem else elem_name)

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

                # All of our elements are always SimpleIO objects
                if not isinstance(elem, Elem):
                    elem = self._convert_to_elem_instance(elem, container, is_required)

                # Make sure all elements have a default value, either a user-defined one or the SimpleIO-level configured one
                sio_default_value = self.definition.sio_default.input_value if container == 'input' else \
                    self.definition.sio_default.output_value

                elem.set_default_value(sio_default_value)

                if is_required:
                    _required.append(elem)
                else:
                    _optional.append(elem)

        required = _required
        optional = _optional

        # Confirm that required elements do not overlap with optional ones
        shared_elems = set(elem.name for elem in required) & set(elem.name for elem in optional)

        if shared_elems:
            raise ValueError('Elements in {}_required and {}_optional cannot be shared, found:`{}` in `{}`'.format(
                    container, container, sorted(elem for elem in shared_elems), class_))

        # Everything is validated, we can actually set the lists of elements now

        container_req_name = '_{}_required'.format(container)
        container_required = getattr(self.definition, container_req_name)
        container_required.set_elems(required)

        container_opt_name = '_{}_optional'.format(container)
        container_optional = getattr(self.definition, container_opt_name)
        container_optional.set_elems(optional)

# ################################################################################################################################

    @staticmethod
    def attach_sio(server_config, class_):
        """ Given a service class, the method extracts its user-defined SimpleIO definition
        and attaches the Cython-based one to the class's _sio attribute.
        """
        try:
            # Get the user-defined SimpleIO definition
            user_sio = getattr(class_, 'SimpleIO', None)

            # This class does not use SIO so we can just return immediately
            if not user_sio:
                return

            # Attach the Cython object representing the parsed user definition
            cy_simple_io = CySimpleIO(server_config, user_sio)
            cy_simple_io.build(class_)
            class_._sio = cy_simple_io

        except Exception:
            logger.warn('Could not attach SimpleIO to class `%s`, e:`%s`', class_, format_exc())
            raise

# ################################################################################################################################

    cdef bint _should_skip_on_input(self, SIODefinition definition, Elem sio_item, input_value) except -1:
        cdef bint should_skip = False

        # Should we skip this value ..
        if definition.skip_empty.skip_all_empty_input or sio_item.name in definition.skip_empty.skip_input_set:

            # .. possibly, unless we are forced not to include it.
            if sio_item.name not in definition.skip_empty.force_empty_input_set:
                return True

        # In all other cases, we explicitly say that this value should not be skipped
        return False

# ################################################################################################################################

    cdef dict _parse_input_elem(self, elem, unicode data_format):

        if not isinstance(elem, dict):
            raise ValueError('Expected a dict instead of `{!r}` ({})'.format(elem, type(elem).__name__))

        cdef dict out = {}

        for sio_item in chain(self.definition._input_required, self.definition._input_optional):
            input_value = elem.get(sio_item.name, InternalNotGiven)

            # We do not have such a key on input so an exception needs to be raised if this is a require one
            if input_value is InternalNotGiven:
                if sio_item.is_required:
                    raise ValueError('No such key `{}` among `{}` in `{}`'.format(sio_item.name, elem.keys(), elem))
                else:
                    if self._should_skip_on_input(self.definition, sio_item, input_value):
                        # Continue to the next sio_item
                        continue
                    else:
                        value = sio_item.default_value
            else:
                parse_func = sio_item.parse_from[data_format]
                value = parse_func(input_value)

            # We get here only if should_skip is not True
            out[sio_item.name] = value

        return out

# ################################################################################################################################

    cpdef parse_input(self, data, data_format):

        if isinstance(data, list):
            out = []
            for elem in data:
                converted = self._parse_input_elem(elem, data_format)
                out.append(bunchify(converted))
            return out
        else:
            out = self._parse_input_elem(data, data_format)
            return bunchify(out)

# ################################################################################################################################

# Create server/process-wide singletons
NotGiven = _NotGiven()

# Akin to NotGiven but must not be used by users
InternalNotGiven = _InternalNotGiven()

# ################################################################################################################################
