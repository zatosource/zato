//! Token bucket rate limiter with lazy refill and O(1) per-check cost.
//!
//! Each bucket holds two plain `u64` fields: token balance and last refill
//! timestamp. The refill rate is constant for the lifetime of a config and
//! is precomputed at construction time. All access is single-threaded
//! by design. A `parking_lot::Mutex` wraps the `HashMap` only to satisfy
//! `PyO3`'s `Send + Sync` requirement on `#[pyclass]` types.
//!
//! Buckets live in a `HashMap` keyed by an arbitrary string that the Python
//! caller provides.

use std::collections::HashMap;
use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

use parking_lot::Mutex;
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

/// One token expressed in microtokens (fixed-point arithmetic avoids floating point).
const MICROTOKENS_PER_TOKEN: u64 = 1_000_000;

/// One second expressed in microseconds (for time conversions).
const MICROSECONDS_PER_SECOND: u64 = 1_000_000;

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

// ----------------------------------------------------------- bucket internals

/// Internal bucket state stored per key.
///
/// Both fields are plain `u64` values - no atomics, no mutexes.
/// Single-threaded access is guaranteed by design.
struct BucketState {

    /// Current token balance in microtokens (1 token = `1_000_000` microtokens).
    tokens_remaining_micro: u64,

    /// Microseconds since Unix epoch when tokens were last refilled.
    last_refill_us: u64,
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

/// Python-visible configuration for a single token bucket.
///
/// The user provides `rate` (tokens per second) and `burst_allowed`
/// (maximum tokens the bucket can hold). The refill rate in
/// microtokens per microsecond is precomputed at construction time.
#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct TokenBucketConfig {

    /// Tokens added per second.
    #[pyo3(get)]
    pub rate: u64,

    /// Maximum burst size (bucket capacity).
    #[pyo3(get)]
    pub burst_allowed: u64,

    /// Precomputed refill speed: microtokens added per microsecond.
    refill_rate_micro_per_us: u64,
}

impl TokenBucketConfig {
    /// Rust-only constructor for tests and fuzz targets.
    #[must_use]
    pub const fn from_parts(rate: u64, burst_allowed: u64) -> Self {
        Self {
            rate,
            burst_allowed,
            refill_rate_micro_per_us: rate,
        }
    }
}

#[pymethods]
impl TokenBucketConfig {
    /// Creates a new token bucket configuration.
    ///
    /// `rate` is tokens per second. `burst_allowed` is the maximum
    /// number of tokens the bucket can hold (the spike tolerance).
    #[new]
    #[expect(clippy::missing_const_for_fn, reason = "PyO3 #[new] cannot be const")]
    fn new(rate: u64, burst_allowed: u64) -> Self {
        Self {
            rate,
            burst_allowed,
            refill_rate_micro_per_us: rate,
        }
    }
}

// --------------------------------------------------------- consume or deny

/// Refills tokens based on elapsed time, clamps to burst limit, then
/// either deducts one token (allow) or records the deficit (deny).
fn consume_or_deny(
    bucket: &mut BucketState,
    config: &TokenBucketConfig,
    burst_micro: u64,
    now_us: u64,
) -> CheckResult {

    // Microseconds elapsed since the last refill. saturating_sub
    // guards against clock skew where now_us < last_refill_us.
    let elapsed_us = now_us.saturating_sub(bucket.last_refill_us);

    // Compute how many microtokens have accumulated since the
    // last refill, then add them to the current balance.
    let added_micro = elapsed_us.saturating_mul(config.refill_rate_micro_per_us);
    let refilled = bucket.tokens_remaining_micro.saturating_add(added_micro);

    // Clamp the balance to the burst limit so tokens
    // never accumulate beyond the configured maximum.
    let capped = refilled.min(burst_micro);

    // Update the refill timestamp.
    bucket.last_refill_us = now_us;

    // Enough tokens to allow the request.
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

    // Not enough tokens - deny the request.
    bucket.tokens_remaining_micro = capped;

    // How many microtokens are missing to reach one full token.
    let deficit_micro = MICROTOKENS_PER_TOKEN - capped;

    // Estimate how many microseconds the caller should wait
    // before retrying. When refill_rate is zero (rate=0 policy),
    // fall back to one full second.
    let retry_us = match deficit_micro.checked_div(config.refill_rate_micro_per_us) {
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
    /// Uses a two-step lookup: `get_mut` for existing keys (no allocation),
    /// `insert` for new keys. This avoids a `key.to_owned()` heap allocation
    /// on every check for existing keys.
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
            return Ok(consume_or_deny(bucket, config, burst_micro, now_us));
        }

        let bucket = map.entry(key.to_owned()).or_insert(BucketState {
            tokens_remaining_micro: burst_micro,
            last_refill_us: now_us,
        });

        let result = consume_or_deny(bucket, config, burst_micro, now_us);
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
