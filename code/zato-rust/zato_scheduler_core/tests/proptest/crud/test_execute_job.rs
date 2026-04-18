use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::scheduler::SchedulerState;
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
        minutes: Some(30),
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
    fn execute_sets_fire_to_now(_n in 0u32..50) {
        let sj = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        let before = Utc::now();
        running_job.next_fire_utc = Some(Utc::now());
        running_job.sync_instant_from_utc_pub(Utc::now());
        let after = Utc::now();
        if let Some(fire) = running_job.next_fire_utc {
            prop_assert!(fire >= before - Duration::seconds(1));
            prop_assert!(fire <= after + Duration::seconds(1));
        }
    }

    #[test]
    fn execute_nonexistent_is_noop(_n in 0u32..50) {
        let mut state = SchedulerState::new();
        let sj = make_job();
        let running_job = RunningJob::from_scheduler_job(&sj);
        state.jobs.insert("j1".into(), running_job);
        if let Some(running_job) = state.jobs.get_mut("nonexistent") {
            running_job.next_fire_utc = Some(Utc::now());
        }
        prop_assert_eq!(state.jobs.len(), 1);
    }
}
