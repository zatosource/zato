use chrono::Utc;
use proptest::prelude::*;
use std::time::Instant;
use zato_scheduler_core::job::{ExecutionRecord, RunningJob};
use zato_scheduler_core::model::SchedulerJob;
use zato_scheduler_core::scheduler::{SchedulerState, check_in_flight_timeouts};

fn make_active_job() -> SchedulerJob {
    let start = (Utc::now() - chrono::Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string();
    SchedulerJob {
        id: 1,
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
        let scheduler_job = make_active_job();
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        check_in_flight_timeouts(&mut state);
        let running_job = state.jobs.get(&1).unwrap();
        prop_assert!(!running_job.in_flight);
        prop_assert!(running_job.history.is_empty());
    }

    #[test]
    fn recent_in_flight_not_timed_out(max_exec in 10_000u64..100_000) {
        let mut scheduler_job = make_active_job();
        scheduler_job.max_execution_time_ms = Some(max_exec);
        let mut running_job = RunningJob::from_scheduler_job(&scheduler_job);
        running_job.in_flight = true;
        running_job.in_flight_since = Some(Instant::now());
        running_job.record_execution(ExecutionRecord::new("p", "a", "executed", 1));
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        check_in_flight_timeouts(&mut state);
        let running_job = state.jobs.get(&1).unwrap();
        prop_assert!(running_job.in_flight);
    }
}
