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

# validate
from validate import is_boolean

# Bunch
from bunch import Bunch

# Zato
from zato.common import ZATO_NONE, ZATO_OK, zato_path
from zato.server.connection.amqp.outgoing import PublisherFacade
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.zmq_.outgoing import ZMQFacade

__all__ = ['Service', 'Request', 'Response', 'Outgoing']


# Need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
# TODO: Move it to zato.common.
ZATO_NO_DEFAULT_VALUE = "ZATO_NO_DEFAULT_VALUE"

def _get_params(payload, request_params, path_prefix='', default_value=ZATO_NO_DEFAULT_VALUE,
                force_type=None, force_type_params=[], use_text=True, boolean_prefixes=('is_', 'should_')):
    """ Gets all requested parameters from a message. Will raise an exception
    if any is missing.
    """
    params = {}
    for param in request_params:

        elem = zato_path(path_prefix + param, True).get_from(payload)

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

        # Should the value be of a specific type?
        if force_type and param in force_type_params:
            if force_type == bool:
                # TODO: Those should be stored in the app context
                if value.lower() in('0', 'false'):
                    value = False
                elif value.lower() in('1', 'true'):
                    value = True
                else:
                    msg = "Don't know how to convert param[{}], value[{}], into a bool".format(
                        param, value)
                    logger.error(msg)
                    raise ZatoException(msg)
            else:
                value = force_type(value)
                
        if any(param.startswith(prefix) for prefix in boolean_prefixes):
            value = is_boolean(value)
            
        if value != ZATO_NONE and (param == 'id' or param.endswith('_id')):
            value = int(value)

        params[param] = value

    return params

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
        self.soap = soap

class Response(object):
    """ A response from the service's invocation.
    """
    __slots__ = ('result', 'result_details', 'payload', 'content_type', 'content_encoding',
                 'headers', 'status_code')
    
    def __init__(self, result=ZATO_OK, result_details='', payload='', 
        content_type='text/plain', content_encoding=None, headers=None,  status_code=OK):
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
    
class ServiceInput(Bunch):
    pass
    
class Request(object):
    """ Wraps a service request and adds some useful meta-data.
    """
    __slots__ = ('payload', 'raw_request', 'input',)
    
    def __init__(self):
        self.payload = ''
        self.raw_request = ''
        self.input = ServiceInput()
        
    def init(self, flat_input):
        """ Initializes the object with an invocation-specific data.
        """
        path_prefix = getattr(flat_input, 'path_prefix', 'data.')
        required_list = getattr(flat_input, 'required', [])
        optional_list = getattr(flat_input, 'optional', [])
        
        if required_list:
            params = _get_params(self.payload, required_list, path_prefix)
            self.input.update(params)
            
        if optional_list:
            default_value = getattr(flat_input, 'default_value', None)
            params = _get_params(self.payload, optional_list, path_prefix, default_value)
            self.input.update(params)
    
class Service(object):
    """ A base class for all services deployed on Zato servers, no matter 
    the transport and protocol, be it plain HTTP, SOAP, WebSphere MQ or any other,
    regardless whether they're built-in or user-defined ones.
    """
    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.broker_client = None
        self.channel = None
        self.rid = None
        self.outgoing = None
        self.worker_store = None
        self.odb = None
        self.request = Request()
        self.response = Response()
        
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
        
        if hasattr(self, 'FlatInput'):
            self.request.init(self.FlatInput)
        
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
    def update(service, server, broker_client, worker_store, rid, payload,
               raw_request, transport=None, init=True):
        """ Takes a service instance and updates it with the current request's
        context data.
        """
        service.server = server
        service.broker_client = broker_client
        service.worker_store = worker_store
        service.rid = rid
        service.request.payload = payload
        service.request.raw_request = raw_request
        
        if init:
            service._init()
