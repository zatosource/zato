use proptest::prelude::*;
use zato_scheduler_core::types::OnMissedPolicy;

proptest! {

    #[test]
    fn as_str_is_always_known_variant(input in "\\PC{0,40}") {
        let policy = OnMissedPolicy::from(input.as_str());
        let out = policy.as_str();
        prop_assert!(out == "skip" || out == "run_once");
    }

    #[test]
    fn skip_roundtrips(_n in 0u32..100) {
        let policy = OnMissedPolicy::from("skip");
        prop_assert_eq!(policy.as_str(), "skip");
        prop_assert_eq!(policy, OnMissedPolicy::Skip);
    }

    #[test]
    fn unknown_defaults_to_run_once(input in "[a-z]{1,20}") {
        if input != "skip" {
            let policy = OnMissedPolicy::from(input.as_str());
            prop_assert_eq!(policy, OnMissedPolicy::RunOnce);
        }
    }
}
