use crate::job::ExecutionRecord;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

pub fn records_to_py_list<'py>(py: Python<'py>, records: &[ExecutionRecord]) -> PyResult<Py<PyList>> {
    let list = PyList::empty(py);
    for rec in records {
        let d = PyDict::new(py);
        for (k, v) in rec.to_dict_items() {
            d.set_item(k, v)?;
        }
        list.append(d)?;
    }
    Ok(list.unbind())
}

pub fn all_history_to_py_dict<'py>(
    py: Python<'py>,
    jobs: &std::collections::HashMap<String, crate::job::RunningJob>,
) -> PyResult<Py<PyDict>> {
    let out = PyDict::new(py);
    for (id, rj) in jobs {
        let records: Vec<&ExecutionRecord> = rj.history.iter().collect();
        let list = PyList::empty(py);
        for rec in &records {
            let d = PyDict::new(py);
            for (k, v) in rec.to_dict_items() {
                d.set_item(k, v)?;
            }
            list.append(d)?;
        }
        out.set_item(id.as_str(), list)?;
    }
    Ok(out.unbind())
}
