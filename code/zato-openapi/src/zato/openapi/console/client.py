# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import json
import logging
import os
import time
from uuid import uuid4

# redis
from redis import Redis

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# All OpenAPI console stream keys carry this per-environment prefix so that multiple Zato environments
# sharing one Redis never consume each other's messages. The server-side listener reads the same variable.
_stream_prefix = os.environ.get('Zato_OpenAPI_Stream_Prefix', 'zato:openapi')

class ModuleCtx:
    Request_Stream = f'{_stream_prefix}:stream:request'
    Reply_Stream = f'{_stream_prefix}:stream:reply'
    Consumer_Group = 'console'
    Consumer_Name = 'console-0'
    Max_Stream_Len = 10_000
    Reply_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIConsoleClient:
    """ Talks to Zato servers over Redis Streams - requests go to the request stream
    and the console blocks until the server replies with a correlated message on the reply stream.
    """

    def __init__(self, redis_conn:'Redis | None'=None) -> 'None':
        if redis_conn:
            self.redis = redis_conn
        else:
            redis_host = os.environ.get('Zato_OpenAPI_Redis_Host', 'localhost')
            redis_port = int(os.environ.get('Zato_OpenAPI_Redis_Port', '6379'))
            redis_password = os.environ.get('Zato_OpenAPI_Redis_Password', None)
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
            )

        self._ensure_reply_group()

# ################################################################################################################################

    def _ensure_reply_group(self) -> 'None':
        try:
            _ = self.redis.xgroup_create(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, id='$', mkstream=True)
        except Exception as exc:

            # The group already exists, which is fine - anything else is a real error.
            if 'BUSYGROUP' not in str(exc):
                raise

# ################################################################################################################################

    def _wait_for_reply(self, correlation_id:'str') -> 'anydictnone':
        """ Blocks until the server's reply with our correlation ID arrives or the timeout passes.
        """
        deadline = time.monotonic() + ModuleCtx.Reply_Timeout

        while time.monotonic() < deadline:
            result = self.redis.xreadgroup(
                groupname=ModuleCtx.Consumer_Group,
                consumername=ModuleCtx.Consumer_Name,
                streams={ModuleCtx.Reply_Stream: '>'},
                count=10,
                block=1000,
            )

            # A synchronous Redis client always returns a list here, never an awaitable
            result = cast_('anylist', result)

            if not result:
                continue

            for stream_name, messages in result:
                for msg_id, fields in messages:
                    _ = self.redis.xack(stream_name, ModuleCtx.Consumer_Group, msg_id)

                    # Replies to other requests are acked and skipped - only ours is returned.
                    if fields['correlation_id'] == correlation_id:
                        return fields

        logger.info('Timed out waiting for an OpenAPI console reply, correlation_id=%s', correlation_id)

# ################################################################################################################################

    def get_spec(self, auth:'anydict') -> 'anydictnone':
        """ Asks a server for the OpenAPI document filtered down to the given caller.
        Returns the document as a dict, or None if the caller was rejected or no server replied.
        """
        correlation_id = uuid4().hex

        _ = self.redis.xadd(ModuleCtx.Request_Stream, {
            'command': 'get_spec',
            'correlation_id': correlation_id,
            'auth_type': auth['auth_type'],
            'username': auth['username'],
            'password': auth['password'],
            'is_admin': auth['is_admin'],
        }, maxlen=ModuleCtx.Max_Stream_Len)

        reply = self._wait_for_reply(correlation_id)

        if not reply:
            return None

        if reply['status'] != 'ok':
            logger.info('OpenAPI document request rejected, status=%s username=%s', reply['status'], auth['username'])
            return None

        out = json.loads(reply['data'])

        return out

# ################################################################################################################################

    def invoke(
        self,
        auth:'anydict',
        http_method:'str',
        url_path:'str',
        query_string:'str',
        body:'str',
        ) -> 'anydictnone':
        """ Relays a try-it invocation to a server and returns the reply fields,
        or None if no server replied in time.
        """
        correlation_id = uuid4().hex

        _ = self.redis.xadd(ModuleCtx.Request_Stream, {
            'command': 'invoke',
            'correlation_id': correlation_id,
            'auth_type': auth['auth_type'],
            'username': auth['username'],
            'password': auth['password'],
            'is_admin': auth['is_admin'],
            'http_method': http_method,
            'url_path': url_path,
            'query_string': query_string,
            'body': body,
        }, maxlen=ModuleCtx.Max_Stream_Len)

        out = self._wait_for_reply(correlation_id)

        return out

# ################################################################################################################################
# ################################################################################################################################
