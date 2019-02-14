# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import datetime
import logging
from copy import deepcopy
from traceback import format_exc

# Bunch
from bunch import Bunch

# lxml
from lxml import etree
from lxml.objectify import Element

# Paste
from paste.util.converters import asbool

# Python 2/3 compatibility
from builtins import bytes
from past.builtins import cmp, unicode

# Zato
from zato.common import APISPEC, DATA_FORMAT, NO_DEFAULT_VALUE, PARAMS_PRIORITY, ParsingException, path, SECRETS, \
     ZatoException, ZATO_NONE, ZATO_SEC_USE_RBAC
from zato.common.exception import BadRequest, Reportable
from zato.common.pubsub import PubSubMessage

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

NOT_GIVEN = b'ZATO_NOT_GIVEN'
_sio_list_like = (list, tuple)

# ################################################################################################################################

class ValidationException(ZatoException):
    def __init__(self, name, value, missing_elem, template):
        self.name = name
        self.value = value
        self.missing_elem = missing_elem
        super(ValidationException, self).__init__(None, template.format(self.name, self.value, self.missing_elem))

# ################################################################################################################################

class ForceType(object):
    """ Forces a SimpleIO element to use a specific data type.
    """
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.default = kwargs.get('default', NO_DEFAULT_VALUE)
        self._list_like = kwargs.get('list_like') or _sio_list_like

        #
        # Key - bool/data_type,
        # - bool is True if this is a conversion from SIO to external data, False in the other direction
        # - data_type is one of DATA_TYPE
        #
        # Value - method to invoke to de-/serialize given value
        #
        self.serialize_dispatch = {
            (False, DATA_FORMAT.JSON): self.from_json,
            (False, DATA_FORMAT.DICT): self.from_json,
            (False, DATA_FORMAT.DICT): self.from_json,
            (False, ''): self.from_json,
            (False, DATA_FORMAT.XML): self.from_xml,

            (True, DATA_FORMAT.JSON): self.to_json,
            (True, DATA_FORMAT.DICT): self.to_json,
            (True, ''): self.to_json,
            (True, DATA_FORMAT.XML): self.to_xml,
        }

    def __cmp__(self, other):
        cmp_to = getattr(other, 'name', other)
        return cmp(self.name, cmp_to)

    def __repr__(self):
        return '<{} at {} name:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.name)

    def from_json(self, value, *ignored):
        raise NotImplementedError('Subclasses should override it')

    def to_json(self, value, *ignored):
        raise NotImplementedError('Subclasses should override it')

    def from_xml(self, value, *ignored):
        raise NotImplementedError('Subclasses should override it')

    def to_xml(self, value, *ignored):
        raise NotImplementedError('Subclasses should override it')

    def convert(self, value, param_name, data_type, from_sio_to_external):
        return self.serialize_dispatch[(from_sio_to_external, data_type)](value, param_name) if value is not None else value

    def get_xml_dict(self, _dict, name):
        xml_dict = Element(name)

        for k, v in _dict.items():
            xml_item = Element('item')

            key = Element('key')
            value = Element('value')

            xml_item.key = key
            xml_item.value = value

            xml_item.key[-1] = k
            xml_item.value[-1] = v

            xml_dict.append(xml_item)

        return xml_dict

# ################################################################################################################################

class AsIs(ForceType):
    """ The object won't be converted by SimpleIO machinery even though normally
    it would've been, for instance, because its name is 'user_id' and should've
    been converted over to an int.
    """
    def from_json(self, value, *ignored):
        return value

    to_json = from_json

# ################################################################################################################################

class Boolean(ForceType):
    """ Gets transformed into a bool object.
    """
    def from_json(self, value, *ignored):
        return asbool(value)

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class CSV(ForceType):
    """ Gets transformed into a comma separated list of items.
    """
    def from_json(self, value, *ignored):
        return value.split(',')

    from_xml = from_json

    def to_json(self, value, *ignored):
        return ','.join(value) if isinstance(value, (list, tuple)) else value

    to_xml = to_json

# ################################################################################################################################

class Dict(ForceType):
    """ JSON dictionary or a key/value in XML.
    """
    def from_json(self, value, *ignored):
        if self.args:
            out = {}
            for key in self.args:
                v = value.get(key, self.default)
                if v == NO_DEFAULT_VALUE:
                    raise ValidationException(self.name, value, key, 'Dict `{}` `{}`  has no key `{}`')
                else:
                    out[key] = v

            return out
        else:
            return value

    to_json = from_json

    def from_xml(self, value, *ignored):
        _dict = {}
        for item in value.iterchildren():
            _dict[item.key.text] = item.value.text
        return _dict

    def to_xml(self, value, param_name):
        return self.get_xml_dict(value, param_name)

# ################################################################################################################################

class Float(ForceType):
    """ Gets transformed into a float object.
    """
    def from_json(self, value, *ignored):
        try:
            return float(value)
        except ValueError:
            raise BadRequest(None, 'Cannot convert `{}` to float'.format(value))

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class Integer(ForceType):
    """ Gets transformed into an int object.
    """
    def from_json(self, value, *ignored):
        return int(value) if value else value

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class List(ForceType):
    """ Transformed into a list of items in JSON or a list of <item> elems in XML.
    """
    def from_json(self, value, *ignored):
        return value if isinstance(value, self._list_like) else [value]

    to_json = from_json

    def from_xml(self, value, *ignored):
        return [elem.text for elem in value.iterchildren()]

    def to_xml(self, value, param_name):
        wrapper = Element(param_name)
        for item_value in value:
            xml_item = Element('item')
            wrapper.append(xml_item)
            wrapper.item[-1] = item_value
        return wrapper

# ################################################################################################################################

class ListOfDicts(ForceType):
    """ Transformed into a list of dictionaries in JSON or a list of
     <my_list_of_dicts>
      <item_dict>
       <item>
         <key>key1</key>
         <value>value1</value>
       </item>
       <item>
         <key>key2</key>
         <value>value2</value>
       </item>
      </item_dict>
      <item_dict>
       <item>
         <key>key3</key>
         <value>value3</value>
       </item>
      </item_dict>
     <my_list_of_dicts>
    elems in XML.
    """
    def from_json(self, value, *ignored):
        return value

    to_json = from_json

    def from_xml(self, value, *ignored):
        list_of_dicts = []

        for item_dict in value.item_dict:
            _dict = {}
            for item in item_dict.iterchildren():
                _dict[item.key.text] = item.value.text
            list_of_dicts.append(_dict)

        return list_of_dicts

    def to_xml(self, value, param_name):
        wrapper = Element(param_name)

        for _dict in value:
            wrapper.append(self.get_xml_dict(_dict, 'dict'))

        return wrapper

# ################################################################################################################################

class Opaque(ForceType):
    """ Allows for embedding arbitrary sub-elements, including simple strings, ForceType or other Nested elements.
    """

    def from_json(self, value, *ignored):
        return value

    to_json = from_json

    def __iter__(self):
        return iter(self.args)

Nested = Opaque

# ################################################################################################################################

class Unicode(ForceType):
    """ Gets transformed into a unicode object.
    """
    def from_json(self, value, *ignored):
        return value if isinstance(value, unicode) else value.decode('utf-8')

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class UTC(ForceType):
    """ Will have the timezone part removed.
    """
    def from_json(self, value, *ignored):
        return value.replace('+00:00', '')

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class Date(ForceType):
    """ Serializes an object to a date string if it is not a string already.
    """
    def __init__(self, name, format='%Y-%m-%d', *args, **kwargs):
        super(Date, self).__init__(name, format=format, *args, **kwargs)

    def from_json(self, value, *ignored):
        if isinstance(value, datetime.date):
            if value.year < 1900:
                return value.isoformat()
            else:
                return value.strftime(self.kwargs['format'])
        else:
            return value

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class DateTime(ForceType):
    """ Serializes an object to a datetime string if it is not a string already.
    """
    def __init__(self, name, format='iso', *args, **kwargs):
        super(DateTime, self).__init__(name, format=format, *args, **kwargs)

    def from_json(self, value, *ignored):
        if isinstance(value, datetime.datetime):
            if self.kwargs['format'] == 'iso':
                return value.isoformat()
            else:
                if value.year < 1900:
                    return value.isoformat()
                else:
                    return value.strftime(self.kwargs['format'])
        else:
            return value

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class ServiceInput(Bunch):
    """ A Bunch holding the input to the service.
    """
    def deepcopy(self):
        return deepcopy(self)

    def require_any(self, *elems):
        for name in elems:
            if self.get(name):
                break
        else:
            raise ValueError('At least one of `{}` is required'.format(', '.join(elems)))

# ################################################################################################################################

COMPLEX_VALUE = (AsIs, Dict, List, ListOfDicts, Nested)

# ################################################################################################################################

def is_bool(param, param_name, bool_parameter_prefixes, _Boolean=Boolean):
    return any(param_name.startswith(prefix) for prefix in bool_parameter_prefixes) or isinstance(param, _Boolean)

# ################################################################################################################################

def is_int(param_name, int_params, int_param_suffixes):
    if any(param_name==elem for elem in int_params) or any(param_name.endswith(suffix) for suffix in int_param_suffixes):
        return True

# ################################################################################################################################

def is_secret(param_name, _secrets_params=SECRETS.PARAMS):
    # Zato 3.1+ will have SIO rewritten to handle user-specified parameters but today this list is fixed.
    return param_name in _secrets_params

# ################################################################################################################################

def resolve_default_value(param, default_value):
    if isinstance(param, ForceType):

        # Use the per-element's default value ..
        value = param.default

        # .. but if it is missing ..
        if value == NO_DEFAULT_VALUE:

            # .. use the SimpleIO-level default value, but only if it is not missing either.
            value = default_value if default_value != NO_DEFAULT_VALUE else ''

    # Not a ForceType wrapper, default to an empty string in this case.
    else:
        value = ''

    return value

# ################################################################################################################################

def _resolve_output_value(param, force_empty_keys):
    return None if force_empty_keys else resolve_default_value(param, '')

# ################################################################################################################################

def convert_sio(cid, param, param_name, value, has_simple_io_config, is_xml, bool_parameter_prefixes, int_parameters,
    int_parameter_suffixes, force_empty_keys, encrypt_func, encrypt_secrets, date_time_format=None, data_format=ZATO_NONE,
    from_sio_to_external=False, special_values=(str(ZATO_NONE), str(ZATO_SEC_USE_RBAC)), _is_bool=is_bool, _is_int=is_int,
    _is_secret=is_secret):
    try:

        if _is_bool(param, param_name, bool_parameter_prefixes):
            if value == '':
                value = _resolve_output_value(param, force_empty_keys)
            else:
                value = asbool(value or None) # value can be an empty string and asbool chokes on that
            return value

        if value is not None:
            if isinstance(param, ForceType):
                if value == '':
                    value = _resolve_output_value(param, force_empty_keys)
                else:
                    value = param.convert(value, param_name, data_format, from_sio_to_external)
            else:
                # Empty string sent in lieu of integers are equivalent to None,
                # as though they were never sent - this is needed for internal metaclasses
                if value == b'':
                    if _is_int(param_name, int_parameters, int_parameter_suffixes):
                        value = None

                if value:
                    if (value not in special_values) and has_simple_io_config:
                        if _is_int(param_name, int_parameters, int_parameter_suffixes):
                            value = int(value)
                        elif encrypt_secrets and _is_secret(param_name):
                            # It will be None in SIO responses
                            if encrypt_func:
                                value = encrypt_func(value)

        return value

    except Exception as e:
        if isinstance(e, Reportable):
            e.cid = cid
            raise
        else:
            msg = 'Conversion error, param:`{}`, param_name:`{}`, repr:`{}`, type:`{}`, e:`{}`'.format(
                param, param_name, repr(value), type(value), format_exc(e))
            logger.error(msg)

            raise ZatoException(msg=msg)

# ################################################################################################################################

class SIOConverter(object):
    """ A class which knows how to convert values into the types defined in a service's SimpleIO config.
    """
    def convert(self, *params):
        value = convert_sio(*params)

        if self.zato_bytes_to_str_encoding and isinstance(value, bytes):
            value = value.decode(self.zato_bytes_to_str_encoding)

        return value

# ################################################################################################################################

def convert_from_json(payload, param_name, cid, *ignored):
    return (payload or {}).get(param_name, NOT_GIVEN)

convert_from_dict = convert_from_json

# ################################################################################################################################

def convert_from_xml(payload, param_name, cid, is_required, is_complex, default_value, path_prefix, use_text):
    try:
        elem = path('{}.{}'.format(path_prefix, param_name), is_required).get_from(payload)
    except ParsingException:
        msg = 'Caught an exception while parsing, payload:`<![CDATA[{}]]>`, e:`{}`'.format(
            etree.tostring(payload), format_exc())
        raise ParsingException(cid, msg)

    if is_complex:
        value = elem
    else:
        if elem is not None:
            if use_text:
                value = elem.text # We are interested in the text the elem contains ..
            else:
                return elem # .. or in the elem itself.
        else:
            value = default_value

    return value

# ################################################################################################################################

convert_impl = {
    DATA_FORMAT.JSON: convert_from_json,
    DATA_FORMAT.XML: convert_from_xml,
    DATA_FORMAT.DICT: convert_from_dict,
    None: convert_from_dict,
}

# ################################################################################################################################

def convert_param(cid, payload, param, data_format, is_required, default_value, path_prefix, use_text, channel_params,
    has_simple_io_config, bool_parameter_prefixes, int_parameters, int_parameter_suffixes, force_empty_keys, encrypt_func,
    encrypt_secrets, params_priority):
    """ Converts request parameters from any data format supported into Python objects.
    """
    param_name = param.name if isinstance(param, ForceType) else param

    # First thing is to find out if we have parameters in channel_params. If so and they have priority
    # over payload, we don't look further. If they don't have priority, whether the value from channel_params
    # is used depends on whether the payload one exists at all.

    # We've got a value from the channel, i.e. in GET parameters
    channel_value = channel_params.get(param_name, ZATO_NONE)

    # Convert it to a native Python data type
    if channel_value != ZATO_NONE:
        channel_value = convert_sio(cid, param, param_name, channel_value, has_simple_io_config, False, bool_parameter_prefixes,
            int_parameters, int_parameter_suffixes, force_empty_keys, encrypt_func, encrypt_secrets, None, data_format, False)

    # Return the value immediately if we already know channel_params are of higer priority
    if params_priority == PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG and channel_value != ZATO_NONE:
        return param_name, channel_value

    # Ok, at that point we either don't have anything in channel_params or they don't have priority over payload.

    if payload is not None:
        value = convert_impl[data_format](payload, param_name, cid, is_required, isinstance(param, COMPLEX_VALUE),
            default_value, path_prefix, use_text)
    else:
        value = NOT_GIVEN

    if (not isinstance(value, PubSubMessage)) and value == NOT_GIVEN:
        if default_value != NO_DEFAULT_VALUE:
            value = default_value
        else:
            if is_required:

                # Ok, we don't have anything in payload but it still may be in channel_params.
                # We arrive here if params priority is not params over msg.
                value = channel_value if (channel_value is not None and channel_value != ZATO_NONE) else ZATO_NONE

                if value == ZATO_NONE:
                    msg = 'Required input element:`{}` not found, value:`{}`, data_format:`{}`, payload:`{}`'\
                        ', channel_params:`{}`'.format(param, value, data_format, payload, channel_params)
                    raise ParsingException(cid, msg)
            else:
                # Not required and not provided on input either in msg or channel params
                # so we can use an empty string, but with ForceType elements in particular,
                # we want to use their optional default value so as not to assume anything about input data.
                value = resolve_default_value(param, default_value)

    else:
        if value is not None and not isinstance(param, COMPLEX_VALUE):
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            else:
                value = unicode(value)

        if not isinstance(param, (AsIs, Opaque)):
            return param_name, convert_sio(cid, param, param_name, value, has_simple_io_config, data_format==DATA_FORMAT.XML,
                bool_parameter_prefixes, int_parameters, int_parameter_suffixes, force_empty_keys, encrypt_func, encrypt_secrets,
                None, data_format, False)

    return param_name, value

# ################################################################################################################################

class SIO_TYPE_MAP:

# ################################################################################################################################

    class OPEN_API_V3:

        name = APISPEC.OPEN_API_V3
        STRING = ('string', 'string')
        DEFAULT = STRING
        INTEGER = ('integer', 'int32')
        BOOLEAN = ('boolean', 'boolean')

        map = {
            AsIs: STRING,
            Boolean: BOOLEAN,
            CSV: STRING,
            Dict: ('string', 'binary'),
            Float: ('number', 'float'),
            Integer: INTEGER,
            List: ('string', 'binary'),
            ListOfDicts: ('string', 'binary'),
            Opaque: ('string', 'binary'),
            Unicode: STRING,
            UTC: ('string', 'date-time'),
        }

    class SOAP_12:

        name = APISPEC.SOAP_12
        STRING = ('string', 'xsd:string')
        DEFAULT = STRING
        INTEGER = ('integer', 'xsd:integer')
        BOOLEAN = ('boolean', 'xsd:boolean')

        map = {
            AsIs: STRING,
            Boolean: BOOLEAN,
            CSV: STRING,
            Dict: ('dict', 'zato:dict'),
            Float: ('number', 'float'),
            Integer: INTEGER,
            List: ('list', 'zato:list'),
            ListOfDicts: ('list-of-dicts', 'zato:list-of-dicts'),
            Opaque: ('opaque', 'anyType'),
            Unicode: STRING,
            UTC: ('string', 'xsd:dateTime'),
        }

# ################################################################################################################################

    class ZATO:

        name = 'zato'
        STRING = ('string', 'string')
        DEFAULT = STRING
        INTEGER = ('integer', 'integer')
        BOOLEAN = ('boolean', 'boolean')

        map = {
            AsIs: STRING,
            Boolean: BOOLEAN,
            CSV: STRING,
            Dict: ('dict', 'dict'),
            Float: ('number', 'float'),
            Integer: INTEGER,
            List: ('list', 'list'),
            ListOfDicts: ('list', 'list-of-dicts'),
            Opaque: ('opaque', 'opaque'),
            Unicode: STRING,
            UTC: ('string', 'date-time-utc'),
        }

# ################################################################################################################################

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.OPEN_API_V3, self.SOAP_12, self.ZATO))

# ################################################################################################################################
