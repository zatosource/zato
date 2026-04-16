use std::sync::Arc;
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
static CONFIG_STORE: std::sync::OnceLock<PyObject> = std::sync::OnceLock::new();
static THREAD_HANDLE: std::sync::Mutex<Option<std::thread::JoinHandle<()>>> = std::sync::Mutex::new(None);

fn get_shared() -> PyResult<&'static Arc<SchedulerShared>> {
    SHARED.get().ok_or_else(|| {
        pyo3::exceptions::PyRuntimeError::new_err("scheduler not started")
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
#[pyo3(signature = (config_store, run_cb, spawn_fn, on_job_executed_cb, initial_sleep_time))]
fn scheduler_start(
    py: Python<'_>,
    config_store: PyObject,
    run_cb: PyObject,
    spawn_fn: PyObject,
    on_job_executed_cb: PyObject,
    initial_sleep_time: f64,
) -> PyResult<()> {
    let shared = Arc::new(SchedulerShared::new());
    let _ = SHARED.set(Arc::clone(&shared));
    let _ = CONFIG_STORE.set(config_store.clone_ref(py));

    let cs = config_store.clone_ref(py);

    let handle = std::thread::Builder::new()
        .name("zato-scheduler".into())
        .spawn(move || {
            scheduler::scheduler_loop(shared, cs, run_cb, spawn_fn, on_job_executed_cb, initial_sleep_time);
        })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("spawn failed: {e}")))?;

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

    let handle = THREAD_HANDLE.lock().ok().and_then(|mut g| g.take());
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
fn scheduler_create_job(_py: Python<'_>, job_id: &str, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
    let shared = get_shared()?;
    let sj = dict_to_scheduler_job(job_id, job_data)?;
    let rj = RunningJob::from_scheduler_job(&sj);
    with_state_mut(shared, |state| {
        state.jobs.insert(job_id.to_string(), rj);
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id, job_data))]
fn scheduler_edit_job(_py: Python<'_>, job_id: &str, job_data: &Bound<'_, PyDict>) -> PyResult<()> {
    let shared = get_shared()?;
    let sj = dict_to_scheduler_job(job_id, job_data)?;
    with_state_mut(shared, |state| {
        if let Some(existing) = state.jobs.get_mut(job_id) {
            existing.update_from_job(&sj);
        } else {
            let rj = RunningJob::from_scheduler_job(&sj);
            state.jobs.insert(job_id.to_string(), rj);
        }
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_delete_job(job_id: &str) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        state.jobs.remove(job_id);
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_execute_job(job_id: &str) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        if let Some(rj) = state.jobs.get_mut(job_id) {
            rj.next_fire_utc = Some(Utc::now());
            rj.sync_instant_from_utc_pub(Utc::now());
        }
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (job_id, outcome, duration_ms))]
fn scheduler_mark_complete(job_id: &str, outcome: &str, duration_ms: u64) -> PyResult<()> {
    let shared = get_shared()?;
    with_state_mut(shared, |state| {
        if let Some(rj) = state.jobs.get_mut(job_id) {
            rj.in_flight = false;
            rj.in_flight_since = None;
            if let Some(last) = rj.history.back_mut() {
                last.duration_ms = Some(duration_ms);
                if outcome != "ok" {
                    last.outcome = outcome.to_string();
                }
            }
        }
    });
    Ok(())
}

#[pyfunction]
#[pyo3(signature = ())]
fn scheduler_reload() -> PyResult<()> {
    let shared = get_shared()?;
    let cs = CONFIG_STORE.get().ok_or_else(|| {
        pyo3::exceptions::PyRuntimeError::new_err("scheduler not started")
    })?;

    Python::try_attach(|py| {
        let cs_bound = cs.bind(py);
        let (new_jobs, new_cals) = scheduler::load_from_config_store_py(cs_bound)?;
        with_state_mut(shared, |state| {
            reload_jobs(state, new_jobs);
            reload_calendars(state, new_cals);
        });
        Ok::<_, PyErr>(())
    }).ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("GIL not available"))??;

    Ok(())
}

pub fn reload_jobs(
    state: &mut scheduler::SchedulerState,
    new_jobs: std::collections::HashMap<String, zato_server_core::model::SchedulerJob>,
) {
    let new_ids: std::collections::HashSet<String> = new_jobs.values().map(|j| j.id.clone()).collect();
    let old_ids: std::collections::HashSet<String> = state.jobs.keys().cloned().collect();

    for id in old_ids.difference(&new_ids) {
        state.jobs.remove(id);
    }

    for (_name, sj) in &new_jobs {
        let job_id = &sj.id;
        if let Some(existing) = state.jobs.get_mut(job_id.as_str()) {
            existing.update_from_job(sj);
        } else {
            let rj = RunningJob::from_scheduler_job(sj);
            state.jobs.insert(job_id.clone(), rj);
        }
    }
}

pub fn reload_calendars(
    state: &mut scheduler::SchedulerState,
    new_cals: std::collections::HashMap<String, zato_server_core::model::HolidayCalendar>,
) {
    state.calendars.clear();
    for (name, cal) in new_cals {
        let mut cd = CalendarData::new(name.clone());
        for ds in &cal.dates {
            if let Ok(d) = chrono::NaiveDate::parse_from_str(ds, "%Y-%m-%d") {
                cd.dates.insert(d);
            }
        }
        cd.weekdays = cal.weekdays.clone();
        cd.description = cal.description.clone();
        state.calendars.insert(name, cd);
    }
}

#[pyfunction]
#[pyo3(signature = (job_id,))]
fn scheduler_get_history(py: Python<'_>, job_id: &str) -> PyResult<Py<PyList>> {
    let shared = get_shared()?;
    let state = shared.state.lock().unwrap();
    if let Some(rj) = state.jobs.get(job_id) {
        let records: Vec<ExecutionRecord> = rj.history.iter().cloned().collect();
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
    for (id, rj) in &state.jobs {
        let d = PyDict::new(py);
        d.set_item("id", id.as_str())?;
        d.set_item("name", rj.name.as_str())?;
        d.set_item("is_active", rj.is_active)?;
        d.set_item("service", rj.service.as_ref())?;
        d.set_item("job_type", rj.job_type.as_str())?;
        d.set_item("in_flight", rj.in_flight)?;
        d.set_item("current_run", rj.current_run)?;
        d.set_item("interval_ms", rj.interval_ms)?;
        match rj.next_fire_utc {
            Some(dt) => d.set_item("next_fire_utc", dt.to_rfc3339())?,
            None => d.set_item("next_fire_utc", py.None())?,
        }
        list.append(d)?;
    }
    Ok(list.unbind())
}

fn dict_to_scheduler_job(job_id: &str, d: &Bound<'_, PyDict>) -> PyResult<zato_server_core::model::SchedulerJob> {
    let get_str = |key: &str| -> String {
        d.get_item(key).ok().flatten().and_then(|v| v.extract::<String>().ok()).unwrap_or_default()
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
    let get_bool = |key: &str, default: bool| -> bool {
        d.get_item(key).ok().flatten().and_then(|v| v.extract::<bool>().ok()).unwrap_or(default)
    };

    Ok(zato_server_core::model::SchedulerJob {
        id: job_id.to_string(),
        name: get_str("name"),
        is_active: get_bool("is_active", true),
        service: get_str("service"),
        job_type: get_str("job_type"),
        start_date: get_str("start_date"),
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
    m.add_function(wrap_pyfunction!(scheduler_start, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_stop, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_create_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_edit_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_delete_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_execute_job, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_mark_complete, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_reload, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_history, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_all_history, m)?)?;
    m.add_function(wrap_pyfunction!(scheduler_get_job_summaries, m)?)?;
    Ok(())
}
