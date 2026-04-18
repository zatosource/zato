# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import queue
import threading
from dataclasses import dataclass
from datetime import timedelta
from json import dumps, loads
from logging import getLogger

# gevent
import gevent
from gevent import sleep, spawn
from gevent.event import AsyncResult

# zato-broker-core (Rust extension)
from zato_broker_core import (
    BrokerConfig,
    broker_broker_loop,
    broker_init,
    broker_init_logging,
    broker_start_http_server,
    broker_stop_http_server,
    broker_apply_auth_delta,
    broker_auth_snapshot,
    broker_auth_limits,
)

# Zato
from zato.common.api import PubSub
from zato.common.broker_message import SERVICE
from zato.common.util.api import as_bool, new_cid_broker_client, new_cid_server, new_msg_id, utcnow
from zato.broker.message_handler import handle_broker_msg

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, callable_, dictlist, strcalldict, strlist, strnone, strstrdict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

_sentinel = object()

# ################################################################################################################################
# ################################################################################################################################

def _to_bytes(value:'any_') -> 'bytes':
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode('utf-8')
    else:
        return dumps(value).encode('utf-8')

def _split_msg(msg:'any_') -> 'tuple[str, bytes]':
    """ Split a message into (meta_str, data_bytes).
    If msg is a dict with a 'data' key, that becomes data_bytes
    and the rest becomes meta_str. Otherwise, the entire message
    is metadata with empty data_bytes.
    """
    if isinstance(msg, dict):
        if 'data' in msg:
            data_bytes = _to_bytes(msg['data'])
            meta = {k: v for k, v in msg.items() if k != 'data'}
            return dumps(meta), data_bytes
        return dumps(msg), b''
    elif isinstance(msg, str):
        return msg, b''
    elif isinstance(msg, bytes):
        return '{}', msg
    else:
        return dumps(msg), b''

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Channel_Prefix = ''
    Queue_Prefix = 'queue.'
    Reply_Prefix = 'reply.'
    Stream_Prefix = 'stream.'
    Consumer_Group = 'zato-broker'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _InvokeWithCallbackCtx:
    correlation_id: 'str'
    reply_channel: 'str'

# ################################################################################################################################
# ################################################################################################################################

class NoResponseReceivedException(Exception):
    pass

# ################################################################################################################################
# ################################################################################################################################

class BrokerCoreAPI:

    def __init__(self, *, server:'ParallelServer | None'=None, **kwargs:'any_') -> 'None':

        self.server = server
        self.lock = threading.RLock()
        self._callbacks:'strcalldict' = {}
        self.correlation_to_channel_map:'strstrdict' = {}

        self.context = kwargs.get('context') or self

        broker_dir = os.environ.get('Zato_Broker_Dir') or os.path.expanduser('~/env/qs-1/data/broker')
        log_dir = os.environ.get('Zato_Broker_Log_Dir') or os.path.expanduser('~/env/qs-1/server1/logs')

        poll_interval = float(os.environ.get('Zato_Broker_Poll_Interval', '0.05'))
        self._reply_poll_interval = float(os.environ.get('Zato_Broker_Reply_Poll_Interval', '0.01'))

        os.makedirs(log_dir, exist_ok=True)

        self._cfg = BrokerConfig(broker_dir, log_dir)

        broker_init_logging(log_dir, 10485760, 10, 10485760, 10)
        broker_init(self._cfg)

        self.broker_dir = broker_dir
        self.log_dir = log_dir

        self.queue_name = kwargs.get('queue_name') or 'server'
        self.channel_name = f'{ModuleCtx.Channel_Prefix}{self.queue_name}'
        self.stream_name = f'{ModuleCtx.Stream_Prefix}{self.queue_name}'

        self._pubsub = None

        self._request_queue = queue.Queue()
        hub = gevent.get_hub()
        self._hub_loop = hub.loop

        self._keepalive = self._hub_loop.timer(86400.0, ref=True)
        self._keepalive.start(lambda: None)

        # The broker loop runs entirely in Rust (broker_broker_loop).
        # It drains requests from the queue, does filesystem I/O without the GIL,
        # and delivers results back via hub_loop.run_callback_threadsafe.
        self._broker_thread = threading.Thread(
            target=broker_broker_loop,
            args=(
                self._request_queue,
                self._hub_loop,
                self._on_message,
                spawn,
                _sentinel,
                broker_dir,
                self._cfg.do_fsync,
                self.channel_name,
                self.queue_name,
                poll_interval,
            ),
            daemon=True,
            name='zato-broker',
        )
        self._broker_thread.start()

        http_host = os.environ.get('Zato_Broker_HTTP_Host', '0.0.0.0')
        http_port = int(os.environ.get('Zato_Broker_HTTP_Port', '20500'))
        http_workers = int(os.environ.get('Zato_Broker_HTTP_Workers', '0'))

        self.http_port = broker_start_http_server(
            self._cfg,
            http_host,
            http_port,
            http_workers or None,
        )
        logger.info('Broker started on %s:%s', http_host, self.http_port)

# ################################################################################################################################

    # Auth is now pushed from Python to Rust as atomic deltas. There are no
    # callbacks from Rust back into Python on the request path; the broker
    # thread consults its own in-process state, which this API mutates.

    @staticmethod
    def apply_auth_delta(delta:'anydict') -> 'None':
        """ Apply a batch of credential and/or ACL changes atomically.
        Every entry is keyed on `user_id`, the stable primary key of a
        security definition. The `username` is a mutable attribute used
        only for wire-level Basic Auth matching.
        `delta` shape:
            {
                'clear_all': bool,
                'cred_upserts': [
                    {
                        'user_id':  str,  # stable, never renamed
                        'username': str,  # current wire-level username
                        'method':   'basic_auth' | 'ldap' | 'oauth2',
                        'password': str,
                    },
                    ...
                ],
                'cred_removes': [user_id, ...],
                'acl_upserts': [
                    {'user_id': str, 'pub': [str, ...], 'sub': [str, ...]},
                    ...
                ],
                'acl_removes': [user_id, ...],
            }
        """
        broker_apply_auth_delta(delta)

    @staticmethod
    def set_credentials(
        user_id:'str',
        username:'str',
        password:'str',
        method:'str'='basic_auth',
    ) -> 'None':
        broker_apply_auth_delta({
            'cred_upserts': [{
                'user_id':  user_id,
                'username': username,
                'method':   method,
                'password': password,
            }],
        })

    @staticmethod
    def remove_credentials(user_id:'str') -> 'None':
        broker_apply_auth_delta({'cred_removes': [user_id]})

    @staticmethod
    def set_acl(user_id:'str', pub_patterns:'strlist', sub_patterns:'strlist') -> 'None':
        broker_apply_auth_delta({
            'acl_upserts': [{
                'user_id': user_id,
                'pub':     list(pub_patterns),
                'sub':     list(sub_patterns),
            }],
        })

    @staticmethod
    def remove_acl(user_id:'str') -> 'None':
        broker_apply_auth_delta({'acl_removes': [user_id]})

    @staticmethod
    def clear_auth_state() -> 'None':
        broker_apply_auth_delta({'clear_all': True})

    @staticmethod
    def auth_snapshot() -> 'anydict':
        return broker_auth_snapshot()

    @staticmethod
    def auth_limits() -> 'anydict':
        return broker_auth_limits()

# ################################################################################################################################

    def _submit(self, op:'str', *args:'any_') -> 'any_':
        async_result = AsyncResult()
        self._request_queue.put((op, args, async_result))
        return async_result.get()

# ################################################################################################################################

    def publish_to_pubsub(self, msg:'any_', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        self.publish(msg, routing_key='pubsub.publish.1')
        self.publish(msg, routing_key='pubsub.pull.1')

# ################################################################################################################################

    def publish(self, msg:'any_', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        should_append_details:'bool' = bool(kwargs.get('should_append_details'))

        if should_append_details:
            now = utcnow()
            pub_time_iso = now.isoformat()
            topic_name = kwargs.get('routing_key', '')
            msg_id = kwargs.get('msg_id') or new_msg_id()
            correl_id = kwargs.get('cid', '') or new_cid_server()
            expiration_time = now + timedelta(seconds=_default_expiration)
            expiration_time_iso = expiration_time.isoformat()

            data_bytes = _to_bytes(msg)

            meta = {
                'topic_name': topic_name,
                'msg_id': msg_id,
                'priority': _default_priority,
                'pub_time_iso': pub_time_iso,
                'recv_time_iso': pub_time_iso,
                'expiration': _default_expiration,
                'expiration_time_iso': expiration_time_iso,
                'correl_id': correl_id,
            }
            meta_str = dumps(meta)
        else:
            meta_str, data_bytes = _split_msg(msg)

        routing_key = kwargs.get('routing_key') or 'server'
        channel = f'{ModuleCtx.Channel_Prefix}{routing_key}'

        _ = self._submit('publish', self._cfg, channel, meta_str, data_bytes)

    invoke_async = publish

# ################################################################################################################################

    def publish_to_queue(self, queue_name:'str', msg:'any_', correlation_id:'str'='') -> 'None':
        meta_str, data_bytes = _split_msg(msg)

        if queue_name.startswith(PubSub.Prefix.Reply_Queue):
            channel = f'{ModuleCtx.Reply_Prefix}{queue_name}'
        else:
            channel = f'{ModuleCtx.Queue_Prefix}{queue_name}'

        if correlation_id:
            try:
                meta_dict = loads(meta_str)
                meta_dict['_correlation_id'] = correlation_id
                meta_str = dumps(meta_dict)
            except Exception:
                pass

        _ = self._submit('publish', self._cfg, channel, meta_str, data_bytes)

# ################################################################################################################################

    def _on_message(self, meta_str:'str', data_bytes:'bytes') -> 'None':
        try:
            body = loads(meta_str)
            if data_bytes:
                body['data'] = data_bytes

            correlation_id = body.pop('_correlation_id', None)

            if correlation_id and correlation_id in self._callbacks:
                callback = self._callbacks.pop(correlation_id)
                callback(body)
            else:
                result = handle_broker_msg(body, self.context)

                if result.was_handled and result.action_code == SERVICE.INVOKE.value:
                    if reply_to := body.get('reply_to'):
                        cid = body.get('cid', '')
                        self.publish_to_queue(reply_to, result.response, correlation_id=cid)

        except Exception as e:
            logger.warning('Error processing broker message: %s', e)

# ################################################################################################################################

    def _on_reply(self, meta_str:'str', data_bytes:'bytes') -> 'None':
        try:
            body = loads(meta_str)
            if data_bytes:
                body['data'] = data_bytes

            correlation_id = body.pop('_correlation_id', None)

            if correlation_id and correlation_id in self._callbacks:
                callback = self._callbacks.pop(correlation_id)

                with self.lock:
                    _ = self.correlation_to_channel_map.pop(correlation_id, None)

                callback(body)
            else:
                logger.warning('No callback found for correlation ID: %s', correlation_id)

        except Exception as e:
            logger.warning('Error processing reply message: %s', e)

# ################################################################################################################################

    def start_consumer(self) -> 'None':
        self._submit('start_consumer')
        logger.info('Started broker consumer')

# ################################################################################################################################

    def stop_consumer(self) -> 'None':
        self._request_queue.put(_sentinel)

        if self._broker_thread and self._broker_thread.is_alive():
            self._broker_thread.join(timeout=5.0)

        try:
            broker_stop_http_server(self._cfg)
        except Exception:
            pass

        if self._keepalive is not None:
            self._keepalive.stop()
            self._keepalive.close()
            self._keepalive = None

        logger.info('Stopped broker thread and HTTP server')

# ################################################################################################################################

    def _create_reply_channel(self) -> 'str':
        return f'{PubSub.Prefix.Reply_Queue}-{new_cid_broker_client()}'

# ################################################################################################################################

    def _subscribe_to_reply_channel(self, channel_name:'str', callback:'callable_') -> 'None':
        full_channel = f'{ModuleCtx.Reply_Prefix}{channel_name}'

        def _wait_for_reply():
            try:
                cursor = self._submit('read_cursor', self._cfg, full_channel, 'reply')
            except Exception:
                cursor = 0

            while True:
                try:
                    messages = self._submit('poll', self._cfg, full_channel, cursor)
                    for seq, meta_str, data_bytes in messages:
                        cursor = seq
                        self._on_reply(meta_str, data_bytes)
                        return
                except Exception:
                    break
                sleep(self._reply_poll_interval)

        _ = spawn(_wait_for_reply)

# ################################################################################################################################

    def _invoke_with_callback(self, msg:'anydict', callback:'callable_') -> '_InvokeWithCallbackCtx':
        correlation_id = new_cid_broker_client()
        reply_channel = self._create_reply_channel()

        self._subscribe_to_reply_channel(reply_channel, callback)

        with self.lock:
            self._callbacks[correlation_id] = callback
            self.correlation_to_channel_map[correlation_id] = reply_channel

            if 'cid' in msg:
                cid = msg['cid']
                self._callbacks[cid] = callback
                self.correlation_to_channel_map[cid] = reply_channel

        msg['reply_to'] = reply_channel
        msg['cid'] = correlation_id

        meta_str, data_bytes = _split_msg(msg)

        channel = f'{ModuleCtx.Channel_Prefix}server'
        _ = self._submit('publish', self._cfg, channel, meta_str, data_bytes)

        ctx = _InvokeWithCallbackCtx()
        ctx.correlation_id = correlation_id
        ctx.reply_channel = reply_channel

        return ctx

# ################################################################################################################################

    def _wait_for_response(self, ctx:'_InvokeWithCallbackCtx', response:'any_',
                           timeout:'int | float', sleep_time:'float', cid:'str') -> 'None':
        end_time = utcnow() + timedelta(seconds=timeout)
        while not response.ready and utcnow() < end_time:
            sleep(sleep_time)

# ################################################################################################################################

    def _invoke_sync(self, service:'str', request:'anydictnone'=None,
                     timeout:'int | float'=PubSub.Timeout.Invoke_Sync,
                     needs_root_elem:'bool'=False, cid:'str'='') -> 'any_':

        class ResponseHolder:
            def __init__(self):
                self.data = None
                self.ready = False
                self.cid = 'cid-not-set'
                self.service = 'service-not-set'

            def set_response(self, response):
                self.data = response
                self.ready = True
                logger.info('Rsp <- %s - `%s`', self.cid, self.service)

        response = ResponseHolder()
        response.service = service
        response.cid = cid

        msg = {
            'action': SERVICE.INVOKE.value,
            'service': service,
            'payload': request or {},
            'cid': cid,
            'request_type': 'sync',
        }

        ctx = self._invoke_with_callback(msg, response.set_response)
        response.reply_channel = ctx.reply_channel

        logger.info('Req -> %s - `%s` - `%s`', cid, service, request)

        self._wait_for_response(ctx, response, timeout, 0.05, cid)

        if not response.ready:
            with self.lock:
                _ = self._callbacks.pop(ctx.correlation_id, None)
                _ = self.correlation_to_channel_map.pop(ctx.correlation_id, None)
            raise NoResponseReceivedException(f'No response received from service `{service}`')

        if not needs_root_elem:
            data = response.data
            root = list(data.keys())[0]
            data = data[root]
        else:
            data = response.data

        return data

# ################################################################################################################################

    def invoke_sync(self, *args:'any_', **kwargs:'any_') -> 'any_':
        response = None
        while not response:
            try:
                response = self._invoke_sync('demo.ping')
            except NoResponseReceivedException as e:
                logger.info('Timeout: %s', e)
        return self._invoke_sync(*args, **kwargs)

# ################################################################################################################################

    def notify_pubsub_counterpart(self, cid:'str', action:'str', source_server_type:'str', **msg_data:'any_') -> 'None':
        counterpart = 'pull' if source_server_type == 'publish' else 'publish'
        queue_name = f'pubsub.{counterpart}.1'
        broker_msg = {'action': action, 'cid': cid, **msg_data}
        self.publish_to_queue(queue_name, broker_msg, cid)

# ################################################################################################################################

    def ping_connection(self) -> 'None':
        result = self._submit('ping', self._cfg)
        logger.info('Broker connection ping: OK (result=%s)', result)

# ################################################################################################################################

    def create_internal_queue(self, queue_name:'str') -> 'None':
        pass

    def delete_queue(self, cid:'str', queue_name:'str') -> 'None':
        pass

    def get_queue_list(self, cid:'str', prefix:'str'='', exclude_list:'strlist | None'=None) -> 'dictlist':
        return []

    def get_bindings(self, *args, **kwargs):
        return []

    def create_bindings(self, *args, **kwargs):
        pass

    def delete_bindings(self, *args, **kwargs):
        pass

    def update_bindings(self, *args, **kwargs):
        pass

    def delete_topic(self, *args, **kwargs):
        pass

    def get_bindings_by_queue(self, *args, **kwargs):
        return []

    def queue_has_bindings(self, *args, **kwargs):
        return False

    def get_bindings_by_routing_key(self, *args, **kwargs):
        return []

    def rename_topic(self, *args, **kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################
