//! Accept loop - accepts TCP connections in batches and spawns a gevent greenlet per connection.

use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyCFunction, PyDict, PyTuple};
use std::sync::atomic::Ordering::Relaxed;

use super::connection::{ConnectionCtx, handle_connection};
use super::socket::setsockopt_logged;
use super::{ACCEPT_WATCHER, GEVENT_IO_READ, LISTEN_FD, MAX_BATCH_ACCEPT, PyObject};

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

/// RAII guard that clears `ACCEPT_WATCHER` on drop.
struct WatcherCleanup;
impl Drop for WatcherCleanup {
    fn drop(&mut self) {
        let mut guard = ACCEPT_WATCHER.lock();
        *guard = None;
    }
}

/// Main accept loop.
///
/// Registers a gevent IO watcher on `listen_fd`, accepts connections
/// in batches of up to `MAX_BATCH_ACCEPT`, and spawns a greenlet per connection.
/// Returns when `LISTEN_FD` is set to -1 (i.e. the server is stopped).
#[expect(
    clippy::as_conversions,
    clippy::cast_possible_truncation,
    reason = "extracting individual octets from a 32-bit IPv4 address stored in network byte order"
)]
pub(super) fn accept_loop(py: Python<'_>, listen_fd: i32, request_handler: &PyObject, server_software: &str) -> PyResult<()> {
    let gevent = py.import("gevent")?;
    let hub = gevent.call_method0("get_hub")?;
    let loop_obj = hub.getattr(intern!(py, "loop"))?;
    let accept_watcher = loop_obj.call_method1(intern!(py, "io"), (listen_fd, GEVENT_IO_READ))?;

    {
        let mut guard = ACCEPT_WATCHER.lock();
        *guard = Some(accept_watcher.clone().unbind());
    }

    let _cleanup = WatcherCleanup;

    loop {
        if LISTEN_FD.load(Relaxed) < 0 {
            return Ok(());
        }

        for _ in 0..MAX_BATCH_ACCEPT {
            // SAFETY: client_addr is zeroed and its pointer + length are correctly
            // passed to accept4. The kernel fills in the address struct on success.
            let mut client_addr: libc::sockaddr_in = unsafe { std::mem::zeroed() };
            let mut addr_len = std::mem::size_of::<libc::sockaddr_in>() as libc::socklen_t;

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
                let err = std::io::Error::last_os_error();
                if err.kind() == std::io::ErrorKind::WouldBlock {
                    break;
                }
                if err.raw_os_error() == Some(libc::EBADF) {
                    return Ok(());
                }
                continue;
            }

            setsockopt_logged(client_fd, libc::IPPROTO_TCP, libc::TCP_NODELAY, 1, "TCP_NODELAY")?;

            let remote_addr = format!(
                "{}.{}.{}.{}",
                client_addr.sin_addr.s_addr as u8,
                (client_addr.sin_addr.s_addr >> 8) as u8,
                (client_addr.sin_addr.s_addr >> 16) as u8,
                (client_addr.sin_addr.s_addr >> 24) as u8,
            );
            let remote_port = u16::from_be(client_addr.sin_port).to_string();

            let handler_ref = request_handler.clone_ref(py);
            let software = server_software.to_string();

            let handler = PyCFunction::new_closure(
                py,
                None,
                None,
                move |args: &Bound<'_, PyTuple>, _kw: Option<&Bound<'_, PyDict>>| -> PyResult<()> {
                    let py = args.py();
                    let conn_result = handle_connection(
                        py,
                        &ConnectionCtx {
                            fd: client_fd,
                            remote_addr: &remote_addr,
                            remote_port: &remote_port,
                            request_handler: &handler_ref,
                            server_software: &software,
                        },
                    );
                    // SAFETY: client_fd is a valid socket obtained from accept4 above.
                    // The closure owns the fd and this is the only place it is closed.
                    unsafe {
                        libc::close(client_fd);
                    }
                    conn_result.or_else(|err| if is_connection_error(&err) { Ok(()) } else { Err(err) })
                },
            )?;

            gevent.call_method1(intern!(py, "spawn_raw"), (handler,))?;
        }

        if LISTEN_FD.load(Relaxed) < 0 {
            return Ok(());
        }
        let wait_result = hub.call_method1(intern!(py, "wait"), (&accept_watcher,));
        if LISTEN_FD.load(Relaxed) < 0 {
            return Ok(());
        }
        wait_result?;
    }
}
