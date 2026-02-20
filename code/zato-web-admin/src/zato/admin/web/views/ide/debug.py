# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import uuid

# Redis
import redis

# Django
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse

logger = logging.getLogger(__name__)

Redis_Key_Prefix_Debug_Session = 'zato.ide.debug.session.'
Redis_Key_Prefix_Debug_Events = 'zato.ide.debug.events.'

def get_redis_client():
    return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class DAPClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.seq = 1
        self.pending_requests = {}
        self.running = False
        self.receive_thread = None
        self.event_callback = None
        self.lock = threading.Lock()
        self.buffer = b''

    def connect(self, timeout=5):
        logger.info('[DAPClient] Connecting to %s:%d', self.host, self.port)
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.running = True
                self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
                self.receive_thread.start()
                logger.info('[DAPClient] Connected')
                return True
            except ConnectionRefusedError:
                time.sleep(0.1)
            except Exception as e:
                logger.error('[DAPClient] Connection error: %s', e)
                time.sleep(0.1)
        logger.error('[DAPClient] Connection timeout')
        return False

    def disconnect(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None

    def send_request(self, command, arguments=None, callback=None):
        with self.lock:
            seq = self.seq
            self.seq += 1

        request = {
            'seq': seq,
            'type': 'request',
            'command': command,
            'arguments': arguments or {}
        }

        if callback:
            self.pending_requests[seq] = callback

        self._send_message(request)
        return seq

    def send_request_sync(self, command, arguments=None, timeout=30):
        event = threading.Event()
        result = {'response': None, 'error': None}

        def callback(response):
            logger.info('[DAPClient] send_request_sync callback for %s: success=%s', command, response.get('success'))
            if response.get('success'):
                result['response'] = response
            else:
                result['error'] = response.get('message', 'Request failed')
            event.set()

        self.send_request(command, arguments, callback)
        if not event.wait(timeout=timeout):
            logger.error('[DAPClient] send_request_sync timeout for %s after %d seconds', command, timeout)
            raise Exception(f'Timeout waiting for {command} response')

        if result['error']:
            raise Exception(result['error'])
        return result['response']

    def _send_message(self, message):
        content = json.dumps(message)
        content_bytes = content.encode('utf-8')
        header = f'Content-Length: {len(content_bytes)}\r\n\r\n'
        data = header.encode('utf-8') + content_bytes
        logger.info('[DAPClient] Sending: %s', message.get('command', message.get('type')))
        try:
            self.socket.sendall(data)
        except Exception as e:
            logger.error('[DAPClient] Send error: %s', e)

    def _receive_loop(self):
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                self.buffer += data
                self._process_buffer()
            except Exception as e:
                if self.running:
                    logger.error('[DAPClient] Receive error: %s', e)
                break
        self.running = False

    def _process_buffer(self):
        while True:
            header_end = self.buffer.find(b'\r\n\r\n')
            if header_end == -1:
                break

            header = self.buffer[:header_end].decode('utf-8')
            content_length = 0
            for line in header.split('\r\n'):
                if line.startswith('Content-Length:'):
                    content_length = int(line.split(':')[1].strip())
                    break

            if content_length == 0:
                break

            content_start = header_end + 4
            content_end = content_start + content_length

            if len(self.buffer) < content_end:
                break

            content = self.buffer[content_start:content_end].decode('utf-8')
            self.buffer = self.buffer[content_end:]

            try:
                message = json.loads(content)
                self._handle_message(message)
            except json.JSONDecodeError as e:
                logger.error('[DAPClient] JSON decode error: %s', e)

    def _handle_message(self, message):
        msg_type = message.get('type')
        logger.info('[DAPClient] Received: %s %s', msg_type, message.get('command', message.get('event', '')))

        if msg_type == 'response':
            seq = message.get('request_seq')
            callback = self.pending_requests.pop(seq, None)
            if callback:
                callback(message)
        elif msg_type == 'event':
            if self.event_callback:
                self.event_callback(message)


class DebugSession:

    def __init__(self, session_id, code, filename):
        self.session_id = session_id
        self.code = code
        self.filename = filename
        self.process = None
        self.debugpy_port = None
        self.dap_client = None
        self.state = 'idle'
        self.redis_client = get_redis_client()
        self.events_key = Redis_Key_Prefix_Debug_Events + session_id
        self.redis_client.delete(self.events_key)
        self.breakpoints = {}
        self.thread_id = None
        self.temp_file = None
        self.running = False
        self.initialized = False

    def start(self):
        logger.info('[DebugSession] Starting session %s', self.session_id)

        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            prefix='zato_debug_',
            delete=False
        )
        self.temp_file.write(self.code)
        self.temp_file.flush()
        self.temp_file.close()

        self.debugpy_port = 5678 + hash(self.session_id) % 1000

        wrapper_code = f'''
import debugpy
import runpy
debugpy.configure({{"python": "{sys.executable}"}})
debugpy.listen(("127.0.0.1", {self.debugpy_port}), in_process_debug_adapter=True)
debugpy.wait_for_client()
runpy.run_path("{self.temp_file.name}", run_name="__main__")
'''

        self.wrapper_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            prefix='zato_debug_wrapper_',
            delete=False
        )
        self.wrapper_file.write(wrapper_code)
        self.wrapper_file.flush()
        self.wrapper_file.close()

        cmd = [sys.executable, self.wrapper_file.name]

        logger.info('[DebugSession] Running wrapper with in_process_debug_adapter=True on port %d', self.debugpy_port)

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.running = True
        self.state = 'starting'

        self.dap_client = DAPClient('127.0.0.1', self.debugpy_port)
        self.dap_client.event_callback = self._handle_dap_event

        connected = False
        for attempt in range(30):
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                logger.error('[DebugSession] debugpy process exited, stdout=%s stderr=%s', stdout, stderr)
                return False

            try:
                self.dap_client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dap_client.socket.connect(('127.0.0.1', self.debugpy_port))
                self.dap_client.running = True
                self.dap_client.receive_thread = threading.Thread(target=self.dap_client._receive_loop, daemon=True)
                self.dap_client.receive_thread.start()
                logger.info('[DebugSession] Connected to debugpy on attempt %d', attempt + 1)
                connected = True
                break
            except ConnectionRefusedError:
                logger.info('[DebugSession] Connection attempt %d failed, retrying...', attempt + 1)
                time.sleep(0.2)
            except Exception as e:
                logger.error('[DebugSession] Connection error: %s', e)
                time.sleep(0.2)

        if not connected:
            logger.error('[DebugSession] Failed to connect to debugpy after 30 attempts')
            self.stop()
            return False

        try:
            self.dap_client.send_request_sync('initialize', {
                'clientID': 'zato-ide',
                'clientName': 'Zato IDE',
                'adapterID': 'python',
                'pathFormat': 'path',
                'linesStartAt1': True,
                'columnsStartAt1': True,
                'supportsVariableType': True,
                'supportsVariablePaging': False,
                'supportsRunInTerminalRequest': False,
                'locale': 'en-us'
            })
        except Exception as e:
            logger.error('[DebugSession] Initialize failed: %s', e)
            self.stop()
            return False

        try:
            self.dap_client.send_request_sync('attach', {
                'justMyCode': True,
                'subProcess': False
            })
        except Exception as e:
            logger.error('[DebugSession] Attach failed: %s', e)
            self.stop()
            return False

        self.state = 'running'
        self.initialized = True

        return True

    def _handle_dap_event(self, event):
        event_name = event.get('event')
        body = event.get('body', {})
        logger.info('[DebugSession] DAP event: %s', event_name)

        if event_name == 'stopped':
            self.thread_id = body.get('threadId', 1)
            self.state = 'paused'
            self._send_event('stopped', body)
        elif event_name == 'continued':
            self.state = 'running'
            self._send_event('continued', body)
        elif event_name == 'terminated':
            self.state = 'stopped'
            if self.process:
                try:
                    stdout, stderr = self.process.communicate(timeout=1)
                    if stdout:
                        logger.info('[DebugSession] Process stdout: %s', stdout[:500])
                    if stderr:
                        logger.info('[DebugSession] Process stderr: %s', stderr[:500])
                except Exception:
                    pass
            self._send_event('terminated', body)
        elif event_name == 'output':
            self._send_event('output', body)
        elif event_name == 'thread':
            pass
        elif event_name == 'initialized':
            self._send_event('initialized', body)
        elif event_name == 'process':
            pass

    def stop(self):
        logger.info('[DebugSession] Stopping session %s', self.session_id)
        self.running = False

        if self.dap_client:
            try:
                self.dap_client.send_request('disconnect', {'terminateDebuggee': True})
            except Exception:
                pass
            self.dap_client.disconnect()
            self.dap_client = None

        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

        if self.temp_file:
            import os
            try:
                os.unlink(self.temp_file.name)
            except Exception:
                pass

        self.state = 'stopped'
        self._send_event('terminated', {})

    def _send_event(self, event_type, body):
        event = {
            'type': 'event',
            'event': event_type,
            'body': body
        }
        logger.info('[DebugSession] Sending event to Redis: %s', event_type)
        self.redis_client.rpush(self.events_key, json.dumps(event))
        self.redis_client.expire(self.events_key, 3600)

    def get_events(self, timeout=1):
        events = []
        result = self.redis_client.blpop(self.events_key, timeout=timeout)
        if result:
            _, event_data = result
            events.append(json.loads(event_data))
            while True:
                event_data = self.redis_client.lpop(self.events_key)
                if not event_data:
                    break
                events.append(json.loads(event_data))
        return events

    def handle_command(self, command, arguments):
        logger.info('[DebugSession] Command: %s args: %s', command, arguments)
        logger.info('[DebugSession] state=%s initialized=%s dap_client=%s', self.state, self.initialized, self.dap_client is not None)

        if command == 'initialize':
            return self._cmd_initialize(arguments)

        if not self.dap_client or not self.dap_client.running:
            logger.error('[DebugSession] Not connected to debugger, dap_client=%s running=%s',
                        self.dap_client is not None,
                        self.dap_client.running if self.dap_client else 'N/A')
            return {'success': False, 'message': 'Not connected to debugger'}

        handler = getattr(self, f'_cmd_{command}', None)
        if handler:
            logger.info('[DebugSession] Calling handler for %s', command)
            return handler(arguments)

        logger.error('[DebugSession] Unknown command: %s', command)
        return {'success': False, 'message': f'Unknown command: {command}'}

    def _cmd_initialize(self, args):
        return {
            'success': True,
            'body': {
                'supportsConfigurationDoneRequest': True,
                'supportsConditionalBreakpoints': True,
                'supportsEvaluateForHovers': True,
                'supportsSetVariable': True,
                'supportTerminateDebuggee': True,
                'supportsTerminateRequest': True,
            }
        }

    def _cmd_configurationDone(self, args):
        try:
            self.dap_client.send_request_sync('configurationDone', {})
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_launch(self, args):
        try:
            self.dap_client.send_request_sync('launch', {
                'program': self.temp_file.name,
                'stopOnEntry': True,
                'justMyCode': True
            })
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_setBreakpoints(self, args):
        source = args.get('source', {})
        breakpoints = args.get('breakpoints', [])

        source_path = source.get('path', '')
        logger.info('[DebugSession] setBreakpoints: source_path=%s filename=%s temp_file=%s',
                    source_path, self.filename, self.temp_file.name if self.temp_file else None)

        if source_path == self.filename and self.temp_file:
            source['path'] = self.temp_file.name
            logger.info('[DebugSession] setBreakpoints: mapped to temp_file=%s', self.temp_file.name)

        try:
            response = self.dap_client.send_request_sync('setBreakpoints', {
                'source': source,
                'breakpoints': breakpoints,
                'sourceModified': False
            })
            logger.info('[DebugSession] setBreakpoints: response=%s', response)
            return {'success': True, 'body': response.get('body', {})}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_threads(self, args):
        try:
            response = self.dap_client.send_request_sync('threads', {})
            return {'success': True, 'body': response.get('body', {})}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_stackTrace(self, args):
        try:
            response = self.dap_client.send_request_sync('stackTrace', args)
            body = response.get('body', {})
            frames = body.get('stackFrames', [])
            for frame in frames:
                source = frame.get('source', {})
                if source.get('path') == self.temp_file.name:
                    source['path'] = self.filename
            return {'success': True, 'body': body}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_scopes(self, args):
        try:
            response = self.dap_client.send_request_sync('scopes', args)
            return {'success': True, 'body': response.get('body', {})}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_variables(self, args):
        try:
            response = self.dap_client.send_request_sync('variables', args)
            return {'success': True, 'body': response.get('body', {})}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_continue(self, args):
        try:
            response = self.dap_client.send_request_sync('continue', args)
            return {'success': True, 'body': response.get('body', {})}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_next(self, args):
        try:
            response = self.dap_client.send_request_sync('next', args)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_stepIn(self, args):
        try:
            response = self.dap_client.send_request_sync('stepIn', args)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_stepOut(self, args):
        try:
            response = self.dap_client.send_request_sync('stepOut', args)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_pause(self, args):
        try:
            response = self.dap_client.send_request_sync('pause', args)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_evaluate(self, args):
        try:
            response = self.dap_client.send_request_sync('evaluate', args)
            return {'success': True, 'body': response.get('body', {})}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _cmd_disconnect(self, args):
        self.stop()
        return {'success': True}


_local_sessions = {}
_local_sessions_lock = threading.Lock()

class DebugSessionManager:

    def __init__(self):
        self.redis_client = get_redis_client()

    def create_session(self, code, filename):
        session_id = str(uuid.uuid4())
        session = DebugSession(session_id, code, filename)
        self._store_session(session)
        return session

    def get_session(self, session_id):
        with _local_sessions_lock:
            if session_id in _local_sessions:
                return _local_sessions[session_id]

        session_key = Redis_Key_Prefix_Debug_Session + session_id
        session_data = self.redis_client.get(session_key)
        if session_data:
            data = json.loads(session_data)
            session = DebugSession(session_id, data.get('code', ''), data.get('filename', 'untitled.py'))
            session.state = data.get('state', 'idle')
            session.breakpoints = data.get('breakpoints', {})
            with _local_sessions_lock:
                _local_sessions[session_id] = session
            return session
        return None

    def get_or_create_session(self, session_id):
        session = self.get_session(session_id)
        if not session:
            session = DebugSession(session_id, '', 'untitled.py')
            self._store_session(session)
        return session

    def _store_session(self, session):
        with _local_sessions_lock:
            _local_sessions[session.session_id] = session
        session_key = Redis_Key_Prefix_Debug_Session + session.session_id
        session_data = {
            'code': session.code,
            'filename': session.filename,
            'state': session.state,
            'breakpoints': session.breakpoints
        }
        self.redis_client.set(session_key, json.dumps(session_data))
        self.redis_client.expire(session_key, 3600)

    def update_session(self, session):
        self._store_session(session)

    def remove_session(self, session_id):
        with _local_sessions_lock:
            session = _local_sessions.pop(session_id, None)
        session_key = Redis_Key_Prefix_Debug_Session + session_id
        self.redis_client.delete(session_key)
        events_key = Redis_Key_Prefix_Debug_Events + session_id
        self.redis_client.delete(events_key)
        if session:
            session.stop()
        return session


def debug_sse(request):
    session_id = request.GET.get('session_id')
    logger.info('[debug_sse] SSE request for session_id=%s', session_id)

    if not session_id:
        return HttpResponse('Missing session_id', status=400)

    manager = DebugSessionManager()
    session = manager.get_or_create_session(session_id)
    logger.info('[debug_sse] Session ready for session_id=%s', session_id)

    def event_stream():
        yield 'data: {"type": "event", "event": "connected", "body": {}}\n\n'

        timeout_count = 0
        max_timeouts = 300

        while timeout_count < max_timeouts:
            events = session.get_events(timeout=1)
            if events:
                timeout_count = 0
                for event in events:
                    logger.info('[debug_sse] Sending event: %s', event.get('event'))
                    yield f'data: {json.dumps(event)}\n\n'
            else:
                timeout_count += 1
                yield ': keepalive\n\n'

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def debug_command(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_id = data.get('session_id')
    command = data.get('command')
    arguments = data.get('arguments', {})
    seq = data.get('seq', 0)

    logger.info('[debug_command] session_id=%s command=%s', session_id, command)

    if not session_id:
        return JsonResponse({'error': 'Missing session_id'}, status=400)

    if not command:
        return JsonResponse({'error': 'Missing command'}, status=400)

    manager = DebugSessionManager()
    session = manager.get_session(session_id)

    if not session:
        session = manager.get_or_create_session(session_id)

    if command == 'launch':
        code = arguments.get('code', '')
        filename = arguments.get('program', 'untitled.py')
        logger.info('[debug_command] launch: code.length=%d filename=%s', len(code), filename)
        session.code = code
        session.filename = filename
        if code:
            session.start()
            manager.update_session(session)
            logger.info('[debug_command] launch: session started')
            result = {'success': True}
        else:
            result = {'success': False, 'message': 'No code provided'}
    else:
        result = session.handle_command(command, arguments)
        manager.update_session(session)

    response = {
        'type': 'response',
        'request_seq': seq,
        'success': result.get('success', True),
        'command': command,
        'body': result.get('body', {})
    }

    if 'message' in result:
        response['message'] = result['message']

    return JsonResponse(response)
