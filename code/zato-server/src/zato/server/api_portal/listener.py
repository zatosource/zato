# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from json import dumps as json_dumps
from time import time
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.pool import Pool

# redis
from redis import Redis

# Zato
from zato.common.typing_ import cast_
from zato.server.api_portal.cache import get_spec
from zato.server.api_portal.caller import sign_in
from zato.server.api_portal.invoke import handle_invoke

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    from zato.server.base.parallel import ParallelServer
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# All API portal stream keys carry this per-environment prefix so that multiple Zato environments
# sharing one Redis never consume each other's messages. The portal application reads the same variable.
_stream_prefix = os.environ.get('Zato_OpenAPI_Stream_Prefix', 'zato:openapi')

class ModuleCtx:
    Request_Stream  = f'{_stream_prefix}:stream:request'
    Reply_Stream    = f'{_stream_prefix}:stream:reply'
    Consumer_Group  = 'server-openapi'
    Consumer_Name   = 'server-openapi-0'
    Max_Stream_Len  = 10_000
    Read_Count      = 10
    Read_Block_MS   = 1000

    # How many commands are handled at the same time, each in a greenlet of its own
    Max_Concurrent_Commands = 100

# ################################################################################################################################
# ################################################################################################################################

def _handle_sign_in(server:'ParallelServer', fields:'anydict') -> 'anydict':
    """ Builds a reply to a sign_in command - the session token that the portal sends in place of the credentials afterwards.
    """
    # Our response to produce
    out = {'correlation_id': fields['correlation_id']}

    session_token = sign_in(server, fields)

    if session_token is None:
        out['status'] = 'unauthorized'
        out['data'] = ''
    else:
        out['status'] = 'ok'
        out['data'] = session_token

    return out

# ################################################################################################################################

def _handle_get_spec(server:'ParallelServer', fields:'anydict') -> 'anydict':
    """ Builds a reply to a get_spec command - the spec filtered down to the caller.
    """
    # Our response to produce
    out = {'correlation_id': fields['correlation_id']}

    # Filter the cached document down to this caller - None means the caller could not be identified ..
    spec = get_spec(server, fields)

    if spec is None:
        out['status'] = 'unauthorized'
        out['data'] = ''
    else:
        out['status'] = 'ok'
        out['data'] = json_dumps(spec)

    return out

# ################################################################################################################################

# Maps command names from the request stream to their handlers - every handler receives the server
# and the message fields and returns the reply fields to place on the reply stream.
_command_handlers = {
    'sign_in': _handle_sign_in,
    'get_spec': _handle_get_spec,
    'invoke': handle_invoke,
}

# ################################################################################################################################

def is_expired(fields:'anydict', now:'float') -> 'bool':
    """ Whether the portal stopped waiting for the reply to a command before the command could be handled.
    """
    expires_at = float(fields['expires_at'])

    out = now > expires_at
    return out

# ################################################################################################################################

def handle_message(server:'ParallelServer', redis_conn:'Redis', stream_name:'str', msg_id:'str', fields:'anydict') -> 'None':
    """ Handles one command from the request stream and places its reply on the reply stream.
    """
    command = fields['command']

    # A command whose reply the portal no longer waits for is not run at all ..
    now = time()

    if is_expired(fields, now):
        logger.info('Skipping expired API portal command `%s`, correlation_id=%s', command, fields['correlation_id'])

    # .. each other command replies on the reply stream, correlated by the ID the portal sent ..
    elif handler := _command_handlers.get(command):
        try:
            reply = handler(server, fields)
        except Exception:
            logger.warning('Could not handle API portal command `%s`: %s', command, format_exc())
            reply = {
                'correlation_id': fields['correlation_id'],
                'status': 'error',
                'data': '',
            }

        # The reply always maps field names to strings and numbers, which Redis accepts
        reply = cast_('any_', reply)
        _ = redis_conn.xadd(ModuleCtx.Reply_Stream, reply, maxlen=ModuleCtx.Max_Stream_Len)

    # .. unknown commands are logged and skipped.
    else:
        logger.warning('Unknown API portal command `%s`', command)

    # A handled command is removed from the stream, together with the credentials or the session token it carries
    _ = redis_conn.xack(stream_name, ModuleCtx.Consumer_Group, msg_id)
    _ = redis_conn.xdel(stream_name, msg_id)

# ################################################################################################################################

def start_api_portal_listener(server:'ParallelServer') -> 'None':
    """ Starts a greenlet that serves API portal requests arriving via Redis Streams.
    """
    redis_config = server.fs_server_config.redis
    redis_password = redis_config.password if redis_config.password else None

    redis_conn = Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        password=redis_password,
        decode_responses=True,
    )

    server._ensure_stream_group(redis_conn, ModuleCtx.Request_Stream, ModuleCtx.Consumer_Group)

    # Commands run concurrently, and reading from the stream waits while all the greenlets are busy
    pool = Pool(ModuleCtx.Max_Concurrent_Commands)

    def _listener_loop() -> 'None':

        error_since = 0.0
        last_logged = 0.0

        while True:
            try:
                result = redis_conn.xreadgroup(
                    groupname=ModuleCtx.Consumer_Group,
                    consumername=ModuleCtx.Consumer_Name,
                    streams={ModuleCtx.Request_Stream: '>'},
                    count=ModuleCtx.Read_Count,
                    block=ModuleCtx.Read_Block_MS,
                )

                # A synchronous Redis client always returns a list here, never an awaitable
                result = cast_('anylist', result)

                # We are able to read from the stream again, so the error condition, if any, has cleared.
                if error_since:
                    logger.info('API portal listener recovered')
                    error_since = 0.0

                if not result:
                    continue

                for stream_name, messages in result:
                    for msg_id, fields in messages:
                        _ = pool.spawn(handle_message, server, redis_conn, stream_name, msg_id, fields)

            except Exception as exc:
                error_since, last_logged = server._handle_stream_listener_error(
                    'API portal', exc, redis_conn, (ModuleCtx.Request_Stream,), ModuleCtx.Consumer_Group,
                    error_since, last_logged)
                sleep(1)

    _ = spawn(_listener_loop)

    logger.info('API portal listener greenlet started')

# ################################################################################################################################
# ################################################################################################################################
