# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import time
from base64 import b64encode
from uuid import uuid4

# redis
from redis import Redis

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Command_Stream = 'zato:queue_bridge:stream:command'
    Reply_Stream = 'zato:queue_bridge:stream:reply'
    Recv_Stream = 'zato:queue_bridge:stream:recv'
    Consumer_Group = 'server'
    Consumer_Name = 'server-0'
    Http_Base = 'http://127.0.0.1:35111'
    Reply_Timeout = 1.0

# ################################################################################################################################
# ################################################################################################################################

class QueueBridgeClient:
    """ Thin client that replaces the in-process PyO3 QueueBridge.

    Write commands go via Redis Streams (XADD to the command stream).
    Read queries go via HTTP GET to the queue bridge's actix-web API.
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

        self._ensure_reply_group()

# ################################################################################################################################

    def new_redis_conn(self) -> 'Redis':
        """ Returns a new Redis connection using the same config as this client. """
        return Redis(
            host=self.redis.connection_pool.connection_kwargs['host'],
            port=self.redis.connection_pool.connection_kwargs['port'],
            password=self.redis.connection_pool.connection_kwargs.get('password'),
            decode_responses=True,
        )

    def _ensure_reply_group(self) -> 'None':
        try:
            self.redis.xgroup_create(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, id='$', mkstream=True)
        except Exception as exc:
            if 'BUSYGROUP' in str(exc):
                pass
            else:
                raise

# ################################################################################################################################

    def invoke(self, command:'str', payload:'any_'=None, needs_reply:'bool'=False) -> 'anydict | None':
        """ Core method - XADDs a command to the queue bridge stream.

        If needs_reply is True, blocks until the bridge acks via the reply stream.
        """
        correlation_id = uuid4().hex
        payload_json = json.dumps(payload) if payload is not None else '{}'

        self.redis.xadd(ModuleCtx.Command_Stream, {
            'command': command,
            'correlation_id': correlation_id,
            'payload': payload_json,
        }, maxlen=100_000)

        if not needs_reply:
            return None

        deadline = time.monotonic() + ModuleCtx.Reply_Timeout

        while time.monotonic() < deadline:
            result = self.redis.xreadgroup(
                groupname=ModuleCtx.Consumer_Group,
                consumername=ModuleCtx.Consumer_Name,
                streams={ModuleCtx.Reply_Stream: '>'},
                count=10,
                block=1000,
            )

            if not result:
                continue

            for _stream_name, messages in result:
                for msg_id, fields in messages:
                    reply_corr = fields['correlation_id']
                    if reply_corr == correlation_id:
                        self.redis.xack(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, msg_id)
                        return {'status': fields['status'], 'data': fields.get('data', '')}

                    self.redis.xack(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, msg_id)

        logger.info('Timed out waiting for reply to command=%s correlation_id=%s', command, correlation_id)
        return {'status': 'timeout'}

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
        self.invoke('stop', needs_reply=True)

# ################################################################################################################################

    def reload(self, channels:'anylist | None'=None, outgoing:'anylist | None'=None) -> 'None':
        """ Sends the full connection config to the queue bridge. """
        payload = {
            'channels': channels if channels is not None else [],
            'outgoing': outgoing if outgoing is not None else [],
        }
        self.invoke('reload', payload, needs_reply=True)

# ################################################################################################################################

    def add_channel(self, config:'anydict') -> 'None':
        self.invoke('add_channel', config)

# ################################################################################################################################

    def add_outgoing(self, config:'anydict') -> 'None':
        self.invoke('add_outgoing', config)

# ################################################################################################################################

    def delete_channel(self, name:'str') -> 'None':
        self.invoke('delete_channel', {'name': name})

# ################################################################################################################################

    def delete_outgoing(self, name:'str') -> 'None':
        self.invoke('delete_outgoing', {'name': name})

# ################################################################################################################################

    def edit_channel(self, config:'anydict') -> 'None':
        self.invoke('edit_channel', config)

# ################################################################################################################################

    def edit_outgoing(self, config:'anydict') -> 'None':
        self.invoke('edit_outgoing', config)

# ################################################################################################################################

    def ping(self, conn_name:'str') -> 'anydict':
        """ Pings a named outgoing connection, returns reply dict with status. """
        return self.invoke('ping', {'conn_name': conn_name}, needs_reply=True) # type: ignore

# ################################################################################################################################

    def send_message(self, conn_name:'str', data:'bytes') -> 'anydict':
        """ Sends a message through a named outgoing connection, returns reply dict. """
        data_b64 = b64encode(data).decode('ascii')
        return self.invoke('send_message', {'conn_name': conn_name, 'data': data_b64}, needs_reply=True) # type: ignore

# ################################################################################################################################

    def get_connections(self) -> 'anylist':
        return self._http_get('/api/get_connections')

# ################################################################################################################################

    def get_connection_status(self, name:'str') -> 'anydict':
        return self._http_get('/api/get_connection_status', {'name': name})

# ################################################################################################################################
# ################################################################################################################################
