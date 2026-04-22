use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_server_core::model::SchedulerJob;

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
        on_missed: None,
        max_execution_time_ms: None,
    }
}

proptest! {

    #[test]
    fn interval_ms_equals_expected_sum(
        w in 0u32..53,
        d in 0u32..366,
        h in 0u32..24,
        m in 0u32..60,
        s in 0u32..60,
    ) {
        let job = make_job(w, d, h, m, s);
        let ms = RunningJob::compute_interval_ms(&job);
        let expected = w as u64 * 7 * 86_400_000
            + d as u64 * 86_400_000
            + h as u64 * 3_600_000
            + m as u64 * 60_000
            + s as u64 * 1_000;
        prop_assert_eq!(ms, expected);
    }

    #[test]
    fn all_zeros_yields_zero(
        _n in 0u32..100,
    ) {
        let job = make_job(0, 0, 0, 0, 0);
        prop_assert_eq!(RunningJob::compute_interval_ms(&job), 0);
    }
}
