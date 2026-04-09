use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use pyo3::intern;

const MAX_HEADERS: usize = 96;
const RECV_SIZE: usize = 16384;
const MAX_REQUEST_SIZE: usize = 1_048_576;

#[pyclass]
pub struct ConnectionHandler {
    callback: PyObject,
    server_software: String,
}

#[pymethods]
impl ConnectionHandler {
    #[new]
    fn new(callback: PyObject, server_software: String) -> Self {
        Self { callback, server_software }
    }

    fn handle(
        &self,
        py: Python<'_>,
        socket: &Bound<'_, PyAny>,
        address: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let remote_addr: String = address.get_item(0)?.extract()?;
        let remote_port = address.get_item(1)?.extract::<u16>()?.to_string();

        let r = self.serve(py, socket, &remote_addr, &remote_port);
        let _ = socket.call_method0(intern!(py, "close"));

        r.or_else(|e| if is_conn_err(&e) { Ok(()) } else { Err(e) })
    }
}

#[inline]
fn is_conn_err(e: &PyErr) -> bool {
    let s = e.to_string();
    s.contains("onnection") || s.contains("roken pipe")
        || s.contains("imed out") || s.contains("losed")
}

impl ConnectionHandler {
    fn serve(
        &self,
        py: Python<'_>,
        sock: &Bound<'_, PyAny>,
        remote_addr: &str,
        remote_port: &str,
    ) -> PyResult<()> {
        let mut buf: Vec<u8> = Vec::with_capacity(4096);
        let mut resp: Vec<u8> = Vec::with_capacity(512);

        loop {
            // ── recv ──
            if buf.is_empty() {
                let chunk: Vec<u8> = sock
                    .call_method1(intern!(py, "recv"), (RECV_SIZE,))?
                    .extract()?;
                if chunk.is_empty() {
                    return Ok(());
                }
                buf = chunk;
            }

            // ── parse headers + build environ in a single pass ──
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
                        dict.set_item(
                            intern!(py, "SERVER_PROTOCOL"),
                            if ver == 0 { "HTTP/1.0" } else { "HTTP/1.1" },
                        )?;
                        dict.set_item(intern!(py, "SERVER_SOFTWARE"), &self.server_software)?;
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
                            return Err(pyo3::exceptions::PyValueError::new_err(
                                "request too large",
                            ));
                        }
                        let more: Vec<u8> = sock
                            .call_method1(intern!(py, "recv"), (RECV_SIZE,))?
                            .extract()?;
                        if more.is_empty() {
                            return Err(pyo3::exceptions::PyConnectionError::new_err("closed"));
                        }
                        buf.extend(more);
                    }
                    Err(_) => {
                        return Err(pyo3::exceptions::PyValueError::new_err("bad request"));
                    }
                }
            };

            // ── read remaining body ──
            let end = header_len + content_length;
            while buf.len() < end {
                let more: Vec<u8> = sock
                    .call_method1(intern!(py, "recv"), (RECV_SIZE,))?
                    .extract()?;
                if more.is_empty() {
                    return Err(pyo3::exceptions::PyConnectionError::new_err("closed"));
                }
                buf.extend(more);
            }

            dict.set_item(
                intern!(py, "zato.http.raw_request"),
                PyBytes::new(py, &buf[header_len..end]),
            )?;

            // ── dispatch ──
            let result = self.callback.call1(py, (&dict,))?;

            // ── format + send response ──
            {
                let tup = result.bind(py);
                let status_obj = tup.get_item(0)?;
                let status: &str = status_obj.extract()?;
                let hdrs = tup.get_item(1)?;
                let body_obj = tup.get_item(2)?;
                let body: &[u8] = body_obj.extract()?;

                resp.clear();

                // Status line
                resp.extend_from_slice(if version == 0 {
                    b"HTTP/1.0 "
                } else {
                    b"HTTP/1.1 "
                });
                resp.extend_from_slice(status.as_bytes());
                resp.extend_from_slice(b"\r\n");

                // Response headers from Python
                let mut has_cl = false;
                let mut has_conn = false;

                if let Ok(d) = hdrs.downcast::<PyDict>() {
                    for (k, v) in d.iter() {
                        let kk: &str = k.extract()?;
                        let vv: &str = v.extract()?;
                        resp.extend_from_slice(kk.as_bytes());
                        resp.extend_from_slice(b": ");
                        resp.extend_from_slice(vv.as_bytes());
                        resp.extend_from_slice(b"\r\n");
                        if !has_cl && kk.eq_ignore_ascii_case("content-length") {
                            has_cl = true;
                        }
                        if !has_conn && kk.eq_ignore_ascii_case("connection") {
                            has_conn = true;
                        }
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

                sock.call_method1(intern!(py, "sendall"), (PyBytes::new(py, &resp),))?;
            }

            if !keep_alive {
                return Ok(());
            }

            // Shift remaining bytes (pipelined request)
            if end < buf.len() {
                buf.drain(..end);
            } else {
                buf.clear();
            }
        }
    }
}

// ── header → environ key mapping ──

#[inline]
fn set_header(
    py: Python<'_>,
    dict: &Bound<'_, PyDict>,
    name: &str,
    value: &[u8],
) -> PyResult<()> {
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

// ── helpers ──

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
    if trimmed.len() != target.len() {
        return false;
    }
    trimmed
        .iter()
        .zip(target)
        .all(|(a, b)| a.to_ascii_lowercase() == *b)
}

#[inline]
fn trim_ows(b: &[u8]) -> &[u8] {
    let s = b.iter().position(|&c| c != b' ' && c != b'\t').unwrap_or(b.len());
    let e = b.iter().rposition(|&c| c != b' ' && c != b'\t').map_or(s, |p| p + 1);
    &b[s..e]
}

#[inline]
fn push_usize(buf: &mut Vec<u8>, n: usize) {
    if n == 0 {
        buf.push(b'0');
        return;
    }
    let mut tmp = [0u8; 20];
    let mut pos = tmp.len();
    let mut v = n;
    while v > 0 {
        pos -= 1;
        tmp[pos] = b'0' + (v % 10) as u8;
        v /= 10;
    }
    buf.extend_from_slice(&tmp[pos..]);
}

#[pymodule]
fn zato_server_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ConnectionHandler>()?;
    Ok(())
}
