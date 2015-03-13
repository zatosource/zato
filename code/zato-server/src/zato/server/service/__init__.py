# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from httplib import METHOD_NOT_ALLOWED
from sys import maxint
from traceback import format_exc

# anyjson
from anyjson import dumps

# Arrow
import arrow

# Bunch
from bunch import bunchify

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# retools
from retools.lock import Lock

# gevent
from gevent import Timeout, spawn

# Zato
from zato.common import BROKER, CHANNEL, DATA_FORMAT, KVDB, PARAMS_PRIORITY, ZatoException
from zato.common.broker_message import SERVICE
from zato.common.nav import DictNav, ListNav
from zato.common.util import uncamelify, new_cid, payload_from_request, service_name_from_impl
from zato.server.connection import request_response, slow_response
from zato.server.connection.amqp.outgoing import PublisherFacade
from zato.server.connection.email import EMailAPI
from zato.server.connection.jms_wmq.outgoing import WMQFacade
from zato.server.connection.search import SearchAPI
from zato.server.connection.zmq_.outgoing import ZMQFacade
from zato.server.message import MessageFacade
from zato.server.pattern.fanout import FanOut
from zato.server.pattern.invoke_retry import InvokeRetry
from zato.server.pattern.parallel import ParallelExec
from zato.server.service.reqresp import Cloud, Outgoing, Request, Response

# Not used here in this module but it's convenient for callers to be able to import everything from a single namespace
from zato.server.service.reqresp.sio import AsIs, CSV, Boolean, Dict, Float, ForceType, Integer, List, ListOfDicts, Nested, \
     Opaque, Unicode, UTC

# So pyflakes doesn't complain about names being imported but not used
AsIs
CSV
Boolean
Dict
Float
ForceType
Integer
List
ListOfDicts
Nested
Opaque
Unicode
UTC

logger = logging.getLogger(__name__)

NOT_GIVEN = 'ZATO_NOT_GIVEN'

# Back compat
Bool = Boolean
Int = Integer

# ################################################################################################################################

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
        key = 'kvdb:date-format:{}'.format(format[5:])
        format = self.kvdb.conn.get(key)
        if not format:
            msg = 'Key [{}] does not exist'.format(key)
            logger.error(msg)
            raise ValueError(msg)

        return format

    def utcnow(self, format='YYYY-MM-DD HH:mm:ss', needs_format=True):
        """ Returns now in UTC formatted as given in 'format'.
        """
        now = arrow.utcnow()
        if needs_format:
            return now.format(format)
        return now

    def today(self, format='YYYY-MM-DD', tz='UTC', needs_format=True):
        """ Returns current day in a given timezone.
        """
        now = arrow.now(tz=tz)
        today = arrow.Arrow(year=now.year, month=now.month, day=now.day)

        if tz != 'UTC':
            today = today.to(tz)

        if format.startswith('kvdb:'):
            format = self.get_format_from_kvdb(format)

        if needs_format:
            return today.format(format)
        else:
            return today

    def reformat(self, value, from_, to):
        """ Reformats value from one datetime format to another, for instance
        from 23-03-2013 to 03/23/13 (MM-DD-YYYY to DD/MM/YY).
        """
        if from_.startswith('kvdb:'):
            from_ = self.get_format_from_kvdb(from_)

        if to.startswith('kvdb:'):
            to = self.get_format_from_kvdb(to)

        try:
            # Arrow compares to str, not basestring
            value = str(value) if isinstance(value, unicode) else value
            from_ = str(from_) if isinstance(from_, unicode) else from_
            return arrow.get(value, from_).format(to)
        except Exception:
            logger.error('Could not reformat value:`%s` from:`%s` to:`%s`',
                value, from_, to)
            raise

# ################################################################################################################################

class PatternsFacade(object):
    """ The API through which services make use of integration patterns.
    """
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
    http_method_handlers = {}

    def __init__(self, *ignored_args, **ignored_kwargs):
        self.logger = logging.getLogger(self.get_name())
        self.server = None
        self.broker_client = None
        self.pubsub = None
        self.channel = None
        self.cid = None
        self.in_reply_to = None
        self.outgoing = None
        self.cloud = None
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
        self.patterns = None
        self.user_config = None
        self.dictnav = DictNav
        self.listnav = ListNav
        self.has_validate_input = False
        self.has_validate_output = False

    @staticmethod
    def get_name_static(class_):
        return Service.get_name(class_)

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

    @classmethod
    def add_http_method_handlers(class_):

        for name in dir(class_):
            if name.startswith('handle_'):

                if not getattr(class_, 'http_method_handlers', False):
                    setattr(class_, 'http_method_handlers', {})

                method = name.replace('handle_', '')
                class_.http_method_handlers[method] = getattr(class_, name)

    def _init(self):
        """ Actually initializes the service.
        """
        self.odb = self.worker_store.server.odb
        self.kvdb = self.worker_store.kvdb
        self.time.kvdb = self.kvdb
        self.pubsub = self.worker_store.pubsub

        self.slow_threshold = self.server.service_store.services[self.impl_name]['slow_threshold']

        # Queues
        out_amqp = PublisherFacade(self.broker_client, self.server.delivery_store)
        out_jms_wmq = WMQFacade(self.broker_client, self.server.delivery_store)
        out_zmq = ZMQFacade(self.server)

        # Patterns
        self.patterns = PatternsFacade(self)

        # SQL
        out_sql = self.worker_store.sql_pool_store

        # Regular outconns
        out_ftp, out_odoo, out_plain_http, out_soap = self.worker_store.worker_config.outgoing_connections()
        self.outgoing = Outgoing(
            out_amqp, out_ftp, out_jms_wmq, out_odoo, out_plain_http, out_soap, out_sql, out_zmq)

        # Cloud
        self.cloud = Cloud()
        self.cloud.openstack.swift = self.worker_store.worker_config.cloud_openstack_swift
        self.cloud.aws.s3 = self.worker_store.worker_config.cloud_aws_s3

        # Cassandra
        self.cassandra_conn = self.worker_store.cassandra_api
        self.cassandra_query = self.worker_store.cassandra_query_api

        # E-mail
        self.email = EMailAPI(self.worker_store.email_smtp_api, self.worker_store.email_imap_api)

        # Search
        self.search = SearchAPI(self.worker_store.search_es_api, self.worker_store.search_solr_api)

        is_sio = hasattr(self, 'SimpleIO')
        self.request.http.init(self.wsgi_environ)

        if is_sio:
            self.request.init(is_sio, self.cid, self.SimpleIO, self.data_format, self.transport, self.wsgi_environ)
            self.response.init(self.cid, self.SimpleIO, self.data_format)

        self.msg = MessageFacade(self.worker_store.msg_ns_store,
            self.worker_store.json_pointer_store, self.worker_store.xpath_store, self.worker_store.msg_ns_store,
            self.request.payload, self.time)

    def set_response_data(self, service, **kwargs):
        response = service.response.payload
        if not isinstance(response, (basestring, dict, list, tuple, EtreeElement, ObjectifiedElement)):
            response = response.getvalue(serialize=kwargs['serialize'])
            if kwargs['as_bunch']:
                response = bunchify(response)
            service.response.payload = response

        return response

    def _invoke(self, service, channel):
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
        if channel in (CHANNEL.HTTP_SOAP, CHANNEL.INVOKE):

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
            transport, server, broker_client, worker_store, cid, simple_io_config, *args, **kwargs):

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
            worker_store, cid, payload, raw_request, transport,
            simple_io_config, data_format, wsgi_environ,
            job_type=job_type,
            channel_params=channel_params,
            merge_channel_params=merge_channel_params,
            params_priority=params_priority, in_reply_to=wsgi_environ.get('zato.request_ctx.in_reply_to', None),
            environ=kwargs.get('environ'))

        # It's possible the call will be completely filtered out
        if service.accept():

            # Assume everything goes fine
            e, exc_formatted = None, None

            try:
                service.pre_handle()
                service.call_hooks('before')

                service.validate_input()
                self._invoke(service, channel)
                service.validate_output()

                service.call_hooks('after')
                service.post_handle()
                service.call_hooks('finalize')

            except Exception, e:
                exc_formatted = format_exc(e)
                logger.warn(exc_formatted)

            finally:
                response = set_response_func(service, data_format=data_format, transport=transport, **kwargs)

                # If this is was fan-out/fan-in we need to always notify our callbacks no matter the result
                if channel in (CHANNEL.FANOUT_CALL, CHANNEL.PARALLEL_EXEC_CALL):
                    func = self.patterns.fanout.on_call_finished if channel == CHANNEL.FANOUT_CALL else \
                        self.patterns.parallel.on_call_finished
                    spawn(func, self, service.response.payload, exc_formatted)

                if e:
                    raise e

                return response

    def invoke_by_impl_name(self, impl_name, payload='', channel=CHANNEL.INVOKE, data_format=DATA_FORMAT.DICT,
            transport=None, serialize=False, as_bunch=False, timeout=None, raise_timeout=True, **kwargs):
        """ Invokes a service synchronously by its implementation name (full dotted Python name).
        """
        orig_impl_name = impl_name
        impl_name, target = self.extract_target(impl_name)

        # It's possible we are being invoked through self.invoke or self.invoke_by_id
        target = target or kwargs.get('target', '')

        if not self.worker_store.target_matcher.is_allowed(target):
            raise ZatoException(self.cid, 'Invocation target `{}` not allowed ({})'.format(target, orig_impl_name))

        if not self.worker_store.invoke_matcher.is_allowed(impl_name):
            raise ZatoException(self.cid, 'Service `{}` (impl_name) cannot be invoked'.format(impl_name))

        if self.impl_name == impl_name:
            msg = 'A service cannot invoke itself, name:[{}]'.format(self.name)
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)

        service = self.server.service_store.new_instance(impl_name)
        set_response_func = kwargs.pop('set_response_func', self.set_response_data)

        invoke_args = (set_response_func, service, payload, channel, data_format, transport, self.server,
                        self.broker_client, self.worker_store, self.cid, self.request.simple_io_config)

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
        if kwargs.get('debug_invoke'):
            self.logger.info('*' * 30)
            for k, v in sorted(locals().items()):
                self.logger.info('%r=%r', k, v)

        name, target = self.extract_target(name)
        kwargs['target'] = target

        return self.invoke_by_impl_name(self.server.service_store.name_to_impl_name[name], *args, **kwargs)

    def invoke_by_id(self, service_id, *args, **kwargs):
        """ Invokes a service synchronously by its ID.
        """
        service_id, target = self.extract_target(service_id)
        kwargs['target'] = target

        return self.invoke_by_impl_name(self.server.service_store.id_to_impl_name[service_id], *args, **kwargs)

    def invoke_async(self, name, payload='', channel=CHANNEL.INVOKE_ASYNC, data_format=DATA_FORMAT.DICT,
            transport=None, expiration=BROKER.DEFAULT_EXPIRATION, to_json_string=False, cid=None, callback=None,
            zato_ctx={}, environ={}):
        """ Invokes a service asynchronously by its name.
        """
        name, target = self.extract_target(name)
        zato_ctx['zato.request_ctx.target'] = target

        # Let's first find out if the service can be invoked at all
        impl_name = self.server.service_store.name_to_impl_name[name]

        if not self.worker_store.invoke_matcher.is_allowed(impl_name):
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

    def pre_handle(self):
        """ An internal method run just before the service sets to process the payload.
        Used for incrementing the service's usage count and storing the service invocation time.
        """
        if self.server.component_enabled.stats:
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

        if self.server.component_enabled.stats:

            proc_time = self.processing_time_raw.total_seconds() * 1000.0
            proc_time = proc_time if proc_time > 1 else 0

            self.processing_time = int(round(proc_time))

            with self.kvdb.conn.pipeline() as pipe:

                pipe.hset('{}{}'.format(KVDB.SERVICE_TIME_BASIC, self.name), 'last', self.processing_time)
                pipe.rpush('{}{}'.format(KVDB.SERVICE_TIME_RAW, self.name), self.processing_time)

                key = '{}{}:{}'.format(KVDB.SERVICE_TIME_RAW_BY_MINUTE,
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
        if self.server.component_enabled.slow_response:

            if self.processing_time > self.slow_threshold:

                # TODO: Don't parse it here and a moment earlier above
                resp = (self.response.payload.getvalue() if hasattr(self.response.payload, 'getvalue') \
                        else self.response.payload) or ''

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

    def lock(self, name=None, expires=20, timeout=10, backend=None):
        """ Creates a Redis-backed distributed lock.

        name - defaults to self.name effectively making access to this service serialized
        expires - defaults to 20 seconds and is the max time the lock will be held
        timeout - how long (in seconds) we will wait to acquire the lock before giving up and raising LockTimeout
        backend - a Redis connection object, defaults to self.kvdb.conn
        """
        name = '{}{}'.format(KVDB.LOCK_SERVICE_PREFIX, name or self.name)
        backend = backend or self.kvdb.conn
        return Lock(name, expires, timeout, backend)

# ################################################################################################################################

    def accept(self):
        return True

# ################################################################################################################################

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

    def validate_input(self):
        """ Invoked right before handle. Any exception raised means handle will not be called.
        """

    def validate_output(self):
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
                msg[attr] = getattr(self, attr, '(None)')
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
    def update(service, channel, server, broker_client, worker_store, cid, payload,
               raw_request, transport=None, simple_io_config=None, data_format=None,
               wsgi_environ={}, job_type=None, channel_params=None,
               merge_channel_params=True, params_priority=None, in_reply_to=None, environ=None, init=True):
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
        service.user_config = server.user_config

        if channel_params:
            service.request.channel_params.update(channel_params)

        service.request.merge_channel_params = merge_channel_params
        service.request.params_priority = params_priority
        service.in_reply_to = in_reply_to
        service.environ = environ or {}

        if init:
            service._init()

# ################################################################################################################################
