use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::intern;

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
        for b in name.bytes() {
            key.push(if b == b'-' { '_' } else { (b as char).to_ascii_uppercase() });
        }
        dict.set_item(key, &*val)
    }
}
