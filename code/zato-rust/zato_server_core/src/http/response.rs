//! HTTP response builder - serializes status, headers and body into a byte buffer.

use http::StatusCode;
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Parses a status string like `"200 OK"` into an `http::StatusCode`.
pub fn parse_status_code(status_str: &str) -> StatusCode {
    let code_str = status_str.split_whitespace().next().map_or("200", |code| code);
    code_str.parse::<StatusCode>().unwrap_or(StatusCode::OK)
}

/// Parts of an HTTP response to serialize.
pub(super) struct ResponseParts<'resp, 'py> {
    /// HTTP version: 0 for HTTP/1.0, 1 for HTTP/1.1.
    pub version: u8,
    /// Status string like `"200 OK"`.
    pub status_str: &'resp str,
    /// Optional Python dict of response headers.
    pub py_headers: Option<&'resp Bound<'py, PyDict>>,
    /// Response body bytes.
    pub body: &'resp [u8],
    /// Whether to include `Connection: keep-alive`.
    pub keep_alive: bool,
}

/// Serializes a complete HTTP response (status line, headers, body) into `buf`.
///
/// Adds `Content-Length` and `Connection` headers if not already present.
pub(super) fn build_response(parts: &ResponseParts<'_, '_>, buf: &mut Vec<u8>) -> PyResult<()> {
    let status = parse_status_code(parts.status_str);

    buf.clear();

    let version_part = if parts.version == 0 {
        http::Version::HTTP_10
    } else {
        http::Version::HTTP_11
    };

    buf.extend_from_slice(match version_part {
        http::Version::HTTP_10 => b"HTTP/1.0 ",
        _ => b"HTTP/1.1 ",
    });
    buf.extend_from_slice(status.as_str().as_bytes());
    buf.push(b' ');
    buf.extend_from_slice(status.canonical_reason().unwrap_or("").as_bytes());
    buf.extend_from_slice(b"\r\n");

    let mut has_content_length = false;
    let mut has_connection = false;

    if let Some(headers_dict) = parts.py_headers {
        for (key_obj, val_obj) in headers_dict.iter() {
            let header_name: &str = key_obj.extract()?;
            let header_value: &str = val_obj.extract()?;

            if let (Ok(name), Ok(val)) = (
                http::header::HeaderName::from_bytes(header_name.as_bytes()),
                http::header::HeaderValue::from_str(header_value),
            ) {
                buf.extend_from_slice(name.as_str().as_bytes());
                buf.extend_from_slice(b": ");
                buf.extend_from_slice(val.as_bytes());
                buf.extend_from_slice(b"\r\n");

                if !has_content_length && name == http::header::CONTENT_LENGTH {
                    has_content_length = true;
                }
                if !has_connection && name == http::header::CONNECTION {
                    has_connection = true;
                }
            }
        }
    }

    if !has_content_length {
        buf.extend_from_slice(b"content-length: ");
        let _fmt = std::io::Write::write_fmt(buf, format_args!("{}", parts.body.len()));
        buf.extend_from_slice(b"\r\n");
    }
    if !has_connection {
        let conn_header: &[u8] = if parts.keep_alive {
            b"connection: keep-alive\r\n"
        } else {
            b"connection: close\r\n"
        };
        buf.extend_from_slice(conn_header);
    }
    buf.extend_from_slice(b"\r\n");
    buf.extend_from_slice(parts.body);

    Ok(())
}

/// Serializes only the HTTP response header block into `buf` for streaming responses.
///
/// Writes the status line, Python-supplied headers, `Transfer-Encoding: chunked`,
/// and the terminating blank line. Does not write any body and never adds `Content-Length`.
pub(super) fn build_response_headers_only(parts: &ResponseParts<'_, '_>, buf: &mut Vec<u8>) -> PyResult<()> {
    let status = parse_status_code(parts.status_str);

    buf.clear();

    // Write the HTTP version prefix ..
    let version_part = if parts.version == 0 {
        http::Version::HTTP_10
    } else {
        http::Version::HTTP_11
    };

    buf.extend_from_slice(match version_part {
        http::Version::HTTP_10 => b"HTTP/1.0 ",
        _ => b"HTTP/1.1 ",
    });
    buf.extend_from_slice(status.as_str().as_bytes());
    buf.push(b' ');
    buf.extend_from_slice(status.canonical_reason().unwrap_or("").as_bytes());
    buf.extend_from_slice(b"\r\n");

    // .. write Python-supplied headers, tracking whether Connection was already set ..
    let mut has_connection = false;

    if let Some(headers_dict) = parts.py_headers {
        for (key_obj, val_obj) in headers_dict.iter() {
            let header_name: &str = key_obj.extract()?;
            let header_value: &str = val_obj.extract()?;

            if let (Ok(name), Ok(val)) = (
                http::header::HeaderName::from_bytes(header_name.as_bytes()),
                http::header::HeaderValue::from_str(header_value),
            ) {
                buf.extend_from_slice(name.as_str().as_bytes());
                buf.extend_from_slice(b": ");
                buf.extend_from_slice(val.as_bytes());
                buf.extend_from_slice(b"\r\n");

                if !has_connection && name == http::header::CONNECTION {
                    has_connection = true;
                }
            }
        }
    }

    // .. add Transfer-Encoding for chunked streaming ..
    buf.extend_from_slice(b"transfer-encoding: chunked\r\n");

    // .. add Connection if not already present ..
    if !has_connection {
        let conn_header: &[u8] = if parts.keep_alive {
            b"connection: keep-alive\r\n"
        } else {
            b"connection: close\r\n"
        };
        buf.extend_from_slice(conn_header);
    }

    // .. and terminate the header block with the blank line.
    buf.extend_from_slice(b"\r\n");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Helper to build a `ResponseParts` without Python headers.
    fn make_parts(version: u8, status_str: &str, keep_alive: bool) -> ResponseParts<'_, '_> {
        ResponseParts {
            version,
            status_str,
            py_headers: None,
            body: b"",
            keep_alive,
        }
    }

    #[test]
    fn headers_only_produces_valid_status_line() {
        let parts = make_parts(1, "200 OK", true);
        let mut buf = Vec::new();

        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|_py| {
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");
        });

        let output = String::from_utf8_lossy(&buf);
        assert!(output.starts_with("HTTP/1.1 200 OK\r\n"), "unexpected start: {output}");
    }

    #[test]
    fn headers_only_has_no_content_length() {
        let parts = make_parts(1, "200 OK", true);
        let mut buf = Vec::new();

        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|_py| {
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");
        });

        let output = String::from_utf8_lossy(&buf).to_lowercase();
        assert!(
            !output.contains("content-length"),
            "content-length must not appear in streaming headers"
        );
    }

    #[test]
    fn headers_only_has_transfer_encoding_chunked() {
        let parts = make_parts(1, "200 OK", true);
        let mut buf = Vec::new();

        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|_py| {
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");
        });

        let output = String::from_utf8_lossy(&buf);
        assert!(
            output.contains("transfer-encoding: chunked\r\n"),
            "must include chunked transfer-encoding"
        );
    }

    #[test]
    fn headers_only_ends_with_blank_line() {
        let parts = make_parts(1, "200 OK", false);
        let mut buf = Vec::new();

        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|_py| {
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");
        });

        assert!(buf.ends_with(b"\r\n\r\n"), "header block must end with double CRLF");
    }

    #[test]
    fn headers_only_includes_connection_keep_alive() {
        let parts = make_parts(1, "200 OK", true);
        let mut buf = Vec::new();

        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|_py| {
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");
        });

        let output = String::from_utf8_lossy(&buf);
        assert!(
            output.contains("connection: keep-alive\r\n"),
            "must include keep-alive connection header"
        );
    }

    #[test]
    fn headers_only_includes_connection_close() {
        let parts = make_parts(1, "200 OK", false);
        let mut buf = Vec::new();

        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|_py| {
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");
        });

        let output = String::from_utf8_lossy(&buf);
        assert!(output.contains("connection: close\r\n"), "must include close connection header");
    }

    #[test]
    fn headers_only_includes_python_supplied_headers() {
        pyo3::prepare_freethreaded_python();
        pyo3::Python::with_gil(|py| {
            let headers = PyDict::new(py);
            headers.set_item("x-custom-header", "test-value").expect("should set header");

            let parts = ResponseParts {
                version: 1,
                status_str: "200 OK",
                py_headers: Some(&headers),
                body: b"",
                keep_alive: true,
            };
            let mut buf = Vec::new();
            build_response_headers_only(&parts, &mut buf).expect("should serialize headers");

            let output = String::from_utf8_lossy(&buf);
            assert!(output.contains("x-custom-header: test-value\r\n"), "must include custom header");
        });
    }
}
