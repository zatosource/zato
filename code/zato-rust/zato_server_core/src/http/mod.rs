//! HTTP/1.x server built on raw `libc` sockets with gevent cooperative scheduling.

#[allow(unsafe_code, reason = "libc accept4/close syscalls for non-blocking socket accept")]
mod accept;

/// HTTP connection handler - reads requests, dispatches to Python, writes responses.
mod connection;

/// HTTP header parsing and WSGI environ key mapping.
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

pub use server::HTTPServer;
pub use headers::extract_headers;
pub use request::handle_http_request;
pub use request::make_cid_public;

use pyo3::prelude::*;

/// Owned Python object handle.
pub(crate) type PyObject = Py<PyAny>;

use std::sync::atomic::AtomicI32;
use parking_lot::Mutex;

/// File descriptor of the listening TCP socket (-1 when not listening).
pub(crate) static LISTEN_FD: AtomicI32 = AtomicI32::new(-1);

/// Gevent IO watcher for the listen socket - stopped on shutdown to break the accept loop.
pub(crate) static ACCEPT_WATCHER: Mutex<Option<PyObject>> = Mutex::new(None);

/// Maximum HTTP headers parsed per request.
pub(crate) const MAX_HEADERS: usize = 96;

/// Stack buffer size for `libc::read` calls.
pub(crate) const READ_BUF: usize = 16384;

/// Upper bound on total request size to prevent memory exhaustion.
pub(crate) const MAX_REQUEST_SIZE: usize = 1_048_576;

/// TCP listen backlog (pending connections queue depth).
pub(crate) const LISTEN_BACKLOG: libc::c_int = 2048;

/// Maximum connections accepted per event loop iteration before yielding to gevent.
pub(crate) const MAX_BATCH_ACCEPT: usize = 256;

/// Gevent IO event constant for read readiness.
pub(crate) const GEVENT_IO_READ: i32 = 1;

/// Gevent IO event constant for write readiness.
pub(crate) const GEVENT_IO_WRITE: i32 = 2;
