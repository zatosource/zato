//! Fixed-window counter for Zato rate limiting.
//!
//! Enforces a hard cap of N requests per clock-aligned window
//! (second, minute, hour, day, or calendar month).

use std::fmt;
use std::str::FromStr;

use chrono::{DateTime, Datelike, NaiveDate};

use pyo3::prelude::*;

use crate::common::{RateLimitError, RateLimitResult, MICROSECONDS_PER_SECOND};

const SECONDS_PER_MINUTE: u64 = 60;
const SECONDS_PER_HOUR: u64 = 3600;
const SECONDS_PER_DAY: u64 = 86400;

const JANUARY: u32 = 1;
const DECEMBER: u32 = 12;
const MIDNIGHT_HOUR: u32 = 0;
const MIDNIGHT_MINUTE: u32 = 0;
const MIDNIGHT_SECOND: u32 = 0;

// ----------------------------------------------------------------- window unit

/// Clock-aligned window period for the fixed-window counter.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum WindowUnit {

    /// One-second window, aligned to second boundaries.
    Second,

    /// One-minute window, aligned to minute boundaries.
    Minute,

    /// One-hour window, aligned to hour boundaries.
    Hour,

    /// One-day window, aligned to UTC day boundaries.
    Day,

    /// Calendar month window, aligned to the 1st of each month (UTC).
    Month,
}

impl WindowUnit {

    /// Returns the canonical string label for this window unit.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Second => "second",
            Self::Minute => "minute",
            Self::Hour => "hour",
            Self::Day => "day",
            Self::Month => "month",
        }
    }
}

impl FromStr for WindowUnit {
    type Err = RateLimitError;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "second" => Ok(Self::Second),
            "minute" => Ok(Self::Minute),
            "hour" => Ok(Self::Hour),
            "day" => Ok(Self::Day),
            "month" => Ok(Self::Month),
            other => Err(RateLimitError::new(format!("Unknown window_unit: {other}"))),
        }
    }
}

impl fmt::Display for WindowUnit {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(self.as_str())
    }
}

// --------------------------------------------------------- window boundaries

/// Returns the microsecond timestamp at which the current natural window ends.
pub fn compute_window_end_us(unit: WindowUnit, now_us: u64) -> Result<u64, RateLimitError> {
    let period_secs = match unit {
        WindowUnit::Second => Some(1),
        WindowUnit::Minute => Some(SECONDS_PER_MINUTE),
        WindowUnit::Hour => Some(SECONDS_PER_HOUR),
        WindowUnit::Day => Some(SECONDS_PER_DAY),
        WindowUnit::Month => None,
    };

    if let Some(period) = period_secs {
        let now_secs = now_us / MICROSECONDS_PER_SECOND;
        let window_start = now_secs - now_secs % period;
        let window_end_secs = window_start + period;
        let window_end_us = window_end_secs * MICROSECONDS_PER_SECOND;
        return Ok(window_end_us);
    }

    // Month requires chrono for calendar math.
    let now_secs = now_us / MICROSECONDS_PER_SECOND;

    let secs_i64 = i64::try_from(now_secs).map_err(|_| {
        RateLimitError::new(
            format!("Month boundary failed, i64 conversion overflow: {now_us}"),
        )
    })?;

    let dt = DateTime::from_timestamp(secs_i64, 0).ok_or_else(|| {
        RateLimitError::new(
            format!("Month boundary failed, DateTime::from_timestamp returned None: {secs_i64}"),
        )
    })?;

    let year = dt.year();
    let month = dt.month();

    let (next_year, next_month): (i32, u32) = if month == DECEMBER {
        (year + 1, JANUARY)
    } else {
        (year, month + 1)
    };

    let first_of_next = NaiveDate::from_ymd_opt(next_year, next_month, 1)
        .ok_or_else(|| {
            RateLimitError::new(
                format!("Month boundary failed, invalid date: {next_year}-{next_month:02}-01"),
            )
        })?;

    let midnight = first_of_next
        .and_hms_opt(MIDNIGHT_HOUR, MIDNIGHT_MINUTE, MIDNIGHT_SECOND)
        .ok_or_else(|| {
            RateLimitError::new(
                format!("Month boundary failed, midnight construction for {next_year}-{next_month:02}-01"),
            )
        })?;

    let boundary_secs = midnight.and_utc().timestamp();

    let boundary_secs_u64 = u64::try_from(boundary_secs).map_err(|_| {
        RateLimitError::new(
            format!("Month boundary failed, negative timestamp: {boundary_secs}"),
        )
    })?;

    let window_end_us = boundary_secs_u64 * MICROSECONDS_PER_SECOND;

    Ok(window_end_us)
}

// --------------------------------------------------------------- window state

/// Per-key counter state within a single window.
#[expect(dead_code, reason = "Used by FixedWindowRegistry in phase 14")]
pub(crate) struct WindowState {

    /// Requests consumed in the current window.
    pub(crate) count: u64,

    /// Microseconds since epoch when the current window expires.
    pub(crate) window_end_us: u64,
}

// -------------------------------------------------------------------- config

/// Python-visible configuration for a fixed-window counter.
#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct FixedWindowConfig {

    /// Maximum requests allowed per window.
    #[pyo3(get)]
    pub limit: u64,

    /// Cached window unit parsed at construction time.
    parsed_window_unit: WindowUnit,
}

impl FixedWindowConfig {

    /// Rust-only constructor for tests and fuzz targets.
    #[must_use]
    pub const fn from_parts(limit: u64, window_unit: WindowUnit) -> Self {
        Self {
            limit,
            parsed_window_unit: window_unit,
        }
    }

    /// Returns the parsed window unit.
    #[must_use]
    pub const fn unit(&self) -> WindowUnit {
        self.parsed_window_unit
    }
}

#[pymethods]
impl FixedWindowConfig {

    /// Creates a new fixed-window configuration from a limit and unit string.
    #[new]
    fn new(limit: u64, window_unit: &str) -> PyResult<Self> {
        let parsed_window_unit: WindowUnit = window_unit
            .parse()
            .map_err(|err: RateLimitError| pyo3::exceptions::PyValueError::new_err(err.to_string()))?;
        Ok(Self { limit, parsed_window_unit })
    }

    /// Returns the window unit as a string.
    #[getter]
    #[expect(clippy::missing_const_for_fn, reason = "PyO3 #[getter] cannot be const")]
    fn window_unit(&self) -> &str {
        self.parsed_window_unit.as_str()
    }
}

// -------------------------------------------------------------- check result

/// Result of a fixed-window counter check, returned to Python.
#[must_use]
#[pyclass(get_all, skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct FixedWindowCheckResult {

    /// Whether the request was allowed through.
    pub is_allowed: bool,

    /// Requests remaining in this window (0 if denied).
    pub remaining: u64,

    /// Microseconds until the window resets (0 if allowed).
    pub retry_after_us: u64,
}

impl RateLimitResult for FixedWindowCheckResult {

    fn is_allowed(&self) -> bool {
        self.is_allowed
    }

    fn retry_after_us(&self) -> u64 {
        self.retry_after_us
    }
}
