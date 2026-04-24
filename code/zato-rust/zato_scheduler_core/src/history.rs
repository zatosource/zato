use crate::job::ExecutionRecord;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

fn record_to_py_dict<'py>(py: Python<'py>, rec: &ExecutionRecord) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("planned_fire_time_iso", &rec.planned_fire_time_iso)?;
    d.set_item("actual_fire_time_iso", &rec.actual_fire_time_iso)?;
    d.set_item("delay_ms", rec.delay_ms)?;
    d.set_item("outcome", &rec.outcome)?;
    d.set_item("current_run", rec.current_run)?;
    match rec.duration_ms {
        Some(d_ms) => d.set_item("duration_ms", d_ms)?,
        None => d.set_item("duration_ms", py.None())?,
    }
    match &rec.error {
        Some(e) => d.set_item("error", e)?,
        None => d.set_item("error", py.None())?,
    }
    match &rec.outcome_ctx {
        Some(ctx) => d.set_item("outcome_ctx", ctx)?,
        None => d.set_item("outcome_ctx", py.None())?,
    }
    Ok(d)
}

pub fn records_to_py_list<'py>(py: Python<'py>, records: &[ExecutionRecord]) -> PyResult<Py<PyList>> {
    let list = PyList::empty(py);
    for rec in records {
        list.append(record_to_py_dict(py, rec)?)?;
    }
    Ok(list.unbind())
}

pub fn records_page_to_py_dict(py: Python<'_>, records: &[ExecutionRecord], total: usize) -> PyResult<Py<PyDict>> {
    let out = PyDict::new(py);
    let list = PyList::empty(py);
    for rec in records {
        list.append(record_to_py_dict(py, rec)?)?;
    }
    out.set_item("records", list)?;
    out.set_item("total", total)?;
    Ok(out.unbind())
}

pub fn all_history_to_py_dict<'py>(
    py: Python<'py>,
    jobs: &std::collections::HashMap<i64, crate::job::RunningJob>,
) -> PyResult<Py<PyDict>> {
    let out = PyDict::new(py);
    for (id, running_job) in jobs {
        let list = PyList::empty(py);
        for rec in &running_job.history {
            list.append(record_to_py_dict(py, rec)?)?;
        }
        out.set_item(*id, list)?;
    }
    Ok(out.unbind())
}
