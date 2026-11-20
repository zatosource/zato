//! Scheduler core loop and supporting functions.

use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

use jiff::{SignedDuration, Timestamp};
use parking_lot::{Condvar, Mutex};

use crate::DeferredLog;
use crate::deferred_log;
use crate::job::{RunningJob, signed_millis, to_rfc3339};
use crate::types::{FireBatch, OutgoingEvent, TimeoutEvent, outcome};

/// Default threshold (ms) for detecting wall-clock jumps relative to monotonic time.
const DEFAULT_CLOCK_JUMP_THRESHOLD_MS: i64 = 5_000;

/// Default coalesce window (ms) - jobs whose fire time falls within this
/// window ahead of "now" are collected in the same tick.
const DEFAULT_COALESCE_WINDOW_MS: i64 = 50;

/// Mutable state guarded by the scheduler mutex.
pub struct SchedulerState {
    /// Map of job id to its runtime representation.
    pub jobs: HashMap<i64, RunningJob>,

    /// The number of the latest command or reload applied to each job, deleted jobs included,
    /// from the counter that numbers every reload and every job command of the server.
    pub job_sequences: HashMap<i64, u64>,

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
            job_sequences: HashMap::new(),
            dirty: false,
        }
    }

    /// Whether a command or a reload numbered after the given number was applied to the job already.
    #[must_use]
    pub fn is_changed_after(&self, job_id: i64, sequence: u64) -> bool {
        self.job_sequences.get(&job_id).is_some_and(|applied| *applied > sequence)
    }

    /// Records the number of the command or reload that was applied to the job last.
    pub fn record_change(&mut self, job_id: i64, sequence: u64) {
        self.job_sequences.insert(job_id, sequence);
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
    /// Channel for publishing outgoing events directly (used by forced execute).
    pub fire_sender: Mutex<Option<std::sync::mpsc::Sender<OutgoingEvent>>>,
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
            fire_sender: Mutex::new(None),
        }
    }
}

/// Main scheduler loop, meant to run on a dedicated thread.
///
/// Fires due jobs and reports timed-out runs by sending `OutgoingEvent` items
/// through the provided sender. The receiver end publishes them to Redis.
pub fn scheduler_loop(
    shared: &Arc<SchedulerShared>,
    fire_sender: &std::sync::mpsc::Sender<OutgoingEvent>,
    initial_sleep_time: f64,
    heartbeat: Option<&crate::watchdog::HeartbeatHandle>,
) {
    if initial_sleep_time > 0.0 {
        std::thread::sleep(Duration::from_secs_f64(initial_sleep_time));
    }

    if shared.stop_flag.load(Ordering::Relaxed) {
        return;
    }

    tracing::info!("Scheduler loop started");

    let mut last_wall = Timestamp::now();
    let mut last_mono = Instant::now();
    let mut last_status_log = Instant::now();
    let status_log_interval = Duration::from_mins(1);

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
            // A sleep never spans more than a few minutes, so it always fits in a u64,
            // and saturating keeps a wildly out-of-range value from wrapping to a short nap.
            let sleep_ms = u64::try_from(sleep_duration.as_millis()).unwrap_or(u64::MAX);
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

        crate::metrics::TICKS_TOTAL.inc();

        let now_wall = Timestamp::now();
        let now_mono = Instant::now();
        let wall_delta_ms = signed_millis(now_wall, last_wall);
        let mono_delta_ms = i64::try_from(now_mono.duration_since(last_mono).as_millis()).unwrap_or(i64::MAX);
        let drift_ms = (wall_delta_ms - mono_delta_ms).abs();

        if drift_ms > shared.clock_jump_threshold_ms {
            tracing::warn!("Clock jump detected (drift_ms={drift_ms}), reanchoring all jobs");
            crate::metrics::CLOCK_JUMPS_TOTAL.inc();
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

        let (fire_batch, timeout_events) = {
            let mut deferred = DeferredLog::new();
            let batch_and_timeouts = {
                let mut state = shared.state.lock();
                let timeouts = check_in_flight_timeouts(&mut state, &mut deferred);
                let batch = collect_due_jobs(&mut state, now_wall, shared.coalesce_window_ms, &mut deferred);

                let mut total: i64 = 0;
                let mut active: i64 = 0;
                let mut in_flight: i64 = 0;
                for running_job in state.jobs.values() {
                    total += 1;
                    if running_job.is_active {
                        active += 1;
                    }
                    if running_job.is_in_flight() {
                        in_flight += 1;
                    }
                }
                crate::metrics::JOBS_TOTAL.set(total);
                crate::metrics::JOBS_ACTIVE.set(active);
                crate::metrics::JOBS_IN_FLIGHT.set(in_flight);

                // The counts are taken, so the state lock goes back before the deferred log
                // is flushed, which does its own I/O.
                drop(state);
                (batch, timeouts)
            };
            deferred.flush();
            batch_and_timeouts
        };

        // Timed-out runs go out first so the server marks them before any new fire arrives
        for timeout_event in timeout_events {
            if fire_sender.send(OutgoingEvent::Timeout(timeout_event)).is_err() {
                tracing::error!("Fire event channel closed, exiting scheduler loop");
                return;
            }
        }

        for item in &fire_batch {
            crate::metrics::EXECUTIONS_TOTAL
                .with_label_values(&[item.name.as_str(), "fired"])
                .inc();
        }

        for item in fire_batch {
            if fire_sender.send(OutgoingEvent::Fire(item)).is_err() {
                tracing::error!("Fire event channel closed, exiting scheduler loop");
                return;
            }
        }
    }
}

/// Computes how long the scheduler loop should sleep before the next tick.
#[must_use]
pub fn compute_sleep_duration(state: &SchedulerState) -> Duration {
    let now = Timestamp::now();
    let now_instant = Instant::now();
    let mut min_ms: i64 = 60_000;

    for running_job in state.jobs.values() {
        if !running_job.is_active {
            continue;
        }

        // The earliest run in flight is the first one to reach its execution time limit
        if let Some(since) = running_job.earliest_in_flight_since() {
            let elapsed_ms = i64::try_from(now_instant.saturating_duration_since(since).as_millis()).unwrap_or(i64::MAX);
            let limit_ms = i64::try_from(running_job.max_execution_time_ms).unwrap_or(i64::MAX);
            let until_timeout_ms = (limit_ms - elapsed_ms).max(1);
            if until_timeout_ms < min_ms {
                min_ms = until_timeout_ms;
            }
        }

        if let Some(fire_utc) = running_job.next_fire_utc {
            let diff = signed_millis(fire_utc, now);
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
pub fn collect_due_jobs(state: &mut SchedulerState, now: Timestamp, coalesce_window_ms: i64, deferred: &mut DeferredLog) -> Vec<FireBatch> {
    let threshold = now + SignedDuration::from_millis(coalesce_window_ms);
    let mut batch = Vec::new();

    let job_ids: Vec<i64> = state.jobs.keys().copied().collect();

    for job_id in job_ids {
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

        if running_job.is_in_flight() {
            continue;
        }

        let planned = to_rfc3339(fire_utc);
        let nominal = running_job.next_nominal_utc.map_or_else(String::new, to_rfc3339);

        running_job.current_run += 1;
        let delay_ms = signed_millis(now, fire_utc).max(0);

        deferred_log!(
            deferred,
            tracing::Level::INFO,
            "Job executing: name={} run={} service={} delay_ms={delay_ms} job_id={job_id}",
            running_job.name,
            running_job.current_run,
            running_job.service,
        );

        let current_run = running_job.current_run;
        running_job.start_run(current_run, Instant::now());

        batch.push(FireBatch {
            job_id: running_job.id,
            name: running_job.name.clone(),
            service: running_job.service.clone(),
            extra: running_job.extra.clone(),
            job_type: running_job.job_type.clone(),
            current_run: running_job.current_run,
            planned_fire_time_iso: planned,
            nominal_fire_time_iso: nominal,
            on_success_service: running_job.on_success_service.clone(),
            on_success_job: running_job.on_success_job.clone(),
            on_error_service: running_job.on_error_service.clone(),
            on_error_job: running_job.on_error_job.clone(),
        });

        running_job.advance_to_next(now);
    }

    batch
}

/// Checks every run in flight of every job for execution-time timeouts, removes each run
/// that exceeded the limit and returns the timeout events the server records in the audit log.
pub fn check_in_flight_timeouts(state: &mut SchedulerState, deferred: &mut DeferredLog) -> Vec<TimeoutEvent> {
    let now_instant = Instant::now();
    let mut timeout_events = Vec::new();

    for (&job_id, running_job) in &mut state.jobs {
        // Each run is timed out on its own, so a run fired later keeps its own limit
        let timed_out_runs: Vec<(u32, u64)> = running_job
            .in_flight_runs
            .iter()
            .filter_map(|(&run, &since)| {
                let elapsed_ms = u64::try_from(now_instant.duration_since(since).as_millis()).unwrap_or(u64::MAX);
                (elapsed_ms > running_job.max_execution_time_ms).then_some((run, elapsed_ms))
            })
            .collect();

        for (timed_out_run, elapsed_ms) in timed_out_runs {
            deferred_log!(
                deferred,
                tracing::Level::WARN,
                "Timed out name={} run={timed_out_run} after {elapsed_ms}ms (max={}) job_id={}",
                running_job.name,
                running_job.max_execution_time_ms,
                job_id,
            );
            crate::metrics::EXECUTIONS_TOTAL
                .with_label_values(&[running_job.name.as_str(), outcome::TIMEOUT])
                .inc();

            // Durations here are wall-clock milliseconds of a single job run, far below the
            // point where f64 stops representing whole milliseconds exactly.
            let duration_secs = crate::convert::ms_to_seconds(elapsed_ms);
            crate::metrics::EXECUTION_DURATION_SECONDS
                .with_label_values(&[&running_job.name])
                .observe(duration_secs);

            running_job.complete_run(timed_out_run);

            timeout_events.push(TimeoutEvent {
                job_id,
                current_run: timed_out_run,
                elapsed_ms,
                error_msg: format!("exceeded max_execution_time_ms={}", running_job.max_execution_time_ms),
            });
        }
    }

    timeout_events
}

/// Recomputes `next_fire_utc` for every active job after a clock jump.
pub fn reanchor_all_jobs(state: &mut SchedulerState, now: Timestamp) {
    for running_job in state.jobs.values_mut() {
        if running_job.is_active {
            running_job.compute_next_fire(now);
        }
    }
}

/// Logs a periodic summary of scheduler state - active/paused/in-flight counts
/// and the soonest upcoming fire time.
fn log_scheduler_status(state: &SchedulerState, now: Timestamp) {
    let total = state.jobs.len();
    let mut active: usize = 0;
    let mut in_flight: usize = 0;
    let mut soonest_name: Option<&str> = None;
    let mut soonest_ms: i64 = i64::MAX;

    for running_job in state.jobs.values() {
        if running_job.is_active {
            active += 1;
        }
        if running_job.is_in_flight() {
            in_flight += 1;
        }
        if let Some(fire_utc) = running_job.next_fire_utc {
            let diff = signed_millis(fire_utc, now);
            if diff < soonest_ms {
                soonest_ms = diff;
                soonest_name = Some(&running_job.name);
            }
        }
    }

    let paused = total - active;
    let jobs_label = crate::plural(total, "job", "jobs");

    if let Some(name) = soonest_name {
        let soonest_human = crate::humanize_ms(u64::try_from(soonest_ms.max(0)).unwrap_or(0));
        tracing::info!(
            "Status: {total} {jobs_label} ({active} active, {paused} paused, {in_flight} in-flight), next fire: {name} in {soonest_human}"
        );
    } else {
        tracing::info!("Status: {total} {jobs_label} ({active} active, {paused} paused, {in_flight} in-flight), no upcoming fires");
    }
}
