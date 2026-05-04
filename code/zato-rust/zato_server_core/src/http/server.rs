//! Python-visible `HTTPServer` class and lifecycle helpers.

use pyo3::prelude::*;
use std::sync::atomic::Ordering::Relaxed;

use super::{LISTEN_FD, ACCEPT_WATCHER, PyObject};
use super::accept::accept_loop;
use super::socket::create_listen_socket;

/// Main Python-visible HTTP server class.
///
/// Binds a TCP listener and dispatches requests via gevent.
#[pyclass]
pub struct HTTPServer {
    /// Python callable that receives `(environ_dict,)` and returns `(status, headers, body)`.
    request_handler: PyObject,
    /// Value for the `SERVER_SOFTWARE` WSGI key.
    server_software: String,
    /// Bind address.
    host: String,
    /// Bind port.
    port: u16,
}

#[pymethods]
impl HTTPServer {
    /// Creates a new server instance (does not start listening yet).
    #[new]
    #[expect(clippy::missing_const_for_fn, reason = "PyO3 #[new] methods cannot be const")]
    fn new(host: String, port: u16, request_handler: PyObject, server_software: String) -> Self {
        Self { request_handler, server_software, host, port }
    }

    /// Binds the socket and enters the accept loop, blocking the current greenlet until stopped.
    fn serve_forever<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        set_process_name();
        let listen_fd = create_listen_socket(&self.host, self.port)?;
        LISTEN_FD.store(listen_fd, Relaxed);
        let result = accept_loop(py, listen_fd, &self.request_handler, &self.server_software);
        close_listen_fd();
        result?;
        Ok(py.None().into_bound(py))
    }

    /// Closes the listener and stops the accept watcher to break the accept loop.
    #[expect(clippy::unused_self, clippy::unnecessary_wraps, reason = "PyO3 method signature requires &self and PyResult return")]
    fn stop<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        close_listen_fd();
        stop_accept_watcher(py);
        Ok(py.None().into_bound(py))
    }
}

impl Drop for HTTPServer {
    fn drop(&mut self) {
        close_listen_fd();
    }
}

/// Sets the Linux process name to `zato-server` for visibility in `ps`/`top`.
fn set_process_name() {
    let _result = prctl::set_name("zato-server");
}

/// Atomically swaps `LISTEN_FD` to -1 and closes the old fd if it was valid.
pub(super) fn close_listen_fd() {
    let fd = LISTEN_FD.swap(-1, Relaxed);
    if fd >= 0 {
        // SAFETY: fd was a valid socket obtained from libc::socket/accept4 and
        // the atomic swap guarantees only one thread closes it.
        unsafe { libc::close(fd); }
    }
}

/// Stops the gevent IO watcher to unblock the accept loop.
pub(super) fn stop_accept_watcher(py: Python<'_>) {
    let mut guard = ACCEPT_WATCHER.lock();
    if let Some(watcher) = guard.take() {
        let _stop_result = watcher.call_method0(py, "stop");
    }
}
