use pyo3::prelude::*;

use super::LISTEN_BACKLOG;

pub(super) fn setsockopt_logged(fd: i32, level: i32, optname: i32, val: i32, label: &str) {
    unsafe {
        let ptr = &val as *const _ as *const libc::c_void;
        let len = std::mem::size_of::<libc::c_int>() as libc::socklen_t;
        if libc::setsockopt(fd, level, optname, ptr, len) < 0 {
            let err = std::io::Error::last_os_error();
            log::warn!("setsockopt {} on fd {}: {}", label, fd, err);
        }
    }
}

pub(super) fn create_listen_socket(host: &str, port: u16) -> PyResult<i32> {
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
        let addr_ptr = &addr as *const _ as *const libc::sockaddr;
        let addr_len = std::mem::size_of::<libc::sockaddr_in>() as libc::socklen_t;

        if libc::bind(fd, addr_ptr, addr_len) < 0 {
            let err = std::io::Error::last_os_error();
            libc::close(fd);
            return Err(pyo3::exceptions::PyOSError::new_err(format!(
                "bind({}:{}) failed: {}", host, port, err
            )));
        }

        if libc::listen(fd, LISTEN_BACKLOG) < 0 {
            let err = std::io::Error::last_os_error();
            libc::close(fd);
            return Err(pyo3::exceptions::PyOSError::new_err(format!(
                "listen() failed: {}", err
            )));
        }

        Ok(fd)
    }
}

fn make_sockaddr(host: &str, port: u16) -> PyResult<libc::sockaddr_in> {
    let ip: std::net::Ipv4Addr = if host == "0.0.0.0" || host.is_empty() {
        std::net::Ipv4Addr::UNSPECIFIED
    } else if host == "127.0.0.1" || host == "localhost" {
        std::net::Ipv4Addr::LOCALHOST
    } else {
        host.parse().map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("bad host: {}", e))
        })?
    };
    let octets = ip.octets();
    let mut addr: libc::sockaddr_in = unsafe { std::mem::zeroed() };
    addr.sin_family = libc::AF_INET as libc::sa_family_t;
    addr.sin_port = port.to_be();
    addr.sin_addr.s_addr = u32::from_ne_bytes(octets);
    Ok(addr)
}
