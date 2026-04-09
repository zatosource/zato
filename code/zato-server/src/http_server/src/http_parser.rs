use bytes::BytesMut;
use std::collections::HashMap;
use std::io::{self, Read};
use std::os::unix::io::{FromRawFd, RawFd};

const MAX_HEADERS: usize = 64;
const INITIAL_BUF_SIZE: usize = 8192;

#[derive(Debug)]
pub enum ParseError {
    Incomplete,
    Invalid(String),
    TooManyHeaders,
    IoError(io::Error),
}

impl From<io::Error> for ParseError {
    fn from(e: io::Error) -> Self {
        ParseError::IoError(e)
    }
}

#[derive(Debug)]
pub struct ParsedRequest {
    pub method: String,
    pub path: String,
    pub query_string: String,
    pub raw_uri: String,
    pub version: u8,
    pub headers: HashMap<String, String>,
    pub content_type: String,
    pub content_length: Option<usize>,
    pub body: Vec<u8>,
}

/// Converts an HTTP header name to CGI-style HTTP_UPPER_UNDERSCORE.
/// Content-Type and Content-Length get special treatment per CGI spec.
fn header_to_cgi_key(name: &str) -> Option<String> {
    let upper = name.to_uppercase().replace('-', "_");
    match upper.as_str() {
        "CONTENT_TYPE" | "CONTENT_LENGTH" => None,
        _ => Some(format!("HTTP_{}", upper)),
    }
}

/// Parses a raw HTTP/1.1 request from the given buffer.
/// Returns (ParsedRequest, bytes_consumed) on success.
pub fn parse_request(buf: &[u8]) -> Result<(ParsedRequest, usize), ParseError> {
    let mut headers_buf = [httparse::EMPTY_HEADER; MAX_HEADERS];
    let mut req = httparse::Request::new(&mut headers_buf);

    let header_len = match req.parse(buf) {
        Ok(httparse::Status::Complete(len)) => len,
        Ok(httparse::Status::Partial) => return Err(ParseError::Incomplete),
        Err(e) => return Err(ParseError::Invalid(format!("{}", e))),
    };

    let method = req.method.ok_or_else(|| ParseError::Invalid("missing method".into()))?;
    let raw_uri = req.path.ok_or_else(|| ParseError::Invalid("missing path".into()))?;
    let version = req.version.unwrap_or(1);

    let (path, query_string) = match raw_uri.find('?') {
        Some(pos) => (&raw_uri[..pos], &raw_uri[pos + 1..]),
        None => (raw_uri, ""),
    };

    let mut headers = HashMap::new();
    let mut content_type = String::new();
    let mut content_length: Option<usize> = None;

    for header in req.headers.iter() {
        let name = header.name;
        let value = std::str::from_utf8(header.value)
            .map_err(|e| ParseError::Invalid(format!("non-utf8 header value: {}", e)))?;

        let upper_name = name.to_uppercase().replace('-', "_");
        match upper_name.as_str() {
            "CONTENT_TYPE" => {
                content_type = value.to_string();
            }
            "CONTENT_LENGTH" => {
                content_length = value
                    .trim()
                    .parse()
                    .map(Some)
                    .map_err(|_| ParseError::Invalid("invalid Content-Length".into()))?;
            }
            _ => {
                let key = format!("HTTP_{}", upper_name);
                headers.insert(key, value.to_string());
            }
        }
    }

    let body_start = header_len;
    let body = if let Some(len) = content_length {
        let available = buf.len() - body_start;
        if available < len {
            return Err(ParseError::Incomplete);
        }
        buf[body_start..body_start + len].to_vec()
    } else {
        Vec::new()
    };

    let total_consumed = body_start + body.len();

    Ok((
        ParsedRequest {
            method: method.to_string(),
            path: path.to_string(),
            query_string: query_string.to_string(),
            raw_uri: raw_uri.to_string(),
            version,
            headers,
            content_type,
            content_length,
            body,
        },
        total_consumed,
    ))
}

/// Reads from an fd until we have a complete HTTP request (headers + body).
/// Returns (ParsedRequest, remaining unconsumed bytes).
pub fn read_and_parse(fd: RawFd) -> Result<(ParsedRequest, BytesMut), ParseError> {
    let mut buf = BytesMut::with_capacity(INITIAL_BUF_SIZE);
    let mut tmp = [0u8; 4096];

    loop {
        let mut file = unsafe { std::fs::File::from_raw_fd(fd) };
        let n = file.read(&mut tmp);
        // Prevent the File from closing the fd on drop
        std::mem::forget(file);

        let n = n?;
        if n == 0 {
            return Err(ParseError::IoError(io::Error::new(
                io::ErrorKind::UnexpectedEof,
                "connection closed",
            )));
        }

        buf.extend_from_slice(&tmp[..n]);

        match parse_request(&buf) {
            Ok((parsed, consumed)) => {
                let remaining = buf.split_off(consumed);
                return Ok((parsed, remaining));
            }
            Err(ParseError::Incomplete) => continue,
            Err(e) => return Err(e),
        }
    }
}

/// Reads from an fd with pre-existing leftover bytes.
pub fn read_and_parse_with_leftover(
    fd: RawFd,
    leftover: &mut BytesMut,
) -> Result<ParsedRequest, ParseError> {
    // First try to parse from leftovers alone
    if !leftover.is_empty() {
        match parse_request(leftover) {
            Ok((parsed, consumed)) => {
                let _ = leftover.split_to(consumed);
                return Ok(parsed);
            }
            Err(ParseError::Incomplete) => {}
            Err(e) => return Err(e),
        }
    }

    let mut tmp = [0u8; 4096];
    loop {
        let mut file = unsafe { std::fs::File::from_raw_fd(fd) };
        let n = file.read(&mut tmp);
        std::mem::forget(file);

        let n = n?;
        if n == 0 {
            return Err(ParseError::IoError(io::Error::new(
                io::ErrorKind::UnexpectedEof,
                "connection closed",
            )));
        }

        leftover.extend_from_slice(&tmp[..n]);

        match parse_request(leftover) {
            Ok((parsed, consumed)) => {
                let _ = leftover.split_to(consumed);
                return Ok(parsed);
            }
            Err(ParseError::Incomplete) => continue,
            Err(e) => return Err(e),
        }
    }
}
