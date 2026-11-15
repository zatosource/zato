//! Python-visible `HTTPServer` class and lifecycle helpers.

use pyo3::exceptions::{PyOSError, PyValueError};
use pyo3::prelude::*;
use std::ffi::CString;
use std::sync::atomic::Ordering::Relaxed;

use super::accept::accept_loop;
use super::socket::create_listen_socket;
use super::{ACCEPT_WATCHER, LISTEN_FD, PyObject};

/// Main Python-visible HTTP server class.
///
/// Binds a TCP listener and dispatches requests via gevent.
#[pyclass]
pub struct HTTPServer {
    /// Python callable that receives `(request_ctx,)` and returns `(status, headers, body)`.
    request_handler: PyObject,
    /// Value for the `SERVER_SOFTWARE` request context key.
    server_software: String,
    /// Bind address.
    host: String,
    /// Bind port.
    port: u16,
    /// Upper bound on total request size in bytes.
    max_msg_size: usize,
}

#[pymethods]
impl HTTPServer {
    /// Creates a new server instance (does not start listening yet).
    #[new]
    #[expect(clippy::missing_const_for_fn, reason = "PyO3 #[new] methods cannot be const")]
    fn new(host: String, port: u16, request_handler: PyObject, server_software: String, max_msg_size: usize) -> Self {
        Self {
            request_handler,
            server_software,
            host,
            port,
            max_msg_size,
        }
    }

    /// Binds the socket and enters the accept loop, blocking the current greenlet until stopped.
    fn serve_forever<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let listen_fd = create_listen_socket(&self.host, self.port)?;
        LISTEN_FD.store(listen_fd, Relaxed);
        let result = accept_loop(py, listen_fd, &self.request_handler, &self.server_software, self.max_msg_size);
        close_listen_fd();
        result?;
        Ok(py.None().into_bound(py))
    }

    /// Closes the listener and stops the accept watcher to break the accept loop.
    #[expect(
        clippy::unused_self,
        clippy::unnecessary_wraps,
        reason = "PyO3 method signature requires &self and PyResult return"
    )]
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

/// Sets the name that `ps` and `top` list for the process to its role.
///
/// The roles are `zato-arbiter`, `zato-worker-<slot>` and `zato-writer`. The name is set through `PR_SET_NAME`
/// of the calling thread, which Linux truncates to 15 bytes.
#[pyfunction]
pub fn set_process_name(name: &str) -> PyResult<()> {
    // A name with a NUL byte inside it has no C form
    let c_name = CString::new(name).map_err(|err| PyValueError::new_err(err.to_string()))?;
    rustix::thread::set_name(&c_name).map_err(|err| PyOSError::new_err(err.to_string()))
}

/// Atomically swaps `LISTEN_FD` to -1 and closes the old fd if it was valid.
pub(super) fn close_listen_fd() {
    let fd = LISTEN_FD.swap(-1, Relaxed);
    if fd >= 0 {
        // SAFETY: fd was a valid socket obtained from libc::socket/accept4 and
        // the atomic swap guarantees only one thread closes it.
        unsafe {
            libc::close(fd);
        }
    }
}

/// Stops the gevent IO watcher to unblock the accept loop.
pub(super) fn stop_accept_watcher(py: Python<'_>) {
    let mut guard = ACCEPT_WATCHER.lock();
    if let Some(watcher) = guard.take() {
        let _stop_result = watcher.call_method0(py, "stop");
    }
}
