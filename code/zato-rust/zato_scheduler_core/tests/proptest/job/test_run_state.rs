use chrono::{DateTime, Duration, Utc};
use proptest::prelude::*;
use zato_scheduler_core::DeferredLog;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::{ReloadedJob, SchedulerJob};
use zato_scheduler_core::scheduler::{SchedulerState, collect_due_jobs};
use zato_scheduler_core::wire::parse_payload;

/// Hours between the start date of a past job and the current time.
const HOURS_SINCE_START: i64 = 2;

/// Coalesce window used when collecting due jobs.
const COALESCE_WINDOW_MS: i64 = 50;

fn make_job(job_type: &str, start: DateTime<Utc>, minutes: Option<u32>, jitter_ms: Option<u32>) -> SchedulerJob {
    SchedulerJob {
        id: 1,
        name: "test".into(),
        is_active: true,
        service: "svc".into(),
        job_type: job_type.into(),
        start_date: start.format("%Y-%m-%dT%H:%M:%S").to_string(),
        extra: None,
        weeks: None,
        days: None,
        hours: None,
        minutes,
        seconds: None,
        repeats: None,
        jitter_ms,
        timezone: None,
        max_execution_time_ms: None,
        on_success_service: None,
        on_success_job: None,
        on_error_service: None,
        on_error_job: None,
    }
}

fn past_start() -> DateTime<Utc> {
    Utc::now() - Duration::hours(HOURS_SINCE_START)
}

fn interval_of(minutes: u32) -> Duration {
    Duration::minutes(i64::from(minutes))
}

#[test]
fn reloaded_job_is_parsed_with_its_run_state() {
    let payload = r#"{"id": 7, "name": "job-7", "is_active": true, "service": "svc", "job_type": "interval_based",
        "start_date": "2026-01-01T00:00:00", "extra": null, "minutes": "5", "repeats": "",
        "current_run": 12, "last_slot_iso": "2026-01-01T01:00:00+00:00"}"#;
    let parsed: Result<ReloadedJob, _> = parse_payload(payload);
    let Ok(reloaded) = parsed else {
        panic!("the reload entry is parsed");
    };
    assert_eq!(reloaded.job.id, 7);
    assert_eq!(reloaded.job.minutes, Some(5));
    assert_eq!(reloaded.job.repeats, None);
    assert_eq!(reloaded.current_run, 12);
    assert_eq!(reloaded.last_slot_iso.as_deref(), Some("2026-01-01T01:00:00+00:00"));
}

#[test]
fn reloaded_job_without_run_state_starts_from_zero() {
    let payload = r#"{"id": 7, "name": "job-7", "is_active": true, "service": "svc", "job_type": "one_time",
        "start_date": "2026-01-01T00:00:00", "extra": null, "last_slot_iso": null}"#;
    let parsed: Result<ReloadedJob, _> = parse_payload(payload);
    let Ok(reloaded) = parsed else {
        panic!("the reload entry is parsed");
    };
    assert_eq!(reloaded.current_run, 0);
    assert_eq!(reloaded.last_slot_iso, None);
}

proptest! {

    #[test]
    fn nominal_slot_is_on_the_grid_and_precedes_jitter(minutes in 1u32..60, jitter_ms in 1u32..10_000) {
        let job = make_job("interval_based", past_start(), Some(minutes), Some(jitter_ms));
        let running_job = RunningJob::from_scheduler_job(&job);

        let (Some(nominal), Some(fire), Some(start)) = (running_job.next_nominal_utc, running_job.next_fire_utc, running_job.start_date) else {
            return Err(TestCaseError::fail("an active interval job has a start date and a next fire"));
        };

        let interval_ms = interval_of(minutes).num_milliseconds();
        let offset_ms = (nominal - start).num_milliseconds();
        prop_assert_eq!(offset_ms % interval_ms, 0);

        let jitter_applied_ms = (fire - nominal).num_milliseconds();
        prop_assert!(jitter_applied_ms >= 0);
        prop_assert!(jitter_applied_ms < i64::from(jitter_ms));
    }

    #[test]
    fn fire_event_carries_the_nominal_slot(minutes in 1u32..60) {
        let job = make_job("interval_based", past_start(), Some(minutes), None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let latest_due = running_job.latest_due_slot(Utc::now());
        running_job.restore_run_state(0, latest_due.map(|slot| slot - interval_of(minutes)), Utc::now());

        let mut state = SchedulerState::new();
        state.jobs.insert(1, running_job);
        let mut deferred = DeferredLog::new();
        let batch = collect_due_jobs(&mut state, Utc::now(), COALESCE_WINDOW_MS, &mut deferred);

        prop_assert_eq!(batch.len(), 1);
        let Some(item) = batch.first() else {
            return Err(TestCaseError::fail("one fire event is due"));
        };
        let expected = latest_due.map(|slot| slot.to_rfc3339());
        prop_assert_eq!(Some(item.nominal_fire_time_iso.clone()), expected);
    }

    #[test]
    fn run_counter_is_restored(current_run in 0u32..10_000, minutes in 1u32..60) {
        let job = make_job("interval_based", past_start(), Some(minutes), None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        running_job.restore_run_state(current_run, None, Utc::now());
        prop_assert_eq!(running_job.current_run, current_run);
    }

    #[test]
    fn used_up_repeats_do_not_fire(repeats in 1u32..100, extra_runs in 0u32..10, minutes in 1u32..60) {
        let mut job = make_job("interval_based", past_start(), Some(minutes), None);
        job.repeats = Some(repeats);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        running_job.restore_run_state(repeats + extra_runs, None, Utc::now());
        prop_assert!(running_job.next_fire_utc.is_none());
        prop_assert!(running_job.next_nominal_utc.is_none());
    }

    #[test]
    fn remaining_repeats_still_fire(repeats in 2u32..100, minutes in 1u32..60) {
        let mut job = make_job("interval_based", past_start(), Some(minutes), None);
        job.repeats = Some(repeats);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        running_job.restore_run_state(repeats - 1, None, Utc::now());
        prop_assert!(running_job.next_fire_utc.is_some());
    }

    #[test]
    fn one_time_job_that_ran_does_not_fire(current_run in 1u32..100, minutes_ago in 1i64..10_000) {
        let start = Utc::now() - Duration::minutes(minutes_ago);
        let job = make_job("one_time", start, None, None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        running_job.restore_run_state(current_run, Some(start), Utc::now());
        prop_assert!(running_job.next_fire_utc.is_none());
    }

    #[test]
    fn one_time_job_whose_start_was_missed_fires_once(minutes_ago in 1i64..10_000) {
        let start = Utc::now() - Duration::minutes(minutes_ago);
        let job = make_job("one_time", start, None, None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let now = Utc::now();
        running_job.restore_run_state(0, None, now);

        prop_assert_eq!(running_job.next_fire_utc, Some(now));
        prop_assert_eq!(running_job.next_nominal_utc, running_job.start_date);

        running_job.advance_to_next(now);
        prop_assert!(running_job.next_fire_utc.is_none());
    }

    #[test]
    fn missed_slots_fire_once_for_the_latest(minutes in 1u32..60, missed in 1i32..20) {
        let job = make_job("interval_based", past_start(), Some(minutes), None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let now = Utc::now();
        let Some(latest_due) = running_job.latest_due_slot(now) else {
            return Err(TestCaseError::fail("a job started in the past has a due slot"));
        };
        let last_slot = latest_due - interval_of(minutes) * missed;

        running_job.restore_run_state(0, Some(last_slot), now);
        prop_assert_eq!(running_job.next_fire_utc, Some(now));
        prop_assert_eq!(running_job.next_nominal_utc, Some(latest_due));

        // After the catch-up run, the job returns to its regular slot after the current time
        running_job.advance_to_next(now);
        prop_assert_eq!(running_job.next_nominal_utc, Some(latest_due + interval_of(minutes)));
    }

    #[test]
    fn no_missed_slot_keeps_the_regular_schedule(minutes in 1u32..60) {
        let job = make_job("interval_based", past_start(), Some(minutes), None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let now = Utc::now();
        let Some(latest_due) = running_job.latest_due_slot(now) else {
            return Err(TestCaseError::fail("a job started in the past has a due slot"));
        };

        running_job.restore_run_state(0, Some(latest_due), now);
        prop_assert_eq!(running_job.next_nominal_utc, Some(latest_due + interval_of(minutes)));
    }

    #[test]
    fn job_that_never_ran_has_no_catch_up(minutes in 1u32..60) {
        let job = make_job("interval_based", past_start(), Some(minutes), None);
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let now = Utc::now();
        running_job.restore_run_state(0, None, now);

        let Some(fire) = running_job.next_fire_utc else {
            return Err(TestCaseError::fail("an active interval job has a next fire"));
        };
        prop_assert!(fire > now);
    }

    #[test]
    fn inactive_job_does_not_fire_after_restore(minutes in 1u32..60, missed in 1i32..20) {
        let mut job = make_job("interval_based", past_start(), Some(minutes), None);
        job.is_active = false;
        let mut running_job = RunningJob::from_scheduler_job(&job);
        let last_slot = past_start() + interval_of(minutes) * missed;
        running_job.restore_run_state(0, Some(last_slot), Utc::now());
        prop_assert!(running_job.next_fire_utc.is_none());
    }
}
