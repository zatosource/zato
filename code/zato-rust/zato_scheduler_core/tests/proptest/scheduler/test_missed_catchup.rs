use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::scheduler::{SchedulerState, apply_missed_catchup};
use zato_scheduler_core::model::SchedulerJob;

fn make_interval_job(on_missed: &str, past_hours: u32) -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(i64::from(past_hours) + 2))
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
        weeks: None,
        days: None,
        hours: None,
        minutes: Some(5),
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        on_missed: Some(on_missed.into()),
        max_execution_time_ms: None,
    }
}

proptest! {

    #[test]
    fn skip_policy_recomputes_to_future(past_hours in 1u32..24) {
        let sj = make_interval_job("skip", past_hours);
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        running_job.next_fire_utc = Some(Utc::now() - Duration::hours(1));
        running_job.sync_instant_from_utc_pub(Utc::now());
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        let now = Utc::now();
        apply_missed_catchup(&mut state, now);
        let running_job = state.jobs.get(&1).unwrap();
        if let Some(fire) = running_job.next_fire_utc {
            prop_assert!(fire >= now - Duration::seconds(1));
        }
    }

    #[test]
    fn one_time_jobs_ignored(_n in 0u32..50) {
        let start = (Utc::now() - Duration::hours(1))
            .format("%Y-%m-%dT%H:%M:%S")
            .to_string();
        let sj = SchedulerJob {
            id: 1,
            name: "test".into(),
            is_active: true,
            service: "svc".into(),
            job_type: "one_time".into(),
            start_date: start,
            extra: None,
            weeks: None, days: None, hours: None, minutes: None, seconds: None,
            repeats: None, jitter_ms: None, timezone: None, calendar: None,
            on_missed: Some("skip".into()),
            max_execution_time_ms: None,
        };
        let running_job = RunningJob::from_scheduler_job(&sj);
        let fire_before = running_job.next_fire_utc;
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        apply_missed_catchup(&mut state, Utc::now());
        let running_job = state.jobs.get(&1).unwrap();
        prop_assert_eq!(running_job.next_fire_utc, fire_before);
    }

    #[test]
    fn inactive_jobs_ignored(_n in 0u32..50) {
        let mut sj = make_interval_job("skip", 1);
        sj.is_active = false;
        let running_job = RunningJob::from_scheduler_job(&sj);
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        apply_missed_catchup(&mut state, Utc::now());
        let running_job = state.jobs.get(&1).unwrap();
        prop_assert!(running_job.next_fire_utc.is_none());
    }
}
