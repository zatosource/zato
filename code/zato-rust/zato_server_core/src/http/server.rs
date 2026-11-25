//! Python-visible `HTTPServer` class and lifecycle helpers.

use parking_lot::Mutex;
use pyo3::exceptions::{PyOSError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyCFunction, PyDict, PyTuple};
use std::ffi::CString;
use std::sync::Arc;
use std::sync::atomic::Ordering::Relaxed;

use super::accept::{AcceptCtx, accept_loop};
use super::socket::create_listen_socket;
use super::unix_socket::{create_unix_listen_socket, remove_bound_socket_file};
use super::{LISTENERS, PyObject, TCP_LISTENER, UNIX_LISTENER};

/// Main Python-visible HTTP server class.
///
/// Binds a TCP listener, and a Unix domain socket listener when given a socket path, and dispatches requests via gevent.
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

    /// Filesystem path of the Unix domain socket that the server listens on in addition to the TCP address, if configured.
    unix_socket_path: Option<String>,
}

/// Greenlet that runs the accept loop of the Unix listener, together with the error that ended the loop, if any.
struct UnixAcceptTask {
    /// gevent `Greenlet` that runs the accept loop.
    greenlet: PyObject,

    /// Error that ended the accept loop, recorded by the greenlet so that `serve_forever` raises it.
    loop_error: Arc<Mutex<Option<PyErr>>>,
}

impl UnixAcceptTask {
    /// Ends the accept loop of the Unix listener, waits for its greenlet and returns the error that ended the loop, if any.
    fn finish(self, py: Python<'_>) -> PyResult<()> {
        // A TCP loop that ended on an error leaves the Unix loop waiting on its listener, so it is woken here
        close_listeners();
        cancel_accept_waits(py)?;

        self.greenlet.call_method0(py, "join")?;

        // The lock is held only to take the error
        let taken_error = self.loop_error.lock().take();
        taken_error.map_or(Ok(()), Err)
    }
}

#[pymethods]
impl HTTPServer {
    /// Creates a new server instance (does not start listening yet).
    ///
    /// `bind_address` is the `(host, port)` of the TCP listener, and `unix_socket_path`, when not `None`,
    /// is the path of the Unix domain socket that the server listens on as well.
    #[new]
    #[pyo3(signature = (bind_address, request_handler, server_software, max_msg_size, unix_socket_path))]
    fn new(
        bind_address: (String, u16),
        request_handler: PyObject,
        server_software: String,
        max_msg_size: usize,
        unix_socket_path: Option<String>,
    ) -> Self {
        let (host, port) = bind_address;
        Self {
            request_handler,
            server_software,
            host,
            port,
            max_msg_size,
            unix_socket_path,
        }
    }

    /// Binds the sockets and runs the accept loops, blocking the current greenlet until stopped.
    ///
    /// The TCP loop runs in the current greenlet and the Unix loop, if configured, in a greenlet of its own.
    fn serve_forever<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let tcp_fd = create_listen_socket(&self.host, self.port)?;
        TCP_LISTENER.fd.store(tcp_fd, Relaxed);

        // A Unix listener that cannot be started leaves no TCP listener behind
        let unix_task = match self.start_unix_listener(py) {
            Ok(task) => task,
            Err(err) => {
                close_listeners();
                return Err(err);
            }
        };

        let ctx = AcceptCtx {
            request_handler: &self.request_handler,
            server_software: &self.server_software,
            max_msg_size: self.max_msg_size,
        };
        let tcp_result = accept_loop(py, &TCP_LISTENER, &ctx);

        // The TCP loop returned, on a stop or on an error, and the Unix loop returns as well before the server does
        let unix_result = unix_task.map_or(Ok(()), |task| task.finish(py));

        close_listeners();
        tcp_result?;
        unix_result?;
        Ok(py.None().into_bound(py))
    }

    /// Closes the listeners, removes the Unix socket file and wakes the accept loops, so that `serve_forever` returns.
    #[expect(clippy::unused_self, reason = "PyO3 method signature requires &self")]
    fn stop<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        close_listeners();
        cancel_accept_waits(py)?;
        Ok(py.None().into_bound(py))
    }
}

impl HTTPServer {
    /// Binds the Unix domain socket, if a path is configured, and spawns the greenlet of its accept loop.
    fn start_unix_listener(&self, py: Python<'_>) -> PyResult<Option<UnixAcceptTask>> {
        // Without a socket path the server listens on TCP only
        let Some(path) = &self.unix_socket_path else {
            return Ok(None);
        };

        let unix_fd = create_unix_listen_socket(path)?;
        UNIX_LISTENER.fd.store(unix_fd, Relaxed);

        let task = self.spawn_unix_accept_loop(py)?;
        Ok(Some(task))
    }

    /// Spawns the greenlet that runs the accept loop of the Unix listener.
    fn spawn_unix_accept_loop(&self, py: Python<'_>) -> PyResult<UnixAcceptTask> {
        let handler_ref = self.request_handler.clone_ref(py);
        let software = self.server_software.clone();
        let max_msg_size = self.max_msg_size;

        let loop_error = Arc::new(Mutex::new(None));
        let greenlet_error = Arc::clone(&loop_error);

        let run_loop = PyCFunction::new_closure(
            py,
            None,
            None,
            move |args: &Bound<'_, PyTuple>, _kw: Option<&Bound<'_, PyDict>>| -> PyResult<()> {
                let py = args.py();
                let ctx = AcceptCtx {
                    request_handler: &handler_ref,
                    server_software: &software,
                    max_msg_size,
                };

                // The error ends the TCP loop as well, and serve_forever raises it once both loops returned
                if let Err(err) = accept_loop(py, &UNIX_LISTENER, &ctx) {
                    *greenlet_error.lock() = Some(err);
                    close_listeners();
                    cancel_accept_waits(py)?;
                }
                Ok(())
            },
        )?;

        let gevent = py.import("gevent")?;
        let greenlet = gevent.call_method1("spawn", (run_loop,))?;

        Ok(UnixAcceptTask {
            greenlet: greenlet.unbind(),
            loop_error,
        })
    }
}

impl Drop for HTTPServer {
    fn drop(&mut self) {
        close_listeners();
    }
}

/// Sets the name that `ps` and `top` list for the process to its role.
///
/// The roles are `zato-arbiter`, `zato-config` and `zato-worker`. The name is set through `PR_SET_NAME`
/// of the calling thread, which Linux truncates to 15 bytes.
#[pyfunction]
pub fn set_process_name(name: &str) -> PyResult<()> {
    // A name with a NUL byte inside it has no C form
    let c_name = CString::new(name).map_err(|err| PyValueError::new_err(err.to_string()))?;
    rustix::thread::set_name(&c_name).map_err(|err| PyOSError::new_err(err.to_string()))
}

/// Closes every listener and removes the socket file of the Unix listener.
///
/// The file descriptor of each listener is atomically swapped to -1 and closed if it was valid.
pub(super) fn close_listeners() {
    for listener in LISTENERS {
        let fd = listener.fd.swap(-1, Relaxed);
        if fd >= 0 {
            // SAFETY: fd was a valid socket obtained from libc::socket or socket2 and
            // the atomic swap guarantees only one caller closes it.
            unsafe {
                libc::close(fd);
            }
        }
    }

    remove_bound_socket_file();
}

/// Wakes the greenlet of each accept loop that waits on the gevent IO watcher of its listening socket.
///
/// The hub throws `cancel_wait_ex` into that greenlet and then closes the watcher. Stopping the watcher instead
/// would leave the greenlet waiting forever, because a stopped watcher never switches back to it.
pub(super) fn cancel_accept_waits(py: Python<'_>) -> PyResult<()> {
    for listener in LISTENERS {
        // The lock is held only to take the watcher, and is released before the hub is called
        let taken_watcher = listener.watcher.lock().take();

        // A loop that already returned, or never started, has cleared its watcher and has nothing to wake
        if let Some(watcher) = taken_watcher {
            let gevent = py.import("gevent")?;
            let hub = gevent.call_method0("get_hub")?;

            // The accept loop sees the listener closed once it wakes, so the error it receives ends it
            let cancel_error = py.import("gevent.socket")?.getattr("cancel_wait_ex")?;
            let close_watcher = true;
            hub.call_method1("cancel_wait", (watcher, cancel_error, close_watcher))?;
        }
    }

    Ok(())
}
