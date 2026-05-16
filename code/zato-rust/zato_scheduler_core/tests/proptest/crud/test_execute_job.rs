use chrono::{Duration, Utc};
use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;
use zato_scheduler_core::redis_streams::handle_execute_job;
use zato_scheduler_core::scheduler::SchedulerShared;
use zato_scheduler_core::types::FireBatch;

fn make_job(is_active: bool) -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string();
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
        minutes: Some(30),
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        max_execution_time_ms: None,
        on_success_service: None,
        on_success_job: None,
        on_error_service: None,
        on_error_job: None,
    }
}

fn setup_shared(is_active: bool) -> (std::sync::Arc<SchedulerShared>, std::sync::mpsc::Receiver<FireBatch>) {
    let shared = std::sync::Arc::new(SchedulerShared::new());
    let (sender, receiver) = std::sync::mpsc::channel::<FireBatch>();
    *shared.fire_sender.lock() = Some(sender);

    let scheduler_job = make_job(is_active);
    let running_job = RunningJob::from_scheduler_job(&scheduler_job);
    shared.state.lock().jobs.insert(1, running_job);

    (shared, receiver)
}

proptest! {

    #[test]
    fn execute_active_job_sends_fire_batch(_n in 0u32..10) {
        let (shared, receiver) = setup_shared(true);
        let original_fire = shared.state.lock().jobs[&1].next_fire_utc;

        handle_execute_job(&shared, r#"{"job_id": 1}"#);

        let batch = receiver.try_recv().unwrap();
        prop_assert_eq!(batch.job_id.0, 1);
        prop_assert_eq!(batch.service.0, "svc");

        let state = shared.state.lock();
        let job = &state.jobs[&1];
        prop_assert_eq!(job.next_fire_utc, original_fire);
        prop_assert!(job.in_flight);
        prop_assert_eq!(job.current_run, 1);
    }

    #[test]
    fn execute_inactive_job_sends_fire_batch(_n in 0u32..10) {
        let (shared, receiver) = setup_shared(false);

        handle_execute_job(&shared, r#"{"job_id": 1}"#);

        let batch = receiver.try_recv().unwrap();
        prop_assert_eq!(batch.job_id.0, 1);

        let state = shared.state.lock();
        let job = &state.jobs[&1];
        prop_assert!(job.next_fire_utc.is_none());
        prop_assert!(job.in_flight);
        prop_assert_eq!(job.current_run, 1);
    }

    #[test]
    fn execute_preserves_next_fire_utc(_n in 0u32..10) {
        let (shared, _receiver) = setup_shared(true);
        let original_fire = shared.state.lock().jobs[&1].next_fire_utc;

        handle_execute_job(&shared, r#"{"job_id": 1}"#);

        let after_fire = shared.state.lock().jobs[&1].next_fire_utc;
        prop_assert_eq!(original_fire, after_fire);
    }

    #[test]
    fn execute_nonexistent_job_is_noop(_n in 0u32..10) {
        let (shared, receiver) = setup_shared(true);

        handle_execute_job(&shared, r#"{"job_id": 999}"#);

        prop_assert!(receiver.try_recv().is_err());
    }

    #[test]
    fn execute_records_history(_n in 0u32..10) {
        let (shared, _receiver) = setup_shared(true);

        handle_execute_job(&shared, r#"{"job_id": 1}"#);

        let state = shared.state.lock();
        let job = &state.jobs[&1];
        prop_assert_eq!(job.history.len(), 1);
        let rec = &job.history[0];
        prop_assert_eq!(&rec.outcome, "running");
        prop_assert_eq!(rec.current_run, 1);
        prop_assert_eq!(rec.log_entries.len(), 1);
        prop_assert!(rec.log_entries[0].message.contains("forced execute"));
    }
}
