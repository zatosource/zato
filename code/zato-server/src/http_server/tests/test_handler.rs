use std::io::{Read, Write};
use std::os::unix::io::IntoRawFd;
use std::os::unix::net::UnixStream;

use zato_server_core::http_parser::parse_request;
use zato_server_core::http_response::write_response;

fn make_socketpair() -> (UnixStream, UnixStream) {
    UnixStream::pair().unwrap()
}

fn send_request(sock: &mut UnixStream, method: &str, path: &str, headers: &[(&str, &str)], body: &[u8]) {
    let mut req = format!("{} {} HTTP/1.1\r\n", method, path);
    for (k, v) in headers {
        req.push_str(&format!("{}: {}\r\n", k, v));
    }
    if !body.is_empty() {
        req.push_str(&format!("Content-Length: {}\r\n", body.len()));
    }
    req.push_str("\r\n");
    sock.write_all(req.as_bytes()).unwrap();
    if !body.is_empty() {
        sock.write_all(body).unwrap();
    }
}

fn read_response(sock: &mut UnixStream) -> String {
    let mut buf = vec![0u8; 65536];
    let n = sock.read(&mut buf).unwrap();
    String::from_utf8_lossy(&buf[..n]).to_string()
}

#[test]
fn test_parse_and_respond_single_exchange() {
    let (mut client, server) = make_socketpair();
    let server_fd = server.into_raw_fd();

    send_request(
        &mut client,
        "GET",
        "/hello",
        &[("Host", "localhost")],
        b"",
    );

    // Simulate: read from server_fd, parse, write response
    let mut buf = vec![0u8; 4096];
    let mut file = unsafe { std::fs::File::from_raw_fd(server_fd) };
    let n = file.read(&mut buf).unwrap();
    std::mem::forget(file);

    let (req, _consumed) = parse_request(&buf[..n]).unwrap();
    assert_eq!(req.method, "GET");
    assert_eq!(req.path, "/hello");
    assert_eq!(req.headers.get("HTTP_HOST").unwrap(), "localhost");

    let resp_body = b"OK";
    write_response(
        server_fd,
        "200 OK",
        &[("Content-Type".to_string(), "text/plain".to_string())],
        resp_body,
        1,
        false,
    )
    .unwrap();

    unsafe { libc::close(server_fd); }

    let response = read_response(&mut client);
    assert!(response.contains("HTTP/1.1 200 OK"));
    assert!(response.contains("Content-Length: 2"));
    assert!(response.ends_with("OK"));
}

use std::os::unix::io::{FromRawFd, RawFd};

#[test]
fn test_keepalive_two_requests() {
    let (mut client, server) = make_socketpair();
    let server_fd = server.into_raw_fd();

    // Send first request with keep-alive (default for HTTP/1.1)
    send_request(
        &mut client,
        "GET",
        "/first",
        &[("Host", "localhost")],
        b"",
    );

    // Read and parse first request
    let mut buf = vec![0u8; 4096];
    let mut file = unsafe { std::fs::File::from_raw_fd(server_fd) };
    let n = file.read(&mut buf).unwrap();
    std::mem::forget(file);

    let (req1, _) = parse_request(&buf[..n]).unwrap();
    assert_eq!(req1.path, "/first");

    write_response(
        server_fd,
        "200 OK",
        &[("Content-Type".to_string(), "text/plain".to_string())],
        b"first",
        1,
        true,
    )
    .unwrap();

    // Read first response
    let resp1 = read_response(&mut client);
    assert!(resp1.contains("HTTP/1.1 200 OK"));
    assert!(resp1.ends_with("first"));

    // Send second request on same connection
    send_request(
        &mut client,
        "GET",
        "/second",
        &[("Host", "localhost")],
        b"",
    );

    let mut buf2 = vec![0u8; 4096];
    let mut file2 = unsafe { std::fs::File::from_raw_fd(server_fd) };
    let n2 = file2.read(&mut buf2).unwrap();
    std::mem::forget(file2);

    let (req2, _) = parse_request(&buf2[..n2]).unwrap();
    assert_eq!(req2.path, "/second");

    write_response(
        server_fd,
        "200 OK",
        &[("Content-Type".to_string(), "text/plain".to_string())],
        b"second",
        1,
        false,
    )
    .unwrap();

    unsafe { libc::close(server_fd); }

    let resp2 = read_response(&mut client);
    assert!(resp2.contains("HTTP/1.1 200 OK"));
    assert!(resp2.ends_with("second"));
}

#[test]
fn test_connection_close_header() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    let conn = req.headers.get("HTTP_CONNECTION").unwrap();
    assert_eq!(conn.to_lowercase(), "close");
}

#[test]
fn test_http10_no_keepalive() {
    let raw = b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.version, 0);
    // No Connection header -> HTTP/1.0 defaults to close
    assert!(req.headers.get("HTTP_CONNECTION").is_none());
}

#[test]
fn test_post_body_roundtrip() {
    let (mut client, server) = make_socketpair();
    let server_fd = server.into_raw_fd();

    let body = b"{\"key\": \"value\"}";
    send_request(
        &mut client,
        "POST",
        "/api",
        &[
            ("Host", "localhost"),
            ("Content-Type", "application/json"),
        ],
        body,
    );

    let mut buf = vec![0u8; 4096];
    let mut file = unsafe { std::fs::File::from_raw_fd(server_fd) };
    let n = file.read(&mut buf).unwrap();
    std::mem::forget(file);

    let (req, _) = parse_request(&buf[..n]).unwrap();
    assert_eq!(req.method, "POST");
    assert_eq!(req.content_type, "application/json");
    assert_eq!(req.body, body.to_vec());

    unsafe { libc::close(server_fd); }
}

#[test]
fn test_remote_addr_and_port() {
    // This just tests the parser handles these as regular header data;
    // REMOTE_ADDR/REMOTE_PORT come from the address tuple, not headers.
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.method, "GET");
    // No REMOTE_ADDR in headers - it comes from the socket address
}

#[test]
fn test_error_response_on_bad_request() {
    let (writer, reader) = make_socketpair();
    let writer_fd = writer.into_raw_fd();
    let reader_fd = reader.into_raw_fd();

    zato_server_core::http_response::write_error_response(writer_fd, 400, 1).unwrap();
    unsafe { libc::close(writer_fd); }

    let mut file = unsafe { std::fs::File::from_raw_fd(reader_fd) };
    let mut output = String::new();
    file.read_to_string(&mut output).unwrap();

    assert!(output.starts_with("HTTP/1.1 400 Bad Request\r\n"));
    assert!(output.contains("Connection: close\r\n"));
}

#[test]
fn test_zero_length_post() {
    let raw = b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.method, "POST");
    assert_eq!(req.content_length, Some(0));
    assert!(req.body.is_empty());
}
