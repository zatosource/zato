use chrono::{Duration, Utc};
use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;
use zato_scheduler_core::scheduler::SchedulerState;

fn make_job(id: i64, job_type: &str, is_active: bool, minutes: u32, future_start: bool) -> SchedulerJob {
    let start = if future_start {
        (Utc::now() + Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string()
    } else {
        (Utc::now() - Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string()
    };
    SchedulerJob {
        id,
        name: format!("job-{id}"),
        is_active,
        service: "svc".into(),
        job_type: job_type.into(),
        start_date: start,
        extra: None,
        weeks: None,
        days: None,
        hours: None,
        minutes: Some(minutes),
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        max_execution_time_ms: None,
    }
}

proptest! {

    #[test]
    fn active_interval_job_has_next_fire(minutes in 1u32..60) {
        let scheduler_job = make_job(1, "interval_based", true, minutes, false);
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        let running_job = state.jobs.get(&1).unwrap();
        prop_assert!(running_job.next_fire_utc.is_some());
        prop_assert!(!running_job.in_flight);
        prop_assert_eq!(running_job.current_run, 0);
        prop_assert!(running_job.history.is_empty());
    }

    #[test]
    fn active_one_time_future_start_has_fire(minutes in 1u32..60) {
        let scheduler_job = make_job(1, "one_time", true, minutes, true);
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        prop_assert!(running_job.next_fire_utc.is_some());
    }

    #[test]
    fn inactive_job_has_no_fire(minutes in 1u32..60) {
        let scheduler_job = make_job(1, "interval_based", false, minutes, false);
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        prop_assert!(running_job.next_fire_utc.is_none());
    }

    #[test]
    fn interval_ms_matches_expected(minutes in 1u32..60) {
        let scheduler_job = make_job(1, "interval_based", true, minutes, false);
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        prop_assert_eq!(running_job.interval_ms, u64::from(minutes) * 60_000);
    }

    #[test]
    fn create_always_fresh_state(minutes in 1u32..60) {
        let scheduler_job = make_job(1, "interval_based", true, minutes, false);
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        prop_assert!(!running_job.in_flight);
        prop_assert!(running_job.in_flight_since.is_none());
        prop_assert_eq!(running_job.current_run, 0);
        prop_assert!(running_job.history.is_empty());
    }
}
