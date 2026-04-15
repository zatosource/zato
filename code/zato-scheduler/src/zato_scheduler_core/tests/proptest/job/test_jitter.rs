use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_server_core::model::SchedulerJob;

fn make_jitter_job(jitter_ms: u32) -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string();
    SchedulerJob {
        id: "jitter-test".into(),
        name: "jitter-test".into(),
        is_active: true,
        service: "svc".into(),
        job_type: "interval_based".into(),
        start_date: start,
        extra: None,
        weeks: None,
        days: None,
        hours: None,
        minutes: Some(5),
        seconds: None,
        repeats: None,
        jitter_ms: Some(jitter_ms),
        timezone: None,
        calendar: None,
        on_missed: None,
        max_execution_time_ms: None,
    }
}

proptest! {

    #[test]
    fn zero_jitter_fires_on_interval_boundary(
        _n in 0u32..50,
    ) {
        let job = make_jitter_job(0);
        let rj = RunningJob::from_scheduler_job(&job);
        if let (Some(fire), Some(sd)) = (rj.next_fire_utc, rj.start_date) {
            let diff_ms = (fire - sd).num_milliseconds();
            prop_assert!(diff_ms >= 0);
            prop_assert_eq!(diff_ms % (5 * 60_000), 0);
        }
    }

    #[test]
    fn same_id_produces_same_jitter(_n in 0u32..20) {
        let job = make_jitter_job(5000);
        let rj1 = RunningJob::from_scheduler_job(&job);
        let rj2 = RunningJob::from_scheduler_job(&job);
        prop_assert_eq!(rj1.next_fire_utc, rj2.next_fire_utc);
    }
}
