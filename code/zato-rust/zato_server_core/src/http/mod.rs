//! HTTP/1.x server built on raw `libc` sockets with gevent cooperative scheduling.

#[allow(unsafe_code, reason = "libc accept4/close syscalls for non-blocking socket accept")]
mod accept;

/// HTTP connection handler - reads requests, dispatches to Python, writes responses.
mod connection;

/// HTTP header parsing and request context key mapping.
mod headers;

#[allow(unsafe_code, reason = "libc read/write syscalls for non-blocking socket I/O")]
/// Low-level fd I/O with gevent yield-on-block.
pub mod io;

/// Main `handle_http_request` Python entrypoint.
pub mod request;

/// HTTP response builder.
pub mod response;

#[allow(unsafe_code, reason = "libc socket/bind/listen/setsockopt syscalls for TCP listener setup")]
mod server;

#[allow(unsafe_code, reason = "libc socket/bind/listen/setsockopt syscalls for TCP listener setup")]
mod socket;

/// Unix domain socket listener - the socket file of the server, bound at start and removed at stop.
mod unix_socket;

pub use headers::extract_headers;
pub use request::fractional_micros;
pub use request::handle_http_request;
pub use request::make_cid_public;
pub use response::build_response_head;
pub use server::HTTPServer;
pub use server::set_process_name;

use pyo3::prelude::*;

/// Owned Python object handle.
pub(crate) type PyObject = Py<PyAny>;

use parking_lot::Mutex;
use std::sync::atomic::AtomicI32;

/// Transport of a listening socket, which decides how an accepted connection is configured and addressed.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum ListenerKind {
    /// TCP socket bound to the host and port of the server.
    Tcp,

    /// Unix domain socket bound to a filesystem path.
    Unix,
}

/// Listening socket of the HTTP server, together with the gevent IO watcher of its accept loop.
pub(crate) struct Listener {
    /// Transport of the listening socket.
    pub kind: ListenerKind,

    /// File descriptor of the listening socket (-1 when not listening).
    pub fd: AtomicI32,

    /// Gevent IO watcher of the listening socket, whose wait is cancelled on shutdown to end the accept loop.
    pub watcher: Mutex<Option<PyObject>>,
}

impl Listener {
    /// Creates a listener of the given transport that does not listen yet.
    const fn new(kind: ListenerKind) -> Self {
        Self {
            kind,
            fd: AtomicI32::new(-1),
            watcher: Mutex::new(None),
        }
    }
}

/// TCP listener of the server, always present while the server runs.
pub(crate) static TCP_LISTENER: Listener = Listener::new(ListenerKind::Tcp);

/// Unix domain socket listener of the server, present only when the server is given a socket path.
pub(crate) static UNIX_LISTENER: Listener = Listener::new(ListenerKind::Unix);

/// Every listener of the server, in the order in which a stop closes them.
pub(crate) static LISTENERS: [&Listener; 2] = [&TCP_LISTENER, &UNIX_LISTENER];

/// Value of `REMOTE_ADDR` for a request accepted on the Unix domain socket, which has no peer IP address.
///
/// The address of the client is in the `X-Zato-Forwarded-For` header that the load balancer sets.
pub(crate) const UNIX_REMOTE_ADDR: &str = "127.0.0.1";

/// Value of `REMOTE_PORT` for a request accepted on the Unix domain socket, which has no peer port.
pub(crate) const UNIX_REMOTE_PORT: &str = "0";

/// Permission bits of the Unix domain socket file - read and write for the owning user only.
pub(crate) const UNIX_SOCKET_MODE: u32 = 0o600;

/// Maximum HTTP headers parsed per request.
pub(crate) const MAX_HEADERS: usize = 96;

/// Stack buffer size for `libc::read` calls.
pub(crate) const READ_BUF: usize = 16384;

/// Listen backlog (pending connections queue depth) of the TCP and Unix domain socket listeners.
pub(crate) const LISTEN_BACKLOG: libc::c_int = 2048;

/// Maximum connections accepted per event loop iteration before yielding to gevent.
pub(crate) const MAX_BATCH_ACCEPT: usize = 256;

/// Gevent IO event constant for read readiness.
pub(crate) const GEVENT_IO_READ: i32 = 1;

/// Gevent IO event constant for write readiness.
pub(crate) const GEVENT_IO_WRITE: i32 = 2;
