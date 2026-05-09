use proptest::prelude::*;
use zato_rate_limiting_core::token_bucket::{TokenBucketConfig, TokenBucketRegistry};

proptest! {
    #[test]
    fn first_check_always_allowed(
        rate in 1u64..1_000_000,
        burst in 1u64..10_000,
        now_us in 1_000_000_000_000u64..2_000_000_000_000u64,
    ) {
        let registry = TokenBucketRegistry::new();
        let config = TokenBucketConfig::from_parts(rate, burst);
        let result = registry.check_inner("prop_key", &config, now_us)
            .map_err(|err| TestCaseError::Fail(format!("{err}").into()))?;
        prop_assert!(result.allowed, "First request must always be allowed");
    }

    #[test]
    fn tokens_never_exceed_burst(
        rate in 1u64..100_000,
        burst in 1u64..1_000,
        now_us in 1_000_000_000_000u64..2_000_000_000_000u64,
    ) {
        let registry = TokenBucketRegistry::new();
        let config = TokenBucketConfig::from_parts(rate, burst);
        let result = registry.check_inner("prop_key", &config, now_us)
            .map_err(|err| TestCaseError::Fail(format!("{err}").into()))?;
        prop_assert!(
            result.tokens_remaining < burst,
            "After consuming one token, remaining ({}) must be < burst ({})",
            result.tokens_remaining,
            burst,
        );
    }

    #[test]
    fn exhaustion_then_deny(
        rate in 1u64..1_000,
        burst in 1u64..50,
        now_us in 1_000_000_000_000u64..2_000_000_000_000u64,
    ) {
        let registry = TokenBucketRegistry::new();
        let config = TokenBucketConfig::from_parts(rate, burst);
        for _ in 0..burst {
            let _ = registry.check_inner("exhaust", &config, now_us)
                .map_err(|err| TestCaseError::Fail(format!("{err}").into()))?;
        }
        let result = registry.check_inner("exhaust", &config, now_us)
            .map_err(|err| TestCaseError::Fail(format!("{err}").into()))?;
        prop_assert!(!result.allowed, "After exhausting all {} tokens, next must be denied", burst);
        prop_assert!(result.retry_after_us > 0, "Denied request must have retry_after_us > 0");
    }
}
