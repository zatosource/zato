//! The head of an outgoing request - the request line and the headers, merged and validated
//! the way requests merges and validates them.
//!
//! The default headers of the connection's session come first, the headers of the call replace them
//! regardless of case and keep their position, a header whose value is `None` is removed, and the
//! `Content-Length` header is set the way requests sets it. A header requests would reject, or one
//! the transport does not implement, makes the invocation go through requests.

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString};

/// The methods requests sends without a `Content-Length` header when they have no body.
const METHODS_WITHOUT_LENGTH: [&str; 2] = ["GET", "HEAD"];

/// One header of a request, its name as the caller spelled it and its value as sent.
struct Header {
    /// The name, as last spelled by whoever set the header.
    name: String,

    /// The value, encoded as Latin-1 the way `http.client` encodes it.
    value: Vec<u8>,
}

/// What a request head is built from.
pub struct HeadInput<'call, 'py> {
    /// The method, already in uppercase.
    pub method: &'call str,

    /// The path and the query string of the request line.
    pub request_target: &'call str,

    /// The value of the `Host` header, sent unless the caller gives one.
    pub host_header: &'call str,

    /// The default headers of the connection's session, in their order.
    pub defaults: &'call [(String, Vec<u8>)],

    /// The headers of the call.
    pub headers: &'call Bound<'py, PyDict>,

    /// The length of the body, if the request has a body that is not empty.
    pub body_len: Option<usize>,
}

/// Builds the head of a request, or returns `None` if the request is to go through requests.
pub fn build_head(input: &HeadInput<'_, '_>) -> PyResult<Option<Vec<u8>>> {
    let mut merged: Vec<Header> = Vec::with_capacity(input.defaults.len() + input.headers.len() + 2);

    for (name, value) in input.defaults {
        merged.push(Header {
            name: name.clone(),
            value: value.clone(),
        });
    }

    // The headers of the call replace the defaults, and a header set to None removes one ..
    for (key, value) in input.headers.iter() {
        let Some(name) = extract_name(&key)? else {
            return Ok(None);
        };

        if value.is_none() {
            merged.retain(|header| !header.name.eq_ignore_ascii_case(&name));
            continue;
        }

        let Some(encoded) = extract_value(&value)? else {
            return Ok(None);
        };

        set_header(&mut merged, name, encoded);
    }

    // .. requests sends its defaults whatever the caller removed, which is left to requests ..
    for (name, _) in input.defaults {
        if find_header(&merged, name).is_none() {
            return Ok(None);
        }
    }

    // .. a body the caller frames with its own transfer encoding is left to requests too ..
    if find_header(&merged, "Transfer-Encoding").is_some() {
        return Ok(None);
    }

    set_content_length(&mut merged, input.method, input.body_len);

    Ok(Some(serialize(input, &merged)))
}

/// Extracts the name of a header, returning `None` for a name requests would reject or `http.client` could not encode.
fn extract_name(key: &Bound<'_, PyAny>) -> PyResult<Option<String>> {
    let Ok(text) = key.cast::<PyString>() else {
        return Ok(None);
    };

    let name = text.to_str()?;

    if !is_valid_name(name) {
        return Ok(None);
    }

    Ok(Some(name.to_owned()))
}

/// Extracts the value of a header as the bytes sent, returning `None` for a value requests would reject.
fn extract_value(value: &Bound<'_, PyAny>) -> PyResult<Option<Vec<u8>>> {
    if let Ok(text) = value.cast::<PyString>() {
        let text = text.to_str()?;

        if !is_valid_text_value(text) {
            return Ok(None);
        }

        return Ok(encode_latin1(text));
    }

    if let Ok(raw) = value.cast::<PyBytes>() {
        let raw = raw.as_bytes();

        if !is_valid_bytes_value(raw) {
            return Ok(None);
        }

        return Ok(Some(raw.to_vec()));
    }

    Ok(None)
}

/// Whether a header name matches what requests and `http.client` accept - ASCII, not empty, not starting
/// with a colon or whitespace, and without a colon or a line break anywhere.
fn is_valid_name(name: &str) -> bool {
    let bytes = name.as_bytes();

    let Some(&first) = bytes.first() else {
        return false;
    };

    if !name.is_ascii() || first == b':' || first.is_ascii_whitespace() || first == VERTICAL_TAB {
        return false;
    }

    !bytes.iter().any(|byte| matches!(byte, b':' | b'\r' | b'\n'))
}

/// The vertical tab, which Python counts as whitespace and Rust's ASCII whitespace test does not.
const VERTICAL_TAB: u8 = 0x0b;

/// Whether a text value matches what requests accepts - empty, or not starting with whitespace and without
/// a line break anywhere.
fn is_valid_text_value(value: &str) -> bool {
    let Some(first) = value.chars().next() else {
        return true;
    };

    !is_python_space(first) && !value.contains(['\r', '\n'])
}

/// Whether a bytes value matches what requests accepts - empty, or not starting with ASCII whitespace
/// and without a line break anywhere.
fn is_valid_bytes_value(value: &[u8]) -> bool {
    let Some(&first) = value.first() else {
        return true;
    };

    !(first.is_ascii_whitespace() || first == VERTICAL_TAB) && !value.iter().any(|byte| matches!(byte, b'\r' | b'\n'))
}

/// Whether Python's regular expressions count a character as whitespace, for the characters Latin-1 can encode.
const fn is_python_space(character: char) -> bool {
    matches!(
        character,
        '\t' | '\n' | '\u{0b}' | '\u{0c}' | '\r' | '\u{1c}'..='\u{1f}' | ' ' | '\u{85}' | '\u{a0}'
    )
}

/// Encodes text as Latin-1, returning `None` if it has a character Latin-1 cannot encode.
fn encode_latin1(text: &str) -> Option<Vec<u8>> {
    let mut out = Vec::with_capacity(text.len());

    for character in text.chars() {
        out.push(u8::try_from(u32::from(character)).ok()?);
    }

    Some(out)
}

/// Finds a header by name, compared case-insensitively.
fn find_header<'list>(headers: &'list [Header], name: &str) -> Option<&'list Header> {
    headers.iter().find(|header| header.name.eq_ignore_ascii_case(name))
}

/// Sets a header, replacing the name and the value of an existing one in its position or appending a new one.
fn set_header(headers: &mut Vec<Header>, name: String, value: Vec<u8>) {
    if let Some(existing) = headers.iter_mut().find(|header| header.name.eq_ignore_ascii_case(&name)) {
        existing.name = name;
        existing.value = value;
    } else {
        headers.push(Header { name, value });
    }
}

/// Sets `Content-Length` the way requests sets it - the length of a body that is not empty, replacing
/// whatever the caller gave, or zero for a method other than GET and HEAD without a body, unless the caller gave one.
fn set_content_length(headers: &mut Vec<Header>, method: &str, body_len: Option<usize>) {
    match body_len {
        Some(length) => set_header(headers, String::from("Content-Length"), length.to_string().into_bytes()),
        None => {
            let is_without_length = METHODS_WITHOUT_LENGTH.contains(&method);

            if !is_without_length && find_header(headers, "Content-Length").is_none() {
                headers.push(Header {
                    name: String::from("Content-Length"),
                    value: b"0".to_vec(),
                });
            }
        }
    }
}

/// Writes the request line, the `Host` header unless the caller gave one, and the merged headers.
fn serialize(input: &HeadInput<'_, '_>, headers: &[Header]) -> Vec<u8> {
    let mut out = Vec::with_capacity(512);

    out.extend_from_slice(input.method.as_bytes());
    out.push(b' ');
    out.extend_from_slice(input.request_target.as_bytes());
    out.extend_from_slice(b" HTTP/1.1\r\n");

    // http.client puts its own Host header first, unless the caller gave one
    if find_header(headers, "Host").is_none() {
        out.extend_from_slice(b"Host: ");
        out.extend_from_slice(input.host_header.as_bytes());
        out.extend_from_slice(b"\r\n");
    }

    for header in headers {
        out.extend_from_slice(header.name.as_bytes());
        out.extend_from_slice(b": ");
        out.extend_from_slice(&header.value);
        out.extend_from_slice(b"\r\n");
    }

    out.extend_from_slice(b"\r\n");
    out
}

/// Whether a method consists of the token characters `http.client` sends, i.e. ASCII letters, digits and marks.
pub fn is_valid_method(method: &str) -> bool {
    !method.is_empty() && method.bytes().all(|byte| byte.is_ascii_graphic())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn header_names() {
        assert!(is_valid_name("X-Custom-Header"));
        assert!(!is_valid_name(""));
        assert!(!is_valid_name(":path"));
        assert!(!is_valid_name(" X-Leading"));
        assert!(!is_valid_name("X-Bad:Name"));
        assert!(!is_valid_name("X-Bad\r\nName"));
        assert!(!is_valid_name("X-Caf\u{e9}"));
    }

    #[test]
    fn text_values() {
        assert!(is_valid_text_value(""));
        assert!(is_valid_text_value("Test value"));
        assert!(!is_valid_text_value(" Test value"));
        assert!(!is_valid_text_value("\u{a0}Test"));
        assert!(!is_valid_text_value("Test\r\nX-Injected: value"));
        assert!(!is_valid_text_value("Test\nvalue"));
    }

    #[test]
    fn bytes_values() {
        assert!(is_valid_bytes_value(b""));
        assert!(is_valid_bytes_value(b"\xa0Test"));
        assert!(!is_valid_bytes_value(b"\tTest"));
        assert!(!is_valid_bytes_value(b"Test\rvalue"));
    }

    #[test]
    fn latin1() {
        assert_eq!(encode_latin1("Z\u{fc}rich"), Some(b"Z\xfcrich".to_vec()));
        assert_eq!(encode_latin1("\u{141}\u{f3}d\u{17a}"), None);
    }

    #[test]
    fn content_length() {
        let mut headers = Vec::new();
        set_content_length(&mut headers, "GET", None);
        assert!(headers.is_empty());

        set_content_length(&mut headers, "POST", None);
        assert_eq!(find_header(&headers, "content-length").map(|header| header.value.clone()), Some(b"0".to_vec()));

        set_content_length(&mut headers, "POST", Some(12));
        assert_eq!(headers.len(), 1);
        assert_eq!(find_header(&headers, "Content-Length").map(|header| header.value.clone()), Some(b"12".to_vec()));
    }

    #[test]
    fn replaced_header_keeps_position_and_takes_new_name() {
        let mut headers = vec![
            Header {
                name: String::from("Content-Type"),
                value: b"text/plain".to_vec(),
            },
            Header {
                name: String::from("X-Other"),
                value: b"1".to_vec(),
            },
        ];

        set_header(&mut headers, String::from("content-type"), b"application/xml".to_vec());

        assert_eq!(headers.len(), 2);
        assert_eq!(headers.first().map(|header| header.name.as_str()), Some("content-type"));
        assert_eq!(headers.first().map(|header| header.value.clone()), Some(b"application/xml".to_vec()));
    }
}
