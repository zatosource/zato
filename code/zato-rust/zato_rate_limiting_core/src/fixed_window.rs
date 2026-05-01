//! Fixed-window counter for Zato rate limiting.
//!
//! Enforces a hard cap of N requests per clock-aligned window
//! (second, minute, hour, day, or calendar month).

use std::fmt;
use std::str::FromStr;

use crate::common::{RateLimitError, MICROSECONDS_PER_SECOND};

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
    let now_secs = now_us / MICROSECONDS_PER_SECOND;

    match unit {
        WindowUnit::Second => Ok((now_secs + 1) * MICROSECONDS_PER_SECOND),
        WindowUnit::Minute => Ok((now_secs - now_secs % 60 + 60) * MICROSECONDS_PER_SECOND),
        WindowUnit::Hour => Ok((now_secs - now_secs % 3600 + 3600) * MICROSECONDS_PER_SECOND),

        other => Err(RateLimitError::new(
            format!("compute_window_end_us not yet implemented for {other}"),
        )),
    }
}
