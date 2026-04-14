use pyo3::prelude::*;
use pyo3::types::{PyCFunction, PyDict, PyTuple};
use pyo3::intern;
use std::sync::atomic::Ordering::Relaxed;

use super::{LISTEN_FD, ACCEPT_WATCHER, PyObject, MAX_BATCH_ACCEPT, GEVENT_IO_READ};
use super::socket::setsockopt_logged;
use super::connection::handle_connection;

fn is_connection_error(e: &PyErr) -> bool {
    let s = e.to_string();
    let lower = s.to_ascii_lowercase();
    lower.contains("connection reset")
        || lower.contains("connection refused")
        || lower.contains("connection aborted")
        || lower.contains("broken pipe")
        || lower.contains("timed out")
        || lower.contains("connection closed")
}

pub(super) fn accept_loop(
    py: Python<'_>,
    listen_fd: i32,
    request_handler: &PyObject,
    server_software: &str,
) -> PyResult<()> {
    let gevent = py.import("gevent")?;
    let hub = gevent.call_method0("get_hub")?;
    let loop_obj = hub.getattr(intern!(py, "loop"))?;
    let accept_watcher = loop_obj.call_method1(intern!(py, "io"), (listen_fd, GEVENT_IO_READ))?;

    {
        if let Ok(mut guard) = ACCEPT_WATCHER.lock() {
            *guard = Some(accept_watcher.clone().unbind());
        }
    }

    struct WatcherCleanup;
    impl Drop for WatcherCleanup {
        fn drop(&mut self) {
            if let Ok(mut guard) = ACCEPT_WATCHER.lock() {
                *guard = None;
            }
        }
    }
    let _cleanup = WatcherCleanup;

    loop {
        if LISTEN_FD.load(Relaxed) < 0 {
            return Ok(());
        }

        for _ in 0..MAX_BATCH_ACCEPT {
            let mut client_addr: libc::sockaddr_in = unsafe { std::mem::zeroed() };
            let mut addr_len = std::mem::size_of::<libc::sockaddr_in>() as libc::socklen_t;

            let client_fd = unsafe {
                libc::accept4(
                    listen_fd,
                    &mut client_addr as *mut _ as *mut libc::sockaddr,
                    &mut addr_len,
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

            setsockopt_logged(client_fd, libc::IPPROTO_TCP, libc::TCP_NODELAY, 1, "TCP_NODELAY");

            let remote_addr = format!(
                "{}.{}.{}.{}",
                client_addr.sin_addr.s_addr as u8,
                (client_addr.sin_addr.s_addr >> 8) as u8,
                (client_addr.sin_addr.s_addr >> 16) as u8,
                (client_addr.sin_addr.s_addr >> 24) as u8,
            );
            let remote_port = u16::from_be(client_addr.sin_port).to_string();

            let cb = request_handler.clone_ref(py);
            let sw = server_software.to_string();

            let handler = PyCFunction::new_closure(
                py, None, None,
                move |args: &Bound<'_, PyTuple>, _kw: Option<&Bound<'_, PyDict>>| -> PyResult<()> {
                    let py = args.py();
                    let r = handle_connection(py, client_fd, &remote_addr, &remote_port, &cb, &sw);
                    unsafe { libc::close(client_fd); }
                    r.or_else(|e| {
                        if is_connection_error(&e) { Ok(()) } else { Err(e) }
                    })
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
