use crate::job::ExecutionRecord;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

fn record_to_py_dict<'py>(py: Python<'py>, rec: &ExecutionRecord) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    for (k, v) in rec.to_dict_items() {
        d.set_item(k, v)?;
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
    jobs: &std::collections::HashMap<String, crate::job::RunningJob>,
) -> PyResult<Py<PyDict>> {
    let out = PyDict::new(py);
    for (id, running_job) in jobs {
        let list = PyList::empty(py);
        for rec in &running_job.history {
            list.append(record_to_py_dict(py, rec)?)?;
        }
        out.set_item(id.as_str(), list)?;
    }
    Ok(out.unbind())
}
