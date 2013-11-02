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

# Arrow
import arrow

# Bunch
from bunch import Bunch, bunchify

# Django
from django.http import QueryDict

# lxml
from lxml import etree
from lxml.objectify import deannotate, Element, ElementMaker

# Paste
from paste.util.converters import asbool

# retools
from retools.lock import Lock, LockTimeout as RetoolsLockTimeout

# SQLAlchemy
from sqlalchemy.util import NamedTuple

# Zato
from zato.common import BROKER, CHANNEL, KVDB, PARAMS_PRIORITY, ParsingException, \
     path, SIMPLE_IO, URL_TYPE, ZatoException, ZATO_NONE, ZATO_OK
from zato.common.broker_message import SERVICE
from zato.common.util import uncamelify, make_repr, new_cid, payload_from_request, service_name_from_impl, TRACE1
from zato.server.connection import request_response, slow_response
from zato.server.connection.amqp.outgoing import PublisherFacade
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.zmq_.outgoing import ZMQFacade

__all__ = ['Service', 'Request', 'Response', 'Outgoing', 'SimpleIOPayload']

# Need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
# TODO: Move it to zato.common.
ZATO_NO_DEFAULT_VALUE = 'ZATO_NO_DEFAULT_VALUE'

logger = logging.getLogger(__name__)

# ##############################################################################

class ValueConverter(object):
    """ A class which knows how to convert values into the types defined in
    a service's SimpleIO config.
    """
    def convert(self, param, param_name, value, has_simple_io_config, date_time_format=None):
        try:
            if any(param_name.startswith(prefix) for prefix in self.bool_parameter_prefixes) or isinstance(param, Boolean):
                value = asbool(value or None) # value can be an empty string and asbool chokes on that
                
            if value and value is not None: # Can be a 0
                if isinstance(param, Boolean):
                    value = asbool(value)
                elif isinstance(param, CSV):
                    value = value.split(',')
                elif isinstance(param, Integer):
                    value = int(value)
                elif isinstance(param, Unicode):
                    value = unicode(value)
                elif isinstance(param, UTC):
                    value = value.replace('+00:00', '')
                else:
                    if value and value != ZATO_NONE and has_simple_io_config:
                        if any(param_name==elem for elem in self.int_parameters) or \
                           any(param_name.endswith(suffix) for suffix in self.int_parameter_suffixes):
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

# ##############################################################################
    
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
    """ Gets transformed into an int object.
    """

class Integer(ForceType):
    """ Gets transformed into an int object.
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
    
# ##############################################################################

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

# ##############################################################################

class HTTPRequestData(object):
    """ Data regarding an HTTP request.
    """
    def __init__(self):
        self.method = None
        self.GET = None
        self.POST = None
        
    def init(self, wsgi_environ):
        self.method = wsgi_environ.get('REQUEST_METHOD')
        
        # Note tht we always require UTF-8
        self.GET = wsgi_environ.get('zato.http.GET', {})
        self.POST = wsgi_environ.get('zato.http.POST', {})
        
    def __repr__(self):
        return make_repr(self)
        
# ##############################################################################

class Request(ValueConverter):
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
        if transport in(URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP):
            self.http.init(wsgi_environ)
        
        if is_sio:
            self.is_xml = data_format == SIMPLE_IO.FORMAT.XML
            self.data_format = data_format
            self.transport = transport
            self._wsgi_environ = wsgi_environ
            
            path_prefix = getattr(io, 'request_elem', 'request')
            required_list = getattr(io, 'input_required', [])
            optional_list = getattr(io, 'input_optional', [])
            default_value = getattr(io, 'default_value', None)
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
            
    def get_params(self, request_params, path_prefix='', default_value=ZATO_NO_DEFAULT_VALUE, use_text=True, is_required=True):
        """ Gets all requested parameters from a message. Will raise ParsingException if any is missing.
        """
        params = {}
        if not isinstance(self.payload, basestring):
            for param in request_params:
                
                if isinstance(param, ForceType):
                    param_name = param.name
                else:
                    param_name = param
    
                if self.is_xml:
                    try:
                        elem = path('{}.{}'.format(path_prefix, param_name), is_required).get_from(self.payload)
                    except ParsingException, e:
                        msg = 'Caught an exception while parsing, payload:[<![CDATA[{}]]>], e:[{}]'.format(
                            etree.tostring(self.payload), format_exc(e))
                        raise ParsingException(self.cid, msg)
                    
                    if elem is not None:
                        if use_text:
                            value = elem.text # We are interested in the text the elem contains ..
                        else:
                            return elem # .. or in the elem itself.
                    else:
                        value = default_value
                else:
                    value = self.payload.get(param_name)
                    
                # Use a default value if an element is empty and we're allowed to
                # substitute its (empty) value with the default one.
                if default_value != ZATO_NO_DEFAULT_VALUE and value is None:
                    value = default_value
                else:
                    if value is not None:
                        value = unicode(value)

                try:
                    if not isinstance(param, AsIs):
                        params[param_name] = self.convert(param, param_name, value, self.has_simple_io_config)
                    else:
                        params[param_name] = value
                except Exception, e:
                    msg = 'Caught an exception, param:[{}], param_name:[{}], value:[{}], self.has_simple_io_config:[{}], e:[{}]'.format(
                        param, param_name, value, self.has_simple_io_config, format_exc(e))
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
        request.logger = logging.getLogger(self.logger.getName())
        
        for name in Request.__slots__:
            if name == 'logger':
                continue
            setattr(request, name, deepcopy(getattr(self, name)))
            
    
    def bunchified(self):
        """ Returns a bunchified (converted into bunch.Bunch) version of self.raw_request,
        deep copied if it's a dict (or a subclass). Note that it makes to use this method
        only with dicts or JSON input.
        """
        # We have a dict
        if isinstance(self.raw_request, dict):
            return bunchify(deepcopy(self.raw_request))
        
        # Must be a JSON input, raises exception when attempting to load it if it's not
        return bunchify(loads(self.raw_request))

# ##############################################################################
        
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

# ##############################################################################
            
class SimpleIOPayload(ValueConverter):
    """ Produces the actual response - XML or JSON - out of the user-provided
    SimpleIO abstract data. All of the attributes are prefixed with zato_ so that
    they don't conflict with user-provided data.
    """
    def __init__(self, zato_cid, logger, data_format, required_list, optional_list, simple_io_config, response_elem, namespace):
        self.zato_cid = zato_cid
        self.zato_logger = logger
        self.zato_is_xml = data_format == SIMPLE_IO.FORMAT.XML
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
            return self.convert(name, lookup_name, elem_value, True)

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

# ##############################################################################

class TimeUtil(object):
    """ A thin layer around Arrow's date/time handling library customized for our needs.
    Default format is always taken from ISO 8601 (so it's sorted lexicographically)
    and default timezone is always UTC.
    """
    def __init__(self, kvdb):
        self.kvdb = kvdb
        
    def get_format_from_kvdb(self, format):
        """ Returns format stored under a key pointed to by 'format' or raises 
        ValueError if the key is missing/has no value.
        """
        key = 'zato:date-format:{}'.format(format[5:])
        format = self.kvdb.conn.get(key)
        if not format:
            msg = 'Key [{}] does not exist'.format(key)
            logger.error(msg)
            raise ValueError(msg)
        
        return format
        
    def utcnow(self, format='YYYY-MM-DD HH:mm:ss'):
        """ Returns now in UTC formatted as given in 'format'.
        """
        return arrow.utcnow().format(format)
    
    def today(self, format='YYYY-MM-DD', tz='UTC'):
        """ Returns current day in a given timezone.
        """
        now = arrow.utcnow()
        
        if tz != 'UTC':
            now = now.to(tz)
            
        if format.startswith('zato:'):
            format = self.get_format_from_kvdb(format)
            
        return now.format(format)
    
    def reformat(self, value, from_, to):
        """ Reformats value from one datetime format to another, for instance
        from 23-03-2013 to 03/23/13 (MM-DD-YYYY to DD/MM/YY).
        """
        if from_.startswith('zato:'):
            from_ = self.get_format_from_kvdb(from_)
            
        if to.startswith('zato:'):
            to = self.get_format_from_kvdb(to)
            
        try:
            return arrow.get(value, from_).format(to)
        except Exception, e:
            logger.error('Could not reformat value:[%s] from_:[%s] to:[%s]',
                value, from_, to)
            raise
        
# ##############################################################################

class Service(object):
    """ A base class for all services deployed on Zato servers, no matter 
    the transport and protocol, be it plain HTTP, SOAP, WebSphere MQ or any other,
    regardless whether they're built-in or user-defined ones.
    """
    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = logging.getLogger(self.get_name())
        self.server = None
        self.broker_client = None
        self.channel = None
        self.cid = None
        self.outgoing = None
        self.worker_store = None
        self.odb = None
        self.data_format = None
        self.transport = None
        self.wsgi_environ = None
        self.job_type = None
        self.delivery_store = None
        self.environ = {}
        self.request = Request(self.logger)
        self.response = Response(self.logger)
        self.invocation_time = None # When was the service invoked
        self.handle_return_time = None # When did its 'handle' method finished processing the request
        self.processing_time_raw = None # A timedelta object with the processing time up to microseconds
        self.processing_time = None # Processing time in milliseconds
        self.usage = 0 # How many times the service has been invoked
        self.slow_threshold = maxint # After how many ms to consider the response came too late
        self.name = self.__class__.get_name()
        self.impl_name = self.__class__.get_impl_name()
        self.time = TimeUtil(None)
        
    @classmethod
    def get_name(class_):
        """ Returns a service's name, settings its .name attribute along. This will
        be called once while the service is being deployed.
        """
        if not hasattr(class_, '__name'):
            name = getattr(class_, 'name', None)
            if not name:
                name = service_name_from_impl(class_.get_impl_name())
                name = class_.convert_impl_name(name)
                    
            class_.__name = name
            
        return class_.__name

    @classmethod
    def get_impl_name(class_):
        if not hasattr(class_, '__impl_name'):
            class_.__impl_name = '{}.{}'.format(class_.__module__, class_.__name__)
        return class_.__impl_name
    
    @staticmethod
    def convert_impl_name(name):
        # TODO: Move the replace functionality over to uncamelify, possibly modifying its regexp
        split = uncamelify(name).split('.')
        
        path, class_name = split[:-1], split[-1]
        path = [elem.replace('_', '-') for elem in path]
        
        class_name = class_name[1:] if class_name.startswith('-') else class_name
        class_name = class_name.replace('.-', '.').replace('_-', '_')
        
        return '{}.{}'.format('.'.join(path), class_name)
        
    def _init(self):
        """ Actually initializes the service.
        """
        self.odb = self.worker_store.odb
        self.kvdb = self.worker_store.kvdb
        self.time.kvdb = self.kvdb
        
        self.slow_threshold = self.server.service_store.services[self.impl_name]['slow_threshold']
        
        out_amqp = PublisherFacade(self.broker_client, self.server.delivery_store)
        out_jms_wmq = WMQFacade(self.broker_client, self.server.delivery_store)
        out_zmq = ZMQFacade(self.broker_client, self.server.delivery_store)
        out_sql = self.worker_store.sql_pool_store

        out_ftp, out_plain_http, out_soap = self.worker_store.worker_config.outgoing_connections()
        self.outgoing = Outgoing(out_ftp, out_amqp, out_zmq, out_jms_wmq, out_sql, out_plain_http, out_soap)
        
        is_sio = hasattr(self, 'SimpleIO')
        
        self.request.init(is_sio, self.cid, getattr(self, 'SimpleIO', None),
            self.data_format, self.transport, self.wsgi_environ)
        
        if is_sio:
            self.response.init(self.cid, self.SimpleIO, self.data_format)
            
    def set_response_data(self, service, **kwargs):
        response = service.response.payload
        if not isinstance(response, basestring):
            response = response.getvalue(serialize=kwargs['serialize'])
            if kwargs['as_bunch']:
                response = bunchify(response)
            service.response.payload = response
            
        return response
            
    def update_handle(self, set_response_func, service, raw_request, channel, data_format, 
            transport, server, broker_client, worker_store, cid, simple_io_config, *args, **kwargs):

        payload = payload_from_request(cid, raw_request, data_format, transport)
        
        service.update(service, channel, server, broker_client, 
            worker_store, cid, payload, raw_request, transport, 
            simple_io_config, data_format, kwargs.get('wsgi_environ', {}), 
            job_type=kwargs.get('job_type'),
            channel_params=kwargs.get('channel_params', {}),
            merge_channel_params=kwargs.get('merge_channel_params', True),
            params_priority=kwargs.get('params_priority', PARAMS_PRIORITY.DEFAULT))
            
        service.pre_handle()
        service.call_hooks('before')
        service.handle()
        service.call_hooks('after')
        service.post_handle()
        service.call_hooks('finalize')
        
        return set_response_func(service, data_format=data_format, transport=transport, **kwargs)
            
    def invoke_by_impl_name(self, impl_name, payload='', channel=CHANNEL.INVOKE, data_format=None,
            transport=None, serialize=False, as_bunch=False):
        """ Invokes a service synchronously by its implementation name (full dotted Python name).
        """
            
        if self.impl_name == impl_name:
            msg = 'A service cannot invoke itself, name:[{}]'.format(self.name)
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)
            
        service = self.server.service_store.new_instance(impl_name)
        return self.update_handle(self.set_response_data, service, payload, channel, 
            data_format, transport, self.server, self.broker_client, self.worker_store,
            self.cid, self.request.simple_io_config, serialize=serialize, as_bunch=as_bunch)
        
    def invoke(self, name, *args, **kwargs):
        """ Invokes a service synchronously by its name.
        """
        return self.invoke_by_impl_name(self.server.service_store.name_to_impl_name[name], *args, **kwargs)
        
    def invoke_by_id(self, service_id, *args, **kwargs):
        """ Invokes a service synchronously by its ID.
        """
        return self.invoke_by_impl_name(self.server.service_store.id_to_impl_name[service_id], *args, **kwargs)
        
    def invoke_async(self, name, payload='', channel=CHANNEL.INVOKE_ASYNC, data_format=None, 
            transport=None, expiration=BROKER.DEFAULT_EXPIRATION, to_json_string=False):
        """ Invokes a service asynchronously by its name.
        """
        if to_json_string:
            payload = dumps(payload)

        cid = new_cid()

        msg = {}
        msg['action'] = SERVICE.PUBLISH
        msg['service'] = name
        msg['payload'] = payload
        msg['cid'] = cid
        msg['channel'] = channel
        msg['data_format'] = data_format
        msg['transport'] = transport

        self.broker_client.invoke_async(msg, expiration=expiration)

        return cid

    def deliver(self, def_name, payload, task_id=None, *args, **kwargs):
        """ Uses guaranteed delivery to send payload using a delivery definition known by def_name.
        *args and **kwargs will be passed directly as-is to the target behind the def_name.
        """
        task_id = task_id or new_cid()
        self.delivery_store.deliver(
            self.server.cluster_id, def_name, payload, task_id, self.invoke, 
            kwargs.pop('is_resubmit', False), 
            kwargs.pop('is_auto', False), 
            *args, **kwargs)
        
        return task_id
            
    def pre_handle(self):
        """ An internal method run just before the service sets to process the payload.
        Used for incrementing the service's usage count and storing the service invocation time.
        """
        self.usage = self.kvdb.conn.incr('{}{}'.format(KVDB.SERVICE_USAGE, self.name))
        self.invocation_time = datetime.utcnow()
        
    def post_handle(self):
        """ An internal method executed after the service has completed and has
        a response ready to return. Updates its statistics and, optionally, stores
        a sample request/response pair.
        """
        
        #
        # Statistics
        #
        
        self.handle_return_time = datetime.utcnow()
        self.processing_time_raw = self.handle_return_time - self.invocation_time
        
        proc_time = self.processing_time_raw.total_seconds() * 1000.0
        proc_time = proc_time if proc_time > 1 else 0
        
        self.processing_time = int(round(proc_time))

        self.kvdb.conn.hset('{}{}'.format(KVDB.SERVICE_TIME_BASIC, self.name), 'last', self.processing_time)
        self.kvdb.conn.rpush('{}{}'.format(KVDB.SERVICE_TIME_RAW, self.name), self.processing_time)

        key = '{}{}:{}'.format(KVDB.SERVICE_TIME_RAW_BY_MINUTE, 
            self.name, self.handle_return_time.strftime('%Y:%m:%d:%H:%M'))
        self.kvdb.conn.rpush(key, self.processing_time)
        
        # .. we'll have 5 minutes (5 * 60 seconds = 300 seconds) 
        # to aggregate processing times for a given minute and then it will expire
        
        # Note that we need Redis 2.1.3+ otherwise the key has just been overwritten
        self.kvdb.conn.expire(key, 300)
        
        # 
        # Sample requests/responses
        #
        key, freq = request_response.should_store(self.kvdb, self.usage, self.name)
        if freq:

            # TODO: Don't parse it here and a moment later below
            resp = (self.response.payload.getvalue() if hasattr(self.response.payload, 'getvalue') else self.response.payload) or ''            
            
            data = {
                'cid': self.cid,
                'req_ts': self.invocation_time.isoformat(),
                'resp_ts': self.handle_return_time.isoformat(),
                'req': self.request.raw_request or '',
                'resp':resp,
            }
            request_response.store(self.kvdb, key, self.usage, freq, **data)
            
        #
        # Slow responses
        #
        if self.processing_time > self.slow_threshold:

            # TODO: Don't parse it here and a moment earlier above
            resp = (self.response.payload.getvalue() if hasattr(self.response.payload, 'getvalue') else self.response.payload) or ''            
            
            data = {
                'cid': self.cid,
                'proc_time': self.processing_time,
                'slow_threshold': self.slow_threshold,
                'req_ts': self.invocation_time.isoformat(),
                'resp_ts': self.handle_return_time.isoformat(),
                'req': self.request.raw_request or '',
                'resp': resp,
            }
            slow_response.store(self.kvdb, self.name, **data)
            
    def translate(self, *args, **kwargs):
        raise NotImplementedError('An initializer should override this method')
        
    def handle(self):
        """ The only method Zato services need to implement in order to process
        incoming requests.
        """
        raise NotImplementedError('Should be overridden by subclasses')
    
    def lock(self, name=None, expires=20, timeout=0, backend=None):
        """ Creates a Redis-backed distributed lock.
        
        name - defaults to self.name effectively making access to this service serialized
        expires - defaults to 20 seconds and is the max time the lock will be held
        timeout - how long (in seconds) we will wait to acquire the lock before giving up and raising LockTimeout
        backend - a Redis connection object, defaults to self.kvdb.conn
        """
        name = '{}{}'.format(KVDB.LOCK_SERVICE_PREFIX, name or self.name)
        backend = backend or self.kvdb.conn
        return Lock(name, expires, timeout, backend)
    
# ##############################################################################

    def call_job_hooks(self, prefix):
        if self.channel == CHANNEL.SCHEDULER and prefix != 'finalize':
            try:
                getattr(self, '{}_job'.format(prefix))()
            except Exception, e:
                self.logger.error("Can't run {}_job, e:[{}]".format(prefix, format_exc(e)))
            else:
                try:
                    func_name = '{}_{}_job'.format(prefix, self.job_type)
                    func = getattr(self, func_name)
                    func()
                except Exception, e:
                    self.logger.error("Can't run {}, e:[{}]".format(func_name, format_exc(e)))

    def call_handle(self, prefix):
        try:
            getattr(self, '{}_handle'.format(prefix))()
        except Exception, e:
            self.logger.error("Can't run {}_handle, e:[{}]".format(prefix, format_exc(e)))

    def call_hooks(self, prefix):
        if prefix == 'before':
            self.call_job_hooks(prefix)
            self.call_handle(prefix)
        else:
            self.call_handle(prefix)
            self.call_job_hooks(prefix)
            
    @classmethod
    def before_add_to_store(cls, logger):
        """ Invoked right before the class is added to the service store.
        """
        return True

    def before_job(self):
        """ Invoked  if the service has been defined as a job's invocation target,
        regardless of the job's type.
        """

    def before_one_time_job(self):
        """ Invoked if the service has been defined as a one-time job's
        invocation target.
        """

    def before_interval_based_job(self):
        """ Invoked if the service has been defined as an interval-based job's
        invocation target.
        """
        
    def before_cron_style_job(self):
        """ Invoked if the service has been defined as a cron-style job's
        invocation target.
        """
        
    def before_handle(self, *args, **kwargs):
        """ Invoked just before the actual service receives the request data.
        """

    def after_job(self):
        """ Invoked  if the service has been defined as a job's invocation target,
        regardless of the job's type.
        """

    def after_one_time_job(self):
        """ Invoked if the service has been defined as a one-time job's
        invocation target.
        """

    def after_interval_based_job(self):
        """ Invoked if the service has been defined as an interval-based job's
        invocation target.
        """
        
    def after_cron_style_job(self):
        """ Invoked if the service has been defined as a cron-style job's
        invocation target.
        """
        
    def after_handle(self):
        """ Invoked right after the actual service has been invoked, regardless
        of whether the service raised an exception or not.
        """
        
    def finalize_handle(self):
        """ Offers the last chance to influence the service's operations.
        """

    @staticmethod
    def after_add_to_store(logger):
        """ Invoked right after the class has been added to the service store.
        """
        
# ##############################################################################

    def _log_input_output(self, user_msg, level, suppress_keys, is_response):
    
        suppress_keys = suppress_keys or []
        suppressed_msg = '(suppressed)'
        container = 'response' if is_response else 'request'
        payload_key = '{}.payload'.format(container)
        user_msg = '{} '.format(user_msg) if user_msg else user_msg
        
        msg = {}
        if payload_key not in suppress_keys:
            msg[payload_key] = getattr(self, container).payload
        else:
            msg[payload_key] = suppressed_msg
        
        attrs = ('channel', 'cid', 'data_format', 'environ', 'impl_name', 
             'invocation_time', 'job_type', 'name', 'slow_threshold', 'usage', 'wsgi_environ')
             
        if is_response:
            attrs += ('handle_return_time', 'processing_time', 'processing_time_raw',
                'zato.http.response.headers')
            
        for attr in attrs:
            if attr not in suppress_keys:
                msg[attr] = getattr(self, attr, '(None)')
            else:
                msg[attr] = suppressed_msg

        self.logger.log(level, '{}{}'.format(user_msg, msg))
        
        return msg
        
    def log_input(self, user_msg='', level=logging.INFO, suppress_keys=None):
        return self._log_input_output(user_msg, level, suppress_keys, False)
        
    def log_output(self, user_msg='', level=logging.INFO, suppress_keys=('wsgi_environ',)):
        return self._log_input_output(user_msg, level, suppress_keys, True)
        
# ##############################################################################
        
    @staticmethod
    def update(service, channel, server, broker_client, worker_store, cid, payload,
               raw_request, transport=None, simple_io_config=None, data_format=None,
               wsgi_environ=None, job_type=None, channel_params=None,
               merge_channel_params=True, params_priority=None, init=True):
        """ Takes a service instance and updates it with the current request's
        context data.
        """
        service.channel = channel
        service.server = server
        service.broker_client = broker_client
        service.worker_store = worker_store
        service.cid = cid
        service.request.payload = payload
        service.request.raw_request = raw_request
        service.transport = transport
        service.request.simple_io_config = simple_io_config
        service.response.simple_io_config = simple_io_config
        service.data_format = data_format
        service.wsgi_environ = wsgi_environ
        service.job_type = job_type
        service.translate = server.kvdb.translate
        service.delivery_store = server.delivery_store
        
        if channel_params:
            service.request.channel_params.update(channel_params)
            
        service.request.merge_channel_params = merge_channel_params
        service.request.params_priority = params_priority
        
        if init:
            service._init()

# ##############################################################################
