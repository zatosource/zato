//! Core scheduler crate for Zato - re-exports submodules and provides the `PyO3` entry points.

use std::sync::Arc;
use std::sync::atomic::{AtomicU32, Ordering};
use std::time::Duration;

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Calendar holiday support.
pub mod calendar;

/// Execution-history serialisation helpers.
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
    pub use crate::reload_jobs;
    pub use crate::reload_calendars;
}

use calendar::CalendarData;
use job::{ExecutionRecord, RunningJob};
use scheduler::SchedulerShared;

/// Convenience alias so the rest of the module can say `PyObject`.
type PyObject = Py<PyAny>;

/// Lazily-initialised reference to the shared scheduler core.
static SHARED: std::sync::OnceLock<Arc<SchedulerShared>> = std::sync::OnceLock::new();

/// Lazily-initialised reference to the Python ODB adapter.
static ODB_ADAPTER: std::sync::OnceLock<PyObject> = std::sync::OnceLock::new();

/// Handle for the background scheduler thread.
static THREAD_HANDLE: parking_lot::Mutex<Option<std::thread::JoinHandle<()>>> =
    parking_lot::Mutex::new(None);

/// Returns a reference to the shared scheduler state, or a Python error if not yet started.
fn get_shared() -> PyResult<&'static Arc<SchedulerShared>> {
    SHARED.get().ok_or_else(|| {
        pyo3::exceptions::PyException::new_err("scheduler not started")
    })
}

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

/// Starts the scheduler background thread.
#[pyfunction]
#[pyo3(signature = (odb_adapter, run_cb, spawn_fn, on_job_executed_cb, initial_sleep_time))]
#[expect(clippy::needless_pass_by_value, reason = "PyO3 requires by-value arguments for #[pyfunction]")]
fn scheduler_start(
    py: Python<'_>,
    odb_adapter: PyObject,
    run_cb: PyObject,
    spawn_fn: PyObject,
    on_job_executed_cb: PyObject,
    initial_sleep_time: f64,
) -> PyResult<()> {
    let shared = Arc::new(SchedulerShared::new());
    let _ = SHARED.set(Arc::clone(&shared));
    let _ = ODB_ADAPTER.set(odb_adapter.clone_ref(py));

    let adapter = odb_adapter.clone_ref(py);

    let handle = std::thread::Builder::new()
        .name("zato-scheduler".into())
        .spawn(move || {
            scheduler::scheduler_loop(shared, adapter, run_cb, spawn_fn, on_job_executed_cb, initial_sleep_time);
        })
        .map_err(|err| pyo3::exceptions::PyException::new_err(format!("spawn failed: {err}")))?;

    {
        let mut guard = THREAD_HANDLE.lock();
        *guard = Some(handle);
    }

    Ok(())
}

/// Requests a graceful stop and waits up to `timeout_s` seconds.
#[pyfunction]
#[pyo3(signature = (timeout_s,))]
fn scheduler_stop(timeout_s: f64) -> PyResult<()> {
    let shared = get_shared()?;
    shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
    shared.condvar.notify_all();

    let handle = THREAD_HANDLE.lock().take();
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
#[pyfunction]
#[pyo3(signature = (job_id, job_data))]
fn scheduler_create_job(_py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
    let shared = get_shared()?;
    let scheduler_job = dict_to_scheduler_job(job_id, job_data)?;
    let running_job = RunningJob::from_scheduler_job(&scheduler_job);
    with_state_mut(shared, |state| {
        state.jobs.insert(job_id, running_job);
    });
    Ok(())
}

/// Edits an existing job or inserts a new one if not found.
#[pyfunction]
#[pyo3(signature = (job_id, job_data))]
fn scheduler_edit_job(_py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
    let shared = get_shared()?;
    let scheduler_job = dict_to_scheduler_job(job_id, job_data)?;
    with_state_mut(shared, |state| {
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
#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_delete_job(job_id: i64) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        state.jobs.remove(&job_id);
    });
    Ok(())
}

/// Forces immediate execution of the given job.
#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_execute_job(job_id: i64) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        if let Some(running_job) = state.jobs.get_mut(&job_id) {
            running_job.next_fire_utc = Some(Utc::now());
            running_job.sync_instant_from_utc_pub(Utc::now());
        }
    });
    Ok(())
}

/// Non-OK outcomes injected after each real completion during testing.
const TEST_INJECT_OUTCOMES: &[&str] = &[
    "error",
    types::outcome::TIMEOUT,
    types::outcome::SKIPPED_ALREADY_IN_FLIGHT,
    "error",
    types::outcome::TIMEOUT,
    "error",
];

/// Monotonically increasing index into `TEST_INJECT_OUTCOMES`.
static TEST_INJECT_IDX: AtomicU32 = AtomicU32::new(0);

/// Marks a job execution as complete and injects synthetic test records.
#[pyfunction]
#[pyo3(signature = (job_id, outcome, duration_ms, current_run))]
fn scheduler_mark_complete(job_id: i64, outcome: &str, duration_ms: u64, current_run: u32) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        if let Some(running_job) = state.jobs.get_mut(&job_id) {
            running_job.in_flight = false;
            running_job.in_flight_since = None;
            running_job.in_flight_run = None;
            for rec in running_job.history.iter_mut().rev() {
                if rec.current_run == current_run {
                    rec.duration_ms = Some(duration_ms);
                    rec.outcome = outcome.to_string();
                    break;
                }
            }

            let now_iso = Utc::now().to_rfc3339();
            for _ in 0..2 {
                let raw_idx = TEST_INJECT_IDX.fetch_add(1, Ordering::Relaxed);
                let wrapped_idx = usize::try_from(raw_idx).map_or(0, |idx| idx % TEST_INJECT_OUTCOMES.len());
                let fake_outcome = TEST_INJECT_OUTCOMES.get(wrapped_idx).copied().unwrap_or("error");
                let fake_duration = if fake_outcome == types::outcome::TIMEOUT { 32000 } else { 150 };
                running_job.current_run += 1;
                let mut rec = ExecutionRecord::new(&now_iso, &now_iso, fake_outcome, running_job.current_run)
                    .with_duration(fake_duration)
                    .with_error(format!("TEST: synthetic {fake_outcome}"));
                if fake_outcome == types::outcome::SKIPPED_ALREADY_IN_FLIGHT {
                    rec = rec.with_outcome_ctx(current_run.to_string());
                }
                running_job.record_execution(rec);
            }
        }
    });
    Ok(())
}

/// Reloads all jobs from the ODB adapter.
#[pyfunction]
#[pyo3(signature = ())]
fn scheduler_reload() -> PyResult<()> {
    let shared = get_shared()?;
    let adapter = ODB_ADAPTER.get().ok_or_else(|| {
        pyo3::exceptions::PyException::new_err("scheduler not started")
    })?;

    Python::try_attach(|py| {
        let adapter_bound = adapter.bind(py);
        let (new_jobs, _cals) = scheduler::load_jobs(adapter_bound)?;
        with_state_mut(shared, |state| {
            reload_jobs(state, &new_jobs);
        });
        Ok::<_, PyErr>(())
    }).ok_or_else(|| pyo3::exceptions::PyException::new_err("GIL not available"))??;

    Ok(())
}

/// Reconciles the running-job map with a freshly loaded list of scheduler jobs.
pub fn reload_jobs(
    state: &mut scheduler::SchedulerState,
    new_jobs: &[crate::model::SchedulerJob],
) {
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
pub fn reload_calendars(
    state: &mut scheduler::SchedulerState,
    new_cals: std::collections::HashMap<String, crate::model::HolidayCalendar>,
) {
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

/// Returns the full execution history for a single job as a Python list.
#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_get_history(py: Python<'_>, job_id: i64) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock();
    state.jobs.get(&job_id).map_or_else(
        || Ok(PyList::empty(py).unbind()),
        |running_job| {
            let records: Vec<ExecutionRecord> = running_job.history.iter().cloned().collect();
            history::records_to_py_list(py, &records)
        },
    )
}

/// Parses the `outcomes` argument into an optional allow-list of outcome strings.
fn parse_outcome_filter(outcomes: &Bound<'_, PyAny>) -> PyResult<Option<Vec<String>>> {
    if let Ok(text) = outcomes.extract::<String>()
        && text == types::outcome::ALL {
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

/// Returns a page of execution-history records for a single job.
#[pyfunction]
#[pyo3(signature = (job_id, offset, limit, outcomes))]
#[expect(clippy::needless_pass_by_value, reason = "PyO3 requires owned Bound for extraction")]
fn scheduler_get_history_page(py: Python<'_>, job_id: i64, offset: usize, limit: usize, outcomes: Bound<'_, PyAny>) -> PyResult<Py<PyDict>> {
    let shared = get_shared()?;
    let state = shared.state.lock();
    if let Some(running_job) = state.jobs.get(&job_id) {
        let filter = parse_outcome_filter(&outcomes)?;
        filter.map_or_else(
            || {
                let total = running_job.history.iter().filter(|rec| rec.outcome != types::outcome::RUNNING).count();
                let all_len = running_job.history.len();
                let start = if offset >= all_len { all_len } else { all_len - offset };
                let end = start.saturating_sub(limit);
                let slice: Vec<ExecutionRecord> = running_job.history.range(end..start).rev().cloned().collect();
                history::records_page_to_py_dict(py, &slice, total)
            },
            |allowed| {
                let filtered: Vec<ExecutionRecord> = running_job.history.iter()
                    .filter(|rec| allowed.iter().any(|allowed_val| allowed_val == &rec.outcome))
                    .cloned()
                    .collect();
                let total = filtered.iter().filter(|rec| rec.outcome != types::outcome::RUNNING).count();
                let start = if offset >= filtered.len() { filtered.len() } else { filtered.len() - offset };
                let end = start.saturating_sub(limit);
                let slice: Vec<ExecutionRecord> = filtered.get(end..start)
                    .unwrap_or(&[])
                    .iter()
                    .rev()
                    .cloned()
                    .collect();
                history::records_page_to_py_dict(py, &slice, total)
            },
        )
    } else {
        history::records_page_to_py_dict(py, &[], 0)
    }
}

/// Returns records added since a given ISO timestamp, optionally filtered by outcome.
#[pyfunction]
#[pyo3(signature = (job_id, since_iso, outcomes, running_runs))]
#[expect(clippy::needless_pass_by_value, reason = "PyO3 requires owned Bound and Vec for extraction")]
fn scheduler_get_history_since(py: Python<'_>, job_id: i64, since_iso: &str, outcomes: Bound<'_, PyAny>, running_runs: Vec<u32>) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock();
    if let Some(running_job) = state.jobs.get(&job_id) {
        let filter = parse_outcome_filter(&outcomes)?;
        let records: Vec<ExecutionRecord> = running_job.history.iter()
            .filter(|rec| rec.actual_fire_time_iso.as_str() >= since_iso
                || running_runs.contains(&rec.current_run))
            .filter(|rec| filter.as_ref().is_none_or(|allowed|
                allowed.iter().any(|allowed_val| allowed_val == &rec.outcome)
                    || running_runs.contains(&rec.current_run)))
            .rev()
            .cloned()
            .collect();
        history::records_to_py_list(py, &records)
    } else {
        Ok(PyList::empty(py).unbind())
    }
}

/// Returns the full execution history for every job, keyed by job id.
#[pyfunction]
#[pyo3(signature = ())]
fn scheduler_get_all_history(py: Python<'_>) -> PyResult<Py<PyDict>> {
    let shared = get_shared()?;
    let state = shared.state.lock();
    history::all_history_to_py_dict(py, &state.jobs)
}

/// Returns a summary list of all jobs (id, name, active, service, etc.).
#[pyfunction]
#[pyo3(signature = ())]
fn scheduler_get_job_summaries(py: Python<'_>) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock();
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
        list.append(dict)?;
    }
    drop(state);
    Ok(list.unbind())
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
        dict.get_item(key).ok().flatten().and_then(|val| val.extract::<String>().ok()).filter(|text| !text.is_empty())
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

/// `PyO3` module entry point - registers all scheduler functions.
#[pymodule]
fn zato_scheduler_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();
    module.add_function(wrap_pyfunction!(scheduler_start, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_stop, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_create_job, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_edit_job, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_delete_job, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_execute_job, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_mark_complete, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_reload, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_get_history, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_get_history_page, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_get_history_since, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_get_all_history, module)?)?;
    module.add_function(wrap_pyfunction!(scheduler_get_job_summaries, module)?)?;
    Ok(())
}
