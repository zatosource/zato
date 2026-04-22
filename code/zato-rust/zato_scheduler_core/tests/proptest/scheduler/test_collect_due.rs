use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::scheduler::{SchedulerState, collect_due_jobs};
use zato_server_core::model::SchedulerJob;

fn make_due_job(id: i64, minutes_ago: u32) -> SchedulerJob {
    let start = (Utc::now() - Duration::minutes(i64::from(minutes_ago) + 60))
        .format("%Y-%m-%dT%H:%M:%S")
        .to_string();
    SchedulerJob {
        id,
        name: format!("job-{id}"),
        is_active: true,
        service: "svc".into(),
        job_type: "interval_based".into(),
        start_date: start,
        extra: None,
        weeks: None,
        days: None,
        hours: None,
        minutes: Some(minutes_ago.max(1)),
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
    fn inactive_jobs_never_collected(minutes in 1u32..60) {
        let mut sj = make_due_job(1, minutes);
        sj.is_active = false;
        let running_job = RunningJob::from_scheduler_job(&sj);
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        let now = Utc::now();
        let batch = collect_due_jobs(&mut state, now, 50);
        prop_assert!(batch.is_empty());
    }

    #[test]
    fn in_flight_jobs_skipped(minutes in 1u32..30) {
        let sj = make_due_job(1, minutes);
        let mut running_job = RunningJob::from_scheduler_job(&sj);
        running_job.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
        running_job.sync_instant_from_utc_pub(Utc::now());
        running_job.in_flight = true;
        running_job.in_flight_since = Some(std::time::Instant::now());
        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        let now = Utc::now();
        let batch = collect_due_jobs(&mut state, now, 50);
        prop_assert!(batch.is_empty());
        let running_job = state.jobs.get(&1).unwrap();
        let last = running_job.history.back().unwrap();
        prop_assert_eq!(&last.outcome, "skipped_already_in_flight");
    }
}
