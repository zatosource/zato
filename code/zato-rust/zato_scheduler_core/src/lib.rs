use std::sync::Arc;
use std::sync::atomic::{AtomicU32, Ordering};
use std::time::Duration;

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

pub mod calendar;
pub mod history;
pub mod job;
pub mod scheduler;
pub mod types;

#[doc(hidden)]
pub mod test_support {
    pub use crate::job::clamp_max_execution_time;
    pub use crate::reload_jobs;
    pub use crate::reload_calendars;
}

use calendar::CalendarData;
use job::{ExecutionRecord, RunningJob};
use scheduler::SchedulerShared;

type PyObject = Py<PyAny>;

static SHARED: std::sync::OnceLock<Arc<SchedulerShared>> = std::sync::OnceLock::new();
static ODB_ADAPTER: std::sync::OnceLock<PyObject> = std::sync::OnceLock::new();
static THREAD_HANDLE: std::sync::Mutex<Option<std::thread::JoinHandle<()>>> = std::sync::Mutex::new(None);

fn get_shared() -> PyResult<&'static Arc<SchedulerShared>> {
    SHARED.get().ok_or_else(|| {
        pyo3::exceptions::PyException::new_err("scheduler not started")
    })
}

fn with_state_mut<F, R>(shared: &SchedulerShared, f: F) -> R
where
    F: FnOnce(&mut scheduler::SchedulerState) -> R,
{
    let mut state = shared.state.lock().unwrap();
    let result = f(&mut state);
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    result
}

#[pyfunction]
#[pyo3(signature = (odb_adapter, run_cb, spawn_fn, on_job_executed_cb, initial_sleep_time))]
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
        .map_err(|e| pyo3::exceptions::PyException::new_err(format!("spawn failed: {e}")))?;

    if let Ok(mut guard) = THREAD_HANDLE.lock() {
        *guard = Some(handle);
    }

    Ok(())
}

#[pyfunction]
#[pyo3(signature = (timeout_s,))]
fn scheduler_stop(timeout_s: f64) -> PyResult<()> {
    let shared = get_shared()?;
    shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
    shared.condvar.notify_all();

    let handle = THREAD_HANDLE.lock().unwrap().take();
    if let Some(h) = handle {
        let deadline = std::time::Instant::now() + Duration::from_secs_f64(timeout_s.min(30.0));
        while !h.is_finished() {
            let remaining = deadline.saturating_duration_since(std::time::Instant::now());
            if remaining.is_zero() {
                break;
            }
            std::thread::sleep(remaining.min(Duration::from_millis(50)));
        }
    }
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id, job_data))]
fn scheduler_create_job(_py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
    let shared = get_shared()?;
    let sj = dict_to_scheduler_job(job_id, job_data)?;
    let running_job = RunningJob::from_scheduler_job(&sj);
    with_state_mut(shared, |state| {
        state.jobs.insert(job_id, running_job);
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id, job_data))]
fn scheduler_edit_job(_py: Python<'_>, job_id: i64, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
    let shared = get_shared()?;
    let sj = dict_to_scheduler_job(job_id, job_data)?;
    with_state_mut(shared, |state| {
        if let Some(existing) = state.jobs.get_mut(&job_id) {
            existing.update_from_job(&sj);
        } else {
            let running_job = RunningJob::from_scheduler_job(&sj);
            state.jobs.insert(job_id, running_job);
        }
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_delete_job(job_id: i64) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        state.jobs.remove(&job_id);
    });
    Ok(())
}

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

// TEST: non-OK outcomes to inject after each real completion
const TEST_INJECT_OUTCOMES: &[&str] = &[
    "error",
    types::outcome::TIMEOUT,
    types::outcome::SKIPPED_ALREADY_IN_FLIGHT,
    "error",
    types::outcome::TIMEOUT,
    "error",
];
static TEST_INJECT_IDX: AtomicU32 = AtomicU32::new(0);

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

            // TEST: inject 2 fake non-OK records right after the real one,
            //  using sequential run numbers so the next real run follows naturally.
            let now_iso = Utc::now().to_rfc3339();
            for _ in 0..2 {
                let idx = TEST_INJECT_IDX.fetch_add(1, Ordering::Relaxed) as usize;
                let fake_outcome = TEST_INJECT_OUTCOMES[idx % TEST_INJECT_OUTCOMES.len()];
                let fake_duration = match fake_outcome {
                    types::outcome::TIMEOUT => 32000,
                    _ => 150,
                };
                running_job.current_run += 1;
                let mut rec = ExecutionRecord::new(&now_iso, &now_iso, fake_outcome, running_job.current_run)
                    .with_duration(fake_duration)
                    .with_error(format!("TEST: synthetic {}", fake_outcome));
                if fake_outcome == types::outcome::SKIPPED_ALREADY_IN_FLIGHT {
                    rec = rec.with_outcome_ctx(current_run.to_string());
                }
                running_job.record_execution(rec);
            }
        }
    });
    Ok(())
}

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
            reload_jobs(state, new_jobs);
        });
        Ok::<_, PyErr>(())
    }).ok_or_else(|| pyo3::exceptions::PyException::new_err("GIL not available"))??;

    Ok(())
}

pub fn reload_jobs(
    state: &mut scheduler::SchedulerState,
    new_jobs: Vec<zato_server_core::model::SchedulerJob>,
) {
    let new_ids: std::collections::HashSet<i64> = new_jobs.iter().map(|j| j.id).collect();
    let old_ids: std::collections::HashSet<i64> = state.jobs.keys().cloned().collect();

    for id in old_ids.difference(&new_ids) {
        state.jobs.remove(id);
    }

    for sj in &new_jobs {
        let job_id = sj.id;
        if let Some(existing) = state.jobs.get_mut(&job_id) {
            existing.update_from_job(sj);
        } else {
            let running_job = RunningJob::from_scheduler_job(sj);
            state.jobs.insert(job_id, running_job);
        }
    }
}

pub fn reload_calendars(
    state: &mut scheduler::SchedulerState,
    new_cals: std::collections::HashMap<String, zato_server_core::model::HolidayCalendar>,
) {
    state.calendars.clear();
    for (name, cal) in new_cals {
        let mut calendar_data = CalendarData::new(name.clone());
        for date_str in &cal.dates {
            if let Ok(date) = chrono::NaiveDate::parse_from_str(date_str, "%Y-%m-%d") {
                calendar_data.dates.insert(date);
            }
        }
        calendar_data.weekdays = cal.weekdays.clone();
        calendar_data.description = cal.description.clone();
        state.calendars.insert(name, calendar_data);
    }
}

#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_get_history(py: Python<'_>, job_id: i64) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock().unwrap();
    if let Some(running_job) = state.jobs.get(&job_id) {
        let records: Vec<ExecutionRecord> = running_job.history.iter().cloned().collect();
        history::records_to_py_list(py, &records)
    } else {
        Ok(PyList::empty(py).unbind())
    }
}

fn parse_outcome_filter(outcomes: &Bound<'_, PyAny>) -> PyResult<Option<Vec<String>>> {
    if let Ok(s) = outcomes.extract::<String>() {
        if s == types::outcome::ALL {
            return Ok(None);
        }
    }
    if let Ok(list) = outcomes.cast::<PyList>() {
        let mut items: Vec<String> = list.iter().map(|item| item.extract::<String>()).collect::<PyResult<_>>()?;
        if !items.iter().any(|v| v == types::outcome::RUNNING) {
            items.push(types::outcome::RUNNING.to_string());
        }
        return Ok(Some(items));
    }
    Ok(None)
}

#[pyfunction]
#[pyo3(signature = (job_id, offset, limit, outcomes))]
fn scheduler_get_history_page(py: Python<'_>, job_id: i64, offset: usize, limit: usize, outcomes: Bound<'_, PyAny>) -> PyResult<Py<PyDict>> {
    let shared = get_shared()?;
    let state = shared.state.lock().unwrap();
    if let Some(running_job) = state.jobs.get(&job_id) {
        let filter = parse_outcome_filter(&outcomes)?;
        match filter {
            None => {
                let total = running_job.history.iter().filter(|r| r.outcome != types::outcome::RUNNING).count();
                let all_len = running_job.history.len();
                let start = if offset >= all_len { all_len } else { all_len - offset };
                let end = if limit >= start { 0 } else { start - limit };
                let slice: Vec<ExecutionRecord> = running_job.history.range(end..start).rev().cloned().collect();
                history::records_page_to_py_dict(py, &slice, total)
            }
            Some(allowed) => {
                let filtered: Vec<ExecutionRecord> = running_job.history.iter()
                    .filter(|r| allowed.iter().any(|a| a == &r.outcome))
                    .cloned()
                    .collect();
                let total = filtered.iter().filter(|r| r.outcome != types::outcome::RUNNING).count();
                let start = if offset >= filtered.len() { filtered.len() } else { filtered.len() - offset };
                let end = if limit >= start { 0 } else { start - limit };
                let slice: Vec<ExecutionRecord> = filtered[end..start].iter().rev().cloned().collect();
                history::records_page_to_py_dict(py, &slice, total)
            }
        }
    } else {
        history::records_page_to_py_dict(py, &[], 0)
    }
}

#[pyfunction]
#[pyo3(signature = (job_id, since_iso, outcomes, running_runs))]
fn scheduler_get_history_since(py: Python<'_>, job_id: i64, since_iso: &str, outcomes: Bound<'_, PyAny>, running_runs: Vec<u32>) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock().unwrap();
    if let Some(running_job) = state.jobs.get(&job_id) {
        let filter = parse_outcome_filter(&outcomes)?;
        let records: Vec<ExecutionRecord> = running_job.history.iter()
            .filter(|r| r.actual_fire_time_iso.as_str() >= since_iso
                || running_runs.contains(&r.current_run))
            .filter(|r| match &filter {
                None => true,
                Some(allowed) => allowed.iter().any(|a| a == &r.outcome)
                    || running_runs.contains(&r.current_run),
            })
            .rev()
            .cloned()
            .collect();
        history::records_to_py_list(py, &records)
    } else {
        Ok(PyList::empty(py).unbind())
    }
}

#[pyfunction]
#[pyo3(signature = ())]
fn scheduler_get_all_history(py: Python<'_>) -> PyResult<Py<PyDict>> {
    let shared = get_shared()?;
    let state = shared.state.lock().unwrap();
    history::all_history_to_py_dict(py, &state.jobs)
}

#[pyfunction]
#[pyo3(signature = ())]
fn scheduler_get_job_summaries(py: Python<'_>) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock().unwrap();
    let list = PyList::empty(py);
    for (id, running_job) in &state.jobs {
        let d = PyDict::new(py);
        d.set_item("id", *id)?;
        d.set_item("name", running_job.name.as_str())?;
        d.set_item("is_active", running_job.is_active)?;
        d.set_item("service", running_job.service.as_ref())?;
        d.set_item("job_type", running_job.job_type.as_str())?;
        d.set_item("in_flight", running_job.in_flight)?;
        d.set_item("current_run", running_job.current_run)?;
        d.set_item("interval_ms", running_job.interval_ms)?;
        match running_job.next_fire_utc {
            Some(dt) => d.set_item("next_fire_utc", dt.to_rfc3339())?,
            None => d.set_item("next_fire_utc", py.None())?,
        }
        list.append(d)?;
    }
    Ok(list.unbind())
}

pub fn dict_to_scheduler_job(job_id: i64, d: &Bound<'_, PyDict>) -> PyResult<zato_server_core::model::SchedulerJob> {
    let get_str = |key: &str| -> PyResult<String> {
        d.get_item(key)?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_string()))?
            .extract::<String>()
    };
    let get_opt_str = |key: &str| -> Option<String> {
        d.get_item(key).ok().flatten().and_then(|v| v.extract::<String>().ok()).filter(|s| !s.is_empty())
    };
    let get_opt_u32 = |key: &str| -> Option<u32> {
        d.get_item(key).ok().flatten().and_then(|v| v.extract::<u32>().ok())
    };
    let get_opt_u64 = |key: &str| -> Option<u64> {
        d.get_item(key).ok().flatten().and_then(|v| v.extract::<u64>().ok())
    };
    let get_bool = |key: &str| -> PyResult<bool> {
        d.get_item(key)?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_string()))?
            .extract::<bool>()
    };

    Ok(zato_server_core::model::SchedulerJob {
        id: job_id,
        name: get_str("name")?,
        is_active: get_bool("is_active")?,
        service: get_str("service")?,
        job_type: get_str("job_type")?,
        start_date: get_str("start_date")?,
        extra: get_opt_str("extra"),
        weeks: get_opt_u32("weeks"),
        days: get_opt_u32("days"),
        hours: get_opt_u32("hours"),
        minutes: get_opt_u32("minutes"),
        seconds: get_opt_u32("seconds"),
        repeats: get_opt_u32("repeats"),
        jitter_ms: get_opt_u32("jitter_ms"),
        timezone: get_opt_str("timezone"),
        calendar: get_opt_str("calendar"),
        on_missed: get_opt_str("on_missed"),
        max_execution_time_ms: get_opt_u64("max_execution_time_ms"),
    })
}

#[pymodule]
fn zato_scheduler_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();
    m.add_function(wrap_pyfunction!(scheduler_start, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_stop, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_create_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_edit_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_delete_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_execute_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_mark_complete, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_reload, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_history, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_history_page, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_history_since, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_all_history, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_job_summaries, m)?)?;
    Ok(())
}
