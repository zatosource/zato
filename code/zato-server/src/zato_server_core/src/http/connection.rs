use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use pyo3::intern;

use super::{PyObject, MAX_HEADERS, MAX_REQUEST_SIZE};
use super::headers::set_header;
use super::io::{fd_read, fd_write_all, parse_content_length, header_value_eq};
use super::response::build_response;

pub(super) fn handle_connection(
    py: Python<'_>,
    fd: i32,
    remote_addr: &str,
    remote_port: &str,
    request_handler: &PyObject,
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
                            cl = parse_content_length(h.value);
                        } else if h.name.eq_ignore_ascii_case("connection") {
                            ka = header_value_eq(h.value, b"keep-alive");
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

        let result = request_handler.call1(py, (&dict,))?;

        {
            let tup = result.bind(py);
            let status_obj = tup.get_item(0)?;
            let status: &str = status_obj.extract()?;
            let hdrs = tup.get_item(1)?;
            let body_obj = tup.get_item(2)?;
            let body: &[u8] = body_obj.extract()?;

            let py_headers = hdrs.cast::<PyDict>().ok();
            build_response(version, status, py_headers.as_deref(), body, keep_alive, &mut resp)?;
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
