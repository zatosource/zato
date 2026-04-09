use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use std::fmt::Write as FmtWrite;

const MAX_HEADERS: usize = 128;
const INITIAL_BUF_SIZE: usize = 8192;
const MAX_REQUEST_SIZE: usize = 1_048_576; // 1 MB header limit

#[pyclass]
pub struct ConnectionHandler {
    callback: PyObject,
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

    /// Called by gevent StreamServer for each accepted connection.
    /// `socket` is a gevent socket object, `address` is (host, port).
    fn handle(&self, py: Python<'_>, socket: &Bound<'_, PyAny>, address: &Bound<'_, PyAny>) -> PyResult<()> {
        let remote_addr: String = address.get_item(0)?.extract()?;
        let remote_port: u16 = address.get_item(1)?.extract()?;

        let result = self.handle_connection(py, socket, &remote_addr, remote_port);

        // Always close the socket, regardless of outcome
        let _ = socket.call_method0("close");

        match result {
            Ok(()) => Ok(()),
            Err(e) => {
                // Connection errors (client disconnect, broken pipe) are expected — don't propagate
                let msg = format!("{}", e);
                if msg.contains("Connection reset")
                    || msg.contains("Broken pipe")
                    || msg.contains("timed out")
                    || msg.contains("empty request")
                {
                    Ok(())
                } else {
                    Err(e)
                }
            }
        }
    }
}

impl ConnectionHandler {
    fn handle_connection(
        &self,
        py: Python<'_>,
        socket: &Bound<'_, PyAny>,
        remote_addr: &str,
        remote_port: u16,
    ) -> PyResult<()> {
        let mut buf = Vec::with_capacity(INITIAL_BUF_SIZE);
        let mut keep_alive = true;

        while keep_alive {
            let (method, path, version, headers, body, consumed) =
                self.read_request(py, socket, &mut buf)?;

            keep_alive = self.should_keep_alive(version, &headers);

            let http_environ =
                self.build_environ(py, &method, &path, version, &headers, &body, remote_addr, remote_port)?;

            let response = self.callback.call1(py, (http_environ,))?;

            let (status, resp_headers, resp_body) = self.unpack_response(py, &response)?;

            self.write_response(py, socket, version, keep_alive, &status, &resp_headers, &resp_body)?;

            // Shift any trailing bytes (pipelined request) to the front
            buf.drain(..consumed);
        }

        Ok(())
    }

    /// Reads bytes from the socket until we have a complete HTTP request
    /// (headers + body per Content-Length). Returns parsed components and
    /// total byte count consumed from `buf`.
    fn read_request(
        &self,
        py: Python<'_>,
        socket: &Bound<'_, PyAny>,
        buf: &mut Vec<u8>,
    ) -> PyResult<(String, String, u8, Vec<(String, String)>, Vec<u8>, usize)> {
        loop {
            // Try to parse what we have
            let mut parsed_headers = [httparse::EMPTY_HEADER; MAX_HEADERS];
            let mut req = httparse::Request::new(&mut parsed_headers);

            match req.parse(buf) {
                Ok(httparse::Status::Complete(header_len)) => {
                    let method = req.method.unwrap_or("GET").to_string();
                    let path = req.path.unwrap_or("/").to_string();
                    let version = req.version.unwrap_or(1);

                    let mut headers: Vec<(String, String)> = Vec::with_capacity(req.headers.len());
                    let mut content_length: usize = 0;

                    for h in req.headers.iter() {
                        let name = h.name.to_string();
                        let val = String::from_utf8_lossy(h.value).to_string();
                        if h.name.eq_ignore_ascii_case("content-length") {
                            content_length = val.trim().parse().unwrap_or(0);
                        }
                        headers.push((name, val));
                    }

                    let total_needed = header_len + content_length;

                    // Do we have the full body yet?
                    if buf.len() < total_needed {
                        // Need more data for the body
                        self.recv_into(py, socket, buf, total_needed - buf.len())?;
                    }

                    let body = buf[header_len..header_len + content_length].to_vec();
                    return Ok((method, path, version, headers, body, total_needed));
                }
                Ok(httparse::Status::Partial) => {
                    if buf.len() >= MAX_REQUEST_SIZE {
                        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                            "Request headers too large",
                        ));
                    }
                    // Need more data
                    self.recv_into(py, socket, buf, 0)?;
                }
                Err(e) => {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "HTTP parse error: {}",
                        e
                    )));
                }
            }
        }
    }

    /// Receive data from the gevent socket into `buf`.
    /// If `min_bytes` > 0, keeps reading until we have at least that many additional bytes.
    fn recv_into(
        &self,
        py: Python<'_>,
        socket: &Bound<'_, PyAny>,
        buf: &mut Vec<u8>,
        min_bytes: usize,
    ) -> PyResult<()> {
        let target = if min_bytes > 0 {
            buf.len() + min_bytes
        } else {
            buf.len() + 1 // at least one byte
        };

        while buf.len() < target {
            let chunk: Vec<u8> = socket
                .call_method1("recv", (INITIAL_BUF_SIZE,))?
                .extract()?;
            if chunk.is_empty() {
                return Err(PyErr::new::<pyo3::exceptions::PyConnectionError, _>(
                    "empty request",
                ));
            }
            buf.extend_from_slice(&chunk);

            // Allow gevent to schedule other greenlets
            py.check_signals()?;
        }

        Ok(())
    }

    fn should_keep_alive(&self, version: u8, headers: &[(String, String)]) -> bool {
        for (name, val) in headers {
            if name.eq_ignore_ascii_case("connection") {
                return val.trim().eq_ignore_ascii_case("keep-alive");
            }
        }
        // HTTP/1.1 defaults to keep-alive, HTTP/1.0 does not
        version >= 1
    }

    fn build_environ(
        &self,
        py: Python<'_>,
        method: &str,
        path: &str,
        version: u8,
        headers: &[(String, String)],
        body: &[u8],
        remote_addr: &str,
        remote_port: u16,
    ) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);

        dict.set_item("REQUEST_METHOD", method)?;

        // Split path and query string
        if let Some(qpos) = path.find('?') {
            dict.set_item("PATH_INFO", &path[..qpos])?;
            dict.set_item("QUERY_STRING", &path[qpos + 1..])?;
        } else {
            dict.set_item("PATH_INFO", path)?;
            dict.set_item("QUERY_STRING", "")?;
        }

        dict.set_item("RAW_URI", path)?;

        let proto = if version == 0 {
            "HTTP/1.0"
        } else {
            "HTTP/1.1"
        };
        dict.set_item("SERVER_PROTOCOL", proto)?;
        dict.set_item("SERVER_SOFTWARE", &self.server_software)?;

        dict.set_item("REMOTE_ADDR", remote_addr)?;
        dict.set_item("REMOTE_PORT", remote_port.to_string())?;

        for (name, val) in headers {
            let upper = name.to_uppercase().replace('-', "_");
            if upper == "CONTENT_TYPE" {
                dict.set_item("CONTENT_TYPE", val)?;
            } else if upper == "CONTENT_LENGTH" {
                dict.set_item("CONTENT_LENGTH", val)?;
            } else {
                let key = format!("HTTP_{}", upper);
                dict.set_item(key, val)?;
            }
        }

        dict.set_item("zato.http.raw_request", PyBytes::new(py, body))?;

        Ok(dict.into())
    }

    fn unpack_response(
        &self,
        py: Python<'_>,
        response: &Py<PyAny>,
    ) -> PyResult<(String, Vec<(String, String)>, Vec<u8>)> {
        let tuple = response.bind(py);
        let status: String = tuple.get_item(0)?.extract()?;
        let headers_dict = tuple.get_item(1)?;
        let body: Vec<u8> = tuple.get_item(2)?.extract()?;

        let mut headers = Vec::new();
        if let Ok(dict) = headers_dict.downcast::<PyDict>() {
            for (k, v) in dict.iter() {
                let key: String = k.extract()?;
                let val: String = v.extract()?;
                headers.push((key, val));
            }
        }

        Ok((status, headers, body))
    }

    fn write_response(
        &self,
        py: Python<'_>,
        socket: &Bound<'_, PyAny>,
        version: u8,
        keep_alive: bool,
        status: &str,
        headers: &[(String, String)],
        body: &[u8],
    ) -> PyResult<()> {
        let proto = if version == 0 { "HTTP/1.0" } else { "HTTP/1.1" };

        let mut resp = String::with_capacity(256 + body.len());
        let _ = write!(resp, "{} {}\r\n", proto, status);

        let mut has_content_length = false;
        let mut has_connection = false;

        for (k, v) in headers {
            let _ = write!(resp, "{}: {}\r\n", k, v);
            if k.eq_ignore_ascii_case("content-length") {
                has_content_length = true;
            }
            if k.eq_ignore_ascii_case("connection") {
                has_connection = true;
            }
        }

        if !has_content_length {
            let _ = write!(resp, "Content-Length: {}\r\n", body.len());
        }
        if !has_connection {
            let conn_val = if keep_alive { "keep-alive" } else { "close" };
            let _ = write!(resp, "Connection: {}\r\n", conn_val);
        }

        resp.push_str("\r\n");

        // Build the full response bytes: header string + body
        let mut out = resp.into_bytes();
        out.extend_from_slice(body);

        let py_bytes = PyBytes::new(py, &out);
        socket.call_method1("sendall", (py_bytes,))?;

        Ok(())
    }
}

#[pymodule]
fn zato_server_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ConnectionHandler>()?;
    Ok(())
}
