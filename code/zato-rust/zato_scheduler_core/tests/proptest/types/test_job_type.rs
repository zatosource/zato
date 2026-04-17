use proptest::prelude::*;
use zato_scheduler_core::types::JobType;

proptest! {

    #[test]
    fn as_str_is_always_known_variant(s in "\\PC{0,40}") {
        let jt = JobType::from(s.as_str());
        let out = jt.as_str();
        prop_assert!(out == "one_time" || out == "interval_based");
    }

    #[test]
    fn display_matches_as_str(s in "\\PC{0,40}") {
        let jt = JobType::from(s.as_str());
        prop_assert_eq!(jt.to_string(), jt.as_str());
    }

    #[test]
    fn one_time_roundtrips(_n in 0u32..100) {
        let jt = JobType::from("one_time");
        prop_assert_eq!(jt.as_str(), "one_time");
        prop_assert_eq!(jt, JobType::OneTime);
    }

    #[test]
    fn unknown_defaults_to_interval_based(s in "[a-z]{1,20}") {
        if s != "one_time" {
            let jt = JobType::from(s.as_str());
            prop_assert_eq!(jt, JobType::IntervalBased);
        }
    }
}
