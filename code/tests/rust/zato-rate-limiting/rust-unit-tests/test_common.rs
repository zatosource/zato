use chrono::Utc;
use zato_rate_limiting_core::common::{RateLimitError, RateLimitResult, current_time_us, MICROSECONDS_PER_SECOND};
use zato_rate_limiting_core::token_bucket::CheckResult;

#[test]
fn error_display() {
    let err = RateLimitError::new("boom");
    assert_eq!(format!("{err}"), "boom");
}

#[test]
fn error_debug_contains_msg() {
    let err = RateLimitError::new("test error");
    let debug = format!("{err:?}");
    assert!(debug.contains("test error"), "Debug output must contain the message, got: {debug}");
}

#[test]
fn microseconds_per_second_value() {
    assert_eq!(MICROSECONDS_PER_SECOND, 1_000_000);
}

struct MockResult {
    allowed: bool,
    retry: u64,
}

impl RateLimitResult for MockResult {
    fn is_allowed(&self) -> bool {
        self.allowed
    }
    fn retry_after_us(&self) -> u64 {
        self.retry
    }
}

#[test]
fn trait_is_allowed_true() {
    let result = MockResult { allowed: true, retry: 0 };
    assert!(result.is_allowed());
    assert_eq!(result.retry_after_us(), 0);
}

#[test]
fn trait_is_allowed_false() {
    let result = MockResult { allowed: false, retry: 5000 };
    assert!(!result.is_allowed());
    assert_eq!(result.retry_after_us(), 5000);
}

#[test]
fn current_time_us_returns_nonzero() {
    let now = current_time_us().expect("current_time_us must succeed");
    assert!(now > 0);
}

#[test]
fn current_time_us_is_plausible() {
    let now = current_time_us().expect("current_time_us must succeed");
    assert!(now > 1_700_000_000_000_000, "Timestamp must be after ~2023-11-14, got: {now}");
}

#[test]
fn check_result_trait_allowed() {
    let result = CheckResult { allowed: true, tokens_remaining: 5, retry_after_us: 0 };
    assert!(result.is_allowed());
    assert_eq!(result.retry_after_us(), 0);
}

#[test]
fn check_result_trait_denied() {
    let result = CheckResult { allowed: false, tokens_remaining: 0, retry_after_us: 1234 };
    assert!(!result.is_allowed());
    assert_eq!(result.retry_after_us(), 1234);
}

#[test]
fn error_new_with_string() {
    let owned = String::from("owned message");
    let err = RateLimitError::new(owned);
    assert_eq!(format!("{err}"), "owned message");
}

#[test]
fn error_source_is_none() {
    use std::error::Error;
    let err = RateLimitError::new("x");
    assert!(err.source().is_none());
}

#[test]
fn chrono_dependency_works() {
    let now = Utc::now();
    assert!(now.timestamp() > 0);
}
