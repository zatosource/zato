use chrono::{Duration, Utc};
use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;

fn make_interval_job(minutes: u32) -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(2)).format("%Y-%m-%dT%H:%M:%S").to_string();
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
        minutes: Some(minutes),
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        on_missed: None,
        max_execution_time_ms: None,
    }
}

fn make_one_time_job() -> SchedulerJob {
    let start = (Utc::now() + Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string();
    SchedulerJob {
        id: 1,
        name: "test".into(),
        is_active: true,
        service: "svc".into(),
        job_type: "one_time".into(),
        start_date: start,
        extra: None,
        weeks: None,
        days: None,
        hours: None,
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
    fn one_time_clears_fire_after_advance(_n in 0u32..50) {
        let job = make_one_time_job();
        let mut running_job = RunningJob::from_scheduler_job(&job);
        prop_assert!(running_job.next_fire_utc.is_some());
        running_job.advance_to_next(Utc::now());
        prop_assert!(running_job.next_fire_utc.is_none());
    }

    #[test]
    fn interval_advances_to_later_fire(minutes in 1u32..60) {
        let job = make_interval_job(minutes);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let now = Utc::now();
        let first_fire = running_job.next_fire_utc;
        running_job.advance_to_next(now);
        if let (Some(first_fire_time), Some(next_fire_time)) = (first_fire, running_job.next_fire_utc) {
            prop_assert!(next_fire_time >= first_fire_time);
        }
    }

    #[test]
    fn exhausted_repeats_clears_fire(minutes in 1u32..60) {
        let mut scheduler_job = make_interval_job(minutes);
        scheduler_job.repeats = Some(1);
        let mut running_job = RunningJob::from_scheduler_job(&scheduler_job);
        running_job.current_run = 1;
        running_job.advance_to_next(Utc::now());
        prop_assert!(running_job.next_fire_utc.is_none());
    }
}
