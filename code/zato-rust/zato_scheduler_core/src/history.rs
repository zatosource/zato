// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

use crate::job::ExecutionRecord;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Converts a single execution record into a Python dictionary.
///
/// Includes a `log_summary` dict with per-level counts (cheap, no message bodies).
///
/// # Errors
///
/// Returns a `PyErr` if any dict key/value insertion fails.
fn record_to_py_dict<'py>(py: Python<'py>, rec: &ExecutionRecord) -> PyResult<Bound<'py, PyDict>> {
    let out = PyDict::new(py);
    out.set_item("planned_fire_time_iso", &rec.planned_fire_time_iso)?;
    out.set_item("actual_fire_time_iso", &rec.actual_fire_time_iso)?;
    out.set_item("delay_ms", rec.delay_ms)?;
    out.set_item("outcome", &rec.outcome)?;
    out.set_item("current_run", rec.current_run)?;
    match rec.duration_ms {
        Some(duration) => out.set_item("duration_ms", duration)?,
        None => out.set_item("duration_ms", py.None())?,
    }
    match &rec.error {
        Some(error_text) => out.set_item("error", error_text)?,
        None => out.set_item("error", py.None())?,
    }
    match &rec.outcome_ctx {
        Some(outcome_ctx) => out.set_item("outcome_ctx", outcome_ctx)?,
        None => out.set_item("outcome_ctx", py.None())?,
    }

    let log_summary = PyDict::new(py);
    let mut system_count: usize = 0;
    let mut info_count: usize = 0;
    let mut warn_count: usize = 0;
    let mut error_count: usize = 0;
    for entry in &rec.log_entries {
        match entry.level.as_str() {
            "SYSTEM" => system_count += 1,
            "WARNING" | "WARN" => warn_count += 1,
            "ERROR" | "CRITICAL" => error_count += 1,
            _ => info_count += 1,
        }
    }
    log_summary.set_item("system", system_count)?;
    log_summary.set_item("info", info_count)?;
    log_summary.set_item("warn", warn_count)?;
    log_summary.set_item("error", error_count)?;
    out.set_item("log_summary", log_summary)?;

    Ok(out)
}

/// Converts a slice of execution record references into a Python list of dictionaries.
///
/// # Errors
///
/// Returns a `PyErr` if record conversion or list insertion fails.
pub fn records_to_py_list(py: Python<'_>, records: &[&ExecutionRecord]) -> PyResult<Py<PyList>> {
    let list = PyList::empty(py);
    for rec in records {
        list.append(record_to_py_dict(py, rec)?)?;
    }
    Ok(list.unbind())
}

/// Converts a page of execution record references and total count into a Python dictionary
/// with `records` and `total` keys.
///
/// # Errors
///
/// Returns a `PyErr` if record conversion or dict insertion fails.
pub fn records_page_to_py_dict(py: Python<'_>, records: &[&ExecutionRecord], total: usize) -> PyResult<Py<PyDict>> {
    let out = PyDict::new(py);
    let list = PyList::empty(py);
    for rec in records {
        list.append(record_to_py_dict(py, rec)?)?;
    }
    out.set_item("records", list)?;
    out.set_item("total", total)?;
    Ok(out.unbind())
}
