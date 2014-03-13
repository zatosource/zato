# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

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
from zato.common import BROKER, CHANNEL, KVDB, NO_DEFAULT_VALUE, PARAMS_PRIORITY, ParsingException, \
     path, SIMPLE_IO, URL_TYPE, ZatoException, ZATO_NONE, ZATO_OK
from zato.common.broker_message import SERVICE
from zato.common.util import uncamelify, make_repr, new_cid, payload_from_request, service_name_from_impl, TRACE1
from zato.server.connection import request_response, slow_response
from zato.server.connection.amqp.outgoing import PublisherFacade
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.zmq_.outgoing import ZMQFacade
from zato.server.message import MessageFacade
from zato.server.service.reqresp.sio import AsIs, COMPLEX_VALUE, convert_param, ForceType, ServiceInput, SIOConverter

logger = logging.getLogger(__name__)

NOT_GIVEN = 'ZATO_NOT_GIVEN'

# ################################################################################################################################

class HTTPRequestData(object):
    """ Data regarding an HTTP request.
    """
    def __init__(self):
        self.method = None
        self.GET = None
        self.POST = None

    def init(self, wsgi_environ={}):
        self.method = wsgi_environ.get('REQUEST_METHOD')

        # Note tht we always require UTF-8
        self.GET = wsgi_environ.get('zato.http.GET', {})
        self.POST = wsgi_environ.get('zato.http.POST', {})

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class Request(SIOConverter):
    """ Wraps a service request and adds some useful meta-data.
    """
    __slots__ = ('logger', 'payload', 'raw_request', 'input', 'cid', 'has_simple_io_config',
                 'simple_io_config', 'bool_parameter_prefixes', 'int_parameters',
                 'int_parameter_suffixes', 'is_xml', 'data_format', 'transport',
                 '_wsgi_environ', 'channel_params', 'merge_channel_params')

    def __init__(self, logger, simple_io_config={}, data_format=None, transport=None):
        self.logger = logger
        self.payload = ''
        self.raw_request = ''
        self.input = ServiceInput()
        self.cid = None
        self.simple_io_config = simple_io_config
        self.has_simple_io_config = False
        self.bool_parameter_prefixes = simple_io_config.get('bool_parameter_prefixes', [])
        self.int_parameters = simple_io_config.get('int_parameters', [])
        self.int_parameter_suffixes = simple_io_config.get('int_parameter_suffixes', [])
        self.is_xml = None
        self.data_format = data_format
        self.transport = transport
        self.http = HTTPRequestData()
        self._wsgi_environ = None
        self.channel_params = {}
        self.merge_channel_params = True
        self.params_priority = PARAMS_PRIORITY.DEFAULT

    def init(self, is_sio, cid, io, data_format, transport, wsgi_environ):
        """ Initializes the object with an invocation-specific data.
        """

        if is_sio:
            self.is_xml = data_format == SIMPLE_IO.FORMAT.XML
            self.data_format = data_format
            self.transport = transport
            self._wsgi_environ = wsgi_environ

            path_prefix = getattr(io, 'request_elem', 'request')
            required_list = getattr(io, 'input_required', [])
            optional_list = getattr(io, 'input_optional', [])
            default_value = getattr(io, 'default_value', NO_DEFAULT_VALUE)
            use_text = getattr(io, 'use_text', True)

            if self.simple_io_config:
                self.has_simple_io_config = True
                self.bool_parameter_prefixes = self.simple_io_config.get('bool_parameter_prefixes', [])
                self.int_parameters = self.simple_io_config.get('int_parameters', [])
                self.int_parameter_suffixes = self.simple_io_config.get('int_parameter_suffixes', [])
            else:
                self.payload = self.raw_request

            if required_list:
                required_params = self.get_params(required_list, path_prefix, default_value, use_text)
            else:
                required_params = {}

            if optional_list:
                optional_params = self.get_params(optional_list, path_prefix, default_value, use_text, False)
            else:
                optional_params = {}

            if self.params_priority == PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG:
                self.input.update(required_params)
                self.input.update(optional_params)
                self.input.update(self.channel_params)
            else:
                self.input.update(self.channel_params)
                self.input.update(required_params)
                self.input.update(optional_params)

        # We merge channel params in if requested even if it's not SIO
        else:
            if self.merge_channel_params:
                self.input.update(self.channel_params)

    def get_params(self, request_params, path_prefix='', default_value=NO_DEFAULT_VALUE, use_text=True, is_required=True):
        """ Gets all requested parameters from a message. Will raise ParsingException if any is missing.
        """
        params = {}
        if not isinstance(self.payload, basestring):
            for param in request_params:
                try:
                    param_name, value = convert_param(self.cid, self.payload, param, self.data_format, is_required, default_value,
                            path_prefix, use_text, self.channel_params, self.has_simple_io_config,
                            self.bool_parameter_prefixes, self.int_parameters, self.int_parameter_suffixes)
                    params[param_name] = value
    
                except Exception, e:
                    msg = 'Caught an exception, param:[{}], self.has_simple_io_config:[{}], e:[{}]'.format(
                        param, self.has_simple_io_config, format_exc(e))
                    self.logger.error(msg)
                    raise Exception(msg)
        else:
            if self.logger.isEnabledFor(TRACE1):
                msg = 'payload repr=[{}], type=[{}]'.format(repr(self.payload), type(self.payload))
                self.logger.log(TRACE1, msg)

        return params

    def deepcopy(self):
        """ Returns a deep copy of self.
        """
        request = Request(None)
        request.logger = logging.getLogger(self.logger.name)

        for name in Request.__slots__:
            if name == 'logger':
                continue
            setattr(request, name, deepcopy(getattr(self, name)))

        return request

    def bunchified(self):
        """ Returns a bunchified (converted into bunch.Bunch) version of self.raw_request,
        deep copied if it's a dict (or a subclass). Note that it makes sense to use this method
        only with dicts or JSON input.
        """
        # We have a dict
        if isinstance(self.raw_request, dict):
            return bunchify(deepcopy(self.raw_request))

        # Must be a JSON input, raises exception when attempting to load it if it's not
        return bunchify(loads(self.raw_request))

# ################################################################################################################################

class SimpleIOPayload(SIOConverter):
    """ Produces the actual response - XML or JSON - out of the user-provided
    SimpleIO abstract data. All of the attributes are prefixed with zato_ so that
    they don't conflict with user-provided data.
    """
    def __init__(self, zato_cid, logger, data_format, required_list, optional_list, simple_io_config, response_elem, namespace):
        self.zato_cid = zato_cid
        self.zato_logger = logger
        self.zato_data_format = data_format
        self.zato_is_xml = self.zato_data_format == SIMPLE_IO.FORMAT.XML
        self.zato_output = []
        self.zato_required = [(True, name) for name in required_list]
        self.zato_optional = [(False, name) for name in optional_list]
        self.zato_is_repeated = False
        self.bool_parameter_prefixes = simple_io_config.get('bool_parameter_prefixes', [])
        self.int_parameters = simple_io_config.get('int_parameters', [])
        self.int_parameter_suffixes = simple_io_config.get('int_parameter_suffixes', [])
        self.date_time_format = simple_io_config.get('date_time_format', 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM')
        self.response_elem = response_elem
        self.namespace = namespace

        self.zato_all_attrs = set()
        for name in chain(required_list, optional_list):
            if isinstance(name, ForceType):
                name = name.name
            self.zato_all_attrs.add(name)

        self.set_expected_attrs(required_list, optional_list)

    def __setslice__(self, i, j, seq):
        """ Assigns a list of output elements to self.zato_output, so that they
        don't have to be each individually appended. Also sets a flag indicating
        that the payload is actually a list of repeated elements.
        """
        self.zato_output[i:j] = seq
        self.zato_is_repeated = True

    def _is_sqlalchemy(self, item):
        return hasattr(item, '_sa_class_manager')

    def set_expected_attrs(self, required_list, optional_list):
        """ Dynamically assigns all the expected attributes to self. Setting a value
        of an attribute will actually add data to self.zato_output.
        """
        for name in chain(required_list, optional_list):
            if isinstance(name, ForceType):
                name = name.name
            setattr(self, name, '')

    def set_payload_attrs(self, attrs):
        """ Called when the user wants to set the payload to a bunch of attributes.
        """
        names = None
        if isinstance(attrs, (dict, NamedTuple)):
            names = attrs.keys()
        elif self._is_sqlalchemy(attrs):
            names = attrs._sa_class_manager.keys()

        if not names:
            raise Exception('Could not get the keys out of attrs:[{}]'.format(attrs))

        if isinstance(attrs, dict):
            for name in names:
                setattr(self, name, attrs[name])
        else:
            for name in names:
                setattr(self, name, getattr(attrs, name))

    def append(self, item):
        self.zato_output.append(item)
        self.zato_is_repeated = True

    def _getvalue(self, name, item, is_sa_namedtuple, is_required, leave_as_is):
        """ Returns an element's value if any has been provided while taking
        into account the differences between dictionaries and other formats
        as well as the type conversions.
        """
        lookup_name = name.name if isinstance(name, ForceType) else name

        if is_sa_namedtuple or self._is_sqlalchemy(item):
            elem_value = getattr(item, lookup_name, '')
        else:
            elem_value = item.get(lookup_name, '')

        if isinstance(elem_value, basestring) and not elem_value:
            msg = self._missing_value_log_msg(name, item, is_sa_namedtuple, is_required)
            if is_required:
                self.zato_logger.debug(msg)
                raise ZatoException(self.zato_cid, msg)
            else:
                if self.zato_logger.isEnabledFor(TRACE1):
                    self.zato_logger.log(TRACE1, msg)

        if leave_as_is:
            return elem_value
        else:
            return self.convert(name, lookup_name, elem_value, True, self.zato_is_xml, self.bool_parameter_prefixes,
                self.int_parameters, self.int_parameter_suffixes, None, self.zato_data_format, True)

    def _missing_value_log_msg(self, name, item, is_sa_namedtuple, is_required):
        """ Returns a log message indicating that an element was missing.
        """
        if is_sa_namedtuple:
            msg_item = (item.keys(), item)
        else:
            msg_item = item
        return '{} elem:[{}] not found in item:[{}]'.format(
            'Expected' if is_required else 'Optional', name, msg_item)

    def getvalue(self, serialize=True):
        """ Gets the actual payload's value converted to a string representing
        either XML or JSON.
        """
        if self.zato_is_xml:
            if self.zato_is_repeated:
                value = Element('item_list')
            else:
                value = Element('item')
        else:
            if self.zato_is_repeated:
                value = []
            else:
                value = {}

        if self.zato_is_repeated:
            output = self.zato_output
        else:
            output = set(dir(self)) & self.zato_all_attrs
            output = [dict((name, getattr(self, name)) for name in output)]

        if output:

            # All elements must be of the same type so it's OK to do it
            is_sa_namedtuple = isinstance(output[0], NamedTuple)

            for item in output:
                if self.zato_is_xml:
                    out_item = Element('item')
                else:
                    out_item = {}
                for is_required, name in chain(self.zato_required, self.zato_optional):
                    leave_as_is = isinstance(name, AsIs)
                    elem_value = self._getvalue(name, item, is_sa_namedtuple, is_required, leave_as_is)

                    if isinstance(name, ForceType):
                        name = name.name

                    if isinstance(elem_value, basestring):
                        elem_value = elem_value.decode('utf-8')

                    if self.zato_is_xml:
                        setattr(out_item, name, elem_value)
                    else:
                        out_item[name] = elem_value

                if self.zato_is_repeated:
                    value.append(out_item)
                else:
                    value = out_item

        if self.zato_is_xml:
            em = ElementMaker(annotate=False, namespace=self.namespace, nsmap={None:self.namespace})
            zato_env = em.zato_env(em.cid(self.zato_cid), em.result(ZATO_OK))
            top = getattr(em, self.response_elem)(zato_env)
            top.append(value)
        else:
            top = {self.response_elem: value}

        if serialize:
            if self.zato_is_xml:
                deannotate(top, cleanup_namespaces=True)
                return etree.tostring(top)
            else:
                return dumps(top)
        else:
            return top

# ################################################################################################################################

class Outgoing(object):
    """ A container for various outgoing connections a service can access. This
    in fact is a thin wrapper around data fetched from the service's self.worker_store.
    """
    __slots__ = ('ftp', 'amqp', 'zmq', 'jms_wmq', 'sql', 'plain_http', 'soap')

    def __init__(self, ftp=None, amqp=None, zmq=None, jms_wmq=None, sql=None,
                 plain_http=None, soap=None):
        self.ftp = ftp
        self.amqp = amqp
        self.zmq = zmq
        self.jms_wmq = jms_wmq
        self.sql = sql
        self.plain_http = plain_http
        self.soap = soap

# ################################################################################################################################

class Response(object):
    """ A response from the service's invocation.
    """
    __slots__ = ('logger', 'result', 'result_details', '_payload', 'payload',
        '_content_type', 'content_type', 'content_type_changed', 'content_encoding',
        'headers', 'status_code', 'data_format', 'simple_io_config', 'outgoing_declared')

    def __init__(self, logger, result=ZATO_OK, result_details='', payload='',
            _content_type='text/plain', content_encoding=None, data_format=None, headers=None,
            status_code=OK, status_message='OK', simple_io_config={}):
        self.logger = logger
        self.result = ZATO_OK
        self.result_details = result_details
        self._payload = ''
        self._content_type = _content_type
        self.content_type_changed = False
        self.content_encoding = content_encoding
        self.data_format = data_format

        # Specific to HTTP/SOAP probably?
        self.headers = headers or Bunch()
        self.status_code = status_code

        self.simple_io_config = simple_io_config
        self.outgoing_declared = False

    def __len__(self):
        return len(self._payload)

    def _get_content_type(self):
        return self._content_type

    def _set_content_type(self, value):
        self._content_type = value
        self.content_type_changed = True

    content_type = property(_get_content_type, _set_content_type)

    def _get_payload(self):
        return self._payload

    def _set_payload(self, value):
        if isinstance(value, basestring):
            self._payload = value
        else:
            if not self.outgoing_declared:
                raise Exception("Can't set payload, there's no output_required nor output_optional declared")
            self._payload.set_payload_attrs(value)

    payload = property(_get_payload, _set_payload)

    def init(self, cid, io, data_format):
        self.data_format = data_format
        required_list = getattr(io, 'output_required', [])
        optional_list = getattr(io, 'output_optional', [])
        response_elem = getattr(io, 'response_elem', 'response')
        namespace = getattr(io, 'namespace', '')
        self.outgoing_declared = True if required_list or optional_list else False

        if required_list or optional_list:
            self._payload = SimpleIOPayload(cid, self.logger, data_format,
                required_list, optional_list, self.simple_io_config, response_elem, namespace)