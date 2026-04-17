use proptest::prelude::*;
use std::time::Instant;
use chrono::Utc;
use zato_scheduler_core::job::{RunningJob, ExecutionRecord};
use zato_scheduler_core::scheduler::{SchedulerState, check_in_flight_timeouts};
use zato_server_core::model::SchedulerJob;

fn make_active_job() -> SchedulerJob {
    let start = (Utc::now() - chrono::Duration::hours(1))
        .format("%Y-%m-%dT%H:%M:%S")
        .to_string();
    SchedulerJob {
        id: "j1".into(),
        name: "test".into(),
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
        jitter_ms: None,
        timezone: None,
        calendar: None,
        on_missed: None,
        max_execution_time_ms: Some(1_000),
    }
}

proptest! {

    #[test]
    fn non_in_flight_jobs_not_touched(_n in 0u32..50) {
        let sj = make_active_job();
        let rj = RunningJob::from_scheduler_job(&sj);
        let mut state = SchedulerState::new();
        state.jobs.insert("j1".into(), rj);
        check_in_flight_timeouts(&mut state);
        let rj = state.jobs.get("j1").unwrap();
        prop_assert!(!rj.in_flight);
        prop_assert!(rj.history.is_empty());
    }

    #[test]
    fn recent_in_flight_not_timed_out(max_exec in 10_000u64..100_000) {
        let mut sj = make_active_job();
        sj.max_execution_time_ms = Some(max_exec);
        let mut rj = RunningJob::from_scheduler_job(&sj);
        rj.in_flight = true;
        rj.in_flight_since = Some(Instant::now());
        rj.record_execution(ExecutionRecord::new("p", "a", "executed", 1));
        let mut state = SchedulerState::new();
        state.jobs.insert("j1".into(), rj);
        check_in_flight_timeouts(&mut state);
        let rj = state.jobs.get("j1").unwrap();
        prop_assert!(rj.in_flight);
    }
}
