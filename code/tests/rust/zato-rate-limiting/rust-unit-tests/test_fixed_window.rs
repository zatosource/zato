use zato_rate_limiting_core::common::RateLimitResult;
use zato_rate_limiting_core::fixed_window::{
    FixedWindowCheckResult, FixedWindowConfig, FixedWindowRegistry,
    WindowUnit, compute_window_end_us,
};

#[test]
fn window_unit_from_str_second() {
    assert_eq!("second".parse::<WindowUnit>().expect("must parse"), WindowUnit::Second);
}

#[test]
fn window_unit_from_str_minute() {
    assert_eq!("minute".parse::<WindowUnit>().expect("must parse"), WindowUnit::Minute);
}

#[test]
fn window_unit_from_str_hour() {
    assert_eq!("hour".parse::<WindowUnit>().expect("must parse"), WindowUnit::Hour);
}

#[test]
fn window_unit_from_str_day() {
    assert_eq!("day".parse::<WindowUnit>().expect("must parse"), WindowUnit::Day);
}

#[test]
fn window_unit_from_str_month() {
    assert_eq!("month".parse::<WindowUnit>().expect("must parse"), WindowUnit::Month);
}

#[test]
fn window_unit_from_str_invalid() {
    assert!("bogus".parse::<WindowUnit>().is_err());
}

#[test]
fn window_unit_from_str_error_message_content() {
    let err = "bogus".parse::<WindowUnit>().unwrap_err();
    let msg = format!("{err}");
    assert!(msg.contains("bogus"), "Error message must contain the invalid input, got: {msg}");
}

#[test]
fn as_str_all_variants() {
    assert_eq!(WindowUnit::Second.as_str(), "second");
    assert_eq!(WindowUnit::Minute.as_str(), "minute");
    assert_eq!(WindowUnit::Hour.as_str(), "hour");
    assert_eq!(WindowUnit::Day.as_str(), "day");
    assert_eq!(WindowUnit::Month.as_str(), "month");
}

#[test]
fn window_unit_display_round_trips() {
    let units = [
        WindowUnit::Second,
        WindowUnit::Minute,
        WindowUnit::Hour,
        WindowUnit::Day,
        WindowUnit::Month,
    ];
    for unit in units {
        let text = format!("{unit}");
        let parsed: WindowUnit = text.parse().expect("round-trip must succeed");
        assert_eq!(parsed, unit);
    }
}

// ------------------------------------------ compute_window_end_us: Second

#[test]
fn second_boundary_mid_second() {
    let now_us = 1_700_000_000_500_000;
    let end = compute_window_end_us(WindowUnit::Second, now_us).expect("must succeed");
    assert_eq!(end, 1_700_000_001_000_000);
}

#[test]
fn second_boundary_exact_second() {
    let now_us = 1_700_000_000_000_000;
    let end = compute_window_end_us(WindowUnit::Second, now_us).expect("must succeed");
    assert_eq!(end, 1_700_000_001_000_000);
}

#[test]
fn second_boundary_last_microsecond() {
    let now_us = 1_700_000_000_999_999;
    let end = compute_window_end_us(WindowUnit::Second, now_us).expect("must succeed");
    assert_eq!(end, 1_700_000_001_000_000);
}

// ------------------------------------------ compute_window_end_us: Minute
// Base minute starts at epoch second 1_699_999_980 (1_699_999_980 % 60 == 0).
// Next minute boundary = 1_700_000_040.

#[test]
fn minute_boundary_mid_minute() {
    // 45 seconds into the minute
    let now_us = 1_700_000_025_000_000;
    let end = compute_window_end_us(WindowUnit::Minute, now_us).expect("must succeed");
    assert_eq!(end, 1_700_000_040_000_000);
}

#[test]
fn minute_boundary_start_of_minute() {
    let now_us = 1_699_999_980_000_000;
    let end = compute_window_end_us(WindowUnit::Minute, now_us).expect("must succeed");
    assert_eq!(end, 1_700_000_040_000_000);
}

#[test]
fn minute_boundary_last_second() {
    // 59.999 seconds into the minute
    let now_us = 1_700_000_039_999_000;
    let end = compute_window_end_us(WindowUnit::Minute, now_us).expect("must succeed");
    assert_eq!(end, 1_700_000_040_000_000);
}

// ------------------------------------------ compute_window_end_us: Hour
// 1_700_000_000 % 3600 == 800, so hour starts at 1_699_999_200.
// Next hour boundary = 1_700_002_800.

#[test]
fn hour_boundary_mid_hour() {
    let now_us = 1_700_000_000_000_000;
    let end = compute_window_end_us(WindowUnit::Hour, now_us).expect("must succeed");
    assert_eq!(end, 1_700_002_800_000_000);
}

#[test]
fn hour_boundary_start_of_hour() {
    let now_us = 1_699_999_200_000_000;
    let end = compute_window_end_us(WindowUnit::Hour, now_us).expect("must succeed");
    assert_eq!(end, 1_700_002_800_000_000);
}

#[test]
fn hour_boundary_last_second() {
    let now_us = 1_700_002_799_999_000;
    let end = compute_window_end_us(WindowUnit::Hour, now_us).expect("must succeed");
    assert_eq!(end, 1_700_002_800_000_000);
}

// ------------------------------------------ compute_window_end_us: Day
// 1_700_000_000 % 86400 == 80_000, so day starts at 1_699_920_000.
// Next day boundary = 1_700_006_400.

#[test]
fn day_boundary_mid_day() {
    let now_us = 1_700_000_000_000_000;
    let end = compute_window_end_us(WindowUnit::Day, now_us).expect("must succeed");
    assert_eq!(end, 1_700_006_400_000_000);
}

#[test]
fn day_boundary_start_of_day() {
    let now_us = 1_699_920_000_000_000;
    let end = compute_window_end_us(WindowUnit::Day, now_us).expect("must succeed");
    assert_eq!(end, 1_700_006_400_000_000);
}

#[test]
fn day_boundary_last_second() {
    let now_us = 1_700_006_399_999_000;
    let end = compute_window_end_us(WindowUnit::Day, now_us).expect("must succeed");
    assert_eq!(end, 1_700_006_400_000_000);
}

// ------------------------------------------ compute_window_end_us: Month

#[test]
fn month_boundary_february() {
    // Feb 15 2023 00:00:00 UTC -> next = Mar 1 2023
    let now_us = 1_676_419_200_000_000;
    let end = compute_window_end_us(WindowUnit::Month, now_us).expect("must succeed");
    assert_eq!(end, 1_677_628_800_000_000);
}

#[test]
fn month_boundary_february_leap() {
    // Feb 15 2024 00:00:00 UTC (leap year) -> next = Mar 1 2024
    let now_us = 1_707_955_200_000_000;
    let end = compute_window_end_us(WindowUnit::Month, now_us).expect("must succeed");
    assert_eq!(end, 1_709_251_200_000_000);
}

#[test]
fn month_boundary_december() {
    // Dec 15 2023 00:00:00 UTC -> next = Jan 1 2024
    let now_us = 1_702_598_400_000_000;
    let end = compute_window_end_us(WindowUnit::Month, now_us).expect("must succeed");
    assert_eq!(end, 1_704_067_200_000_000);
}

#[test]
fn month_boundary_january() {
    // Jan 20 2024 00:00:00 UTC -> next = Feb 1 2024
    let now_us = 1_705_708_800_000_000;
    let end = compute_window_end_us(WindowUnit::Month, now_us).expect("must succeed");
    assert_eq!(end, 1_706_745_600_000_000);
}

#[test]
fn month_boundary_last_day() {
    // Mar 31 2024 23:59:59 UTC -> next = Apr 1 2024
    let now_us = 1_711_929_599_000_000;
    let end = compute_window_end_us(WindowUnit::Month, now_us).expect("must succeed");
    assert_eq!(end, 1_711_929_600_000_000);
}

#[test]
fn month_boundary_invalid_timestamp() {
    assert!(compute_window_end_us(WindowUnit::Month, u64::MAX).is_err());
}

// ------------------------------------------ FixedWindowConfig

#[test]
fn config_from_parts() {
    let config = FixedWindowConfig::from_parts(100, WindowUnit::Minute);
    assert_eq!(config.limit, 100);
    assert_eq!(config.unit(), WindowUnit::Minute);
}

#[test]
fn config_from_parts_all_units() {
    let units = [
        (WindowUnit::Second, "second"),
        (WindowUnit::Minute, "minute"),
        (WindowUnit::Hour, "hour"),
        (WindowUnit::Day, "day"),
        (WindowUnit::Month, "month"),
    ];
    for (unit, label) in units {
        let config = FixedWindowConfig::from_parts(50, unit);
        assert_eq!(config.unit(), unit);
        assert_eq!(config.unit().as_str(), label);
    }
}

// ------------------------------------------ FixedWindowCheckResult + RateLimitResult

#[test]
fn fw_check_result_trait_allowed() {
    let result = FixedWindowCheckResult {
        is_allowed: true,
        remaining: 99,
        retry_after_us: 0,
    };
    assert!(result.is_allowed());
    assert_eq!(result.remaining, 99);
    assert_eq!(result.retry_after_us(), 0);
}

#[test]
fn fw_check_result_trait_denied() {
    let result = FixedWindowCheckResult {
        is_allowed: false,
        remaining: 0,
        retry_after_us: 5000,
    };
    assert!(!result.is_allowed());
    assert_eq!(result.remaining, 0);
    assert_eq!(result.retry_after_us(), 5000);
}

// ------------------------------------------ Registry test helpers

/// Creates a registry, exhausts limit=1, and returns (registry, config, denied_result).
fn exhaust_one(unit: WindowUnit, now_us: u64) -> (FixedWindowRegistry, FixedWindowConfig, FixedWindowCheckResult) {
    let registry = FixedWindowRegistry::new();
    let config = FixedWindowConfig::from_parts(1, unit);

    let first = registry.check_inner("k", &config, now_us).expect("must succeed");
    assert!(first.is_allowed());

    let denied = registry.check_inner("k", &config, now_us).expect("must succeed");
    assert!(!denied.is_allowed());

    (registry, config, denied)
}

// ------------------------------------------ FixedWindowRegistry: Second

#[test]
fn second_allow_up_to_limit_then_deny() {
    let registry = FixedWindowRegistry::new();
    let config = FixedWindowConfig::from_parts(3, WindowUnit::Second);
    let now_us = 1_700_000_000_500_000;

    for _ in 0..3 {
        let result = registry.check_inner("k", &config, now_us).expect("must succeed");
        assert!(result.is_allowed());
    }

    let denied = registry.check_inner("k", &config, now_us).expect("must succeed");
    assert!(!denied.is_allowed());
}

#[test]
fn second_zero_limit_always_denies() {
    let registry = FixedWindowRegistry::new();
    let config = FixedWindowConfig::from_parts(0, WindowUnit::Second);
    let now_us = 1_700_000_000_500_000;

    let result = registry.check_inner("k", &config, now_us).expect("must succeed");
    assert!(!result.is_allowed());
}

#[test]
fn second_remaining_decrements() {
    let registry = FixedWindowRegistry::new();
    let config = FixedWindowConfig::from_parts(5, WindowUnit::Second);
    let now_us = 1_700_000_000_500_000;

    for expected_remaining in (0..5).rev() {
        let result = registry.check_inner("k", &config, now_us).expect("must succeed");
        assert_eq!(result.remaining, expected_remaining);
    }
}

#[test]
fn second_window_reset() {
    // now_us is mid-second, window ends at 1_700_000_001_000_000.
    let (registry, config, _denied) = exhaust_one(WindowUnit::Second, 1_700_000_000_500_000);

    // Advance to the next second boundary.
    let after_reset = registry.check_inner("k", &config, 1_700_000_001_000_000).expect("must succeed");
    assert!(after_reset.is_allowed());
}

#[test]
fn second_retry_after_is_correct() {
    // now_us is mid-second, window ends at 1_700_000_001_000_000.
    let (_registry, _config, denied) = exhaust_one(WindowUnit::Second, 1_700_000_000_500_000);

    // 1_700_000_001_000_000 - 1_700_000_000_500_000 = 500_000 us.
    assert_eq!(denied.retry_after_us(), 500_000);
}

// ------------------------------------------ FixedWindowRegistry: Minute
// Base minute starts at epoch second 1_699_999_980.
// now_us at second 1_700_000_005 = 25 seconds into the minute.
// Next minute boundary = 1_700_000_040.

#[test]
fn minute_window_reset_allows_again() {
    let (registry, config, _denied) = exhaust_one(WindowUnit::Minute, 1_700_000_005_000_000);

    // Advance past the minute boundary.
    let after_reset = registry.check_inner("k", &config, 1_700_000_040_000_000).expect("must succeed");
    assert!(after_reset.is_allowed());
}

#[test]
fn minute_retry_after_is_correct() {
    let (_registry, _config, denied) = exhaust_one(WindowUnit::Minute, 1_700_000_005_000_000);

    // 1_700_000_040_000_000 - 1_700_000_005_000_000 = 35_000_000 us (35 seconds).
    assert_eq!(denied.retry_after_us(), 35_000_000);
}
