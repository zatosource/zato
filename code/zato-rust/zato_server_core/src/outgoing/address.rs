//! Parsing of the address an outgoing request is sent to.
//!
//! The transport accepts an address only when requests would send it unchanged - an `http` or `https`
//! scheme, an ASCII host in lowercase without credentials, and a path and query string that requests
//! would not re-quote. Any other address is sent through requests.

use std::borrow::Cow;

/// The port of an `http` address that does not name one.
const DEFAULT_HTTP_PORT: u16 = 80;

/// The port of an `https` address that does not name one.
const DEFAULT_HTTPS_PORT: u16 = 443;

/// The separator between a scheme and the rest of an address.
const SCHEME_SEPARATOR: &str = "://";

/// The characters requests leaves as they are when it re-quotes an address, besides letters and digits.
const SAFE_PUNCTUATION: &[u8] = b"-._~!$&'()*+,/:;=?@[]";

/// The characters a percent-encoded octet decodes to that requests decodes back when it re-quotes an address.
const UNRESERVED_PUNCTUATION: &[u8] = b"-._~";

/// An address split into what a connection is opened to and what the request line carries.
pub struct Target<'url> {
    /// Whether the connection uses TLS.
    pub is_tls: bool,

    /// The host name or IP address, without the brackets of an IPv6 address.
    pub host: &'url str,

    /// The port, the default port of the scheme if the address does not name one.
    pub port: u16,

    /// The value of the `Host` header, which names the port only if it is not the default one.
    pub host_header: String,

    /// The path and the query string, as sent in the request line.
    pub request_target: Cow<'url, str>,
}

/// Parses an address, returning `None` for an address the transport leaves to requests.
pub fn parse(url: &str) -> Option<Target<'_>> {
    // A fragment is never sent, but requests keeps it in the URL of the response, which is left to requests
    if url.contains('#') {
        return None;
    }

    let (scheme, rest) = url.split_once(SCHEME_SEPARATOR)?;

    let is_tls = if scheme.eq_ignore_ascii_case("https") {
        true
    } else if scheme.eq_ignore_ascii_case("http") {
        false
    } else {
        return None;
    };

    let authority_end = rest.find(['/', '?']).unwrap_or(rest.len());
    let (authority, path_and_query) = rest.split_at(authority_end);

    let (host, explicit_port, is_ipv6) = split_authority(authority)?;

    let default_port = if is_tls { DEFAULT_HTTPS_PORT } else { DEFAULT_HTTP_PORT };
    let port = explicit_port.unwrap_or(default_port);

    if !is_valid_target(path_and_query.as_bytes()) {
        return None;
    }

    // A request line always has a path, and requests sends an empty one as a slash
    let request_target = if path_and_query.starts_with('/') {
        Cow::Borrowed(path_and_query)
    } else {
        Cow::Owned(format!("/{path_and_query}"))
    };

    let host_header = build_host_header(host, port, default_port, is_ipv6);

    Some(Target {
        is_tls,
        host,
        port,
        host_header,
        request_target,
    })
}

/// Splits an authority into its host, its port if it names one, and whether the host is an IPv6 address.
fn split_authority(authority: &str) -> Option<(&str, Option<u16>, bool)> {
    // Credentials in the address are sent by requests as Basic Auth, which is left to requests
    if authority.is_empty() || authority.contains('@') {
        return None;
    }

    let (host, port_text, is_ipv6) = if let Some(bracketed) = authority.strip_prefix('[') {
        let (host, after_host) = bracketed.split_once(']')?;
        let port_text = if after_host.is_empty() { None } else { Some(after_host.strip_prefix(':')?) };
        (host, port_text, true)
    } else {
        match authority.split_once(':') {
            Some((host, port_text)) => (host, Some(port_text), false),
            None => (authority, None, false),
        }
    };

    if !is_valid_host(host, is_ipv6) {
        return None;
    }

    let port = match port_text {
        Some(text) => Some(parse_port(text)?),
        None => None,
    };

    Some((host, port, is_ipv6))
}

/// Parses a port that consists of decimal digits only and is not zero.
fn parse_port(text: &str) -> Option<u16> {
    if text.is_empty() || !text.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }

    text.parse::<u16>().ok().filter(|port| *port != 0)
}

/// Whether a host consists of the characters requests sends unchanged - lowercase letters, digits,
/// dots, hyphens and underscores, or the hexadecimal digits, colons and dots of an IPv6 address.
fn is_valid_host(host: &str, is_ipv6: bool) -> bool {
    if host.is_empty() {
        return false;
    }

    if is_ipv6 {
        return host.bytes().all(|byte| byte.is_ascii_digit() || matches!(byte, b'a'..=b'f' | b':' | b'.'));
    }

    host.bytes().all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || matches!(byte, b'.' | b'-' | b'_'))
}

/// Whether requests would send a path and query string exactly as they are, without re-quoting any of it.
///
/// Every character must be one that requests leaves alone, and every percent sign must start an encoded octet
/// that requests does not decode, i.e. one that does not stand for a letter, a digit or an unreserved mark.
pub fn is_valid_target(target: &[u8]) -> bool {
    let mut position = 0;

    while let Some(&byte) = target.get(position) {
        if byte == b'%' {
            let Some(octet) = target.get(position + 1..position + 3).and_then(decode_hex_pair) else {
                return false;
            };

            if is_unreserved(octet) {
                return false;
            }

            position += 3;
            continue;
        }

        if !byte.is_ascii_alphanumeric() && !SAFE_PUNCTUATION.contains(&byte) {
            return false;
        }

        position += 1;
    }

    true
}

/// Decodes two hexadecimal digits into the octet they stand for.
fn decode_hex_pair(pair: &[u8]) -> Option<u8> {
    let text = std::str::from_utf8(pair).ok()?;
    u8::from_str_radix(text, 16).ok()
}

/// Whether an octet is a letter, a digit or an unreserved mark.
fn is_unreserved(octet: u8) -> bool {
    octet.is_ascii_alphanumeric() || UNRESERVED_PUNCTUATION.contains(&octet)
}

/// Builds the value of the `Host` header the way `http.client` builds it.
fn build_host_header(host: &str, port: u16, default_port: u16, is_ipv6: bool) -> String {
    let host_part = if is_ipv6 { format!("[{host}]") } else { host.to_owned() };

    if port == default_port {
        host_part
    } else {
        format!("{host_part}:{port}")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn plain_address() {
        let target = parse("http://127.0.0.1:8080/api/customers?id=1").unwrap();

        assert!(!target.is_tls);
        assert_eq!(target.host, "127.0.0.1");
        assert_eq!(target.port, 8080);
        assert_eq!(target.host_header, "127.0.0.1:8080");
        assert_eq!(target.request_target, "/api/customers?id=1");
    }

    #[test]
    fn default_port_is_not_in_host_header() {
        let target = parse("https://api.example.com/v1").unwrap();

        assert!(target.is_tls);
        assert_eq!(target.port, DEFAULT_HTTPS_PORT);
        assert_eq!(target.host_header, "api.example.com");
    }

    #[test]
    fn explicit_default_port_is_not_in_host_header() {
        let target = parse("http://api.example.com:80/v1").unwrap();
        assert_eq!(target.host_header, "api.example.com");
    }

    #[test]
    fn empty_path_becomes_slash() {
        assert_eq!(parse("http://localhost:1234").unwrap().request_target, "/");
        assert_eq!(parse("http://localhost:1234?page=2").unwrap().request_target, "/?page=2");
    }

    #[test]
    fn ipv6_host() {
        let target = parse("http://[::1]:9000/items").unwrap();

        assert_eq!(target.host, "::1");
        assert_eq!(target.host_header, "[::1]:9000");
    }

    #[test]
    fn addresses_left_to_requests() {
        assert!(parse("ftp://example.com/file").is_none());
        assert!(parse("http://user:secret@example.com/").is_none());
        assert!(parse("http://Example.com/").is_none());
        assert!(parse("http://example.com/a#section").is_none());
        assert!(parse("http://example.com:/a").is_none());
        assert!(parse("http://example.com:0/a").is_none());
        assert!(parse("http://example.com/a b").is_none());
        assert!(parse("http://example.com/caf\u{e9}").is_none());
        assert!(parse("http://ex\u{e4}mple.com/").is_none());
    }

    #[test]
    fn percent_encoding() {
        assert!(is_valid_target(b"/a%2Fb?x=%C3%BC"));
        assert!(is_valid_target(b"/a%2fb"));
        assert!(!is_valid_target(b"/a%41"));
        assert!(!is_valid_target(b"/a%7E"));
        assert!(!is_valid_target(b"/a%zz"));
        assert!(!is_valid_target(b"/a%2"));
    }
}
