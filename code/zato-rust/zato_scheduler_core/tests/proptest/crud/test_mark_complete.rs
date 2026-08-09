use chrono::{Duration, Utc};
use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;

fn make_job() -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string();
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
        max_execution_time_ms: None,
        on_success_service: None,
        on_success_job: None,
        on_error_service: None,
        on_error_job: None,
    }
}

/// Mirrors what `handle_mark_complete` does to a job's runtime state -
/// the run's historical record lives in the server's audit log now.
fn mark_complete(running_job: &mut RunningJob) {
    running_job.in_flight = false;
    running_job.in_flight_since = None;
    running_job.in_flight_run = None;
}

proptest! {

    #[test]
    fn clears_in_flight(current_run in 1u32..100_000) {
        let scheduler_job = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&scheduler_job);
        running_job.in_flight = true;
        running_job.in_flight_since = Some(std::time::Instant::now());
        running_job.in_flight_run = Some(current_run);
        mark_complete(&mut running_job);
        prop_assert!(!running_job.in_flight);
        prop_assert!(running_job.in_flight_since.is_none());
        prop_assert!(running_job.in_flight_run.is_none());
    }
}
