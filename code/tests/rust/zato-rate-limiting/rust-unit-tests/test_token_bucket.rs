use zato_rate_limiting_core::token_bucket::{TokenBucketConfig, TokenBucketRegistry};

type TestResult = Result<(), Box<dyn std::error::Error>>;

#[test]
fn allow_exactly_burst_then_deny() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_700_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(100, 5);

    for idx in 0..5 {
        let result = registry.check_inner("key_a", &config, now)?;
        assert!(result.allowed, "Request {idx} of 5 must be allowed");
        assert_eq!(result.tokens_remaining, 4 - idx);
    }

    let denied = registry.check_inner("key_a", &config, now)?;
    assert!(!denied.allowed);
    assert_eq!(denied.tokens_remaining, 0);

    Ok(())
}

#[test]
fn retry_after_is_positive_on_deny() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_700_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(1, 1);

    let _ = registry.check_inner("key_b", &config, now)?;
    let denied = registry.check_inner("key_b", &config, now)?;
    assert!(!denied.allowed);
    assert!(denied.retry_after_us > 0);

    Ok(())
}

#[test]
fn refill_restores_tokens() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_700_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(10, 1);

    let _ = registry.check_inner("key_c", &config, now)?;
    let denied = registry.check_inner("key_c", &config, now)?;
    assert!(!denied.allowed);

    let later = now + 200_000;
    let restored = registry.check_inner("key_c", &config, later)?;
    assert!(restored.allowed);

    Ok(())
}

#[test]
fn separate_keys_are_independent() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_700_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(1, 1);

    let _ = registry.check_inner("key_x", &config, now)?;
    let denied = registry.check_inner("key_x", &config, now)?;
    assert!(!denied.allowed);

    let other = registry.check_inner("key_y", &config, now)?;
    assert!(other.allowed);

    Ok(())
}

#[test]
fn burst_cap_after_long_idle() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_700_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(10, 3);

    let _ = registry.check_inner("key_d", &config, now)?;

    let much_later = now + 999_000_000_000;
    let result = registry.check_inner("key_d", &config, much_later)?;
    assert!(result.allowed);
    assert_eq!(result.tokens_remaining, 2, "After long idle, bucket refills to burst_allowed");

    Ok(())
}

#[test]
fn remove_clears_bucket() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_700_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(1, 1);

    let _ = registry.check_inner("key_f", &config, now)?;
    let denied = registry.check_inner("key_f", &config, now)?;
    assert!(!denied.allowed);

    registry.remove("key_f");

    let fresh = registry.check_inner("key_f", &config, now)?;
    assert!(fresh.allowed, "After remove, bucket starts fresh");

    Ok(())
}

#[test]
fn clear_removes_all_buckets() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let now = 1_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(10, 5);

    let _ = registry.check_inner("a", &config, now)?;
    let _ = registry.check_inner("b", &config, now)?;
    assert_eq!(registry.len(), 2);

    registry.remove("a");
    assert_eq!(registry.len(), 1);

    registry.clear();
    assert!(registry.is_empty());

    Ok(())
}

#[test]
fn basic_allow_and_deny() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let key = "chan:1:apikey:42";
    let now = 1_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(10, 3);

    let result = registry.check_inner(key, &config, now)?;
    assert!(result.allowed);
    assert_eq!(result.tokens_remaining, 2);

    let result = registry.check_inner(key, &config, now)?;
    assert!(result.allowed);
    assert_eq!(result.tokens_remaining, 1);

    let result = registry.check_inner(key, &config, now)?;
    assert!(result.allowed);
    assert_eq!(result.tokens_remaining, 0);

    let result = registry.check_inner(key, &config, now)?;
    assert!(!result.allowed);
    assert_eq!(result.tokens_remaining, 0);
    assert!(result.retry_after_us > 0);

    Ok(())
}

#[test]
fn refill_after_time_passes() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let key = "chan:1:ip:10.0.0.1";
    let now = 1_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(10, 3);

    for _ in 0..3 {
        let _ = registry.check_inner(key, &config, now)?;
    }

    let result = registry.check_inner(key, &config, now)?;
    assert!(!result.allowed);

    let later = now + 500_000;
    let result = registry.check_inner(key, &config, later)?;
    assert!(result.allowed);

    Ok(())
}

#[test]
fn burst_cap() -> TestResult {
    let registry = TokenBucketRegistry::new();
    let key = "chan:2:apikey:99";
    let now = 1_000_000_000_000u64;
    let config = TokenBucketConfig::from_parts(10, 5);

    let result = registry.check_inner(key, &config, now)?;
    assert!(result.allowed);
    assert_eq!(result.tokens_remaining, 4);

    let _ = registry.check_inner(key, &config, now)?;
    let _ = registry.check_inner(key, &config, now)?;
    let _ = registry.check_inner(key, &config, now)?;
    let _ = registry.check_inner(key, &config, now)?;

    let much_later = now + 100_000_000_000;
    let result = registry.check_inner(key, &config, much_later)?;
    assert!(result.allowed);
    assert_eq!(result.tokens_remaining, 4);

    Ok(())
}
