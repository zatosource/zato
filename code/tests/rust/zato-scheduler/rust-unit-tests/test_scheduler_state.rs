use std::collections::HashMap;
use std::sync::atomic::Ordering;
use std::sync::Arc;

use zato_scheduler_core::calendar::CalendarData;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::model::SchedulerJob;
use zato_scheduler_core::scheduler::{SchedulerShared, SchedulerState};

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
// SchedulerState basics
// ################################################################

#[test]
fn test_new_state_is_empty() {
    let state = SchedulerState::new();
    assert!(state.jobs.is_empty());
    assert!(state.calendars.is_empty());
    assert!(!state.dirty);
}

#[test]
fn test_insert_and_retrieve_job() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(1, "s1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(1, rj);
    assert_eq!(state.jobs.len(), 1);
    assert!(state.jobs.contains_key(&1));
}

#[test]
fn test_remove_job() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(2, "s2", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(2, rj);
    state.jobs.remove(&2);
    assert!(state.jobs.is_empty());
}

#[test]
fn test_insert_calendar() {
    let mut state = SchedulerState::new();
    let cal = CalendarData::new("test-cal".into());
    state.calendars.insert("test-cal".into(), cal);
    assert_eq!(state.calendars.len(), 1);
}

// ################################################################
// SchedulerShared
// ################################################################

#[test]
fn test_shared_initial_state() {
    let shared = SchedulerShared::new();
    assert!(!shared.stop_flag.load(Ordering::Relaxed));

    let state = shared.state.lock();
    assert!(state.jobs.is_empty());
}

#[test]
fn test_shared_stop_flag() {
    let shared = SchedulerShared::new();
    shared.stop_flag.store(true, Ordering::Relaxed);
    assert!(shared.stop_flag.load(Ordering::Relaxed));
}

#[test]
fn test_shared_condvar_notify() {
    let shared = Arc::new(SchedulerShared::new());
    let shared2 = Arc::clone(&shared);

    let handle = std::thread::spawn(move || {
        let mut state = shared2.state.lock();
        let timeout = shared2
            .condvar
            .wait_for(&mut state, std::time::Duration::from_secs(5));
        let _ = timeout;
        state.dirty
    });

    std::thread::sleep(std::time::Duration::from_millis(50));
    {
        let mut state = shared.state.lock();
        state.dirty = true;
    }
    shared.condvar.notify_one();

    let result = handle.join().unwrap();
    assert!(result);
}

// ################################################################
// Job CRUD through state
// ################################################################

#[test]
fn test_edit_existing_job_in_state() {
    let mut state = SchedulerState::new();
    let job = make_interval_job(10, "e1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    state.jobs.insert(10, rj);

    let updated = make_interval_job(10, "e1-renamed", 20);
    if let Some(existing) = state.jobs.get_mut(&10) {
        existing.update_from_job(&updated);
    }

    let rj = state.jobs.get(&10).unwrap();
    assert_eq!(rj.name, "e1-renamed");
    assert_eq!(rj.interval_ms, 20 * 60_000);
}

#[test]
fn test_multiple_jobs_independent() {
    let mut state = SchedulerState::new();

    for i in 1_i64..=5 {
        let job = make_interval_job(i, &format!("multi-{}", i), 10 * i as u32);
        let rj = RunningJob::from_scheduler_job(&job);
        state.jobs.insert(i, rj);
    }

    assert_eq!(state.jobs.len(), 5);

    state.jobs.remove(&3);
    assert_eq!(state.jobs.len(), 4);
    assert!(!state.jobs.contains_key(&3));
    assert!(state.jobs.contains_key(&1));
}

// ################################################################
// Holiday calendar integration with jobs
// ################################################################

#[test]
fn test_job_holiday_check_no_calendar() {
    let job = make_interval_job(20, "hol1", 10);
    let rj = RunningJob::from_scheduler_job(&job);
    let cals = HashMap::new();
    assert!(!rj.is_holiday_today(&cals));
}

#[test]
fn test_job_holiday_check_missing_calendar_name() {
    let mut job = make_interval_job(21, "hol2", 10);
    job.calendar = Some("nonexistent".into());
    let rj = RunningJob::from_scheduler_job(&job);
    let cals = HashMap::new();
    assert!(!rj.is_holiday_today(&cals));
}
