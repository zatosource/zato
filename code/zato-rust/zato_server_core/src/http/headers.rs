//! HTTP header parsing and WSGI environ key mapping.

use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString};

use crate::logging::transform_header_key;

/// Converts a WSGI environ dict into a Zato-style HTTP headers dict
/// by stripping the `HTTP_` prefix and lowercasing.
#[pyfunction]
pub fn extract_headers(environ: &Bound<'_, PyDict>) -> PyResult<Py<PyDict>> {
    let py = environ.py();
    let headers = PyDict::new(py);
    for (key, value) in environ.iter() {
        let key_str: &Bound<'_, PyString> = key.cast_exact()?;
        let key_text = key_str.to_str()?;
        if let Some(header) = transform_header_key(key_text) {
            headers.set_item(header, value)?;
        }
    }
    Ok(headers.unbind())
}

/// Maps a single HTTP header name/value pair into the WSGI environ dict format.
///
/// Well-known headers (Content-Type, Authorization, etc.) are mapped to their canonical keys,
/// everything else becomes `HTTP_<UPPERCASED_UNDERSCORED>`.
#[inline]
pub(super) fn set_header(py: Python<'_>, dict: &Bound<'_, PyDict>, name: &str, value: &[u8]) -> PyResult<()> {
    let val = String::from_utf8_lossy(value);
    if name.eq_ignore_ascii_case("Content-Type") {
        dict.set_item(intern!(py, "CONTENT_TYPE"), &*val)
    } else if name.eq_ignore_ascii_case("Content-Length") {
        dict.set_item(intern!(py, "CONTENT_LENGTH"), &*val)
    } else if name.eq_ignore_ascii_case("Authorization") {
        dict.set_item(intern!(py, "HTTP_AUTHORIZATION"), &*val)
    } else if name.eq_ignore_ascii_case("User-Agent") {
        dict.set_item(intern!(py, "HTTP_USER_AGENT"), &*val)
    } else if name.eq_ignore_ascii_case("X-Forwarded-For") {
        dict.set_item(intern!(py, "HTTP_X_FORWARDED_FOR"), &*val)
    } else if name.eq_ignore_ascii_case("X-Zato-Forwarded-For") {
        dict.set_item(intern!(py, "HTTP_X_ZATO_FORWARDED_FOR"), &*val)
    } else if name.eq_ignore_ascii_case("Connection") {
        dict.set_item(intern!(py, "HTTP_CONNECTION"), &*val)
    } else {
        let mut key = String::with_capacity(5 + name.len());
        key.push_str("HTTP_");
        for byte in name.bytes() {
            key.push(if byte == b'-' { '_' } else { char::from(byte).to_ascii_uppercase() });
        }
        dict.set_item(key, &*val)
    }
}
