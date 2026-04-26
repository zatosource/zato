//! Core scheduler crate for Zato - re-exports submodules and provides the `PyO3` entry points.

use std::sync::Arc;
use std::sync::atomic::{AtomicU32, Ordering};
use std::time::{Duration, Instant};

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Calendar holiday support.
pub mod calendar;

/// Execution-history serialization helpers.
pub mod history;

/// Running-job state machine.
pub mod job;

/// Data-transfer objects shared between Python and Rust.
pub mod model;

/// Core scheduler loop and helpers.
pub mod scheduler;

/// Shared type definitions (job-id wrappers, outcome constants, etc.).
pub mod types;

/// Watchdog thread for detecting hung threads.
pub mod watchdog;

/// Re-exports used exclusively by the test harness.
#[doc(hidden)]
pub mod test_support {
    pub use crate::job::clamp_max_execution_time;
    pub use crate::reload_calendars;
    pub use crate::reload_jobs;
}

use calendar::CalendarData;
use job::{ExecutionRecord, LogEntry, RunningJob};
use scheduler::{SchedulerShared, SyntheticDrip};

/// Convenience alias so the rest of the module can say `PyObject`.
type PyObject = Py<PyAny>;

/// Collects log messages while the state mutex is held so they can be
/// flushed after the lock is released, avoiding `pyo3_log`'s blocking
/// `Python::attach` call that would otherwise deadlock with the GIL.
pub struct DeferredLog {
    /// Buffered messages with their log level.
    entries: Vec<(log::Level, String)>,
}

impl Default for DeferredLog {
    fn default() -> Self {
        Self::new()
    }
}

impl DeferredLog {
    /// Creates an empty buffer.
    pub const fn new() -> Self {
        Self { entries: Vec::new() }
    }

    /// Flushes all buffered messages through `log::log!`.
    ///
    /// Must be called only when no mutex is held.
    pub fn flush(self) {
        for (level, msg) in self.entries {
            log::log!(level, "{msg}");
        }
    }
}

/// Buffers a formatted log message into a `DeferredLog` instead of calling `log::` directly.
macro_rules! deferred_log {
    ($dl:expr, $level:expr, $($arg:tt)*) => {
        $dl.entries.push(($level, format!($($arg)*)))
    };
}

pub(crate) use deferred_log;

/// Releases the GIL, acquires the state lock, applies `func`, marks the state dirty and wakes the condvar.
///
/// The GIL is released before locking the mutex so that the two locks are never
/// held at the same time, preventing deadlocks with the scheduler thread.
/// The closure receives a `DeferredLog` to buffer log messages; they are
/// flushed after the mutex and the GIL detachment are both released.
fn with_state_mut<F, R>(py: Python<'_>, shared: &SchedulerShared, func: F) -> R
where
    F: FnOnce(&mut scheduler::SchedulerState, &mut DeferredLog) -> R + Send,
    R: Send,
{
    let (result, deferred) = py.detach(|| {
        let mut state = shared.state.lock();
        let mut deferred = DeferredLog::new();
        let result = func(&mut state, &mut deferred);
        state.dirty = true;
        drop(state);
        shared.condvar.notify_one();
        (result, deferred)
    });
    deferred.flush();
    result
}

/// Formats a duration in milliseconds into a human-readable string.
fn humanize_ms(millis: u64) -> String {
    if millis == 0 {
        return "< 1ms".to_string();
    }
    humantime::format_duration(Duration::from_millis(millis)).to_string()
}

/// Populates an already-completed synthetic execution record with realistic log entries.
fn populate_synthetic_logs(rec: &mut ExecutionRecord, now_iso: &str, fake_outcome: &str) {
    rec.log_entries.push(LogEntry {
        timestamp_iso: now_iso.into(),
        level: "SYSTEM".into(),
        message: format!("Scheduler fired job, outcome={fake_outcome}"),
    });
    rec.log_entries.push(LogEntry {
        timestamp_iso: now_iso.into(),
        level: "INFO".into(),
        message: "Connecting to backend service endpoint".into(),
    });
    rec.log_entries.push(LogEntry {
        timestamp_iso: now_iso.into(),
        level: "INFO".into(),
        message: "Processing 42 items from input queue".into(),
    });
    if fake_outcome == types::outcome::ERROR || fake_outcome == types::outcome::TIMEOUT {
        rec.log_entries.push(LogEntry {
            timestamp_iso: now_iso.into(),
            level: "WARNING".into(),
            message: "Retry threshold reached, escalating".into(),
        });
        rec.log_entries.push(LogEntry {
            timestamp_iso: now_iso.into(),
            level: "ERROR".into(),
            message: format!("Service failed with outcome `{fake_outcome}`: connection refused"),
        });
    } else {
        rec.log_entries.push(LogEntry {
            timestamp_iso: now_iso.into(),
            level: "INFO".into(),
            message: "All items processed successfully".into(),
        });
    }
}

/// Builds the sequence of `LogEntry` items to drip-feed into a running synthetic record.
fn build_synthetic_drip_entries(now_iso: &str, fake_outcome: &str) -> Vec<LogEntry> {
    let mut entries = vec![
        LogEntry {
            timestamp_iso: now_iso.into(),
            level: "SYSTEM".into(),
            message: "Scheduler fired job, starting execution".into(),
        },
        LogEntry {
            timestamp_iso: now_iso.into(),
            level: "INFO".into(),
            message: "Connecting to backend service endpoint".into(),
        },
        LogEntry {
            timestamp_iso: now_iso.into(),
            level: "INFO".into(),
            message: "Processing 42 items from input queue".into(),
        },
    ];
    if fake_outcome == types::outcome::ERROR || fake_outcome == types::outcome::TIMEOUT {
        entries.push(LogEntry {
            timestamp_iso: now_iso.into(),
            level: "WARNING".into(),
            message: "Retry threshold reached, escalating".into(),
        });
        entries.push(LogEntry {
            timestamp_iso: now_iso.into(),
            level: "ERROR".into(),
            message: format!("Service failed with outcome `{fake_outcome}`: connection refused"),
        });
    } else {
        entries.push(LogEntry {
            timestamp_iso: now_iso.into(),
            level: "INFO".into(),
            message: "All items processed successfully".into(),
        });
    }
    entries
}

/// Non-OK outcomes injected after each real completion during testing.
const TEST_INJECT_OUTCOMES: &[&str] = &[
    types::outcome::ERROR,
    types::outcome::TIMEOUT,
    types::outcome::SKIPPED_ALREADY_IN_FLIGHT,
    types::outcome::ERROR,
    types::outcome::TIMEOUT,
    types::outcome::ERROR,
];

/// Monotonically increasing index into `TEST_INJECT_OUTCOMES`.
static TEST_INJECT_IDX: AtomicU32 = AtomicU32::new(0);

/// The scheduler runtime, exposed to Python as a `#[pyclass]`.
///
/// Owns all scheduler state so that each instance is independent.
#[pyclass]
pub struct Scheduler {
    /// Shared state accessed by both the background thread and API methods.
    shared: Arc<SchedulerShared>,
    /// Reference to the Python ODB adapter for reload operations.
    odb_adapter: PyObject,
    /// Handle for the background scheduler thread.
    thread_handle: parking_lot::Mutex<Option<std::thread::JoinHandle<()>>>,
    /// Watchdog registry for monitoring thread liveness.
    watchdog_registry: Arc<watchdog::WatchdogRegistry>,
}

#[pymethods]
impl Scheduler {
    /// Creates a new scheduler instance with no background thread running.
    #[new]
    fn new(py: Python<'_>) -> Self {
        let shared = Arc::new(SchedulerShared::new());
        let watchdog_registry = Arc::new(watchdog::WatchdogRegistry::new(Arc::clone(&shared)));
        Self {
            shared,
            odb_adapter: py.None(),
            thread_handle: parking_lot::Mutex::new(None),
            watchdog_registry,
        }
    }

    /// Starts the scheduler background thread from a config dict.
    ///
    /// The dict must contain keys: `odb_adapter`, `run_cb`, `spawn_fn`,
    /// `on_job_executed_cb`, and `initial_sleep_time`.
    fn start(&mut self, py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<()> {
        let odb_adapter: PyObject = config
            .get_item("odb_adapter")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing odb_adapter"))?
            .unbind();
        let run_cb: PyObject = config
            .get_item("run_cb")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing run_cb"))?
            .unbind();
        let spawn_fn: PyObject = config
            .get_item("spawn_fn")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing spawn_fn"))?
            .unbind();
        let on_job_executed_cb: PyObject = config
            .get_item("on_job_executed_cb")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing on_job_executed_cb"))?
            .unbind();
        let initial_sleep_time: f64 = config
            .get_item("initial_sleep_time")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing initial_sleep_time"))?
            .extract()?;
        let with_test_data: bool = config
            .get_item("with_test_data")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing with_test_data"))?
            .extract()?;

        py.detach(|| {
            let mut state = self.shared.state.lock();
            state.with_test_data = with_test_data;
        });

        self.odb_adapter = odb_adapter.clone_ref(py);
        let shared = Arc::clone(&self.shared);
        let heartbeat = self.watchdog_registry.register("zato-scheduler");

        let handle = std::thread::Builder::new()
            .name("zato-scheduler".into())
            .spawn(move || {
                let callbacks = scheduler::SchedulerCallbacks {
                    run_cb,
                    spawn_fn,
                    on_job_executed_cb,
                };
                scheduler::scheduler_loop(shared, callbacks, initial_sleep_time, Some(heartbeat));
            })
            .map_err(|err| pyo3::exceptions::PyException::new_err(format!("spawn failed: {err}")))?;

        *self.thread_handle.lock() = Some(handle);

        watchdog::start_watchdog(Arc::clone(&self.watchdog_registry));

        Ok(())
    }

    /// Requests a graceful stop and waits up to `timeout_s` seconds.
    #[pyo3(signature = (timeout_s,))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn stop(&self, timeout_s: f64) -> PyResult<()> {
        self.shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
        self.shared.condvar.notify_all();

        let handle = self.thread_handle.lock().take();
        if let Some(thread_handle) = handle {
            let deadline = std::time::Instant::now() + Duration::from_secs_f64(timeout_s.min(30.0));
            while !thread_handle.is_finished() {
                let remaining = deadline.saturating_duration_since(std::time::Instant::now());
                if remaining.is_zero() {
                    break;
                }
                std::thread::sleep(remaining.min(Duration::from_millis(50)));
            }
        }
        Ok(())
    }

    /// Creates a new job from a Python dict and inserts it into the scheduler state.
    #[pyo3(signature = (job_id, job_data))]
    fn create_job(&self, py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
        let scheduler_job = dict_to_scheduler_job(job_id, job_data)?;
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        with_state_mut(py, &self.shared, |state, _deferred| {
            state.jobs.insert(job_id, running_job);
        });
        Ok(())
    }

    /// Edits an existing job or inserts a new one if not found.
    #[pyo3(signature = (job_id, job_data))]
    fn edit_job(&self, py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
        let scheduler_job = dict_to_scheduler_job(job_id, job_data)?;
        with_state_mut(py, &self.shared, |state, _deferred| {
            if let Some(existing) = state.jobs.get_mut(&job_id) {
                existing.update_from_job(&scheduler_job);
            } else {
                let running_job = RunningJob::from_scheduler_job(&scheduler_job);
                state.jobs.insert(job_id, running_job);
            }
        });
        Ok(())
    }

    /// Removes a job from the scheduler state.
    #[pyo3(signature = (job_id,))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn delete_job(&self, py: Python<'_>, job_id: i64) -> PyResult<()> {
        with_state_mut(py, &self.shared, |state, _deferred| {
            state.jobs.remove(&job_id);
        });
        Ok(())
    }

    /// Forces immediate execution of the given job.
    #[pyo3(signature = (job_id,))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn execute_job(&self, py: Python<'_>, job_id: i64) -> PyResult<()> {
        with_state_mut(py, &self.shared, |state, _deferred| {
            if let Some(running_job) = state.jobs.get_mut(&job_id) {
                let now = Utc::now();
                running_job.next_fire_utc = Some(now);
                running_job.sync_instant_from_utc_pub(now);
            }
        });
        Ok(())
    }

    /// Marks a job execution as complete, records the final outcome and duration,
    /// and catches up any interval fires that were missed while the job was in flight.
    /// When test data is enabled, also injects synthetic history records and drip-fed log entries.
    #[pyo3(signature = (job_id, outcome, duration_ms, current_run))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn mark_complete(&self, py: Python<'_>, job_id: i64, outcome: &str, duration_ms: u64, current_run: u32) -> PyResult<()> {
        let outcome_owned = outcome.to_string();
        log::info!("mark_complete: job_id={job_id} outcome={outcome_owned} run={current_run} duration_ms={duration_ms}");
        with_state_mut(py, &self.shared, |state, deferred| {
            let outcome = outcome_owned.as_str();
            if let Some(running_job) = state.jobs.get_mut(&job_id) {
                running_job.in_flight = false;
                running_job.in_flight_since = None;
                running_job.in_flight_run = None;

                let mut found_rec = false;
                for rec in running_job.history.iter_mut().rev() {
                    if rec.current_run == current_run {
                        rec.duration_ms = Some(duration_ms);
                        rec.outcome = outcome.to_string();
                        rec.log_entries.push(LogEntry {
                            timestamp_iso: Utc::now().to_rfc3339(),
                            level: "SYSTEM".into(),
                            message: format!("Job completed, outcome: {outcome}, duration: {}", humanize_ms(duration_ms)),
                        });
                        found_rec = true;
                        break;
                    }
                }
                if !found_rec {
                    deferred_log!(
                        deferred,
                        log::Level::Warn,
                        "mark_complete: job_id={job_id} name={} no history rec for run={current_run}",
                        running_job.name,
                    );
                }

                if running_job.interval_ms > 0 && duration_ms >= running_job.interval_ms {
                    let now = Utc::now();
                    while let Some(fire) = running_job.next_fire_utc {
                        if fire >= now {
                            break;
                        }
                        running_job.current_run += 1;
                        let skipped_run = running_job.current_run;
                        running_job.record_execution(
                            ExecutionRecord::new(
                                &fire.to_rfc3339(),
                                &now.to_rfc3339(),
                                types::outcome::SKIPPED_ALREADY_IN_FLIGHT,
                                skipped_run,
                            )
                            .with_outcome_ctx(current_run.to_string()),
                        );
                        running_job.advance_to_next(now);
                    }
                }

                if state.with_test_data {
                    for rec in running_job.history.iter_mut().rev() {
                        if rec.current_run == current_run {
                            populate_synthetic_logs(rec, &Utc::now().to_rfc3339(), outcome);
                            break;
                        }
                    }

                    let now_iso = Utc::now().to_rfc3339();
                    let now_inst = Instant::now();
                    let mut drip_base_ms: u64 = 0;

                    for _iter_idx in 0..2u8 {
                        let raw_idx = TEST_INJECT_IDX.fetch_add(1, Ordering::Relaxed);
                        let wrapped_idx = usize::try_from(raw_idx).map_or(0, |idx| idx % TEST_INJECT_OUTCOMES.len());
                        let fake_outcome = TEST_INJECT_OUTCOMES.get(wrapped_idx).copied().unwrap_or(types::outcome::ERROR);
                        let fake_duration = if fake_outcome == types::outcome::TIMEOUT { 32000 } else { 150 };
                        running_job.current_run += 1;
                        let run = running_job.current_run;

                        let mut rec = ExecutionRecord::new(&now_iso, &now_iso, types::outcome::RUNNING, run);
                        if fake_outcome == types::outcome::SKIPPED_ALREADY_IN_FLIGHT {
                            rec = rec.with_outcome_ctx(current_run.to_string());
                        }
                        running_job.record_execution(rec);

                        let drip_entries = build_synthetic_drip_entries(&now_iso, fake_outcome);
                        let drip_count = drip_entries.len();
                        for (drip_idx, entry) in drip_entries.into_iter().enumerate() {
                            let offset_ms = drip_base_ms + (u64::try_from(drip_idx).unwrap_or(0) + 1) * 5500;
                            let is_last = drip_idx == drip_count - 1;
                            state.synthetic_drips.push(std::cmp::Reverse(SyntheticDrip {
                                due_at: now_inst + Duration::from_millis(offset_ms),
                                job_id,
                                current_run: run,
                                entry,
                                finalize: if is_last {
                                    Some((fake_outcome.to_string(), fake_duration))
                                } else {
                                    None
                                },
                            }));
                        }
                        drip_base_ms += u64::try_from(drip_count).unwrap_or(0) * 5500;
                    }
                }
            }
        });
        Ok(())
    }

    /// Reloads all jobs from the ODB adapter.
    #[pyo3(signature = ())]
    fn reload(&self, py: Python<'_>) -> PyResult<()> {
        let adapter_bound = self.odb_adapter.bind(py);
        let (new_jobs, _cals) = scheduler::load_jobs(adapter_bound)?;
        with_state_mut(py, &self.shared, |state, _deferred| {
            reload_jobs(state, &new_jobs);
        });
        Ok(())
    }

    /// Returns a page of execution-history records for a single job.
    #[pyo3(signature = (job_id, offset, limit, outcomes))]
    #[expect(clippy::needless_pass_by_value, reason = "PyO3 requires owned Bound for extraction")]
    fn get_history_page(
        &self,
        py: Python<'_>,
        job_id: i64,
        offset: usize,
        limit: usize,
        outcomes: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyDict>> {
        let filter = parse_outcome_filter(&outcomes)?;

        let (records, total, job_name) = py.detach(|| {
            let state = self.shared.state.lock();
            state.jobs.get(&job_id).map_or_else(
                || (Vec::new(), 0, String::new()),
                |running_job| {
                    let name = running_job.name.clone();
                    let (page, total) = filter.as_ref().map_or_else(
                        || {
                            let total = running_job
                                .history
                                .iter()
                                .filter(|rec| rec.outcome != types::outcome::RUNNING)
                                .count();
                            let all_len = running_job.history.len();
                            let start = if offset >= all_len { all_len } else { all_len - offset };
                            let end = start.saturating_sub(limit);
                            let page: Vec<ExecutionRecord> = running_job.history.range(end..start).rev().cloned().collect();
                            (page, total)
                        },
                        |allowed| {
                            let mut total: usize = 0;
                            let mut page: Vec<ExecutionRecord> = Vec::with_capacity(limit);
                            let mut skipped: usize = 0;

                            for rec in running_job.history.iter().rev() {
                                if !allowed.iter().any(|allowed_val| allowed_val == &rec.outcome) {
                                    continue;
                                }
                                if rec.outcome != types::outcome::RUNNING {
                                    total += 1;
                                }
                                if page.len() < limit {
                                    if skipped < offset {
                                        skipped += 1;
                                    } else {
                                        page.push(rec.clone());
                                    }
                                }
                            }
                            (page, total)
                        },
                    );
                    (page, total, name)
                },
            )
        });

        history::records_page_to_py_dict(py, &records, total, job_id, &job_name)
    }

    /// Returns records added since a given ISO timestamp, optionally filtered by outcome.
    ///
    /// Also returns the total count for the given outcome filter so that the
    /// Python caller does not need a second round-trip for the total.
    #[pyo3(signature = (job_id, since_iso, outcomes, running_runs))]
    #[expect(clippy::needless_pass_by_value, reason = "PyO3 requires owned Bound and Vec for extraction")]
    fn get_history_since(
        &self,
        py: Python<'_>,
        job_id: i64,
        since_iso: &str,
        outcomes: Bound<'_, PyAny>,
        running_runs: Vec<u32>,
    ) -> PyResult<Py<PyDict>> {
        let filter = parse_outcome_filter(&outcomes)?;
        let since_owned = since_iso.to_string();

        let (records, total, job_name) = py.detach(|| {
            let state = self.shared.state.lock();
            state.jobs.get(&job_id).map_or_else(
                || (Vec::new(), 0, String::new()),
                |running_job| {
                    let name = running_job.name.clone();
                    let mut records: Vec<ExecutionRecord> = Vec::new();
                    let mut total: usize = 0;

                    for rec in &running_job.history {
                        let outcome_allowed = filter
                            .as_ref()
                            .is_none_or(|allowed| allowed.iter().any(|allowed_val| allowed_val == &rec.outcome));

                        if outcome_allowed && rec.outcome != types::outcome::RUNNING {
                            total += 1;
                        }

                        let run_override = running_runs.contains(&rec.current_run);
                        let is_since = rec.actual_fire_time_iso.as_str() >= since_owned.as_str() || run_override;
                        if is_since && (outcome_allowed || run_override) {
                            records.push(rec.clone());
                        }
                    }

                    records.reverse();
                    (records, total, name)
                },
            )
        });

        let out = PyDict::new(py);
        if records.is_empty() {
            out.set_item("rows", PyList::empty(py))?;
        } else {
            out.set_item("rows", history::records_to_py_list(py, &records, job_id, &job_name)?)?;
        }
        out.set_item("total", total)?;
        Ok(out.unbind())
    }

    /// Returns a single execution record by run number, plus adjacent run numbers for navigation.
    ///
    /// Uses the two-phase `py.detach` pattern: the state mutex is locked and the
    /// record is cloned into plain Rust data with the GIL released, then the
    /// Python dict is built after the mutex is dropped and the GIL is reacquired.
    #[pyo3(signature = (job_id, current_run))]
    fn get_run_detail(&self, py: Python<'_>, job_id: i64, current_run: u32) -> PyResult<Py<PyDict>> {
        let result = py.detach(|| {
            let state = self.shared.state.lock();
            state.jobs.get(&job_id).and_then(|running_job| {
                let mut prev_run: Option<u32> = None;
                let mut found: Option<ExecutionRecord> = None;
                let mut next_run: Option<u32> = None;

                for rec in &running_job.history {
                    if found.is_some() {
                        next_run = Some(rec.current_run);
                        break;
                    }
                    if rec.current_run == current_run {
                        found = Some(rec.clone());
                    } else {
                        prev_run = Some(rec.current_run);
                    }
                }

                found.map(|rec| (rec, running_job.name.clone(), prev_run, next_run))
            })
        });

        let out = PyDict::new(py);
        if let Some((rec, job_name, prev_run, next_run)) = result {
            out.set_item("record", history::record_to_py_dict(py, &rec, job_id, &job_name)?)?;
            match prev_run {
                Some(run) => out.set_item("prev_run", run)?,
                None => out.set_item("prev_run", py.None())?,
            }
            match next_run {
                Some(run) => out.set_item("next_run", run)?,
                None => out.set_item("next_run", py.None())?,
            }
        } else {
            out.set_item("record", py.None())?;
            out.set_item("prev_run", py.None())?;
            out.set_item("next_run", py.None())?;
        }
        Ok(out.unbind())
    }

    /// Returns a summary list of all jobs including history-derived fields.
    ///
    /// Each dict contains: `id`, `name`, `is_active`, `service`, `job_type`, `in_flight`,
    /// `current_run`, `interval_ms`, `next_fire_utc`, `last_outcome`, `last_duration_ms`,
    /// `recent_outcomes` (last 10), and per-job `outcome_counts`.
    #[pyo3(signature = ())]
    fn get_job_summaries(&self, py: Python<'_>) -> PyResult<Py<PyList>> {
        let summaries: Vec<job::JobSummary> = py.detach(|| {
            let state = self.shared.state.lock();
            state.jobs.values().map(job::RunningJob::summary).collect()
        });

        let countable = types::outcome::COUNTABLE;
        let list = PyList::empty(py);
        for summary in &summaries {
            let dict = PyDict::new(py);
            dict.set_item("id", summary.id)?;
            dict.set_item("name", summary.name.as_str())?;
            dict.set_item("is_active", summary.is_active)?;
            dict.set_item("service", summary.service.as_str())?;
            dict.set_item("job_type", summary.job_type.as_str())?;
            dict.set_item("in_flight", summary.in_flight)?;
            dict.set_item("current_run", summary.current_run)?;
            dict.set_item("interval_ms", summary.interval_ms)?;
            match &summary.next_fire_utc {
                Some(val) => dict.set_item("next_fire_utc", val.as_str())?,
                None => dict.set_item("next_fire_utc", py.None())?,
            }
            match &summary.last_outcome {
                Some(val) => dict.set_item("last_outcome", val.as_str())?,
                None => dict.set_item("last_outcome", py.None())?,
            }
            match summary.last_duration_ms {
                Some(val) => dict.set_item("last_duration_ms", val)?,
                None => dict.set_item("last_duration_ms", py.None())?,
            }

            let recent_outcomes = PyList::empty(py);
            for outcome in &summary.recent_outcomes {
                recent_outcomes.append(outcome.as_str())?;
            }
            dict.set_item("recent_outcomes", recent_outcomes)?;

            let outcome_counts = PyDict::new(py);
            for (label, count) in countable.iter().zip(&summary.outcome_counts) {
                outcome_counts.set_item(*label, *count)?;
            }
            dict.set_item("outcome_counts", outcome_counts)?;

            list.append(dict)?;
        }
        Ok(list.unbind())
    }

    /// Returns a lightweight timeline of execution events for the dashboard chart.
    ///
    /// Each dict contains: `outcome`, `actual_fire_time_iso`, `job_id`, `job_name`, `duration_ms`.
    /// Returns at most `max_events` records (default 1000), sorted by timestamp descending
    /// (most recent first) so the Python side does not need to re-sort.
    #[pyo3(signature = (max_events=1000))]
    fn get_timeline_events(&self, py: Python<'_>, max_events: usize) -> PyResult<Py<PyList>> {
        let events: Vec<job::TimelineEvent> = py.detach(|| {
            let state = self.shared.state.lock();
            let mut events: Vec<job::TimelineEvent> = Vec::new();
            for (job_id, running_job) in &state.jobs {
                for rec in &running_job.history {
                    events.push(job::TimelineEvent {
                        job_id: *job_id,
                        job_name: running_job.name.clone(),
                        record: rec.clone(),
                    });
                }
            }
            drop(state);
            events.sort_unstable_by(|lhs, rhs| rhs.record.actual_fire_time_iso.cmp(&lhs.record.actual_fire_time_iso));
            events.truncate(max_events);
            events
        });

        let list = PyList::empty(py);
        for event in &events {
            let rec = &event.record;
            let dict = PyDict::new(py);
            dict.set_item("outcome", rec.outcome.as_str())?;
            dict.set_item("actual_fire_time_iso", rec.actual_fire_time_iso.as_str())?;
            dict.set_item("job_id", event.job_id)?;
            dict.set_item("job_name", event.job_name.as_str())?;
            match rec.duration_ms {
                Some(duration) => dict.set_item("duration_ms", duration)?,
                None => dict.set_item("duration_ms", py.None())?,
            }
            match &rec.error {
                Some(error_text) => dict.set_item("error", error_text)?,
                None => dict.set_item("error", py.None())?,
            }
            match &rec.outcome_ctx {
                Some(outcome_ctx) => dict.set_item("outcome_ctx", outcome_ctx)?,
                None => dict.set_item("outcome_ctx", py.None())?,
            }
            dict.set_item("current_run", rec.current_run)?;
            dict.set_item("planned_fire_time_iso", rec.planned_fire_time_iso.as_str())?;
            list.append(dict)?;
        }
        Ok(list.unbind())
    }

    /// Appends a log entry to the execution record for a given job and run number.
    ///
    /// The `LogEntry` is built from the `&str` params before releasing the GIL,
    /// since those borrows are tied to the GIL lifetime.
    #[pyo3(signature = (job_id, current_run, timestamp_iso, level, message))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn append_log_entry(
        &self,
        py: Python<'_>,
        job_id: i64,
        current_run: u32,
        timestamp_iso: &str,
        level: &str,
        message: &str,
    ) -> PyResult<()> {
        let entry = LogEntry {
            timestamp_iso: timestamp_iso.to_string(),
            level: level.to_string(),
            message: message.to_string(),
        };
        py.detach(|| {
            let mut state = self.shared.state.lock();
            if let Some(running_job) = state.jobs.get_mut(&job_id) {
                for rec in running_job.history.iter_mut().rev() {
                    if rec.current_run == current_run {
                        rec.log_entries.push(entry);
                        break;
                    }
                }
            }
        });
        Ok(())
    }

    /// Returns log entries for a specific execution record.
    ///
    /// When `since_idx` is 0, returns all entries (initial panel expand).
    /// When it is greater than zero, returns only entries added after that index
    /// (incremental poll while the panel is open).
    #[pyo3(signature = (job_id, current_run, since_idx))]
    fn get_log_entries(&self, py: Python<'_>, job_id: i64, current_run: u32, since_idx: usize) -> PyResult<Py<PyList>> {
        let entries: Vec<LogEntry> = py.detach(|| {
            let state = self.shared.state.lock();
            state.jobs.get(&job_id).map_or_else(Vec::new, |running_job| {
                let mut found = Vec::new();
                for rec in running_job.history.iter().rev() {
                    if rec.current_run == current_run {
                        found = rec.log_entries.iter().skip(since_idx).cloned().collect();
                        break;
                    }
                }
                found
            })
        });

        let list = PyList::empty(py);
        for entry in &entries {
            let dict = PyDict::new(py);
            dict.set_item("timestamp_iso", entry.timestamp_iso.as_str())?;
            dict.set_item("level", entry.level.as_str())?;
            dict.set_item("message", entry.message.as_str())?;
            list.append(dict)?;
        }
        Ok(list.unbind())
    }
}

/// Reconciles the running-job map with a freshly loaded list of scheduler jobs.
pub fn reload_jobs(state: &mut scheduler::SchedulerState, new_jobs: &[crate::model::SchedulerJob]) {
    let new_ids: std::collections::HashSet<i64> = new_jobs.iter().map(|job| job.id).collect();
    let old_ids: std::collections::HashSet<i64> = state.jobs.keys().copied().collect();

    for removed_id in old_ids.difference(&new_ids) {
        state.jobs.remove(removed_id);
    }

    for scheduler_job in new_jobs {
        let job_id = scheduler_job.id;
        if let Some(existing) = state.jobs.get_mut(&job_id) {
            existing.update_from_job(scheduler_job);
        } else {
            let running_job = RunningJob::from_scheduler_job(scheduler_job);
            state.jobs.insert(job_id, running_job);
        }
    }
}

/// Replaces the calendar map in scheduler state with newly loaded calendars.
#[expect(clippy::implicit_hasher, reason = "callers always use the default hasher")]
pub fn reload_calendars(state: &mut scheduler::SchedulerState, new_cals: std::collections::HashMap<String, crate::model::HolidayCalendar>) {
    state.calendars.clear();
    for (name, cal) in new_cals {
        let mut calendar_data = CalendarData::new(name.clone());
        for date_str in &cal.dates {
            if let Ok(date) = chrono::NaiveDate::parse_from_str(date_str, "%Y-%m-%d") {
                calendar_data.dates.insert(date);
            }
        }
        calendar_data.weekdays.clone_from(&cal.weekdays);
        calendar_data.description.clone_from(&cal.description);
        state.calendars.insert(name, calendar_data);
    }
}

/// Parses the `outcomes` argument into an optional allow-list of outcome strings.
fn parse_outcome_filter(outcomes: &Bound<'_, PyAny>) -> PyResult<Option<Vec<String>>> {
    if let Ok(text) = outcomes.extract::<String>()
        && text == types::outcome::ALL
    {
        return Ok(None);
    }
    if let Ok(list) = outcomes.cast::<PyList>() {
        let mut items: Vec<String> = list.iter().map(|item| item.extract::<String>()).collect::<PyResult<_>>()?;
        if !items.iter().any(|val| val == types::outcome::RUNNING) {
            items.push(types::outcome::RUNNING.to_string());
        }
        return Ok(Some(items));
    }
    Ok(None)
}

/// Converts a Python dict into a `SchedulerJob` model.
///
/// # Errors
///
/// Returns a `PyErr` if a required key is missing or has the wrong type.
pub fn dict_to_scheduler_job(job_id: i64, dict: &Bound<'_, PyDict>) -> PyResult<crate::model::SchedulerJob> {
    /// Extracts a required string value from the dict.
    fn get_str(dict: &Bound<'_, PyDict>, key: &str) -> PyResult<String> {
        dict.get_item(key)?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_string()))?
            .extract::<String>()
    }

    /// Extracts an optional non-empty string from the dict.
    fn get_opt_str(dict: &Bound<'_, PyDict>, key: &str) -> Option<String> {
        dict.get_item(key)
            .ok()
            .flatten()
            .and_then(|val| val.extract::<String>().ok())
            .filter(|text| !text.is_empty())
    }

    /// Extracts an optional u32 from the dict.
    fn get_opt_u32(dict: &Bound<'_, PyDict>, key: &str) -> Option<u32> {
        dict.get_item(key).ok().flatten().and_then(|val| val.extract::<u32>().ok())
    }

    /// Extracts an optional u64 from the dict.
    fn get_opt_u64(dict: &Bound<'_, PyDict>, key: &str) -> Option<u64> {
        dict.get_item(key).ok().flatten().and_then(|val| val.extract::<u64>().ok())
    }

    /// Extracts a required bool from the dict.
    fn get_bool(dict: &Bound<'_, PyDict>, key: &str) -> PyResult<bool> {
        dict.get_item(key)?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_string()))?
            .extract::<bool>()
    }

    Ok(crate::model::SchedulerJob {
        id: job_id,
        name: get_str(dict, "name")?,
        is_active: get_bool(dict, "is_active")?,
        service: get_str(dict, "service")?,
        job_type: get_str(dict, "job_type")?,
        start_date: get_str(dict, "start_date")?,
        extra: get_opt_str(dict, "extra"),
        weeks: get_opt_u32(dict, "weeks"),
        days: get_opt_u32(dict, "days"),
        hours: get_opt_u32(dict, "hours"),
        minutes: get_opt_u32(dict, "minutes"),
        seconds: get_opt_u32(dict, "seconds"),
        repeats: get_opt_u32(dict, "repeats").filter(|&val| val > 0),
        jitter_ms: get_opt_u32(dict, "jitter_ms"),
        timezone: get_opt_str(dict, "timezone"),
        calendar: get_opt_str(dict, "calendar"),
        max_execution_time_ms: get_opt_u64(dict, "max_execution_time_ms"),
    })
}

/// `PyO3` module entry point - registers the `Scheduler` class.
#[pymodule]
fn zato_scheduler_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();
    module.add_class::<Scheduler>()?;
    Ok(())
}
