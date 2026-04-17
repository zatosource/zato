use std::time::Duration;
use proptest::prelude::*;
use chrono::{Duration as CDuration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::scheduler::{SchedulerState, compute_sleep_duration};
use zato_server_core::model::SchedulerJob;

fn make_job_at_offset(id: &str, offset_secs: i64) -> SchedulerJob {
    let start = (Utc::now() + CDuration::seconds(offset_secs))
        .format("%Y-%m-%dT%H:%M:%S")
        .to_string();
    SchedulerJob {
        id: id.into(),
        name: id.into(),
        is_active: true,
        service: "svc".into(),
        job_type: "interval_based".into(),
        start_date: start,
        extra: None,
        weeks: None,
        days: None,
        hours: Some(1),
        minutes: None,
        seconds: None,
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
    fn empty_state_returns_60s(_n in 0u32..50) {
        let state = SchedulerState::new();
        let dur = compute_sleep_duration(&state);
        prop_assert_eq!(dur, Duration::from_secs(60));
    }

    #[test]
    fn sleep_duration_capped_at_60s(offset in 120i64..600) {
        let mut state = SchedulerState::new();
        let sj = make_job_at_offset("j1", offset);
        let rj = RunningJob::from_scheduler_job(&sj);
        state.jobs.insert("j1".into(), rj);
        let dur = compute_sleep_duration(&state);
        prop_assert!(dur <= Duration::from_secs(60));
    }

    #[test]
    fn sleep_duration_at_least_1ms(offset in -100i64..1) {
        let mut state = SchedulerState::new();
        let sj = make_job_at_offset("j1", offset);
        let rj = RunningJob::from_scheduler_job(&sj);
        state.jobs.insert("j1".into(), rj);
        let dur = compute_sleep_duration(&state);
        prop_assert!(dur >= Duration::from_millis(1));
    }
}
