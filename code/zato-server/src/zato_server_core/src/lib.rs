mod models;
mod config_store;

use pyo3::prelude::*;
use pyo3::types::{PyCFunction, PyBytes, PyDict, PyTuple};
use pyo3::intern;

type PyObject = Py<PyAny>;

use std::sync::atomic::{AtomicI32, Ordering::Relaxed};

static LISTEN_FD: AtomicI32 = AtomicI32::new(-1);

const MAX_HEADERS: usize = 96;
const READ_BUF: usize = 16384;
const MAX_REQUEST_SIZE: usize = 1_048_576;
const LISTEN_BACKLOG: libc::c_int = 2048;
const MAX_BATCH_ACCEPT: usize = 256;

// ── HTTPServer ──

#[pyclass]
pub struct HTTPServer {
    callback: PyObject,
    server_software: String,
    host: String,
    port: u16,
}

#[pymethods]
impl HTTPServer {
    #[new]
    fn new(host: String, port: u16, callback: PyObject, server_software: String) -> Self {
        Self { callback, server_software, host, port }
    }

    fn serve_forever<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        set_process_name();
        let listen_fd = create_listen_socket(&self.host, self.port)?;
        LISTEN_FD.store(listen_fd, Relaxed);
        let result = accept_loop(py, listen_fd, &self.callback, &self.server_software);
        close_listen_fd();
        result?;
        Ok(py.None().into_bound(py))
    }

    fn stop<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        close_listen_fd();
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

fn close_listen_fd() {
    let fd = LISTEN_FD.swap(-1, Relaxed);
    if fd >= 0 {
        unsafe { libc::close(fd); }
    }
}

// ── socket setup ──

fn create_listen_socket(host: &str, port: u16) -> PyResult<i32> {
    unsafe {
        let fd = libc::socket(
            libc::AF_INET,
            libc::SOCK_STREAM | libc::SOCK_NONBLOCK | libc::SOCK_CLOEXEC,
            0,
        );
        if fd < 0 {
            return Err(pyo3::exceptions::PyOSError::new_err("socket() failed"));
        }

        let one: libc::c_int = 1;
        let one_ptr = &one as *const _ as *const libc::c_void;
        let one_len = std::mem::size_of::<libc::c_int>() as libc::socklen_t;

        libc::setsockopt(fd, libc::SOL_SOCKET, libc::SO_REUSEADDR, one_ptr, one_len);
        libc::setsockopt(fd, libc::SOL_SOCKET, libc::SO_REUSEPORT, one_ptr, one_len);

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

// ── accept loop (runs in calling greenlet — blocks via hub.wait) ──

fn accept_loop(
    py: Python<'_>,
    listen_fd: i32,
    callback: &PyObject,
    server_software: &str,
) -> PyResult<()> {
    let gevent = py.import("gevent")?;
    let hub = gevent.call_method0("get_hub")?;
    let loop_obj = hub.getattr(intern!(py, "loop"))?;
    let accept_watcher = loop_obj.call_method1(intern!(py, "io"), (listen_fd, 1))?;

    loop {
        // Batch accept
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
                continue; // transient error, skip
            }

            // TCP_NODELAY
            unsafe {
                let one: libc::c_int = 1;
                libc::setsockopt(
                    client_fd, libc::IPPROTO_TCP, libc::TCP_NODELAY,
                    &one as *const _ as *const libc::c_void,
                    std::mem::size_of::<libc::c_int>() as libc::socklen_t,
                );
            }

            let remote_addr = format!(
                "{}.{}.{}.{}",
                client_addr.sin_addr.s_addr as u8,
                (client_addr.sin_addr.s_addr >> 8) as u8,
                (client_addr.sin_addr.s_addr >> 16) as u8,
                (client_addr.sin_addr.s_addr >> 24) as u8,
            );
            let remote_port = u16::from_be(client_addr.sin_port).to_string();

            // Spawn handler greenlet
            let cb = callback.clone_ref(py);
            let sw = server_software.to_string();

            let handler = PyCFunction::new_closure(
                py, None, None,
                move |args: &Bound<'_, PyTuple>, _kw: Option<&Bound<'_, PyDict>>| -> PyResult<()> {
                    let py = args.py();
                    let r = handle_connection(py, client_fd, &remote_addr, &remote_port, &cb, &sw);
                    unsafe { libc::close(client_fd); }
                    r.or_else(|e| {
                        let s = e.to_string();
                        if s.contains("onnection") || s.contains("roken pipe")
                            || s.contains("imed out") || s.contains("losed") {
                            Ok(())
                        } else {
                            Err(e)
                        }
                    })
                },
            )?;

            gevent.call_method1(intern!(py, "spawn_raw"), (handler,))?;
        }

        // Wait for more incoming connections
        hub.call_method1(intern!(py, "wait"), (&accept_watcher,))?;
    }
}

// ── connection handler (runs as a greenlet) ──

fn handle_connection(
    py: Python<'_>,
    fd: i32,
    remote_addr: &str,
    remote_port: &str,
    callback: &PyObject,
    server_software: &str,
) -> PyResult<()> {
    let hub = py.import("gevent")?.call_method0("get_hub")?;
    let loop_obj = hub.getattr(intern!(py, "loop"))?;

    let mut buf: Vec<u8> = Vec::with_capacity(4096);
    let mut resp: Vec<u8> = Vec::with_capacity(512);

    loop {
        if buf.is_empty() {
            let n = fd_read(py, fd, &mut buf, &hub, &loop_obj)?;
            if n == 0 { return Ok(()); }
        }

        let (header_len, content_length, keep_alive, version, dict) = loop {
            let mut hdr = [httparse::EMPTY_HEADER; MAX_HEADERS];
            let mut req = httparse::Request::new(&mut hdr);

            match req.parse(&buf) {
                Ok(httparse::Status::Complete(hlen)) => {
                    let method = req.method.unwrap_or("GET");
                    let path = req.path.unwrap_or("/");
                    let ver = req.version.unwrap_or(1);

                    let dict = PyDict::new(py);
                    dict.set_item(intern!(py, "REQUEST_METHOD"), method)?;
                    if let Some(q) = path.find('?') {
                        dict.set_item(intern!(py, "PATH_INFO"), &path[..q])?;
                        dict.set_item(intern!(py, "QUERY_STRING"), &path[q + 1..])?;
                    } else {
                        dict.set_item(intern!(py, "PATH_INFO"), path)?;
                        dict.set_item(intern!(py, "QUERY_STRING"), "")?;
                    }
                    dict.set_item(intern!(py, "RAW_URI"), path)?;
                    dict.set_item(intern!(py, "SERVER_PROTOCOL"),
                        if ver == 0 { "HTTP/1.0" } else { "HTTP/1.1" })?;
                    dict.set_item(intern!(py, "SERVER_SOFTWARE"), server_software)?;
                    dict.set_item(intern!(py, "REMOTE_ADDR"), remote_addr)?;
                    dict.set_item(intern!(py, "REMOTE_PORT"), remote_port)?;

                    let mut cl: usize = 0;
                    let mut ka = ver >= 1;
                    for h in req.headers.iter() {
                        set_header(py, &dict, h.name, h.value)?;
                        if h.name.eq_ignore_ascii_case("content-length") {
                            cl = parse_cl(h.value);
                        } else if h.name.eq_ignore_ascii_case("connection") {
                            ka = val_eq_ci(h.value, b"keep-alive");
                        }
                    }
                    break (hlen, cl, ka, ver, dict);
                }
                Ok(httparse::Status::Partial) => {
                    if buf.len() >= MAX_REQUEST_SIZE {
                        return Err(pyo3::exceptions::PyValueError::new_err("request too large"));
                    }
                    let n = fd_read(py, fd, &mut buf, &hub, &loop_obj)?;
                    if n == 0 {
                        return Err(pyo3::exceptions::PyConnectionError::new_err("closed"));
                    }
                }
                Err(_) => {
                    return Err(pyo3::exceptions::PyValueError::new_err("bad request"));
                }
            }
        };

        let end = header_len + content_length;
        while buf.len() < end {
            let n = fd_read(py, fd, &mut buf, &hub, &loop_obj)?;
            if n == 0 {
                return Err(pyo3::exceptions::PyConnectionError::new_err("closed"));
            }
        }
        dict.set_item(
            intern!(py, "zato.http.raw_request"),
            PyBytes::new(py, &buf[header_len..end]),
        )?;

        let result = callback.call1(py, (&dict,))?;

        {
            let tup = result.bind(py);
            let status_obj = tup.get_item(0)?;
            let status: &str = status_obj.extract()?;
            let hdrs = tup.get_item(1)?;
            let body_obj = tup.get_item(2)?;
            let body: &[u8] = body_obj.extract()?;

            resp.clear();
            resp.extend_from_slice(if version == 0 { b"HTTP/1.0 " } else { b"HTTP/1.1 " });
            resp.extend_from_slice(status.as_bytes());
            resp.extend_from_slice(b"\r\n");

            let mut has_cl = false;
            let mut has_conn = false;
            if let Ok(d) = hdrs.cast::<PyDict>() {
                for (k, v) in d.iter() {
                    let kk: &str = k.extract()?;
                    let vv: &str = v.extract()?;
                    resp.extend_from_slice(kk.as_bytes());
                    resp.extend_from_slice(b": ");
                    resp.extend_from_slice(vv.as_bytes());
                    resp.extend_from_slice(b"\r\n");
                    if !has_cl && kk.eq_ignore_ascii_case("content-length") { has_cl = true; }
                    if !has_conn && kk.eq_ignore_ascii_case("connection") { has_conn = true; }
                }
            }
            if !has_cl {
                resp.extend_from_slice(b"Content-Length: ");
                push_usize(&mut resp, body.len());
                resp.extend_from_slice(b"\r\n");
            }
            if !has_conn {
                resp.extend_from_slice(if keep_alive {
                    b"Connection: keep-alive\r\n" as &[u8]
                } else {
                    b"Connection: close\r\n"
                });
            }
            resp.extend_from_slice(b"\r\n");
            resp.extend_from_slice(body);
        }

        fd_write_all(py, fd, &resp, &hub, &loop_obj)?;

        if !keep_alive { return Ok(()); }

        if end < buf.len() {
            buf.drain(..end);
        } else {
            buf.clear();
        }
    }
}

// ── direct fd I/O with gevent cooperation ──

fn fd_read(
    py: Python<'_>,
    fd: i32,
    buf: &mut Vec<u8>,
    hub: &Bound<'_, PyAny>,
    loop_obj: &Bound<'_, PyAny>,
) -> PyResult<usize> {
    let mut tmp = [0u8; READ_BUF];
    loop {
        let n = unsafe { libc::read(fd, tmp.as_mut_ptr() as *mut libc::c_void, tmp.len()) };
        if n > 0 {
            buf.extend_from_slice(&tmp[..n as usize]);
            return Ok(n as usize);
        }
        if n == 0 {
            return Ok(0);
        }
        let err = std::io::Error::last_os_error();
        if err.kind() == std::io::ErrorKind::WouldBlock {
            let w = loop_obj.call_method1(intern!(py, "io"), (fd, 1))?;
            hub.call_method1(intern!(py, "wait"), (&w,))?;
            continue;
        }
        if err.raw_os_error() == Some(libc::EINTR) {
            continue;
        }
        return Err(pyo3::exceptions::PyConnectionError::new_err(
            format!("read: {}", err)
        ));
    }
}

fn fd_write_all(
    py: Python<'_>,
    fd: i32,
    data: &[u8],
    hub: &Bound<'_, PyAny>,
    loop_obj: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let mut off = 0;
    while off < data.len() {
        let n = unsafe {
            libc::write(fd, data[off..].as_ptr() as *const libc::c_void, data.len() - off)
        };
        if n > 0 {
            off += n as usize;
            continue;
        }
        if n == 0 {
            return Err(pyo3::exceptions::PyConnectionError::new_err("write returned 0"));
        }
        let err = std::io::Error::last_os_error();
        if err.kind() == std::io::ErrorKind::WouldBlock {
            let w = loop_obj.call_method1(intern!(py, "io"), (fd, 2))?;
            hub.call_method1(intern!(py, "wait"), (&w,))?;
            continue;
        }
        if err.raw_os_error() == Some(libc::EINTR) {
            continue;
        }
        return Err(pyo3::exceptions::PyConnectionError::new_err(
            format!("write: {}", err)
        ));
    }
    Ok(())
}

// ── header helpers ──

#[inline]
fn set_header(py: Python<'_>, dict: &Bound<'_, PyDict>, name: &str, value: &[u8]) -> PyResult<()> {
    let val = String::from_utf8_lossy(value);
    if name.eq_ignore_ascii_case("Host") {
        dict.set_item(intern!(py, "HTTP_HOST"), &*val)
    } else if name.eq_ignore_ascii_case("User-Agent") {
        dict.set_item(intern!(py, "HTTP_USER_AGENT"), &*val)
    } else if name.eq_ignore_ascii_case("Accept") {
        dict.set_item(intern!(py, "HTTP_ACCEPT"), &*val)
    } else if name.eq_ignore_ascii_case("Accept-Encoding") {
        dict.set_item(intern!(py, "HTTP_ACCEPT_ENCODING"), &*val)
    } else if name.eq_ignore_ascii_case("Accept-Language") {
        dict.set_item(intern!(py, "HTTP_ACCEPT_LANGUAGE"), &*val)
    } else if name.eq_ignore_ascii_case("Connection") {
        dict.set_item(intern!(py, "HTTP_CONNECTION"), &*val)
    } else if name.eq_ignore_ascii_case("Content-Type") {
        dict.set_item(intern!(py, "CONTENT_TYPE"), &*val)
    } else if name.eq_ignore_ascii_case("Content-Length") {
        dict.set_item(intern!(py, "CONTENT_LENGTH"), &*val)
    } else if name.eq_ignore_ascii_case("Authorization") {
        dict.set_item(intern!(py, "HTTP_AUTHORIZATION"), &*val)
    } else if name.eq_ignore_ascii_case("Cookie") {
        dict.set_item(intern!(py, "HTTP_COOKIE"), &*val)
    } else if name.eq_ignore_ascii_case("X-Forwarded-For") {
        dict.set_item(intern!(py, "HTTP_X_FORWARDED_FOR"), &*val)
    } else if name.eq_ignore_ascii_case("X-Forwarded-Proto") {
        dict.set_item(intern!(py, "HTTP_X_FORWARDED_PROTO"), &*val)
    } else if name.eq_ignore_ascii_case("X-Real-IP") {
        dict.set_item(intern!(py, "HTTP_X_REAL_IP"), &*val)
    } else if name.eq_ignore_ascii_case("Cache-Control") {
        dict.set_item(intern!(py, "HTTP_CACHE_CONTROL"), &*val)
    } else if name.eq_ignore_ascii_case("Origin") {
        dict.set_item(intern!(py, "HTTP_ORIGIN"), &*val)
    } else if name.eq_ignore_ascii_case("Referer") {
        dict.set_item(intern!(py, "HTTP_REFERER"), &*val)
    } else if name.eq_ignore_ascii_case("If-None-Match") {
        dict.set_item(intern!(py, "HTTP_IF_NONE_MATCH"), &*val)
    } else if name.eq_ignore_ascii_case("If-Modified-Since") {
        dict.set_item(intern!(py, "HTTP_IF_MODIFIED_SINCE"), &*val)
    } else if name.eq_ignore_ascii_case("Upgrade") {
        dict.set_item(intern!(py, "HTTP_UPGRADE"), &*val)
    } else if name.eq_ignore_ascii_case("X-Zato-CID") {
        dict.set_item(intern!(py, "HTTP_X_ZATO_CID"), &*val)
    } else {
        let mut key = String::with_capacity(5 + name.len());
        key.push_str("HTTP_");
        for b in name.bytes() {
            key.push(if b == b'-' { '_' } else { (b as char).to_ascii_uppercase() });
        }
        dict.set_item(key, &*val)
    }
}

#[inline]
fn parse_cl(b: &[u8]) -> usize {
    let mut n: usize = 0;
    for &c in b {
        match c {
            b'0'..=b'9' => n = n * 10 + (c - b'0') as usize,
            b' ' | b'\t' => {}
            _ => break,
        }
    }
    n
}

#[inline]
fn val_eq_ci(raw: &[u8], target: &[u8]) -> bool {
    let trimmed = trim_ows(raw);
    if trimmed.len() != target.len() { return false; }
    trimmed.iter().zip(target).all(|(a, b)| a.to_ascii_lowercase() == *b)
}

#[inline]
fn trim_ows(b: &[u8]) -> &[u8] {
    let s = b.iter().position(|&c| c != b' ' && c != b'\t').unwrap_or(b.len());
    let e = b.iter().rposition(|&c| c != b' ' && c != b'\t').map_or(s, |p| p + 1);
    &b[s..e]
}

#[inline]
fn push_usize(buf: &mut Vec<u8>, n: usize) {
    if n == 0 { buf.push(b'0'); return; }
    let mut tmp = [0u8; 20];
    let mut pos = tmp.len();
    let mut v = n;
    while v > 0 { pos -= 1; tmp[pos] = b'0' + (v % 10) as u8; v /= 10; }
    buf.extend_from_slice(&tmp[pos..]);
}

// ── module ──

#[pymodule]
fn zato_server_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<HTTPServer>()?;
    m.add_class::<config_store::ConfigStore>()?;
    Ok(())
}
