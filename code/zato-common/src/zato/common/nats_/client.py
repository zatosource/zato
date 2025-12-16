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
import threading
from io import BytesIO

# Zato
from zato.common.typing_ import any_, anydict, callable_, intnone, optional, strnone

# Local
from .const import CRLF, CRLF_LEN, CONNECT_OP, Default_Buffer_Size, Default_Host, Default_Inbox_Prefix, \
     Default_Max_Payload, Default_Port, Default_Timeout, ERR_OP, INFO_OP, JS_Ack, JS_API_Consumer_Create, \
     JS_API_Consumer_Create_Durable, JS_API_Consumer_Delete, JS_API_Consumer_Info, JS_API_Consumer_Msg_Next, \
     JS_API_Stream_Create, JS_API_Stream_Delete, JS_API_Stream_Info, JS_API_Stream_Purge, JS_Nak, JS_Progress, \
     JS_Term, NATS_HDR_Line, NATS_HDR_Line_Size, OK_OP, PING_CMD, PING_OP, PONG_CMD, PONG_OP, SPC
from .exc import NATSConnectionError, NATSError, NATSJetStreamError, NATSNoRespondersError, \
     NATSProtocolError, NATSTimeoutError
from .model import ConnectOptions, ConsumerConfig, ConsumerInfo, Msg, PubAck, ServerInfo, StreamConfig, StreamInfo
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
        self._sock: 'optional[socket.socket]' = None
        self._ssl_context: 'optional[ssl.SSLContext]' = None
        self._server_info: 'optional[ServerInfo]' = None
        self._options: 'optional[ConnectOptions]' = None
        self._buffer = BytesIO()
        self._nuid = NUID()

        self._sid = 0
        self._subscriptions: 'anydict' = {}
        self._pending_msgs: 'anydict' = {}
        self._resp_map: 'anydict' = {}
        self._resp_sub_prefix: 'optional[bytearray]' = None

        self._max_payload = Default_Max_Payload
        self._connected = False
        self._lock = threading.Lock()

        self._host = Default_Host
        self._port = Default_Port
        self._timeout = Default_Timeout

    # ############################################################################################################################

    @property
    def is_connected(self) -> 'bool':
        return self._connected

    @property
    def server_info(self) -> 'optional[ServerInfo]':
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
        ssl_context:'optional[ssl.SSLContext]'=None,
        connect_timeout:'optional[float]'=None,
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
        info_data = json.loads(info_json.decode('utf-8'))
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
        connect_cmd = CONNECT_OP + SPC + json.dumps(self._options.to_dict()).encode('utf-8') + CRLF
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
                err_msg = line[len(ERR_OP):].strip().decode('utf-8')
                raise NATSConnectionError(f'Server error: {err_msg}')
            else:
                raise NATSProtocolError(f'Unexpected response: {line!r}')

        self._connected = True
        logger.info(f'Connected to NATS server at {host}:{port}')

    # ############################################################################################################################

    def close(self) -> None:
        """ Closes the connection.
        """
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        self._connected = False
        self._subscriptions.clear()
        self._pending_msgs.clear()
        logger.info('Disconnected from NATS server')

    # ############################################################################################################################

    def _send(self, data:'bytes') -> None:
        if not self._sock:
            raise NATSConnectionError('Not connected')
        try:
            self._sock.sendall(data)
        except socket.error as e:
            self._connected = False
            raise NATSConnectionError(f'Send failed: {e}') from e

    # ############################################################################################################################

    def _read_line(self) -> 'bytes':
        if not self._sock:
            raise NATSConnectionError('Not connected')

        data = bytearray()
        while True:
            try:
                chunk = self._sock.recv(1)
                if not chunk:
                    raise NATSConnectionError('Connection closed by server')
                data.extend(chunk)
                if data.endswith(CRLF):
                    return bytes(data)
            except socket.timeout:
                raise NATSTimeoutError('Read timeout')
            except socket.error as e:
                self._connected = False
                raise NATSConnectionError(f'Read failed: {e}') from e

    # ############################################################################################################################

    def _read_bytes(self, n:'int') -> 'bytes':
        if not self._sock:
            raise NATSConnectionError('Not connected')

        data = bytearray()
        remaining = n
        while remaining > 0:
            try:
                chunk = self._sock.recv(min(remaining, Default_Buffer_Size))
                if not chunk:
                    raise NATSConnectionError('Connection closed by server')
                data.extend(chunk)
                remaining -= len(chunk)
            except socket.timeout:
                raise NATSTimeoutError('Read timeout')
            except socket.error as e:
                self._connected = False
                raise NATSConnectionError(f'Read failed: {e}') from e
        return bytes(data)

    # ############################################################################################################################

    def publish(
        self,
        subject:'str',
        payload:'bytes'=b'',
        reply:'str'='',
        headers:'optional[anydict]'=None,
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
        callback:'optional[callable_]'=None,
        max_msgs:'int'=0,
    ) -> 'Subscription':
        if not self._connected:
            raise NATSConnectionError('Not connected')

        self._sid += 1
        sid = self._sid

        sub = Subscription(self, sid, subject, queue, callback, max_msgs)
        self._subscriptions[sid] = sub
        self._pending_msgs[sid] = []

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
        timeout:'optional[float]'=None,
        headers:'optional[anydict]'=None,
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
                if status == '503':
                    raise NATSNoRespondersError('No responders available')

            return msg
        finally:
            try:
                sub.unsubscribe()
            except Exception:
                pass

    # ############################################################################################################################

    def _wait_for_msg(self, sid:'int', timeout:'optional[float]'=None) -> 'Msg':
        if timeout is None:
            timeout = self._timeout

        if not self._sock:
            raise NATSConnectionError('Not connected')

        original_timeout = self._sock.gettimeout()
        if timeout:
            self._sock.settimeout(timeout)

        try:
            # Check if there are pending messages
            pending = self._pending_msgs.get(sid, [])
            if pending:
                return pending.pop(0)

            # Read messages until we get one for this subscription
            while True:
                msg = self._read_msg()
                if msg is None:
                    continue

                if msg.sid == sid:
                    sub = self._subscriptions.get(sid)
                    if sub:
                        sub._received += 1
                    return msg
                else:
                    # Queue message for different subscription
                    if msg.sid in self._pending_msgs:
                        self._pending_msgs[msg.sid].append(msg)

        finally:
            if timeout:
                self._sock.settimeout(original_timeout)

    # ############################################################################################################################

    def _read_msg(self) -> 'optional[Msg]':
        line = self._read_line()

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
            err_msg = line[len(ERR_OP):].strip().decode('utf-8')
            raise NATSProtocolError(f'Server error: {err_msg}')

        # Handle MSG
        match = MSG_RE.match(line)
        if match:
            subject = match.group(1).decode('utf-8')
            sid = int(match.group(2))
            reply = match.group(4).decode('utf-8') if match.group(4) else ''
            payload_size = int(match.group(5))

            payload = self._read_bytes(payload_size)
            self._read_bytes(CRLF_LEN)  # Read trailing CRLF

            return Msg(subject=subject, reply=reply, data=payload, sid=sid)

        # Handle HMSG (with headers)
        match = HMSG_RE.match(line)
        if match:
            subject = match.group(1).decode('utf-8')
            sid = int(match.group(2))
            reply = match.group(4).decode('utf-8') if match.group(4) else ''
            hdr_size = int(match.group(5))
            total_size = int(match.group(6))

            total_data = self._read_bytes(total_size)
            self._read_bytes(CRLF_LEN)  # Read trailing CRLF

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
                headers[key.decode('utf-8').strip()] = value.decode('utf-8').strip()

        return headers

    # ############################################################################################################################

    def flush(self, timeout:'optional[float]'=None) -> None:
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
                    err_msg = line[len(ERR_OP):].strip().decode('utf-8')
                    raise NATSProtocolError(f'Server error: {err_msg}')
        finally:
            if timeout:
                self._sock.settimeout(original_timeout)

    # ############################################################################################################################
    # JetStream Methods
    # ############################################################################################################################

    def js_publish(
        self,
        subject:'str',
        payload:'bytes'=b'',
        timeout:'optional[float]'=None,
        headers:'optional[anydict]'=None,
        msg_id:'strnone'=None,
        expected_stream:'strnone'=None,
        expected_last_seq:'intnone'=None,
    ) -> 'PubAck':
        """ Publishes a message to JetStream and waits for an acknowledgment.
        """
        if timeout is None:
            timeout = self._timeout

        hdr = headers or {}
        if msg_id:
            hdr['Nats-Msg-Id'] = msg_id
        if expected_stream:
            hdr['Nats-Expected-Stream'] = expected_stream
        if expected_last_seq is not None:
            hdr['Nats-Expected-Last-Sequence'] = str(expected_last_seq)

        msg = self.request(subject, payload, timeout=timeout, headers=hdr if hdr else None)

        resp = json.loads(msg.data.decode('utf-8'))
        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return PubAck.from_dict(resp)

    # ############################################################################################################################

    def js_create_stream(self, config:'StreamConfig', timeout:'optional[float]'=None) -> 'StreamInfo':
        """ Creates a JetStream stream.
        """
        if not config.name:
            raise NATSError('Stream name is required')

        subject = JS_API_Stream_Create.format(stream=config.name)
        payload = json.dumps(config.to_dict()).encode('utf-8')

        msg = self.request(subject, payload, timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return StreamInfo.from_dict(resp)

    # ############################################################################################################################

    def js_delete_stream(self, stream:'str', timeout:'optional[float]'=None) -> 'bool':
        """ Deletes a JetStream stream.
        """
        subject = JS_API_Stream_Delete.format(stream=stream)
        msg = self.request(subject, b'', timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return resp['success']

    # ############################################################################################################################

    def js_stream_info(self, stream:'str', timeout:'optional[float]'=None) -> 'StreamInfo':
        """ Returns information about a JetStream stream.
        """
        subject = JS_API_Stream_Info.format(stream=stream)
        msg = self.request(subject, b'', timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return StreamInfo.from_dict(resp)

    # ############################################################################################################################

    def js_purge_stream(self, stream:'str', timeout:'optional[float]'=None) -> 'int':
        """ Purges messages from a JetStream stream. Returns the number of purged messages.
        """
        subject = JS_API_Stream_Purge.format(stream=stream)
        msg = self.request(subject, b'', timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return resp['purged']

    # ############################################################################################################################

    def js_create_consumer(
        self,
        stream:'str',
        config:'ConsumerConfig',
        timeout:'optional[float]'=None,
    ) -> 'ConsumerInfo':
        """ Creates a JetStream consumer.
        """
        if config.durable_name:
            subject = JS_API_Consumer_Create_Durable.format(stream=stream, consumer=config.durable_name)
        else:
            subject = JS_API_Consumer_Create.format(stream=stream)

        payload = json.dumps({
            'stream_name': stream,
            'config': config.to_dict(),
        }).encode('utf-8')

        msg = self.request(subject, payload, timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return ConsumerInfo.from_dict(resp)

    # ############################################################################################################################

    def js_delete_consumer(self, stream:'str', consumer:'str', timeout:'optional[float]'=None) -> 'bool':
        """ Deletes a JetStream consumer.
        """
        subject = JS_API_Consumer_Delete.format(stream=stream, consumer=consumer)
        msg = self.request(subject, b'', timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return resp['success']

    # ############################################################################################################################

    def js_consumer_info(self, stream:'str', consumer:'str', timeout:'optional[float]'=None) -> 'ConsumerInfo':
        """ Returns information about a JetStream consumer.
        """
        subject = JS_API_Consumer_Info.format(stream=stream, consumer=consumer)
        msg = self.request(subject, b'', timeout=timeout)
        resp = json.loads(msg.data.decode('utf-8'))

        if 'error' in resp:
            err = resp['error']
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return ConsumerInfo.from_dict(resp)

    # ############################################################################################################################

    def js_fetch(
        self,
        stream:'str',
        consumer:'str',
        batch:'int'=1,
        timeout:'optional[float]'=None,
        no_wait:'bool'=False,
    ) -> 'anylist':
        """ Fetches messages from a JetStream consumer.
        """
        if timeout is None:
            timeout = self._timeout

        subject = JS_API_Consumer_Msg_Next.format(stream=stream, consumer=consumer)

        inbox = self.new_inbox()
        sub = self.subscribe(inbox, max_msgs=batch)

        try:
            # Build fetch request
            req = {'batch': batch}
            if timeout:
                req['expires'] = int(timeout * 1_000_000_000)
            if no_wait:
                req['no_wait'] = True

            self.publish(subject, json.dumps(req).encode('utf-8'), reply=inbox)

            msgs = []
            while len(msgs) < batch:
                try:
                    msg = sub.next_msg(timeout=timeout)

                    # Check for status message
                    if msg.headers:
                        status = msg.headers.get('Status')
                        if status == '404':
                            # No messages
                            break
                        elif status == '408':
                            # Timeout
                            break
                        elif status == '409':
                            # Conflict
                            continue
                        elif status == '100':
                            # Heartbeat
                            continue

                    msgs.append(msg)
                except NATSTimeoutError:
                    break

            return msgs
        finally:
            try:
                sub.unsubscribe()
            except Exception:
                pass

    # ############################################################################################################################

    def js_ack(self, msg:'Msg') -> None:
        """ Acknowledges a JetStream message.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')
        self.publish(msg.reply, JS_Ack)

    # ############################################################################################################################

    def js_nak(self, msg:'Msg', delay:'optional[float]'=None) -> None:
        """ Negatively acknowledges a JetStream message.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')

        if delay:
            payload = json.dumps({'delay': int(delay * 1_000_000_000)}).encode('utf-8')
            self.publish(msg.reply, JS_Nak + b' ' + payload)
        else:
            self.publish(msg.reply, JS_Nak)

    # ############################################################################################################################

    def js_in_progress(self, msg:'Msg') -> None:
        """ Marks a JetStream message as in progress, extending the ack deadline.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')
        self.publish(msg.reply, JS_Progress)

    # ############################################################################################################################

    def js_term(self, msg:'Msg') -> None:
        """ Terminates a JetStream message - it will not be redelivered.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')
        self.publish(msg.reply, JS_Term)

    # ############################################################################################################################

    def __enter__(self) -> 'NATSClient':
        return self

    def __exit__(self, exc_type:'any_', exc_val:'any_', exc_tb:'any_') -> None:
        self.close()

# ################################################################################################################################
# ################################################################################################################################
