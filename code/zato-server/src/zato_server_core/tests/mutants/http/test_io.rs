use zato_server_core::http::io::{parse_content_length, header_value_eq, trim_ows};

const MAX_REQUEST_SIZE: usize = 1_048_576;

#[test]
fn parse_content_length_zero() {
    assert_eq!(parse_content_length(b"0"), 0);
}

#[test]
fn parse_content_length_exact_max() {
    let s = MAX_REQUEST_SIZE.to_string();
    assert_eq!(parse_content_length(s.as_bytes()), MAX_REQUEST_SIZE);
}

#[test]
fn parse_content_length_above_max_clamps() {
    let s = (MAX_REQUEST_SIZE + 1).to_string();
    assert_eq!(parse_content_length(s.as_bytes()), MAX_REQUEST_SIZE);
}

#[test]
fn parse_content_length_empty() {
    assert_eq!(parse_content_length(b""), 0);
}

#[test]
fn parse_content_length_non_digit() {
    assert_eq!(parse_content_length(b"abc"), 0);
}

#[test]
fn parse_content_length_leading_spaces() {
    assert_eq!(parse_content_length(b"  42"), 42);
}

#[test]
fn header_value_eq_same_case() {
    assert!(header_value_eq(b"hello", b"hello"));
}

#[test]
fn header_value_eq_mixed_case() {
    assert!(header_value_eq(b"HeLLo", b"hello"));
}

#[test]
fn header_value_eq_with_ows() {
    assert!(header_value_eq(b" hello ", b"hello"));
}

#[test]
fn header_value_eq_mismatch() {
    assert!(!header_value_eq(b"hello", b"world"));
}

#[test]
fn header_value_eq_different_length() {
    assert!(!header_value_eq(b"hi", b"hello"));
}

#[test]
fn trim_ows_empty() {
    assert_eq!(trim_ows(b""), b"");
}

#[test]
fn trim_ows_only_spaces() {
    assert_eq!(trim_ows(b"   "), b"");
}

#[test]
fn trim_ows_only_tabs() {
    assert_eq!(trim_ows(b"\t\t"), b"");
}

#[test]
fn trim_ows_inner_preserved() {
    assert_eq!(trim_ows(b" a b "), b"a b");
}

#[test]
fn trim_ows_no_whitespace() {
    assert_eq!(trim_ows(b"abc"), b"abc");
}
