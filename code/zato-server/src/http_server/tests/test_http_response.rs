use std::os::unix::io::IntoRawFd;
use zato_server_core::http_response::{parse_status, write_response, write_error_response};

fn make_socketpair() -> (std::os::unix::io::RawFd, std::os::unix::io::RawFd) {
    let (a, b) = std::os::unix::net::UnixStream::pair().unwrap();
    (a.into_raw_fd(), b.into_raw_fd())
}

fn read_all(fd: std::os::unix::io::RawFd) -> Vec<u8> {
    use std::io::Read;
    use std::os::unix::io::FromRawFd;

    let mut file = unsafe { std::fs::File::from_raw_fd(fd) };
    let mut buf = Vec::new();
    let _ = file.read_to_end(&mut buf);
    // Don't forget: we own the fd now, File will close it on drop
    buf
}

#[test]
fn test_parse_status_full() {
    let (code, reason) = parse_status("200 OK");
    assert_eq!(code, 200);
    assert_eq!(reason, "OK");
}

#[test]
fn test_parse_status_code_only() {
    let (code, reason) = parse_status("404");
    assert_eq!(code, 404);
    assert_eq!(reason, "Not Found");
}

#[test]
fn test_parse_status_internal_server_error() {
    let (code, reason) = parse_status("500 Internal Server Error");
    assert_eq!(code, 500);
    assert_eq!(reason, "Internal Server Error");
}

#[test]
fn test_simple_200_response() {
    let (writer_fd, reader_fd) = make_socketpair();
    let body = b"Hello, World!";
    let headers = vec![
        ("Content-Type".to_string(), "text/plain".to_string()),
    ];

    write_response(writer_fd, "200 OK", &headers, body, 1, true).unwrap();

    // Close writer so reader gets EOF
    unsafe { libc::close(writer_fd); }

    let output = read_all(reader_fd);
    let output_str = String::from_utf8_lossy(&output);

    assert!(output_str.starts_with("HTTP/1.1 200 OK\r\n"));
    assert!(output_str.contains("Content-Type: text/plain\r\n"));
    assert!(output_str.contains(&format!("Content-Length: {}\r\n", body.len())));
    assert!(output_str.ends_with("Hello, World!"));
}

#[test]
fn test_multiple_headers() {
    let (writer_fd, reader_fd) = make_socketpair();
    let headers = vec![
        ("Content-Type".to_string(), "application/json".to_string()),
        ("X-Custom".to_string(), "value1".to_string()),
        ("X-Other".to_string(), "value2".to_string()),
    ];

    write_response(writer_fd, "200 OK", &headers, b"{}", 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.contains("Content-Type: application/json\r\n"));
    assert!(output.contains("X-Custom: value1\r\n"));
    assert!(output.contains("X-Other: value2\r\n"));
}

#[test]
fn test_empty_body() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_response(writer_fd, "204 No Content", &[], b"", 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.contains("Content-Length: 0\r\n"));
    assert!(output.starts_with("HTTP/1.1 204 No Content\r\n"));
}

#[test]
fn test_binary_body() {
    let (writer_fd, reader_fd) = make_socketpair();
    let body: Vec<u8> = (0..=255).collect();
    write_response(writer_fd, "200 OK", &[], &body, 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = read_all(reader_fd);
    // The body should appear at the end, after \r\n\r\n
    let separator = b"\r\n\r\n";
    let pos = output
        .windows(separator.len())
        .position(|w| w == separator)
        .unwrap();
    let response_body = &output[pos + separator.len()..];
    assert_eq!(response_body, &body[..]);
}

#[test]
fn test_common_status_codes() {
    for (input, expected_code) in &[
        ("200 OK", 200u16),
        ("201 Created", 201),
        ("204 No Content", 204),
        ("301 Moved Permanently", 301),
        ("400 Bad Request", 400),
        ("403 Forbidden", 403),
        ("404 Not Found", 404),
        ("500 Internal Server Error", 500),
        ("502 Bad Gateway", 502),
        ("503 Service Unavailable", 503),
    ] {
        let (writer_fd, reader_fd) = make_socketpair();
        write_response(writer_fd, input, &[], b"", 1, false).unwrap();
        unsafe { libc::close(writer_fd); }

        let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
        let expected_line = format!("HTTP/1.1 {} ", expected_code);
        assert!(
            output.starts_with(&expected_line),
            "for status '{}': expected line starting with '{}' but got '{}'",
            input,
            expected_line,
            &output[..output.find('\r').unwrap_or(output.len())]
        );
    }
}

#[test]
fn test_content_length_auto_calculated() {
    let (writer_fd, reader_fd) = make_socketpair();
    let body = b"12345";
    write_response(writer_fd, "200 OK", &[], body, 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.contains("Content-Length: 5\r\n"));
}

#[test]
fn test_explicit_content_length_not_duplicated() {
    let (writer_fd, reader_fd) = make_socketpair();
    let body = b"12345";
    let headers = vec![("Content-Length".to_string(), "5".to_string())];
    write_response(writer_fd, "200 OK", &headers, body, 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert_eq!(output.matches("Content-Length").count(), 1);
}

#[test]
fn test_http10_connection_close() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_response(writer_fd, "200 OK", &[], b"", 0, false).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.starts_with("HTTP/1.0 200 OK\r\n"));
    // HTTP/1.0 without keep-alive should not add Connection header
    // (default is close for 1.0)
    assert!(!output.contains("Connection:"));
}

#[test]
fn test_http10_keepalive() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_response(writer_fd, "200 OK", &[], b"", 0, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.contains("Connection: keep-alive\r\n"));
}

#[test]
fn test_http11_connection_close() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_response(writer_fd, "200 OK", &[], b"", 1, false).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.contains("Connection: close\r\n"));
}

#[test]
fn test_http11_no_keepalive_header() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_response(writer_fd, "200 OK", &[], b"", 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    // HTTP/1.1 default is keep-alive, no header needed
    assert!(!output.contains("Connection:"));
}

#[test]
fn test_large_body_no_truncation() {
    let (writer_fd, reader_fd) = make_socketpair();
    let body = vec![b'A'; 1_048_576]; // 1MB
    write_response(writer_fd, "200 OK", &[], &body, 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = read_all(reader_fd);
    let separator = b"\r\n\r\n";
    let pos = output
        .windows(separator.len())
        .position(|w| w == separator)
        .unwrap();
    let response_body = &output[pos + separator.len()..];
    assert_eq!(response_body.len(), 1_048_576);
}

#[test]
fn test_error_response_500() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_error_response(writer_fd, 500, 1).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.starts_with("HTTP/1.1 500 Internal Server Error\r\n"));
    assert!(output.contains("Content-Type: text/plain\r\n"));
    assert!(output.ends_with("500 Internal Server Error"));
}

#[test]
fn test_error_response_400() {
    let (writer_fd, reader_fd) = make_socketpair();
    write_error_response(writer_fd, 400, 1).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.starts_with("HTTP/1.1 400 Bad Request\r\n"));
}

#[test]
fn test_header_values_with_special_chars() {
    let (writer_fd, reader_fd) = make_socketpair();
    let headers = vec![
        ("Content-Type".to_string(), "text/html; charset=utf-8".to_string()),
        ("X-Values".to_string(), "a, b, c".to_string()),
    ];
    write_response(writer_fd, "200 OK", &headers, b"", 1, true).unwrap();
    unsafe { libc::close(writer_fd); }

    let output = String::from_utf8_lossy(&read_all(reader_fd)).to_string();
    assert!(output.contains("Content-Type: text/html; charset=utf-8\r\n"));
    assert!(output.contains("X-Values: a, b, c\r\n"));
}
