use zato_server_core::http_parser::{parse_request, ParseError};

#[test]
fn test_minimal_get() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, consumed) = parse_request(raw).unwrap();
    assert_eq!(req.method, "GET");
    assert_eq!(req.path, "/");
    assert_eq!(req.query_string, "");
    assert_eq!(req.raw_uri, "/");
    assert_eq!(req.version, 1);
    assert!(req.body.is_empty());
    assert_eq!(consumed, raw.len());
}

#[test]
fn test_get_with_query_string() {
    let raw = b"GET /path?foo=1&bar=2 HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.path, "/path");
    assert_eq!(req.query_string, "foo=1&bar=2");
    assert_eq!(req.raw_uri, "/path?foo=1&bar=2");
}

#[test]
fn test_post_with_body() {
    let body = b"hello world";
    let raw = format!(
        "POST /api HTTP/1.1\r\nHost: localhost\r\nContent-Length: {}\r\n\r\n{}",
        body.len(),
        std::str::from_utf8(body).unwrap()
    );
    let (req, consumed) = parse_request(raw.as_bytes()).unwrap();
    assert_eq!(req.method, "POST");
    assert_eq!(req.path, "/api");
    assert_eq!(req.body, body.to_vec());
    assert_eq!(req.content_length, Some(body.len()));
    assert_eq!(consumed, raw.len());
}

#[test]
fn test_multiple_headers() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\nAccept: text/html\r\nUser-Agent: test/1.0\r\nX-Custom: value\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.headers.get("HTTP_HOST").unwrap(), "localhost");
    assert_eq!(req.headers.get("HTTP_ACCEPT").unwrap(), "text/html");
    assert_eq!(req.headers.get("HTTP_USER_AGENT").unwrap(), "test/1.0");
    assert_eq!(req.headers.get("HTTP_X_CUSTOM").unwrap(), "value");
}

#[test]
fn test_http10_version() {
    let raw = b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.version, 0);
}

#[test]
fn test_http11_version() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.version, 1);
}

#[test]
fn test_header_case_normalization() {
    let raw = b"GET / HTTP/1.1\r\naccept-encoding: gzip\r\nx-forwarded-for: 1.2.3.4\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(
        req.headers.get("HTTP_ACCEPT_ENCODING").unwrap(),
        "gzip"
    );
    assert_eq!(
        req.headers.get("HTTP_X_FORWARDED_FOR").unwrap(),
        "1.2.3.4"
    );
}

#[test]
fn test_content_type_extracted_separately() {
    let raw = b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: 0\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.content_type, "application/json");
    assert!(req.headers.get("HTTP_CONTENT_TYPE").is_none());
}

#[test]
fn test_content_length_extracted_separately() {
    let raw = b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhello";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.content_length, Some(5));
    assert!(req.headers.get("HTTP_CONTENT_LENGTH").is_none());
}

#[test]
fn test_incomplete_request() {
    let raw = b"GET / HTTP/1.1\r\nHost: loc";
    match parse_request(raw) {
        Err(ParseError::Incomplete) => {}
        other => panic!("expected Incomplete, got {:?}", other),
    }
}

#[test]
fn test_incomplete_body() {
    let raw = b"POST / HTTP/1.1\r\nContent-Length: 100\r\n\r\nshort";
    match parse_request(raw) {
        Err(ParseError::Incomplete) => {}
        other => panic!("expected Incomplete, got {:?}", other),
    }
}

#[test]
fn test_malformed_request_line() {
    let raw = b"GARBAGE\r\n\r\n";
    match parse_request(raw) {
        Err(ParseError::Invalid(_)) => {}
        Err(ParseError::Incomplete) => {} // httparse may also return partial
        other => panic!("expected Invalid or Incomplete, got {:?}", other),
    }
}

#[test]
fn test_zero_headers() {
    let raw = b"GET / HTTP/1.1\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.method, "GET");
    assert!(req.headers.is_empty());
}

#[test]
fn test_all_standard_methods() {
    for method in &["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"] {
        let raw = format!("{} / HTTP/1.1\r\nHost: localhost\r\n\r\n", method);
        let (req, _) = parse_request(raw.as_bytes()).unwrap();
        assert_eq!(req.method, *method);
    }
}

#[test]
fn test_percent_encoded_uri() {
    let raw = b"GET /path%20with%20spaces?q=%3F HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.raw_uri, "/path%20with%20spaces?q=%3F");
    assert_eq!(req.path, "/path%20with%20spaces");
    assert_eq!(req.query_string, "q=%3F");
}

#[test]
fn test_empty_query_string() {
    let raw = b"GET /path? HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.path, "/path");
    assert_eq!(req.query_string, "");
    assert_eq!(req.raw_uri, "/path?");
}

#[test]
fn test_no_query_string() {
    let raw = b"GET /path HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.path, "/path");
    assert_eq!(req.query_string, "");
    assert_eq!(req.raw_uri, "/path");
}

#[test]
fn test_zero_content_length() {
    let raw = b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.content_length, Some(0));
    assert!(req.body.is_empty());
}

#[test]
fn test_missing_content_type() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.content_type, "");
}

#[test]
fn test_binary_body() {
    let body: Vec<u8> = (0..=255).collect();
    let header = format!(
        "POST /bin HTTP/1.1\r\nHost: localhost\r\nContent-Length: {}\r\n\r\n",
        body.len()
    );
    let mut raw: Vec<u8> = header.into_bytes();
    raw.extend_from_slice(&body);

    let (req, consumed) = parse_request(&raw).unwrap();
    assert_eq!(req.body, body);
    assert_eq!(consumed, raw.len());
}

#[test]
fn test_large_body() {
    let body = vec![b'x'; 1_048_576]; // 1MB
    let header = format!(
        "POST /large HTTP/1.1\r\nHost: localhost\r\nContent-Length: {}\r\n\r\n",
        body.len()
    );
    let mut raw: Vec<u8> = header.into_bytes();
    raw.extend_from_slice(&body);

    let (req, consumed) = parse_request(&raw).unwrap();
    assert_eq!(req.body.len(), 1_048_576);
    assert_eq!(consumed, raw.len());
}

#[test]
fn test_authorization_header() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost\r\nAuthorization: Basic dXNlcjpwYXNz\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(
        req.headers.get("HTTP_AUTHORIZATION").unwrap(),
        "Basic dXNlcjpwYXNz"
    );
}

#[test]
fn test_header_values_with_colons() {
    let raw = b"GET / HTTP/1.1\r\nHost: localhost:8080\r\n\r\n";
    let (req, _) = parse_request(raw).unwrap();
    assert_eq!(req.headers.get("HTTP_HOST").unwrap(), "localhost:8080");
}
