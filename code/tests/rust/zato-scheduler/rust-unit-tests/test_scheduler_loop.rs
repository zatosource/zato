use std::time::Instant;

use chrono::{Duration, Utc};

use zato_scheduler_core::calendar::CalendarData;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;
use zato_scheduler_core::scheduler::{
    check_in_flight_timeouts, collect_due_jobs, compute_sleep_duration,
    reanchor_all_jobs, SchedulerState,
};
use zato_scheduler_core::DeferredLog;

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

// ################################################################
// compute_sleep_duration
// ################################################################

#[test]
fn test_sleep_duration_no_jobs() {
    let state = SchedulerState::new();
    let dur = compute_sleep_duration(&state);
    assert_eq!(dur.as_millis(), 60_000);
}

#[test]
fn test_sleep_duration_with_future_job() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(1, "sd1", 5);
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(1, rj);

    let dur = compute_sleep_duration(&state);
    assert!(dur.as_millis() > 0);
    assert!(dur.as_millis() <= 5 * 60_000);
}

#[test]
fn test_sleep_duration_inactive_job_ignored() {
    let mut state = SchedulerState::new();
    let mut job = make_interval_job(2, "sd2", 1);
    job.is_active = false;
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(2, rj);

    let dur = compute_sleep_duration(&state);
    assert_eq!(dur.as_millis(), 60_000);
}

#[test]
fn test_sleep_duration_past_fire_returns_1ms() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(3, "sd3", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(10));
    state.jobs.insert(3, rj);

    let dur = compute_sleep_duration(&state);
    assert_eq!(dur.as_millis(), 1);
}

#[test]
fn test_sleep_duration_picks_soonest() {
    let mut state = SchedulerState::new();

    let job1 = make_interval_job(4, "sd4a", 30);
    let mut rj1 = RunningJob::from_scheduler_job(&job1);
    rj1.next_fire_utc = Some(Utc::now() + Duration::minutes(30));
    state.jobs.insert(4, rj1);

    let job2 = make_interval_job(5, "sd4b", 2);
    let mut rj2 = RunningJob::from_scheduler_job(&job2);
    rj2.next_fire_utc = Some(Utc::now() + Duration::seconds(5));
    state.jobs.insert(5, rj2);

    let dur = compute_sleep_duration(&state);
    assert!(dur.as_millis() <= 6_000);
}

// ################################################################
// collect_due_jobs
// ################################################################

#[test]
fn test_collect_due_no_jobs() {
    let mut state = SchedulerState::new();
    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);
    assert!(batch.is_empty());
}

#[test]
fn test_collect_due_fires_past_job() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(10, "cd1", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
    state.jobs.insert(10, rj);

    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);
    assert_eq!(batch.len(), 1);
    assert_eq!(batch[0].job_id.0, 10);
}

#[test]
fn test_collect_due_skips_future_job() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(11, "cd2", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() + Duration::hours(1));
    state.jobs.insert(11, rj);

    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);
    assert!(batch.is_empty());
}

#[test]
fn test_collect_due_skips_inactive() {
    let mut state = SchedulerState::new();
    let mut job = make_interval_job(12, "cd3", 5);
    job.is_active = false;
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.is_active = false;
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
    state.jobs.insert(12, rj);

    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);
    assert!(batch.is_empty());
}

#[test]
fn test_collect_due_skips_in_flight() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(13, "cd4", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
    rj.in_flight = true;
    rj.in_flight_since = Some(Instant::now());
    state.jobs.insert(13, rj);

    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);
    assert!(batch.is_empty());

    let rj = state.jobs.get(&13).unwrap();
    assert!(rj.in_flight);
}

#[test]
fn test_collect_due_marks_in_flight() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(14, "cd5", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
    state.jobs.insert(14, rj);

    let mut deferred = DeferredLog::default();
    let _batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);

    let rj = state.jobs.get(&14).unwrap();
    assert!(rj.in_flight);
    assert!(rj.in_flight_since.is_some());
    assert_eq!(rj.current_run, 1);
}

#[test]
fn test_collect_due_records_executed_history() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(15, "cd6", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
    state.jobs.insert(15, rj);

    let mut deferred = DeferredLog::default();
    let _batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);

    let rj = state.jobs.get(&15).unwrap();
    let last = rj.history.back().unwrap();
    assert_eq!(last.outcome, "running");
}

#[test]
fn test_collect_due_advances_next_fire() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(16, "cd7", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    let old_fire = Utc::now() - Duration::seconds(1);
    rj.next_fire_utc = Some(old_fire);
    state.jobs.insert(16, rj);

    let mut deferred = DeferredLog::default();
    let _batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);

    let rj = state.jobs.get(&16).unwrap();
    assert!(rj.next_fire_utc.is_some());
    assert!(rj.next_fire_utc.unwrap() > old_fire);
}

#[test]
fn test_collect_due_skips_holiday() {
    let mut state = SchedulerState::new();

    let today = Utc::now().date_naive();
    let mut cal = CalendarData::new("test-cal".into());
    cal.dates.insert(today);
    state.calendars.insert("test-cal".into(), cal);

    let mut job = make_interval_job(17, "cd8", 5);
    job.calendar = Some("test-cal".into());
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::seconds(1));
    state.jobs.insert(17, rj);

    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, Utc::now(), 0, &mut deferred);
    assert!(batch.is_empty());

    let rj = state.jobs.get(&17).unwrap();
    let last = rj.history.back().unwrap();
    assert_eq!(last.outcome, "skipped_holiday");
}

#[test]
fn test_collect_due_multiple_jobs() {
    let mut state = SchedulerState::new();
    let now = Utc::now();

    for idx in 0..3 {
        let id = 100 + idx as i64;
        let name = format!("cd9-{}", idx);
        let job = make_interval_job(id, &name, 5);
        let mut rj = RunningJob::from_scheduler_job(&job);
        rj.next_fire_utc = Some(now - Duration::seconds(1));
        state.jobs.insert(id, rj);
    }

    let mut deferred = DeferredLog::default();
    let batch = collect_due_jobs(&mut state, now, 0, &mut deferred);
    assert_eq!(batch.len(), 3);
}

// ################################################################
// check_in_flight_timeouts
// ################################################################

#[test]
fn test_timeout_not_triggered_within_limit() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(20, "to1", 5);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.in_flight = true;
    rj.in_flight_since = Some(Instant::now());
    state.jobs.insert(20, rj);

    let mut deferred = DeferredLog::default();
    check_in_flight_timeouts(&mut state, &mut deferred);

    let rj = state.jobs.get(&20).unwrap();
    assert!(rj.in_flight);
}

#[test]
fn test_timeout_triggered_past_limit() {
    let mut state = SchedulerState::new();
    let mut job = make_interval_job(21, "to2", 5);
    job.max_execution_time_ms = Some(1_000);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.in_flight = true;
    rj.in_flight_since = Some(Instant::now() - std::time::Duration::from_millis(2_000));
    state.jobs.insert(21, rj);

    let mut deferred = DeferredLog::default();
    check_in_flight_timeouts(&mut state, &mut deferred);

    let rj = state.jobs.get(&21).unwrap();
    assert!(!rj.in_flight);
    assert!(rj.in_flight_since.is_none());
    let last = rj.history.back().unwrap();
    assert_eq!(last.outcome, "timeout");
}

#[test]
fn test_timeout_ignores_not_in_flight() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(22, "to3", 5);
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(22, rj);

    let mut deferred = DeferredLog::default();
    check_in_flight_timeouts(&mut state, &mut deferred);

    let rj = state.jobs.get(&22).unwrap();
    assert!(!rj.in_flight);
    assert!(rj.history.is_empty());
}

// ################################################################
// reanchor_all_jobs
// ################################################################

#[test]
fn test_reanchor_updates_active_jobs() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(30, "ra1", 10);
    let mut rj = RunningJob::from_scheduler_job(&job);
    rj.next_fire_utc = Some(Utc::now() - Duration::hours(2));
    state.jobs.insert(30, rj);

    let now = Utc::now();
    reanchor_all_jobs(&mut state, now);

    let rj = state.jobs.get(&30).unwrap();
    assert!(rj.next_fire_utc.is_some());
    assert!(rj.next_fire_utc.unwrap() >= now);
}

#[test]
fn test_reanchor_skips_inactive_jobs() {
    let mut state = SchedulerState::new();
    let mut job = make_interval_job(31, "ra2", 10);
    job.is_active = false;
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(31, rj);

    reanchor_all_jobs(&mut state, Utc::now());

    let rj = state.jobs.get(&31).unwrap();
    assert!(rj.next_fire_utc.is_none());
}
