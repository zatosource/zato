use chrono::Utc;

use zato_scheduler_core::job::{RunningJob, DEFAULT_MAX_EXECUTION_TIME_MS, DEFAULT_MAX_HISTORY};
use zato_scheduler_core::model::SchedulerJob;

fn make_interval_job(id: i64, name: &str, minutes: u32) -> SchedulerJob {
    SchedulerJob {
        id,
        name: name.into(),
        is_active: true,
        service: "demo.ping".into(),
        job_type: "interval_based".into(),
        start_date: "2026-01-01T00:00:00".into(),
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
        max_execution_time_ms: None,
    }
}

fn make_one_time_job(id: i64, name: &str, start_date: &str) -> SchedulerJob {
    SchedulerJob {
        id,
        name: name.into(),
        is_active: true,
        service: "demo.ping".into(),
        job_type: "one_time".into(),
        start_date: start_date.into(),
        extra: None,
        weeks: None,
        days: None,
        hours: None,
        minutes: None,
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        max_execution_time_ms: None,
    }
}

// ################################################################
// Interval computation
// ################################################################

#[test]
fn test_interval_minutes_only() {
    let job = make_interval_job(1, "j1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj.interval_ms, 10 * 60_000);
}

#[test]
fn test_interval_all_components() {
    let mut job = make_interval_job(2, "j2", 4);
    job.weeks = Some(1);
    job.days = Some(2);
    job.hours = Some(3);
    job.seconds = Some(5);

    let rj = RunningJob::from_scheduler_job(&job);
    let expected = 1u64 * 7 * 86_400_000
        + 2 * 86_400_000
        + 3 * 3_600_000
        + 4 * 60_000
        + 5 * 1_000;
    assert_eq!(rj.interval_ms, expected);
}

#[test]
fn test_interval_zero_when_no_components() {
    let mut job = make_interval_job(3, "j3", 0);
    job.minutes = Some(0);
    let rj = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj.interval_ms, 0);
}

// ################################################################
// Start date parsing
// ################################################################

#[test]
fn test_parse_iso_datetime() {
    let job = make_interval_job(10, "p1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.start_date.is_some());
}

#[test]
fn test_parse_datetime_with_fraction() {
    let mut job = make_interval_job(11, "p2", 10);
    job.start_date = "2026-04-10T12:30:45.123456".into();
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.start_date.is_some());
}

#[test]
fn test_parse_datetime_with_z_suffix() {
    let mut job = make_interval_job(12, "p3", 10);
    job.start_date = "2026-04-10T12:30:45Z".into();
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.start_date.is_some());
}

#[test]
fn test_parse_datetime_with_offset() {
    let mut job = make_interval_job(13, "p4", 10);
    job.start_date = "2026-04-10T12:30:45+02:00".into();
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.start_date.is_some());
}

#[test]
fn test_parse_datetime_space_separator() {
    let mut job = make_interval_job(14, "p5", 10);
    job.start_date = "2026-04-10 12:30:45".into();
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.start_date.is_some());
}

#[test]
fn test_parse_empty_start_date_falls_back_to_now() {
    let mut job = make_interval_job(15, "p6", 10);
    job.start_date = String::new();
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.start_date.is_some());
    assert!(rj.next_fire_utc.is_some());
}

// ################################################################
// Timezone handling
// ################################################################

#[test]
fn test_timezone_parsed() {
    let mut job = make_interval_job(20, "tz1", 10);
    job.timezone = Some("America/New_York".into());
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.timezone.is_some());
    assert_eq!(rj.timezone_str.as_deref(), Some("America/New_York"));
}

#[test]
fn test_invalid_timezone_ignored() {
    let mut job = make_interval_job(21, "tz2", 10);
    job.timezone = Some("Invalid/Zone".into());
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.timezone.is_none());
}

#[test]
fn test_no_timezone() {
    let job = make_interval_job(22, "tz3", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.timezone.is_none());
}

// ################################################################
// One-time jobs
// ################################################################

#[test]
fn test_one_time_future_date() {
    let job = make_one_time_job(30, "ot1", "2099-12-31T23:59:59");
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.next_fire_utc.is_some());
    assert!(rj.next_fire_utc.unwrap() > Utc::now());
}

#[test]
fn test_one_time_past_date_fires_immediately() {
    let job = make_one_time_job(31, "ot2", "2020-01-01T00:00:00");
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.next_fire_utc.is_some());
}

#[test]
fn test_one_time_advance_clears_fire() {
    let job = make_one_time_job(32, "ot3", "2099-12-31T23:59:59");
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.advance_to_next(Utc::now());
    assert!(rj.next_fire_utc.is_none());
}

// ################################################################
// Interval next-fire computation
// ################################################################

#[test]
fn test_interval_next_fire_in_future() {
    let job = make_interval_job(40, "nf1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.next_fire_utc.is_some());
}

#[test]
fn test_interval_advance_produces_new_fire() {
    let job = make_interval_job(41, "nf2", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);
    let past = Utc::now() - chrono::Duration::minutes(5);
    rj.next_fire_utc = Some(past);
    rj.advance_to_next(Utc::now());
    assert!(rj.next_fire_utc.is_some());
    assert!(rj.next_fire_utc.unwrap() > past);
}

// ################################################################
// Repeats
// ################################################################

#[test]
fn test_repeats_exhausted_clears_fire() {
    let mut job = make_interval_job(50, "rep1", 10);
    job.repeats = Some(2);
    let mut rj = RunningJob::from_scheduler_job(&job);

    rj.current_run = 2;
    rj.advance_to_next(Utc::now());
    assert!(rj.next_fire_utc.is_none());
}

#[test]
fn test_repeats_not_exhausted_keeps_fire() {
    let mut job = make_interval_job(51, "rep2", 10);
    job.repeats = Some(5);
    let mut rj = RunningJob::from_scheduler_job(&job);

    rj.current_run = 3;
    rj.advance_to_next(Utc::now());
    assert!(rj.next_fire_utc.is_some());
}

#[test]
fn test_no_repeats_limit() {
    let job = make_interval_job(52, "rep3", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);

    rj.current_run = 1000;
    rj.advance_to_next(Utc::now());
    assert!(rj.next_fire_utc.is_some());
}

// ################################################################
// Jitter
// ################################################################

#[test]
fn test_jitter_applied() {
    let mut job = make_interval_job(60, "jit1", 10);
    job.jitter_ms = Some(5000);
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.jitter_ms == Some(5000));
}

#[test]
fn test_jitter_deterministic_for_same_id() {
    let mut job1 = make_interval_job(61, "jit-same", 10);
    job1.jitter_ms = Some(5000);
    let rj1 = RunningJob::from_scheduler_job(&job1);

    let mut job2 = make_interval_job(61, "jit-same", 10);
    job2.jitter_ms = Some(5000);
    let rj2 = RunningJob::from_scheduler_job(&job2);

    assert_eq!(rj1.next_fire_utc, rj2.next_fire_utc);
}

// ################################################################
// Defaults
// ################################################################

#[test]
fn test_default_max_execution_time() {
    let job = make_interval_job(70, "def2", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj.max_execution_time_ms, DEFAULT_MAX_EXECUTION_TIME_MS);
}

#[test]
fn test_default_history_capacity() {
    let job = make_interval_job(71, "def3", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj.max_history, DEFAULT_MAX_HISTORY);
}

#[test]
fn test_custom_max_execution_time() {
    let mut job = make_interval_job(72, "def5", 10);
    job.max_execution_time_ms = Some(120_000);
    let rj = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj.max_execution_time_ms, 120_000);
}

// ################################################################
// update_from_job
// ################################################################

#[test]
fn test_update_renames_job() {
    let job = make_interval_job(80, "upd1", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);

    let mut updated = make_interval_job(80, "upd1-renamed", 10);
    updated.id = job.id;
    rj.update_from_job(&updated);

    assert_eq!(rj.name, "upd1-renamed");
}

#[test]
fn test_update_changes_interval() {
    let job = make_interval_job(81, "upd2", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj.interval_ms, 10 * 60_000);

    let mut updated = make_interval_job(81, "upd2", 7);
    updated.id = job.id;
    rj.update_from_job(&updated);

    assert_eq!(rj.interval_ms, 7 * 60_000);
    assert!(rj.next_fire_utc.is_some());
}

#[test]
fn test_update_deactivates_job() {
    let job = make_interval_job(82, "upd3", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.next_fire_utc.is_some());

    let mut updated = make_interval_job(82, "upd3", 10);
    updated.id = job.id;
    updated.is_active = false;
    rj.update_from_job(&updated);

    assert!(!rj.is_active);
    assert!(rj.next_fire_utc.is_none());
}

#[test]
fn test_update_preserves_history() {
    let job = make_interval_job(83, "upd4", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);

    rj.record_execution(zato_scheduler_core::job::ExecutionRecord {
        planned_fire_time_iso: "2026-01-01T00:00:00+00:00".into(),
        actual_fire_time_iso: "2026-01-01T00:00:00+00:00".into(),
        delay_ms: 0,
        outcome: "executed".into(),
        current_run: 1,
        duration_ms: Some(100),
        error: None,
        outcome_ctx: None,
        log_entries: vec![],
    });

    let mut updated = make_interval_job(83, "upd4-renamed", 20);
    updated.id = job.id;
    rj.update_from_job(&updated);

    assert_eq!(rj.history.len(), 1);
    assert_eq!(rj.name, "upd4-renamed");
}

// ################################################################
// Execution history
// ################################################################

#[test]
fn test_record_execution() {
    let job = make_interval_job(90, "hist1", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);

    rj.record_execution(zato_scheduler_core::job::ExecutionRecord {
        planned_fire_time_iso: "2026-01-01T00:00:00+00:00".into(),
        actual_fire_time_iso: "2026-01-01T00:00:01+00:00".into(),
        delay_ms: 1000,
        outcome: "executed".into(),
        current_run: 1,
        duration_ms: Some(50),
        error: None,
        outcome_ctx: None,
        log_entries: vec![],
    });

    assert_eq!(rj.history.len(), 1);
    assert_eq!(rj.history[0].outcome, "executed");
    assert_eq!(rj.history[0].delay_ms, 1000);
}

#[test]
fn test_history_capped_at_max() {
    let job = make_interval_job(91, "hist2", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);

    for i in 0..DEFAULT_MAX_HISTORY + 50 {
        rj.record_execution(zato_scheduler_core::job::ExecutionRecord {
            planned_fire_time_iso: format!("2026-01-01T00:{:02}:00+00:00", i % 60),
            actual_fire_time_iso: format!("2026-01-01T00:{:02}:00+00:00", i % 60),
            delay_ms: 0,
            outcome: "executed".into(),
            current_run: i as u32,
            duration_ms: None,
            error: None,
            outcome_ctx: None,
            log_entries: vec![],
        });
    }

    assert_eq!(rj.history.len(), DEFAULT_MAX_HISTORY);
}

// ################################################################
// In-flight state
// ################################################################

#[test]
fn test_initial_not_in_flight() {
    let job = make_interval_job(100, "inf1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(!rj.in_flight);
    assert!(rj.in_flight_since.is_none());
}

#[test]
fn test_inactive_job_no_next_fire() {
    let mut job = make_interval_job(101, "ia1", 10);
    job.is_active = false;
    let rj = RunningJob::from_scheduler_job(&job);
    assert!(rj.next_fire_utc.is_none());
}

// ################################################################
// Name hash stability
// ################################################################

#[test]
fn test_name_hash_stable() {
    let job = make_interval_job(110, "hash-test", 10);
    let rj1 = RunningJob::from_scheduler_job(&job);
    let rj2 = RunningJob::from_scheduler_job(&job);
    assert_eq!(rj1.next_fire_utc, rj2.next_fire_utc);
}

#[test]
fn test_different_names_different_jitter() {
    let mut job1 = make_interval_job(111, "hash-a", 10);
    job1.jitter_ms = Some(10000);
    let rj1 = RunningJob::from_scheduler_job(&job1);

    let mut job2 = make_interval_job(112, "hash-b", 10);
    job2.jitter_ms = Some(10000);
    let rj2 = RunningJob::from_scheduler_job(&job2);

    assert!(rj1.next_fire_utc.is_some());
    assert!(rj2.next_fire_utc.is_some());
}
