# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of an outgoing Kafka connection - a listener standing in for the Kafka instance, which every request
# of the connection goes through. It records every message a produce request carries and either hands the request
# on to the instance or answers it with an error itself, which is how an endpoint refuses a message here. The
# instance is made to look like it lives at the endpoint's own port, so a client never goes around it, and a
# request for the metadata of every topic, which is what a ping is, is recorded as a read.

# stdlib
import logging
import selectors
import socket
import threading
import time
from collections import deque
from dataclasses import dataclass, field

# Test support
from queue_delivery.receiver import RecordedRequest, RecordingReceiver
from zato.common.typing_ import cast_
from _protocol import Api_Metadata, Api_Produce, Api_Versions, build_produce_response, cap_api_versions_response, \
    Error_Invalid_Record, Error_None, frame, is_metadata_request_for_everything, read_produce_request, \
    read_request_header, Reader, rewrite_metadata_response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple
    from _protocol import ProduceRequest, RequestHeader

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_kafka.receiver')

_host = '127.0.0.1'

# How long the listener waits for a connection before checking whether it is still meant to run
_accept_timeout_seconds = 0.2
_shutdown_timeout_seconds = 5
_connect_timeout_seconds = 5.0

# How long an endpoint that comes back after a stop gives its client to find it again - a client that lost the
# endpoint tries again at ever longer intervals, of up to ten seconds, and a test that goes on before the client is
# back would only see a timeout
_reconnect_wait_seconds = 12.0
_reconnect_poll_seconds = 0.1

# Every message on the wire opens with its length
_length_size = 4

# How many bytes one read of a connection takes at most
_recv_size = 65536

# A produce request that wants no acknowledgment is answered by no one
_acks_none = 0

# A connection opened to ask about every topic there is
Ping_Outcome = 'ping'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class KafkaRecordedRequest(RecordedRequest):
    """ One message as the endpoint of an outgoing Kafka connection saw it - the body is the value of the record as
    text and the outcome is the error code it was answered with, zero when it was handed on to the instance.
    """
    topic: str = ''
    partition: int = -1
    key: 'bytes | None' = None
    headers: 'list[anytuple]' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

def _take_frames(buffer:'bytearray') -> 'list[bytes]':
    """ Removes every complete message from the front of what arrived on a connection so far and returns them in order,
    leaving an incomplete one in the buffer until the rest of it arrives.
    """
    out:'list[bytes]' = []

    while len(buffer) >= _length_size:
        length = Reader(bytes(buffer[:_length_size])).int32()
        end = _length_size + length

        if len(buffer) < end:
            break

        out.append(bytes(buffer[_length_size:end]))
        del buffer[:end]

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class _Owed:
    """ One answer the client is owed - the header of a request the instance has yet to answer, or the bytes of an
    answer the endpoint gave itself that waits its turn.
    """
    header: 'RequestHeader | None' = None
    reply: 'bytes | None' = None

# ################################################################################################################################
# ################################################################################################################################

class _Connection:
    """ One client's connection through the endpoint to the instance - requests go one way, answers the other,
    and answers reach the client in the order of their requests whether the instance or the endpoint gave them.
    Both directions are served by the thread of the endpoint.
    """

    def __init__(self, receiver:'KafkaRecordingReceiver', client:'socket.socket', upstream:'socket.socket') -> 'None':
        self.receiver = receiver
        self.client = client
        self.upstream = upstream

        # What is owed to the client, in order
        self._pending:'deque[_Owed]' = deque()

        # What arrived from each side and does not form a complete message yet
        self._client_buffer = bytearray()
        self._upstream_buffer = bytearray()

# ################################################################################################################################

    def close(self) -> 'None':
        for connection in (self.client, self.upstream):
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()

# ################################################################################################################################

    def on_readable(self, sock:'socket.socket') -> 'bool':
        """ Reads what arrived on one side and handles each message it completes. Returns False once the connection
        is closed, by either side or because a message could not be handled.
        """
        try:
            chunk = sock.recv(_recv_size)
        except OSError:
            return False

        if not chunk:
            return False

        is_client = sock is self.client

        if is_client:
            buffer = self._client_buffer
        else:
            buffer = self._upstream_buffer

        buffer.extend(chunk)

        for payload in _take_frames(buffer):

            if is_client:
                try:
                    self._on_request(payload)
                except Exception:
                    logger.warning('Endpoint on port %d could not read a request', self.receiver.port, exc_info=True)
                    return False

            else:
                try:
                    self._on_response(payload)
                except Exception:
                    logger.warning('Endpoint on port %d could not pass an answer on', self.receiver.port, exc_info=True)
                    return False

        return True

# ################################################################################################################################

    def _on_request(self, payload:'bytes') -> 'None':
        """ Records what the endpoint cares about in a request of the client and hands it on unless it answers it itself.
        """
        header = read_request_header(payload)

        if header.api_key == Api_Produce:
            request = read_produce_request(payload, header.body_position)

            if self.receiver.handle_produce(request):
                if request.acks != _acks_none:
                    reply = build_produce_response(header.correlation_id, request.partitions, Error_Invalid_Record)
                    self._answer(reply)
                return

            needs_answer = request.acks != _acks_none

        elif header.api_key == Api_Metadata:
            if is_metadata_request_for_everything(payload, header.body_position):
                self.receiver.handle_ping()

            needs_answer = True

        else:
            needs_answer = True

        self._forward(header, payload, needs_answer)

# ################################################################################################################################

    def _on_response(self, payload:'bytes') -> 'None':
        """ Passes an answer of the instance to the client, rewritten where the endpoint has to.
        """
        correlation_id = Reader(payload).int32()
        header = self._take_request(correlation_id)

        if header.api_key == Api_Versions:
            payload = cap_api_versions_response(payload, header.api_version)

        elif header.api_key == Api_Metadata:
            payload = rewrite_metadata_response(payload, _host, self.receiver.port)

        self.client.sendall(frame(payload))
        self._flush_own_answers()

# ################################################################################################################################

    def _forward(self, header:'RequestHeader', payload:'bytes', needs_answer:'bool') -> 'None':
        """ Hands a request on to the instance, noting that its answer is owed to the client if one is.
        """
        if needs_answer:
            self._pending.append(_Owed(header=header))

        self.upstream.sendall(frame(payload))

# ################################################################################################################################

    def _answer(self, reply:'bytes') -> 'None':
        """ Gives the client an answer of the endpoint's own - at once if nothing is owed before it, otherwise in its turn.
        """
        if self._pending:
            self._pending.append(_Owed(reply=reply))
        else:
            self.client.sendall(reply)

# ################################################################################################################################

    def _take_request(self, correlation_id:'int') -> 'RequestHeader':
        """ The request an answer of the instance is for - the oldest one owed, which has to carry the same id.
        """
        owed = self._pending.popleft()

        if owed.header is None or owed.header.correlation_id != correlation_id:
            raise ValueError(f'An answer for request {correlation_id} arrived out of turn, expected {owed!r}')

        out = owed.header
        return out

# ################################################################################################################################

    def _flush_own_answers(self) -> 'None':
        """ Sends every answer of the endpoint's own that was waiting its turn behind the one just passed on.
        """
        while self._pending and self._pending[0].reply is not None:
            owed = self._pending.popleft()
            self.client.sendall(owed.reply or b'')

# ################################################################################################################################
# ################################################################################################################################

class KafkaRecordingReceiver(RecordingReceiver[KafkaRecordedRequest]):
    """ The endpoint of an outgoing Kafka connection.
    """

    Accept_Outcome = Error_None
    Refuse_Outcome = Error_Invalid_Record

    # Where the Kafka instance behind every endpoint is - the suite sets it before any endpoint is started
    instance_host = _host
    instance_port = 0

    # Set while the output of the queue bridge is expected to report errors - the suite sets it before any endpoint
    # is started, and it is set while any endpoint is stopped, until the bridge has connected through it again
    bridge_is_expected:'threading.Event'
    stopped_ports:'set[int]' = set()

    def __init__(self, port:'int') -> 'None':
        super().__init__(port)

        self._listener:'socket.socket | None' = None
        self._thread:'threading.Thread | None' = None
        self._is_running = False

        self._connections:'list[_Connection]' = []
        self._connections_lock = threading.Lock()

        # Whether the endpoint was stopped before, in which case a start waits for its client to come back
        self._was_stopped = False

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts listening in a thread of its own, which serves every connection through the endpoint and is named
        after it, so a restart of the endpoint leaves no thread of a new name behind - and after a stop,
        waits for the client to find the endpoint again.
        """
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((_host, self.port))
        listener.listen()

        self._listener = listener
        self._is_running = True

        thread = threading.Thread(target=self._serve, name=f'kafka-endpoint-{self.port}', daemon=True)
        thread.start()

        self._thread = thread

        logger.info('Endpoint started on port %d for Kafka at %s:%d', self.port, self.instance_host, self.instance_port)

        if self._was_stopped:
            self._wait_for_a_client()

            KafkaRecordingReceiver.stopped_ports.discard(self.port)

            if not KafkaRecordingReceiver.stopped_ports:
                KafkaRecordingReceiver.bridge_is_expected.clear()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops listening and cuts every connection through the endpoint - nothing answers on the port once this returns.
        """
        KafkaRecordingReceiver.stopped_ports.add(self.port)
        KafkaRecordingReceiver.bridge_is_expected.set()

        self._is_running = False

        if self._thread:
            self._thread.join(timeout=_shutdown_timeout_seconds)
            self._thread = None

        if self._listener:
            self._listener.close()
            self._listener = None

        with self._connections_lock:
            connections = list(self._connections)
            self._connections = []

        for connection in connections:
            connection.close()

        self._was_stopped = True

        logger.info('Endpoint stopped on port %d', self.port)

# ################################################################################################################################

    def _wait_for_a_client(self) -> 'None':
        """ Waits until a client has connected through the endpoint again, or until a client that has no reason to
        has had every chance to.
        """
        deadline = time.monotonic() + _reconnect_wait_seconds

        while time.monotonic() < deadline:

            with self._connections_lock:
                if self._connections:
                    logger.info('Endpoint on port %d has its client back', self.port)
                    return

            time.sleep(_reconnect_poll_seconds)

        logger.info('Endpoint on port %d has had no client back within %ss', self.port, _reconnect_wait_seconds)

# ################################################################################################################################

    def _serve(self) -> 'None':
        """ Accepts connections for as long as the endpoint runs, opening one to the instance for each,
        and passes on what arrives on either side of each of them.
        """
        listener = self._listener

        # Only start puts the thread on, and it sets the listener first
        if listener is None:
            return

        selector = selectors.DefaultSelector()
        _ = selector.register(listener, selectors.EVENT_READ)

        try:
            while self._is_running:

                for key, _ in selector.select(_accept_timeout_seconds):

                    if key.fileobj is listener:
                        self._accept(listener, selector)

                    else:
                        connection:'_Connection' = key.data
                        sock = cast_('socket.socket', key.fileobj)

                        if not connection.on_readable(sock):
                            self._drop(connection, selector)

        finally:
            selector.close()

# ################################################################################################################################

    def _accept(self, listener:'socket.socket', selector:'selectors.BaseSelector') -> 'None':
        """ Accepts one client and opens its connection to the instance.
        """
        client, _ = listener.accept()
        client.settimeout(None)

        try:
            upstream = socket.create_connection((self.instance_host, self.instance_port), timeout=_connect_timeout_seconds)
            upstream.settimeout(None)
        except OSError:
            logger.warning('Endpoint on port %d could not reach Kafka at %s:%d', self.port, self.instance_host,
                self.instance_port, exc_info=True)
            client.close()
            return

        connection = _Connection(self, client, upstream)

        _ = selector.register(client, selectors.EVENT_READ, connection)
        _ = selector.register(upstream, selectors.EVENT_READ, connection)

        with self._connections_lock:
            self._connections.append(connection)

# ################################################################################################################################

    def _drop(self, connection:'_Connection', selector:'selectors.BaseSelector') -> 'None':
        """ Closes a connection that either side closed and stops watching it.
        """
        _ = selector.unregister(connection.client)
        _ = selector.unregister(connection.upstream)

        connection.close()

        with self._connections_lock:
            self._connections.remove(connection)

# ################################################################################################################################

    def handle_produce(self, request:'ProduceRequest') -> 'bool':
        """ Records every message of a produce request with the outcome each is due, and says whether the request
        is refused - which it is as soon as any of its messages is.
        """
        is_refused = False

        for record in request.records:
            outcome = self.next_outcome()
            is_accepted = self.is_accepted(outcome)

            if record.value is None:
                body = ''
            else:
                body = record.value.decode('utf8')

            self.add_request(KafkaRecordedRequest(
                body=body,
                outcome=outcome,
                is_accepted=is_accepted,
                is_read=False,
                topic=record.topic,
                partition=record.partition,
                key=record.key,
                headers=record.headers,
            ))

            if not is_accepted:
                is_refused = True

        return is_refused

# ################################################################################################################################

    def handle_ping(self) -> 'None':
        """ A request for the metadata of every topic - a read, which the script does not apply to.
        """
        self.add_request(KafkaRecordedRequest(
            body='',
            outcome=Ping_Outcome,
            is_accepted=True,
            is_read=True,
        ))

# ################################################################################################################################
# ################################################################################################################################
