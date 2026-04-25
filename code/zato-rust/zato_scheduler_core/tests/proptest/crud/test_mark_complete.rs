use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::{RunningJob, ExecutionRecord};
use zato_scheduler_core::model::SchedulerJob;

fn make_job() -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1))
        .format("%Y-%m-%dT%H:%M:%S")
        .to_string();
    SchedulerJob {
        id: 1,
        name: "test".into(),
        is_active: true,
        service: "svc".into(),
        job_type: "interval_based".into(),
        start_date: start,
        extra: None,
        weeks: None, days: None, hours: None,
        minutes: Some(5),
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        on_missed: None,
        max_execution_time_ms: None,
    }
}

fn mark_complete(running_job: &mut RunningJob, outcome: &str, duration_ms: u64) {
    running_job.in_flight = false;
    running_job.in_flight_since = None;
    if let Some(last) = running_job.history.back_mut() {
        last.duration_ms = Some(duration_ms);
        last.outcome = outcome.to_string();
    }
}

proptest! {

    #[test]
    fn clears_in_flight(duration_ms in 0u64..100_000) {
        let sj = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        running_job.in_flight = true;
        running_job.in_flight_since = Some(std::time::Instant::now());
        running_job.record_execution(ExecutionRecord::new("p", "a", "running", 1));
        mark_complete(&mut running_job, "ok", duration_ms);
        prop_assert!(!running_job.in_flight);
        prop_assert!(running_job.in_flight_since.is_none());
    }

    #[test]
    fn records_duration(duration_ms in 1u64..100_000) {
        let sj = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        running_job.in_flight = true;
        running_job.record_execution(ExecutionRecord::new("p", "a", "running", 1));
        mark_complete(&mut running_job, "ok", duration_ms);
        let last = running_job.history.back().unwrap();
        prop_assert_eq!(last.duration_ms, Some(duration_ms));
    }

    #[test]
    fn outcome_set_to_timeout(duration_ms in 0u64..100_000) {
        let sj = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        running_job.in_flight = true;
        running_job.record_execution(ExecutionRecord::new("p", "a", "running", 1));
        mark_complete(&mut running_job, "timeout", duration_ms);
        let last = running_job.history.back().unwrap();
        prop_assert_eq!(&last.outcome, "timeout");
    }

    #[test]
    fn outcome_set_to_ok(duration_ms in 0u64..100_000) {
        let sj = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        running_job.in_flight = true;
        running_job.record_execution(ExecutionRecord::new("p", "a", "running", 1));
        mark_complete(&mut running_job, "ok", duration_ms);
        let last = running_job.history.back().unwrap();
        prop_assert_eq!(&last.outcome, "ok");
    }
}
