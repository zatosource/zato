# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import pty
import select
import signal
import struct
import fcntl
import termios
import threading
import time
import uuid
from http.client import BAD_REQUEST
from traceback import format_exc

# Redis
import redis

# Django
from django.http import JsonResponse, StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed

logger = logging.getLogger(__name__)

Redis_Key_Prefix_Terminal_Session = 'zato.ide.terminal.session.'
Redis_Key_Prefix_Terminal_Commands = 'zato.ide.terminal.commands.'
Redis_Key_Prefix_Terminal_Output = 'zato.ide.terminal.output.'

_local_sessions = {}
_local_sessions_lock = threading.Lock()

def get_redis_client():
    return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class PTYSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.master_fd = None
        self.pid = None
        self.alive = True
        self.redis_client = get_redis_client()
        self.output_key = Redis_Key_Prefix_Terminal_Output + session_id
        self.commands_key = Redis_Key_Prefix_Terminal_Commands + session_id
        self.running = False
        self.reader_thread = None
        self.command_thread = None

    def start(self, rows=24, cols=80):
        pid, master_fd = pty.fork()

        if pid == 0:
            os.environ['TERM'] = 'xterm-256color'
            os.environ['COLORTERM'] = 'truecolor'
            shell = os.environ.get('SHELL', '/bin/bash')
            os.execvp(shell, [shell, '-l'])
        else:
            self.pid = pid
            self.master_fd = master_fd

            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            self.resize(rows, cols)
            self.running = True

            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()

            self.command_thread = threading.Thread(target=self._command_loop, daemon=True)
            self.command_thread.start()

    def _read_loop(self):
        logger.info('[terminal] reader thread started for session %s', self.session_id)
        while self.running and self.alive:
            try:
                ready, _, _ = select.select([self.master_fd], [], [], 0.05)
                if ready:
                    data = os.read(self.master_fd, 4096)
                    if data:
                        output = data.decode('utf-8', errors='replace')
                        self.redis_client.rpush(self.output_key, output)
                        self.redis_client.expire(self.output_key, 3600)
            except OSError:
                self.alive = False
                break
            except Exception:
                logger.warning('[terminal] reader error: %s', format_exc())
                break

        self.redis_client.rpush(self.output_key, '\x00CLOSED\x00')
        logger.info('[terminal] reader thread stopped for session %s', self.session_id)

    def _command_loop(self):
        logger.info('[terminal] command thread started for session %s', self.session_id)
        while self.running and self.alive:
            try:
                result = self.redis_client.blpop(self.commands_key, timeout=1)
                if not result:
                    continue

                _, cmd_data = result
                cmd = json.loads(cmd_data)
                cmd_type = cmd.get('type')

                if cmd_type == 'write':
                    data = cmd.get('data', '')
                    if self.master_fd is not None and self.alive:
                        os.write(self.master_fd, data.encode('utf-8'))
                elif cmd_type == 'resize':
                    rows = cmd.get('rows', 24)
                    cols = cmd.get('cols', 80)
                    self.resize(rows, cols)
                elif cmd_type == 'close':
                    self.close()
                    break

            except Exception:
                logger.warning('[terminal] command error: %s', format_exc())

        logger.info('[terminal] command thread stopped for session %s', self.session_id)

    def resize(self, rows, cols):
        if self.master_fd is not None:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def close(self):
        self.alive = False
        self.running = False
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        if self.pid is not None:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, os.WNOHANG)
            except OSError:
                pass


def _store_session_metadata(redis_client, session_id):
    session_key = Redis_Key_Prefix_Terminal_Session + session_id
    redis_client.set(session_key, json.dumps({'created': time.time()}))
    redis_client.expire(session_key, 3600)


def _session_exists(redis_client, session_id):
    session_key = Redis_Key_Prefix_Terminal_Session + session_id
    return redis_client.exists(session_key)


def _delete_session_metadata(redis_client, session_id):
    session_key = Redis_Key_Prefix_Terminal_Session + session_id
    output_key = Redis_Key_Prefix_Terminal_Output + session_id
    commands_key = Redis_Key_Prefix_Terminal_Commands + session_id
    redis_client.delete(session_key, output_key, commands_key)


@method_allowed('POST')
def terminal_create(req):
    """ Create a new PTY session. """
    try:
        body = json.loads(req.body)
        rows = body.get('rows', 24)
        cols = body.get('cols', 80)
    except Exception:
        rows = 24
        cols = 80

    session_id = str(uuid.uuid4())
    session = PTYSession(session_id)
    session.start(rows, cols)

    with _local_sessions_lock:
        _local_sessions[session_id] = session

    redis_client = get_redis_client()
    _store_session_metadata(redis_client, session_id)

    logger.info('[terminal] created session %s with rows=%s, cols=%s', session_id, rows, cols)

    return JsonResponse({'success': True, 'session_id': session_id})


@method_allowed('POST')
def terminal_write(req):
    """ Write data to a PTY session via Redis command queue. """
    try:
        body = json.loads(req.body)
        session_id = body.get('session_id', '')
        data = body.get('data', '')
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=BAD_REQUEST)

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    redis_client = get_redis_client()

    if not _session_exists(redis_client, session_id):
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=BAD_REQUEST)

    commands_key = Redis_Key_Prefix_Terminal_Commands + session_id
    redis_client.rpush(commands_key, json.dumps({'type': 'write', 'data': data}))

    return JsonResponse({'success': True})


@method_allowed('POST')
def terminal_resize(req):
    """ Resize a PTY session via Redis command queue. """
    try:
        body = json.loads(req.body)
        session_id = body.get('session_id', '')
        rows = body.get('rows', 24)
        cols = body.get('cols', 80)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=BAD_REQUEST)

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    redis_client = get_redis_client()

    if not _session_exists(redis_client, session_id):
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=BAD_REQUEST)

    commands_key = Redis_Key_Prefix_Terminal_Commands + session_id
    redis_client.rpush(commands_key, json.dumps({'type': 'resize', 'rows': rows, 'cols': cols}))

    return JsonResponse({'success': True})


@method_allowed('POST')
def terminal_close(req):
    """ Close a PTY session. """
    try:
        body = json.loads(req.body)
        session_id = body.get('session_id', '')
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=BAD_REQUEST)

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    redis_client = get_redis_client()

    commands_key = Redis_Key_Prefix_Terminal_Commands + session_id
    redis_client.rpush(commands_key, json.dumps({'type': 'close'}))

    with _local_sessions_lock:
        session = _local_sessions.pop(session_id, None)
        if session:
            session.close()

    _delete_session_metadata(redis_client, session_id)

    logger.info('[terminal] closed session %s', session_id)

    return JsonResponse({'success': True})


@method_allowed('GET')
def terminal_stream(req):
    """ Stream PTY output via SSE from Redis. """
    session_id = req.GET.get('session_id', '')

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    redis_client = get_redis_client()

    if not _session_exists(redis_client, session_id):
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=BAD_REQUEST)

    output_key = Redis_Key_Prefix_Terminal_Output + session_id

    def generate_events():
        logger.info('[terminal] SSE stream started for session %s', session_id)
        timeout_count = 0
        max_timeouts = 300

        try:
            while timeout_count < max_timeouts:
                result = redis_client.blpop(output_key, timeout=1)
                if result:
                    timeout_count = 0
                    _, data = result
                    if data == '\x00CLOSED\x00':
                        yield 'event: closed\ndata: {}\n\n'
                        break
                    payload = json.dumps({'output': data})
                    yield 'data: {}\n\n'.format(payload)
                else:
                    timeout_count += 1
                    yield ': keepalive\n\n'

        except GeneratorExit:
            logger.info('[terminal] SSE client disconnected for session %s', session_id)
        except Exception:
            error_msg = format_exc()
            logger.warning('[terminal] SSE error for session %s: %s', session_id, error_msg)

    response = StreamingHttpResponse(generate_events(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
