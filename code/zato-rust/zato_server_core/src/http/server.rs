use pyo3::prelude::*;
use std::sync::atomic::Ordering::Relaxed;

use super::{LISTEN_FD, ACCEPT_WATCHER, PyObject};
use super::accept::accept_loop;
use super::socket::create_listen_socket;

#[pyclass]
pub struct HTTPServer {
    request_handler: PyObject,
    server_software: String,
    host: String,
    port: u16,
}

#[pymethods]
impl HTTPServer {
    #[new]
    fn new(host: String, port: u16, request_handler: PyObject, server_software: String) -> Self {
        Self { request_handler, server_software, host, port }
    }

    fn serve_forever<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        set_process_name();
        let listen_fd = create_listen_socket(&self.host, self.port)?;
        LISTEN_FD.store(listen_fd, Relaxed);
        let result = accept_loop(py, listen_fd, &self.request_handler, &self.server_software);
        close_listen_fd();
        result?;
        Ok(py.None().into_bound(py))
    }

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

fn set_process_name() {
    unsafe {
        let name = b"zato-server\0";
        libc::prctl(libc::PR_SET_NAME, name.as_ptr() as libc::c_ulong, 0, 0, 0);
    }
}

pub(super) fn close_listen_fd() {
    let fd = LISTEN_FD.swap(-1, Relaxed);
    if fd >= 0 {
        unsafe { libc::close(fd); }
    }
}

pub(super) fn stop_accept_watcher(py: Python<'_>) {
    if let Ok(mut guard) = ACCEPT_WATCHER.lock() {
        if let Some(watcher) = guard.take() {
            let _ = watcher.call_method0(py, "stop");
        }
    }
}
