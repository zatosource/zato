# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import re
import socket
import ssl
from traceback import format_exc

# gevent
from gevent import spawn
from gevent.event import Event
from gevent.lock import RLock
from gevent.queue import Queue

# Zato
from zato.common.typing_ import any_, anydict, anydictnone, callable_, callnone, floatnone, strnone

# Local
from .const import CRLF, CRLF_LEN, CONNECT_OP, Default_Buffer_Size, Default_Host, Default_Inbox_Prefix, \
     Default_Max_Payload, Default_Port, Default_Timeout, ERR_OP, INFO_OP, NATS_HDR_Line, NATS_HDR_Line_Size, \
     OK_OP, PING_CMD, PING_OP, PONG_CMD, PONG_OP, SPC, Status_No_Responders
from .exc import NATSConnectionError, NATSError, NATSNoRespondersError, NATSProtocolError, NATSTimeoutError
from .model import ConnectOptions, Msg, ServerInfo
from .nuid import NUID
from .sub import Subscription

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Regular expressions for parsing protocol messages
MSG_RE = re.compile(rb'^MSG\s+([^\s]+)\s+([^\s]+)\s+(([^\s]+)\s+)?(\d+)\r\n')
HMSG_RE = re.compile(rb'^HMSG\s+([^\s]+)\s+([^\s]+)\s+(([^\s]+)\s+)?(\d+)\s+(\d+)\r\n')

# ################################################################################################################################
# ################################################################################################################################

class NATSClient:
    """ Synchronous TCP NATS client.
    """
    def __init__(self) -> None:
        self._sock: 'socket.socket | None' = None
        self._ssl_context: 'ssl.SSLContext | None' = None
        self._server_info: 'ServerInfo | None' = None
        self._options: 'ConnectOptions | None' = None
        self._read_buffer = bytearray()
        self._nuid = NUID()

        self._sid = 0
        self._subscriptions: 'anydict' = {}
        self._pending_msgs: 'anydict' = {}
        self._resp_map: 'anydict' = {}
        self._resp_sub_prefix: 'bytearray | None' = None

        self._max_payload = Default_Max_Payload
        self._connected = False
        self._lock = RLock()
        self._write_lock = RLock()
        self._msg_queues: 'anydict' = {}  # sid -> Queue for multiplexing
        self._reader_greenlet = None

        self._host = Default_Host
        self._port = Default_Port
        self._timeout = Default_Timeout

    # ############################################################################################################################

    @property
    def is_connected(self) -> 'bool':
        return self._connected

    @property
    def server_info(self) -> 'ServerInfo | None':
        return self._server_info

    @property
    def max_payload(self) -> 'int':
        return self._max_payload

    # ############################################################################################################################

    def connect(
        self,
        host:'str'=Default_Host,
        port:'int'=Default_Port,
        timeout:'float'=Default_Timeout,
        name:'strnone'=None,
        user:'strnone'=None,
        password:'strnone'=None,
        token:'strnone'=None,
        verbose:'bool'=False,
        pedantic:'bool'=False,
        ssl_context:'ssl.SSLContext | None'=None,
        connect_timeout:'floatnone'=None,
    ) -> None:
        """ Connects to a NATS server.
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._ssl_context = ssl_context

        connect_timeout = connect_timeout or timeout

        # Create socket
        self._sock = socket.create_connection((host, port), timeout=connect_timeout)
        self._sock.settimeout(timeout)

        # Read INFO from server
        info_line = self._read_line()
        if not info_line.startswith(INFO_OP):
            raise NATSProtocolError(f'Expected INFO, got: {info_line!r}')

        info_json = info_line[len(INFO_OP) + 1:].strip()
        info_json = info_json.decode('utf-8')
        info_data = json.loads(info_json)
        self._server_info = ServerInfo.from_dict(info_data)
        self._max_payload = self._server_info.max_payload

        # Upgrade to TLS if required
        if self._server_info.tls_required or ssl_context:
            if ssl_context is None:
                ssl_context = ssl.create_default_context()
            self._sock = ssl_context.wrap_socket(self._sock, server_hostname=host)
            self._sock.settimeout(timeout)

        # Build CONNECT options
        self._options = ConnectOptions(
            verbose=verbose,
            pedantic=pedantic,
            name=name,
            headers=self._server_info.headers,
            no_responders=self._server_info.headers,
        )

        if user and password:
            self._options.user = user
            self._options.password = password
        elif token:
            self._options.auth_token = token

        # Send CONNECT
        connect_data = json.dumps(self._options.to_dict())
        connect_data = connect_data.encode('utf-8')
        connect_cmd = CONNECT_OP + SPC + connect_data + CRLF
        self._send(connect_cmd)

        # Send PING and wait for PONG to confirm connection
        self._send(PING_CMD)

        # Read response (may be +OK if verbose, then PONG)
        while True:
            line = self._read_line()
            if line.startswith(PONG_OP):
                break
            elif line.startswith(OK_OP):
                continue
            elif line.startswith(ERR_OP):
                err_msg = line[len(ERR_OP):].strip()
                err_msg = err_msg.decode('utf-8')
                raise NATSConnectionError(f'Server error: {err_msg}')
            else:
                raise NATSProtocolError(f'Unexpected response: {line!r}')

        self._connected = True
        self._reader_greenlet = spawn(self._reader_loop)
        logger.info(f'Connected to NATS server at {host}:{port}')

    # ############################################################################################################################

    def close(self) -> None:
        """ Closes the connection.
        """
        self._connected = False
        if self._reader_greenlet:
            self._reader_greenlet.kill()
            self._reader_greenlet = None
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        self._subscriptions.clear()
        self._pending_msgs.clear()
        self._msg_queues.clear()
        logger.info('Disconnected from NATS server')

    # ############################################################################################################################

    def _reader_loop(self) -> None:
        """ Background greenlet that reads messages and routes them to queues.
        """
        while self._connected:
            try:
                msg = self._read_msg()
                if msg is None:
                    continue
                sid = msg.sid
                if sid in self._msg_queues:
                    self._msg_queues[sid].put(msg)
                elif sid in self._subscriptions:
                    # Store in pending for next_msg calls
                    if sid not in self._pending_msgs:
                        self._pending_msgs[sid] = []
                    self._pending_msgs[sid].append(msg)
            except NATSTimeoutError:
                continue
            except NATSConnectionError:
                break
            except Exception:
                logger.error(f'Reader error: {format_exc()}')
                break

    # ############################################################################################################################

    def _send(self, data:'bytes') -> None:
        if not self._sock:
            raise NATSConnectionError('Not connected')
        with self._write_lock:
            try:
                self._sock.sendall(data)
            except socket.error as e:
                self._connected = False
                raise NATSConnectionError(f'Send failed: {e}') from e

    # ############################################################################################################################

    def _fill_buffer(self) -> None:
        """ Fills the read buffer from the socket.
        """
        try:
            chunk = self._sock.recv(Default_Buffer_Size)
            if not chunk:
                raise NATSConnectionError('Connection closed by server')
            self._read_buffer.extend(chunk)
        except socket.timeout:
            raise NATSTimeoutError('Read timeout')
        except socket.error as e:
            self._connected = False
            raise NATSConnectionError(f'Read failed: {e}') from e

    # ############################################################################################################################

    def _read_line(self) -> 'bytes':
        if not self._sock:
            raise NATSConnectionError('Not connected')

        while True:
            # Check if we have a complete line in buffer
            idx = self._read_buffer.find(CRLF)
            if idx >= 0:
                line = bytes(self._read_buffer[:idx + CRLF_LEN])
                del self._read_buffer[:idx + CRLF_LEN]
                return line

            # Need more data
            self._fill_buffer()

    # ############################################################################################################################

    def _read_bytes(self, n:'int') -> 'bytes':
        if not self._sock:
            raise NATSConnectionError('Not connected')

        while len(self._read_buffer) < n:
            self._fill_buffer()

        data = bytes(self._read_buffer[:n])
        del self._read_buffer[:n]
        return data

    # ############################################################################################################################

    def publish(
        self,
        subject:'str',
        payload:'bytes'=b'',
        reply:'str'='',
        headers:'anydictnone'=None,
    ) -> None:
        if not self._connected:
            raise NATSConnectionError('Not connected')

        payload_size = len(payload)
        if payload_size > self._max_payload:
            raise NATSError(f'Payload too large: {payload_size} > {self._max_payload}')

        if headers:
            # HPUB with headers
            hdr = bytearray(NATS_HDR_Line)
            hdr.extend(CRLF)
            for key, value in headers.items():
                hdr.extend(key.encode('utf-8'))
                hdr.extend(b': ')
                hdr.extend(str(value).encode('utf-8'))
                hdr.extend(CRLF)
            hdr.extend(CRLF)

            hdr_len = len(hdr)
            total_len = hdr_len + payload_size

            if reply:
                cmd = f'HPUB {subject} {reply} {hdr_len} {total_len}\r\n'.encode('utf-8')
            else:
                cmd = f'HPUB {subject} {hdr_len} {total_len}\r\n'.encode('utf-8')

            self._send(cmd + bytes(hdr) + payload + CRLF)
        else:
            # PUB without headers
            if reply:
                cmd = f'PUB {subject} {reply} {payload_size}\r\n'.encode('utf-8')
            else:
                cmd = f'PUB {subject} {payload_size}\r\n'.encode('utf-8')

            self._send(cmd + payload + CRLF)

    # ############################################################################################################################

    def subscribe(
        self,
        subject:'str',
        queue:'str'='',
        callback:'callnone'=None,
        max_msgs:'int'=0,
    ) -> 'Subscription':
        if not self._connected:
            raise NATSConnectionError('Not connected')

        self._sid += 1
        sid = self._sid

        sub = Subscription(self, sid, subject, queue, callback, max_msgs)
        self._subscriptions[sid] = sub
        self._pending_msgs[sid] = []
        self._msg_queues[sid] = Queue()

        if queue:
            cmd = f'SUB {subject} {queue} {sid}\r\n'.encode('utf-8')
        else:
            cmd = f'SUB {subject} {sid}\r\n'.encode('utf-8')

        self._send(cmd)

        if max_msgs > 0:
            self._send_unsubscribe(sid, max_msgs)

        return sub

    # ############################################################################################################################

    def _send_unsubscribe(self, sid:'int', max_msgs:'int'=0) -> None:
        if max_msgs > 0:
            cmd = f'UNSUB {sid} {max_msgs}\r\n'.encode('utf-8')
        else:
            cmd = f'UNSUB {sid}\r\n'.encode('utf-8')
        self._send(cmd)

    # ############################################################################################################################

    def _remove_subscription(self, sid:'int') -> None:
        self._subscriptions.pop(sid, None)
        self._pending_msgs.pop(sid, None)
        self._msg_queues.pop(sid, None)

    # ############################################################################################################################

    def new_inbox(self) -> 'str':
        """ Generates a new unique inbox subject.
        """
        inbox = bytearray(Default_Inbox_Prefix)
        inbox.extend(b'.')
        inbox.extend(self._nuid.next())
        return inbox.decode('utf-8')

    # ############################################################################################################################

    def request(
        self,
        subject:'str',
        payload:'bytes'=b'',
        timeout:'floatnone'=None,
        headers:'anydictnone'=None,
    ) -> 'Msg':
        """ Sends a request and waits for a response.
        """
        if timeout is None:
            timeout = self._timeout

        inbox = self.new_inbox()
        sub = self.subscribe(inbox, max_msgs=1)

        try:
            self.publish(subject, payload, reply=inbox, headers=headers)
            msg = sub.next_msg(timeout=timeout)

            # Check for no responders
            if msg.headers:
                status = msg.headers.get('Status')
                if status == Status_No_Responders:
                    raise NATSNoRespondersError('No responders available')

            return msg
        finally:
            try:
                sub.unsubscribe()
            except Exception:
                pass

    # ############################################################################################################################

    def _wait_for_msg(self, sid:'int', timeout:'floatnone'=None) -> 'Msg':
        if timeout is None:
            timeout = self._timeout

        if not self._connected:
            raise NATSConnectionError('Not connected')

        q = self._msg_queues.get(sid)
        if not q:
            raise NATSError(f'No queue for subscription {sid}')

        try:
            msg = q.get(timeout=timeout)
            sub = self._subscriptions.get(sid)
            if sub:
                sub._received += 1
            return msg
        except Exception:
            raise NATSTimeoutError('Timeout waiting for message')

    # ############################################################################################################################

    def _read_msg(self) -> 'Msg | None':
        line = self._read_line()

        # Handle INFO (server may send updated info at any time)
        if line.startswith(INFO_OP):
            return None

        # Handle PING
        if line.startswith(PING_OP):
            self._send(PONG_CMD)
            return None

        # Handle PONG
        if line.startswith(PONG_OP):
            return None

        # Handle +OK
        if line.startswith(OK_OP):
            return None

        # Handle -ERR
        if line.startswith(ERR_OP):
            err_msg = line[len(ERR_OP):].strip()
            err_msg = err_msg.decode('utf-8')
            raise NATSProtocolError(f'Server error: {err_msg}')

        # Handle MSG
        match = MSG_RE.match(line)
        if match:
            subject = match.group(1)
            subject = subject.decode('utf-8')
            sid = match.group(2)
            sid = int(sid)
            reply = match.group(4)
            reply = reply.decode('utf-8') if reply else ''
            payload_size = match.group(5)
            payload_size = int(payload_size)

            payload = self._read_bytes(payload_size)
            _ = self._read_bytes(CRLF_LEN)  # Read trailing CRLF

            return Msg(subject=subject, reply=reply, data=payload, sid=sid)

        # Handle HMSG (with headers)
        match = HMSG_RE.match(line)
        if match:
            subject = match.group(1)
            subject = subject.decode('utf-8')
            sid = match.group(2)
            sid = int(sid)
            reply = match.group(4)
            reply = reply.decode('utf-8') if reply else ''
            hdr_size = match.group(5)
            hdr_size = int(hdr_size)
            total_size = match.group(6)
            total_size = int(total_size)

            total_data = self._read_bytes(total_size)
            _ = self._read_bytes(CRLF_LEN)  # Read trailing CRLF

            hdr_data = total_data[:hdr_size]
            payload = total_data[hdr_size:]

            headers = self._parse_headers(hdr_data)

            return Msg(subject=subject, reply=reply, data=payload, headers=headers, sid=sid)

        # Unknown protocol
        raise NATSProtocolError(f'Unknown protocol line: {line!r}')

    # ############################################################################################################################

    def _parse_headers(self, hdr_data:'bytes') -> 'anydict':
        headers = {}
        lines = hdr_data.split(CRLF)

        if not lines:
            return headers

        # First line is NATS/1.0 [status [description]]
        first_line = lines[0]
        if first_line.startswith(NATS_HDR_Line):
            rest = first_line[NATS_HDR_Line_Size:].strip()
            if rest:
                parts = rest.split(b' ', 1)
                status = parts[0].decode('utf-8')
                headers['Status'] = status
                if len(parts) > 1:
                    headers['Description'] = parts[1].decode('utf-8')

        # Parse remaining headers
        for line in lines[1:]:
            if not line or line == b'':
                continue
            if b':' in line:
                key, value = line.split(b':', 1)
                key = key.decode('utf-8')
                key = key.strip()
                value = value.decode('utf-8')
                value = value.strip()
                headers[key] = value

        return headers

    # ############################################################################################################################

    def flush(self, timeout:'floatnone'=None) -> None:
        """ Flushes pending data to the server.
        """
        if timeout is None:
            timeout = self._timeout

        if not self._sock:
            raise NATSConnectionError('Not connected')

        original_timeout = self._sock.gettimeout()
        if timeout:
            self._sock.settimeout(timeout)

        try:
            self._send(PING_CMD)

            while True:
                line = self._read_line()
                if line.startswith(PONG_OP):
                    break
                elif line.startswith(PING_OP):
                    self._send(PONG_CMD)
                elif line.startswith(OK_OP):
                    continue
                elif line.startswith(ERR_OP):
                    err_msg = line[len(ERR_OP):].strip()
                    err_msg = err_msg.decode('utf-8')
                    raise NATSProtocolError(f'Server error: {err_msg}')
        finally:
            if timeout:
                self._sock.settimeout(original_timeout)

    # ############################################################################################################################

    def jetstream(self) -> 'JetStream':
        """ Returns a JetStream context for this client.
        """
        from .js import JetStream
        return JetStream(self)

    # ############################################################################################################################

    def __enter__(self) -> 'NATSClient':
        return self

    def __exit__(self, exc_type:'any_', exc_val:'any_', exc_tb:'any_') -> None:
        self.close()

# ################################################################################################################################
# ################################################################################################################################
