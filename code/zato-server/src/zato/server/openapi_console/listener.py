# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from json import dumps as json_dumps
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# redis
from redis import Redis

# Zato
from zato.common.typing_ import cast_
from zato.server.openapi_console.invoke import handle_invoke
from zato.server.openapi_console.spec import build_spec

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

# All OpenAPI console stream keys carry this per-environment prefix so that multiple Zato environments
# sharing one Redis never consume each other's messages. The console application reads the same variable.
_stream_prefix = os.environ.get('Zato_OpenAPI_Stream_Prefix', 'zato:openapi')

class ModuleCtx:
    Request_Stream = f'{_stream_prefix}:stream:request'
    Reply_Stream = f'{_stream_prefix}:stream:reply'
    Consumer_Group = 'server-openapi'
    Consumer_Name = 'server-openapi-0'
    Max_Stream_Len = 10_000

# ################################################################################################################################
# ################################################################################################################################

def _handle_get_spec(server:'ParallelServer', fields:'anydict') -> 'anydict':
    """ Builds a reply to a get_spec command - the spec filtered down to the caller's credentials.
    """
    username = fields['username']
    password = fields['password']

    # Our response to produce
    out = {'correlation_id': fields['correlation_id']}

    # Build the document for this caller - None means the credentials were not valid ..
    spec = build_spec(server, username, password)

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
    'get_spec': _handle_get_spec,
    'invoke': handle_invoke,
}

# ################################################################################################################################

def start_openapi_console_listener(server:'ParallelServer') -> 'None':
    """ Starts a greenlet that serves OpenAPI console requests arriving via Redis Streams.
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

    def _listener_loop() -> 'None':

        error_since = 0.0
        last_logged = 0.0

        while True:
            try:
                result = redis_conn.xreadgroup(
                    groupname=ModuleCtx.Consumer_Group,
                    consumername=ModuleCtx.Consumer_Name,
                    streams={ModuleCtx.Request_Stream: '>'},
                    count=10,
                    block=1000,
                )

                # A synchronous Redis client always returns a list here, never an awaitable
                result = cast_('anylist', result)

                # We are able to read from the stream again, so the error condition, if any, has cleared.
                if error_since:
                    logger.info('OpenAPI console listener recovered')
                    error_since = 0.0

                if not result:
                    continue

                for stream_name, messages in result:
                    for msg_id, fields in messages:

                        command = fields['command']

                        # Each command replies on the reply stream, correlated by the ID the console sent ..
                        if handler := _command_handlers.get(command):
                            try:
                                reply = handler(server, fields)
                            except Exception:
                                logger.warning('Could not handle OpenAPI console command `%s`: %s', command, format_exc())
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
                            logger.warning('Unknown OpenAPI console command `%s`', command)

                        _ = redis_conn.xack(stream_name, ModuleCtx.Consumer_Group, msg_id)

            except Exception as exc:
                error_since, last_logged = server._handle_stream_listener_error(
                    'OpenAPI console', exc, redis_conn, (ModuleCtx.Request_Stream,), ModuleCtx.Consumer_Group,
                    error_since, last_logged)
                sleep(1)

    _ = spawn(_listener_loop)

    logger.info('OpenAPI console listener greenlet started')

# ################################################################################################################################
# ################################################################################################################################
