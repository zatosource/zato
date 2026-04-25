use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;

fn make_interval_job(minutes: u32, future_start: bool, is_active: bool) -> SchedulerJob {
    let start = if future_start {
        (Utc::now() + Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string()
    } else {
        (Utc::now() - Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string()
    };
    SchedulerJob {
        id: 1,
        name: "test".into(),
        is_active,
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

proptest! {

    #[test]
    fn active_interval_job_has_next_fire(minutes in 1u32..120) {
        let job = make_interval_job(minutes, false, true);
        let running_job = RunningJob::from_scheduler_job(&job);
        prop_assert!(running_job.next_fire_utc.is_some());
    }

    #[test]
    fn active_interval_job_next_fire_not_in_past(minutes in 1u32..120) {
        let before = Utc::now();
        let job = make_interval_job(minutes, false, true);
        let running_job = RunningJob::from_scheduler_job(&job);
        if let Some(fire) = running_job.next_fire_utc {
            prop_assert!(fire >= before - Duration::seconds(1));
        }
    }

    #[test]
    fn inactive_job_has_no_next_fire(minutes in 1u32..120) {
        let job = make_interval_job(minutes, false, false);
        let running_job = RunningJob::from_scheduler_job(&job);
        prop_assert!(running_job.next_fire_utc.is_none());
    }

    #[test]
    fn future_start_fires_at_start(minutes in 1u32..120) {
        let job = make_interval_job(minutes, true, true);
        let running_job = RunningJob::from_scheduler_job(&job);
        if let Some(fire) = running_job.next_fire_utc
            && let Some(sd) = running_job.start_date {
            let diff = (fire - sd).num_milliseconds().abs();
            prop_assert!(diff < i64::from(running_job.jitter_ms.unwrap_or(0)) + 1000);
        }
    }
}
