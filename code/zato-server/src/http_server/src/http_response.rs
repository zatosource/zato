use std::io::{self, Write};
use std::os::unix::io::{FromRawFd, RawFd};

/// Mapping from numeric status codes to reason phrases.
fn reason_phrase(code: u16) -> &'static str {
    match code {
        200 => "OK",
        201 => "Created",
        204 => "No Content",
        301 => "Moved Permanently",
        302 => "Found",
        304 => "Not Modified",
        400 => "Bad Request",
        401 => "Unauthorized",
        403 => "Forbidden",
        404 => "Not Found",
        405 => "Method Not Allowed",
        408 => "Request Timeout",
        429 => "Too Many Requests",
        500 => "Internal Server Error",
        502 => "Bad Gateway",
        503 => "Service Unavailable",
        504 => "Gateway Timeout",
        _ => "Unknown",
    }
}

/// Parses a status string like "200 OK" into (200, "OK").
/// Falls back to looking up the reason phrase if only a code is given.
pub fn parse_status(status: &str) -> (u16, String) {
    let trimmed = status.trim();
    if let Some(pos) = trimmed.find(' ') {
        let code_str = &trimmed[..pos];
        let reason = trimmed[pos + 1..].trim();
        let code = code_str.parse::<u16>().unwrap_or(500);
        (code, reason.to_string())
    } else {
        let code = trimmed.parse::<u16>().unwrap_or(500);
        (code, reason_phrase(code).to_string())
    }
}

/// Serializes an HTTP/1.1 response and writes it to the given fd.
pub fn write_response(
    fd: RawFd,
    status: &str,
    headers: &[(String, String)],
    body: &[u8],
    http_version: u8,
    keep_alive: bool,
) -> io::Result<()> {
    let (code, reason) = parse_status(status);

    let protocol = if http_version == 0 {
        "HTTP/1.0"
    } else {
        "HTTP/1.1"
    };

    let mut out = Vec::with_capacity(256 + body.len());

    // Status line
    out.extend_from_slice(format!("{} {} {}\r\n", protocol, code, reason).as_bytes());

    // Headers from Python
    let mut has_content_length = false;
    let mut has_connection = false;
    for (name, value) in headers {
        let name_lower = name.to_lowercase();
        if name_lower == "content-length" {
            has_content_length = true;
        }
        if name_lower == "connection" {
            has_connection = true;
        }
        out.extend_from_slice(format!("{}: {}\r\n", name, value).as_bytes());
    }

    if !has_content_length {
        out.extend_from_slice(format!("Content-Length: {}\r\n", body.len()).as_bytes());
    }

    if !has_connection {
        if http_version == 0 && keep_alive {
            out.extend_from_slice(b"Connection: keep-alive\r\n");
        } else if http_version == 1 && !keep_alive {
            out.extend_from_slice(b"Connection: close\r\n");
        }
    }

    // End of headers
    out.extend_from_slice(b"\r\n");

    // Body
    out.extend_from_slice(body);

    // Write to fd
    let mut file = unsafe { std::fs::File::from_raw_fd(fd) };
    let result = file.write_all(&out);
    std::mem::forget(file);

    result
}

/// Writes a minimal error response (no Python involvement).
pub fn write_error_response(fd: RawFd, code: u16, http_version: u8) -> io::Result<()> {
    let reason = reason_phrase(code);
    let body = format!("{} {}", code, reason);
    write_response(
        fd,
        &format!("{} {}", code, reason),
        &[("Content-Type".to_string(), "text/plain".to_string())],
        body.as_bytes(),
        http_version,
        false,
    )
}
