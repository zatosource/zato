use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;

fn make_job(weeks: u32, days: u32, hours: u32, minutes: u32, seconds: u32) -> SchedulerJob {
    SchedulerJob {
        id: 1,
        name: "test".into(),
        is_active: true,
        service: "svc".into(),
        job_type: "interval_based".into(),
        start_date: "2026-01-01T00:00:00".into(),
        extra: None,
        weeks: Some(weeks),
        days: Some(days),
        hours: Some(hours),
        minutes: Some(minutes),
        seconds: Some(seconds),
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        max_execution_time_ms: None,
    }
}

proptest! {

    #[test]
    fn interval_ms_equals_expected_sum(
        weeks in 0u32..53,
        days in 0u32..366,
        hours in 0u32..24,
        mins in 0u32..60,
        secs in 0u32..60,
    ) {
        let job = make_job(weeks, days, hours, mins, secs);
        let interval = RunningJob::compute_interval_ms(&job);
        let expected = u64::from(weeks) * 7 * 86_400_000
            + u64::from(days) * 86_400_000
            + u64::from(hours) * 3_600_000
            + u64::from(mins) * 60_000
            + u64::from(secs) * 1_000;
        prop_assert_eq!(interval, expected);
    }

    #[test]
    fn all_zeros_yields_zero(
        _n in 0u32..100,
    ) {
        let job = make_job(0, 0, 0, 0, 0);
        prop_assert_eq!(RunningJob::compute_interval_ms(&job), 0);
    }
}
