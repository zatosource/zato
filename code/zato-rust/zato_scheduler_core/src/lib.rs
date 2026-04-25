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

/// Acquires the state lock, applies `func`, marks the state dirty and wakes the condvar.
fn with_state_mut<F, R>(shared: &SchedulerShared, func: F) -> R
where
    F: FnOnce(&mut scheduler::SchedulerState) -> R,
{
    let mut state = shared.state.lock();
    let result = func(&mut state);
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    result
}

/// Formats a duration in milliseconds into a human-readable string.
fn humanize_ms(millis: u64) -> String {
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
}

#[pymethods]
impl Scheduler {
    /// Creates a new scheduler instance with no background thread running.
    #[new]
    fn new(py: Python<'_>) -> Self {
        Self {
            shared: Arc::new(SchedulerShared::new()),
            odb_adapter: py.None(),
            thread_handle: parking_lot::Mutex::new(None),
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

        {
            let mut state = self.shared.state.lock();
            state.with_test_data = with_test_data;
        }

        self.odb_adapter = odb_adapter.clone_ref(py);
        let adapter = odb_adapter.clone_ref(py);
        let shared = Arc::clone(&self.shared);

        let handle = std::thread::Builder::new()
            .name("zato-scheduler".into())
            .spawn(move || {
                let callbacks = scheduler::SchedulerCallbacks {
                    run_cb,
                    spawn_fn,
                    on_job_executed_cb,
                };
                scheduler::scheduler_loop(shared, adapter, callbacks, initial_sleep_time);
            })
            .map_err(|err| pyo3::exceptions::PyException::new_err(format!("spawn failed: {err}")))?;

        *self.thread_handle.lock() = Some(handle);

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
    fn create_job(&self, _py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
        let scheduler_job = dict_to_scheduler_job(job_id, job_data)?;
        let running_job = RunningJob::from_scheduler_job(&scheduler_job);
        with_state_mut(&self.shared, |state| {
            state.jobs.insert(job_id, running_job);
        });
        Ok(())
    }

    /// Edits an existing job or inserts a new one if not found.
    #[pyo3(signature = (job_id, job_data))]
    fn edit_job(&self, _py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
        let scheduler_job = dict_to_scheduler_job(job_id, job_data)?;
        with_state_mut(&self.shared, |state| {
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
    fn delete_job(&self, job_id: i64) -> PyResult<()> {
        with_state_mut(&self.shared, |state| {
            state.jobs.remove(&job_id);
        });
        Ok(())
    }

    /// Forces immediate execution of the given job.
    #[pyo3(signature = (job_id,))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn execute_job(&self, job_id: i64) -> PyResult<()> {
        with_state_mut(&self.shared, |state| {
            if let Some(running_job) = state.jobs.get_mut(&job_id) {
                let now = Utc::now();
                running_job.next_fire_utc = Some(now);
                running_job.sync_instant_from_utc_pub(now);
            }
        });
        Ok(())
    }

    /// Marks a job execution as complete, optionally injecting synthetic test records.
    #[pyo3(signature = (job_id, outcome, duration_ms, current_run))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    fn mark_complete(&self, job_id: i64, outcome: &str, duration_ms: u64, current_run: u32) -> PyResult<()> {
        log::info!("mark_complete called: job_id={job_id} outcome={outcome} current_run={current_run}");
        with_state_mut(&self.shared, |state| {
            if let Some(running_job) = state.jobs.get_mut(&job_id) {
                running_job.in_flight = false;
                running_job.in_flight_since = None;
                running_job.in_flight_run = None;
                for rec in running_job.history.iter_mut().rev() {
                    if rec.current_run == current_run {
                        rec.duration_ms = Some(duration_ms);
                        rec.outcome = outcome.to_string();
                        rec.log_entries.push(LogEntry {
                            timestamp_iso: Utc::now().to_rfc3339(),
                            level: "SYSTEM".into(),
                            message: format!("Job completed, outcome: {outcome}, duration: {}", humanize_ms(duration_ms)),
                        });
                        break;
                    }
                }

                if state.with_test_data {
                    for rec in running_job.history.iter_mut().rev() {
                        if rec.current_run == current_run {
                            populate_synthetic_logs(rec, &Utc::now().to_rfc3339(), outcome);
                            log::info!("Populated real rec run={current_run} with {} log entries", rec.log_entries.len());
                            break;
                        }
                    }

                    let now_iso = Utc::now().to_rfc3339();
                    let now_inst = Instant::now();
                    let mut drip_base_ms: u64 = 0;

                    for iter_idx in 0..2u8 {
                        let raw_idx = TEST_INJECT_IDX.fetch_add(1, Ordering::Relaxed);
                        let wrapped_idx = usize::try_from(raw_idx).map_or(0, |idx| idx % TEST_INJECT_OUTCOMES.len());
                        let fake_outcome = TEST_INJECT_OUTCOMES.get(wrapped_idx).copied().unwrap_or(types::outcome::ERROR);
                        let fake_duration = if fake_outcome == types::outcome::TIMEOUT { 32000 } else { 150 };
                        running_job.current_run += 1;
                        let run = running_job.current_run;

                        log::info!("Creating synthetic running rec iter={iter_idx} run={run} fake_outcome={fake_outcome}");

                        let mut rec = ExecutionRecord::new(&now_iso, &now_iso, types::outcome::RUNNING, run);
                        if fake_outcome == types::outcome::SKIPPED_ALREADY_IN_FLIGHT {
                            rec = rec.with_outcome_ctx(current_run.to_string());
                        }
                        running_job.record_execution(rec);

                        let drip_entries = build_synthetic_drip_entries(&now_iso, fake_outcome);
                        let drip_count = drip_entries.len();
                        log::info!("Queuing {drip_count} drips for run={run}, drip_base_ms={drip_base_ms}");
                        for (drip_idx, entry) in drip_entries.into_iter().enumerate() {
                            let offset_ms = drip_base_ms + (u64::try_from(drip_idx).unwrap_or(0) + 1) * 5500;
                            let is_last = drip_idx == drip_count - 1;
                            log::info!(
                                "  drip {drip_idx}/{drip_count} offset_ms={offset_ms} level={} finalize={} due_at=now+{offset_ms}ms",
                                entry.level,
                                is_last
                            );
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
                    log::info!("Total drips queued: {}", state.synthetic_drips.len());
                }
            } else {
                log::info!("mark_complete: job_id={job_id} not found in state");
            }
        });
        Ok(())
    }

    /// Reloads all jobs from the ODB adapter.
    #[pyo3(signature = ())]
    fn reload(&self, py: Python<'_>) -> PyResult<()> {
        let adapter_bound = self.odb_adapter.bind(py);
        let (new_jobs, _cals) = scheduler::load_jobs(adapter_bound)?;
        with_state_mut(&self.shared, |state| {
            reload_jobs(state, &new_jobs);
        });
        Ok(())
    }

    /// Returns a page of execution-history records for a single job.
    #[pyo3(signature = (job_id, offset, limit, outcomes))]
    #[expect(clippy::needless_pass_by_value, reason = "PyO3 requires owned Bound for extraction")]
    #[expect(
        clippy::too_many_arguments,
        reason = "PyO3 method with 4 Python-visible args called from multiple files"
    )]
    fn get_history_page(
        &self,
        py: Python<'_>,
        job_id: i64,
        offset: usize,
        limit: usize,
        outcomes: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyDict>> {
        let state = self.shared.state.lock();
        if let Some(running_job) = state.jobs.get(&job_id) {
            let filter = parse_outcome_filter(&outcomes)?;
            filter.map_or_else(
                || {
                    let total = running_job
                        .history
                        .iter()
                        .filter(|rec| rec.outcome != types::outcome::RUNNING)
                        .count();
                    let all_len = running_job.history.len();
                    let start = if offset >= all_len { all_len } else { all_len - offset };
                    let end = start.saturating_sub(limit);
                    let slice: Vec<&ExecutionRecord> = running_job.history.range(end..start).rev().collect();
                    history::records_page_to_py_dict(py, &slice, total)
                },
                |allowed| {
                    let mut total: usize = 0;
                    let mut page: Vec<&ExecutionRecord> = Vec::with_capacity(limit);
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
                                page.push(rec);
                            }
                        }
                    }
                    history::records_page_to_py_dict(py, &page, total)
                },
            )
        } else {
            history::records_page_to_py_dict(py, &[], 0)
        }
    }

    /// Returns records added since a given ISO timestamp, optionally filtered by outcome.
    ///
    /// Also returns the total count for the given outcome filter so that the
    /// Python caller does not need a second round-trip for the total.
    #[pyo3(signature = (job_id, since_iso, outcomes, running_runs))]
    #[expect(clippy::needless_pass_by_value, reason = "PyO3 requires owned Bound and Vec for extraction")]
    #[expect(
        clippy::too_many_arguments,
        reason = "PyO3 method with 4 Python-visible args called from multiple files"
    )]
    fn get_history_since(
        &self,
        py: Python<'_>,
        job_id: i64,
        since_iso: &str,
        outcomes: Bound<'_, PyAny>,
        running_runs: Vec<u32>,
    ) -> PyResult<Py<PyDict>> {
        let state = self.shared.state.lock();
        if let Some(running_job) = state.jobs.get(&job_id) {
            let filter = parse_outcome_filter(&outcomes)?;
            let mut records: Vec<&ExecutionRecord> = Vec::new();
            let mut total: usize = 0;

            for rec in &running_job.history {
                let outcome_allowed = filter
                    .as_ref()
                    .is_none_or(|allowed| allowed.iter().any(|allowed_val| allowed_val == &rec.outcome));

                if outcome_allowed && rec.outcome != types::outcome::RUNNING {
                    total += 1;
                }

                let run_override = running_runs.contains(&rec.current_run);
                let is_since = rec.actual_fire_time_iso.as_str() >= since_iso || run_override;
                if is_since && (outcome_allowed || run_override) {
                    records.push(rec);
                }
            }

            records.reverse();

            let out = PyDict::new(py);
            out.set_item("rows", history::records_to_py_list(py, &records)?)?;
            out.set_item("total", total)?;
            Ok(out.unbind())
        } else {
            let out = PyDict::new(py);
            out.set_item("rows", PyList::empty(py))?;
            out.set_item("total", 0)?;
            Ok(out.unbind())
        }
    }

    /// Returns a summary list of all jobs including history-derived fields.
    ///
    /// Each dict contains: `id`, `name`, `is_active`, `service`, `job_type`, `in_flight`,
    /// `current_run`, `interval_ms`, `next_fire_utc`, `last_outcome`, `last_duration_ms`,
    /// `recent_outcomes` (last 10), and per-job `outcome_counts`.
    #[pyo3(signature = ())]
    fn get_job_summaries(&self, py: Python<'_>) -> PyResult<Py<PyList>> {
        let state = self.shared.state.lock();
        let list = PyList::empty(py);
        for (job_id, running_job) in &state.jobs {
            let dict = PyDict::new(py);
            dict.set_item("id", *job_id)?;
            dict.set_item("name", running_job.name.as_str())?;
            dict.set_item("is_active", running_job.is_active)?;
            dict.set_item("service", running_job.service.as_ref())?;
            dict.set_item("job_type", running_job.job_type.as_str())?;
            dict.set_item("in_flight", running_job.in_flight)?;
            dict.set_item("current_run", running_job.current_run)?;
            dict.set_item("interval_ms", running_job.interval_ms)?;
            match running_job.next_fire_utc {
                Some(fire_dt) => dict.set_item("next_fire_utc", fire_dt.to_rfc3339())?,
                None => dict.set_item("next_fire_utc", py.None())?,
            }

            let history = &running_job.history;

            let last_outcome = history.back().map(|rec| rec.outcome.as_str());
            match last_outcome {
                Some(val) => dict.set_item("last_outcome", val)?,
                None => dict.set_item("last_outcome", py.None())?,
            }

            let last_duration_ms = history.iter().rev().find_map(|rec| rec.duration_ms);
            match last_duration_ms {
                Some(val) => dict.set_item("last_duration_ms", val)?,
                None => dict.set_item("last_duration_ms", py.None())?,
            }

            let recent_start = history.len().saturating_sub(10);
            let recent_outcomes = PyList::empty(py);
            for rec in history.range(recent_start..) {
                recent_outcomes.append(rec.outcome.as_str())?;
            }
            dict.set_item("recent_outcomes", recent_outcomes)?;

            let outcome_counts = PyDict::new(py);
            let countable = types::outcome::COUNTABLE;
            let mut counts = vec![0usize; countable.len()];
            for rec in history {
                if let Some(pos) = countable.iter().position(|label| *label == rec.outcome)
                    && let Some(slot) = counts.get_mut(pos)
                {
                    *slot += 1;
                }
            }
            for (label, count) in countable.iter().zip(&counts) {
                outcome_counts.set_item(*label, *count)?;
            }
            dict.set_item("outcome_counts", outcome_counts)?;

            list.append(dict)?;
        }
        drop(state);
        Ok(list.unbind())
    }

    /// Returns a lightweight timeline of execution events for the dashboard chart.
    ///
    /// Each dict contains: `outcome`, `actual_fire_time_iso`, `job_id`, `job_name`, `duration_ms`.
    /// Returns at most `max_events` records (default 1000), sorted by timestamp descending
    /// (most recent first) so the Python side does not need to re-sort.
    #[pyo3(signature = (max_events=1000))]
    fn get_timeline_events(&self, py: Python<'_>, max_events: usize) -> PyResult<Py<PyList>> {
        let state = self.shared.state.lock();

        let mut refs: Vec<(i64, &str, &ExecutionRecord)> = Vec::new();
        for (job_id, running_job) in &state.jobs {
            for rec in &running_job.history {
                refs.push((*job_id, running_job.name.as_str(), rec));
            }
        }

        refs.sort_unstable_by(|lhs, rhs| rhs.2.actual_fire_time_iso.cmp(&lhs.2.actual_fire_time_iso));
        refs.truncate(max_events);

        let list = PyList::empty(py);
        for (job_id, job_name, rec) in &refs {
            let dict = PyDict::new(py);
            dict.set_item("outcome", rec.outcome.as_str())?;
            dict.set_item("actual_fire_time_iso", rec.actual_fire_time_iso.as_str())?;
            dict.set_item("job_id", *job_id)?;
            dict.set_item("job_name", *job_name)?;
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
        drop(state);
        Ok(list.unbind())
    }

    /// Appends a log entry to the execution record for a given job and run number.
    #[pyo3(signature = (job_id, current_run, timestamp_iso, level, message))]
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 method protocol requires PyResult return")]
    #[expect(
        clippy::too_many_arguments,
        reason = "PyO3 method with 5 Python-visible args called from Python log handler"
    )]
    fn append_log_entry(&self, job_id: i64, current_run: u32, timestamp_iso: &str, level: &str, message: &str) -> PyResult<()> {
        let mut state = self.shared.state.lock();
        if let Some(running_job) = state.jobs.get_mut(&job_id) {
            for rec in running_job.history.iter_mut().rev() {
                if rec.current_run == current_run {
                    rec.log_entries.push(LogEntry {
                        timestamp_iso: timestamp_iso.to_string(),
                        level: level.to_string(),
                        message: message.to_string(),
                    });
                    break;
                }
            }
        }
        drop(state);
        Ok(())
    }

    /// Returns log entries for a specific execution record.
    ///
    /// When `since_idx` is 0, returns all entries (initial panel expand).
    /// When it is greater than zero, returns only entries added after that index
    /// (incremental poll while the panel is open).
    #[pyo3(signature = (job_id, current_run, since_idx))]
    fn get_log_entries(&self, py: Python<'_>, job_id: i64, current_run: u32, since_idx: usize) -> PyResult<Py<PyList>> {
        log::info!("get_log_entries: job_id={job_id} current_run={current_run} since_idx={since_idx}");
        let state = self.shared.state.lock();
        let list = PyList::empty(py);
        if let Some(running_job) = state.jobs.get(&job_id) {
            for rec in running_job.history.iter().rev() {
                if rec.current_run == current_run {
                    for entry in rec.log_entries.iter().skip(since_idx) {
                        let dict = PyDict::new(py);
                        dict.set_item("timestamp_iso", entry.timestamp_iso.as_str())?;
                        dict.set_item("level", entry.level.as_str())?;
                        dict.set_item("message", entry.message.as_str())?;
                        list.append(dict)?;
                    }
                    break;
                }
            }
        }
        drop(state);
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
        repeats: get_opt_u32(dict, "repeats"),
        jitter_ms: get_opt_u32(dict, "jitter_ms"),
        timezone: get_opt_str(dict, "timezone"),
        calendar: get_opt_str(dict, "calendar"),
        on_missed: get_opt_str(dict, "on_missed"),
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
