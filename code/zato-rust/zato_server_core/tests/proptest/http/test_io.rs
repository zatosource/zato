use proptest::prelude::*;
use zato_server_core::http::io::{parse_content_length, header_value_eq, trim_ows};

const MAX_REQUEST_SIZE: usize = 1_048_576;

proptest! {

    #[test]
    fn parse_content_length_never_exceeds_max(input in proptest::collection::vec(any::<u8>(), 0..256)) {
        let result = parse_content_length(&input);
        prop_assert!(result <= MAX_REQUEST_SIZE);
    }

    #[test]
    fn parse_content_length_valid_digits(n in 0usize..=MAX_REQUEST_SIZE) {
        let s = n.to_string();
        let result = parse_content_length(s.as_bytes());
        prop_assert_eq!(result, n);
    }

    #[test]
    fn parse_content_length_overflow_clamps(s in "[0-9]{20,40}") {
        let result = parse_content_length(s.as_bytes());
        prop_assert!(result <= MAX_REQUEST_SIZE);
    }

    #[test]
    fn parse_content_length_ignores_whitespace(n in 0usize..=999999, spaces in " {0,5}") {
        let s = format!("{}{}", spaces, n);
        let result = parse_content_length(s.as_bytes());
        prop_assert_eq!(result, n);
    }

    #[test]
    fn parse_content_length_stops_at_non_digit(n in 0usize..=999999, suffix in "[a-z]{1,5}") {
        let s = format!("{}{}", n, suffix);
        let result = parse_content_length(s.as_bytes());
        prop_assert_eq!(result, n);
    }

    #[test]
    fn trim_ows_idempotent(input in proptest::collection::vec(any::<u8>(), 0..128)) {
        let once = trim_ows(&input);
        let twice = trim_ows(once);
        prop_assert_eq!(once, twice);
    }

    #[test]
    fn trim_ows_no_leading_trailing_ws(input in proptest::collection::vec(any::<u8>(), 1..128)) {
        let trimmed = trim_ows(&input);
        if !trimmed.is_empty() {
            prop_assert!(trimmed[0] != b' ' && trimmed[0] != b'\t');
            prop_assert!(trimmed[trimmed.len() - 1] != b' ' && trimmed[trimmed.len() - 1] != b'\t');
        }
    }

    #[test]
    fn header_value_eq_matches_lowercase(s in "[a-zA-Z]{1,20}") {
        let lower = s.to_ascii_lowercase();
        prop_assert!(header_value_eq(s.as_bytes(), lower.as_bytes()));
    }

    #[test]
    fn header_value_eq_with_surrounding_ws(s in "[a-zA-Z]{1,20}", pad in " {0,5}") {
        let lower = s.to_ascii_lowercase();
        let padded = format!("{}{}{}", pad, s, pad);
        prop_assert!(header_value_eq(padded.as_bytes(), lower.as_bytes()));
    }

    #[test]
    fn header_value_eq_rejects_different_length(a in "[a-z]{1,10}", b in "[a-z]{11,20}") {
        prop_assert!(!header_value_eq(a.as_bytes(), b.as_bytes()));
    }
}
