//! Scheduler core loop and supporting functions.

use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

use chrono::Utc;
use parking_lot::{Condvar, Mutex};
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::DeferredLog;
use crate::calendar::CalendarData;
use crate::deferred_log;
use crate::job::{ExecutionRecord, LogEntry, RunningJob};
use crate::types::{FireBatch, outcome};

/// Re-export of `Py<PyAny>` for brevity.
type PyObject = Py<PyAny>;

/// Default threshold (ms) for detecting wall-clock jumps relative to monotonic time.
const DEFAULT_CLOCK_JUMP_THRESHOLD_MS: i64 = 5_000;

/// Default coalesce window (ms) - jobs whose fire time falls within this
/// window ahead of "now" are collected in the same tick.
const DEFAULT_COALESCE_WINDOW_MS: i64 = 50;

/// A single pending synthetic log entry to be drip-fed into a running execution record.
pub struct SyntheticDrip {
    /// When this drip becomes due.
    pub due_at: Instant,
    /// Target job.
    pub job_id: i64,
    /// Target execution run number.
    pub current_run: u32,
    /// Log entry to append.
    pub entry: LogEntry,
    /// If set, finalize the record with this outcome and duration after appending.
    pub finalize: Option<(String, u64)>,
}

impl PartialEq for SyntheticDrip {
    fn eq(&self, other: &Self) -> bool {
        self.due_at == other.due_at
    }
}

impl Eq for SyntheticDrip {}

impl PartialOrd for SyntheticDrip {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for SyntheticDrip {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.due_at.cmp(&other.due_at)
    }
}

/// Mutable state guarded by the scheduler mutex.
pub struct SchedulerState {
    /// Map of job id to its runtime representation.
    pub jobs: HashMap<i64, RunningJob>,
    /// Holiday / exclusion calendars keyed by name.
    pub calendars: HashMap<String, CalendarData>,
    /// Flag set whenever the state is mutated from outside the loop.
    pub dirty: bool,
    /// Pending synthetic log drips in a min-heap ordered by `due_at`.
    pub synthetic_drips: BinaryHeap<Reverse<SyntheticDrip>>,
    /// Whether synthetic test data injection is enabled.
    pub with_test_data: bool,
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
            synthetic_drips: BinaryHeap::new(),
            with_test_data: false,
        }
    }
}

/// Shared data visible to both the scheduler thread and the Python API.
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

/// Python callbacks used by the scheduler to dispatch and report job execution.
pub struct SchedulerCallbacks {
    /// Called to run a job via the gevent event loop.
    pub run_cb: PyObject,
    /// The gevent spawn function used to schedule greenlets.
    pub spawn_fn: PyObject,
    /// Called after a job finishes executing to record the result.
    pub on_job_executed_cb: PyObject,
}

/// Main scheduler loop, meant to run on a dedicated thread.
#[expect(clippy::needless_pass_by_value, reason = "thread entry point owns these values")]
pub fn scheduler_loop(
    shared: Arc<SchedulerShared>,
    callbacks: SchedulerCallbacks,
    initial_sleep_time: f64,
    heartbeat: Option<crate::watchdog::HeartbeatHandle>,
) {
    if initial_sleep_time > 0.0 {
        std::thread::sleep(Duration::from_secs_f64(initial_sleep_time));
    }

    if shared.stop_flag.load(Ordering::Relaxed) {
        return;
    }

    let mut last_wall = Utc::now();
    let mut last_mono = Instant::now();

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
            log::warn!("Clock jump detected (drift_ms={drift_ms}), reanchoring all jobs");
            let mut state = shared.state.lock();
            reanchor_all_jobs(&mut state, now_wall);
        }

        last_wall = now_wall;
        last_mono = now_mono;

        let fire_batch = {
            let mut deferred = DeferredLog::new();
            let batch = {
                let mut state = shared.state.lock();
                check_in_flight_timeouts(&mut state, &mut deferred);
                drain_synthetic_drips(&mut state);
                collect_due_jobs(&mut state, now_wall, shared.coalesce_window_ms, &mut deferred)
            };
            deferred.flush();
            batch
        };

        if !fire_batch.is_empty() {
            for item in &fire_batch {
                log::info!(
                    "Dispatching job_id={} name={} service={} run={}",
                    item.job_id.0,
                    item.name,
                    item.service,
                    item.current_run,
                );
            }
            dispatch_jobs(&fire_batch, &callbacks.run_cb, &callbacks.spawn_fn, &callbacks.on_job_executed_cb);
        }
    }
}

/// Load jobs from the ODB adapter, returning parsed job models and calendar models.
///
/// # Errors
///
/// Returns a `PyErr` if the adapter call or dict extraction fails.
pub fn load_jobs(
    adapter: &Bound<'_, PyAny>,
) -> PyResult<(Vec<crate::model::SchedulerJob>, HashMap<String, crate::model::HolidayCalendar>)> {
    use pyo3::types::PyDict;

    let jobs_dict: Bound<'_, PyDict> = adapter.call_method0("get_scheduler_jobs")?.cast_into()?;
    let mut jobs = Vec::new();
    for (key, value) in jobs_dict.iter() {
        let job_id: i64 = key.extract()?;
        let job_data: Bound<'_, PyDict> = value.cast_into()?;
        let scheduler_job = crate::dict_to_scheduler_job(job_id, &job_data)?;
        jobs.push(scheduler_job);
    }

    let cals = HashMap::new();
    Ok((jobs, cals))
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

        if running_job.in_flight {
            if let Some(since) = running_job.in_flight_since {
                let elapsed_ms = i64::try_from(now_instant.saturating_duration_since(since).as_millis()).unwrap_or(i64::MAX);
                let limit_ms = i64::try_from(running_job.max_execution_time_ms).unwrap_or(i64::MAX);
                let until_timeout_ms = (limit_ms - elapsed_ms).max(1);
                if until_timeout_ms < min_ms {
                    min_ms = until_timeout_ms;
                }
            }
            continue;
        }

        if let Some(fire_utc) = running_job.next_fire_utc {
            let diff = (fire_utc - now).num_milliseconds();
            if diff < min_ms {
                min_ms = diff;
            }
        }
    }

    if let Some(Reverse(front)) = state.synthetic_drips.peek() {
        let drip_ms = i64::try_from(front.due_at.saturating_duration_since(Instant::now()).as_millis()).unwrap_or(i64::MAX);
        if drip_ms < min_ms {
            min_ms = drip_ms;
        }
    }

    let clamped = min_ms.max(1);
    Duration::from_millis(u64::try_from(clamped).unwrap_or(1))
}

/// Collects all jobs whose next fire time falls within the coalesce window.
///
/// Jobs that are currently in flight are silently skipped; missed-fire catchup
/// for long-running jobs is handled in `Scheduler::mark_complete` instead.
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
            log::Level::Info,
            "Firing job_id={job_id} name={} run={} delay_ms={delay_ms}",
            running_job.name,
            running_job.current_run,
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

/// Dispatches a batch of due jobs to the Python callback.
fn dispatch_jobs(batch: &[FireBatch], run_cb: &PyObject, spawn_fn: &PyObject, on_job_executed_cb: &PyObject) {
    let _attached = Python::try_attach(|py| {
        for item in batch {
            let ctx_dict = PyDict::new(py);
            ctx_dict.set_item("id", item.job_id.0).ok();
            ctx_dict.set_item("name", &item.name).ok();
            ctx_dict.set_item("service", item.service.as_ref()).ok();
            ctx_dict.set_item("extra", &item.extra).ok();
            ctx_dict.set_item("job_type", item.job_type.as_str()).ok();
            ctx_dict.set_item("current_run", item.current_run).ok();
            let py_ctx = ctx_dict.into_any().unbind();
            if let Err(err) = run_cb.call1(py, (spawn_fn, on_job_executed_cb, py_ctx)) {
                log::error!(
                    "Failed to dispatch job `{}` (service=`{}`, run={}): {}",
                    item.name,
                    item.service,
                    item.current_run,
                    err
                );
            }
        }
    });
}

/// Checks all in-flight jobs for execution-time timeouts and marks them accordingly.
pub fn check_in_flight_timeouts(state: &mut SchedulerState, deferred: &mut DeferredLog) {
    let now_instant = Instant::now();

    for running_job in state.jobs.values_mut() {
        if !running_job.in_flight {
            continue;
        }
        let Some(since) = running_job.in_flight_since else { continue };
        let elapsed_ms = u64::try_from(now_instant.duration_since(since).as_millis()).unwrap_or(u64::MAX);
        if elapsed_ms > running_job.max_execution_time_ms {
            let timed_out_run = running_job.in_flight_run.unwrap_or(0);
            deferred_log!(
                deferred,
                log::Level::Warn,
                "Timed out job={} run={timed_out_run} after {elapsed_ms}ms (max={})",
                running_job.name,
                running_job.max_execution_time_ms,
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

/// Processes any due synthetic log drips, appending entries and optionally finalizing records.
///
/// This is a no-op when `with_test_data` is false.
pub fn drain_synthetic_drips(state: &mut SchedulerState) {
    if !state.with_test_data {
        return;
    }
    let now = Instant::now();
    while let Some(Reverse(front)) = state.synthetic_drips.peek() {
        if front.due_at > now {
            break;
        }
        let Some(Reverse(drip)) = state.synthetic_drips.pop() else { break };
        if let Some(running_job) = state.jobs.get_mut(&drip.job_id) {
            for rec in running_job.history.iter_mut().rev() {
                if rec.current_run == drip.current_run {
                    rec.log_entries.push(drip.entry);
                    if let Some((ref final_outcome, final_duration)) = drip.finalize {
                        rec.outcome.clone_from(final_outcome);
                        rec.duration_ms = Some(final_duration);
                    }
                    break;
                }
            }
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
