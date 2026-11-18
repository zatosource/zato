//! New connections to an endpoint, and one request and its response on a connection.
//!
//! The messages of the errors follow the messages urllib3 and requests produce for the same failures.

use std::net::{IpAddr, SocketAddr, TcpStream};
use std::os::fd::AsRawFd;
use std::sync::Arc;
use std::time::{Duration, Instant};

use rustls::{ClientConfig, ClientConnection};
use socket2::{Domain, Protocol, SockAddr, Socket, Type};

use super::error::TransportError;
use super::response::{ChunkedDecoder, Framing, HeadStatus, ResponseHead, parse_head};
use super::stream::{IoContext, IoError, Stream};
use super::tls::server_name;
use super::wait::ResolveError;

/// How many bytes one read from a connection asks for.
const READ_CHUNK_SIZE: usize = 16 * 1024;

/// The longest response head accepted, beyond which the response is rejected as `http.client` rejects it.
const MAX_HEAD_LEN: usize = 1024 * 1024;

/// The endpoint of a request, as the messages of its errors describe it.
pub struct Peer<'call> {
    /// Whether the connection uses TLS.
    pub is_tls: bool,

    /// The host name or IP address.
    pub host: &'call str,

    /// The port.
    pub port: u16,

    /// The path and the query string of the request.
    pub request_target: &'call str,

    /// The timeout of the connection, in seconds, or `None` if it has none.
    pub timeout: Option<f64>,
}

impl Peer<'_> {
    /// The name urllib3 gives the pool of connections to the endpoint, as it appears in its messages.
    fn pool_name(&self) -> String {
        let kind = if self.is_tls { "HTTPSConnectionPool" } else { "HTTPConnectionPool" };
        format!("{kind}(host='{}', port={})", self.host, self.port)
    }

    /// The timeout as Python prints it.
    fn timeout_text(&self) -> String {
        self.timeout.map_or_else(|| String::from("None"), |timeout| format!("{timeout:?}"))
    }

    /// The message of an error that ended the attempts to send the request.
    fn max_retries(&self, cause: &str) -> String {
        format!(
            "{}: Max retries exceeded with url: {} (Caused by {cause})",
            self.pool_name(),
            self.request_target
        )
    }

    /// The error of a read that did not complete within the timeout.
    fn read_timeout(&self) -> TransportError {
        TransportError::ReadTimeout(format!(
            "{}: Read timed out. (read timeout={})",
            self.pool_name(),
            self.timeout_text()
        ))
    }

    /// The error of a failed TLS session.
    fn tls_error(&self, reason: &str) -> TransportError {
        TransportError::Tls(self.max_retries(&format!("SSLError({reason:?})")))
    }
}

/// A response read from a connection.
pub struct RawResponse {
    /// The status line and the headers.
    pub head: ResponseHead,

    /// The body, as it was sent, before any content decoding.
    pub body: Vec<u8>,

    /// How long it took from the start of the request until the head of the response was read.
    pub elapsed: Duration,

    /// Whether the connection can serve another request.
    pub is_keep_alive: bool,
}

/// Why a request on a connection did not produce a response.
pub struct ExchangeFailure {
    /// The error the invocation fails with.
    pub error: TransportError,

    /// Whether the connection failed before any byte of the response arrived, in which case a request
    /// on a reused connection is repeated on a new one.
    pub is_before_response: bool,
}

/// A request ready to be written to a connection.
pub struct OutgoingRequest<'call> {
    /// The request line, the headers and, if it is small enough, the body, written at once.
    pub head: &'call [u8],

    /// The body, if it is not part of the head.
    pub body: Option<&'call [u8]>,

    /// Whether the request is a HEAD request, whose response has no body.
    pub is_head: bool,

    /// When the invocation started.
    pub start: Instant,
}

/// Opens a new connection to the endpoint, trying each of its addresses in turn.
pub fn connect(ctx: &IoContext<'_, '_>, peer: &Peer<'_>, tls_config: Option<&Arc<ClientConfig>>) -> Result<Stream, TransportError> {
    let addresses = resolve(ctx, peer)?;
    let mut last_error = None;

    for address in addresses {
        match connect_address(ctx, address) {
            Ok(tcp) => return establish(ctx, peer, tcp, tls_config),

            // A Python exception, such as a timeout of the caller, ends the attempts at once
            Err(IoError::Python(err)) => return Err(TransportError::Python(err)),
            Err(err) => last_error = Some(err),
        }
    }

    Err(connect_failure(peer, last_error))
}

/// Resolves the host of the endpoint, or uses it as it is if it is an IP address.
fn resolve(ctx: &IoContext<'_, '_>, peer: &Peer<'_>) -> Result<Vec<SocketAddr>, TransportError> {
    if let Ok(ip_address) = peer.host.parse::<IpAddr>() {
        return Ok(vec![SocketAddr::new(ip_address, peer.port)]);
    }

    match ctx.gevent.resolve(ctx.py, peer.host, peer.port) {
        Ok(addresses) if !addresses.is_empty() => Ok(addresses),
        Ok(_) => Err(name_resolution_error(peer, "No address associated with hostname")),
        Err(ResolveError::Failed(message)) => Err(name_resolution_error(peer, &message)),
        Err(ResolveError::Python(err)) => Err(TransportError::Python(err)),
    }
}

/// The error of a host name that does not resolve.
fn name_resolution_error(peer: &Peer<'_>, message: &str) -> TransportError {
    let cause = format!(
        "NameResolutionError(\"<urllib3.connection.HTTPConnection object>: Failed to resolve '{}' ({message})\")",
        peer.host
    );
    TransportError::Connection(peer.max_retries(&cause))
}

/// Opens a non-blocking TCP connection to one address, waiting for the connect to complete.
fn connect_address(ctx: &IoContext<'_, '_>, address: SocketAddr) -> Result<TcpStream, IoError> {
    let socket = Socket::new(Domain::for_address(address), Type::STREAM, Some(Protocol::TCP)).map_err(IoError::System)?;

    socket.set_nonblocking(true).map_err(IoError::System)?;
    socket.set_tcp_nodelay(true).map_err(IoError::System)?;

    match socket.connect(&SockAddr::from(address)) {
        Ok(()) => {}

        // A non-blocking connect is in progress until the socket becomes writable
        Err(err) if err.raw_os_error() == Some(libc::EINPROGRESS) => {
            ctx.gevent.wait_writable(ctx.py, socket.as_raw_fd(), ctx.timeout)?;

            // A writable socket has either connected or failed, and the pending error tells which
            if let Some(err) = socket.take_error().map_err(IoError::System)? {
                return Err(IoError::System(err));
            }
        }
        Err(err) => return Err(IoError::System(err)),
    }

    Ok(TcpStream::from(socket))
}

/// Completes a new connection - starts its TLS session if it uses TLS.
fn establish(
    ctx: &IoContext<'_, '_>,
    peer: &Peer<'_>,
    tcp: TcpStream,
    tls_config: Option<&Arc<ClientConfig>>,
) -> Result<Stream, TransportError> {
    let Some(config) = tls_config else {
        return Ok(Stream::Plain(tcp));
    };

    let name = server_name(peer.host).map_err(|message| peer.tls_error(&message))?;
    let session = ClientConnection::new(Arc::clone(config), name).map_err(|err| peer.tls_error(&err.to_string()))?;

    Stream::new_tls(ctx, tcp, session).map_err(|err| match err {
        IoError::TimedOut => peer.read_timeout(),
        IoError::Tls(err) => peer.tls_error(&err.to_string()),
        IoError::HandshakeEof => peer.tls_error("EOF occurred in violation of protocol"),
        IoError::System(err) => TransportError::Connection(connection_aborted(&os_error_text(&err))),
        IoError::Python(err) => TransportError::Python(err),
    })
}

/// The error of a connection that could not be established.
fn connect_failure(peer: &Peer<'_>, error: Option<IoError>) -> TransportError {
    match error {
        Some(IoError::TimedOut) => {
            let cause = format!(
                "ConnectTimeoutError(<urllib3.connection.HTTPConnection object>, 'Connection to {} timed out. (connect timeout={})')",
                peer.host,
                peer.timeout_text()
            );
            TransportError::ConnectTimeout(peer.max_retries(&cause))
        }
        Some(IoError::System(err)) => {
            let cause = format!(
                "NewConnectionError('<urllib3.connection.HTTPConnection object>: Failed to establish a new connection: {}')",
                os_error_text(&err)
            );
            TransportError::Connection(peer.max_retries(&cause))
        }
        Some(IoError::Python(err)) => TransportError::Python(err),
        Some(IoError::Tls(_) | IoError::HandshakeEof) | None => {
            TransportError::Connection(peer.max_retries("NewConnectionError('Failed to establish a new connection')"))
        }
    }
}

/// Describes an OS error the way Python prints it, e.g. `[Errno 111] Connection refused`.
fn os_error_text(err: &std::io::Error) -> String {
    let Some(code) = err.raw_os_error() else {
        return err.to_string();
    };

    // The description of the standard library ends with the code, which Python puts in front instead
    let description = err.to_string();
    let suffix = format!(" (os error {code})");
    let reason = description.strip_suffix(&suffix).unwrap_or(&description);

    format!("[Errno {code}] {reason}")
}

/// The message of a connection that was closed or reset before the response arrived.
fn connection_aborted(cause: &str) -> String {
    format!("('Connection aborted.', {cause:?})")
}

/// The error of a connection that failed after the request was written and before the response head was read.
fn before_response_error(peer: &Peer<'_>, err: IoError) -> TransportError {
    match err {
        IoError::TimedOut => peer.read_timeout(),
        IoError::System(err) => TransportError::Connection(connection_aborted(&os_error_text(&err))),
        IoError::Tls(err) => peer.tls_error(&err.to_string()),
        IoError::HandshakeEof => peer.tls_error("EOF occurred in violation of protocol"),
        IoError::Python(err) => TransportError::Python(err),
    }
}

/// A failure after part of the response arrived, which is never repeated on a new connection.
const fn after_response_started(error: TransportError) -> ExchangeFailure {
    ExchangeFailure {
        error,
        is_before_response: false,
    }
}

/// The error of a chunked body that is invalid or incomplete.
fn chunked_error(message: &str) -> ExchangeFailure {
    after_response_started(TransportError::ChunkedEncoding(format!(
        "('Connection broken: {message}', {message:?})"
    )))
}

/// Sends a request on a connection and reads its response.
pub fn exchange(
    ctx: &IoContext<'_, '_>,
    peer: &Peer<'_>,
    stream: &mut Stream,
    request: &OutgoingRequest<'_>,
) -> Result<RawResponse, ExchangeFailure> {
    let mut exchange = Exchange {
        ctx,
        peer,
        stream,
        chunk: [0_u8; READ_CHUNK_SIZE],
    };

    exchange.send(request)?;

    let mut buffer = Vec::with_capacity(READ_CHUNK_SIZE);

    // Informational responses are read and skipped until the final response arrives
    let head = loop {
        let head = exchange.read_head(&mut buffer)?;

        if !head.is_interim() {
            break head;
        }

        buffer.drain(..head.head_len);
    };

    let elapsed = request.start.elapsed();
    let mut leftover = buffer.split_off(head.head_len);

    let framing = head.framing(request.is_head);
    let mut is_keep_alive = head.is_keep_alive();

    let body = match framing {
        Framing::Empty => {
            is_keep_alive = is_keep_alive && leftover.is_empty();
            Vec::new()
        }
        Framing::Length(length) => {
            let is_complete = exchange.read_until_length(&mut leftover, length)?;

            // Bytes beyond the declared length, or a body the endpoint cut short, leave the connection unusable
            is_keep_alive = is_keep_alive && is_complete && leftover.len() == length;
            leftover.truncate(length);
            leftover
        }
        Framing::Chunked => {
            let (body, has_extra) = exchange.read_chunked(leftover)?;
            is_keep_alive = is_keep_alive && !has_extra;
            body
        }
        Framing::UntilClose => {
            exchange.read_until_close(&mut leftover)?;
            is_keep_alive = false;
            leftover
        }
    };

    Ok(RawResponse {
        head,
        body,
        elapsed,
        is_keep_alive,
    })
}

/// One request and its response on a connection.
struct Exchange<'call, 'ctx, 'py> {
    /// What the waits of the connection need.
    ctx: &'call IoContext<'ctx, 'py>,

    /// The endpoint, as the messages of the errors describe it.
    peer: &'call Peer<'call>,

    /// The connection.
    stream: &'call mut Stream,

    /// The buffer each read from the connection goes to.
    chunk: [u8; READ_CHUNK_SIZE],
}

impl Exchange<'_, '_, '_> {
    /// Writes the request to the connection.
    fn send(&mut self, request: &OutgoingRequest<'_>) -> Result<(), ExchangeFailure> {
        let mut result = self.stream.write_all(self.ctx, request.head);

        if let (Ok(()), Some(body)) = (&result, request.body) {
            result = self.stream.write_all(self.ctx, body);
        }

        // A connection the endpoint closed while it was idle in the pool fails here with an OS error
        result.map_err(|err| ExchangeFailure {
            is_before_response: matches!(err, IoError::System(_)),
            error: before_response_error(self.peer, err),
        })
    }

    /// Reads once from the connection, appending what arrived to the buffer, and returns how many bytes arrived.
    fn read_into(&mut self, buffer: &mut Vec<u8>) -> Result<usize, IoError> {
        let count = self.stream.read(self.ctx, &mut self.chunk)?;
        buffer.extend_from_slice(self.chunk.get(..count).unwrap_or_default());
        Ok(count)
    }

    /// Reads from the connection until the buffer starts with a complete response head.
    fn read_head(&mut self, buffer: &mut Vec<u8>) -> Result<ResponseHead, ExchangeFailure> {
        loop {
            if !buffer.is_empty() {
                match parse_head(buffer) {
                    Ok(HeadStatus::Complete(head)) => return Ok(head),
                    Ok(HeadStatus::Partial) => {}
                    Err(message) => {
                        let error = TransportError::Connection(connection_aborted(&message));
                        return Err(after_response_started(error));
                    }
                }

                if buffer.len() > MAX_HEAD_LEN {
                    let error = TransportError::Connection(connection_aborted("LineTooLong('header line')"));
                    return Err(after_response_started(error));
                }
            }

            let was_empty = buffer.is_empty();

            let count = self.read_into(buffer).map_err(|err| ExchangeFailure {
                is_before_response: was_empty && matches!(err, IoError::System(_)),
                error: before_response_error(self.peer, err),
            })?;

            // An endpoint that closed the connection before the response ended never sends the rest of it
            if count == 0 {
                let cause = "RemoteDisconnected('Remote end closed connection without response')";

                return Err(ExchangeFailure {
                    error: TransportError::Connection(connection_aborted(cause)),
                    is_before_response: was_empty,
                });
            }
        }
    }

    /// The error of a connection that failed while the body was being read, as requests raises it.
    fn body_error(&self, err: IoError) -> ExchangeFailure {
        let error = match err {
            // requests turns a read timeout during the body into a connection error
            IoError::TimedOut => TransportError::Connection(format!("{}: Read timed out.", self.peer.pool_name())),
            IoError::System(err) => {
                let text = os_error_text(&err);
                TransportError::ChunkedEncoding(format!("('Connection broken: {text}', {text:?})"))
            }
            IoError::Tls(err) => self.peer.tls_error(&err.to_string()),
            IoError::HandshakeEof => self.peer.tls_error("EOF occurred in violation of protocol"),
            IoError::Python(err) => TransportError::Python(err),
        };

        after_response_started(error)
    }

    /// Reads a body of the given length, returning whether all of it arrived before the endpoint closed the connection.
    fn read_until_length(&mut self, body: &mut Vec<u8>, length: usize) -> Result<bool, ExchangeFailure> {
        body.reserve(length.saturating_sub(body.len()));

        while body.len() < length {
            let count = self.read_into(body).map_err(|err| self.body_error(err))?;

            // A body cut short by the endpoint is returned as far as it arrived, as urllib3 returns it
            if count == 0 {
                return Ok(false);
            }
        }

        Ok(true)
    }

    /// Reads and decodes a chunked body, returning it and whether bytes followed its end.
    fn read_chunked(&mut self, mut pending: Vec<u8>) -> Result<(Vec<u8>, bool), ExchangeFailure> {
        let mut decoder = ChunkedDecoder::new();
        let mut body = Vec::new();

        loop {
            let consumed = decoder.feed(&pending, &mut body).map_err(|message| chunked_error(&message))?;
            pending.drain(..consumed);

            if decoder.is_done() {
                return Ok((body, !pending.is_empty()));
            }

            let count = self.read_into(&mut pending).map_err(|err| self.body_error(err))?;

            // A chunked body the endpoint cut before its last chunk is an incomplete body
            if count == 0 {
                return Err(chunked_error("IncompleteRead(0 bytes read)"));
            }
        }
    }

    /// Reads a body that ends when the endpoint closes the connection.
    fn read_until_close(&mut self, body: &mut Vec<u8>) -> Result<(), ExchangeFailure> {
        loop {
            let count = self.read_into(body).map_err(|err| self.body_error(err))?;

            if count == 0 {
                return Ok(());
            }
        }
    }
}
