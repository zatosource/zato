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
    const LOG_KEYS: [&str; 4] = ["system", "info", "warn", "error"];

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
    let mut log_counts = [0usize; 4];
    for entry in &rec.log_entries {
        let bucket = match entry.level.as_str() {
            "SYSTEM" => 0,
            "WARNING" | "WARN" => 2,
            "ERROR" | "CRITICAL" => 3,
            _ => 1,
        };
        if let Some(slot) = log_counts.get_mut(bucket) {
            *slot += 1;
        }
    }
    for (key, count) in LOG_KEYS.iter().zip(&log_counts) {
        log_summary.set_item(*key, *count)?;
    }
    out.set_item("log_summary", log_summary)?;

    Ok(out)
}

/// Converts a slice of execution records into a Python list of dictionaries.
///
/// # Errors
///
/// Returns a `PyErr` if record conversion or list insertion fails.
pub fn records_to_py_list(py: Python<'_>, records: &[ExecutionRecord]) -> PyResult<Py<PyList>> {
    let list = PyList::empty(py);
    for rec in records {
        list.append(record_to_py_dict(py, rec)?)?;
    }
    Ok(list.unbind())
}

/// Converts a page of execution records and total count into a Python dictionary
/// with `records` and `total` keys.
///
/// # Errors
///
/// Returns a `PyErr` if record conversion or dict insertion fails.
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
