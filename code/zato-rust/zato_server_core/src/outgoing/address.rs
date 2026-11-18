//! Preparation of the address an outgoing request is sent to.
//!
//! An address is prepared exactly as requests prepares it - urllib3 parses and normalizes it, and requests
//! rebuilds and re-quotes it - so the request carries the same request target, the same `Host` header
//! and the same credentials, and its response reports the same URL. An address requests could not send
//! either, or one whose host requires IDNA encoding, is sent through requests, which reports it as it always has.

use super::headers::encode_latin1;

/// The port of an `http` address that does not name one.
const DEFAULT_HTTP_PORT: u16 = 80;

/// The port of an `https` address that does not name one.
const DEFAULT_HTTPS_PORT: u16 = 443;

/// The separator between a scheme and the rest of an address.
const SCHEME_SEPARATOR: &str = "://";

/// The scheme of a plain HTTP address, as a prepared address spells it.
const HTTP_SCHEME: &str = "http";

/// The scheme of a TLS address, as a prepared address spells it.
const HTTPS_SCHEME: &str = "https";

/// The most digits of a port, after its leading zeros, that urllib3 accepts.
const MAX_PORT_DIGITS: usize = 5;

/// The radix of the digits of a percent-encoded octet.
const HEX_RADIX: u32 = 16;

/// The digits a percent-encoded octet is written with, in uppercase as urllib3 writes them.
const UPPERCASE_HEX_DIGITS: &[u8; 16] = b"0123456789ABCDEF";

/// How many bits the high digit of a percent-encoded octet is shifted by.
const HIGH_NIBBLE_SHIFT: u32 = 4;

/// The mask of the low digit of a percent-encoded octet.
const LOW_NIBBLE_MASK: u8 = 0x0f;

/// The characters urllib3 leaves as they are in credentials, besides letters and digits -
/// the unreserved marks, the sub-delimiters and the colon.
const USERINFO_PUNCTUATION: &[u8] = b"._-~!$&'()*+,;=:";

/// The characters urllib3 leaves as they are in a path, besides letters and digits -
/// those of credentials, the at sign and the slash.
const PATH_PUNCTUATION: &[u8] = b"._-~!$&'()*+,;=:@/";

/// The characters urllib3 leaves as they are in a query string and in a fragment, besides letters and digits -
/// those of a path and the question mark.
const QUERY_PUNCTUATION: &[u8] = b"._-~!$&'()*+,;=:@/?";

/// The marks a percent-encoded octet decodes to that requests decodes back when it re-quotes an address,
/// besides letters and digits.
const UNRESERVED_PUNCTUATION: &[u8] = b"-._~";

/// The prefix of the value of an `Authorization` header that carries Basic credentials.
const BASIC_PREFIX: &[u8] = b"Basic ";

/// The characters of Base64, in the order of the values they stand for.
const BASE64_ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/// The character that pads the last group of Base64 when the input does not fill it.
const BASE64_PADDING: char = '=';

/// How many input bytes one group of Base64 encodes.
const BASE64_GROUP_LEN: usize = 3;

/// How many characters one group of Base64 is written as.
const BASE64_GROUP_CHARS: usize = 4;

/// How many bits one character of Base64 stands for.
const BASE64_CHAR_BITS: u32 = 6;

/// The mask of the bits one character of Base64 stands for.
const BASE64_CHAR_MASK: u32 = 0x3f;

/// How many bits a byte has.
const BYTE_BITS: u32 = 8;

/// An address prepared for a request.
pub struct Target {
    /// Whether the connection to the endpoint uses TLS.
    pub is_tls: bool,

    /// The host in lowercase, without the brackets of an IPv6 address, which the connection is opened to.
    pub host: String,

    /// The port, the default port of the scheme if the address names none or names zero.
    pub port: u16,

    /// The address as requests prepares it, which the response reports as its URL.
    pub url: String,

    /// The path and the query string, as the request line to the endpoint carries them.
    pub path_and_query: String,

    /// The value of the `Authorization` header the credentials in the address produce, if it has any.
    pub authorization: Option<Vec<u8>>,

    /// Whether the host is an IPv6 address.
    is_ipv6: bool,

    /// The scheme in lowercase.
    scheme: &'static str,

    /// The host, in brackets if it is an IPv6 address, and the port if the address names one other than zero.
    netloc: String,

    /// The path, as requests prepares it.
    path: String,

    /// The query string, as requests prepares it, or an empty string if the address has none.
    query: String,
}

impl Target {
    /// The default port of the scheme.
    const fn default_port(&self) -> u16 {
        if self.is_tls { DEFAULT_HTTPS_PORT } else { DEFAULT_HTTP_PORT }
    }

    /// The value of the `Host` header of a request sent to the endpoint directly, which `http.client` builds
    /// from the host of the connection, without the trailing dots urllib3 removes from it.
    pub fn host_header(&self) -> String {
        build_host_header(self.server_name(), self.is_ipv6, self.port, self.default_port())
    }

    /// The name the certificate of the endpoint is verified against when the connection is direct,
    /// without the trailing dots urllib3 removes from the host.
    pub fn server_name(&self) -> &str {
        self.host.trim_end_matches('.')
    }

    /// The name the certificate of the endpoint is verified against when the connection goes through
    /// a tunnel of a proxy, the host as it is, which urllib3 takes from the tunnel.
    pub fn tunnel_server_name(&self) -> &str {
        &self.host
    }

    /// The value of the `Host` header of a request sent through a tunnel, which `http.client` builds
    /// from the host of the tunnel.
    pub fn tunneled_host_header(&self) -> String {
        build_host_header(&self.host, self.is_ipv6, self.port, self.default_port())
    }

    /// The `CONNECT` request that opens a tunnel to the endpoint through a proxy, without its headers,
    /// as `http.client` writes it.
    pub fn connect_line(&self) -> String {
        format!("CONNECT {}:{} HTTP/1.1\r\n", wrap_ipv6(&self.host, self.is_ipv6), self.port)
    }

    /// The value of the `Host` header of the `CONNECT` request, which `http.client` writes with the port
    /// and without the brackets of an IPv6 address.
    pub fn connect_host_header(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }

    /// The host and the port the `Host` header of a request sent through a proxy names, as urllib3 sets it.
    pub fn netloc(&self) -> &str {
        &self.netloc
    }

    /// The request target of a request sent through a proxy - the address without its credentials and its fragment,
    /// as requests passes it to urllib3 and as urllib3 parses it again before sending it.
    pub fn absolute_form(&self) -> String {
        let path = remove_dot_segments(remove_empty_parameters(&self.path));

        let mut out = format!("{}{SCHEME_SEPARATOR}{}{path}", self.scheme, self.netloc);

        if !self.query.is_empty() {
            out.push('?');
            out.push_str(&self.query);
        }

        out
    }
}

/// Prepares an address, returning `None` for an address the transport leaves to requests.
pub fn parse(url: &str) -> Option<Target> {
    // Control characters, backslashes and leading whitespace are treated by requests and urllib3 in ways of their own
    let has_unusual_byte = url.bytes().any(|byte| byte.is_ascii_control() || byte == b'\\');
    if has_unusual_byte || url.starts_with(char::is_whitespace) {
        return None;
    }

    let (scheme_text, rest) = url.split_once(SCHEME_SEPARATOR)?;

    // urllib3 reads the scheme in any case and writes it in lowercase
    let (scheme, is_tls) = if scheme_text.eq_ignore_ascii_case(HTTPS_SCHEME) {
        (HTTPS_SCHEME, true)
    } else if scheme_text.eq_ignore_ascii_case(HTTP_SCHEME) {
        (HTTP_SCHEME, false)
    } else {
        return None;
    };

    let authority_end = rest.find(['/', '?', '#']).unwrap_or(rest.len());
    let (authority, after_authority) = rest.split_at(authority_end);

    let path_end = after_authority.find(['?', '#']).unwrap_or(after_authority.len());
    let (raw_path, after_path) = after_authority.split_at(path_end);

    let (raw_query, raw_fragment) = split_query_and_fragment(after_path);

    // The credentials end at the last at sign, and an empty part before it is no credentials at all
    let (raw_userinfo, host_port) = match authority.rsplit_once('@') {
        Some((userinfo, host_port)) => (Some(userinfo).filter(|userinfo| !userinfo.is_empty()), host_port),
        None => (None, authority),
    };

    let host_port = parse_host_port(host_port)?;

    let userinfo = match raw_userinfo {
        Some(userinfo) => Some(unquote_unreserved(&encode_invalid(userinfo, USERINFO_PUNCTUATION))?),
        None => None,
    };

    // requests sends an address without a path to the root path
    let path = if raw_path.is_empty() {
        String::from("/")
    } else {
        unquote_unreserved(&encode_invalid(&remove_dot_segments(raw_path), PATH_PUNCTUATION))?
    };

    let query = prepare_component(raw_query)?;
    let fragment = prepare_component(raw_fragment)?;

    let bracketed_host = wrap_ipv6(&host_port.host, host_port.is_ipv6);

    let netloc = match host_port.explicit_port {
        Some(port) => format!("{bracketed_host}:{port}"),
        None => bracketed_host,
    };

    let url = build_url(scheme, userinfo.as_deref(), &netloc, &path, &query, &fragment);

    let mut path_and_query = path.clone();
    if !query.is_empty() {
        path_and_query.push('?');
        path_and_query.push_str(&query);
    }

    let authorization = match &userinfo {
        Some(userinfo) => credentials_authorization(userinfo)?,
        None => None,
    };

    let default_port = if is_tls { DEFAULT_HTTPS_PORT } else { DEFAULT_HTTP_PORT };

    Some(Target {
        is_tls,
        host: host_port.host,
        port: host_port.explicit_port.unwrap_or(default_port),
        url,
        path_and_query,
        authorization,
        is_ipv6: host_port.is_ipv6,
        scheme,
        netloc,
        path,
        query,
    })
}

/// Splits what follows the path of an address into its query string and its fragment, each `None` if the address
/// has no question mark or no hash sign introducing it.
fn split_query_and_fragment(after_path: &str) -> (Option<&str>, Option<&str>) {
    if let Some(rest) = after_path.strip_prefix('?') {
        return match rest.split_once('#') {
            Some((query, fragment)) => (Some(query), Some(fragment)),
            None => (Some(rest), None),
        };
    }

    (None, after_path.strip_prefix('#'))
}

/// Prepares a query string or a fragment, which an empty one or none at all leave out of the prepared address.
fn prepare_component(raw: Option<&str>) -> Option<String> {
    match raw {
        Some(text) if !text.is_empty() => unquote_unreserved(&encode_invalid(text, QUERY_PUNCTUATION)),
        _ => Some(String::new()),
    }
}

/// Builds the address as requests rebuilds it from its parts.
fn build_url(scheme: &str, userinfo: Option<&str>, netloc: &str, path: &str, query: &str, fragment: &str) -> String {
    let mut out = String::with_capacity(scheme.len() + netloc.len() + path.len() + query.len() + fragment.len() + 8);

    out.push_str(scheme);
    out.push_str(SCHEME_SEPARATOR);

    if let Some(userinfo) = userinfo {
        out.push_str(userinfo);
        out.push('@');
    }

    out.push_str(netloc);
    out.push_str(path);

    if !query.is_empty() {
        out.push('?');
        out.push_str(query);
    }

    if !fragment.is_empty() {
        out.push('#');
        out.push_str(fragment);
    }

    out
}

/// The host and the port of an address.
struct HostPort {
    /// The host in lowercase, without the brackets of an IPv6 address.
    host: String,

    /// Whether the host is an IPv6 address.
    is_ipv6: bool,

    /// The port the address names, `None` if it names none or names zero, which requests leaves out.
    explicit_port: Option<u16>,
}

/// Parses the host and the port of an address, as urllib3 matches them.
fn parse_host_port(host_port: &str) -> Option<HostPort> {
    let (host, port_text, is_ipv6) = if let Some(bracketed) = host_port.strip_prefix('[') {
        let (host, after_host) = bracketed.split_once(']')?;
        let port_text = if after_host.is_empty() {
            None
        } else {
            Some(after_host.strip_prefix(':')?)
        };
        (host, port_text, true)
    } else {
        match host_port.split_once(':') {
            Some((host, port_text)) => (host, Some(port_text), false),
            None => (host_port, None, false),
        }
    };

    if !is_valid_host(host, is_ipv6) {
        return None;
    }

    let explicit_port = match port_text {
        Some(text) => parse_port(text)?,
        None => None,
    };

    Some(HostPort {
        host: host.to_ascii_lowercase(),
        is_ipv6,
        explicit_port,
    })
}

/// Parses a port the way urllib3 matches it - decimal digits with any number of leading zeros, an empty port
/// meaning none. Returns `None` for a port urllib3 rejects, and `Some(None)` for none at all or for zero,
/// which requests leaves out of the address, so the default port of the scheme is used.
fn parse_port(text: &str) -> Option<Option<u16>> {
    if !text.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }

    let significant = text.trim_start_matches('0');

    if significant.len() > MAX_PORT_DIGITS {
        return None;
    }

    if significant.is_empty() {
        return Some(None);
    }

    // A port above the largest one is rejected by urllib3, as it is by this conversion
    let port = significant.parse::<u16>().ok()?;

    Some(Some(port))
}

/// Whether the transport sends to a host as it is, after it is put in lowercase - an IPv6 address without a zone,
/// or a name of ASCII letters, digits, dots, hyphens and underscores, whose labels need no IDNA encoding.
fn is_valid_host(host: &str, is_ipv6: bool) -> bool {
    if is_ipv6 {
        return host.contains(':') && host.bytes().all(|byte| byte.is_ascii_hexdigit() || matches!(byte, b':' | b'.'));
    }

    let is_ascii_name = host
        .bytes()
        .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-' | b'_'));

    // A host of dots alone is nothing once urllib3 removes its trailing dots
    is_ascii_name && !host.trim_end_matches('.').is_empty()
}

/// Puts an IPv6 address in brackets, as an address and a `Host` header write it.
fn wrap_ipv6(host: &str, is_ipv6: bool) -> String {
    if is_ipv6 { format!("[{host}]") } else { host.to_owned() }
}

/// Builds the value of a `Host` header the way `http.client` builds it, with the port only if it is not the default one.
fn build_host_header(host: &str, is_ipv6: bool, port: u16, default_port: u16) -> String {
    let host_part = wrap_ipv6(host, is_ipv6);

    if port == default_port {
        host_part
    } else {
        format!("{host_part}:{port}")
    }
}

/// Removes the dot segments of a path as urllib3 removes them.
fn remove_dot_segments(path: &str) -> String {
    let mut output: Vec<&str> = Vec::new();

    for segment in path.split('/') {
        match segment {
            // The current directory adds nothing to the path
            "." => {}

            // The parent directory removes the segment before it, if there is one
            ".." => {
                output.pop();
            }

            _ => output.push(segment),
        }
    }

    // A path that starts with a slash keeps it
    if path.starts_with('/') && output.first().is_none_or(|first| !first.is_empty()) {
        output.insert(0, "");
    }

    // A path that ends with a dot segment ends with a slash
    if path.ends_with("/.") || path.ends_with("/..") {
        output.push("");
    }

    output.join("/")
}

/// Removes the semicolon that ends the last segment of a path when nothing follows it, which `urlparse` reads
/// as empty parameters and `urlunparse` then leaves out.
fn remove_empty_parameters(path: &str) -> &str {
    let last_segment_start = path.rfind('/').map_or(0, |index| index + 1);
    let last_segment = path.get(last_segment_start..).unwrap_or_default();

    let is_empty_parameters = last_segment.find(';').is_some_and(|index| index + 1 == last_segment.len());

    if is_empty_parameters {
        path.strip_suffix(';').unwrap_or(path)
    } else {
        path
    }
}

/// Percent-encodes the characters of a component that urllib3 encodes, leaving the encoded octets alone
/// if every percent sign of the component begins one.
///
/// The digits of an encoded octet are put in uppercase first, as urllib3 does.
fn encode_invalid(component: &str, allowed: &[u8]) -> String {
    let source = component.as_bytes();
    let mut normalized = source.to_vec();

    let mut encoded_count = 0_usize;
    let mut position = 0;

    while let Some(&byte) = source.get(position) {
        let is_encoded_octet = byte == b'%' && source.get(position + 1..position + 3).is_some_and(is_hex_pair);

        if is_encoded_octet {
            for offset in 1..3 {
                if let Some(digit) = normalized.get_mut(position + offset) {
                    digit.make_ascii_uppercase();
                }
            }

            encoded_count += 1;
            position += 3;
        } else {
            position += 1;
        }
    }

    // A percent sign that does not begin an encoded octet means the component is not encoded yet,
    // so every percent sign in it is encoded as well
    let percent_count = source.iter().filter(|&&byte| byte == b'%').count();
    let is_percent_encoded = encoded_count == percent_count;

    let mut out = String::with_capacity(normalized.len());

    for byte in normalized {
        if (is_percent_encoded && byte == b'%') || byte.is_ascii_alphanumeric() || allowed.contains(&byte) {
            out.push(char::from(byte));
        } else {
            push_encoded_octet(&mut out, byte);
        }
    }

    out
}

/// Whether two bytes are hexadecimal digits, in either case.
fn is_hex_pair(pair: &[u8]) -> bool {
    pair.len() == 2 && pair.iter().all(u8::is_ascii_hexdigit)
}

/// Appends an octet percent-encoded with uppercase digits.
fn push_encoded_octet(out: &mut String, byte: u8) {
    let high = usize::from(byte >> HIGH_NIBBLE_SHIFT);
    let low = usize::from(byte & LOW_NIBBLE_MASK);

    out.push('%');
    out.push(char::from(UPPERCASE_HEX_DIGITS.get(high).copied().unwrap_or_default()));
    out.push(char::from(UPPERCASE_HEX_DIGITS.get(low).copied().unwrap_or_default()));
}

/// Decodes the encoded octets that stand for a letter, a digit or an unreserved mark, as requests does when it
/// re-quotes an address, returning `None` for a percent sign followed by two letters or digits that are not
/// hexadecimal, which requests quotes in a way of its own.
///
/// requests then quotes the characters it does not consider safe, of which a component urllib3 encoded has none.
fn unquote_unreserved(text: &str) -> Option<String> {
    let mut parts = text.split('%');
    let mut out = String::with_capacity(text.len());

    out.push_str(parts.next().unwrap_or_default());

    for part in parts {
        let pair = part.get(..2).filter(|pair| pair.bytes().all(|byte| byte.is_ascii_alphanumeric()));

        let Some(pair) = pair else {
            out.push('%');
            out.push_str(part);
            continue;
        };

        let octet = u8::from_str_radix(pair, HEX_RADIX).ok()?;

        if octet.is_ascii_alphanumeric() || UNRESERVED_PUNCTUATION.contains(&octet) {
            out.push(char::from(octet));
            out.push_str(part.get(2..).unwrap_or_default());
        } else {
            out.push('%');
            out.push_str(part);
        }
    }

    Some(out)
}

/// Decodes every percent-encoded octet of a component, leaving a percent sign that does not begin one as it is,
/// and decodes the octets as UTF-8, the way `urllib.parse.unquote` decodes them.
fn percent_decode(text: &str) -> String {
    let source = text.as_bytes();
    let mut decoded = Vec::with_capacity(source.len());
    let mut position = 0;

    while let Some(&byte) = source.get(position) {
        let octet = source
            .get(position + 1..position + 3)
            .filter(|pair| is_hex_pair(pair))
            .and_then(|pair| std::str::from_utf8(pair).ok())
            .and_then(|pair| u8::from_str_radix(pair, HEX_RADIX).ok());

        match (byte, octet) {
            (b'%', Some(octet)) => {
                decoded.push(octet);
                position += 3;
            }
            _ => {
                decoded.push(byte);
                position += 1;
            }
        }
    }

    String::from_utf8_lossy(&decoded).into_owned()
}

/// Returns the value of the `Authorization` header requests builds from the credentials in an address, `Some(None)`
/// if it builds none, or `None` if requests would fail to encode them, which it then reports itself.
fn credentials_authorization(userinfo: &str) -> Option<Option<Vec<u8>>> {
    // requests reads no credentials from an address whose credentials have no password
    let Some((username, password)) = userinfo.split_once(':') else {
        return Some(None);
    };

    if username.is_empty() && password.is_empty() {
        return Some(None);
    }

    // requests encodes the decoded user name and password as Latin-1
    let mut pair = encode_latin1(&percent_decode(username))?;
    let password = encode_latin1(&percent_decode(password))?;

    pair.push(b':');
    pair.extend_from_slice(&password);

    let mut out = BASIC_PREFIX.to_vec();
    out.extend_from_slice(encode_base64(&pair).as_bytes());

    Some(Some(out))
}

/// Encodes bytes as Base64 with padding.
fn encode_base64(input: &[u8]) -> String {
    let group_count = input.len().div_ceil(BASE64_GROUP_LEN);
    let mut out = String::with_capacity(group_count.saturating_mul(BASE64_GROUP_CHARS));

    for group in input.chunks(BASE64_GROUP_LEN) {
        let first = group.first().copied().unwrap_or_default();
        let second = group.get(1).copied();
        let third = group.get(2).copied();

        // The three bytes of a group make one number whose bits are read six at a time
        let joined = (u32::from(first) << (BYTE_BITS * 2))
            | (u32::from(second.unwrap_or_default()) << BYTE_BITS)
            | u32::from(third.unwrap_or_default());

        out.push(base64_char(joined >> (BASE64_CHAR_BITS * 3)));
        out.push(base64_char(joined >> (BASE64_CHAR_BITS * 2)));

        // A group short of its second or third byte is padded in place of the characters they would have produced
        out.push(if second.is_some() {
            base64_char(joined >> BASE64_CHAR_BITS)
        } else {
            BASE64_PADDING
        });
        out.push(if third.is_some() { base64_char(joined) } else { BASE64_PADDING });
    }

    out
}

/// The character of Base64 that stands for the lowest six bits of a number.
fn base64_char(value: u32) -> char {
    let index = usize::try_from(value & BASE64_CHAR_MASK).unwrap_or_default();
    char::from(BASE64_ALPHABET.get(index).copied().unwrap_or_default())
}

#[cfg(test)]
#[path = "address_tests.rs"]
mod tests;
