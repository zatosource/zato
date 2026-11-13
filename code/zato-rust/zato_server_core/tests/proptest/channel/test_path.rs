use proptest::prelude::*;
use zato_server_core::channel::path::{normalize_path_info, to_internal_accept, unquote};

#[test]
fn empty_and_dot_segments_are_resolved() {
    assert_eq!(normalize_path_info("/api//customers/./123"), "/api/customers/123");
    assert_eq!(normalize_path_info("/api/orders/../customers"), "/api/customers");
    assert_eq!(normalize_path_info("/../../etc"), "/etc");
    assert_eq!(normalize_path_info(""), "/");
    assert_eq!(normalize_path_info("/"), "/");
    assert_eq!(normalize_path_info("//"), "/");
}

#[test]
fn trailing_slash_is_preserved() {
    assert_eq!(normalize_path_info("/api/customers/"), "/api/customers/");
    assert_eq!(normalize_path_info("/api/customers/.."), "/api");
    assert_eq!(normalize_path_info("/api/.."), "/");
    assert_eq!(normalize_path_info("/api/../"), "/");
}

#[test]
fn segments_are_decoded_after_dot_resolution() {
    assert_eq!(normalize_path_info("/api/%2E%2E/customers"), "/api/../customers");
    assert_eq!(normalize_path_info("/api/a%2Fb"), "/api/a%2Fb");
    assert_eq!(normalize_path_info("/api/John%20Smith"), "/api/John Smith");
    assert_eq!(normalize_path_info("/api/%C5%BC"), "/api/\u{17c}");
}

#[test]
fn invalid_utf8_is_replaced() {
    assert_eq!(unquote("%FF"), "\u{fffd}");
    assert_eq!(unquote("a%C5"), "a\u{fffd}");
    assert_eq!(unquote("%C5\u{17c}%BC"), "\u{fffd}\u{17c}\u{fffd}");
}

#[test]
fn incomplete_escapes_are_kept() {
    assert_eq!(unquote("100%"), "100%");
    assert_eq!(unquote("%4"), "%4");
    assert_eq!(unquote("%zz"), "%zz");
    assert_eq!(unquote("%%41"), "%A");
}

#[test]
fn accept_header_internal_form() {
    assert_eq!(to_internal_accept(None), "haanyHTTP_SEPhaany");
    assert_eq!(to_internal_accept(Some("")), "haanyHTTP_SEPhaany");
    assert_eq!(to_internal_accept(Some("application/json")), "applicationHTTP_SEPjson");
    assert_eq!(to_internal_accept(Some("text/*")), "textHTTP_SEPhaany");
}

proptest! {

    #[test]
    fn normalized_path_starts_with_one_slash(path in "[a-z%./]{0,40}") {
        let normalized = normalize_path_info(&path);
        prop_assert!(normalized.starts_with('/'));
        prop_assert!(!normalized.starts_with("//"));
    }

    #[test]
    fn plain_segments_are_unchanged(segments in prop::collection::vec("[a-z0-9_-]{1,10}", 1..6)) {
        let path = format!("/{}", segments.join("/"));
        prop_assert_eq!(normalize_path_info(&path), path);
    }

    #[test]
    fn unquote_without_percent_is_identity(text in "\\PC{0,30}") {
        if !text.contains('%') {
            prop_assert_eq!(unquote(&text), text);
        }
    }
}
