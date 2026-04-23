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
        prop_assert_eq!(rec.delay_ms, 0);
        prop_assert!(rec.duration_ms.is_none());
        prop_assert!(rec.error.is_none());
    }

    #[test]
    fn builder_chain_sets_all_fields(
        delay in 0u64..100_000,
        duration in 0u64..100_000,
        error in "[a-z ]{5,30}",
    ) {
        let rec = ExecutionRecord::new("p", "a", "ok", 1)
            .with_delay(delay)
            .with_duration(duration)
            .with_error(error.clone());
        prop_assert_eq!(rec.delay_ms, delay);
        prop_assert_eq!(rec.duration_ms, Some(duration));
        prop_assert_eq!(rec.error.as_ref().unwrap(), &error);
    }

}
