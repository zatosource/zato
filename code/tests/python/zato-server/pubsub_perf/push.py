# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import errno
import json
import time
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socket import SHUT_RDWR, socket
from threading import Lock, Thread

# Zato
from zato.common.test.reservation import PortInUse, start_on_reserved_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import PortReservation
    from zato.common.typing_ import any_, strfloatdict, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The address the receiver listens on, on a reserved port of this purpose
Push_Host = '127.0.0.1'
_port_purpose = 'pubsub-perf-push-receiver'

# The headers of a push that identify the message and its attempt, and the key of the envelope with the payload
_header_msg_id = 'X-Zato-Msg-ID'
_header_delivery_attempt = 'X-Zato-Delivery-Attempt'
_header_content_length = 'Content-Length'
_payload_key = 'data'

# The path under which the receiver accepts the pushes of each push subscriber
_path_prefix = '/perf/push/'

# The separator of the parts of a key, the run prefix being everything before its last two parts
_key_separator = '.'
_key_suffix_parts = 2

# ################################################################################################################################
# ################################################################################################################################

pushrecordsdict = dict[str, 'PushRecords']
socketset       = set[socket]
runcountsdict   = dict[str, 'RunCounts']

# ################################################################################################################################
# ################################################################################################################################

def get_push_path(index:'int') -> 'str':
    """ Returns the path under which the receiver accepts the pushes of the push subscriber of the given index.
    """
    out = f'{_path_prefix}{index:02d}'
    return out

# ################################################################################################################################

def _get_run_prefix(key:'str') -> 'str':
    """ Returns the prefix of the run that a key of a message belongs to.
    """
    parts = key.rsplit(_key_separator, _key_suffix_parts)
    run_part = parts[0]

    out = run_part + _key_separator
    return out

# ################################################################################################################################
# ################################################################################################################################

class RunCounts:
    """ The counts of the pushes of one run to one push subscriber - its distinct keys, its pushes with an attempt
    above the first one and its pushes whose message ID is not their key.
    """

    def __init__(self) -> 'None':
        self.distinct_count = 0
        self.retried_count = 0
        self.mismatch_count = 0

# ################################################################################################################################
# ################################################################################################################################

class PushRecords:
    """ The pushes that one push subscriber received - the first receive time of each key, how many pushes
    each key had and the counts of each run.
    """

    def __init__(self) -> 'None':
        self.lock = Lock()

        self.first_times:'strfloatdict' = {}
        self.push_counts:'strintdict' = {}
        self.run_counts:'runcountsdict' = {}

# ################################################################################################################################

    def add(self, msg_id:'str', attempt:'int', key:'str', received_at:'float') -> 'None':
        """ Records one push.
        """
        prefix = _get_run_prefix(key)

        with self.lock:

            # Each run has counts of its own ..
            if not (run_counts := self.run_counts.get(prefix)):
                run_counts = RunCounts()
                self.run_counts[prefix] = run_counts

            # .. a push whose message ID is not its key is counted as a mismatch ..
            if msg_id != key:
                run_counts.mismatch_count += 1

            # .. one above the first attempt is counted as retried ..
            if attempt > 1:
                run_counts.retried_count += 1

            # .. and the first push of each key is the time of its receipt.
            if key in self.push_counts:
                self.push_counts[key] += 1
            else:
                self.push_counts[key] = 1
                self.first_times[key] = received_at
                run_counts.distinct_count += 1

# ################################################################################################################################

    def get_run_counts(self, prefix:'str') -> 'RunCounts':
        """ Returns the counts of the run of the given prefix, which are all zero before its first push.
        """
        with self.lock:
            if not (out := self.run_counts.get(prefix)):
                out = RunCounts()

        return out

# ################################################################################################################################

    def get_run_keys(self, prefix:'str') -> 'strlist':
        """ Returns the distinct keys of the run of the given prefix that were pushed.
        """
        out:'strlist' = []

        with self.lock:
            for key in self.push_counts:
                if key.startswith(prefix):
                    out.append(key)

        return out

# ################################################################################################################################

    def count_repeated(self, prefix:'str') -> 'int':
        """ Returns how many pushes of keys of the run of the given prefix repeated a push of their key.
        """
        out = 0

        with self.lock:
            for key, push_count in self.push_counts.items():
                if key.startswith(prefix):
                    out += push_count - 1

        return out

# ################################################################################################################################

    def get_first_times(self, prefix:'str') -> 'strfloatdict':
        """ Returns the first receive time of each key of the run of the given prefix.
        """
        out:'strfloatdict' = {}

        with self.lock:
            for key, received_at in self.first_times.items():
                if key.startswith(prefix):
                    out[key] = received_at

        return out

# ################################################################################################################################
# ################################################################################################################################

class _PushServer(ThreadingHTTPServer):
    """ The HTTP server of the receiver, with the records of each path and the connections it serves.
    """
    daemon_threads = True
    records_by_path: 'pushrecordsdict'
    connections: 'socketset'
    connections_lock: 'Lock'

    def finish_request(self, request:'any_', client_address:'any_') -> 'None':
        """ Serves one connection in its own thread, keeping it among the open connections until it is closed.
        """
        with self.connections_lock:
            self.connections.add(request)

        try:
            super().finish_request(request, client_address)
        finally:
            with self.connections_lock:
                self.connections.discard(request)

# ################################################################################################################################
# ################################################################################################################################

class _PushHandler(BaseHTTPRequestHandler):
    """ Records each push under its path and confirms it, keeping the connection open for the next push.
    """
    protocol_version = 'HTTP/1.1'
    server: '_PushServer'

    def log_message(self, format:'str', *args:'any_') -> 'None': # noqa: A002
        pass

# ################################################################################################################################

    def do_POST(self) -> 'None': # noqa: N802

        received_at = time.monotonic()

        # The body is read whole, so that the connection is ready for the next push ..
        content_length = int(self.headers[_header_content_length])
        body = self.rfile.read(content_length)

        msg_id = self.headers[_header_msg_id]
        attempt = int(self.headers[_header_delivery_attempt])

        # .. the payload is a JSON document inside the envelope ..
        envelope = json.loads(body)
        data = json.loads(envelope[_payload_key])

        # .. the push is recorded under the subscriber of its path ..
        records = self.server.records_by_path[self.path]
        records.add(msg_id, attempt, data['key'], received_at)

        # .. and confirmed.
        self.send_response(OK)
        self.send_header(_header_content_length, '0')
        self.end_headers()

# ################################################################################################################################
# ################################################################################################################################

class PushReceiver:
    """ The endpoint that the server pushes the messages of every push subscriber to, one path per subscriber.
    """

    def __init__(self, subscriber_count:'int') -> 'None':

        records_by_path:'pushrecordsdict' = {}

        for index in range(subscriber_count):
            path = get_push_path(index)
            records_by_path[path] = PushRecords()

        self.records_by_path = records_by_path

        # The server and its thread exist once the receiver starts on its reserved port
        self.server:'_PushServer'
        self.thread:'Thread'
        self.reservation:'PortReservation'
        self.port:'int'

# ################################################################################################################################

    def _start_on_port(self, port:'int') -> 'None':
        """ Starts the server on the port, raising PortInUse if another process took the port before it was bound.
        """
        try:
            server = _PushServer((Push_Host, port), _PushHandler)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                raise PortInUse(f'Port {port} of the push receiver is in use') from e
            raise

        server.records_by_path = self.records_by_path
        server.connections = set()
        server.connections_lock = Lock()

        self.server = server
        self.port = port

        self.thread = Thread(target=server.serve_forever, name='pubsub-perf-push-receiver', daemon=True)
        self.thread.start()

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the server on a reserved port.
        """
        started = start_on_reserved_port(_port_purpose, self._start_on_port)
        self.reservation = started.reservation

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and releases its port.
        """
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.reservation.release()

# ################################################################################################################################

    def close_connections(self) -> 'None':
        """ Shuts down the connections that the server keeps open between pushes, so that the thread serving each of them
        ends with the test. The next push opens a new connection.
        """
        with self.server.connections_lock:
            connections = list(self.server.connections)

        for connection in connections:
            connection.shutdown(SHUT_RDWR)

# ################################################################################################################################

    def get_records(self, index:'int') -> 'PushRecords':
        """ Returns the records of the push subscriber of the given index.
        """
        path = get_push_path(index)

        out = self.records_by_path[path]
        return out

# ################################################################################################################################
# ################################################################################################################################
