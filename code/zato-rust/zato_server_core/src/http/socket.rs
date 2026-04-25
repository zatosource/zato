//! TCP socket creation and binding using raw `libc` syscalls.

use pyo3::prelude::*;

use super::LISTEN_BACKLOG;

/// Sets a socket option, logging a warning on failure.
#[expect(
    clippy::as_conversions,
    reason = "pointer casts required by the libc setsockopt API"
)]
pub(super) fn setsockopt_logged(fd: i32, level: i32, optname: i32, val: i32, label: &str) {
    // SAFETY: fd is a valid socket, val is a stack-local i32 whose address and size
    // are correctly passed to setsockopt. The kernel reads exactly sizeof(c_int) bytes.
    unsafe {
        let ptr = (&raw const val).cast::<libc::c_void>();
        let len = std::mem::size_of::<libc::c_int>() as libc::socklen_t;
        if libc::setsockopt(fd, level, optname, ptr, len) < 0 {
            let err = std::io::Error::last_os_error();
            log::warn!("setsockopt {label} on fd {fd}: {err}");
        }
    }
}

/// Creates a non-blocking, `CLOEXEC` TCP listener socket bound to `host:port`.
#[expect(
    clippy::as_conversions,
    reason = "pointer and integer casts required by the libc socket/bind/listen API"
)]
pub(super) fn create_listen_socket(host: &str, port: u16) -> PyResult<i32> {
    // SAFETY: all libc calls below operate on the fd returned by socket().
    // On failure each call checks the return value and closes fd before returning an error,
    // preventing fd leaks. addr is a stack-local sockaddr_in whose pointer and size
    // are correctly passed to bind.
    unsafe {
        let fd = libc::socket(
            libc::AF_INET,
            libc::SOCK_STREAM | libc::SOCK_NONBLOCK | libc::SOCK_CLOEXEC,
            0,
        );
        if fd < 0 {
            return Err(pyo3::exceptions::PyOSError::new_err("socket() failed"));
        }

        setsockopt_logged(fd, libc::SOL_SOCKET, libc::SO_REUSEADDR, 1, "SO_REUSEADDR");
        setsockopt_logged(fd, libc::SOL_SOCKET, libc::SO_REUSEPORT, 1, "SO_REUSEPORT");

        let addr = make_sockaddr(host, port)?;
        let addr_ptr = (&raw const addr).cast::<libc::sockaddr>();
        let addr_len = std::mem::size_of::<libc::sockaddr_in>() as libc::socklen_t;

        if libc::bind(fd, addr_ptr, addr_len) < 0 {
            let err = std::io::Error::last_os_error();
            libc::close(fd);
            return Err(pyo3::exceptions::PyOSError::new_err(format!(
                "bind({host}:{port}) failed: {err}"
            )));
        }

        if libc::listen(fd, LISTEN_BACKLOG) < 0 {
            let err = std::io::Error::last_os_error();
            libc::close(fd);
            return Err(pyo3::exceptions::PyOSError::new_err(format!(
                "listen() failed: {err}"
            )));
        }

        Ok(fd)
    }
}

/// Converts a host string and port into a `sockaddr_in`.
#[expect(
    clippy::as_conversions,
    reason = "sa_family_t cast required by the libc sockaddr_in struct"
)]
fn make_sockaddr(host: &str, port: u16) -> PyResult<libc::sockaddr_in> {
    let ip_addr: std::net::Ipv4Addr = if host == "0.0.0.0" || host.is_empty() {
        std::net::Ipv4Addr::UNSPECIFIED
    } else if host == "127.0.0.1" || host == "localhost" {
        std::net::Ipv4Addr::LOCALHOST
    } else {
        host.parse().map_err(|err| {
            pyo3::exceptions::PyValueError::new_err(format!("bad host: {err}"))
        })?
    };
    let octets = ip_addr.octets();
    // SAFETY: zeroed sockaddr_in is a valid initial state per POSIX.
    let mut addr: libc::sockaddr_in = unsafe { std::mem::zeroed() };
    addr.sin_family = libc::AF_INET as libc::sa_family_t;
    addr.sin_port = port.to_be();
    addr.sin_addr.s_addr = u32::from_ne_bytes(octets);
    Ok(addr)
}
