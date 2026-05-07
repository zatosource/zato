use proptest::prelude::*;
use zato_server_core::http::io::{header_value_eq, parse_content_length, trim_ows};

const MAX_REQUEST_SIZE: usize = 1_048_576;

proptest! {

    #[test]
    fn parse_content_length_never_exceeds_max(input in proptest::collection::vec(any::<u8>(), 0..256)) {
        let result = parse_content_length(&input);
        prop_assert!(result <= MAX_REQUEST_SIZE);
    }

    #[test]
    fn parse_content_length_valid_digits(num in 0usize..=MAX_REQUEST_SIZE) {
        let text = num.to_string();
        let result = parse_content_length(text.as_bytes());
        prop_assert_eq!(result, num);
    }

    #[test]
    fn parse_content_length_overflow_clamps(text in "[0-9]{20,40}") {
        let result = parse_content_length(text.as_bytes());
        prop_assert!(result <= MAX_REQUEST_SIZE);
    }

    #[test]
    fn parse_content_length_ignores_whitespace(num in 0usize..=999_999, spaces in " {0,5}") {
        let text = format!("{spaces}{num}");
        let result = parse_content_length(text.as_bytes());
        prop_assert_eq!(result, num);
    }

    #[test]
    fn parse_content_length_stops_at_non_digit(num in 0usize..=999_999, suffix in "[a-z]{1,5}") {
        let text = format!("{num}{suffix}");
        let result = parse_content_length(text.as_bytes());
        prop_assert_eq!(result, num);
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
            prop_assert!(*trimmed.first().unwrap() != b' ' && *trimmed.first().unwrap() != b'\t');
            prop_assert!(*trimmed.last().unwrap() != b' ' && *trimmed.last().unwrap() != b'\t');
        }
    }

    #[test]
    fn header_value_eq_matches_lowercase(text in "[a-zA-Z]{1,20}") {
        let lower = text.to_ascii_lowercase();
        prop_assert!(header_value_eq(text.as_bytes(), lower.as_bytes()));
    }

    #[test]
    fn header_value_eq_with_surrounding_ws(text in "[a-zA-Z]{1,20}", pad in " {0,5}") {
        let lower = text.to_ascii_lowercase();
        let padded = format!("{pad}{text}{pad}");
        prop_assert!(header_value_eq(padded.as_bytes(), lower.as_bytes()));
    }

    #[test]
    fn header_value_eq_rejects_different_length(short in "[a-z]{1,10}", long in "[a-z]{11,20}") {
        prop_assert!(!header_value_eq(short.as_bytes(), long.as_bytes()));
    }
}
