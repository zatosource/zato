//! The head of an outgoing request, merged and validated the way requests merges and validates it.
//!
//! The default headers of the connection's session come first, the headers of the call replace them
//! regardless of case and keep their position, a header whose value is `None` is removed, and the
//! `Content-Length` and `Content-Type` headers are set the way requests sets them. The headers urllib3
//! and `http.client` add of their own are added as they add them, and a request sent through a proxy
//! has the headers urllib3 sets for a proxy. A header requests would reject makes the invocation go
//! through requests, which then rejects it.

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString};

/// The methods requests sends without a `Content-Length` header when they have no body.
const METHODS_WITHOUT_LENGTH: [&str; 2] = ["GET", "HEAD"];

/// The header the credentials of a connection are sent in.
const AUTHORIZATION_HEADER: &str = "Authorization";

/// The header the credentials of a proxy are sent in.
pub const PROXY_AUTHORIZATION_HEADER: &str = "Proxy-Authorization";

/// The header urllib3 names itself in when the request names no client.
const USER_AGENT_HEADER: &str = "User-Agent";

/// The header `http.client` asks for an unencoded body in when the request asks for no encoding.
const ACCEPT_ENCODING_HEADER: &str = "Accept-Encoding";

/// The encoding `http.client` asks for when the request asks for none.
const IDENTITY_ENCODING: &[u8] = b"identity";

/// The header urllib3 accepts any media type in for a request sent through a proxy.
const ACCEPT_HEADER: &str = "Accept";

/// The media types urllib3 accepts for a request sent through a proxy, unless the request names its own.
const ANY_MEDIA_TYPE: &[u8] = b"*/*";

/// Where a request is sent, which decides the headers added to it.
pub enum HeadLayout<'call> {
    /// To the endpoint, directly or through a tunnel, with the `Host` header `http.client` builds
    /// unless the caller gives one.
    Origin {
        /// The value of the `Host` header.
        host_header: &'call str,
    },

    /// To an HTTP proxy, with the `Accept` and `Host` headers and the credentials of the proxy that urllib3 sets.
    Proxied {
        /// The host and the port of the endpoint, as the `Host` header names them.
        netloc: &'call str,

        /// The value of the `Proxy-Authorization` header the credentials of the proxy produce, if it has any.
        proxy_authorization: Option<&'call [u8]>,
    },
}

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

    /// The request target of the request line - the path and the query string, or the whole address
    /// for a request sent through an HTTP proxy.
    pub request_target: &'call str,

    /// Where the request is sent.
    pub layout: HeadLayout<'call>,

    /// The default headers of the connection's session, in their order.
    pub defaults: &'call [(String, Vec<u8>)],

    /// The headers of the call.
    pub headers: &'call Bound<'py, PyDict>,

    /// The length of the body, if the request has a body that is not empty.
    pub body_len: Option<usize>,

    /// The media type requests gives a body it encodes itself, sent unless the request names its own.
    pub content_type: Option<&'call [u8]>,

    /// The value of the `Authorization` header, if the call uses the credentials of the connection
    /// or the address has credentials of its own.
    pub authorization: Option<&'call [u8]>,

    /// The value of the `User-Agent` header urllib3 sends when the request names no client.
    pub user_agent: &'call [u8],
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

    // .. a body the caller frames with its own transfer encoding is left to requests ..
    if find_header(&merged, "Transfer-Encoding").is_some() {
        return Ok(None);
    }

    // .. the length and the media type of the body follow, as requests prepares the body after the headers ..
    set_content_length(&mut merged, input.method, input.body_len);

    if let Some(value) = input.content_type
        && find_header(&merged, "Content-Type").is_none()
    {
        merged.push(Header {
            name: String::from("Content-Type"),
            value: value.to_vec(),
        });
    }

    // .. the credentials come after the length, as requests applies its auth object last ..
    if let Some(value) = input.authorization {
        set_header(&mut merged, String::from(AUTHORIZATION_HEADER), value.to_vec());
    }

    // .. a request sent through a proxy has the headers urllib3 sets for the proxy ..
    let mut ordered = match &input.layout {
        HeadLayout::Origin { .. } => merged,
        HeadLayout::Proxied {
            netloc,
            proxy_authorization,
        } => to_proxied(merged, netloc, *proxy_authorization),
    };

    // .. and urllib3 names itself as the client of a request that names none.
    add_user_agent(&mut ordered, input.user_agent);

    Ok(Some(serialize(input.method, input.request_target, &input.layout, &ordered)))
}

/// Appends the `User-Agent` urllib3 sends in a request that has none of its own.
fn add_user_agent(headers: &mut Vec<Header>, user_agent: &[u8]) {
    if find_header(headers, USER_AGENT_HEADER).is_none() {
        headers.push(Header {
            name: String::from(USER_AGENT_HEADER),
            value: user_agent.to_vec(),
        });
    }
}

/// Arranges the headers of a request sent through an HTTP proxy the way urllib3 arranges them - its `Accept`
/// and `Host` headers first, then the headers of the request and the credentials of the proxy, each replacing
/// a header of exactly the same name, because urllib3 merges them into a plain dictionary.
fn to_proxied(merged: Vec<Header>, netloc: &str, proxy_authorization: Option<&[u8]>) -> Vec<Header> {
    let mut out = Vec::with_capacity(merged.len() + 3);

    out.push(Header {
        name: String::from(ACCEPT_HEADER),
        value: ANY_MEDIA_TYPE.to_vec(),
    });

    out.push(Header {
        name: String::from("Host"),
        value: netloc.as_bytes().to_vec(),
    });

    for header in merged {
        set_exact_header(&mut out, header);
    }

    if let Some(value) = proxy_authorization {
        set_exact_header(
            &mut out,
            Header {
                name: String::from(PROXY_AUTHORIZATION_HEADER),
                value: value.to_vec(),
            },
        );
    }

    out
}

/// Sets a header the way a plain dictionary does, replacing the value of a header whose name is spelled exactly
/// the same and keeping its position, or appending the header otherwise.
fn set_exact_header(headers: &mut Vec<Header>, header: Header) {
    if let Some(existing) = headers.iter_mut().find(|existing| existing.name == header.name) {
        existing.value = header.value;
    } else {
        headers.push(header);
    }
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
        return Ok(encode_text_value(text.to_str()?));
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

/// Encodes a text value as the bytes sent, returning `None` for a value requests would reject or Latin-1 cannot encode.
pub fn encode_text_value(text: &str) -> Option<Vec<u8>> {
    if !is_valid_text_value(text) {
        return None;
    }

    encode_latin1(text)
}

/// Whether a header name matches what requests and `http.client` accept - ASCII, not empty, not starting
/// with a colon or whitespace, and without a colon or a line break anywhere.
pub fn is_valid_name(name: &str) -> bool {
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

    !(first.is_ascii_whitespace() || first == VERTICAL_TAB || value.iter().any(|byte| matches!(byte, b'\r' | b'\n')))
}

/// Whether Python's regular expressions count a character as whitespace, for the characters Latin-1 can encode.
const fn is_python_space(character: char) -> bool {
    matches!(
        character,
        '\t' | '\n' | '\u{0b}' | '\u{0c}' | '\r' | '\u{1c}'..='\u{1f}' | ' ' | '\u{85}' | '\u{a0}'
    )
}

/// Encodes text as Latin-1, returning `None` if it has a character Latin-1 cannot encode.
pub fn encode_latin1(text: &str) -> Option<Vec<u8>> {
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

/// Sets `Content-Length` the way requests sets it.
///
/// A body that is not empty sets its length, replacing whatever the caller gave, and a method other than
/// GET and HEAD without a body sends zero, unless the caller gave a length.
fn set_content_length(headers: &mut Vec<Header>, method: &str, body_len: Option<usize>) {
    if let Some(length) = body_len {
        set_header(headers, String::from("Content-Length"), length.to_string().into_bytes());
        return;
    }

    let is_without_length = METHODS_WITHOUT_LENGTH.contains(&method);

    if !is_without_length && find_header(headers, "Content-Length").is_none() {
        headers.push(Header {
            name: String::from("Content-Length"),
            value: b"0".to_vec(),
        });
    }
}

/// Writes the request line, the `Host` and `Accept-Encoding` headers `http.client` puts first unless
/// the request has them already, and the headers of the request.
fn serialize(method: &str, request_target: &str, layout: &HeadLayout<'_>, headers: &[Header]) -> Vec<u8> {
    let mut out = Vec::with_capacity(512);

    out.extend_from_slice(method.as_bytes());
    out.push(b' ');
    out.extend_from_slice(request_target.as_bytes());
    out.extend_from_slice(b" HTTP/1.1\r\n");

    // A request sent through a proxy always has the Host header urllib3 set for it
    if let HeadLayout::Origin { host_header } = layout
        && find_header(headers, "Host").is_none()
    {
        write_header(&mut out, "Host", host_header.as_bytes());
    }

    if find_header(headers, ACCEPT_ENCODING_HEADER).is_none() {
        write_header(&mut out, ACCEPT_ENCODING_HEADER, IDENTITY_ENCODING);
    }

    for header in headers {
        write_header(&mut out, &header.name, &header.value);
    }

    out.extend_from_slice(b"\r\n");
    out
}

/// Writes one header line.
fn write_header(out: &mut Vec<u8>, name: &str, value: &[u8]) {
    out.extend_from_slice(name.as_bytes());
    out.extend_from_slice(b": ");
    out.extend_from_slice(value);
    out.extend_from_slice(b"\r\n");
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
        assert_eq!(
            find_header(&headers, "content-length").map(|header| header.value.clone()),
            Some(b"0".to_vec())
        );

        set_content_length(&mut headers, "POST", Some(12));
        assert_eq!(headers.len(), 1);
        assert_eq!(
            find_header(&headers, "Content-Length").map(|header| header.value.clone()),
            Some(b"12".to_vec())
        );
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
        assert_eq!(
            headers.first().map(|header| header.value.clone()),
            Some(b"application/xml".to_vec())
        );
    }

    /// A header with the given name and value.
    fn header(name: &str, value: &str) -> Header {
        Header {
            name: String::from(name),
            value: value.as_bytes().to_vec(),
        }
    }

    /// The text of a serialized head, which the tests build from ASCII only.
    fn text(head: &[u8]) -> String {
        String::from_utf8_lossy(head).into_owned()
    }

    #[test]
    fn origin_head_has_host_and_identity_encoding_first() {
        let headers = vec![header("Accept", "*/*")];
        let layout = HeadLayout::Origin {
            host_header: "example.com:8080",
        };

        let head = serialize("GET", "/api", &layout, &headers);

        assert_eq!(
            text(&head),
            "GET /api HTTP/1.1\r\nHost: example.com:8080\r\nAccept-Encoding: identity\r\nAccept: */*\r\n\r\n"
        );
    }

    #[test]
    fn origin_head_keeps_host_and_encoding_of_the_call() {
        let headers = vec![header("accept-encoding", "gzip"), header("host", "other.example.com")];
        let layout = HeadLayout::Origin {
            host_header: "example.com",
        };

        let head = serialize("GET", "/", &layout, &headers);

        assert_eq!(
            text(&head),
            "GET / HTTP/1.1\r\naccept-encoding: gzip\r\nhost: other.example.com\r\n\r\n"
        );
    }

    #[test]
    fn user_agent_appended_only_when_missing() {
        let mut headers = vec![header("Accept", "*/*")];
        add_user_agent(&mut headers, b"python-urllib3/1.26.20");

        assert_eq!(
            headers.last().map(|header| (header.name.as_str(), header.value.clone())),
            Some(("User-Agent", b"python-urllib3/1.26.20".to_vec()))
        );

        let mut headers = vec![header("user-agent", "Zato")];
        add_user_agent(&mut headers, b"python-urllib3/1.26.20");

        assert_eq!(headers.len(), 1);
    }

    #[test]
    fn proxied_headers_follow_the_dictionary_of_urllib3() {
        let merged = vec![
            header("User-Agent", "Zato"),
            header("Accept", "application/json"),
            header("host", "caller.example.com"),
        ];

        let ordered = to_proxied(merged, "example.com:8080", Some(b"Basic dTpw"));
        let names: Vec<(&str, &[u8])> = ordered.iter().map(|header| (header.name.as_str(), header.value.as_slice())).collect();

        assert_eq!(
            names,
            vec![
                ("Accept", b"application/json".as_slice()),
                ("Host", b"example.com:8080".as_slice()),
                ("User-Agent", b"Zato".as_slice()),
                ("host", b"caller.example.com".as_slice()),
                ("Proxy-Authorization", b"Basic dTpw".as_slice()),
            ]
        );
    }

    #[test]
    fn proxied_head_has_no_host_of_its_own() {
        let headers = vec![header("Accept", "*/*"), header("Host", "example.com")];
        let layout = HeadLayout::Proxied {
            netloc: "example.com",
            proxy_authorization: None,
        };

        let head = serialize("GET", "http://example.com/", &layout, &headers);

        assert_eq!(
            text(&head),
            "GET http://example.com/ HTTP/1.1\r\nAccept-Encoding: identity\r\nAccept: */*\r\nHost: example.com\r\n\r\n"
        );
    }
}
