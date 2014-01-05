# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from datetime import datetime
from httplib import OK
from itertools import chain
from sys import maxint
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import Bunch, bunchify

# Django
from django.http import QueryDict

# lxml
from lxml import etree
from lxml.etree import _Element as EtreeElement
from lxml.objectify import deannotate, Element, ElementMaker

# Paste
from paste.util.converters import asbool

# retools
from retools.lock import Lock, LockTimeout as RetoolsLockTimeout

# SQLAlchemy
from sqlalchemy.util import NamedTuple

# Zato
from zato.common import BROKER, CHANNEL, DATA_FORMAT, KVDB, NO_DEFAULT_VALUE, PARAMS_PRIORITY, ParsingException, \
     path, SIMPLE_IO, URL_TYPE, ZatoException, ZATO_NONE, ZATO_OK
from zato.common.broker_message import SERVICE
from zato.common.util import uncamelify, make_repr, new_cid, payload_from_request, service_name_from_impl, TRACE1
from zato.server.connection import request_response, slow_response
from zato.server.connection.amqp.outgoing import PublisherFacade
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.zmq_.outgoing import ZMQFacade
from zato.server.message import MessageFacade

logger = logging.getLogger(__name__)

NOT_GIVEN = 'ZATO_NOT_GIVEN'

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

        #
        # Key - bool/data_type,
        # - bool is True if this is a conversion from SIO to external data, False in the other direction
        # - data_type is one of DATA_TYPE
        #
        # Value - method to invoke to de-/serialize given value
        #
        self.serialize_dispatch = {
            (False, DATA_FORMAT.JSON): self.from_json,
            (False, DATA_FORMAT.XML): self.from_xml,

            (True, DATA_FORMAT.JSON): self.to_json,
            (True, DATA_FORMAT.XML): self.to_xml,
        }

    def __repr__(self):
        return '<{} at {} name:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.name)

    def from_json(self, value):
        raise NotImplementedError('Subclasses should override it')

    def to_json(self, value):
        raise NotImplementedError('Subclasses should override it')

    def from_xml(self, value):
        raise NotImplementedError('Subclasses should override it')

    def to_xml(self, value):
        raise NotImplementedError('Subclasses should override it')

    def convert(self, value, param_name, data_type, from_sio_to_external):
        return self.serialize_dispatch[(from_sio_to_external, data_type)](value, param_name)

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
        return ','.join(value)

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
                    raise ValidationException(self.name, value, key, 'Dict [{}] [{}]  has no key [{}]')
                else:
                    out[key] = v

            return out
        else:
            return value

    to_json = from_json

    def from_xml(self, value, *ignored):
        _dict = {}
        for item in value.iterchildren():
            _dict[item.find('key').text] = item.find('value').text
        return _dict

    def to_xml(self, value, param_name):
        return self.get_xml_dict(value, param_name)

# ################################################################################################################################

class Integer(ForceType):
    """ Gets transformed into an int object.
    """
    def from_json(self, value, *ignored):
        return int(value)

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class List(ForceType):
    """ Transformed into a list of items in JSON or a list of <item> elems in XML.
    """
    def from_json(self, value, *ignored):
        return value

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
    """ Transformed into a list of dictionaries in JSON or a
    list of
     <dict>
      <item>
        <key>key1</key>
        <value>value1</value>
      </item>
      <item>
        <key>key2</key>
        <value>value2</value>
      </item>
     <dict>
    elems in XML.
    """
    def from_json(self, value, *ignored):
        return value

    to_json = from_json

    def from_xml(self, value, *ignored):
        list_of_dicts = []

        for xml_dict in value.iterchildren():
            _dict = {}
            for item in xml_dict.iterchildren():
                _dict[item.find('key').text] = item.find('value').text
            list_of_dicts.append(_dict)

        return list_of_dicts

    def to_xml(self, value, param_name):
        wrapper = Element(param_name)

        for _dict in value:
            wrapper.append(self.get_xml_dict(_dict, 'dict'))

        return wrapper

# ################################################################################################################################

class Nested(ForceType):
    """ Allows for embedding arbitrary sub-elements, including simple strings, ForceType or other Nested elements.
    """

    def from_json(self, value, *ignored):
        return value

    to_json = from_json

    def __iter__(self):
        return iter(self.args)

# ################################################################################################################################

class Unicode(ForceType):
    """ Gets transformed into a unicode object.
    """
    def from_json(self, value, *ignored):
        return unicode(value)

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class UTC(ForceType):
    """ Will have the timezone part removed.
    """
    def from_json(self, value, *ignored):
        return value.replace('+00:00', '')

    from_xml = to_json = to_xml = from_json

# ################################################################################################################################

class ServiceInput(Bunch):
    """ A Bunch holding the input to the service.
    """
    def deepcopy(self):
        return deepcopy(self)

# ################################################################################################################################

COMPLEX_VALUE = (Dict, List, ListOfDicts, Nested)

# ################################################################################################################################

def convert_sio(param, param_name, value, has_simple_io_config, is_xml, bool_parameter_prefixes, int_parameters, 
                int_parameter_suffixes, date_time_format=None, data_format=ZATO_NONE, from_sio_to_external=False):
    try:
        if any(param_name.startswith(prefix) for prefix in bool_parameter_prefixes) or isinstance(param, Boolean):
            value = asbool(value or None) # value can be an empty string and asbool chokes on that

        if value and value is not None: # Can be a 0
            if isinstance(param, ForceType):
                value = param.convert(value, param_name, data_format, from_sio_to_external)
            else:
                if value and value != ZATO_NONE and has_simple_io_config:
                    if any(param_name==elem for elem in int_parameters) or \
                       any(param_name.endswith(suffix) for suffix in int_parameter_suffixes):
                        value = int(value)

        return value

    except Exception, e:
        msg = 'Conversion error, param:[{}], param_name:[{}], repr(value):[{}], e:[{}]'.format(
            param, param_name, repr(value), format_exc(e))
        logger.error(msg)

        raise ZatoException(msg=msg)

# ################################################################################################################################

class SIOConverter(object):
    """ A class which knows how to convert values into the types defined in a service's SimpleIO config.
    """
    def convert(self, *params):
        return convert_sio(*params)

# ################################################################################################################################

def convert_from_json(payload, param_name, cid, *ignored):
    return payload.get(param_name, NOT_GIVEN)

def convert_from_xml(payload, param_name, cid, is_required, is_complex, default_value, path_prefix, use_text):
    try:
        elem = path('{}.{}'.format(path_prefix, param_name), is_required).get_from(payload)
    except ParsingException, e:
        msg = 'Caught an exception while parsing, payload:[<![CDATA[{}]]>], e:[{}]'.format(
            etree.tostring(payload), format_exc(e))
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

convert_impl = {
    DATA_FORMAT.JSON: convert_from_json,
    DATA_FORMAT.XML: convert_from_xml,
}

def convert_param(cid, payload, param, data_format, is_required, default_value, path_prefix, use_text, 
                  channel_params, has_simple_io_config, bool_parameter_prefixes, int_parameters, int_parameter_suffixes):
    """ Converts request parameters from any data format supported into Python objects.
    """
    param_name = param.name if isinstance(param, ForceType) else param
    value = convert_impl[data_format](payload, param_name, cid, is_required, isinstance(param, COMPLEX_VALUE), 
                                      default_value, path_prefix, use_text)

    if value == NOT_GIVEN:
        if default_value != NO_DEFAULT_VALUE:
            value = default_value
        else:
            if is_required and not channel_params.get(param_name):
                msg = 'Required input element:[{}] not found, value:[{}]'.format(param, value)
                raise ParsingException(cid, msg)
            else:
                # Not required and not provided on input
                value = ''
    else:
        if value is not None and not isinstance(param, COMPLEX_VALUE):
            value = unicode(value)

        if not isinstance(param, AsIs):
            return param_name, convert_sio(param, param_name, value, has_simple_io_config, data_format==DATA_FORMAT.XML,
                bool_parameter_prefixes, int_parameters, int_parameter_suffixes, None, data_format, False)

    return param_name, value
