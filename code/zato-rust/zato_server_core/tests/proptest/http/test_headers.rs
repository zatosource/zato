use proptest::prelude::*;
use zato_server_core::logging::transform_header_key;

proptest! {

    #[test]
    fn http_keys_always_produce_lowercase(suffix in "[A-Z_]{1,30}") {
        let key = format!("HTTP_{}", suffix);
        let header = transform_header_key(&key).unwrap();
        let lower = header.to_ascii_lowercase();
        prop_assert_eq!(header, lower);
    }

    #[test]
    fn underscores_become_hyphens(suffix in "[A-Z]{1,5}(_[A-Z]{1,5}){1,4}") {
        let key = format!("HTTP_{}", suffix);
        let header = transform_header_key(&key).unwrap();
        prop_assert!(!header.contains('_'));
        let expected_hyphens = suffix.chars().filter(|&c| c == '_').count();
        let actual_hyphens = header.chars().filter(|&c| c == '-').count();
        prop_assert_eq!(actual_hyphens, expected_hyphens);
    }

    #[test]
    fn non_http_keys_return_none(key in "[A-Z]{1,20}") {
        if !key.starts_with("HTTP_") {
            prop_assert!(transform_header_key(&key).is_none());
        }
    }

    #[test]
    fn roundtrip_length_preserved(suffix in "[A-Z_]{1,30}") {
        let key = format!("HTTP_{}", suffix);
        let header = transform_header_key(&key).unwrap();
        prop_assert_eq!(header.len(), suffix.len());
    }
}
