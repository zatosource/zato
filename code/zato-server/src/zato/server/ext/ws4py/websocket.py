# -*- coding: utf-8 -*-
# flake8: noqa

import logging
import socket
import time
import threading
from json import dumps
from types import GeneratorType

try:
    from OpenSSL.SSL import Error as pyOpenSSLError
except ImportError:
    class pyOpenSSLError(Exception):
        pass

from zato.common.api import GENERIC, WEB_SOCKET
from zato.common.marshal_.api import Model
from zato.common.util.config import replace_query_string_items
from zato.server.ext.ws4py.streaming import Stream
from zato.server.ext.ws4py.messaging import Message, PingControlMessage

Default_Read_Size = 200
Default_Socket_Read_Timeout  = WEB_SOCKET.DEFAULT.Socket_Read_Timeout
Default_Socket_Write_Timeout = WEB_SOCKET.DEFAULT.Socket_Write_Timeout

logger = logging.getLogger('zato_web_socket')

__all__ = ['WebSocket', 'EchoWebSocket', 'Heartbeat']

class Heartbeat(threading.Thread):
    def __init__(self, websocket, frequency=2.0):
        """
        Runs at a periodic interval specified by
        `frequency` by sending an unsolicitated pong
        message to the connected peer.

        If the message fails to be sent and a socket
        error is raised, we close the websocket
        socket automatically, triggering the `closed`
        handler.
        """
        threading.Thread.__init__(self)
        self.websocket = websocket
        self.frequency = frequency

    def __enter__(self):
        if self.frequency:
            self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:

            time.sleep(self.frequency)
            if self.websocket.terminated:
                break

            try:
                self.websocket.send(PingControlMessage(data='{}'))
            except socket.error as e:
                logger.info('WSX PingControl error -> %s', e)
                self.websocket.server_terminated = True
                self.websocket.close_connection()
                break

class WebSocket(object):
    """ Represents a websocket endpoint and provides a high level interface to drive the endpoint.
    """

    # This will be provided by subclasses
    url:'str'

    def __init__(self, server, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None,
        socket_read_timeout=None, socket_write_timeout=None):
        """ The ``sock`` is an opened connection
        resulting from the websocket handshake.

        If ``protocols`` is provided, it is a list of protocols
        negotiated during the handshake as is ``extensions``.

        If ``environ`` is provided, it is a copy of the WSGI environ
        dictionnary from the underlying WSGI server.
        """
        self.address_masked = replace_query_string_items(server, self.url)

        self.stream = Stream(always_mask=False)
        """
        Underlying websocket stream that performs the websocket
        parsing to high level objects. By default this stream
        never masks its messages. Clients using this class should
        set the ``stream.always_mask`` fields to ``True``
        and ``stream.expect_masking`` fields to ``False``.
        """

        self.protocols = protocols
        """
        List of protocols supported by this endpoint.
        Unused for now.
        """

        self.extensions = extensions
        """
        List of extensions supported by this endpoint.
        Unused for now.
        """

        self.sock = sock
        """
        Underlying connection.
        """

        self._is_secure = hasattr(sock, '_ssl') or hasattr(sock, '_sslobj')
        """
        Tell us if the socket is secure or not.
        """

        self.client_terminated = False
        """
        Indicates if the client has been marked as terminated.
        """

        self.server_terminated = False
        """
        Indicates if the server has been marked as terminated.
        """

        self.reading_buffer_size = Default_Read_Size
        """
        Current connection reading buffer size.
        """

        self.environ = environ
        """
        WSGI environ dictionary.
        """

        self.heartbeat_freq = heartbeat_freq
        """
        At which interval the heartbeat will be running.
        Set this to `0` or `None` to disable it entirely.
        """

        self.socket_read_timeout  = socket_read_timeout or Default_Socket_Read_Timeout
        self.socket_write_timeout = socket_write_timeout or Default_Socket_Write_Timeout

        self._local_address = None
        self._peer_address = None

        # These will be used by self.terminate
        self.last_close_code = 4003
        self.last_close_reason = GENERIC.InitialReason

    @property
    def local_address(self):
        """
        Local endpoint address as a tuple
        """
        if not self._local_address:
            self._local_address = self.sock.getsockname()
            if len(self._local_address) == 4:
                self._local_address = self._local_address[:2]
        return self._local_address

    @property
    def peer_address(self):
        """
        Peer endpoint address as a tuple
        """
        if not self._peer_address:
            self._peer_address = self.sock.getpeername()
            if len(self._peer_address) == 4:
                self._peer_address = self._peer_address[:2]
        return self._peer_address

    def zopened(self):
        """
        Called by the server when the upgrade handshake
        has succeeeded.
        """
        pass

    def close(self, code=4041, reason='Z4041'):
        """
        Call this method to initiate the websocket connection
        closing by sending a close frame to the connected peer.
        The ``code`` is the status code representing the
        termination's reason.

        Once this method is called, the ``server_terminated``
        attribute is set. Calling this method several times is
        safe as the closing frame will be sent only the first
        time.

        .. seealso:: Defined Status Codes http://tools.ietf.org/html/rfc6455#section-7.4.1
        """

        # Set for self.terminate to use
        self.last_close_code = code
        self.last_close_reason = reason

        if not self.server_terminated:
            self.server_terminated = True
            self._write(self.stream.close(code=code, reason=reason).single(mask=self.stream.always_mask))

    def zclosed(self, code, reason=None):
        """
        Called  when the websocket stream and connection are finally closed.
        The provided ``code`` is status set by the other point and
        ``reason`` is a human readable message.

        .. seealso:: Defined Status Codes http://tools.ietf.org/html/rfc6455#section-7.4.1
        """
        pass

    @property
    def terminated(self):
        """
        Returns ``True`` if both the client and server have been
        marked as terminated.
        """
        client_terminated = self.client_terminated is True
        server_terminated = self.server_terminated is True
        is_terminated = client_terminated and server_terminated
        return is_terminated

    @property
    def connection(self):
        return self.sock

    def close_connection(self):
        """
        Shutdowns then closes the underlying connection.
        """
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None

        self.client_terminated = True
        self.server_terminated = True

    def ping(self, message):
        """
        Send a ping message to the remote peer.
        The given `message` must be a unicode string.
        """
        self.send(PingControlMessage(message))

    def ponged(self, pong):
        """
        Pong message, as a :class:`messaging.PongControlMessage` instance,
        received on the stream.
        """
        pass

    def zreceived_message(self, message):
        """
        Called whenever a complete ``message``, binary or text,
        is received and ready for application's processing.

        The passed message is an instance of :class:`messaging.TextMessage`
        or :class:`messaging.BinaryMessage`.

        .. note:: You should override this method in your subclass.
        """
        pass

    def unhandled_error(self, error):
        """
        Called whenever a socket, or an OS, error is trapped
        by ws4py but not managed by it. The given error is
        an instance of `socket.error` or `OSError`.

        Note however that application exceptions will not go
        through this handler. Instead, do make sure you
        protect your code appropriately in `received_message`
        or `send`.

        The default behaviour of this handler is to log
        the error with a message.
        """
        logger.warn("Failed to receive WSX data from `%s` -> `%s`", self.address_masked, error)

    def _write(self, data):
        """
        Trying to prevent a write operation
        on an already closed websocket stream.

        This cannot be bullet proof but hopefully
        will catch almost all use cases.
        """
        if self.terminated or self.sock is None:
            logger.info('Could not send message on a terminated socket; `%s` -> %s (%s)',
                self.config.client_name, self.config.address, self.config.client_id)
        else:
            self.sock.settimeout(self.socket_write_timeout)
            self.sock.sendall(data)

    def send(self, payload, binary=False):
        """
        Sends the given ``payload`` out.

        If ``payload`` is some bytes or a bytearray,
        then it is sent as a single message not fragmented.

        If ``payload`` is a generator, each chunk is sent as part of
        fragmented message.

        If ``binary`` is set, handles the payload as a binary message.
        """

        if not self.stream:
            logger.info('Could not send message without self.stream -> %s -> %s (%s -> %s) ',
                self.config.client_name,
                self.config.address,
                self.config.username,
                self.config.client_id,
            )
            return

        message_sender = self.stream.binary_message if binary else self.stream.text_message # type: any_

        if payload is None or isinstance(payload, (dict, list, tuple, int, float)):
            payload = dumps(payload)

        elif isinstance(payload, Model):
            payload = payload.to_json()

        if isinstance(payload, str) or isinstance(payload, bytearray):
            m = message_sender(payload).single(mask=self.stream.always_mask)
            self._write(m)

        elif isinstance(payload, Message):
            data = payload.single(mask=self.stream.always_mask)
            self._write(data)

        elif type(payload) == GeneratorType:
            bytes = next(payload)
            first = True
            for chunk in payload:
                self._write(message_sender(bytes).fragment(first=first, mask=self.stream.always_mask))
                bytes = chunk
                first = False

            self._write(message_sender(bytes).fragment(last=True, mask=self.stream.always_mask))

        else:
            raise ValueError('Unsupported type `%s` passed to send()' % type(payload))

    def _get_from_pending(self):
        """
        The SSL socket object provides the same interface
        as the socket interface but behaves differently.

        When data is sent over a SSL connection
        more data may be read than was requested from by
        the ws4py websocket object.

        In that case, the data may have been indeed read
        from the underlying real socket, but not read by the
        application which will expect another trigger from the
        manager's polling mechanism as if more data was still on the
        wire. This will happen only when new data is
        sent by the other peer which means there will be
        some delay before the initial read data is handled
        by the application.

        Due to this, we have to rely on a non-public method
        to query the internal SSL socket buffer if it has indeed
        more data pending in its buffer.

        Now, some people in the Python community
        `discourage <https://bugs.python.org/issue21430>`_
        this usage of the ``pending()`` method because it's not
        the right way of dealing with such use case. They advise
        `this approach <https://docs.python.org/dev/library/ssl.html#notes-on-non-blocking-sockets>`_
        instead. Unfortunately, this applies only if the
        application can directly control the poller which is not
        the case with the WebSocket abstraction here.

        We therefore rely on this `technic <http://stackoverflow.com/questions/3187565/select-and-ssl-in-python>`_
        which seems to be valid anyway.

        This is a bit of a shame because we have to process
        more data than what wanted initially.
        """
        data = b""
        pending = self.sock.pending()
        while pending:
            data += self.sock.recv(pending)
            pending = self.sock.pending()
        return data

    def once(self):
        """
        Performs the operation of reading from the underlying
        connection in order to feed the stream of bytes.

        We start with a small size of two bytes to be read
        from the connection so that we can quickly parse an
        incoming frame header. Then the stream indicates
        whatever size must be read from the connection since
        it knows the frame payload length.

        It returns `False` if an error occurred at the
        socket level or during the bytes processing. Otherwise,
        it returns `True`.
        """
        if self.terminated:
            return False

        if not self.sock:
            return False

        try:
            self.sock.settimeout(self.socket_read_timeout)
            b = self.sock.recv(self.reading_buffer_size)

            # This will only make sense with secure sockets.
            if self._is_secure:
                b += self._get_from_pending()

        except TimeoutError as e:
            return True
        except (ValueError, socket.error, OSError, pyOpenSSLError) as e:
            self.unhandled_error(e)
            return True
        else:
            if not self.process(b):
                return False

        return True

    def terminate(self):
        """
        Completes the websocket by calling the `closed`
        method either using the received closing code
        and reason, or when none was received, using
        the special `1006` code.

        Finally close the underlying connection for
        good and cleanup resources by unsetting
        the `environ` and `stream` attributes.
        """
        s = self.stream

        self.client_terminated = self.server_terminated = True

        try:
            if s.closing is None:
                self.closed(self.last_close_code, self.last_close_reason)
            else:
                self.closed(s.closing.code, s.closing.reason)
        finally:
            self.close_connection()

            # Cleaning up resources
            s._cleanup()
            self.stream = None
            self.environ = None

    def process(self, bytes):
        """ Takes some bytes and process them through the
        internal stream's parser. If a message of any kind is
        found, performs one of these actions:

        * A closing message will initiate the closing handshake
        * Errors will initiate a closing handshake
        * A message will be passed to the ``received_message`` method
        * Pings will see pongs be sent automatically
        * Pongs will be passed to the ``ponged`` method

        The process should be terminated when this method
        returns ``False``.
        """
        s = self.stream

        if not bytes and self.reading_buffer_size > 0:
            return False

        self.reading_buffer_size = s.parser.send(bytes) or Default_Read_Size

        if s.closing is not None:
            logger.info("Closing message received (%d) '%s'" % (s.closing.code, s.closing.reason))
            if not self.server_terminated:
                self.close(s.closing.code, s.closing.reason)
            else:
                self.client_terminated = True
            return False

        if s.errors:
            for error in s.errors:
                logger.info("Error message received (%d) '%s'" % (error.code, error.reason))
                self.close(error.code, error.reason)
            s.errors = []
            return False

        if s.has_message:
            self.received_message(s.message)
            if s.message is not None:
                s.message.data = None
                s.message = None
            return True

        if s.pings:
            for ping in s.pings:
                self._write(s.pong(ping.data))
            s.pings = []

        if s.pongs:
            for pong in s.pongs:
                self.ponged(pong)
            s.pongs = []

        return True

    def run(self):
        """
        Performs the operation of reading from the underlying
        connection in order to feed the stream of bytes.

        We start with a small size of two bytes to be read
        from the connection so that we can quickly parse an
        incoming frame header. Then the stream indicates
        whatever size must be read from the connection since
        it knows the frame payload length.

        Note that we perform some automatic opererations:

        * On a closing message, we respond with a closing
          message and finally close the connection
        * We respond to pings with pong messages.
        * Whenever an error is raised by the stream parsing,
          we initiate the closing of the connection with the
          appropiate error code.

        This method is blocking and should likely be run
        in a thread.
        """
        self.sock.setblocking(True)
        with Heartbeat(self, frequency=self.heartbeat_freq):

            try:
                self.opened()
                while not self.terminated:
                    if not self.once():
                        break
            finally:
                self.terminate()

class EchoWebSocket(WebSocket):
    def received_message(self, message):
        """
        Automatically sends back the provided ``message`` to
        its originating endpoint.
        """
        self.send(message.data, message.is_binary)
