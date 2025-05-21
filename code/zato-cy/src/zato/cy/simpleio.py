# -*- coding: utf-8 -*-

# cython: auto_pickle=False

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from builtins import bool as stdlib_bool
from copy import deepcopy
from csv import DictWriter, reader as csv_reader
from datetime import date as stdlib_date, datetime as stdlib_datetime
from decimal import Decimal as decimal_Decimal
from io import StringIO
from json import JSONEncoder
from itertools import chain
from logging import getLogger
from traceback import format_exc
from uuid import UUID as uuid_UUID

# Cython
import cython as cy

# datetutil
from dateutil.parser import parse as dt_parse

# lxml
from lxml.etree import _Element as EtreeElementClass, SubElement, XPath

# Zato
from zato.common.api import APISPEC, DATA_FORMAT, ZATO_NONE
from zato.common.marshal_.api import ElementMissing
from zato.common.odb.api import SQLRow
from zato.common.pubsub import PubSubMessage
from zato.util_convert import to_bool

# Zato - Cython
from zato.bunch import Bunch, bunchify

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring, str as past_str

# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

_zato_none:str = ZATO_NONE

_builtin_float = float
_builtin_int = int
_list_like = (list, tuple)

# Default value added for backward-compatibility with SimpleIO definitions created before the rewrite in Cython.
backward_compat_default_value = ''

prefix_optional = '-'

# Dictionaries that map our own CSV parameters to stdlib's ones
_csv_common_attr_map:dict = {
    'dialect': 'dialect',
    'delimiter': 'delimiter',
    'needs_double_quote': 'doublequote',
    'escape_char': 'escapechar',
    'line_terminator': 'lineterminator',
    'quote_char': 'quotechar',
    'quoting': 'quoting',
    'should_skip_initial_space': 'skipinitialspace',
    'is_strict': 'strict',
}

_csv_writer_attr_map:dict = {
    'on_missing': 'restval',
    'on_extra': 'extrasaction',
}

# ################################################################################################################################

DATA_FORMAT_CSV:object  = DATA_FORMAT.CSV
DATA_FORMAT_DICT:object = DATA_FORMAT.DICT
DATA_FORMAT_JSON:object = DATA_FORMAT.JSON
DATA_FORMAT_POST:object = DATA_FORMAT.POST
DATA_FORMAT_FORM:object = DATA_FORMAT.FORM_DATA

# ################################################################################################################################

def _not_implemented(func):
    def _inner(*args, **kwargs):
        raise NotImplementedError('{} - operation not implemented'.format(func))
    return _inner

# ################################################################################################################################

class SIOJSONEncoder(JSONEncoder):

    def __init__(self, *args, **kwargs):
        super(SIOJSONEncoder, self).__init__(*args, **kwargs)
        self.bytes_to_str_encoding = None # type: str

    def default(self, value):
        if isinstance(value, bytes):
            # Ultimately, this should use bytes_to_str_encoding
            return value.decode(self.bytes_to_str_encoding)

# ################################################################################################################################

@cy.cclass
class _ForceEmptyKeyMarker:
    pass

# ################################################################################################################################

@cy.cclass
class _NotGiven:
    """ Indicates that a particular value was not provided on input or output.
    """
    def __str__(self):
        return '<_NotGiven>'

    def __bool__(self):
        return False # Always evaluates to a boolean False

@cy.cclass
class _InternalNotGiven(_NotGiven):
    """ Like _NotGiven but used only internally.
    """
    def __str__(self):
        return '<_InternalNotGiven>'

# ################################################################################################################################

class ServiceInput(Bunch):
    """ A Bunch holding input data for a service.
    """
    def __getattr__(self, name):
        try:
            return super(ServiceInput, self).__getattr__(name)
        except AttributeError:
            raise AttributeError('No such key `{}` among `{}`'.format(name, self))

    def deepcopy(self):
        return deepcopy(self)

    def require_any(self, *elems):
        for name in elems:
            if self.get(name):
                break
        else:
            raise ValueError('At least one of `{}` is required'.format(', '.join(elems)))

# ################################################################################################################################

@cy.cclass
class SIODefault:

    input_value = cy.declare(object, visibility='public') # type: object
    output_value = cy.declare(object, visibility='public') # type: object

    def __init__(self, input_value, output_value, default_value):

        if input_value is InternalNotGiven:
            input_value = backward_compat_default_value if default_value is InternalNotGiven else default_value

        if output_value is InternalNotGiven:
            output_value = backward_compat_default_value if output_value is InternalNotGiven else default_value

        self.input_value = input_value
        self.output_value = output_value

# ################################################################################################################################

@cy.cclass
class SIOSkipEmpty:

    empty_output_value     = cy.declare(object, visibility='public') # type: object
    skip_input_set         = cy.declare(set, visibility='public')    # type: set
    skip_output_set        = cy.declare(set, visibility='public')    # type: set
    force_empty_input_set  = cy.declare(set, visibility='public')    # type: set
    force_empty_output_set = cy.declare(set, visibility='public')    # type: set

    skip_all_empty_input   = cy.declare(cy.bint, visibility='public') # type: bool
    skip_all_empty_output  = cy.declare(cy.bint, visibility='public') # type: bool

    has_skip_input_set = cy.declare(cy.bint, visibility='public') # type: bool

    def __init__(self, input_def, output_def, force_empty_input_set, force_empty_output_set, empty_output_value):

        skip_all_empty_input:cy.bint = False
        skip_all_empty_output:cy.bint = False
        skip_input_set:set = set()
        skip_output_set:set = set()

        # Construct configuration for empty input values

        if input_def is not NotGiven:
            if input_def is True:
                skip_all_empty_input = True
            elif input_def is False:
                skip_all_empty_input = False
            else:
                skip_input_set.update(set(input_def))

        # Likewise, for output values

        if output_def is not NotGiven:
            if output_def is True:
                skip_all_empty_output = True
            elif output_def is False:
                skip_all_empty_output = False
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

        self.has_skip_input_set = bool(self.skip_input_set)

# ################################################################################################################################

@cy.cclass
class ParsingError(Exception):
    pass

# ################################################################################################################################

@cy.cclass
class SerialisationError(Exception):
    pass

# ################################################################################################################################

@cy.cclass
class ElemType:
    as_is:int         =  1000
    bool:int          =  2000
    csv:int           =  3000
    date:int          =  4000
    date_time:int     =  5000
    decimal:int       =  5000
    dict_:int         =  6000
    dict_list:int     =  7000
    float_:int        =  8000
    int_:int          =  9000
    list_:int         = 10000
    secret:int        = 11000
    text:int          = 12000
    utc:int           = 13000 # Deprecated, do not use
    uuid:int          = 14000
    user_defined:int  = 1_000_000

# ################################################################################################################################

# Useful to make sure no attribute lookups for 'text' under ElemType as performed in runtime
sio_text_type:int = ElemType.text

# ################################################################################################################################

@cy.cclass
class Elem:
    """ An individual input or output element. May be a ForceType instance or not.
    """
    _type  = cy.declare(cy.int, visibility='public')     # type: int
    _name  = cy.declare(object, visibility='public') # type: str
    _xpath = cy.declare(object, visibility='public')  # type: object

    user_default_value = cy.declare(object, visibility='public') # type: object
    default_value      = cy.declare(object, visibility='public') # type: object
    is_required        = cy.declare(cy.bint, visibility='public')   # type: bool

    # From external formats to Python objects
    parse_from = cy.declare(dict, visibility='public') # type: dict

    # From Python objects to external formats
    parse_to   = cy.declare(dict, visibility='public') # type: dict

    get_default_value = None

# ################################################################################################################################

    def __cinit__(self):
        self._type = ElemType.as_is
        self.parse_from = {}
        self.parse_to = {}

        self.parse_from[DATA_FORMAT_JSON] = self.from_json
        self.parse_from[DATA_FORMAT_CSV] = self.from_csv
        self.parse_from[DATA_FORMAT_DICT] = self.from_dict
        self.parse_from[DATA_FORMAT_FORM] = self.from_dict

        self.parse_to[DATA_FORMAT_JSON] = self.to_json
        self.parse_to[DATA_FORMAT_CSV] = self.to_csv
        self.parse_to[DATA_FORMAT_DICT] = self.to_dict
        self.parse_to[DATA_FORMAT_FORM] = self.to_dict

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

# ################################################################################################################################

    def __lt__(self, other):
        if isinstance(other, Elem):
            return self.name < other.name
        else:
            return self.name < other

    def __gt__(self, other):
        if isinstance(other, Elem):
            return self.name > other.name
        else:
            return self.name > other

# ################################################################################################################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = self._get_unicode_name(name)

# ################################################################################################################################

    @cy.returns(str)
    def _get_unicode_name(self, name:object) -> str:
        if name:
            if not isinstance(name, basestring):
                logger.warning('Name `%s` should be a str/bytes/unicode object rather than `%s`', name, type(name))
            if not isinstance(name, str):
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

    @property
    def xpath(self):
        return self._xpath

    @xpath.setter
    def xpath(self, value):
        self._xpath = value

# ################################################################################################################################

    from_json = _not_implemented('Elem.from_json')  # noqa: F821
    to_json   = _not_implemented('Elem.to_json')    # noqa: F821

    from_xml  = _not_implemented('Elem.from_xml')   # noqa: F821
    to_xml    = _not_implemented('Elem.to_xml')     # noqa: F821

    from_csv  = _not_implemented('Elem.from_csv')   # noqa: F821
    to_csv    = _not_implemented('Elem.to_csv')     # noqa: F821

    from_dict  = _not_implemented('Elem.from_dict') # noqa: F821
    to_dict    = _not_implemented('Elem.to_dict')   # noqa: F821

# ################################################################################################################################

@cy.cclass
class AsIs(Elem):
    def __cinit__(self):
        self._type = ElemType.as_is

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value

    def from_json(self, value):
        return AsIs.from_json_static(value)

    to_dict = from_dict = to_csv = from_csv = to_xml = from_xml = to_json = from_json

# Defined only for backward compatibility
Opaque = AsIs

# ################################################################################################################################

@cy.cclass
class Bool(Elem):
    def __cinit__(self):
        self._type = ElemType.bool

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return to_bool(value)

    def from_json(self, value):
        return Bool.from_json_static(value)

    @staticmethod
    def to_json_static(value, *args, **kwargs):
        return 'true' if value else 'false'

    def to_json(self, value):
        return Bool.to_json_static(value)

    def get_default_value(self):
        return False

    to_dict = from_dict = to_csv = to_xml = from_csv = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class CSV(Elem):
    def __cinit__(self):
        self._type = ElemType.csv

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value.split(',')

    def from_json(self, value):
        return CSV.from_json_static(value)

    def to_json(self, value, *ignored):
        return ','.join(value) if isinstance(value, (list, tuple)) else value

    to_xml    = to_json
    from_xml  = from_json
    to_dict   = to_json
    from_dict = from_json
    to_csv    = _not_implemented('CSV.to_csv')
    from_csv  = _not_implemented('CSV.from_csv')

# ################################################################################################################################

@cy.cclass
class Date(Elem):

    stdlib_type = stdlib_date

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

    @staticmethod
    def to_json_static(value, stdlib_type, *args, **kwargs):

        if value is None:
            return value

        # Convert a timestamp in milliseconds to a datetime object
        if isinstance(value, float):
            value = stdlib_datetime.fromtimestamp(value)

        elif not isinstance(value, (stdlib_date, stdlib_datetime)):
            value = dt_parse(value)

        if stdlib_type is stdlib_date:
            return str(value.date())
        elif stdlib_type is stdlib_datetime:
            return value.isoformat()
        else:
            return value

    def to_json(self, value):
        return Date.to_json_static(value, self.stdlib_type, class_name=self.__class__.__name__)

    from_dict = from_csv = from_xml = from_json
    to_dict   = to_csv   = to_xml   = to_json

# ################################################################################################################################

@cy.cclass
class DateTime(Date):

    stdlib_type = stdlib_datetime

    def __cinit__(self):
        self._type = ElemType.date_time

# ################################################################################################################################

@cy.cclass
class Decimal(Elem):
    def __cinit__(self):
        self._type = ElemType.decimal

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return decimal_Decimal(value)

    def from_json(self, value):
        return Decimal.from_json_static(value)

    @staticmethod
    def to_json_static(value, *args, **kwargs):
        return str(value)

    def to_json(self, value):
        return Decimal.to_json_static(value)

    to_dict   = to_csv   = to_xml   = to_json
    from_dict = from_csv = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class Dict(Elem):

    _keys_required = cy.declare(set, visibility='public') # type: set
    _keys_optional = cy.declare(set, visibility='public') # type: set
    skip_empty = cy.declare(SIOSkipEmpty, visibility='public') # type: SIOSkipEmpty

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

    def from_json(self, value):
        return Dict.from_json_static(value, self._keys_required, self._keys_optional, self.default_value)

    from_dict = to_dict = from_json

    to_csv    = _not_implemented('Dict.to_csv')
    from_csv  = _not_implemented('Dict.from_csv')
    to_xml    = _not_implemented('Dict.to_xml')
    from_xml  = _not_implemented('Dict.from_xml')

# ################################################################################################################################

@cy.cclass
class DictList(Dict):
    def __cinit__(self):
        self._type = ElemType.dict_list

    @staticmethod
    def from_json_static(value, keys_required, keys_optional, default_value, *args, **kwargs):
        out = []
        for elem in value:
            value = Dict.from_json_static(elem, keys_required, keys_optional, default_value)
            out.append(value)
        return out

    def from_json(self, value):
        return DictList.from_json_static(value, self._keys_required, self._keys_optional, self.default_value)

    from_dict = to_dict = from_json

    to_csv    = _not_implemented('DictList.to_csv')
    from_csv  = _not_implemented('DictList.from_csv')
    to_xml    = _not_implemented('DictList.to_xml')
    from_xml  = _not_implemented('DictList.from_xml')

# ################################################################################################################################

@cy.cclass
class Float(Elem):
    def __cinit__(self):
        self._type = ElemType.float_

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        if value and value != _zato_none:
            return _builtin_float(value)
        elif value is None:
            return 0.0
        else:
            return value

    def from_json(self, value):
        return Float.from_json_static(value)

    to_dict = from_dict = to_csv = from_csv = to_xml = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class Int(Elem):
    def __cinit__(self):
        self._type = ElemType.int_

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        if value and value != _zato_none:
            return _builtin_int(value)
        elif value is None:
            return None
        else:
            return value

    def from_json(self, value):
        return Int.from_json_static(value)

    to_dict = from_dict = to_csv = from_csv = to_xml = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class List(Elem):
    def __cinit__(self):
        self._type = ElemType.list_

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        if value is not None:
            return value if isinstance(value, _list_like) else [value]
        else:
            return []

    def from_json(self, value):
        return List.from_json_static(value)

    to_dict = from_dict = to_csv = from_csv = to_xml = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class Text(Elem):

    encoding = cy.declare(object, visibility='public') # type: str
    is_secret = cy.declare(cy.bint, visibility='public') # type: bool

    def __cinit__(self):
        self._type = ElemType.text

    def __init__(self, name, **kwargs):
        super(Text, self).__init__(name, **kwargs)
        self.encoding = kwargs.get('encoding', 'utf8')
        self.is_secret = False

    @staticmethod
    def _from_value_static(value, *args, **kwargs):
        if isinstance(value, basestring):
            return value
        else:
            if isinstance(value, str):
                return value
            else:
                if isinstance(value, past_str):
                    encoding = kwargs.get('encoding') or 'utf8'
                    return str(value, encoding)
                else:
                    if value is None:
                        return value
                    else:
                        return str(value)

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return Text._from_value_static(value, *args, **kwargs)

    def from_json(self, value):
        return Text.from_json_static(value, encoding=self.encoding)

    to_dict = from_dict = to_csv = from_csv = to_xml = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class Secret(Text):
    def __init__(self, *args, **kwargs):
        super(Secret, self).__init__(*args, **kwargs)
        self.is_secret = True

# ################################################################################################################################

@cy.cclass
class UTC(Elem):
    def __cinit__(self):
        self._type = ElemType.utc

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return value.replace('+00:00', '')

    def from_json(self, value):
        return UTC.from_json_static(value)

    to_dict = from_dict = to_csv = from_csv = to_xml = from_xml = from_json

# ################################################################################################################################

@cy.cclass
class UUID(Elem):

    def __cinit__(self):
        self._type = ElemType.uuid

    @staticmethod
    def from_json_static(value, *args, **kwargs):
        return uuid_UUID(value)

    def from_json(self, value):
        return UUID.from_json_static(value)

    @staticmethod
    def to_json_static(value, *args, **kwargs):
        if isinstance(value, uuid_UUID):
            return value.hex
        else:
            return value

    def to_json(self, value):
        return UUID.to_json_static(value)

    to_dict   = to_csv   = to_xml   = to_json
    from_dict = from_csv = from_xml = from_json

# ################################################################################################################################

# For backward compatibility
Boolean     = Bool
Integer     = Int
ListOfDicts = DictList
Unicode     = Text

# ################################################################################################################################

class SIO_TYPE_MAP:

# ################################################################################################################################

    class OPEN_API_V3:

        name    = APISPEC.OPEN_API_V3
        STRING  = ('string', 'string')
        DEFAULT = STRING
        INTEGER = ('integer', 'int32')
        FLOAT   = ('float',   'float')
        BOOLEAN = ('boolean', 'boolean')
        LIST    = ('array',   'array')
        DICT    = ('object',  'object')

        map = {
            AsIs: STRING,
            Bool: BOOLEAN,
            CSV: STRING,
            Dict: ('object', 'object'),
            Float: ('number', 'float'),
            Int: INTEGER,
            List: ('array', 'array'),
            DictList: ('string', 'binary'),
            Opaque: ('string', 'binary'),
            Text: STRING,
            UTC: ('string', 'date-time'),
        }

# ################################################################################################################################

    class ZATO:

        name    = 'zato'
        STRING  = ('string', 'string')
        DEFAULT = STRING
        INTEGER = ('integer', 'integer')
        FLOAT   = ('float',   'float')
        BOOLEAN = ('boolean', 'boolean')
        LIST    = ('list',    'list')
        DICT    = ('dict',    'dict')

        map = {
            AsIs: STRING,
            Bool: BOOLEAN,
            CSV: STRING,
            Dict: ('dict', 'dict'),
            Float: ('number', 'float'),
            Int: INTEGER,
            List: ('list', 'list'),
            DictList: ('list', 'list-of-dicts'),
            Opaque: ('opaque', 'opaque'),
            Text: STRING,
            UTC: ('string', 'date-time-utc'),
        }

# ################################################################################################################################

    def __iter__(self):
        return iter((self.OPEN_API_V3, self.ZATO))

# ################################################################################################################################

@cy.cclass
class ConfigItem:
    """ An individual instance of server-wide SimpleIO configuration. Each subclass covers
    a particular set of exact values, prefixes or suffixes.
    """
    exact    = cy.declare(set, visibility='public') # type: set
    prefixes = cy.declare(set, visibility='public') # type: set
    suffixes = cy.declare(set, visibility='public') # type: set

    def __str__(self):
        return '<{} at {} e:{}, p:{}, s:{}>'.format(self.__class__.__name__, hex(id(self)),
            sorted(self.exact), sorted(self.prefixes), sorted(self.suffixes))

# ################################################################################################################################

@cy.cclass
class BoolConfig(ConfigItem):
    """ SIO configuration for boolean values.
    """

# ################################################################################################################################

@cy.cclass
class IntConfig(ConfigItem):
    """ SIO configuration for integer values.
    """

# ################################################################################################################################

@cy.cclass
class SecretConfig(ConfigItem):
    """ SIO configuration for secret values, passwords, tokens, API keys etc.
    """

# ################################################################################################################################

@cy.cclass
class SIOServerConfig:
    """ Contains global SIO configuration. Each service's _sio attribute
    will refer to this object so as to have only one place where all the global configuration is kept.
    """
    bool_config = cy.declare(BoolConfig, visibility='public')     # type: BoolConfig
    int_config = cy.declare(IntConfig, visibility='public')       # type: IntConfig
    secret_config = cy.declare(SecretConfig, visibility='public') # type: SecretConfig

    # Custom JSON encoder to handle types outside what the stdlib's one supports
    json_encoder = cy.declare(object, visibility='public') # type: SIOJSONEncoder

    # Names in SimpleIO declarations that can be overridden by users
    input_required_name = cy.declare(str, visibility='public')  # type: str
    input_optional_name = cy.declare(str, visibility='public')  # type: str
    output_required_name = cy.declare(str, visibility='public') # type: str
    output_optional_name = cy.declare(str, visibility='public') # type: str
    default_value = cy.declare(str, visibility='public')        # type: str
    default_input_value = cy.declare(str, visibility='public')  # type: str
    default_output_value = cy.declare(str, visibility='public') # type: str
    response_elem = cy.declare(str, visibility='public')        # type: str

    prefix_as_is = cy.declare(str, visibility='public')     # type: str # a
    prefix_bool = cy.declare(str, visibility='public')      # type: str # b
    prefix_csv = cy.declare(str, visibility='public')       # type: str # c
    prefix_date = cy.declare(str, visibility='public')      # type: str # dt
    prefix_date_time = cy.declare(str, visibility='public') # type: str # dtm
    prefix_dict = cy.declare(str, visibility='public')      # type: str # d
    prefix_dict_list = cy.declare(str, visibility='public') # type: str # dl
    prefix_float = cy.declare(str, visibility='public')     # type: str # f
    prefix_int = cy.declare(str, visibility='public')       # type: str # i
    prefix_list = cy.declare(str, visibility='public')      # type: str # l
    prefix_text = cy.declare(str, visibility='public')      # type: str # t
    prefix_uuid = cy.declare(str, visibility='public')      # type: str # u

    # Python 2/3 compatibility
    bytes_to_str_encoding = cy.declare(str, visibility='public') # type: str

    # Global variables, can be always overridden on a per-declaration basis
    skip_empty_keys = cy.declare(object, visibility='public')          # type: object
    skip_empty_request_keys = cy.declare(object, visibility='public')  # type: object
    skip_empty_response_keys = cy.declare(object, visibility='public') # type: object

    @cy.cfunc
    @cy.returns(cy.bint)
    def is_int(self, name) -> cy.bint:
        """ Returns True if input name should be treated like ElemType.int.
        """

    @cy.cfunc
    @cy.returns(cy.bint)
    def is_bool(self, name) -> cy.bint:
        """ Returns True if input name should be treated like ElemType.bool.
        """

    @cy.cfunc
    @cy.returns(cy.bint)
    def is_secret(self, name) -> cy.bint:
        """ Returns True if input name should be treated like ElemType.secret.
        """

    def __cinit__(self):
        self.json_encoder = SIOJSONEncoder()

# ################################################################################################################################

@cy.cclass
class SIOList:
    """ Represents one of input/output required/optional.
    """
    elems         = cy.declare(list, visibility='public') # type: list
    elems_by_name = cy.declare(dict, visibility='public') # type: dict

    def __cinit__(self):
        self.elems = []
        self.elems_by_name = {}

    def __iter__(self):
        return iter(self.elems)

    def __len__(self):
        return len(self.elems)

    def set_elems(self, elems:list):
        self.elems[:] = elems
        for elem in self.elems:
            self.elems_by_name[elem.name] = elem

    def get_elem_by_name(self, name:object) -> Elem:
        return self.elems_by_name[name]

    def get_elem_names(self, use_sorted=False) -> list:
        out = [elem.name for elem in self.elems]
        return sorted(out) if use_sorted else out

# ################################################################################################################################

@cy.cclass
class CSVConfig:
    """ Represents CSV configuration that a particular SimpleIO definition uses.
    """
    dialect             = cy.declare(object, visibility='public') # type: str
    common_config       = cy.declare(dict, visibility='public')    # type: dict
    writer_config       = cy.declare(dict, visibility='public')    # type: dict
    should_write_header = cy.declare(cy.bint, visibility='public')    # type: bool

    def __cinit__(self):
        self.dialect = 'excel'
        self.common_config = {}
        self.writer_config = {}
        self.should_write_header = True

# ################################################################################################################################

@cy.cclass
class XMLConfig:
    """ Represents XML configuration that a particular SimpleIO definition uses.
    """
    namespace    = cy.declare(object, visibility='public')  # type: object
    encoding     = cy.declare(object, visibility='public') # type: str
    declaration  = cy.declare(cy.bint, visibility='public')    # type: bool
    pretty_print = cy.declare(cy.bint, visibility='public')    # type: bool

    def __cinit__(self):
        self.namespace = InternalNotGiven
        self.encoding = 'UTF-8'
        self.declaration = True
        self.pretty_print = InternalNotGiven

# ################################################################################################################################

@cy.cclass
class SIODefinition:
    """ A single SimpleIO definition attached to a service.
    """
    # A list of Elem items required on input
    _input_required = cy.declare(SIOList, visibility='public') # type: SIOList

    # A list of Elem items optional on input
    _input_optional = cy.declare(SIOList, visibility='public') # type: SIOList

    # A list of Elem items required on output
    _output_required = cy.declare(SIOList, visibility='public') # type: _output_required

    # A list of Elem items optional on output
    _output_optional = cy.declare(SIOList, visibility='public') # type: SIOList

    # Default values to use for optional elements, unless overridden on a per-element basis
    sio_default = cy.declare(SIODefault, visibility='public') # type: SIODefault

    # Which empty values should not be produced from input or sent on output, unless overridden by each element
    skip_empty = cy.declare(SIOSkipEmpty, visibility='public') # type: SIOSkipEmpty

    # CSV configuration for the definition
    _csv_config = cy.declare(CSVConfig, visibility='public') # type: CSVConfig

    # XML configuration for the definition
    _xml_config = cy.declare(XMLConfig, visibility='public') # type: XMLConfig

    # A flag that can be set by users explicitly
    output_repeated = cy.declare(cy.bint, visibility='public') # type: bool

    # To indicate whether I/O particular definitions exist or not
    has_input_required = cy.declare(cy.bint, visibility='public') # type: bool
    has_input_optional = cy.declare(cy.bint, visibility='public') # type: bool
    has_input_declared = cy.declare(cy.bint, visibility='public') # type: bool

    has_output_required = cy.declare(cy.bint, visibility='public') # type: bool
    has_output_optional = cy.declare(cy.bint, visibility='public') # type: bool
    has_output_declared = cy.declare(cy.bint, visibility='public') # type: bool

    # All input/output element names, both required and optional ones
    all_input_elem_names  = cy.declare(list, visibility='public') # type: list
    all_output_elem_names = cy.declare(list, visibility='public') # type: list

    # All input/output elements (not just names), both required and optional ones
    all_input_elems  = cy.declare(list, visibility='public') # type: list
    all_output_elems = cy.declare(list, visibility='public') # type: list

    # Name of the service this definition is for
    _service_name = cy.declare(object, visibility='public') # type: str

    # Name of the response element, or None if there should be no top-level one
    _response_elem = cy.declare(object, visibility='public') # type: object

    # To let Cython use cy.bint in order to check if _response_elem is provided
    _has_response_elem = cy.declare(cy.bint, visibility='public') # type: object

    def __cinit__(self):
        self._input_required = SIOList()
        self._input_optional = SIOList()
        self._output_required = SIOList()
        self._output_optional = SIOList()
        self._csv_config = CSVConfig()
        self._xml_config = XMLConfig()

        self.output_repeated = False

        self.has_input_required = False
        self.has_input_optional = False
        self.has_input_declared = False

        self.has_output_required = False
        self.has_output_optional = False
        self.has_output_declared = False

        self.all_input_elem_names  = []
        self.all_output_elem_names = []

        self.all_input_elems = []

    def __init__(self, sio_default:SIODefault, skip_empty:SIOSkipEmpty):
        self.sio_default = sio_default
        self.skip_empty = skip_empty

# ################################################################################################################################

    def get_input_required(self) -> SIOList:
        return self._input_required

# ################################################################################################################################

    def get_input_optional(self) -> SIOList:
        return self._input_optional

# ################################################################################################################################

    def get_output_required(self) -> SIOList:
        return self._output_required

# ################################################################################################################################

    def get_output_optional(self) -> SIOList:
        return self._output_optional

# ################################################################################################################################

    def get_input_required_elem_names(self) -> list:
        return self._input_required.get_elem_names()

# ################################################################################################################################

    def get_input_optional_elem_names(self) -> list:
        return self._input_optional.get_elem_names()

# ################################################################################################################################

    def get_output_required_elem_names(self) -> list:
        return self._output_required.get_elem_names()

# ################################################################################################################################

    def get_output_optional_elem_names(self) -> list:
        return self._output_optional.get_elem_names()

# ################################################################################################################################

    @cy.returns(str)
    def get_elems_pretty(self, required_list:SIOList, optional_list:SIOList) -> str:
        out:object = ''

        if required_list.elems:
            out += ', '.join(required_list.get_elem_names())

        if optional_list.elems:
            # Separate with a semicolon only if there is some required part to separate it from
            if required_list.elems:
                out += '; '
            out += ', '.join(['-' + elem for elem in optional_list.get_elem_names()])

        return out

# ################################################################################################################################

    @cy.returns(str)
    def get_input_pretty(self) -> str:
        return self.get_elems_pretty(self._input_required, self._input_optional)

# ################################################################################################################################

    @cy.returns(str)
    def get_output_pretty(self) -> str:
        return self.get_elems_pretty(self._output_required, self._output_optional)

# ################################################################################################################################

    @cy.cfunc
    def set_csv_config(self, dialect:object, common_config:dict, writer_config:dict, should_write_header:cy.bint):
        self._csv_config.dialect = dialect
        self._csv_config.common_config.update(common_config)
        self._csv_config.writer_config.update(writer_config)
        self._csv_config.should_write_header = should_write_header

# ################################################################################################################################

    @cy.cfunc
    def set_xml_config(self, namespace:object, pretty_print:cy.bint, encoding:object, declaration:cy.bint):
        self._xml_config.namespace = namespace
        self._xml_config.pretty_print = pretty_print
        self._xml_config.encoding = encoding
        self._xml_config.declaration = declaration

# ################################################################################################################################

    def __str__(self):
        return '<{} at {}, input:`{}`, output:`{}`>'.format(self.__class__.__name__, hex(id(self)),
            self.get_input_pretty(), self.get_output_pretty())

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class CySimpleIO:
    """ If a service uses SimpleIO then, during deployment, its class will receive an attribute called _sio
    based on the service's SimpleIO attribute. The _sio one will be an instance of this Cython class.
    """

    # We are not based on dataclasses, unlike DataClassSimpleIO
    is_dataclass = False

    # A parallel server instance
    server = cy.declare(object, visibility='public') # type: ParallelServer

    # Server-wide configuration
    server_config = cy.declare(SIOServerConfig, visibility='public') # type: SIOServerConfig

    # Current service's configuration, after parsing
    definition = cy.declare(SIODefinition, visibility='public') # type: SIODefinition

    # User-provided SimpleIO declaration, before parsing. This is parsed into self.definition.
    user_declaration = cy.declare(object, visibility='public') # type: object

    # Kept for backward compatibility with 3.0
    has_bool_force_empty_keys = cy.declare(cy.bint, visibility='public') # type: bool

    # A service class this SimpleIO object is attached to
    service_class = cy.declare(object, visibility='public') # type: object

# ################################################################################################################################

    def __cinit__(self, server:object, server_config:SIOServerConfig, user_declaration:object):

        input_value = getattr(user_declaration, 'default_input_value', InternalNotGiven)
        output_value = getattr(user_declaration, 'default_output_value', InternalNotGiven)
        default_value = getattr(user_declaration, 'default_value', InternalNotGiven)

        sio_default:SIODefault = SIODefault(input_value, output_value, default_value)

        raw_skip_empty = getattr(user_declaration, 'skip_empty_keys', NotGiven) # For backward compatibility
        class_skip_empty = getattr(user_declaration, 'SkipEmpty', NotGiven)

        # Quick input validation - we cannot have both kinds of configuration
        if (raw_skip_empty is not NotGiven) and (class_skip_empty is not NotGiven):
            raise ValueError('Cannot specify both skip_empty_input and SkipEmpty in a SimpleIO definition')

        # Note that to retain backward compatibility, it is force_empty_keys instead of force_empty_output_set
        raw_force_empty_output_set = getattr(user_declaration, 'force_empty_keys', NotGiven) # For backward compatibility
        if raw_force_empty_output_set in (True, False):
            self.has_bool_force_empty_keys = True
        else:
            self.has_bool_force_empty_keys = False # Initialize it explicitly

        # Again, quick input validation
        if (raw_force_empty_output_set is not NotGiven) and (class_skip_empty is not NotGiven):
            raise ValueError('Cannot specify both force_empty_keys and SkipEmpty in a SimpleIO definition')

        if class_skip_empty is NotGiven:
            empty_output_value = NotGiven
            input_def = NotGiven
            output_def = raw_skip_empty if raw_skip_empty is not NotGiven else NotGiven
            force_empty_input_set = NotGiven
            force_empty_output_set = raw_force_empty_output_set if raw_force_empty_output_set is not NotGiven else NotGiven

        else:
            empty_output_value = getattr(class_skip_empty, 'empty_output_value', InternalNotGiven)

            # We cannot have NotGiven as the default output value, it cannot be serialised in a meaningful way
            if empty_output_value is NotGiven:
                raise ValueError('NotGiven cannot be used as empty_output_value')

            input_def = getattr(class_skip_empty, 'input', NotGiven)
            output_def = getattr(class_skip_empty, 'output_def', NotGiven)
            force_empty_input_set = getattr(class_skip_empty, 'force_empty_input', NotGiven)
            force_empty_output_set = getattr(class_skip_empty, 'force_empty_output', NotGiven)

        # ####################################################################################
        #
        # As far as skipping of empty keys goes, we potentially have now
        # its definition from SkipEmpty or from individual (pre-3.2) attributes.
        # But if we do not have either of them, we need to look the defaults
        # in the server's configuration.
        #
        # ####################################################################################

        if input_def is NotGiven:
            input_def = server_config.skip_empty_request_keys

        if output_def is NotGiven:
            output_def = server_config.skip_empty_response_keys

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

        sio_skip_empty:SIOSkipEmpty  = SIOSkipEmpty(input_def, output_def, force_empty_input_set,
            force_empty_output_set, empty_output_value)

        self.definition = SIODefinition(sio_default, sio_skip_empty)
        self.server = server
        self.server_config = server_config
        self.user_declaration = user_declaration

# ################################################################################################################################

    @cy.cfunc
    def _resolve_bool_force_empty_keys(self):
        self.definition.skip_empty.force_empty_output_set = set(self.definition._output_optional.get_elem_names())

# ################################################################################################################################

    @cy.cfunc
    def _set_up_csv_config(self):
        csv_dialect:object  = 'excel'
        csv_common_config:dict  = {}
        csv_writer_config:dict  = {}
        csv_sio_class:object  = getattr(self.user_declaration, 'CSV', InternalNotGiven)
        has_csv_sio_class:cy.bint  = csv_sio_class is not InternalNotGiven
        should_write_header:object
        cy_attr:object
        stdlib_attr:object
        value:object
        attr_map:dict
        target_config:dict

        to_process:list = [
            (_csv_common_attr_map, csv_common_config),
            (_csv_writer_attr_map, csv_writer_config),
        ]

        for attr_map, target_config in to_process:
            for cy_attr, stdlib_attr in attr_map.items():
                if has_csv_sio_class:
                    value = getattr(csv_sio_class, cy_attr, InternalNotGiven)
                else:
                    value = InternalNotGiven

                if value is InternalNotGiven:
                    value = getattr(self.user_declaration, 'csv_' + cy_attr, InternalNotGiven)

                if cy_attr == 'dialect':
                    if value is not InternalNotGiven:
                        csv_dialect = value
                else:
                    if value is not InternalNotGiven:
                        target_config[stdlib_attr] = value

        # Unlike the stdlib, we default to ignoring any extra elements found in CSV serialisation
        if 'extrasaction' not in csv_writer_config:
            csv_writer_config['extrasaction'] = 'ignore'

        # Merge common options to writer ones
        csv_writer_config.update(csv_common_config)

        if has_csv_sio_class:
            should_write_header = getattr(csv_sio_class, 'should_write_header', InternalNotGiven)
        else:
            should_write_header = getattr(self.user_declaration, 'csv_should_write_header', InternalNotGiven)

        if should_write_header is InternalNotGiven:
            should_write_header = True

        # Assign for later use
        self.definition.set_csv_config(csv_dialect, csv_common_config, csv_writer_config, should_write_header)

# ################################################################################################################################

    @cy.cfunc
    def _set_up_xml_config(self):

        attrs:list  = ['namespace', 'pretty_print', 'encoding', 'declaration']
        attr_values:dict  = {}
        namespace:object
        pretty_print:object
        encoding:object
        declaration:object
        value:object  = InternalNotGiven
        xml_sio_class:object  = getattr(self.user_declaration, 'XML', InternalNotGiven)
        has_xml_sio_class:cy.bint = xml_sio_class is not InternalNotGiven

        for attr_name in attrs:

            value = InternalNotGiven

            if has_xml_sio_class:
                value = getattr(xml_sio_class, attr_name, InternalNotGiven)

            if value is InternalNotGiven:
                value = getattr(self.user_declaration, 'xml_'+ attr_name, InternalNotGiven)

            attr_values[attr_name] = value

        namespace = attr_values['namespace']
        if namespace is InternalNotGiven:
            namespace = ''

        pretty_print = attr_values['pretty_print']
        if pretty_print is InternalNotGiven:
            pretty_print = True

        encoding = attr_values['encoding']
        if encoding is InternalNotGiven:
            encoding = 'UTF-8'

        declaration = attr_values['declaration']
        if declaration is InternalNotGiven:
            declaration = True

        self.definition.set_xml_config(namespace, pretty_print, encoding, declaration)

# ################################################################################################################################

    @cy.ccall
    def build(self, class_:object):
        """ Parses a user-defined SimpleIO declaration (a Python class) and populates all the internal structures as needed.
        """
        self._build_io_elems('input', class_)
        self._build_io_elems('output', class_)

        # Now that we have all the elements, and if we have a definition using 'force_empty_keys = True' (or False),
        # we need to turn the _ForceEmptyKeyMarker into an acutal list of elements to force into empty keys.
        if self.has_bool_force_empty_keys:
            self._resolve_bool_force_empty_keys()

        response_elem = getattr(self.user_declaration, 'response_elem', InternalNotGiven)

        if response_elem is InternalNotGiven:
            if getattr(class_, '_zato_needs_response_wrapper', None) is False:
                response_elem = None

        if response_elem is InternalNotGiven:
            response_elem = getattr(self.server_config, 'response_elem', InternalNotGiven)

        if (not response_elem) or (response_elem is InternalNotGiven):
            response_elem = None

        output_repeated = getattr(self.user_declaration, 'output_repeated', InternalNotGiven)
        if output_repeated is not InternalNotGiven:
            self.definition.output_repeated = bool(output_repeated)

        self.definition._response_elem = response_elem
        self.definition._has_response_elem = bool(self.definition._response_elem)

        self.definition.has_input_required = stdlib_bool(len(self.definition._input_required))
        self.definition.has_input_optional = stdlib_bool(len(self.definition._input_optional))
        self.definition.has_input_declared = self.definition.has_input_required or self.definition.has_input_optional

        self.definition.has_output_required = stdlib_bool(len(self.definition._output_required))
        self.definition.has_output_optional = stdlib_bool(len(self.definition._output_optional))
        self.definition.has_output_declared = self.definition.has_output_required or self.definition.has_output_optional

        self.definition.all_input_elem_names.extend(self.definition.get_input_required_elem_names())
        self.definition.all_input_elem_names.extend(self.definition.get_input_optional_elem_names())

        self.definition.all_output_elem_names.extend(self.definition.get_output_required_elem_names())
        self.definition.all_output_elem_names.extend(self.definition.get_output_optional_elem_names())

        self.definition.all_input_elems.extend(self.definition.get_input_required())
        self.definition.all_input_elems.extend(self.definition.get_input_optional())

        # Set up CSV configuration
        self._set_up_csv_config()

        # Set up XML configuration
        self._set_up_xml_config()

# ################################################################################################################################

    @cy.returns(Elem)
    def convert_to_elem_instance(self, elem_name, is_required:cy.bint) -> Elem:

        # The element we return, at this point we do not know what its exact subtype will be
        _elem:Elem

        exact:set
        prefixes:set
        suffixes:set

        config_item:ConfigItem

        config_item_to_type:tuple = (
            (Bool,   self.server_config.bool_config),
            (Int,    self.server_config.int_config),
            (Secret, self.server_config.secret_config),
        )

        for (ElemClass, config_item) in config_item_to_type:

            exact = config_item.exact
            prefixes = config_item.prefixes
            suffixes = config_item.suffixes

            # Try an exact match first ..
            for config_elem in exact:
                if elem_name == config_elem:
                    _elem = ElemClass(elem_name)
                    _elem.name = elem_name
                    _elem.is_required = is_required
                    return _elem

            # .. try prefix matching then ..
            for config_elem in prefixes:
                if elem_name.startswith(config_elem):
                    _elem = ElemClass(elem_name)
                    _elem.name = elem_name
                    _elem.is_required = is_required
                    return _elem

            # .. finally, try suffix matching.
            for config_elem in suffixes:
                if elem_name.endswith(config_elem):
                    _elem = ElemClass(elem_name)
                    _elem.name = elem_name
                    _elem.is_required = is_required
                    return _elem

        # If we get here, it means that none of the configuration objects above
        # matched our input, i.e. none of exact, prefix or suffix elements,
        # so we can just return a Text one.

        _elem = Text(elem_name)
        _elem.name = elem_name
        _elem.is_required = is_required

        return _elem

# ################################################################################################################################

    @cy.cfunc
    def _build_io_elems(self, container, class_):
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

                if elem_name.startswith(prefix_optional) or (is_sio_elem and (not elem.is_required)):
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

        elem:Elem = None
        elem_list:list = None
        is_required:cy.bint

        for elem_list, is_required in elems:
            for initial_elem in elem_list:

                # All of our elements are always SimpleIO objects
                if isinstance(initial_elem, Elem):
                    elem = initial_elem
                else:
                    elem = self.convert_to_elem_instance(initial_elem, is_required)

                # By default all Elem instances are required so we need
                # to potentially overwrite it with the actual is_required value.
                elem.is_required = is_required

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

        # If there are elements shared by required and optional lists, the ones from the optional list
        # need to be removed, the required ones take priority. The reason for that is that it is common
        # to have a base SimpleIO class with optional elements that are made mandatory in a child class.
        shared_elems = {elem.name for elem in required} & {elem.name for elem in optional}

        if shared_elems:

            # Iterate through all the shared elements found, take note of what is shared ..
            to_remove = []
            for shared_name in shared_elems:
                for elem in optional:
                    if elem.name == shared_name:
                        to_remove.append(elem)

            # .. remove them from the optional list ..
            for shared_elem in to_remove:
                optional.remove(shared_elem)

            # .. and let the user know about it.
            logger.info('Shared elements found; {}_required will take priority, `{}`, `{}`'.format(
                container, sorted(elem for elem in shared_elems), class_))

        # Everything is validated, we can actually set the lists of elements now

        container_req_name = '_{}_required'.format(container)
        container_required:SIOList = getattr(self.definition, container_req_name)
        container_required.set_elems(required)

        container_opt_name = '_{}_optional'.format(container)
        container_optional:SIOList = getattr(self.definition, container_opt_name)
        container_optional.set_elems(optional)

# ################################################################################################################################

    @staticmethod
    def attach_sio(server: object, server_config:object, class_:object):
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
            sio = CySimpleIO(server, server_config, user_sio)
            sio.service_class = class_
            sio.build(class_)
            class_._sio = sio

        except Exception:
            logger.warning('Could not attach CySimpleIO to class `%s`, e:`%s`', class_, format_exc())
            raise

# ################################################################################################################################

    @cy.cfunc
    @cy.returns(cy.bint)
    @cy.exceptval(-1)
    def _should_skip_on_input(self, definition:SIODefinition, sio_item:Elem, input_value:object) -> cy.bint:
        has_no_input_value:bool = not bool(input_value)

        matches_skip_all:cy.bint = definition.skip_empty.skip_all_empty_input and has_no_input_value # type: bool
        matches_skip_input_set:cy.bint = definition.skip_empty.has_skip_input_set and \
            sio_item.name in definition.skip_empty.skip_input_set       # type: bool

        # Should we skip this value based on the server's configuration ..
        if matches_skip_all or matches_skip_input_set:

            # .. possibly, unless we are forced not to include it.
            if sio_item.name not in definition.skip_empty.force_empty_input_set:
                return True

        # In all other cases, we explicitly say that this value should not be skipped
        return False

# ################################################################################################################################

    @cy.returns(object)
    def _parse_input_elem(self, elem:object, data_format:object, is_csv:cy.bint=False, extra:dict=None) -> object: # noqa: E252

        # If this is a pub/sub message ..
        if isinstance(elem, PubSubMessage):

            # .. parse out its data ..
            elem = elem.data

            # .. and make sure it is something we can process.
            elem = elem or {}

        is_dict:cy.bint = isinstance(elem, dict)
        is_xml:cy.bint  = isinstance(elem, EtreeElementClass)

        if not (is_dict or is_xml or is_csv):
            logger.debug('Ignoring CySimpleIO input `{%r}` (%s in %s) (not a dict, CSV or EtreeElementClass )',
                elem, type(elem).__name__, self.service_class)
            return

        # This dictionary holds keys that were common to both 'elem' and 'extra'. If extra exists,
        # and some of the extra keys already exist in elem, this dictionary is populated with such
        # keys/value extracted from elem. Before we return, they are re-added. This is needed,
        # because if extra exists, we update elem with extra's keys in-place so we need to make sure
        # that elem is in the same state (has the same keys/values) as before we received it.
        elem_shared_keys:dict = {}

        out:dict = {}
        idx:cy.int = -1
        sio_item:Elem = None
        sio_item_name:str = None
        items:list = self.definition.all_input_elems

        # Overwrite and append any keys found in extra and elem, first make a backup of shared keys for later use.
        if is_dict and extra:
            for extra_key, extra_value in extra.items():

                # .. make backup ..
                if extra_key in elem:
                    elem_shared_keys[extra_key] = elem[extra_key]

                # .. overwrite (note that there is no 'else').
                elem[extra_key] = extra_value

        for sio_item in items:

            # Start the loop with 0
            idx += 1

            sio_item_name = sio_item.name

            # Parse the input dictionary
            if is_dict:
                input_value = cy.cast(dict, elem).get(sio_item_name, InternalNotGiven)

            # Parse the input XML document
            elif is_xml:

                # This will not be populated the first time around we are parsing an input document
                # in which case we create this XPath expression here and make use of it going forward.
                if not sio_item.xpath:
                    sio_item.xpath = XPath('*[local-name() = "{}"]'.format(sio_item_name))

                # Here, elem is the root of an XML document
                input_value = sio_item.xpath.evaluate(elem)

                if input_value:
                    input_value = input_value[0].text
                else:
                    input_value = InternalNotGiven

            else:

                # It still may be CSV ..
                if is_csv:
                    try:
                        input_value = elem[idx]
                    except IndexError:
                        raise ValueError('Could not find input value at index `{}` in `{}` (dialect:{}, config:{})'.format(
                            idx, elem, self.definition._csv_config.dialect, self.definition._csv_config.common_config))

                # Otherwise, refuse to continue
                else:
                    raise Exception('Invalid input, none of is_dict, is_str nor is_xml')

            # We do not have such a elem on input so an exception needs to be raised if this is a require one
            if input_value is InternalNotGiven:

                if sio_item.is_required:

                    if is_dict:
                        all_elems = cy.cast(dict, elem).keys()
                    elif is_xml:
                        all_elems = elem.getchildren()
                    elif is_csv:
                        all_elems = elem

                    # This goes to logs ..
                    logger.warning('%s; No such input elem `%s` among `%s` in `%s`' % (
                        self.service_class, sio_item_name, all_elems, elem))

                    # .. while this is potentially returned to users.
                    raise ElementMissing(sio_item_name)

                else:
                    if self._should_skip_on_input(self.definition, sio_item, input_value):
                        continue
                    else:
                        if sio_item.get_default_value:
                            value = sio_item.get_default_value()
                        else:
                            value = sio_item.default_value
            else:
                parse_func = sio_item.parse_from[data_format]

                try:
                    if self._should_skip_on_input(self.definition, sio_item, input_value):
                        continue
                    else:

                        value = parse_func(input_value)
                        if getattr(sio_item, 'is_secret', False):
                            value = self.eval_(sio_item.name, input_value, self.server.encrypt if self.server else None)

                except NotImplementedError:
                    raise NotImplementedError('No parser for input `{}` ({})'.format(input_value, data_format))

            # We get here only if should_skip is not True
            out[sio_item_name] = value

        # Before returning, if input was a dict (or dict-like, e.g. JSON), undo all the changes
        # made when extra overwrote keys from the 'elem' dict.
        if is_dict and extra:
            for extra_key in extra:

                # .. undo ..
                elem.pop(extra_key)

                # .. bring back the old value.
                if extra_key in elem_shared_keys:
                    elem[extra_key] = elem_shared_keys[extra_key]

        return out

# ################################################################################################################################

    @cy.returns(object)
    def _parse_input_list(self, data:object, data_format:object, is_csv:cy.bint) -> object:
        out = []
        for elem in data:
            converted = self._parse_input_elem(elem, data_format, is_csv)
            out.append(bunchify(converted))
        return out

# ################################################################################################################################

    @cy.returns(object)
    def parse_input(self, data:object, data_format:object, service:object=None, extra:dict=None) -> object:

        is_csv:cy.bint = data_format == DATA_FORMAT_CSV and isinstance(data, basestring)

        if isinstance(data, list):
            return self._parse_input_list(data, data_format, is_csv)
        else:
            if is_csv:
                data = StringIO(data)
                csv_data = csv_reader(data, self.definition._csv_config.dialect, **self.definition._csv_config.common_config)
                return self._parse_input_list(csv_data, data_format, is_csv)
            else:
                out = self._parse_input_elem(data, data_format, extra=extra)
            return bunchify(out)

# ################################################################################################################################

    def _yield_data_dicts(self, data:object, data_format:str):

        required_elems:dict = self.definition._output_required.elems_by_name
        optional_elems:dict = self.definition._output_optional.elems_by_name

        # First yield calls- return only field names
        yield list(required_elems.keys())
        yield list(optional_elems.keys())

        input_data:list = data if isinstance(data, (list, tuple)) else [data]

        # 1st item = is_required
        # 2nd item = elems dict
        all_elems:list = [
            (True, required_elems),
            (False, optional_elems),
        ]

        is_required:cy.bint
        current_elems:dict = None
        current_elem_name:object = None
        current_elem:Elem = None
        input_data_dict = None

        for _input_data_dict in input_data:

            # This is the dictionary that we return.
            out_data_dict = {}

            if isinstance(_input_data_dict, dict):
                input_data_dict = _input_data_dict

            # This could be an SQLAlchemy object that we need to convert to a dictionary
            elif hasattr(_input_data_dict, 'asdict'):
                input_data_dict = _input_data_dict.asdict()

            # This could be an object that explicitly knows how to serialise to Zato
            elif hasattr(_input_data_dict, 'to_zato'):
                input_data_dict = _input_data_dict.to_zato()

            elif isinstance(_input_data_dict, SQLRow):
                input_data_dict = _input_data_dict.get_value()

            for is_required, current_elems in all_elems: # type: bool, dict
                for current_elem_name, current_elem in current_elems.items():
                    value = input_data_dict.get(current_elem_name, InternalNotGiven)
                    if value is InternalNotGiven:
                        if is_required:
                            raise SerialisationError('Required element `{}` missing in `{}` ({})'.format(
                                current_elem_name, input_data_dict, self.service_class))
                    else:
                        try:
                            parse_func = None
                            parse_func = current_elem.parse_to[data_format]
                            value = parse_func(value)
                        except Exception as e:
                            raise SerialisationError('Exception `{!r}` while serialising `{}` ({}) ({}) (func:{})'.format(
                                e, value, self.service_class, input_data_dict, parse_func))

                        if cy.cast(cy.int, current_elem._type) == cy.cast(cy.int, sio_text_type):
                            if isinstance(value, bytes):
                                value = value.decode(current_elem.encoding)

                        # All checks passed - we can append this particular element to the output dictionary
                        out_data_dict[current_elem_name] = value

            # More yields - to actually return data

            yield out_data_dict

# ################################################################################################################################

    @cy.returns(str)
    def _get_output_csv(self, data:object) -> str:

        # No reason to continue if no SimpleIO output is declared
        if not (self.definition.has_output_required or self.definition.has_output_optional):
            return ''

        gen = self._yield_data_dicts(data, DATA_FORMAT_CSV)

        # First, get the field names
        required_field_names:list = next(gen)
        optional_field_names:list = next(gen)

        out:object
        buff:StringIO = StringIO()
        writer:DictWriter = DictWriter(
            buff, required_field_names + optional_field_names, **self.definition._csv_config.writer_config)

        if self.definition._csv_config.should_write_header:
            writer.writeheader()

        for data_dict in gen:
            writer.writerow(data_dict)

        out = buff.getvalue()
        buff.close()

        return out

# ################################################################################################################################

    @cy.returns(object)
    def _convert_to_dicts(self, data:object, data_format:object) -> object:

        # No reason to continue if no SimpleIO output is declared
        if not (self.definition.has_output_required or self.definition.has_output_optional):
            return ''

        # Needed to find out if we are producing a list or a single element
        is_list:cy.bint

        # Local variables
        out_elems:list = []

        if isinstance(data, (list, tuple)):
            is_list = True
        else:
            is_list = False

        gen = self._yield_data_dicts(data, DATA_FORMAT_DICT)

        # Ignore field names, not needed in JSON nor XML serialisation
        next(gen)
        next(gen)

        for data_dict in gen:
            out_elems.append(data_dict)

        # Return a full list or a single element, depending on what is needed
        out:object = out_elems if is_list else out_elems[0]

        # Wrap the response in a top-level element if needed
        if data_format in (DATA_FORMAT_JSON, DATA_FORMAT_DICT):
            if self.definition._has_response_elem:
                out = {
                    self.definition._response_elem: out
                }

        return out

# ################################################################################################################################

    @cy.returns(object)
    def _get_output_json(self, data:object, serialise:cy.bint) -> object:
        out:object = self._convert_to_dicts(data, DATA_FORMAT_JSON)
        return self.serialise(out, DATA_FORMAT_JSON) if serialise else out

# ################################################################################################################################

    @cy.cfunc
    def _convert_dict_to_xml(self, parent:object, namespace:object, dict_elem:dict):
        key:object
        value:object

        for key, value in dict_elem.items():
            xml_elem = SubElement(parent, '{}{}'.format(namespace, key))
            xml_elem.text = str(value)

# ################################################################################################################################

    @cy.returns(object)
    def get_output(self, data:object, data_format:object, serialise:cy.int=True) -> object: # noqa: E252
        """ Returns input converted to the output format, possibly including serialisation to a string representation.
        """
        if data_format == DATA_FORMAT_JSON:
            return self._get_output_json(data, serialise)

        # Note that 'serialise' is ignored for CSV
        elif data_format == DATA_FORMAT_CSV:
            return self._get_output_csv(data)

        elif data_format in (DATA_FORMAT_DICT, DATA_FORMAT_FORM):
            out = self._convert_to_dicts(data, DATA_FORMAT_DICT)
            return out

        else:
            raise ValueError('Unrecognised output data format `{}`'.format(data_format))

# ################################################################################################################################

    @cy.returns(object)
    def serialise(self, data:object, data_format:object) -> object:
        """ Serialises input data to the data format specified.
        """
        if data_format == DATA_FORMAT_JSON:
            return self.server_config.json_encoder.encode(data)

        elif data_format == DATA_FORMAT_POST:
            return self._get_output_post(data)

        elif data_format == DATA_FORMAT_CSV:
            return self._get_output_csv(data)

        elif data_format == DATA_FORMAT.DICT:
            return data

        else:
            raise ValueError('Unrecognised output data format `{}`'.format(data_format))

# ################################################################################################################################

    def eval_multi(self, data, encrypt_func=None):
        """ Runs self.eval_ for each item in the input data dict.
        """
        for elem_name, value in data.items():
            data[elem_name] = self.eval_(elem_name, value, encrypt_func)

# ################################################################################################################################

    def eval_(self, elem_name, value, encrypt_func=None):
        """ Tries to evaluate elem_name as if it was a SIO element, no matter if it belongs to any request or response element.
        This is useful for dynamically created elements that should not be treated as mere strings.
        """
        # type: (str, object, object)

        exact:set
        prefixes:set
        suffixes:set
        is_int:bool

        config_item:ConfigItem

        handler_func_to_type:tuple = (
            (to_bool,      self.server_config.bool_config),
            (int,          self.server_config.int_config),
            (encrypt_func, self.server_config.secret_config),
        )

        for (handler_func, config_item) in handler_func_to_type:

            is_int    = handler_func is int
            is_secret = handler_func is encrypt_func

            exact = config_item.exact
            prefixes = config_item.prefixes
            suffixes = config_item.suffixes

            # Try an exact match first ..
            for config_elem in exact:
                if elem_name == config_elem:

                    # Special-case integers
                    if is_int:
                        if value is None or value == '':
                            return None

                    # Special-case secrets
                    if is_secret:
                        if encrypt_func:
                            return encrypt_func(value)

                    return handler_func(value)

            # .. try prefix matching then ..
            for config_elem in prefixes:
                if elem_name.startswith(config_elem):

                    # Special-case integers
                    if is_int:
                        if value is None or value == '':
                            return None

                    # Special-case secrets
                    if is_secret:
                        if encrypt_func:
                            return encrypt_func(value)

                    return handler_func(value)

            # .. finally, try suffix matching.
            for config_elem in suffixes:
                if elem_name.endswith(config_elem):

                    # Special-case integers
                    if is_int:
                        if value is None or value == '':
                            return None

                    # Special-case secrets
                    if is_secret:
                        if encrypt_func:
                            return encrypt_func(value)

                    return handler_func(value)

        return value or ''

# ################################################################################################################################

@cy.ccall
@cy.returns(cy.bint)
def is_sio_bool(value:object) -> cy.int:
    return isinstance(value, Bool)

# ################################################################################################################################

@cy.ccall
@cy.returns(cy.bint)
def is_sio_int(value:object) -> cy.int:
    return isinstance(value, Int)

# ################################################################################################################################

# Create server/process-wide singletons
NotGiven = _NotGiven()

# Akin to NotGiven but must not be used by users
InternalNotGiven = _InternalNotGiven()

# ################################################################################################################################
