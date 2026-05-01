//! Shared error types and constants for Zato rate limiting modules
//! (token bucket, fixed-window counter).

use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// One second expressed in microseconds (for time conversions).
pub const MICROSECONDS_PER_SECOND: u64 = 1_000_000;

// -------------------------------------------------------------------- errors

/// Represents a rate limiter failure: invalid configuration, arithmetic
/// overflow, or a system clock error.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RateLimitError {
    msg: String,
}

impl RateLimitError {

    /// Wraps a human-readable description of the failure.
    pub fn new(msg: impl Into<String>) -> Self {
        Self { msg: msg.into() }
    }
}

impl fmt::Display for RateLimitError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.msg)
    }
}

impl std::error::Error for RateLimitError {}

impl From<RateLimitError> for PyErr {
    fn from(err: RateLimitError) -> Self {
        PyValueError::new_err(err.msg)
    }
}

// -------------------------------------------------------------------- clock

/// Returns the current wall clock time in microseconds since Unix epoch.
pub fn current_time_us() -> Result<u64, RateLimitError> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|err| {
            RateLimitError::new(format!("Clock error, duration_since(UNIX_EPOCH) failed: {err}"))
        })?;

    let micros = duration.as_micros();

    let micros_u64 = u64::try_from(micros).map_err(|_| {
        RateLimitError::new(format!("Clock error, u64::try_from failed for microseconds: {micros}"))
    })?;

    Ok(micros_u64)
}

// -------------------------------------------------------------- result trait

/// Common interface for rate limit check results.
pub trait RateLimitResult {

    /// Whether the request was allowed through.
    fn is_allowed(&self) -> bool;

    /// Microseconds until the next opportunity to retry (0 if allowed).
    fn retry_after_us(&self) -> u64;
}
