use proptest::prelude::*;
use zato_scheduler_core::types::OnMissedPolicy;

proptest! {

    #[test]
    fn as_str_is_always_known_variant(s in "\\PC{0,40}") {
        let p = OnMissedPolicy::from(s.as_str());
        let out = p.as_str();
        prop_assert!(out == "skip" || out == "run_once");
    }

    #[test]
    fn skip_roundtrips(_n in 0u32..100) {
        let p = OnMissedPolicy::from("skip");
        prop_assert_eq!(p.as_str(), "skip");
        prop_assert_eq!(p, OnMissedPolicy::Skip);
    }

    #[test]
    fn unknown_defaults_to_run_once(s in "[a-z]{1,20}") {
        if s != "skip" {
            let p = OnMissedPolicy::from(s.as_str());
            prop_assert_eq!(p, OnMissedPolicy::RunOnce);
        }
    }
}
