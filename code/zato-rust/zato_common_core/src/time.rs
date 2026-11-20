//! Time utilities for converting UTC timestamps to Python datetime objects.

use std::num::TryFromIntError;

use jiff::Timestamp;
use jiff::tz::TimeZone;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDateTime, PyTzInfo};

/// Nanoseconds in one microsecond, for reducing the sub-second part of a timestamp to what Python keeps.
const NANOS_PER_MICRO: i32 = 1_000;

/// Converts one calendar field of a UTC timestamp to the unsigned type that `PyDateTime::new` expects.
fn calendar_field<Field: TryFrom<i32, Error = TryFromIntError>>(value: i32, name: &str) -> PyResult<Field> {
    Field::try_from(value).map_err(|error| PyValueError::new_err(format!("Calendar field `{name}` out of range: {value}: {error}")))
}

/// Returns the current UTC time as a Python `datetime.datetime` with `datetime.timezone.utc` tzinfo.
#[pyfunction]
pub fn utc_now(py: Python<'_>) -> PyResult<Bound<'_, PyDateTime>> {
    let now = TimeZone::UTC.to_datetime(Timestamp::now());
    let tz_utc: Bound<'_, PyTzInfo> = py.import("datetime")?.getattr("timezone")?.getattr("utc")?.cast_into()?;

    PyDateTime::new(
        py,
        i32::from(now.year()),
        calendar_field(i32::from(now.month()), "month")?,
        calendar_field(i32::from(now.day()), "day")?,
        calendar_field(i32::from(now.hour()), "hour")?,
        calendar_field(i32::from(now.minute()), "minute")?,
        calendar_field(i32::from(now.second()), "second")?,
        calendar_field(now.subsec_nanosecond() / NANOS_PER_MICRO, "microsecond")?,
        Some(&tz_utc),
    )
}
