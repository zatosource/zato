use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::{RunningJob, ExecutionRecord};
use zato_server_core::model::SchedulerJob;

fn make_job() -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1))
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

fn mark_complete(rj: &mut RunningJob, outcome: &str, duration_ms: u64) {
    rj.in_flight = false;
    rj.in_flight_since = None;
    if let Some(last) = rj.history.back_mut() {
        last.duration_ms = Some(duration_ms);
        if outcome != "executed" {
            last.outcome = outcome.to_string();
        }
    }
}

proptest! {

    #[test]
    fn clears_in_flight(duration_ms in 0u64..100_000) {
        let sj = make_job();
        let mut rj = RunningJob::from_scheduler_job(&sj);
        rj.in_flight = true;
        rj.in_flight_since = Some(std::time::Instant::now());
        rj.record_execution(ExecutionRecord::new("p", "a", "executed", 1));
        mark_complete(&mut rj, "executed", duration_ms);
        prop_assert!(!rj.in_flight);
        prop_assert!(rj.in_flight_since.is_none());
    }

    #[test]
    fn records_duration(duration_ms in 1u64..100_000) {
        let sj = make_job();
        let mut rj = RunningJob::from_scheduler_job(&sj);
        rj.in_flight = true;
        rj.record_execution(ExecutionRecord::new("p", "a", "executed", 1));
        mark_complete(&mut rj, "executed", duration_ms);
        let last = rj.history.back().unwrap();
        prop_assert_eq!(last.duration_ms, Some(duration_ms));
    }

    #[test]
    fn non_executed_outcome_overwrites(duration_ms in 0u64..100_000) {
        let sj = make_job();
        let mut rj = RunningJob::from_scheduler_job(&sj);
        rj.in_flight = true;
        rj.record_execution(ExecutionRecord::new("p", "a", "executed", 1));
        mark_complete(&mut rj, "timeout", duration_ms);
        let last = rj.history.back().unwrap();
        prop_assert_eq!(&last.outcome, "timeout");
    }

    #[test]
    fn executed_outcome_preserved(duration_ms in 0u64..100_000) {
        let sj = make_job();
        let mut rj = RunningJob::from_scheduler_job(&sj);
        rj.in_flight = true;
        rj.record_execution(ExecutionRecord::new("p", "a", "executed", 1));
        mark_complete(&mut rj, "executed", duration_ms);
        let last = rj.history.back().unwrap();
        prop_assert_eq!(&last.outcome, "executed");
    }
}
