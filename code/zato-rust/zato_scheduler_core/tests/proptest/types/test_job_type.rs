use proptest::prelude::*;
use zato_scheduler_core::types::JobType;

proptest! {

    #[test]
    fn as_str_is_always_known_variant(input in "\\PC{0,40}") {
        let job_type = JobType::from(input.as_str());
        let out = job_type.as_str();
        prop_assert!(out == "one_time" || out == "interval_based");
    }

    #[test]
    fn display_matches_as_str(input in "\\PC{0,40}") {
        let job_type = JobType::from(input.as_str());
        prop_assert_eq!(job_type.to_string(), job_type.as_str());
    }

    #[test]
    fn one_time_roundtrips(_n in 0u32..100) {
        let job_type = JobType::from("one_time");
        prop_assert_eq!(job_type.as_str(), "one_time");
        prop_assert_eq!(job_type, JobType::OneTime);
    }

    #[test]
    fn unknown_defaults_to_interval_based(input in "[a-z]{1,20}") {
        if input != "one_time" {
            let job_type = JobType::from(input.as_str());
            prop_assert_eq!(job_type, JobType::IntervalBased);
        }
    }
}
