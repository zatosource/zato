use chrono::{Duration, Utc};
use proptest::prelude::*;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;

fn make_job() -> SchedulerJob {
    let start = (Utc::now() - Duration::hours(1)).format("%Y-%m-%dT%H:%M:%S").to_string();
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
        max_execution_time_ms: None,
        on_success_service: None,
        on_success_job: None,
        on_error_service: None,
        on_error_job: None,
    }
}

proptest! {

    #[test]
    fn completion_removes_only_its_run(
        runs in proptest::collection::btree_set(1u32..1_000, 1..8),
        completed in 1u32..1_000,
    ) {
        let scheduler_job = make_job();
        let mut running_job = RunningJob::from_scheduler_job(&scheduler_job);
        let since = std::time::Instant::now();

        for &run in &runs {
            running_job.start_run(run, since);
        }

        running_job.complete_run(completed);

        let mut expected = runs;
        expected.remove(&completed);
        let remaining: std::collections::BTreeSet<u32> = running_job.in_flight_runs.keys().copied().collect();

        prop_assert_eq!(&remaining, &expected);
        prop_assert_eq!(running_job.is_in_flight(), !expected.is_empty());
    }
}
