# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import pty
import select
import signal
import struct
import fcntl
import termios
import time
import uuid
from http.client import BAD_REQUEST
from traceback import format_exc

# Django
from django.http import JsonResponse, StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed

import logging
logger = logging.getLogger(__name__)

pty_sessions = {}

class PTYSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.master_fd = None
        self.pid = None
        self.alive = True

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

    def resize(self, rows, cols):
        if self.master_fd is not None:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def write(self, data):
        if self.master_fd is not None and self.alive:
            os.write(self.master_fd, data.encode('utf-8'))

    def read(self):
        if self.master_fd is None or not self.alive:
            return None

        try:
            ready, _, _ = select.select([self.master_fd], [], [], 0.05)
            if ready:
                data = os.read(self.master_fd, 4096)
                if data:
                    return data.decode('utf-8', errors='replace')
        except OSError:
            self.alive = False
            return None

        return ''

    def close(self):
        self.alive = False
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
    pty_sessions[session_id] = session

    logger.info('[terminal] created session %s with rows=%s, cols=%s', session_id, rows, cols)

    return JsonResponse({'success': True, 'session_id': session_id})

@method_allowed('POST')
def terminal_write(req):
    """ Write data to a PTY session. """
    try:
        body = json.loads(req.body)
        session_id = body.get('session_id', '')
        data = body.get('data', '')
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=BAD_REQUEST)

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    session = pty_sessions.get(session_id)
    if not session:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=BAD_REQUEST)

    if not session.alive:
        return JsonResponse({'success': False, 'error': 'Session closed'}, status=BAD_REQUEST)

    session.write(data)

    return JsonResponse({'success': True})

@method_allowed('POST')
def terminal_resize(req):
    """ Resize a PTY session. """
    try:
        body = json.loads(req.body)
        session_id = body.get('session_id', '')
        rows = body.get('rows', 24)
        cols = body.get('cols', 80)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid request body'}, status=BAD_REQUEST)

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    session = pty_sessions.get(session_id)
    if not session:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=BAD_REQUEST)

    session.resize(rows, cols)

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

    session = pty_sessions.pop(session_id, None)
    if session:
        session.close()
        logger.info('[terminal] closed session %s', session_id)

    return JsonResponse({'success': True})

@method_allowed('GET')
def terminal_stream(req):
    """ Stream PTY output via SSE. """
    session_id = req.GET.get('session_id', '')

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Missing session_id'}, status=BAD_REQUEST)

    session = pty_sessions.get(session_id)
    if not session:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=BAD_REQUEST)

    def generate_events():
        logger.info('[terminal] SSE stream started for session %s', session_id)
        try:
            while session.alive:
                data = session.read()
                if data is None:
                    yield 'event: closed\ndata: {}\n\n'
                    break
                elif data:
                    payload = json.dumps({'output': data})
                    yield 'data: {}\n\n'.format(payload)
                else:
                    yield ': keepalive\n\n'
                time.sleep(0.02)

        except GeneratorExit:
            logger.info('[terminal] SSE client disconnected for session %s', session_id)
        except Exception:
            error_msg = format_exc()
            logger.warning('[terminal] SSE error for session %s: %s', session_id, error_msg)

    response = StreamingHttpResponse(generate_events(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
