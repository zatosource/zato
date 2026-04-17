use http::StatusCode;
use pyo3::prelude::*;
use pyo3::types::PyDict;

pub fn parse_status_code(status_str: &str) -> StatusCode {
    let code_str = status_str.split_whitespace().next().unwrap_or("200");
    code_str.parse::<StatusCode>().unwrap_or(StatusCode::OK)
}

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

    let mut has_cl = false;
    let mut has_conn = false;

    if let Some(d) = py_headers {
        for (k, v) in d.iter() {
            let kk: &str = k.extract()?;
            let vv: &str = v.extract()?;

            if let (Ok(name), Ok(val)) = (
                http::header::HeaderName::from_bytes(kk.as_bytes()),
                http::header::HeaderValue::from_str(vv),
            ) {
                buf.extend_from_slice(name.as_str().as_bytes());
                buf.extend_from_slice(b": ");
                buf.extend_from_slice(val.as_bytes());
                buf.extend_from_slice(b"\r\n");

                if !has_cl && name == http::header::CONTENT_LENGTH { has_cl = true; }
                if !has_conn && name == http::header::CONNECTION { has_conn = true; }
            }
        }
    }

    if !has_cl {
        buf.extend_from_slice(b"content-length: ");
        let _ = std::io::Write::write_fmt(buf, format_args!("{}", body.len()));
        buf.extend_from_slice(b"\r\n");
    }
    if !has_conn {
        buf.extend_from_slice(if keep_alive {
            b"connection: keep-alive\r\n" as &[u8]
        } else {
            b"connection: close\r\n"
        });
    }
    buf.extend_from_slice(b"\r\n");
    buf.extend_from_slice(body);

    Ok(())
}
