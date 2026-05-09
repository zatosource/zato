#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_rate_limiting_core::token_bucket::{TimeUnit, TokenBucketConfig, TokenBucketRegistry};

fuzz_target!(|data: &[u8]| {
    if data.len() < 25 {
        return;
    }

    let rate = u64::from_le_bytes([
        data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
    ]);
    let burst_allowed = u64::from_le_bytes([
        data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15],
    ]);
    let now_us = u64::from_le_bytes([
        data[16], data[17], data[18], data[19], data[20], data[21], data[22], data[23],
    ]);

    let time_unit = match data[24] {
        0 => TimeUnit::Second,
        1 => TimeUnit::Minute,
        2 => TimeUnit::Hour,
        3 => TimeUnit::Day,
        _ => TimeUnit::Month,
    };

    let config = TokenBucketConfig::from_parts(rate, time_unit, burst_allowed);
    let registry = TokenBucketRegistry::new();

    if let Ok(result) = registry.check_inner("fuzz_key", &config, now_us) {
        assert!(result.tokens_remaining <= burst_allowed);
    }
});
