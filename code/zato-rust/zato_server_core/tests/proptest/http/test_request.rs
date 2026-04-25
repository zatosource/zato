use proptest::prelude::*;
use zato_server_core::http::make_cid_public;

proptest! {

    #[test]
    fn never_more_than_four_segments(seg_count in 4usize..10) {
        let segments: Vec<String> = (0..seg_count).map(|idx| format!("seg{idx}")).collect();
        let cid = segments.join("-");
        let result = make_cid_public(&cid);
        let parts: Vec<&str> = result.split('-').collect();
        prop_assert!(parts.len() <= 4, "got {} parts from {}", parts.len(), cid);
    }

    #[test]
    fn four_segment_cid_unchanged(
        seg1 in "[a-z0-9]{4,10}",
        seg2 in "[a-z0-9]{4,10}",
        seg3 in "[a-z0-9]{4,10}",
        seg4 in "[a-z0-9]{4,10}",
    ) {
        let cid = format!("{seg1}-{seg2}-{seg3}-{seg4}");
        let result = make_cid_public(&cid);
        prop_assert_eq!(result, cid);
    }

    #[test]
    fn five_segment_cid_drops_last(
        seg1 in "[a-z0-9]{4,10}",
        seg2 in "[a-z0-9]{4,10}",
        seg3 in "[a-z0-9]{4,10}",
        seg4 in "[a-z0-9]{4,10}",
        seg5 in "[a-z0-9]{4,10}",
    ) {
        let cid = format!("{seg1}-{seg2}-{seg3}-{seg4}-{seg5}");
        let result = make_cid_public(&cid);
        let expected = format!("{seg1}-{seg2}-{seg3}-{seg4}");
        prop_assert_eq!(result, expected);
    }

    #[test]
    fn no_dashes_returns_original(text in "[a-z0-9]{1,30}") {
        let result = make_cid_public(&text);
        prop_assert_eq!(result, text);
    }

    #[test]
    fn empty_string_returns_empty(_dummy in Just(())) {
        let result = make_cid_public("");
        prop_assert_eq!(result, "");
    }
}
