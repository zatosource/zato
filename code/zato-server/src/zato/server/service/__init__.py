# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from httplib import OK
from itertools import chain
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.util import NamedTuple

# lxml
from lxml import etree
from lxml.objectify import Element

# Paste
from paste.util.converters import asbool

# Bunch
from bunch import Bunch

# Zato
from zato.common import ParsingException, SIMPLE_IO, ZatoException, ZATO_NONE, ZATO_OK, zato_path
from zato.common.util import TRACE1
from zato.server.connection.amqp.outgoing import PublisherFacade
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.zmq_.outgoing import ZMQFacade

__all__ = ['Service', 'Request', 'Response', 'Outgoing']


# Need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
# TODO: Move it to zato.common.
ZATO_NO_DEFAULT_VALUE = "ZATO_NO_DEFAULT_VALUE"

class ForceType(object):
    def __init__(self, name):
        self.name = name

class Boolean(ForceType):
    pass

class Integer(ForceType):
    pass

class Outgoing(object):
    """ A container for various outgoing connections a service can access. This
    in fact is a thin wrapper around data fetched from the service's self.worker_store.
    """
    __slots__ = ('ftp', 'amqp', 'zmq', 'jms_wmq', 'sql', 'plain_http', 'soap', 's3')
    def __init__(self, ftp=None, amqp=None, zmq=None, jms_wmq=None, sql=None, 
                 plain_http=None, soap=None, s3=None):
        self.ftp = ftp
        self.amqp = amqp
        self.zmq = zmq
        self.jms_wmq = jms_wmq
        self.sql = sql
        self.plain_http = plain_http
        self.soap = soap
        
class SimpleIOPayload(object):
    """ Produces the actual response - XML or JSON - out of the user-provided
    SimpleIO abstract data.
    """
    def __init__(self, cid, logger, format, required_list, optional_list):
        self.cid = None
        self.logger = logger
        self.is_xml = format == SIMPLE_IO.FORMAT.XML
        self.output = []
        self.required = [(True, name) for name in required_list]
        self.optional = [(False, name) for name in optional_list]
        
    def append(self, item):
        self.output.append(item)
        
    def _getvalue(self, name, item, is_sa_namedtuple):
        """ Returns an element's value if any has been provided while taking
        into account the differences between dictionaries and other formats.
        """
        if is_sa_namedtuple:
            return getattr(item, name, ZATO_NONE)
        else:
            return item.get(required, ZATO_NONE)
            
    def _missing_value_log_msg(self, name, item, is_sa_namedtuple, is_required):
        """ Returns a log message indicating that an element was missing.
        """
        if is_sa_namedtuple:
            msg_item = (item.keys(), item)
        else:
            msg_item = item
        return '{} elem:[{}] not found in item:[{}]'.format(
            'Expected' if is_required else 'Optional', name, msg_item)
        
    def getvalue(self):
        """ Gets the actual payload's value converted to a string representing
        either XML or JSON.
        """
        if self.output:
            if self.is_xml:
                value = Element('item_list')
            else:
                value = {}
                
            # All elements must be of the same type so it's OK to do it
            is_sa_namedtuple = isinstance(self.output[0], NamedTuple) 
            
            for item in self.output:
                out_item = Element('item')
                for is_required, name in chain(self.required, self.optional):
                    elem_value = self._getvalue(name, item, is_sa_namedtuple)
                    if elem_value == ZATO_NONE:
                        msg = self._missing_value_log_msg(name, item, is_sa_namedtuple, is_required)
                        if is_required:
                            self.logger.debug(msg)
                            raise ZatoException(self.cid, msg)
                        else:
                            if self.logger.isEnabledFor(TRACE1):
                                self.logger.log(TRACE1, msg)
                    else:
                        if self.is_xml:
                            setattr(out_item, name, elem_value)
                value.append(out_item)
                
        return etree.tostring(value)

class Response(object):
    """ A response from the service's invocation.
    """
    __slots__ = ('logger', 'result', 'result_details', 'payload', 'content_type', 'content_encoding',
                 'headers', 'status_code')
    
    def __init__(self, logger, result=ZATO_OK, result_details='', payload='', 
        content_type='text/plain', content_encoding=None, headers=None,  status_code=OK):
        self.logger = logger
        self.result = ZATO_OK
        self.result_details = result_details
        self.payload = payload
        self.content_type = content_type
        self.content_encoding = content_encoding
        
        # Specific to HTTP/SOAP probably?
        self.headers = headers or Bunch()
        self.status_code = status_code
        
    def __len__(self):
        return len(self.payload)
    
    def init(self, cid, io):
        required_list = getattr(io, 'output_required', [])
        optional_list = getattr(io, 'output_optional', [])
        
        if required_list or optional_list:
            self.payload = SimpleIOPayload(cid, self.logger, SIMPLE_IO.FORMAT.XML, 
                    required_list, optional_list)
    
class ServiceInput(Bunch):
    pass
    
class Request(object):
    """ Wraps a service request and adds some useful meta-data.
    """
    __slots__ = ('logger', 'payload', 'raw_request', 'input', 'cid', 'int_parameters',
                 'int_parameter_suffixes', 'bool_parameter_prefixes')
    
    def __init__(self, logger):
        self.logger = logger
        self.payload = ''
        self.raw_request = ''
        self.input = ServiceInput()
        self.cid = None
        self.int_parameters = []
        self.int_parameter_suffixes = []
        self.bool_parameter_prefixes = []
        
    def init(self, cid, io):
        """ Initializes the object with an invocation-specific data.
        """
        path_prefix = getattr(io, 'path_prefix', 'data.')
        required_list = getattr(io, 'input_required', [])
        optional_list = getattr(io, 'input_optional', [])
        use_text = getattr(io, 'use_text', True)
        
        if required_list:
            params = self.get_params(required_list, path_prefix, use_text=use_text)
            self.input.update(params)
            
        if optional_list:
            default_value = getattr(io, 'default_value', None)
            params = self.get_params(optional_list, path_prefix, default_value, use_text)
            self.input.update(params)
            
    def get_params(self, request_params, path_prefix='', default_value=ZATO_NO_DEFAULT_VALUE, use_text=True):
        """ Gets all requested parameters from a message. Will raise ParsingException if any is missing.
        """
        params = {}
        for param in request_params:
            
            if isinstance(param, ForceType):
                param_name = param.name
            else:
                param_name = param
    
            try:
                elem = zato_path(path_prefix + param_name, True).get_from(self.payload)
            except ParsingException, e:
                msg = 'Caught an exception while parsing, payload:[<![CDATA[{}]]>], e:[{}]'.format(
                    etree.tostring(self.payload), format_exc(e))
                raise ParsingException(self.cid, msg)
    
            if use_text:
                value = elem.text # We are interested in the text the elem contains ..
            else:
                return elem # .. or in the elem itself.
    
            # Use a default value if an element is empty and we're allowed to
            # substitute its (empty) value with the default one.
            if default_value != ZATO_NO_DEFAULT_VALUE and not value:
                value = default_value
            else:
                if value is not None:
                    value = unicode(value)
    
            if any(param_name.startswith(prefix) for prefix in self.bool_parameter_prefixes):
                value = asbool(value)
                
            if value != ZATO_NONE:
                if any(param_name==elem for elem in self.int_parameters) or \
                   any(param_name.endswith(suffix) for suffix in self.int_parameter_suffixes):
                    value = int(value)
                
            if isinstance(param, Boolean):
                value = asbool(value)
            elif isinstance(param, Integer):
                value = int(value)
                
            params[param_name] = value
    
        return params
    
class Service(object):
    """ A base class for all services deployed on Zato servers, no matter 
    the transport and protocol, be it plain HTTP, SOAP, WebSphere MQ or any other,
    regardless whether they're built-in or user-defined ones.
    """
    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.broker_client = None
        self.channel = None
        self.cid = None
        self.outgoing = None
        self.worker_store = None
        self.odb = None
        self.request = Request(self.logger)
        self.response = Response(self.logger)
        
    def _init(self):
        """ Actually initializes the service.
        """
        self.odb = self.worker_store.odb
        out_amqp = PublisherFacade(self.broker_client)
        out_jms_wmq = WMQFacade(self.broker_client)
        out_zmq = ZMQFacade(self.broker_client)
        out_sql = self.worker_store.sql_pool_store

        out_ftp, out_plain_http, out_soap, out_s3 = self.worker_store.worker_config.outgoing_connections()
        self.outgoing = Outgoing(out_ftp, out_amqp, out_zmq, out_jms_wmq, out_sql, out_plain_http, out_soap, out_s3)
        
        if hasattr(self, 'SimpleIO'):
            self.request.init(self.cid, self.SimpleIO)
            self.response.init(self.cid, self.SimpleIO)
        
    def handle(self, *args, **kwargs):
        """ The only method Zato services need to implement in order to process
        incoming requests.
        """
        raise NotImplementedError('Should be overridden by subclasses')

    def before_handle(self, *args, **kwargs):
        """ Invoked just before the actual service receives the request data.
        """

    def before_job(self, *args, **kwargs):
        """ Invoked by the scheduler, before calling 'handle', if the service
        has been defined as a job's invocation target, regardless of a job's type.
        """

    def before_one_time_job(self, *args, **kwargs):
        """ Invoked by the scheduler, before calling 'handle', if the service
        has been defined as a one-time job's invocation target.
        """

    def before_interval_based_job(self, *args, **kwargs):
        """ Invoked by the scheduler, before calling 'handle', if the service
        has been defined as an interval-based job's invocation target.
        """

    @staticmethod
    def before_add_to_store(*args, **kwargs):
        """ XXX: Docs
        """

    @staticmethod
    def before_remove_from_store(*args, **kwargs):
        """ XXX: Docs
        """

    def after_handle(self, *args, **kwargs):
        """ Invoked right after the actual service has been invoked, regardless
        of whether the service raised an exception or not.
        """

    def after_job(self, *args, **kwargs):
        """ Invoked by the scheduler, after calling 'handle', if the service
        has been defined as a job's invocation target, regardless of a job's type.
        """

    def after_one_time_job(self, *args, **kwargs):
        """ Invoked by the scheduler, after calling 'handle', if the service
        has been defined as a one-time job's invocation target.
        """

    def after_interval_based_job(self, *args, **kwargs):
        """ Invoked by the scheduler, after calling 'handle', if the service
        has been defined as an interval-based job's invocation target.
        """

    @staticmethod
    def after_add_to_store(*args, **kwargs):
        """ XXX: Docs
        """

    @staticmethod
    def after_remove_from_store(*args, **kwargs):
        """ XXX: Docs
        """
        
    @staticmethod
    def update(service, server, broker_client, worker_store, cid, payload,
               raw_request, transport=None, init=True):
        """ Takes a service instance and updates it with the current request's
        context data.
        """
        service.server = server
        service.broker_client = broker_client
        service.worker_store = worker_store
        service.cid = cid
        service.request.payload = payload
        service.request.raw_request = raw_request
        
        if init:
            service._init()
