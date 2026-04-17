use chrono::{Datelike, Timelike, Utc};
use pyo3::prelude::*;
use pyo3::types::{PyDateTime, PyTzInfo};

#[pyfunction]
pub fn utc_now(py: Python<'_>) -> PyResult<Bound<'_, PyDateTime>> {
    let now = Utc::now();
    let tz_utc: Bound<'_, PyTzInfo> = py
        .import("datetime")?
        .getattr("timezone")?
        .getattr("utc")?
        .cast_into()?;
    PyDateTime::new(
        py,
        now.year(),
        now.month() as u8,
        now.day() as u8,
        now.hour() as u8,
        now.minute() as u8,
        now.second() as u8,
        now.timestamp_subsec_micros(),
        Some(&tz_utc),
    )
}
