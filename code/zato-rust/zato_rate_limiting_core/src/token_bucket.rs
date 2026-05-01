//! Token bucket rate limiter with lazy refill and O(1) per-check cost.
//!
//! Each bucket holds four plain `u64` fields: token balance, last refill
//! timestamp, refill rate, and period end. All access is single-threaded
//! by design. A `parking_lot::Mutex` wraps the `HashMap` only to satisfy
//! `PyO3`'s `Send + Sync` requirement on `#[pyclass]` types.
//!
//! Buckets live in a `HashMap` keyed by an arbitrary string that the Python
//! caller provides.

use std::collections::HashMap;
use std::fmt;
use std::str::FromStr;
use std::time::{SystemTime, UNIX_EPOCH};

use chrono::{Datelike, DateTime, NaiveDate, Timelike};
use parking_lot::Mutex;
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// One token expressed in microtokens (fixed-point arithmetic avoids floating point).
const MICROTOKENS_PER_TOKEN: u64 = 1_000_000;

/// One second expressed in microseconds (for time conversions).
const MICROSECONDS_PER_SECOND: u64 = 1_000_000;

/// Seconds in one minute.
const SECONDS_PER_MINUTE: u64 = 60;

/// Seconds in one hour.
const SECONDS_PER_HOUR: u64 = 3_600;

/// Seconds in one day.
const SECONDS_PER_DAY: u64 = 86_400;

// -------------------------------------------------------------------- errors

/// Error type for rate limiter operations that do not depend on Python.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RateLimitError {
    msg: String,
}

impl RateLimitError {
    /// Creates a new error with the given message.
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

// ------------------------------------------------------------------ time unit

/// Supported time units for rate definitions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum TimeUnit {

    /// 1 second.
    Second,

    /// 60 seconds.
    Minute,

    /// 3 600 seconds.
    Hour,

    /// 86 400 seconds.
    Day,

    /// Calendar month (28-31 days depending on the month).
    Month,
}

impl FromStr for TimeUnit {
    type Err = RateLimitError;

    /// Parses a string into a `TimeUnit`.
    ///
    /// Accepted values: "second", "minute", "hour", "day", "month".
    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "second" => Ok(Self::Second),
            "minute" => Ok(Self::Minute),
            "hour" => Ok(Self::Hour),
            "day" => Ok(Self::Day),
            "month" => Ok(Self::Month),
            other => Err(RateLimitError::new(format!("Unknown time_unit: {other}"))),
        }
    }
}

impl fmt::Display for TimeUnit {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

impl TimeUnit {
    /// Returns the canonical string label for this time unit.
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

    /// Returns the full period length in seconds for fixed time units.
    ///
    /// Returns `None` for `Month` because months have variable length
    /// (28-31 days). Callers must use calendar math for months.
    #[must_use]
    pub const fn full_period_seconds(self) -> Option<u64> {
        match self {
            Self::Second => Some(1),
            Self::Minute => Some(SECONDS_PER_MINUTE),
            Self::Hour => Some(SECONDS_PER_HOUR),
            Self::Day => Some(SECONDS_PER_DAY),
            Self::Month => None,
        }
    }
}

/// January's month number in chrono (1-based).
const JANUARY: u32 = 1;

/// December's month number in chrono (1-based).
const DECEMBER: u32 = 12;

/// Returns the number of days in the given month.
fn days_in_month(year: i32, month: u32) -> Result<u64, RateLimitError> {
    let (next_year, next_month) = if month == DECEMBER {
        (year + 1, JANUARY)
    } else {
        (year, month + 1)
    };

    let first_of_this = NaiveDate::from_ymd_opt(year, month, 1).ok_or_else(|| {
        RateLimitError::new(format!("Invalid date: year={year}, month={month}, day=1"))
    })?;

    let first_of_next = NaiveDate::from_ymd_opt(next_year, next_month, 1).ok_or_else(|| {
        RateLimitError::new(format!("Invalid date: year={next_year}, month={next_month}, day=1"))
    })?;

    let num_days = (first_of_next - first_of_this).num_days();

    let day_count = u64::try_from(num_days).map_err(|_| {
        RateLimitError::new(format!("Negative days in month: {num_days} for year={year}, month={month}"))
    })?;

    Ok(day_count)
}

/// Computes seconds remaining in the current calendar month.
///
/// Returns at least 1 so callers can safely use the result as a divisor.
fn remaining_seconds_in_month(now_us: u64) -> Result<u64, RateLimitError> {
    let now_secs = i64::try_from(now_us / MICROSECONDS_PER_SECOND).map_err(|_| {
        RateLimitError::new(format!("Timestamp too large for i64: {now_us}"))
    })?;

    let dt = DateTime::from_timestamp(now_secs, 0).ok_or_else(|| {
        RateLimitError::new(format!("Invalid Unix timestamp: {now_secs}"))
    })?;

    let month_days = days_in_month(dt.year(), dt.month())?;
    let month_total_seconds = month_days * SECONDS_PER_DAY;

    let elapsed_days = u64::from(dt.day() - 1);
    let elapsed_seconds = elapsed_days * SECONDS_PER_DAY
        + u64::from(dt.hour()) * SECONDS_PER_HOUR
        + u64::from(dt.minute()) * SECONDS_PER_MINUTE
        + u64::from(dt.second());

    let remaining = month_total_seconds.checked_sub(elapsed_seconds).ok_or_else(|| {
        RateLimitError::new(format!(
            "Underflow: month_total_seconds ({month_total_seconds}) - elapsed_seconds ({elapsed_seconds})"
        ))
    })?;

    if remaining == 0 {
        Ok(month_total_seconds)
    } else {
        Ok(remaining)
    }
}

/// Computes seconds remaining in the current period for the given time unit.
///
/// Always returns at least 1, so callers can safely divide by the result
/// (after converting to microseconds) without risking division by zero.
fn remaining_seconds_in_period(time_unit: TimeUnit, now_us: u64) -> Result<u64, RateLimitError> {
    match time_unit.full_period_seconds() {

        Some(period) => {
            let now_secs = now_us / MICROSECONDS_PER_SECOND;
            let elapsed_in_period = now_secs % period;
            let remaining = period - elapsed_in_period;

            if remaining == 0 {
                Ok(period)
            } else {
                Ok(remaining)
            }
        }

        None => remaining_seconds_in_month(now_us),
    }
}

// ----------------------------------------------------------- bucket internals

/// Internal bucket state stored per key.
///
/// All four fields are plain `u64` values - no atomics, no mutexes.
/// Single-threaded access is guaranteed by design.
struct BucketState {

    /// Current token balance in microtokens (1 token = `1_000_000` microtokens).
    tokens_remaining_micro: u64,

    /// Microseconds since Unix epoch when tokens were last refilled.
    last_refill_us: u64,

    /// Refill speed in microtokens per microsecond for the current period.
    refill_rate_micro_per_us: u64,

    /// Microseconds since Unix epoch when the current period ends.
    period_end_us: u64,
}

/// Refill rate and period boundary computed from the current calendar period.
struct RefillParams {

    /// Microtokens added per microsecond during this period.
    rate_micro_per_us: u64,

    /// Microseconds since Unix epoch when this period ends.
    period_end_us: u64,
}

/// Computes refill rate and period boundary for the current calendar period.
fn compute_refill_params(rate: u64, time_unit: TimeUnit, now_us: u64) -> Result<RefillParams, RateLimitError> {
    let remaining_secs = remaining_seconds_in_period(time_unit, now_us)?;

    if remaining_secs == 0 {
        return Err(RateLimitError::new("remaining_seconds_in_period returned zero"));
    }

    let remaining_us = remaining_secs.checked_mul(MICROSECONDS_PER_SECOND).ok_or_else(|| {
        RateLimitError::new(format!("Overflow: remaining_secs ({remaining_secs}) * MICROSECONDS_PER_SECOND"))
    })?;

    let rate_micro = rate.checked_mul(MICROTOKENS_PER_TOKEN).ok_or_else(|| {
        RateLimitError::new(format!("Overflow: rate ({rate}) * MICROTOKENS_PER_TOKEN"))
    })?;

    let period_end_us = now_us.checked_add(remaining_us).ok_or_else(|| {
        RateLimitError::new(format!("Overflow: now_us ({now_us}) + remaining_us ({remaining_us})"))
    })?;

    Ok(RefillParams {
        rate_micro_per_us: rate_micro / remaining_us,
        period_end_us,
    })
}

// --------------------------------------------------------------- check result

/// Result of a rate limit check, returned to Python.
#[must_use]
#[pyclass(get_all, skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct CheckResult {

    /// Whether the request is allowed.
    pub allowed: bool,

    /// Tokens remaining after this check (whole tokens, rounded down).
    pub tokens_remaining: u64,

    /// Microseconds until the next token becomes available (0 if allowed).
    pub retry_after_us: u64,
}

// -------------------------------------------------------------------- config

/// Python-visible configuration for a single token bucket window.
#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct TokenBucketConfig {

    /// Requests allowed per `time_unit`.
    #[pyo3(get)]
    pub rate: u64,

    /// Parsed time unit, cached from construction so `check` never re-parses.
    parsed_time_unit: TimeUnit,

    /// Maximum burst size (bucket capacity).
    #[pyo3(get)]
    pub burst_allowed: u64,
}

impl TokenBucketConfig {
    /// Rust-only constructor for tests and fuzz targets.
    #[must_use]
    pub const fn from_parts(rate: u64, time_unit: TimeUnit, burst_allowed: u64) -> Self {
        Self { rate, parsed_time_unit: time_unit, burst_allowed }
    }
}

#[pymethods]
impl TokenBucketConfig {
    /// Creates a new token bucket configuration.
    #[new]
    fn new(rate: u64, time_unit: &str, burst_allowed: u64) -> PyResult<Self> {
        let parsed_time_unit = time_unit.parse::<TimeUnit>()?;
        Ok(Self { rate, parsed_time_unit, burst_allowed })
    }

    /// Returns the time unit string ("second", "minute", "hour", "day", "month").
    #[getter]
    #[expect(clippy::missing_const_for_fn, reason = "PyO3 getter cannot be const")]
    fn time_unit(&self) -> &str {
        self.parsed_time_unit.as_str()
    }
}

// --------------------------------------------------------- consume or deny

/// Refills tokens based on elapsed time, clamps to burst limit, then
/// either deducts one token (allow) or records the deficit (deny).
fn consume_or_deny(
    bucket: &mut BucketState,
    burst_micro: u64,
    now_us: u64,
) -> CheckResult {

    // Microseconds elapsed since the last refill. saturating_sub
    // guards against clock skew where now_us < last_refill_us.
    let elapsed_us = now_us.saturating_sub(bucket.last_refill_us);

    // Compute how many microtokens have accumulated since the
    // last refill, then add them to the current balance.
    let added_micro = elapsed_us.saturating_mul(bucket.refill_rate_micro_per_us);
    let refilled = bucket.tokens_remaining_micro.saturating_add(added_micro);

    // #2: clamp the balance to the burst limit so tokens
    // never accumulate beyond the configured maximum.
    let capped = refilled.min(burst_micro);

    // Update the refill timestamp.
    bucket.last_refill_us = now_us;

    // #3: enough tokens to allow the request.
    if capped >= MICROTOKENS_PER_TOKEN {

        // Deduct exactly one token (in microtokens) from the balance.
        let new_tokens = capped - MICROTOKENS_PER_TOKEN;
        bucket.tokens_remaining_micro = new_tokens;

        return CheckResult {
            allowed: true,
            tokens_remaining: new_tokens / MICROTOKENS_PER_TOKEN,
            retry_after_us: 0,
        };
    }

    // #4: not enough tokens - deny the request.
    bucket.tokens_remaining_micro = capped;

    // How many microtokens are missing to reach one full token.
    let deficit_micro = MICROTOKENS_PER_TOKEN - capped;

    // #5: estimate how many microseconds the caller should wait
    // before retrying. When refill_rate is zero (rate=0 policy),
    // fall back to one full second.
    let retry_us = match deficit_micro.checked_div(bucket.refill_rate_micro_per_us) {
        Some(quotient) => quotient + 1,
        None => MICROSECONDS_PER_SECOND,
    };

    CheckResult {
        allowed: false,
        tokens_remaining: 0,
        retry_after_us: retry_us,
    }
}

// ------------------------------------------------------------------ registry

/// Top-level rate limiter registry holding all buckets across all keys.
///
/// Each key (assembled by the Python caller from channel ID, security
/// definition ID, IP, etc.) maps to a `BucketState`. Access is
/// single-threaded by design.
#[pyclass(skip_from_py_object)]
pub struct TokenBucketRegistry {

    /// Maps caller-assembled keys to their bucket states.
    ///
    /// `parking_lot::Mutex` satisfies `PyO3`'s `Send + Sync` requirement.
    /// In practice, access is always single-threaded.
    buckets: Mutex<HashMap<String, BucketState>>,
}

impl Default for TokenBucketRegistry {
    fn default() -> Self {
        Self::new()
    }
}

impl TokenBucketRegistry {

    /// Creates an empty registry.
    #[must_use]
    pub fn new() -> Self {
        Self {
            buckets: Mutex::new(HashMap::new()),
        }
    }

    /// Core check logic, separated from `PyO3` wrapper for testability.
    ///
    /// Uses a two-step lookup: `get_mut` for existing keys (no allocation,
    /// no `compute_refill_params` unless the period expired), `insert` for
    /// new keys. This avoids a `key.to_owned()` heap allocation on every
    /// check for existing keys.
    pub fn check_inner(
        &self,
        key: &str,
        config: &TokenBucketConfig,
        now_us: u64,
    ) -> Result<CheckResult, RateLimitError> {

        let burst_micro = config.burst_allowed.checked_mul(MICROTOKENS_PER_TOKEN).ok_or_else(|| {
            RateLimitError::new(format!("Overflow: burst_allowed ({}) * MICROTOKENS_PER_TOKEN", config.burst_allowed))
        })?;

        let mut map = self.buckets.lock();

        if let Some(bucket) = map.get_mut(key) {

            // #1: the current period has expired - recalculate the
            // refill rate and period boundary for the new period.
            if now_us >= bucket.period_end_us {
                let new_refill = compute_refill_params(
                    config.rate, config.parsed_time_unit, now_us,
                )?;
                bucket.refill_rate_micro_per_us = new_refill.rate_micro_per_us;
                bucket.period_end_us = new_refill.period_end_us;
            }

            return Ok(consume_or_deny(bucket, burst_micro, now_us));
        }

        // New key - compute refill params, insert with full tokens,
        // then run through consume_or_deny like existing keys.
        let refill = compute_refill_params(config.rate, config.parsed_time_unit, now_us)?;

        let bucket = map.entry(key.to_owned()).or_insert(BucketState {
            tokens_remaining_micro: burst_micro,
            last_refill_us: now_us,
            refill_rate_micro_per_us: refill.rate_micro_per_us,
            period_end_us: refill.period_end_us,
        });

        let result = consume_or_deny(bucket, burst_micro, now_us);
        drop(map);

        Ok(result)
    }

    /// Removes the bucket for the given key, if any.
    pub fn remove(&self, key: &str) {
        self.buckets.lock().remove(key);
    }

    /// Returns the number of active buckets.
    #[must_use]
    pub fn len(&self) -> usize {
        self.buckets.lock().len()
    }

    /// Returns `true` if no buckets are registered.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.buckets.lock().is_empty()
    }

    /// Removes all buckets.
    pub fn clear(&self) {
        self.buckets.lock().clear();
    }
}

#[pymethods]
impl TokenBucketRegistry {

    /// Creates an empty registry (`PyO3` constructor).
    #[new]
    fn new_impl() -> Self {
        Self::new()
    }

    /// Checks whether a request identified by `key` is allowed under the
    /// given bucket configuration.
    ///
    /// If no bucket exists for the key yet, one is created with full tokens.
    /// Returns a `CheckResult` with the allow/deny decision and metadata.
    fn check(&self, key: &str, config: &TokenBucketConfig) -> PyResult<CheckResult> {
        let now_us = current_time_us()?;
        Ok(self.check_inner(key, config, now_us)?)
    }

    /// Removes the bucket for the given key, if any.
    #[pyo3(name = "remove")]
    fn remove_impl(&self, key: &str) {
        self.remove(key);
    }

    /// Returns the number of active buckets.
    #[pyo3(name = "len")]
    fn len_impl(&self) -> usize {
        self.len()
    }

    /// Returns `true` if no buckets are registered.
    #[pyo3(name = "is_empty")]
    fn is_empty_impl(&self) -> bool {
        self.is_empty()
    }

    /// Removes all buckets.
    #[pyo3(name = "clear")]
    fn clear_impl(&self) {
        self.clear();
    }
}

/// Returns the current wall clock time in microseconds since Unix epoch.
fn current_time_us() -> Result<u64, RateLimitError> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|err| RateLimitError::new(format!("System clock before Unix epoch: {err}")))?;

    let micros = duration.as_micros();

    let micros_u64 = u64::try_from(micros).map_err(|_| {
        RateLimitError::new(format!("System clock microseconds too large for u64: {micros}"))
    })?;

    Ok(micros_u64)
}
