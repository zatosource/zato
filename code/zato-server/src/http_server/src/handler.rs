use bytes::BytesMut;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use std::os::unix::io::RawFd;

use crate::http_parser::{self, ParseError, ParsedRequest};
use crate::http_response;

/// Determines whether the connection should be kept alive based on
/// the HTTP version and Connection header value.
fn should_keep_alive(version: u8, headers: &std::collections::HashMap<String, String>) -> bool {
    let conn = headers.get("HTTP_CONNECTION").map(|s| s.to_lowercase());
    match conn.as_deref() {
        Some("close") => false,
        Some("keep-alive") => true,
        _ => version == 1, // HTTP/1.1 defaults to keep-alive
    }
}

/// Builds a Python dict (http_environ) from a parsed HTTP request.
fn build_http_environ<'py>(
    py: Python<'py>,
    req: &ParsedRequest,
    remote_addr: &str,
    remote_port: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);

    dict.set_item("REQUEST_METHOD", &req.method)?;
    dict.set_item("PATH_INFO", &req.path)?;
    dict.set_item("QUERY_STRING", &req.query_string)?;
    dict.set_item("RAW_URI", &req.raw_uri)?;
    dict.set_item("CONTENT_TYPE", &req.content_type)?;
    dict.set_item("REMOTE_ADDR", remote_addr)?;
    dict.set_item("REMOTE_PORT", remote_port)?;

    let protocol = if req.version == 0 {
        "HTTP/1.0"
    } else {
        "HTTP/1.1"
    };
    dict.set_item("SERVER_PROTOCOL", protocol)?;

    if let Some(len) = req.content_length {
        dict.set_item("CONTENT_LENGTH", len.to_string())?;
    } else {
        dict.set_item("CONTENT_LENGTH", "")?;
    }

    for (key, value) in &req.headers {
        dict.set_item(key, value)?;
    }

    dict.set_item("zato.http.raw_request", PyBytes::new(py, &req.body))?;

    Ok(dict)
}

#[pyclass]
pub struct ConnectionHandler {
    callback: PyObject,
    #[pyo3(get)]
    server_software: String,
}

#[pymethods]
impl ConnectionHandler {
    #[new]
    fn new(callback: PyObject, server_software: String) -> Self {
        ConnectionHandler {
            callback,
            server_software,
        }
    }

    /// Called by gevent StreamServer per connection (one greenlet each).
    /// `socket` is a gevent socket, `address` is a (host, port) tuple.
    fn handle(&self, py: Python<'_>, socket: &Bound<'_, PyAny>, address: &Bound<'_, PyAny>) -> PyResult<()> {
        let fd: RawFd = socket.call_method0("fileno")?.extract()?;

        let addr_tuple = address.downcast::<PyTuple>()?;
        let remote_addr: String = addr_tuple.get_item(0)?.extract()?;
        let remote_port: String = format!("{}", addr_tuple.get_item(1)?.extract::<i64>()?);

        let mut leftover = BytesMut::new();

        loop {
            let parsed = match py.allow_threads(|| {
                http_parser::read_and_parse_with_leftover(fd, &mut leftover)
            }) {
                Ok(p) => p,
                Err(ParseError::IoError(ref e))
                    if e.kind() == std::io::ErrorKind::UnexpectedEof =>
                {
                    break;
                }
                Err(ParseError::Invalid(_)) => {
                    let _ = py.allow_threads(|| {
                        http_response::write_error_response(fd, 400, 1)
                    });
                    break;
                }
                Err(_) => break,
            };

            let keep_alive = should_keep_alive(parsed.version, &parsed.headers);

            let environ = build_http_environ(py, &parsed, &remote_addr, &remote_port)?;

            let result = self.callback.call1(py, (environ,));

            match result {
                Ok(ret) => {
                    let tuple = ret.bind(py).downcast::<PyTuple>()?;
                    let status: String = tuple.get_item(0)?.extract()?;

                    let headers_dict = tuple.get_item(1)?.downcast::<PyDict>()?.clone();
                    let mut headers_vec: Vec<(String, String)> = Vec::new();
                    for (k, v) in headers_dict.iter() {
                        headers_vec.push((k.extract::<String>()?, v.extract::<String>()?));
                    }

                    let body: Vec<u8> = tuple.get_item(2)?.extract()?;

                    let version = parsed.version;
                    py.allow_threads(|| {
                        http_response::write_response(
                            fd,
                            &status,
                            &headers_vec,
                            &body,
                            version,
                            keep_alive,
                        )
                    })
                    .map_err(|e| {
                        pyo3::exceptions::PyIOError::new_err(format!("write failed: {}", e))
                    })?;
                }
                Err(_) => {
                    let version = parsed.version;
                    let _ = py.allow_threads(|| {
                        http_response::write_error_response(fd, 500, version)
                    });
                }
            }

            if !keep_alive {
                break;
            }
        }

        Ok(())
    }
}
