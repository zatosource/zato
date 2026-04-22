use proptest::prelude::*;
use chrono::{Duration, Utc};
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::scheduler::SchedulerState;
use zato_server_core::model::SchedulerJob;

fn make_job(id: i64) -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1))
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

proptest! {

    #[test]
    fn delete_subset_leaves_remainder(
        n_total in 2usize..8,
        n_delete in 1usize..4,
    ) {
        let n_delete = n_delete.min(n_total - 1);
        let mut state = SchedulerState::new();
        let ids: Vec<i64> = (0..n_total).map(|i| i as i64).collect();
        for &id in &ids {
            let sj = make_job(id);
            let running_job = RunningJob::from_scheduler_job(&sj);
            state.jobs.insert(id, running_job);
        }
        for &id in &ids[..n_delete] {
            state.jobs.remove(&id);
        }
        prop_assert_eq!(state.jobs.len(), n_total - n_delete);
        for &id in &ids[n_delete..] {
            prop_assert!(state.jobs.contains_key(&id));
        }
    }

    #[test]
    fn delete_nonexistent_is_noop(
        n in 1usize..5,
    ) {
        let mut state = SchedulerState::new();
        for i in 0..n {
            let id = i as i64;
            let sj = make_job(id);
            let running_job = RunningJob::from_scheduler_job(&sj);
            state.jobs.insert(id, running_job);
        }
        state.jobs.remove(&999);
        prop_assert_eq!(state.jobs.len(), n);
    }
}
