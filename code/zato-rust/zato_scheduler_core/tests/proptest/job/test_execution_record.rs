use proptest::prelude::*;
use zato_scheduler_core::job::ExecutionRecord;

proptest! {

    #[test]
    fn new_record_has_correct_fields(
        planned in "[a-z]{5,20}",
        actual in "[a-z]{5,20}",
        outcome in "[a-z]{3,10}",
        run in 0u32..1000,
    ) {
        let rec = ExecutionRecord::new(&planned, &actual, &outcome, run);
        prop_assert_eq!(&rec.planned_fire_time_iso, &planned);
        prop_assert_eq!(&rec.actual_fire_time_iso, &actual);
        prop_assert_eq!(&rec.outcome, &outcome);
        prop_assert_eq!(rec.current_run, run);
        prop_assert_eq!(rec.dispatch_latency_ms, 0);
        prop_assert!(rec.duration_ms.is_none());
        prop_assert!(rec.error.is_none());
    }

    #[test]
    fn builder_chain_sets_all_fields(
        latency in 0u64..100_000,
        duration in 0u64..100_000,
        error in "[a-z ]{5,30}",
    ) {
        let rec = ExecutionRecord::new("p", "a", "ok", 1)
            .with_latency(latency)
            .with_duration(duration)
            .with_error(error.clone());
        prop_assert_eq!(rec.dispatch_latency_ms, latency);
        prop_assert_eq!(rec.duration_ms, Some(duration));
        prop_assert_eq!(rec.error.as_ref().unwrap(), &error);
    }

    #[test]
    fn to_dict_items_always_has_base_keys(
        planned in "[a-z]{5,10}",
        actual in "[a-z]{5,10}",
        outcome in "[a-z]{3,10}",
        run in 0u32..100,
    ) {
        let rec = ExecutionRecord::new(&planned, &actual, &outcome, run);
        let items = rec.to_dict_items();
        let keys: Vec<&str> = items.iter().map(|(k, _)| *k).collect();
        prop_assert!(keys.contains(&"planned_fire_time_iso"));
        prop_assert!(keys.contains(&"actual_fire_time_iso"));
        prop_assert!(keys.contains(&"dispatch_latency_ms"));
        prop_assert!(keys.contains(&"outcome"));
        prop_assert!(keys.contains(&"current_run"));
        prop_assert_eq!(items.len(), 5);
    }

    #[test]
    fn to_dict_items_includes_optional_fields(
        duration in 0u64..100_000,
        error in "[a-z]{5,20}",
    ) {
        let rec = ExecutionRecord::new("p", "a", "ok", 1)
            .with_duration(duration)
            .with_error(error);
        let items = rec.to_dict_items();
        let keys: Vec<&str> = items.iter().map(|(k, _)| *k).collect();
        prop_assert!(keys.contains(&"duration_ms"));
        prop_assert!(keys.contains(&"error"));
        prop_assert_eq!(items.len(), 7);
    }
}
