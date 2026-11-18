//! Unit tests of the preparation of addresses.

use super::*;

/// The prepared form of an address the transport is expected to send itself.
fn prepared(url: &str) -> Target {
    parse(url).unwrap_or_else(|| panic!("Address not prepared: {url}"))
}

#[test]
fn plain_address() {
    let target = prepared("http://127.0.0.1:8080/api/customers?id=1");

    assert!(!target.is_tls);
    assert_eq!(target.host, "127.0.0.1");
    assert_eq!(target.port, 8080);
    assert_eq!(target.host_header(), "127.0.0.1:8080");
    assert_eq!(target.path_and_query, "/api/customers?id=1");
    assert_eq!(target.url, "http://127.0.0.1:8080/api/customers?id=1");
    assert!(target.authorization.is_none());
}

#[test]
fn default_port_is_not_in_host_header() {
    let target = prepared("https://api.example.com/v1");

    assert!(target.is_tls);
    assert_eq!(target.port, DEFAULT_HTTPS_PORT);
    assert_eq!(target.host_header(), "api.example.com");
}

#[test]
fn explicit_default_port_stays_in_url() {
    let target = prepared("http://api.example.com:80/v1");

    assert_eq!(target.host_header(), "api.example.com");
    assert_eq!(target.url, "http://api.example.com:80/v1");
}

#[test]
fn address_without_path() {
    let target = prepared("http://localhost:1234");
    assert_eq!(target.path_and_query, "/");
    assert_eq!(target.url, "http://localhost:1234/");

    let target = prepared("http://localhost:1234?page=2");
    assert_eq!(target.path_and_query, "/?page=2");
    assert_eq!(target.url, "http://localhost:1234/?page=2");
}

#[test]
fn scheme_and_host_in_lowercase() {
    let target = prepared("HTTP://Example.COM/A");

    assert_eq!(target.host, "example.com");
    assert_eq!(target.url, "http://example.com/A");
    assert_eq!(target.path_and_query, "/A");
}

#[test]
fn fragment_kept_in_url_only() {
    let target = prepared("http://example.com/a?b=1#section?x");

    assert_eq!(target.path_and_query, "/a?b=1");
    assert_eq!(target.url, "http://example.com/a?b=1#section?x");
}

#[test]
fn empty_query_and_fragment_removed() {
    let target = prepared("http://example.com/a?#");

    assert_eq!(target.path_and_query, "/a");
    assert_eq!(target.url, "http://example.com/a");
}

#[test]
fn dot_segments() {
    assert_eq!(prepared("http://localhost/a/../b").path_and_query, "/b");
    assert_eq!(prepared("http://localhost/a/./b").path_and_query, "/a/b");
    assert_eq!(prepared("http://localhost/a/b/..").path_and_query, "/a/");
    assert_eq!(prepared("http://localhost/..").path_and_query, "/");
    assert_eq!(prepared("http://localhost/.well-known").path_and_query, "/.well-known");
    assert_eq!(prepared("http://localhost/a?path=/../b").path_and_query, "/a?path=/../b");
}

#[test]
fn invalid_characters_encoded() {
    assert_eq!(prepared("http://example.com/a b").path_and_query, "/a%20b");
    assert_eq!(prepared("http://example.com/a[1]").path_and_query, "/a%5B1%5D");
    assert_eq!(prepared("http://example.com/caf\u{e9}").path_and_query, "/caf%C3%A9");
    assert_eq!(prepared("http://example.com/a?q=x y&z=\"").path_and_query, "/a?q=x%20y&z=%22");
}

#[test]
fn percent_encoding() {
    assert_eq!(prepared("http://example.com/a%2fb").path_and_query, "/a%2Fb");
    assert_eq!(prepared("http://example.com/a%41%7e").path_and_query, "/aA~");
    assert_eq!(prepared("http://example.com/a%zz").path_and_query, "/a%25zz");
    assert_eq!(prepared("http://example.com/a%2F%2").path_and_query, "/a%252F%252");
    assert_eq!(prepared("http://example.com/a?x=%C3%BC").path_and_query, "/a?x=%C3%BC");
}

#[test]
fn ports() {
    assert_eq!(prepared("http://example.com:/a").url, "http://example.com/a");
    assert_eq!(prepared("http://example.com:0080/a").url, "http://example.com:80/a");

    let target = prepared("http://example.com:0/a");
    assert_eq!(target.port, DEFAULT_HTTP_PORT);
    assert_eq!(target.url, "http://example.com/a");

    assert!(parse("http://example.com:65536/a").is_none());
    assert!(parse("http://example.com:123456/a").is_none());
    assert!(parse("http://example.com:8x/a").is_none());
}

#[test]
fn ipv6_host() {
    let target = prepared("http://[::1]:9000/items");

    assert_eq!(target.host, "::1");
    assert_eq!(target.host_header(), "[::1]:9000");
    assert_eq!(target.url, "http://[::1]:9000/items");
    assert_eq!(target.connect_line(), "CONNECT [::1]:9000 HTTP/1.1\r\n");
    assert_eq!(target.connect_host_header(), "::1:9000");
}

#[test]
fn trailing_dot_of_host() {
    let target = prepared("https://example.com./a");

    assert_eq!(target.host, "example.com.");
    assert_eq!(target.host_header(), "example.com");
    assert_eq!(target.server_name(), "example.com");
    assert_eq!(target.tunneled_host_header(), "example.com.");
}

#[test]
fn credentials() {
    let target = prepared("http://user:pa%40ss@example.com/a");
    assert_eq!(target.url, "http://user:pa%40ss@example.com/a");
    assert_eq!(target.authorization, Some(b"Basic dXNlcjpwYUBzcw==".to_vec()));

    let target = prepared("http://a@b:c@example.com/");
    assert_eq!(target.url, "http://a%40b:c@example.com/");
    assert_eq!(target.authorization, Some(b"Basic YUBiOmM=".to_vec()));

    assert!(prepared("http://user@example.com/").authorization.is_none());
    assert!(prepared("http://:@example.com/").authorization.is_none());
    assert_eq!(
        prepared("http://user:@example.com/").authorization,
        Some(b"Basic dXNlcjo=".to_vec())
    );

    assert!(parse("http://u:%C5%81@example.com/").is_none());
}

#[test]
fn absolute_form() {
    let target = prepared("http://u:p@Example.com:8080/a/%2E%2E/b;?x=1#f");

    assert_eq!(target.url, "http://u:p@example.com:8080/a/../b;?x=1#f");
    assert_eq!(target.path_and_query, "/a/../b;?x=1");
    assert_eq!(target.absolute_form(), "http://example.com:8080/b?x=1");
    assert_eq!(target.netloc(), "example.com:8080");
}

#[test]
fn addresses_left_to_requests() {
    assert!(parse("ftp://example.com/file").is_none());
    assert!(parse("http://ex\u{e4}mple.com/").is_none());
    assert!(parse("http://example.com\\a").is_none());
    assert!(parse(" http://example.com/").is_none());
    assert!(parse("http:///a").is_none());
    assert!(parse("http://[fe80::1%25eth0]/").is_none());
    assert!(parse("http://.../").is_none());
}

#[test]
fn base64() {
    assert_eq!(encode_base64(b""), "");
    assert_eq!(encode_base64(b"f"), "Zg==");
    assert_eq!(encode_base64(b"fo"), "Zm8=");
    assert_eq!(encode_base64(b"foo"), "Zm9v");
    assert_eq!(encode_base64(b"\xff\xfe\xfd\xfc"), "//79/A==");
}
