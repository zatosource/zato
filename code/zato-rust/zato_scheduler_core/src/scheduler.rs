//! Scheduler core loop and supporting functions.

use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

use chrono::Utc;
use parking_lot::{Condvar, Mutex};

use crate::DeferredLog;
use crate::calendar::CalendarData;
use crate::deferred_log;
use crate::job::{ExecutionRecord, LogEntry, RunningJob};
use crate::types::{FireBatch, outcome};

/// Default threshold (ms) for detecting wall-clock jumps relative to monotonic time.
const DEFAULT_CLOCK_JUMP_THRESHOLD_MS: i64 = 5_000;

/// Default coalesce window (ms) - jobs whose fire time falls within this
/// window ahead of "now" are collected in the same tick.
const DEFAULT_COALESCE_WINDOW_MS: i64 = 50;

/// Mutable state guarded by the scheduler mutex.
pub struct SchedulerState {
    /// Map of job id to its runtime representation.
    pub jobs: HashMap<i64, RunningJob>,
    /// Holiday / exclusion calendars keyed by name.
    pub calendars: HashMap<String, CalendarData>,
    /// Flag set whenever the state is mutated from outside the loop.
    pub dirty: bool,
}

impl Default for SchedulerState {
    fn default() -> Self {
        Self::new()
    }
}

impl SchedulerState {
    /// Creates a new empty scheduler state.
    #[must_use]
    pub fn new() -> Self {
        Self {
            jobs: HashMap::new(),
            calendars: HashMap::new(),
            dirty: false,
        }
    }
}

/// Shared data visible to both the scheduler thread and the command listener.
pub struct SchedulerShared {
    /// Mutex-protected mutable state.
    pub state: Mutex<SchedulerState>,
    /// Condvar used to wake the scheduler thread early.
    pub condvar: Condvar,
    /// When set, the scheduler thread exits at the next opportunity.
    pub stop_flag: AtomicBool,
    /// Threshold (ms) for detecting wall-clock vs. monotonic drift.
    pub clock_jump_threshold_ms: i64,
    /// Window (ms) for coalescing nearly-due jobs into one tick.
    pub coalesce_window_ms: i64,
}

impl Default for SchedulerShared {
    fn default() -> Self {
        Self::new()
    }
}

impl SchedulerShared {
    /// Creates a new `SchedulerShared` with default thresholds.
    #[must_use]
    pub fn new() -> Self {
        Self {
            state: Mutex::new(SchedulerState::new()),
            condvar: Condvar::new(),
            stop_flag: AtomicBool::new(false),
            clock_jump_threshold_ms: DEFAULT_CLOCK_JUMP_THRESHOLD_MS,
            coalesce_window_ms: DEFAULT_COALESCE_WINDOW_MS,
        }
    }
}

/// Main scheduler loop, meant to run on a dedicated thread.
///
/// Fires due jobs by sending `FireBatch` items through the provided sender.
/// The receiver end publishes them to Redis.
pub fn scheduler_loop(
    shared: Arc<SchedulerShared>,
    fire_sender: std::sync::mpsc::Sender<FireBatch>,
    initial_sleep_time: f64,
    heartbeat: Option<crate::watchdog::HeartbeatHandle>,
) {
    if initial_sleep_time > 0.0 {
        std::thread::sleep(Duration::from_secs_f64(initial_sleep_time));
    }

    if shared.stop_flag.load(Ordering::Relaxed) {
        return;
    }

    tracing::info!("Scheduler loop started");

    let mut last_wall = Utc::now();
    let mut last_mono = Instant::now();
    let mut last_status_log = Instant::now();
    let status_log_interval = Duration::from_secs(60);

    loop {
        if let Some(handle) = &heartbeat {
            handle.beat();
        }

        if shared.stop_flag.load(Ordering::Relaxed) {
            break;
        }

        {
            let mut state = shared.state.lock();
            let sleep_duration = compute_sleep_duration(&state);
            let sleep_ms = sleep_duration.as_millis() as u64;
            if sleep_ms > 100 {
                tracing::debug!("Sleeping for {}", crate::humanize_ms(sleep_ms));
            }
            if let Some(handle) = &heartbeat {
                handle.set_expected_sleep(sleep_duration);
            }
            let _timed_out = shared.condvar.wait_for(&mut state, sleep_duration);
        }

        if let Some(handle) = &heartbeat {
            handle.beat();
        }

        if shared.stop_flag.load(Ordering::Relaxed) {
            break;
        }

        let now_wall = Utc::now();
        let now_mono = Instant::now();
        let wall_delta_ms = (now_wall - last_wall).num_milliseconds();
        let mono_delta_ms = i64::try_from(now_mono.duration_since(last_mono).as_millis()).unwrap_or(i64::MAX);
        let drift_ms = (wall_delta_ms - mono_delta_ms).abs();

        if drift_ms > shared.clock_jump_threshold_ms {
            tracing::warn!("Clock jump detected (drift_ms={drift_ms}), reanchoring all jobs");
            let mut state = shared.state.lock();
            reanchor_all_jobs(&mut state, now_wall);
        }

        last_wall = now_wall;
        last_mono = now_mono;

        if last_status_log.elapsed() >= status_log_interval {
            last_status_log = Instant::now();
            let state = shared.state.lock();
            log_scheduler_status(&state, now_wall);
            drop(state);
        }

        let fire_batch = {
            let mut deferred = DeferredLog::new();
            let batch = {
                let mut state = shared.state.lock();
                check_in_flight_timeouts(&mut state, &mut deferred);
                collect_due_jobs(&mut state, now_wall, shared.coalesce_window_ms, &mut deferred)
            };
            deferred.flush();
            batch
        };

        for item in fire_batch {
            if fire_sender.send(item).is_err() {
                tracing::error!("Fire event channel closed, exiting scheduler loop");
                return;
            }
        }
    }
}

/// Computes how long the scheduler loop should sleep before the next tick.
#[must_use]
pub fn compute_sleep_duration(state: &SchedulerState) -> Duration {
    let now = Utc::now();
    let now_instant = Instant::now();
    let mut min_ms: i64 = 60_000;

    for running_job in state.jobs.values() {
        if !running_job.is_active {
            continue;
        }

        if running_job.in_flight
            && let Some(since) = running_job.in_flight_since
        {
            let elapsed_ms = i64::try_from(now_instant.saturating_duration_since(since).as_millis()).unwrap_or(i64::MAX);
            let limit_ms = i64::try_from(running_job.max_execution_time_ms).unwrap_or(i64::MAX);
            let until_timeout_ms = (limit_ms - elapsed_ms).max(1);
            if until_timeout_ms < min_ms {
                min_ms = until_timeout_ms;
            }
        }

        if let Some(fire_utc) = running_job.next_fire_utc {
            let diff = (fire_utc - now).num_milliseconds();
            if diff < min_ms {
                min_ms = diff;
            }
        }
    }

    let clamped = min_ms.max(1);
    Duration::from_millis(u64::try_from(clamped).unwrap_or(1))
}

/// Collects all jobs whose next fire time falls within the coalesce window.
///
/// Jobs that are currently in flight are silently skipped; missed-fire catchup
/// for long-running jobs is handled in `mark_complete` logic instead.
pub fn collect_due_jobs(
    state: &mut SchedulerState,
    now: chrono::DateTime<Utc>,
    coalesce_window_ms: i64,
    deferred: &mut DeferredLog,
) -> Vec<FireBatch> {
    let threshold = now + chrono::Duration::milliseconds(coalesce_window_ms);
    let mut batch = Vec::new();

    let job_ids: Vec<i64> = state.jobs.keys().copied().collect();

    for job_id in job_ids {
        let calendars_ref = &state.calendars;
        let Some(running_job) = state.jobs.get_mut(&job_id) else { continue };

        if !running_job.is_active {
            continue;
        }

        let Some(fire_utc) = running_job.next_fire_utc else {
            continue;
        };

        if fire_utc > threshold {
            continue;
        }

        if running_job.in_flight {
            continue;
        }

        let planned = fire_utc.to_rfc3339();
        let actual = now.to_rfc3339();

        running_job.current_run += 1;
        let delay_ms = (now - fire_utc).num_milliseconds().max(0);
        let delay_ms_unsigned = u64::try_from(delay_ms).unwrap_or(0);

        deferred_log!(
            deferred,
            tracing::Level::INFO,
            "Job executing: name={} run={} service={} delay_ms={delay_ms} job_id={job_id}",
            running_job.name,
            running_job.current_run,
            running_job.service,
        );

        if running_job.is_holiday_today(calendars_ref) {
            running_job.record_execution(ExecutionRecord::new(
                &planned,
                &actual,
                outcome::SKIPPED_HOLIDAY,
                running_job.current_run,
            ));
            running_job.advance_to_next(now);
            continue;
        }

        running_job.in_flight = true;
        running_job.in_flight_since = Some(Instant::now());
        running_job.in_flight_run = Some(running_job.current_run);

        batch.push(FireBatch {
            job_id: running_job.id,
            name: running_job.name.clone(),
            service: running_job.service.clone(),
            extra: running_job.extra.clone(),
            job_type: running_job.job_type.clone(),
            current_run: running_job.current_run,
        });

        let mut rec = ExecutionRecord::new(&planned, &actual, outcome::RUNNING, running_job.current_run).with_delay(delay_ms_unsigned);

        rec.log_entries.push(LogEntry {
            timestamp_iso: actual.clone(),
            level: "SYSTEM".into(),
            message: format!("Job started, delay: {}", crate::humanize_ms(delay_ms_unsigned)),
        });

        running_job.record_execution(rec);
        running_job.advance_to_next(now);
    }

    batch
}

/// Checks all in-flight jobs for execution-time timeouts and marks them accordingly.
pub fn check_in_flight_timeouts(state: &mut SchedulerState, deferred: &mut DeferredLog) {
    let now_instant = Instant::now();

    for (&job_id, running_job) in &mut state.jobs {
        if !running_job.in_flight {
            continue;
        }
        let Some(since) = running_job.in_flight_since else { continue };
        let elapsed_ms = u64::try_from(now_instant.duration_since(since).as_millis()).unwrap_or(u64::MAX);
        if elapsed_ms > running_job.max_execution_time_ms {
            let timed_out_run = running_job.in_flight_run.unwrap_or(0);
            deferred_log!(
                deferred,
                tracing::Level::WARN,
                "Timed out name={} run={timed_out_run} after {elapsed_ms}ms (max={}) job_id={}",
                running_job.name,
                running_job.max_execution_time_ms,
                job_id,
            );
            running_job.in_flight = false;
            running_job.in_flight_since = None;
            running_job.in_flight_run = None;
            running_job.record_execution(
                ExecutionRecord::new("", &Utc::now().to_rfc3339(), outcome::TIMEOUT, timed_out_run)
                    .with_duration(elapsed_ms)
                    .with_error(format!("exceeded max_execution_time_ms={}", running_job.max_execution_time_ms)),
            );
        }
    }
}

/// Recomputes `next_fire_utc` for every active job after a clock jump.
pub fn reanchor_all_jobs(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    for running_job in state.jobs.values_mut() {
        if running_job.is_active {
            running_job.compute_next_fire(now);
        }
    }
}

/// Logs a periodic summary of scheduler state - active/paused/in-flight counts
/// and the soonest upcoming fire time.
fn log_scheduler_status(state: &SchedulerState, now: chrono::DateTime<Utc>) {
    let total = state.jobs.len();
    let mut active: usize = 0;
    let mut in_flight: usize = 0;
    let mut soonest_name: Option<&str> = None;
    let mut soonest_ms: i64 = i64::MAX;

    for running_job in state.jobs.values() {
        if running_job.is_active {
            active += 1;
        }
        if running_job.in_flight {
            in_flight += 1;
        }
        if let Some(fire_utc) = running_job.next_fire_utc {
            let diff = (fire_utc - now).num_milliseconds();
            if diff < soonest_ms {
                soonest_ms = diff;
                soonest_name = Some(&running_job.name);
            }
        }
    }

    let paused = total - active;

    if let Some(name) = soonest_name {
        let soonest_human = crate::humanize_ms(u64::try_from(soonest_ms.max(0)).unwrap_or(0));
        tracing::info!(
            "Status: {total} jobs ({active} active, {paused} paused, {in_flight} in-flight), next fire: {name} in {soonest_human}"
        );
    } else {
        tracing::info!("Status: {total} jobs ({active} active, {paused} paused, {in_flight} in-flight), no upcoming fires");
    }
}
