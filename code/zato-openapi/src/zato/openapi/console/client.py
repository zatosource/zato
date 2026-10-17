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

# redis
from redis import Redis

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist
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
    Request_Stream  = f'{_stream_prefix}:stream:request'
    Reply_Stream    = f'{_stream_prefix}:stream:reply'
    Stream_Start_ID = '0-0'
    Max_Stream_Len  = 10_000
    Read_Count      = 100
    Read_Block_MS   = 1000
    Reply_Timeout   = 10.0

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIConsoleClient:
    """ Exchanges commands with Zato servers over Redis Streams - requests go to the request stream
    and the console blocks until the server replies with a correlated message on the reply stream.

    Every worker process and every concurrent request reads the reply stream independently, from the position
    the stream had right before its own request was sent, so a reply is never consumed by a request it does not belong to.
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

# ################################################################################################################################

    def _get_reply_position(self) -> 'str':
        """ Returns the ID of the newest message on the reply stream, or the start of the stream if it has no messages.
        """
        newest = self.redis.xrevrange(ModuleCtx.Reply_Stream, count=1)

        # A synchronous Redis client always returns a list here, never an awaitable
        newest = cast_('anylist', newest)

        if newest:
            newest_message = newest[0]
            out = newest_message[0]
        else:
            out = ModuleCtx.Stream_Start_ID

        return out

# ################################################################################################################################

    def _wait_for_reply(self, correlation_id:'str', position:'str') -> 'anydictnone':
        """ Blocks until the server's reply with our correlation ID arrives or the timeout passes.
        """
        deadline = time.monotonic() + ModuleCtx.Reply_Timeout

        while time.monotonic() < deadline:
            result = self.redis.xread(
                streams={ModuleCtx.Reply_Stream: position},
                count=ModuleCtx.Read_Count,
                block=ModuleCtx.Read_Block_MS,
            )

            # A synchronous Redis client always returns a list here, never an awaitable
            result = cast_('anylist', result)

            for _stream_name, messages in result:
                for msg_id, fields in messages:

                    # The next read continues past this message ..
                    position = msg_id

                    # .. and replies to other requests are left for the requests they belong to.
                    if fields['correlation_id'] == correlation_id:
                        return fields

        logger.info('Timed out waiting for an OpenAPI console reply, correlation_id=%s', correlation_id)

# ################################################################################################################################

    def _send(self, fields:'anydict') -> 'anydictnone':
        """ Sends one command to the servers and returns the fields of the reply, or None if no server replied in time.
        """
        correlation_id = CryptoManager.generate_hex_string()
        fields['correlation_id'] = correlation_id

        # The position is taken before the request is sent, so the reply cannot arrive ahead of it ..
        position = self._get_reply_position()

        # .. the request goes out ..
        _ = self.redis.xadd(ModuleCtx.Request_Stream, fields, maxlen=ModuleCtx.Max_Stream_Len)

        # .. and the reply is looked for past that position.
        out = self._wait_for_reply(correlation_id, position)

        return out

# ################################################################################################################################

    def get_spec(self, auth:'anydict') -> 'anydictnone':
        """ Asks a server for the OpenAPI document filtered down to the given caller.
        Returns the document as a dict, or None if the caller was rejected or no server replied.
        """
        reply = self._send({
            'command': 'get_spec',
            'auth_type': auth['auth_type'],
            'username': auth['username'],
            'password': auth['password'],
        })

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
        headers:'str',
        body:'str',
        remote_addr:'str',
        ) -> 'anydictnone':
        """ Relays a try-it invocation to a server and returns the reply fields,
        or None if no server replied in time. The headers are a JSON object of the caller's own request headers
        and the remote address is that of the browser, which the server's rate limits are keyed by.
        """
        out = self._send({
            'command': 'invoke',
            'auth_type': auth['auth_type'],
            'username': auth['username'],
            'password': auth['password'],
            'http_method': http_method,
            'url_path': url_path,
            'query_string': query_string,
            'headers': headers,
            'body': body,
            'remote_addr': remote_addr,
        })

        return out

# ################################################################################################################################
# ################################################################################################################################
