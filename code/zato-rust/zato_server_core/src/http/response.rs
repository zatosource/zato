//! HTTP response builder - serializes status, headers and body into a byte buffer.

use http::StatusCode;
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Parses a status string like `"200 OK"` into an `http::StatusCode`.
pub fn parse_status_code(status_str: &str) -> StatusCode {
    let code_str = status_str.split_whitespace().next().map_or("200", |code| code);
    code_str.parse::<StatusCode>().unwrap_or(StatusCode::OK)
}

/// Serializes a complete HTTP response (status line, headers, body) into `buf`.
///
/// Adds `Content-Length` and `Connection` headers if not already present.
#[expect(clippy::too_many_arguments, reason = "all parts of an HTTP response are needed to serialize it")]
pub(super) fn build_response(
    version: u8,
    status_str: &str,
    py_headers: Option<&Bound<'_, PyDict>>,
    body: &[u8],
    keep_alive: bool,
    buf: &mut Vec<u8>,
) -> PyResult<()> {
    let status = parse_status_code(status_str);

    buf.clear();

    let version_part = if version == 0 {
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

    if let Some(headers_dict) = py_headers {
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

                if !has_content_length && name == http::header::CONTENT_LENGTH { has_content_length = true; }
                if !has_connection && name == http::header::CONNECTION { has_connection = true; }
            }
        }
    }

    if !has_content_length {
        buf.extend_from_slice(b"content-length: ");
        let _fmt = std::io::Write::write_fmt(buf, format_args!("{}", body.len()));
        buf.extend_from_slice(b"\r\n");
    }
    if !has_connection {
        let conn_header: &[u8] = if keep_alive {
            b"connection: keep-alive\r\n"
        } else {
            b"connection: close\r\n"
        };
        buf.extend_from_slice(conn_header);
    }
    buf.extend_from_slice(b"\r\n");
    buf.extend_from_slice(body);

    Ok(())
}
