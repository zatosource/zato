//! Time utilities for converting chrono timestamps to Python datetime objects.

use chrono::{Datelike, Timelike, Utc};
use pyo3::prelude::*;
use pyo3::types::{PyDateTime, PyTzInfo};

/// Returns the current UTC time as a Python `datetime.datetime` with `datetime.timezone.utc` tzinfo.
#[pyfunction]
pub fn utc_now(py: Python<'_>) -> PyResult<Bound<'_, PyDateTime>> {
    let now = Utc::now();
    let tz_utc: Bound<'_, PyTzInfo> = py
        .import("datetime")?
        .getattr("timezone")?
        .getattr("utc")?
        .cast_into()?;

    #[expect(clippy::cast_possible_truncation, reason = "month/day/hour/minute/second always fit in u8")]
    #[expect(clippy::as_conversions, reason = "chrono returns u32 for values guaranteed to be in 1..=12, 1..=31, 0..=23, 0..=59 range")]
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
