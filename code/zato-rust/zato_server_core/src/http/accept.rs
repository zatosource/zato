//! Accept loop - accepts connections in batches on a TCP or Unix domain socket listener and spawns a gevent greenlet
//! per connection.

use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyCFunction, PyDict, PyTuple};
use std::net::Ipv4Addr;
use std::sync::atomic::Ordering::Relaxed;

use super::connection::{ConnectionCtx, handle_connection};
use super::socket::{setsockopt_logged, sockaddr_in_socklen};
use super::{GEVENT_IO_READ, Listener, ListenerKind, MAX_BATCH_ACCEPT, PyObject, UNIX_REMOTE_ADDR, UNIX_REMOTE_PORT};

/// Server-wide parameters of the connections that an accept loop spawns, the same for every listener.
pub(super) struct AcceptCtx<'ctx> {
    /// Python callable that receives `(request_ctx,)` and returns `(status, headers, body)`.
    pub request_handler: &'ctx PyObject,

    /// Value for the `SERVER_SOFTWARE` request context key.
    pub server_software: &'ctx str,

    /// Upper bound on total request size in bytes.
    pub max_msg_size: usize,
}

/// Connection accepted on a listening socket, with the `REMOTE_ADDR` and `REMOTE_PORT` of its requests.
struct AcceptedConnection {
    /// File descriptor of the accepted socket.
    fd: i32,

    /// Value of `REMOTE_ADDR` for the requests of the connection.
    remote_addr: String,

    /// Value of `REMOTE_PORT` for the requests of the connection.
    remote_port: String,
}

/// Outcome of a single `accept4` call on a listening socket.
enum AcceptOutcome {
    /// A connection was accepted.
    Accepted(AcceptedConnection),

    /// No connection is pending, the loop waits for the listener to become readable.
    Drained,

    /// The listening socket was closed by a stop of the server.
    Closed,

    /// A pending connection failed before it was accepted, the loop accepts the next one.
    Skipped,
}

/// Checks if a Python exception is a transient connection error that should be silently dropped.
fn is_connection_error(py_err: &PyErr) -> bool {
    let error_string = py_err.to_string();
    let lower = error_string.to_ascii_lowercase();
    lower.contains("connection reset")
        || lower.contains("connection refused")
        || lower.contains("connection aborted")
        || lower.contains("broken pipe")
        || lower.contains("timed out")
        || lower.contains("connection closed")
}

/// RAII guard that clears the gevent IO watcher of a listener on drop.
struct WatcherCleanup {
    /// Listener whose watcher is cleared.
    listener: &'static Listener,
}

impl Drop for WatcherCleanup {
    fn drop(&mut self) {
        let mut guard = self.listener.watcher.lock();
        *guard = None;
    }
}

/// Maps the error of a failed `accept4` call to the outcome that the accept loop acts on.
fn failed_accept_outcome() -> AcceptOutcome {
    let err = std::io::Error::last_os_error();
    if err.kind() == std::io::ErrorKind::WouldBlock {
        AcceptOutcome::Drained
    } else if err.raw_os_error() == Some(libc::EBADF) {
        AcceptOutcome::Closed
    } else {
        AcceptOutcome::Skipped
    }
}

/// Accepts one connection on a TCP listener, with `TCP_NODELAY` set and the IPv4 address of the peer.
fn accept_tcp(listen_fd: i32) -> PyResult<AcceptOutcome> {
    // SAFETY: client_addr is zeroed and its pointer + length are correctly
    // passed to accept4. The kernel fills in the address struct on success.
    let mut client_addr: libc::sockaddr_in = unsafe { std::mem::zeroed() };
    let mut addr_len = sockaddr_in_socklen()?;

    // SAFETY: listen_fd is a valid listening socket. accept4 returns a new fd
    // or -1 on error. SOCK_NONBLOCK|SOCK_CLOEXEC are set atomically.
    let client_fd = unsafe {
        libc::accept4(
            listen_fd,
            (&raw mut client_addr).cast::<libc::sockaddr>(),
            &raw mut addr_len,
            libc::SOCK_NONBLOCK | libc::SOCK_CLOEXEC,
        )
    };

    if client_fd < 0 {
        return Ok(failed_accept_outcome());
    }

    setsockopt_logged(client_fd, libc::IPPROTO_TCP, libc::TCP_NODELAY, 1, "TCP_NODELAY")?;

    // The kernel stores the address and the port in network byte order
    let remote_ip = Ipv4Addr::from(u32::from_be(client_addr.sin_addr.s_addr));
    let remote_port = u16::from_be(client_addr.sin_port);

    Ok(AcceptOutcome::Accepted(AcceptedConnection {
        fd: client_fd,
        remote_addr: remote_ip.to_string(),
        remote_port: remote_port.to_string(),
    }))
}

/// Accepts one connection on a Unix domain socket listener, whose peer has no IP address or port.
fn accept_unix(listen_fd: i32) -> AcceptOutcome {
    // SAFETY: listen_fd is a valid listening socket. Null address pointers tell accept4
    // not to report the peer address. SOCK_NONBLOCK|SOCK_CLOEXEC are set atomically.
    let client_fd = unsafe {
        libc::accept4(
            listen_fd,
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            libc::SOCK_NONBLOCK | libc::SOCK_CLOEXEC,
        )
    };

    if client_fd < 0 {
        return failed_accept_outcome();
    }

    AcceptOutcome::Accepted(AcceptedConnection {
        fd: client_fd,
        remote_addr: UNIX_REMOTE_ADDR.to_owned(),
        remote_port: UNIX_REMOTE_PORT.to_owned(),
    })
}

/// Spawns the greenlet that serves the requests of an accepted connection and closes its socket afterwards.
fn spawn_connection(py: Python<'_>, gevent: &Bound<'_, PyModule>, connection: AcceptedConnection, ctx: &AcceptCtx<'_>) -> PyResult<()> {
    let handler_ref = ctx.request_handler.clone_ref(py);
    let software = ctx.server_software.to_owned();
    let max_msg_size = ctx.max_msg_size;

    let handler = PyCFunction::new_closure(
        py,
        None,
        None,
        move |args: &Bound<'_, PyTuple>, _kw: Option<&Bound<'_, PyDict>>| -> PyResult<()> {
            let py = args.py();
            let conn_result = handle_connection(
                py,
                &ConnectionCtx {
                    fd: connection.fd,
                    remote_addr: &connection.remote_addr,
                    remote_port: &connection.remote_port,
                    request_handler: &handler_ref,
                    server_software: &software,
                    max_msg_size,
                },
            );
            // SAFETY: connection.fd is a valid socket obtained from accept4.
            // The closure owns the fd and this is the only place it is closed.
            unsafe {
                libc::close(connection.fd);
            }
            conn_result.or_else(|err| if is_connection_error(&err) { Ok(()) } else { Err(err) })
        },
    )?;

    gevent.call_method1(intern!(py, "spawn_raw"), (handler,))?;
    Ok(())
}

/// Main accept loop of one listener.
///
/// Registers a gevent IO watcher on the listening socket, accepts connections
/// in batches of up to `MAX_BATCH_ACCEPT`, and spawns a greenlet per connection.
/// Returns when the file descriptor of the listener is set to -1 (i.e. the server is stopped).
pub(super) fn accept_loop(py: Python<'_>, listener: &'static Listener, ctx: &AcceptCtx<'_>) -> PyResult<()> {
    let listen_fd = listener.fd.load(Relaxed);

    // A listener that a stop closed before its loop started has nothing to watch
    if listen_fd < 0 {
        return Ok(());
    }

    let gevent = py.import("gevent")?;
    let hub = gevent.call_method0("get_hub")?;
    let loop_obj = hub.getattr(intern!(py, "loop"))?;
    let accept_watcher = loop_obj.call_method1(intern!(py, "io"), (listen_fd, GEVENT_IO_READ))?;

    {
        let mut guard = listener.watcher.lock();
        *guard = Some(accept_watcher.clone().unbind());
    }

    let _cleanup = WatcherCleanup { listener };

    loop {
        if listener.fd.load(Relaxed) < 0 {
            return Ok(());
        }

        for _ in 0..MAX_BATCH_ACCEPT {
            let outcome = match listener.kind {
                ListenerKind::Tcp => accept_tcp(listen_fd)?,
                ListenerKind::Unix => accept_unix(listen_fd),
            };

            match outcome {
                AcceptOutcome::Accepted(connection) => spawn_connection(py, &gevent, connection, ctx)?,
                AcceptOutcome::Drained => break,
                AcceptOutcome::Closed => return Ok(()),
                AcceptOutcome::Skipped => {}
            }
        }

        if listener.fd.load(Relaxed) < 0 {
            return Ok(());
        }
        let wait_result = hub.call_method1(intern!(py, "wait"), (&accept_watcher,));
        if listener.fd.load(Relaxed) < 0 {
            return Ok(());
        }
        wait_result?;
    }
}
