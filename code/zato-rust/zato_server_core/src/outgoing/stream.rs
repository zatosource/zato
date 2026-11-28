//! A connection to an endpoint, plain TCP or TLS over TCP, read and written without blocking the process.
//!
//! Every socket is non-blocking. An operation that would block waits for the socket to become ready,
//! with the timeout of the connection, and is then repeated. A greenlet waits through gevent,
//! and a thread of the push engine, which holds no GIL, waits by blocking itself.

use std::io::{ErrorKind, IoSlice, Read, Write};
use std::net::{SocketAddr, TcpStream};
use std::os::fd::{AsFd, BorrowedFd};

use pyo3::marker::Ungil;
use pyo3::prelude::*;
use rustls::ClientConnection;

use super::wait::{Gevent, ResolveError, WaitError, resolve_blocking, wait_readable_blocking, wait_writable_blocking};

/// How an operation that would block waits for its socket.
pub enum Waiter<'ctx, 'py> {

    /// Through the gevent hub, so other greenlets run meanwhile, with syscalls made without the GIL.
    Gevent {

        /// The interpreter the gevent functions are invoked in.
        py: Python<'py>,

        /// The gevent functions the waits go through.
        gevent: &'ctx Gevent,
    },

    /// By blocking the calling OS thread, which holds no GIL.
    Blocking,
}

/// What every operation on a stream needs to wait for its socket.
pub struct IoContext<'ctx, 'py> {

    /// How an operation waits.
    pub waiter: Waiter<'ctx, 'py>,

    /// How long one wait may take, in seconds, or `None` to wait as long as it takes.
    pub timeout: Option<f64>,
}

impl IoContext<'_, '_> {

    /// Runs a syscall, without the GIL if the caller holds it, so that other interpreter threads proceed meanwhile.
    pub fn detach<T, F>(&self, func: F) -> T
    where
        F: Ungil + FnOnce() -> T,
        T: Ungil,
    {
        match &self.waiter {
            Waiter::Gevent { py, .. } => py.detach(func),
            Waiter::Blocking => func(),
        }
    }

    /// Waits until the descriptor is readable.
    pub fn wait_readable(&self, fd: BorrowedFd<'_>) -> Result<(), WaitError> {
        match &self.waiter {
            Waiter::Gevent { py, gevent } => gevent.wait_readable(*py, fd, self.timeout),
            Waiter::Blocking => wait_readable_blocking(fd, self.timeout),
        }
    }

    /// Waits until the descriptor is writable.
    pub fn wait_writable(&self, fd: BorrowedFd<'_>) -> Result<(), WaitError> {
        match &self.waiter {
            Waiter::Gevent { py, gevent } => gevent.wait_writable(*py, fd, self.timeout),
            Waiter::Blocking => wait_writable_blocking(fd, self.timeout),
        }
    }

    /// Resolves a host name into the socket addresses to connect to.
    pub fn resolve(&self, host: &str, port: u16) -> Result<Vec<SocketAddr>, ResolveError> {
        match &self.waiter {
            Waiter::Gevent { py, gevent } => gevent.resolve(*py, host, port),
            Waiter::Blocking => resolve_blocking(host, port),
        }
    }
}

/// Why an operation on a stream failed.
pub enum IoError {
    /// The socket did not become ready within the timeout.
    TimedOut,

    /// The operating system reported an error, or the endpoint closed the connection in the middle of a TLS record.
    System(std::io::Error),

    /// The TLS session failed, e.g. a certificate was rejected or the endpoint sent an alert.
    Tls(rustls::Error),

    /// The endpoint closed the connection before the TLS handshake completed.
    HandshakeEof,

    /// A wait raised a Python exception other than a timeout.
    Python(PyErr),
}

impl From<WaitError> for IoError {
    fn from(error: WaitError) -> Self {
        match error {
            WaitError::TimedOut => Self::TimedOut,
            WaitError::Python(err) => Self::Python(err),
            WaitError::System(err) => Self::System(err),
        }
    }
}

/// A TLS session over a TCP connection.
pub struct TlsStream {
    /// The TCP connection the TLS records travel over.
    tcp: TcpStream,

    /// The TLS session.
    session: ClientConnection,
}

/// A connection to an endpoint.
pub enum Stream {
    /// A plain TCP connection.
    Plain(TcpStream),

    /// A TLS session over a TCP connection.
    Tls(Box<TlsStream>),
}

impl Stream {
    /// Wraps a connected TCP socket in a TLS session and completes the handshake.
    pub fn new_tls(ctx: &IoContext<'_, '_>, tcp: TcpStream, session: ClientConnection) -> Result<Self, IoError> {
        let mut tls = TlsStream { tcp, session };
        tls.handshake(ctx)?;
        Ok(Self::Tls(Box::new(tls)))
    }

    /// Writes the head of a request and then each part of its body, without joining them into one buffer,
    /// waiting for the socket to become writable as often as needed.
    pub fn write_all_vectored(&mut self, ctx: &IoContext<'_, '_>, head: &[u8], parts: &[&[u8]]) -> Result<(), IoError> {
        match self {
            Self::Plain(tcp) => write_all_vectored_plain(ctx, tcp, head, parts),
            Self::Tls(tls) => {
                // The session copies plaintext into its records in any case, so each part is passed to it in turn
                tls.write_all(ctx, head)?;
                for part in parts {
                    tls.write_all(ctx, part)?;
                }
                Ok(())
            }
        }
    }

    /// Reads what is available, waiting for the socket to become readable first if nothing is.
    /// Returns zero once the endpoint closed the connection.
    pub fn read(&mut self, ctx: &IoContext<'_, '_>, buffer: &mut [u8]) -> Result<usize, IoError> {
        match self {
            Self::Plain(tcp) => read_plain(ctx, tcp, buffer),
            Self::Tls(tls) => tls.read(ctx, buffer),
        }
    }

    /// Whether a pooled connection can be used for another request - the endpoint did not close it,
    /// and nothing arrived on it since the previous response.
    pub fn is_reusable(&mut self) -> bool {
        match self {
            Self::Plain(tcp) => is_plain_reusable(tcp),
            Self::Tls(tls) => tls.is_reusable(),
        }
    }

    /// The address of the endpoint the connection is established to.
    pub fn peer_address(&self) -> std::io::Result<SocketAddr> {
        match self {
            Self::Plain(tcp) => tcp.peer_addr(),
            Self::Tls(tls) => tls.tcp.peer_addr(),
        }
    }
}

/// Writes the head and the parts of a request to a plain TCP connection, with one vectored write per syscall.
fn write_all_vectored_plain(ctx: &IoContext<'_, '_>, tcp: &mut TcpStream, head: &[u8], parts: &[&[u8]]) -> Result<(), IoError> {
    // The slices are built for each request, because a write advances them past what was sent
    let mut slices = Vec::with_capacity(parts.len().saturating_add(1));
    slices.push(IoSlice::new(head));
    slices.extend(parts.iter().map(|part| IoSlice::new(part)));

    // A shared reference writes as well as a mutable one, so the descriptor stays borrowed for the waits
    let tcp: &TcpStream = tcp;
    let fd = tcp.as_fd();

    write_all_slices(
        &mut slices,
        // The syscall runs without the GIL, so that other interpreter threads proceed meanwhile
        |current| ctx.detach(|| { let mut writer = tcp; writer.write_vectored(current) }),
        // The send buffer is full, so this greenlet waits while the others run
        || Ok(ctx.wait_writable(fd)?),
    )
}

/// Writes all of the slices through a vectored write, advancing past each partial write
/// and waiting whenever the writer would block.
fn write_all_slices(
    slices: &mut [IoSlice<'_>],
    mut write: impl FnMut(&[IoSlice<'_>]) -> std::io::Result<usize>,
    mut wait_writable: impl FnMut() -> Result<(), IoError>,
) -> Result<(), IoError> {
    let mut remaining = slices;

    // Empty slices at the front would make a write of zero bytes look like a closed connection
    IoSlice::advance_slices(&mut remaining, 0);

    while !remaining.is_empty() {
        match write(remaining) {
            Ok(0) => return Err(IoError::System(ErrorKind::WriteZero.into())),
            Ok(written) => IoSlice::advance_slices(&mut remaining, written),
            Err(err) if err.kind() == ErrorKind::WouldBlock => wait_writable()?,
            Err(err) if err.kind() == ErrorKind::Interrupted => {}
            Err(err) => return Err(IoError::System(err)),
        }
    }

    Ok(())
}

/// Reads what is available from a plain TCP connection.
fn read_plain(ctx: &IoContext<'_, '_>, tcp: &mut TcpStream, buffer: &mut [u8]) -> Result<usize, IoError> {
    loop {
        // The syscall runs without the GIL, so that other interpreter threads proceed meanwhile
        match ctx.detach(|| tcp.read(buffer)) {
            Ok(count) => return Ok(count),

            // Nothing arrived yet, so this greenlet waits while the others run
            Err(err) if err.kind() == ErrorKind::WouldBlock => ctx.wait_readable(tcp.as_fd())?,
            Err(err) if err.kind() == ErrorKind::Interrupted => {}
            Err(err) => return Err(IoError::System(err)),
        }
    }
}

/// Whether a plain TCP connection is still open and has nothing unread on it.
fn is_plain_reusable(tcp: &TcpStream) -> bool {
    let mut probe = [0_u8; 1];

    // A connection with nothing to read is open, whereas zero bytes means the endpoint closed it,
    // and any byte at all is something no request asked for
    matches!(tcp.peek(&mut probe), Err(err) if err.kind() == ErrorKind::WouldBlock)
}

impl TlsStream {
    /// Exchanges handshake records until the TLS session is established.
    fn handshake(&mut self, ctx: &IoContext<'_, '_>) -> Result<(), IoError> {
        while self.session.is_handshaking() {
            if self.session.wants_write() {
                self.flush(ctx)?;
                continue;
            }

            // An endpoint that closes the connection in the middle of a handshake will never complete it
            let is_eof = self.fill(ctx)?;
            if is_eof && self.session.is_handshaking() {
                return Err(IoError::HandshakeEof);
            }
        }

        // The last flight of the handshake may still be waiting to be sent
        self.flush(ctx)
    }

    /// Sends all the TLS records the session has queued.
    fn flush(&mut self, ctx: &IoContext<'_, '_>) -> Result<(), IoError> {
        while self.session.wants_write() {
            // The syscall runs without the GIL, so that other interpreter threads proceed meanwhile
            match ctx.detach(|| self.session.write_tls(&mut self.tcp)) {
                Ok(_) => {}
                Err(err) if err.kind() == ErrorKind::WouldBlock => {
                    ctx.wait_writable(self.tcp.as_fd())?;
                }
                Err(err) if err.kind() == ErrorKind::Interrupted => {}
                Err(err) => return Err(IoError::System(err)),
            }
        }

        Ok(())
    }

    /// Receives TLS records and processes them, waiting for the socket to become readable if nothing arrived yet.
    /// Returns whether the endpoint closed the connection.
    fn fill(&mut self, ctx: &IoContext<'_, '_>) -> Result<bool, IoError> {
        let is_eof = loop {
            // The syscall runs without the GIL, so that other interpreter threads proceed meanwhile
            match ctx.detach(|| self.session.read_tls(&mut self.tcp)) {
                Ok(count) => break count == 0,
                Err(err) if err.kind() == ErrorKind::WouldBlock => {
                    ctx.wait_readable(self.tcp.as_fd())?;
                }
                Err(err) if err.kind() == ErrorKind::Interrupted => {}
                Err(err) => return Err(IoError::System(err)),
            }
        };

        // Decryption runs without the GIL, so that other interpreter threads proceed meanwhile
        if let Err(err) = ctx.detach(|| self.session.process_new_packets()) {
            // The session queued an alert describing the failure, which the endpoint is told of if it still listens
            ctx.detach(|| self.session.write_tls(&mut self.tcp)).ok();
            return Err(IoError::Tls(err));
        }

        // Processing records may have queued records of its own, e.g. a reply to a key update
        if self.session.wants_write() {
            self.flush(ctx)?;
        }

        Ok(is_eof)
    }

    /// Encrypts and sends all of the data.
    fn write_all(&mut self, ctx: &IoContext<'_, '_>, data: &[u8]) -> Result<(), IoError> {
        let mut offset = 0;

        while let Some(remaining) = data.get(offset..) {
            if remaining.is_empty() {
                break;
            }

            // The session accepts as much plaintext as its buffer holds, and sending makes room for more,
            // with encryption running without the GIL, so that other interpreter threads proceed meanwhile
            let accepted = ctx.detach(|| self.session.writer().write(remaining)).map_err(IoError::System)?;
            offset += accepted;

            self.flush(ctx)?;
        }

        Ok(())
    }

    /// Reads decrypted data, receiving more TLS records first if none is buffered.
    fn read(&mut self, ctx: &IoContext<'_, '_>, buffer: &mut [u8]) -> Result<usize, IoError> {
        loop {
            match self.session.reader().read(buffer) {
                Ok(count) => return Ok(count),
                Err(err) if err.kind() == ErrorKind::WouldBlock => {}

                // A connection closed without a TLS close alert ends the data as a clean close would,
                // the way Python's ssl module treats it for requests
                Err(err) if err.kind() == ErrorKind::UnexpectedEof => return Ok(0),
                Err(err) => return Err(IoError::System(err)),
            }

            // Whether the endpoint closed the connection is told by the next read of the session
            self.fill(ctx)?;
        }
    }

    /// Whether the TLS session is still open and has no unread data, processing any records that arrived
    /// since the previous response, such as session tickets.
    fn is_reusable(&mut self) -> bool {
        let mut probe = [0_u8; 1];

        loop {
            match self.session.read_tls(&mut self.tcp) {
                Err(err) if err.kind() == ErrorKind::WouldBlock => return true,
                Ok(0) | Err(_) => return false,
                Ok(_) => {}
            }

            if self.session.process_new_packets().is_err() {
                return false;
            }

            // Records that carry no data leave the session reusable, whereas data or a close alert do not
            match self.session.reader().read(&mut probe) {
                Err(err) if err.kind() == ErrorKind::WouldBlock => {}
                _ => return false,
            }
        }
    }
}

#[cfg(test)]
#[path = "stream_tests.rs"]
mod tests;
