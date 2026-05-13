//! HTTP connection handler.
//!
//! Reads requests, parses with `httparse`, dispatches to the Python request handler,
//! and writes responses back over the same fd.

use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

use super::headers::set_header;
use super::io::{GeventLoop, fd_read, fd_write_all, header_value_eq, parse_content_length};
use super::response::{ResponseParts, build_response, build_response_headers_only};
use super::{MAX_HEADERS, MAX_REQUEST_SIZE, PyObject};

/// Context for handling a single HTTP connection.
pub(super) struct ConnectionCtx<'conn> {
    /// File descriptor for the accepted socket.
    pub fd: i32,
    /// Remote client IP address.
    pub remote_addr: &'conn str,
    /// Remote client port.
    pub remote_port: &'conn str,
    /// Python callback that processes parsed requests.
    pub request_handler: &'conn PyObject,
    /// Server software string for the `Server` response header.
    pub server_software: &'conn str,
}

/// HTTP chunked transfer terminator sent after the last iterator chunk.
const CHUNKED_TERMINATOR: &[u8] = b"0\r\n\r\n";

/// Writes an HTTP chunked frame for a single data chunk.
///
/// Format: `{hex_length}\r\n{data}\r\n`
fn write_chunked_frame(py: Python<'_>, fd: i32, chunk: &[u8], gev: &GeventLoop<'_>) -> PyResult<()> {
    // Format the chunk length as hex ..
    let header = format!("{:x}\r\n", chunk.len());

    // .. write the length prefix ..
    fd_write_all(py, fd, header.as_bytes(), gev)?;

    // .. write the chunk data ..
    fd_write_all(py, fd, chunk, gev)?;

    // .. and write the trailing CRLF.
    fd_write_all(py, fd, b"\r\n", gev)
}

/// Drains a Python iterator over the socket as HTTP chunked frames.
///
/// Each value yielded by the iterator must be `bytes`. After `StopIteration`,
/// the chunked terminator `0\r\n\r\n` is written. On write errors (EPIPE,
/// ECONNRESET), the loop breaks silently because the client has disconnected.
fn stream_iterator(py: Python<'_>, fd: i32, iterator: &Bound<'_, PyAny>, gev: &GeventLoop<'_>) -> PyResult<()> {
    loop {
        // Pull the next chunk from the Python iterator ..
        let next_result = iterator.call_method0(intern!(py, "__next__"));
        match next_result {
            Ok(chunk_obj) => {
                let chunk_bytes: &[u8] = chunk_obj.extract()?;
                let write_result = write_chunked_frame(py, fd, chunk_bytes, gev);

                // .. if the client disconnected, stop streaming ..
                if let Err(ref write_error) = write_result {
                    if is_client_disconnect(write_error) {
                        break;
                    }
                    return write_result;
                }

                // .. yield to gevent so other greenlets can run.
                let io_watcher = gev.loop_obj.call_method1(intern!(py, "io"), (fd, super::GEVENT_IO_WRITE))?;
                gev.hub.call_method1(intern!(py, "wait"), (&io_watcher,))?;
            }
            Err(ref error) if error.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) => {
                // .. iterator exhausted, send the chunked terminator.
                let _write = fd_write_all(py, fd, CHUNKED_TERMINATOR, gev);
                break;
            }
            Err(error) => return Err(error),
        }
    }
    Ok(())
}

/// Checks whether a `PyErr` represents a client disconnect (EPIPE or ECONNRESET).
fn is_client_disconnect(error: &PyErr) -> bool {
    let message = error.to_string();
    message.contains("Broken pipe") || message.contains("Connection reset")
}

/// Drives one HTTP keep-alive connection.
///
/// Reads requests in a loop, parses them, dispatches to the Python handler,
/// and writes back the response. Returns when the client closes the connection
/// or `Connection: close` is seen.
#[expect(
    clippy::indexing_slicing,
    reason = "path slice indices come from find('?') and httparse header_len which guarantee bounds"
)]
pub(super) fn handle_connection(py: Python<'_>, ctx: &ConnectionCtx<'_>) -> PyResult<()> {
    let hub = py.import("gevent")?.call_method0("get_hub")?;
    let loop_obj = hub.getattr(intern!(py, "loop"))?;
    let gev = GeventLoop { hub, loop_obj };

    let mut buf: Vec<u8> = Vec::with_capacity(4096);
    let mut resp: Vec<u8> = Vec::with_capacity(512);

    loop {
        if buf.is_empty() {
            let bytes_read = fd_read(py, ctx.fd, &mut buf, &gev)?;
            if bytes_read == 0 {
                return Ok(());
            }
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
                    if let Some(query_pos) = path.find('?') {
                        dict.set_item(intern!(py, "PATH_INFO"), &path[..query_pos])?;
                        dict.set_item(intern!(py, "QUERY_STRING"), &path[query_pos + 1..])?;
                    } else {
                        dict.set_item(intern!(py, "PATH_INFO"), path)?;
                        dict.set_item(intern!(py, "QUERY_STRING"), "")?;
                    }
                    dict.set_item(intern!(py, "RAW_URI"), path)?;
                    dict.set_item(intern!(py, "SERVER_PROTOCOL"), if ver == 0 { "HTTP/1.0" } else { "HTTP/1.1" })?;
                    dict.set_item(intern!(py, "SERVER_SOFTWARE"), ctx.server_software)?;
                    dict.set_item(intern!(py, "REMOTE_ADDR"), ctx.remote_addr)?;
                    dict.set_item(intern!(py, "REMOTE_PORT"), ctx.remote_port)?;

                    let mut content_len: usize = 0;
                    let mut keep_alive_flag = ver >= 1;
                    for header in req.headers.iter() {
                        set_header(py, &dict, header.name, header.value)?;
                        if header.name.eq_ignore_ascii_case("content-length") {
                            content_len = parse_content_length(header.value);
                        } else if header.name.eq_ignore_ascii_case("connection") {
                            keep_alive_flag = header_value_eq(header.value, b"keep-alive");
                        }
                    }
                    break (hlen, content_len, keep_alive_flag, ver, dict);
                }
                Ok(httparse::Status::Partial) => {
                    if buf.len() >= MAX_REQUEST_SIZE {
                        return Err(pyo3::exceptions::PyValueError::new_err("request too large"));
                    }
                    let bytes_read = fd_read(py, ctx.fd, &mut buf, &gev)?;
                    if bytes_read == 0 {
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
            let bytes_read = fd_read(py, ctx.fd, &mut buf, &gev)?;
            if bytes_read == 0 {
                return Err(pyo3::exceptions::PyConnectionError::new_err("closed"));
            }
        }
        dict.set_item(intern!(py, "zato.http.raw_request"), PyBytes::new(py, &buf[header_len..end]))?;
        dict.set_item(intern!(py, "zato.socket_fd"), ctx.fd)?;

        let result = ctx.request_handler.call1(py, (&dict,))?;

        {
            let tup = result.bind(py);
            let status_obj = tup.get_item(0)?;
            let status: &str = status_obj.extract()?;
            let hdrs = tup.get_item(1)?;
            let body_obj = tup.get_item(2)?;
            let py_headers = hdrs.cast::<PyDict>().ok();

            if body_obj.is_instance_of::<PyBytes>() {
                // Normal request/response path - full body available ..
                let body: &[u8] = body_obj.extract()?;
                build_response(
                    &ResponseParts {
                        version,
                        status_str: status,
                        py_headers,
                        body,
                        keep_alive,
                    },
                    &mut resp,
                )?;
                fd_write_all(py, ctx.fd, &resp, &gev)?;
            } else {
                // .. streaming path - element 2 is a Python iterator yielding bytes chunks.
                build_response_headers_only(
                    &ResponseParts {
                        version,
                        status_str: status,
                        py_headers,
                        body: b"",
                        keep_alive,
                    },
                    &mut resp,
                )?;
                fd_write_all(py, ctx.fd, &resp, &gev)?;
                stream_iterator(py, ctx.fd, &body_obj, &gev)?;
            }
        }

        if !keep_alive {
            return Ok(());
        }

        if end < buf.len() {
            buf.drain(..end);
        } else {
            buf.clear();
        }
    }
}
