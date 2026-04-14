use zato_server_core::http::io::{parse_cl, val_eq_ci, trim_ows};

const MAX_REQUEST_SIZE: usize = 1_048_576;

#[test]
fn parse_cl_zero() {
    assert_eq!(parse_cl(b"0"), 0);
}

#[test]
fn parse_cl_exact_max() {
    let s = MAX_REQUEST_SIZE.to_string();
    assert_eq!(parse_cl(s.as_bytes()), MAX_REQUEST_SIZE);
}

#[test]
fn parse_cl_above_max_clamps() {
    let s = (MAX_REQUEST_SIZE + 1).to_string();
    assert_eq!(parse_cl(s.as_bytes()), MAX_REQUEST_SIZE);
}

#[test]
fn parse_cl_empty() {
    assert_eq!(parse_cl(b""), 0);
}

#[test]
fn parse_cl_non_digit() {
    assert_eq!(parse_cl(b"abc"), 0);
}

#[test]
fn parse_cl_leading_spaces() {
    assert_eq!(parse_cl(b"  42"), 42);
}

#[test]
fn val_eq_ci_same_case() {
    assert!(val_eq_ci(b"hello", b"hello"));
}

#[test]
fn val_eq_ci_mixed_case() {
    assert!(val_eq_ci(b"HeLLo", b"hello"));
}

#[test]
fn val_eq_ci_with_ows() {
    assert!(val_eq_ci(b" hello ", b"hello"));
}

#[test]
fn val_eq_ci_mismatch() {
    assert!(!val_eq_ci(b"hello", b"world"));
}

#[test]
fn val_eq_ci_different_length() {
    assert!(!val_eq_ci(b"hi", b"hello"));
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
