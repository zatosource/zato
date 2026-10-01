# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
from base64 import b64encode
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent import sleep, spawn
from gevent.event import AsyncResult
from gevent.lock import RLock

# redis
from redis import Redis

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, floatnone, intnone, strdict, strdictnone, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Command_Stream = 'zato:queue_bridge:stream:command'
    Reply_Stream = 'zato:queue_bridge:stream:reply'
    Request_Stream = 'zato:queue_bridge:stream:request'

    # The prefix of a channel's recv stream, the channel's id follows
    Recv_Stream_Prefix = 'zato:queue_bridge:stream:recv:'

    Consumer_Group = 'server'
    Consumer_Name = 'server-0'
    Http_Base = 'http://127.0.0.1:35111'

    # How long a command's reply is waited for by default, in seconds
    Reply_Timeout = 1.0

    # How many seconds longer than its own timeout a send is waited for
    Send_Timeout_Margin = 2.0

    # How many entries the command and reply streams keep
    Stream_Max_Len = 100_000

    # How long one read of the reply stream blocks, in milliseconds
    Reply_Block_Ms = 1000

    # How long the reply reader waits after an error, in seconds
    Reply_Error_Sleep = 1.0

    Status_OK = 'ok'
    Status_Error = 'error'
    Status_Timeout = 'timeout'

# ################################################################################################################################
# ################################################################################################################################

def get_recv_stream(channel_id:'int') -> 'str':
    """ The recv stream of one channel.
    """
    out = f'{ModuleCtx.Recv_Stream_Prefix}{channel_id}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class QueueBridgeClient:
    """ The server's side of the queue bridge binary.

    Write commands go via Redis Streams (XADD to the command stream) and their replies come back through the reply
    stream. Read queries go via HTTP GET to the queue bridge's actix-web API.
    """

    def __init__(self, redis_conn:'Redis | None'=None) -> 'None':
        if redis_conn:
            self.redis = redis_conn
        else:
            redis_host = os.environ.get('Zato_Queue_Bridge_Redis_Host', 'localhost')
            redis_port = int(os.environ.get('Zato_Queue_Bridge_Redis_Port', '6379'))
            redis_password = os.environ.get('Zato_Queue_Bridge_Redis_Password', None)
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
            )

        # The callers waiting for a reply, by correlation id
        self._pending:'anydict' = {}
        self._pending_lock = RLock()

        self._ensure_reply_group()

        # The reader has a blocking connection of its own.
        self._reply_redis = self.new_redis_conn()
        self._reply_greenlet = spawn(self._reply_loop)

# ################################################################################################################################

    def new_redis_conn(self) -> 'Redis':
        """ Returns a new Redis connection using the same config as this client.

        The connection is used for blocking stream reads (XREADGROUP with block=...), so it must not
        carry any socket timeout - otherwise the socket aborts the read at the timeout boundary
        instead of letting the server end the block, which surfaces as spurious TimeoutError warnings.
        """
        return Redis(
            host=self.redis.connection_pool.connection_kwargs['host'],
            port=self.redis.connection_pool.connection_kwargs['port'],
            password=self.redis.connection_pool.connection_kwargs.get('password'),
            decode_responses=True,
            socket_timeout=None,
        )

# ################################################################################################################################

    def ensure_stream_group(self, redis_conn:'Redis', stream:'str', group_name:'str', start_id:'str'='$') -> 'None':
        """ Creates a Redis stream and its consumer group, unless they exist already.
        """
        try:
            _ = redis_conn.xgroup_create(stream, group_name, id=start_id, mkstream=True)
        except Exception as exc:

            # The group already exists, which is fine - anything else is a real error.
            if 'BUSYGROUP' not in str(exc):
                raise

# ################################################################################################################################

    def _ensure_reply_group(self) -> 'None':
        self.ensure_stream_group(self.redis, ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group)

# ################################################################################################################################

    def _reply_loop(self) -> 'None':
        """ Reads replies off the reply stream and hands each to the caller waiting for it.
        """
        logger.info('Queue bridge reply reader entering')

        while True:
            try:
                result = self._reply_redis.xreadgroup(
                    groupname=ModuleCtx.Consumer_Group,
                    consumername=ModuleCtx.Consumer_Name,
                    streams={ModuleCtx.Reply_Stream: '>'},
                    count=100,
                    block=ModuleCtx.Reply_Block_Ms,
                )

                if not result:
                    continue

                for _stream_name, messages in result:
                    for msg_id, fields in messages:
                        self._dispatch_reply(fields)
                        _ = self._reply_redis.xack(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, msg_id)

            except Exception as exc:

                # A missing group is created again.
                if 'NOGROUP' in str(exc):
                    logger.warning('Recreating queue bridge reply group: %s', exc)
                    try:
                        self._ensure_reply_group()
                    except Exception:
                        pass
                else:
                    logger.warning('Error in queue bridge reply reader: %s', format_exc())

                sleep(ModuleCtx.Reply_Error_Sleep)

# ################################################################################################################################

    def _dispatch_reply(self, fields:'strdict') -> 'None':
        """ Gives one reply to the caller waiting for it, if there is one.
        """
        correlation_id = fields['correlation_id']

        with self._pending_lock:
            result = self._pending.pop(correlation_id, None)

        if result:
            reply = {'status': fields['status'], 'data': fields['data']}
            result.set(reply)

# ################################################################################################################################

    def invoke(
        self,
        command:'str',
        payload:'any_'=None,
        needs_reply:'bool'=False,
        timeout:'floatnone'=None,
        ) -> 'anydictnone':
        """ Core method - XADDs a command to the queue bridge stream.

        If needs_reply is True, blocks until the bridge replies or the timeout passes.
        """
        correlation_id = uuid4().hex
        payload_json = json.dumps(payload) if payload is not None else '{}'

        # The waiter is registered before the command goes out.
        if needs_reply:
            result = AsyncResult()
            with self._pending_lock:
                self._pending[correlation_id] = result
        else:
            result = None

        try:
            _ = self.redis.xadd(ModuleCtx.Command_Stream, {
                'command': command,
                'correlation_id': correlation_id,
                'payload': payload_json,
            }, maxlen=ModuleCtx.Stream_Max_Len)
        except Exception:
            if result:
                with self._pending_lock:
                    _ = self._pending.pop(correlation_id, None)
            raise

        if not result:
            return None

        if timeout is None:
            timeout = ModuleCtx.Reply_Timeout

        reply = result.wait(timeout)

        if reply is None:
            with self._pending_lock:
                _ = self._pending.pop(correlation_id, None)

            logger.info('Timed out waiting for reply to command=%s correlation_id=%s after %ss', command, correlation_id, timeout)
            reply = {'status': ModuleCtx.Status_Timeout, 'data': ''}

        return reply

# ################################################################################################################################

    def _http_get(self, path:'str', params:'anydict | None'=None) -> 'any_':
        """ Sends a GET request to the queue bridge's HTTP API. """
        url = f'{ModuleCtx.Http_Base}{path}'
        response = requests.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        return response.json()

# ################################################################################################################################

    def start(self, config:'anydict') -> 'None':
        """ No-op - the queue bridge binary is started externally. """
        pass

# ################################################################################################################################

    def stop(self, timeout_s:'float'=30.0) -> 'None':
        _ = self.invoke('stop', needs_reply=True, timeout=timeout_s)

# ################################################################################################################################

    def reload(self, channels:'anylist | None'=None, outgoing:'anylist | None'=None) -> 'None':
        """ Sends the full connection config to the queue bridge. """
        payload = {
            'channels': channels if channels is not None else [],
            'outgoing': outgoing if outgoing is not None else [],
        }
        _ = self.invoke('reload', payload, needs_reply=True)

# ################################################################################################################################

    def add_channel(self, config:'anydict') -> 'None':
        _ = self.invoke('add_channel', config)

# ################################################################################################################################

    def add_outgoing(self, config:'anydict') -> 'None':
        _ = self.invoke('add_outgoing', config)

# ################################################################################################################################

    def delete_channel(self, name:'str') -> 'None':
        _ = self.invoke('delete_channel', {'name': name})

# ################################################################################################################################

    def delete_outgoing(self, name:'str') -> 'None':
        _ = self.invoke('delete_outgoing', {'name': name})

# ################################################################################################################################

    def edit_channel(self, config:'anydict') -> 'None':
        _ = self.invoke('edit_channel', config)

# ################################################################################################################################

    def edit_outgoing(self, config:'anydict') -> 'None':
        _ = self.invoke('edit_outgoing', config)

# ################################################################################################################################

    def commit_offset(self, channel_id:'int', topic:'str', partition:'int', offset:'int') -> 'None':
        """ Tells the bridge to commit one offset of a channel.
        """
        payload = {
            'channel_id': channel_id,
            'topic': topic,
            'partition': partition,
            'offset': offset,
        }
        _ = self.invoke('commit_offset', payload)

# ################################################################################################################################

    def ping(self, conn_name:'str', timeout:'floatnone'=None) -> 'anydict':
        """ Pings a named outgoing connection, returns reply dict with status. """
        out = self.invoke('ping', {'conn_name': conn_name}, needs_reply=True, timeout=timeout)
        return out # type: ignore

# ################################################################################################################################

    def send_message(
        self,
        conn_name:'str',
        data:'bytes',
        *,
        key:'strnone'=None,
        headers:'strdictnone'=None,
        partition:'intnone'=None,
        is_tombstone:'bool'=False,
        send_timeout:'floatnone'=None,
        ) -> 'anydict':
        """ Sends a message through a named outgoing connection, returns reply dict. The reply of a send that went through
        carries the partition and offset the message landed at.
        """
        if headers is None:
            headers = {}

        payload = {
            'conn_name': conn_name,
            'data': b64encode(data).decode('ascii'),
            'headers': headers,
            'is_tombstone': is_tombstone,
        }

        if key is not None:
            payload['key'] = key

        if partition is not None:
            payload['partition'] = partition

        # The bridge gives up on a send after its own timeout first.
        if send_timeout is not None:
            timeout:'floatnone' = send_timeout + ModuleCtx.Send_Timeout_Margin
        else:
            timeout = None

        out = self.invoke('send_message', payload, needs_reply=True, timeout=timeout)
        return out # type: ignore

# ################################################################################################################################

    def send_reply(
        self,
        channel_name:'str',
        reply_to_queue:'str',
        reply_to_queue_manager:'str',
        message_id:'str',
        data:'bytes',
    ) -> 'anydict':
        """ Sends a reply to the reply-to queue of a message received through a channel, returns reply dict. """
        data_b64 = b64encode(data).decode('ascii')
        payload = {
            'channel_name': channel_name,
            'reply_to_queue': reply_to_queue,
            'reply_to_queue_manager': reply_to_queue_manager,
            'message_id': message_id,
            'data': data_b64,
        }
        return self.invoke('send_reply', payload, needs_reply=True) # type: ignore

# ################################################################################################################################

    def get_connections(self) -> 'anylist':
        return self._http_get('/api/get_connections')

# ################################################################################################################################

    def get_connection_status(self, name:'str') -> 'anydict':
        return self._http_get('/api/get_connection_status', {'name': name})

# ################################################################################################################################
# ################################################################################################################################
