use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_server_core::model::SchedulerJob;

fn make_job(minutes: u32, is_active: bool) -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1))
        .format("%Y-%m-%dT%H:%M:%S")
        .to_string();
    SchedulerJob {
        id: 1,
        name: "original".into(),
        is_active,
        service: "svc-original".into(),
        job_type: "interval_based".into(),
        start_date: start,
        extra: Some("extra-data".into()),
        weeks: None, days: None, hours: None,
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
    fn edit_updates_non_schedule_fields(minutes in 1u32..60) {
        let sj = make_job(minutes, true);
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        let mut edited = sj.clone();
        edited.name = "edited-name".into();
        edited.service = "svc-edited".into();
        edited.extra = Some("new-extra".into());
        running_job.update_from_job(&edited);
        prop_assert_eq!(&running_job.name, "edited-name");
        prop_assert_eq!(running_job.service.as_ref(), "svc-edited");
        prop_assert_eq!(running_job.extra.as_deref(), Some("new-extra"));
    }

    #[test]
    fn deactivate_clears_fire(minutes in 1u32..60) {
        let sj = make_job(minutes, true);
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        prop_assert!(running_job.next_fire_utc.is_some());
        let mut edited = sj.clone();
        edited.is_active = false;
        running_job.update_from_job(&edited);
        prop_assert!(running_job.next_fire_utc.is_none());
    }

    #[test]
    fn schedule_change_recomputes_fire(
        old_min in 1u32..30,
        new_min in 31u32..60,
    ) {
        let sj = make_job(old_min, true);
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        let mut edited = sj.clone();
        edited.minutes = Some(new_min);
        running_job.update_from_job(&edited);
        prop_assert!(running_job.next_fire_utc.is_some());
        prop_assert_eq!(running_job.interval_ms, new_min as u64 * 60_000);
    }
}
