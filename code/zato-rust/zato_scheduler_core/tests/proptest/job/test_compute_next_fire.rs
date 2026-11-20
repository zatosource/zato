use jiff::{SignedDuration, Timestamp};
use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::job::signed_millis;
use zato_scheduler_core::model::SchedulerJob;

fn make_interval_job(minutes: u32, future_start: bool, is_active: bool) -> SchedulerJob {
    let start = if future_start {
        (Timestamp::now() + SignedDuration::from_hours(1))
            .strftime("%Y-%m-%dT%H:%M:%S")
            .to_string()
    } else {
        (Timestamp::now() - SignedDuration::from_hours(1))
            .strftime("%Y-%m-%dT%H:%M:%S")
            .to_string()
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
        max_execution_time_ms: None,
        on_success_service: None,
        on_success_job: None,
        on_error_service: None,
        on_error_job: None,
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
        let before = Timestamp::now();
        let job = make_interval_job(minutes, false, true);
        let running_job = RunningJob::from_scheduler_job(&job);
        if let Some(fire) = running_job.next_fire_utc {
            prop_assert!(fire >= before - SignedDuration::from_secs(1));
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
            && let Some(start) = running_job.start_date {
            let diff = signed_millis(fire, start).abs();
            prop_assert!(diff < i64::from(running_job.jitter_ms.unwrap_or(0)) + 1000);
        }
    }
}
