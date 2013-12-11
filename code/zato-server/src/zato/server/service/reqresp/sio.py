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

class ForceType(object):
    """ Forces a SimpleIO element to use a specific data type.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{} at {} name:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.name)

class AsIs(ForceType):
    """ The object won't be converted by SimpleIO machinery even though normally
    it would've been, for instance, because its name is 'user_id' and should've
    been converted over to an int.
    """

class Boolean(ForceType):
    """ Gets transformed into a bool object.
    """

class CSV(ForceType):
    """ Gets transformed into a comma separated list of items.
    """

class Dict(ForceType):
    """ JSON dictionary or a key/value in XML.
    """

class Integer(ForceType):
    """ Gets transformed into an int object.
    """

class List(ForceType):
    """ Transformed into a list of items in JSON or a list of <item> elems in XML.
    """

class ListOfDicts(ForceType):
    """ Transformed into a list of dictionaries in JSON or a
    list of
      <item>
        <key>key1</key>
        <value>value1</value>
      </item>
      <item>
        <key>key2</key>
        <value>value2</value>
      </item>
    elems in XML.
    """

class Unicode(ForceType):
    """ Gets transformed into a unicode object.
    """

class UTC(ForceType):
    """ Will have the timezone part removed.
    """

class ServiceInput(Bunch):
    """ A Bunch holding the input to the service.
    """
    def deepcopy(self):
        return deepcopy(self)

COMPLEX_VALUE = (Dict, List, ListOfDicts)

# ################################################################################################################################

def convert_sio(param, param_name, value, has_simple_io_config, is_xml, bool_parameter_prefixes, int_parameters, 
                int_parameter_suffixes, date_time_format=None):
    try:
        if any(param_name.startswith(prefix) for prefix in bool_parameter_prefixes) or isinstance(param, Boolean):
            value = asbool(value or None) # value can be an empty string and asbool chokes on that

        if value and value is not None: # Can be a 0
            if isinstance(param, Boolean):
                value = asbool(value)

            elif isinstance(param, CSV):
                # Incoming request that is converted into a list
                if isinstance(value, basestring):
                    return value.split(',')

                # We're producing a response and a list is converted into a CSV
                else:
                    return ','.join(value)

            elif isinstance(param, Dict):

                if is_xml:

                    # We are parsing XML to create a SIO request
                    if isinstance(value, EtreeElement):
                        _dict = {}
                        for item in value.iterchildren():
                            _dict[item.find('key').text] = item.find('value').text
                        return _dict

                    # We are producing XML out of an SIO response
                    else:
                        wrapper = Element(param_name)

                        for k, v in value.items():
                            xml_item = Element('item')

                            key = Element('key')
                            value = Element('value')

                            xml_item.key = key
                            xml_item.value = value

                            xml_item.key[-1] = k
                            xml_item.value[-1] = v

                            wrapper.append(xml_item)

                        return wrapper
                else:
                    # This is a JSON dictionary
                    return value

            elif isinstance(param, Integer):
                value = int(value)

            elif isinstance(param, List):
                if is_xml:

                    # We are parsing XML to create a SIO request
                    if isinstance(value, EtreeElement):
                        return [elem.text for elem in value.iterchildren()]

                    # We are producing XML out of an SIO response
                    else:
                        wrapper = Element(param_name)
                        for item_value in value:
                            xml_item = Element('item')
                            wrapper.append(xml_item)
                            wrapper.item[-1] = item_value
                        return wrapper

                # This is a JSON list
                return value

            elif isinstance(param, ListOfDicts):
                if is_xml:

                    # We are parsing XML to create a SIO request
                    if isinstance(value, EtreeElement):
                        list_of_dicts = []

                        for xml_dict in value.iterchildren():
                            _dict = {}
                            for item in xml_dict.iterchildren():
                                _dict[item.find('key').text] = item.find('value').text
                            list_of_dicts.append(_dict)

                        return list_of_dicts

                    else:
                        wrapper = Element(param_name)

                        for _dict in value:
                            xml_dict = Element('dict')

                            for k, v in _dict.items():
                                xml_item = Element('item')

                                key = Element('key')
                                value = Element('value')

                                xml_item.key = key
                                xml_item.value = value

                                xml_item.key[-1] = k
                                xml_item.value[-1] = v

                                xml_dict.append(xml_item)

                            wrapper.append(xml_dict)

                        return wrapper

                else:
                    # This is a JSON of dictionaries
                    return value

            elif isinstance(param, Unicode):
                value = unicode(value)

            elif isinstance(param, UTC):
                value = value.replace('+00:00', '')

            else:
                if value and value != ZATO_NONE and has_simple_io_config:
                    if any(param_name==elem for elem in int_parameters) or \
                       any(param_name.endswith(suffix) for suffix in int_parameter_suffixes):
                        value = int(value)

            if date_time_format and isinstance(value, datetime):
                value = value.strftime(date_time_format)

        if isinstance(param, CSV) and not value:
            value = []

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
                bool_parameter_prefixes, int_parameters, int_parameter_suffixes)

    return param_name, value
