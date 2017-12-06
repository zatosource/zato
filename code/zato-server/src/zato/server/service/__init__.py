# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from httplib import BAD_REQUEST, METHOD_NOT_ALLOWED
from sys import maxint
from traceback import format_exc

# anyjson
from anyjson import dumps

# Bunch
from bunch import bunchify

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# gevent
from gevent import Timeout, spawn

# Zato
from zato.bunch import Bunch
from zato.common import BROKER, CHANNEL, DATA_FORMAT, Inactive, KVDB, PARAMS_PRIORITY, ZatoException
from zato.common.broker_message import SERVICE
from zato.common.exception import Reportable
from zato.common.nav import DictNav, ListNav
from zato.common.util import get_response_value, make_repr, new_cid, payload_from_request, service_name_from_impl, uncamelify
from zato.server.connection import slow_response
from zato.server.connection.email import EMailAPI
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.search import SearchAPI
from zato.server.connection.sms import SMSAPI
from zato.server.connection.zmq_.outgoing import ZMQFacade
from zato.server.message import MessageFacade
from zato.server.pattern.fanout import FanOut
from zato.server.pattern.invoke_retry import InvokeRetry
from zato.server.pattern.parallel import ParallelExec
from zato.server.service.reqresp import AMQPRequestData, Cloud, Outgoing, Request, Response

# Not used here in this module but it's convenient for callers to be able to import everything from a single namespace
from zato.server.service.reqresp.sio import AsIs, CSV, Boolean, Dict, Float, ForceType, Integer, List, ListOfDicts, Nested, \
     Opaque, Unicode, UTC

# Again, not used here but imported for convenience
from zato.server.service.reqresp import fixed_width

# So pyflakes doesn't complain about names being imported but not used
AsIs = AsIs
CSV = CSV
Boolean = Boolean
Dict = Dict
Float = Float
ForceType = ForceType
Integer = Integer
List = List
ListOfDicts = ListOfDicts
Nested = Nested
Opaque = Opaque
Unicode = Unicode
UTC = UTC
fixed_width = fixed_width

logger = logging.getLogger(__name__)

NOT_GIVEN = 'ZATO_NOT_GIVEN'

# Back compat
Bool = Boolean
Int = Integer

# ################################################################################################################################

# Hook methods whose func.im_func.func_defaults contains this argument will be assumed to have not been overridden by users
# and ServiceStore will be allowed to override them with None so that they will not be called in Service.update_handle
# which significantly improves performance (~30%).
zato_no_op_marker = 'zato_no_op_marker'

before_job_hooks = ('before_job', 'before_one_time_job', 'before_interval_based_job', 'before_cron_style_job')
after_job_hooks = ('after_job', 'after_one_time_job', 'after_interval_based_job', 'after_cron_style_job')
before_handle_hooks = ('before_handle',)
after_handle_hooks = ('after_handle', 'finalize_handle')

# The almost identical methods below are defined separately because they are used in critical paths
# where every if counts.

def call_hook_no_service(hook):
    try:
        hook()
    except Exception, e:
        logger.error('Can\'t run hook `%s`, e:`%s`', hook, format_exc(e))

def call_hook_with_service(hook, service):
    try:
        hook(service)
    except Exception, e:
        logger.error('Can\'t run hook `%s`, e:`%s`', hook, format_exc(e))

# ################################################################################################################################

class ChannelInfo(object):
    """ Conveys information abouts the channel that a service is invoked through.
    Available in services as self.channel or self.chan.
    """
    __slots__ = ('id', 'name', 'type', 'data_format', 'is_internal', 'match_target', 'impl', 'security', 'sec')

    def __init__(self, id, name, type, data_format, is_internal, match_target, security, impl):
        self.id = id
        self.name = name
        self.type = type
        self.data_format = data_format
        self.is_internal = is_internal
        self.match_target = match_target
        self.impl = impl
        self.security = self.sec = security

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class ChannelSecurityInfo(object):
    """ Contains information about a security definition assigned to a channel, if any.
    Available in services as:

    * self.channel.security
    * self.channel.sec

    * self.chan.security
    * self.chan.sec
    """
    __slots__ = ('id', 'name', 'type', 'username', 'impl')

    def __init__(self, id, name, type, username, impl):
        self.id = id
        self.name = name
        self.type = type
        self.username = username
        self.impl = impl

# ################################################################################################################################

class AMQPFacade(object):
    """ Introduced solely to let service access outgoing connections through self.out.amqp.invoke/_async
    rather than self.out.amqp_invoke/_async. The .send method is kept for pre-3.0 backward-compatibility.
    """
    __slots__ = ('send', 'invoke', 'invoke_async')

# ################################################################################################################################

class PatternsFacade(object):
    """ The API through which services make use of integration patterns.
    """
    __slots__ = ('invoke_retry', 'fanout', 'parallel')

    def __init__(self, invoking_service):
        self.invoke_retry = InvokeRetry(invoking_service)
        self.fanout = FanOut(invoking_service)
        self.parallel = ParallelExec(invoking_service)

# ################################################################################################################################

class Service(object):
    """ A base class for all services deployed on Zato servers, no matter
    the transport and protocol, be it plain HTTP, SOAP, WebSphere MQ or any other,
    regardless whether they're built-in or user-defined ones.
    """
    _filter_by = None
    _enforce_service_invokes = None
    invokes = []
    http_method_handlers = {}

    # Class-wide attributes shared by all services thus created here instead of assigning to self.
    cloud = Cloud()
    odb = None
    kvdb = None
    pubsub = None
    cassandra_conn = None
    cassandra_query = None
    email = None
    search = None
    amqp = AMQPFacade()

    _worker_store = None
    _worker_config = None
    _msg_ns_store = None
    _ns_store = None
    _json_pointer_store = None
    _xpath_store = None
    _out_ftp = None
    _out_plain_http = None

    _req_resp_freq = 0
    _has_before_job_hooks = None
    _has_after_job_hooks = None
    _before_job_hooks = []
    _after_job_hooks = []

    # For invoking other servers directly
    servers = None

    def __init__(self, _get_logger=logging.getLogger, _Bunch=Bunch, _Request=Request, _Response=Response,
            _DictNav=DictNav, _ListNav=ListNav, _Outgoing=Outgoing, _WMQFacade=WMQFacade, _ZMQFacade=ZMQFacade,
            *ignored_args, **ignored_kwargs):
        self.name = self.__class__.__service_name # Will be set through .get_name by Service Store
        self.impl_name = self.__class__.__service_impl_name # Ditto
        self.logger = _get_logger(self.name)
        self.server = None
        self.broker_client = None
        self.channel = None
        self.cid = None
        self.in_reply_to = None
        self.data_format = None
        self.transport = None
        self.wsgi_environ = None
        self.job_type = None
        self.environ = _Bunch()
        self.request = _Request(self.logger)
        self.response = _Response(self.logger)
        self.invocation_time = None # When was the service invoked
        self.handle_return_time = None # When did its 'handle' method finished processing the request
        self.processing_time_raw = None # A timedelta object with the processing time up to microseconds
        self.processing_time = None # Processing time in milliseconds
        self.usage = 0 # How many times the service has been invoked
        self.slow_threshold = maxint # After how many ms to consider the response came too late
        self.msg = None
        self.time = None
        self.patterns = None
        self.user_config = None
        self.dictnav = _DictNav
        self.listnav = _ListNav
        self.has_validate_input = False
        self.has_validate_output = False
        self.cache = None

        self.out = self.outgoing = _Outgoing(
            self.amqp,
            self._out_ftp,
            _WMQFacade(self.broker_client) if self.component_enabled_websphere_mq else None,
            self._worker_config.out_odoo,
            self._out_plain_http,
            self._worker_config.out_soap,
            self._worker_store.sql_pool_store,
            self._worker_store.stomp_outconn_api,
            ZMQFacade(self.server) if self.component_enabled_zeromq else None,
            self._worker_store.outgoing_web_sockets,
            self._worker_store.vault_conn_api,
            SMSAPI(self._worker_store.sms_twilio_api) if self.component_enabled_sms else None,
        )

    @staticmethod
    def get_name_static(class_):
        return Service.get_name(class_)

    @classmethod
    def get_name(class_):
        """ Returns a service's name, settings its .name attribute along. This will
        be called once while the service is being deployed.
        """
        if not hasattr(class_, '__service_name'):
            name = getattr(class_, 'name', None)
            if not name:
                name = service_name_from_impl(class_.get_impl_name())
                name = class_.convert_impl_name(name)

            class_.__service_name = name

        return class_.__service_name

    @classmethod
    def get_impl_name(class_):
        if not hasattr(class_, '__service_impl_name'):
            class_.__service_impl_name = '{}.{}'.format(class_.__module__, class_.__name__)
        return class_.__service_impl_name

    @staticmethod
    def convert_impl_name(name):
        # TODO: Move the replace functionality over to uncamelify, possibly modifying its regexp
        split = uncamelify(name).split('.')

        path, class_name = split[:-1], split[-1]
        path = [elem.replace('_', '-') for elem in path]

        class_name = class_name[1:] if class_name.startswith('-') else class_name
        class_name = class_name.replace('.-', '.').replace('_-', '_')

        return '{}.{}'.format('.'.join(path), class_name)

    @classmethod
    def add_http_method_handlers(class_):

        for name in dir(class_):
            if name.startswith('handle_'):

                if not getattr(class_, 'http_method_handlers', False):
                    setattr(class_, 'http_method_handlers', {})

                method = name.replace('handle_', '')
                class_.http_method_handlers[method] = getattr(class_, name)

    def _init(self, is_http=False):
        """ Actually initializes the service.
        """
        self.slow_threshold = self.server.service_store.services[self.impl_name]['slow_threshold']

        # The if's below are meant to be written in this way because we don't want any unnecessary attribute lookups
        # and method calls in this method - it's invoked each time a service is executed. The attributes are set
        # for the whole of the Service class each time it is discovered they are needed. It cannot be done in ServiceStore
        # because at the time that ServiceStore executes the worker config may still not be ready.

        if self.component_enabled_cassandra:
            if not Service.cassandra_conn:
                Service.cassandra_conn = self._worker_store.cassandra_api
            if not Service.cassandra_query:
                Service.cassandra_query = self._worker_store.cassandra_query_api

        if self.component_enabled_email:
            if not Service.email:
                Service.email = EMailAPI(self._worker_store.email_smtp_api, self._worker_store.email_imap_api)

        if self.component_enabled_search:
            if not Service.search:
                Service.search = SearchAPI(self._worker_store.search_es_api, self._worker_store.search_solr_api)
        if self.component_enabled_msg_path:
            self.msg = MessageFacade(
                self._json_pointer_store, self._xpath_store, self._msg_ns_store, self.request.payload, self.time)

        if self.component_enabled_patterns:
            self.patterns = PatternsFacade(self)

        if is_http:
            self.request.http.init(self.wsgi_environ)

        # self.is_sio attribute is set by ServiceStore during deployment
        if self.has_sio:
            self.request.init(True, self.cid, self.SimpleIO, self.data_format, self.transport, self.wsgi_environ)
            self.response.init(self.cid, self.SimpleIO, self.data_format)

        # Cache is always enabled
        self.cache = self._worker_store.cache_api

    def set_response_data(self, service, _raw_types=(basestring, dict, list, tuple, EtreeElement, ObjectifiedElement), **kwargs):
        response = service.response.payload
        if not isinstance(response, _raw_types):
            response = response.getvalue(serialize=kwargs['serialize'])
            if kwargs['as_bunch']:
                response = bunchify(response)
            service.response.payload = response

        return response

    def _invoke(self, service, channel, http_channels=(CHANNEL.HTTP_SOAP, CHANNEL.INVOKE)):
        #
        # If channel is HTTP and there are any per-HTTP verb methods, it means we want for the service to be a REST target.
        # Let's say it is POST. If we have handle_POST, it is invoked. If there is no handle_POST,
        # '405 Method Not Allowed is returned'.
        #
        # However, if we have 'handle' only, it means this is always invoked and no default 405 is returned.
        #
        # In short, implement handle_* if you want REST behaviour. Otherwise, keep everything in handle.
        #

        # Ok, this is HTTP
        if channel in http_channels:

            # We have at least one per-HTTP verb handler
            if service.http_method_handlers:

                # But do we have any handler matching current request's verb?
                if service.request.http.method in service.http_method_handlers:

                    # Yes, call the handler
                    service.http_method_handlers[service.request.http.method](service)

                # No, return 405
                else:
                    service.response.status_code = METHOD_NOT_ALLOWED

            # We have no custom handlers so we always call 'handle'
            else:
                service.handle()

        # It's not HTTP so we simply call 'handle'
        else:
            service.handle()

    def extract_target(self, name):
        """ Splits a service's name into name and target, if the latter is provided on input at all.
        """
        # It can be either a name or a name followed by the target to invoke the service on,
        # i.e. 'myservice' or 'myservice@mytarget'.
        if '@' in name:
            name, target = name.split('@')
            if not target:
                raise ZatoException(self.cid, 'Target must not be empty in `{}`'.format(name))
        else:
            target = ''

        return name, target

    def update_handle(self, set_response_func, service, raw_request, channel, data_format,
            transport, server, broker_client, worker_store, cid, simple_io_config, _utcnow=datetime.utcnow,
            _call_hook_with_service=call_hook_with_service, _call_hook_no_service=call_hook_no_service,
            _CHANNEL_SCHEDULER=CHANNEL.SCHEDULER, _pattern_channels=(CHANNEL.FANOUT_CALL, CHANNEL.PARALLEL_EXEC_CALL),
            *args, **kwargs):

        wsgi_environ = kwargs.get('wsgi_environ', {})
        payload = wsgi_environ.get('zato.request.payload')

        # Here's an edge case. If a SOAP request has a single child in Body and this child is an empty element
        # (though possibly with attributes), checking for 'not payload' alone won't suffice - this evaluates
        # to False so we'd be parsing the payload again superfluously.
        if not isinstance(payload, ObjectifiedElement) and not payload:
            payload = payload_from_request(cid, raw_request, data_format, transport)

        job_type = kwargs.get('job_type')
        channel_params = kwargs.get('channel_params', {})
        merge_channel_params = kwargs.get('merge_channel_params', True)
        params_priority = kwargs.get('params_priority', PARAMS_PRIORITY.DEFAULT)

        service.update(service, channel, server, broker_client,
            worker_store, cid, payload, raw_request, transport, simple_io_config, data_format, wsgi_environ,
            job_type=job_type, channel_params=channel_params,
            merge_channel_params=merge_channel_params, params_priority=params_priority,
            in_reply_to=wsgi_environ.get('zato.request_ctx.in_reply_to', None), environ=kwargs.get('environ'))

        # It's possible the call will be completely filtered out. The uncommonly looking not self.accept shortcuts
        # if ServiceStore replaces self.accept with None in the most common case of this method's not being
        # implemented by user services.
        if (not self.accept) or service.accept():

            # Assume everything goes fine
            e, exc_formatted = None, None

            try:

                if service.server.component_enabled.stats:
                    service.usage = service.kvdb.conn.incr('{}{}'.format(KVDB.SERVICE_USAGE, service.name))
                service.invocation_time = _utcnow()

                # All hooks are optional so we check if they have not been replaced with None by ServiceStore.

                # Call before job hooks if any are defined and we are called from the scheduler
                if service._has_before_job_hooks and self.channel.type == _CHANNEL_SCHEDULER:
                    for elem in service._before_job_hooks:
                        if elem:
                            _call_hook_with_service(elem, service)

                # Called before .handle - catches exceptions
                if service.before_handle:
                    _call_hook_no_service(service.before_handle)

                # Called before .handle - does not catch exceptions
                if service.validate_input:
                    service.validate_input()

                # This is the place where the service is invoked
                self._invoke(service, channel)

                # Called after .handle - does not catch exceptions
                if service.validate_output:
                    service.validate_output()

                # Called after .handle - catches exceptions
                if service.after_handle:
                    _call_hook_no_service(service.after_handle)

                # Call after job hooks if any are defined and we are called from the scheduler
                if service._has_after_job_hooks and self.channel.type == _CHANNEL_SCHEDULER:
                    for elem in service._after_job_hooks:
                        if elem:
                            _call_hook_with_service(elem, service)

                # Internal method - always defined and called
                service.post_handle()

                # Optional, almost never overridden.
                if service.finalize_handle:
                    _call_hook_no_service(service.finalize_handle)

            except Exception, e:
                exc_formatted = format_exc(e)
                logger.warn(exc_formatted)

            finally:
                try:
                    response = set_response_func(service, data_format=data_format, transport=transport, **kwargs)

                    # If this was fan-out/fan-in we need to always notify our callbacks no matter the result
                    if channel in _pattern_channels:
                        func = self.patterns.fanout.on_call_finished if channel == CHANNEL.FANOUT_CALL else \
                            self.patterns.parallel.on_call_finished
                        spawn(func, self, service.response.payload, exc_formatted)

                except Exception, resp_e:

                    # If we already have an exception around, log the new one but don't overwrite the old one with it.
                    logger.warn('Exception in service `%s`, e:`%s`', service.name, format_exc(resp_e))

                    if e:
                        if isinstance(e, Reportable):
                            raise e
                        else:
                            raise Exception(exc_formatted)
                    raise resp_e

                else:
                    if e:
                        raise

        # We don't accept it but some response needs to be returned anyway.
        else:
            response = service.response
            response.payload = ''
            response.status_code = BAD_REQUEST

        return response

    def invoke_by_impl_name(self, impl_name, payload='', channel=CHANNEL.INVOKE, data_format=DATA_FORMAT.DICT,
                            transport=None, serialize=False, as_bunch=False, timeout=None, raise_timeout=True, **kwargs):
        """ Invokes a service synchronously by its implementation name (full dotted Python name).
        """
        if self.component_enabled_target_matcher:

            orig_impl_name = impl_name
            impl_name, target = self.extract_target(impl_name)

            # It's possible we are being invoked through self.invoke or self.invoke_by_id
            target = target or kwargs.get('target', '')

            if not self._worker_store.target_matcher.is_allowed(target):
                raise ZatoException(self.cid, 'Invocation target `{}` not allowed ({})'.format(target, orig_impl_name))

        if self.component_enabled_invoke_matcher:
            if not self._worker_store.invoke_matcher.is_allowed(impl_name):
                raise ZatoException(self.cid, 'Service `{}` (impl_name) cannot be invoked'.format(impl_name))

        if self.impl_name == impl_name:
            msg = 'A service cannot invoke itself, name:[{}]'.format(self.name)
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)

        service, is_active = self.server.service_store.new_instance(impl_name)
        if not is_active:
            raise Inactive(service.get_name())

        set_response_func = kwargs.pop('set_response_func', service.set_response_data)

        invoke_args = (set_response_func, service, payload, channel, data_format, transport, self.server,
                       self.broker_client, self._worker_store, kwargs.pop('cid', self.cid), self.request.simple_io_config)

        kwargs.update({'serialize':serialize, 'as_bunch':as_bunch})

        try:
            if timeout:
                try:
                    g = spawn(self.update_handle, *invoke_args, **kwargs)
                    return g.get(block=True, timeout=timeout)
                except Timeout:
                    g.kill()
                    logger.warn('Service `%s` timed out (%s)', service.name, self.cid)
                    if raise_timeout:
                        raise
            else:
                return self.update_handle(*invoke_args, **kwargs)
        except Exception, e:
            logger.warn('Could not invoke `%s`, e:`%s`', service.name, format_exc(e))
            raise

    def invoke(self, name, *args, **kwargs):
        """ Invokes a service synchronously by its name.
        """
        if self.component_enabled_target_matcher:
            name, target = self.extract_target(name)
            kwargs['target'] = target

        if self._enforce_service_invokes and self.invokes:
            if name not in self.invokes:
                msg = 'Could not invoke `{}` which is not in `{}`'.format(name, self.invokes)
                self.logger.warn(msg)
                raise ValueError(msg)

        return self.invoke_by_impl_name(self.server.service_store.name_to_impl_name[name], *args, **kwargs)

    def invoke_by_id(self, service_id, *args, **kwargs):
        """ Invokes a service synchronously by its ID.
        """
        if self.component_enabled_target_matcher:
            service_id, target = self.extract_target(service_id)
            kwargs['target'] = target

        return self.invoke_by_impl_name(self.server.service_store.id_to_impl_name[service_id], *args, **kwargs)

    def invoke_async(self, name, payload='', channel=CHANNEL.INVOKE_ASYNC, data_format=DATA_FORMAT.DICT,
                     transport=None, expiration=BROKER.DEFAULT_EXPIRATION, to_json_string=False, cid=None, callback=None,
                     zato_ctx={}, environ={}):
        """ Invokes a service asynchronously by its name.
        """
        if self.component_enabled_target_matcher:
            name, target = self.extract_target(name)
            zato_ctx['zato.request_ctx.target'] = target

        # Let's first find out if the service can be invoked at all
        impl_name = self.server.service_store.name_to_impl_name[name]

        if self.component_enabled_invoke_matcher:
            if not self._worker_store.invoke_matcher.is_allowed(impl_name):
                raise ZatoException(self.cid, 'Service `{}` (impl_name) cannot be invoked'.format(impl_name))

        if to_json_string:
            payload = dumps(payload)

        cid = cid or new_cid()

        # If there is any callback at all, we need to figure out its name because that's how it will be invoked by.
        if callback:

            # The same service
            if callback is self:
                callback = self.name

        else:
            sink = '{}-async-callback'.format(self.name)
            if sink in self.server.service_store.name_to_impl_name:
                callback = sink

            # Otherwise the callback must be a string pointing to the actual service to reply to so we don't need to do anything.

        msg = {}
        msg['action'] = SERVICE.PUBLISH.value
        msg['service'] = name
        msg['payload'] = payload
        msg['cid'] = cid
        msg['channel'] = channel
        msg['data_format'] = data_format
        msg['transport'] = transport
        msg['is_async'] = True
        msg['callback'] = callback
        msg['zato_ctx'] = zato_ctx
        msg['environ'] = environ

        # If we have a target we need to invoke all the servers
        # and these which are not able to handle the target will drop the message.
        (self.broker_client.publish if target else self.broker_client.invoke_async)(msg, expiration=expiration)

        return cid

    def post_handle(self, _get_response_value=get_response_value, _utcnow=datetime.utcnow,
        _service_time_basic=KVDB.SERVICE_TIME_BASIC, _service_time_raw=KVDB.SERVICE_TIME_RAW,
        _service_time_raw_by_minute=KVDB.SERVICE_TIME_RAW_BY_MINUTE):
        """ An internal method executed after the service has completed and has
        a response ready to return. Updates its statistics and, optionally, stores
        a sample request/response pair.
        """

        #
        # Statistics
        #

        self.handle_return_time = _utcnow()
        self.processing_time_raw = self.handle_return_time - self.invocation_time

        if self.server.component_enabled.stats:

            proc_time = self.processing_time_raw.total_seconds() * 1000.0
            proc_time = proc_time if proc_time > 1 else 0

            self.processing_time = int(round(proc_time))

            with self.kvdb.conn.pipeline() as pipe:

                pipe.hset('%s%s' % (_service_time_basic, self.name), 'last', self.processing_time)
                pipe.rpush('%s%s' % (_service_time_raw, self.name), self.processing_time)

                key = '%s%s:%s' % (_service_time_raw_by_minute,
                    self.name, self.handle_return_time.strftime('%Y:%m:%d:%H:%M'))
                pipe.rpush(key, self.processing_time)

                # .. we'll have 5 minutes (5 * 60 seconds = 300 seconds)
                # to aggregate processing times for a given minute and then it will expire

                # Note that we need Redis 2.1.3+ otherwise the key has just been overwritten
                pipe.expire(key, 300)
                pipe.execute()

        #
        # Sample requests/responses
        #

        if self._req_resp_freq and self.usage % self._req_resp_freq == 0:

            data = {
                'cid': self.cid,
                'req_ts': self.invocation_time.isoformat(),
                'resp_ts': self.handle_return_time.isoformat(),
                'req': self.request.raw_request or '',
                'resp':_get_response_value(self.response), # TODO: Don't parse it here and a moment later below
            }
            self.kvdb.conn.hmset(key, data)

        #
        # Slow responses
        #
        if self.server.component_enabled.slow_response:

            if self.processing_time > self.slow_threshold:

                data = {
                    'cid': self.cid,
                    'proc_time': self.processing_time,
                    'slow_threshold': self.slow_threshold,
                    'req_ts': self.invocation_time.isoformat(),
                    'resp_ts': self.handle_return_time.isoformat(),
                    'req': self.request.raw_request or '',
                    'resp':_get_response_value(self.response), # TODO: Don't parse it here and a moment earlier above
                }
                slow_response.store(self.kvdb, self.name, **data)

    def translate(self, *args, **kwargs):
        raise NotImplementedError('An initializer should override this method')

    def handle(self):
        """ The only method Zato services need to implement in order to process
        incoming requests.
        """
        raise NotImplementedError('Should be overridden by subclasses')

    def lock(self, name=None, ttl=20, block=10):
        """ Creates a distributed lock.

        name - defaults to self.name effectively making access to this service serialized
        ttl - defaults to 20 seconds and is the max time the lock will be held
        block - how long (in seconds) we will wait to acquire the lock before giving up
        """
        return self.server.zato_lock_manager(name or self.name, ttl=ttl, block=block)

# ################################################################################################################################

    def accept(self, _zato_no_op_marker=zato_no_op_marker):
        return True

# ################################################################################################################################

    @classmethod
    def before_add_to_store(cls, logger):
        """ Invoked right before the class is added to the service store.
        """
        return True

    def before_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked  if the service has been defined as a job's invocation target,
        regardless of the job's type.
        """

    def before_one_time_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked if the service has been defined as a one-time job's
        invocation target.
        """

    def before_interval_based_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked if the service has been defined as an interval-based job's
        invocation target.
        """

    def before_cron_style_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked if the service has been defined as a cron-style job's
        invocation target.
        """

    def before_handle(self, _zato_no_op_marker=zato_no_op_marker, *args, **kwargs):
        """ Invoked just before the actual service receives the request data.
        """

    def after_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked  if the service has been defined as a job's invocation target,
        regardless of the job's type.
        """

    def after_one_time_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked if the service has been defined as a one-time job's
        invocation target.
        """

    def after_interval_based_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked if the service has been defined as an interval-based job's
        invocation target.
        """

    def after_cron_style_job(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked if the service has been defined as a cron-style job's
        invocation target.
        """

    def after_handle(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked right after the actual service has been invoked, regardless
        of whether the service raised an exception or not.
        """

    def finalize_handle(self, _zato_no_op_marker=zato_no_op_marker):
        """ Offers the last chance to influence the service's operations.
        """

    @staticmethod
    def after_add_to_store(logger):
        """ Invoked right after the class has been added to the service store.
        """

    def validate_input(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked right before handle. Any exception raised means handle will not be called.
        """

    def validate_output(self, _zato_no_op_marker=zato_no_op_marker):
        """ Invoked right after handle. Any exception raised means further hooks will not be called.
        """

# ################################################################################################################################

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
                msg[attr] = self.channel.type if attr == 'channel' else getattr(self, attr, '(None)')
            else:
                msg[attr] = suppressed_msg

        self.logger.log(level, '{}{}'.format(user_msg, msg))

        return msg

    def log_input(self, user_msg='', level=logging.INFO, suppress_keys=None):
        return self._log_input_output(user_msg, level, suppress_keys, False)

    def log_output(self, user_msg='', level=logging.INFO, suppress_keys=('wsgi_environ',)):
        return self._log_input_output(user_msg, level, suppress_keys, True)

# ################################################################################################################################

    @staticmethod
    def update(service, channel_type, server, broker_client, _ignored, cid, payload,
               raw_request, transport=None, simple_io_config=None, data_format=None,
               wsgi_environ={}, job_type=None, channel_params=None,
               merge_channel_params=True, params_priority=None, in_reply_to=None, environ=None, init=True,
               http_soap=CHANNEL.HTTP_SOAP, _CHANNEL_AMQP=CHANNEL.AMQP):
        """ Takes a service instance and updates it with the current request's
        context data.
        """
        service.server = server
        service.broker_client = broker_client
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
        service.user_config = server.user_config
        service.static_config = server.static_config
        service.time = server.time_util

        if channel_params:
            service.request.channel_params.update(channel_params)

        service.request.merge_channel_params = merge_channel_params
        service.request.params_priority = params_priority
        service.in_reply_to = in_reply_to
        service.environ = environ or {}

        channel_item = wsgi_environ.get('zato.channel_item', {})
        sec_def_info = wsgi_environ.get('zato.sec_def', {})

        if channel_type == _CHANNEL_AMQP:
            service.request.amqp = AMQPRequestData(channel_item['amqp_msg'])

        service.channel = service.chan = ChannelInfo(
            channel_item.get('id'), channel_item.get('name'), channel_type,
            channel_item.get('data_format'), channel_item.get('is_internal'), channel_item.get('match_target'),
            ChannelSecurityInfo(sec_def_info.get('id'), sec_def_info.get('name'), sec_def_info.get('type'),
                sec_def_info.get('username'), sec_def_info.get('impl')), channel_item)

        if init:
            service._init(channel_type==http_soap)

# ################################################################################################################################

class PubSubHook(Service):
    """ Subclasses of this class may act as pub/sub hooks.
    """
