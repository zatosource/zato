use proptest::prelude::*;
use zato_server_core::http::make_cid_public;

proptest! {

    #[test]
    fn never_more_than_four_segments(seg_count in 4usize..10) {
        let segments: Vec<String> = (0..seg_count).map(|i| format!("seg{i}")).collect();
        let cid = segments.join("-");
        let result = make_cid_public(&cid);
        let parts: Vec<&str> = result.split('-').collect();
        prop_assert!(parts.len() <= 4, "got {} parts from {}", parts.len(), cid);
    }

    #[test]
    fn four_segment_cid_unchanged(
        a in "[a-z0-9]{4,10}",
        b in "[a-z0-9]{4,10}",
        c in "[a-z0-9]{4,10}",
        d in "[a-z0-9]{4,10}",
    ) {
        let cid = format!("{a}-{b}-{c}-{d}");
        let result = make_cid_public(&cid);
        prop_assert_eq!(result, cid);
    }

    #[test]
    fn five_segment_cid_drops_last(
        a in "[a-z0-9]{4,10}",
        b in "[a-z0-9]{4,10}",
        c in "[a-z0-9]{4,10}",
        d in "[a-z0-9]{4,10}",
        e in "[a-z0-9]{4,10}",
    ) {
        let cid = format!("{a}-{b}-{c}-{d}-{e}");
        let result = make_cid_public(&cid);
        let expected = format!("{a}-{b}-{c}-{d}");
        prop_assert_eq!(result, expected);
    }

    #[test]
    fn no_dashes_returns_original(s in "[a-z0-9]{1,30}") {
        let result = make_cid_public(&s);
        prop_assert_eq!(result, s);
    }

    #[test]
    fn empty_string_returns_empty(_dummy in Just(())) {
        let result = make_cid_public("");
        prop_assert_eq!(result, "");
    }
}
