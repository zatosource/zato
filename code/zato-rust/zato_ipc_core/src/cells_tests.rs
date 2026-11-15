//! Unit tests of the rate limiting cells.

use proptest::prelude::*;

use super::*;
use crate::layout::RegionParams;
use crate::view::test_support::{new_words, small_params};

/// A clock reading in the year 2026, in microseconds since the epoch.
const NOW_US: u64 = 1_794_000_000_000_000;

/// Microtokens in one token, as the in-process registry counts them.
const MICROTOKENS_PER_TOKEN: u64 = 1_000_000;

/// The in-process token bucket of the server, for comparison with the shared cell.
struct InProcessBucket {

    /// Current balance in microtokens.
    tokens_micro: u64,

    /// Clock reading of the last refill, in microseconds.
    last_refill_us: u64,
}

impl InProcessBucket {

    /// Returns a full bucket created at the given clock reading.
    const fn new(params: TokenBucketParams, now_us: u64) -> Self {
        Self {
            tokens_micro: params.burst * MICROTOKENS_PER_TOKEN,
            last_refill_us: now_us,
        }
    }

    /// Decides one request as the in-process registry does.
    fn check(&mut self, params: TokenBucketParams, now_us: u64) -> bool {
        let burst_micro = params.burst * MICROTOKENS_PER_TOKEN;
        let elapsed_us = now_us.saturating_sub(self.last_refill_us);
        let added_micro = elapsed_us.saturating_mul(params.rate).min(burst_micro);

        self.tokens_micro = self.tokens_micro.saturating_add(added_micro).min(burst_micro);
        self.last_refill_us = now_us;

        if self.tokens_micro >= MICROTOKENS_PER_TOKEN {
            self.tokens_micro -= MICROTOKENS_PER_TOKEN;
            true
        } else {
            false
        }
    }
}

/// Returns a view of a new region of the given sizes.
fn new_view(params: RegionParams) -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(params)?;
    RegionView::new(words, layout)
}

/// Returns the key of the first time range of the orders channel.
fn orders_key() -> CellKey {
    CellKey::new("rest.orders:0", "rest.orders:")
}

/// Returns the key of the first time range of the invoices channel.
fn invoices_key() -> CellKey {
    CellKey::new("rest.invoices:0", "rest.invoices:")
}

/// Returns the key of one time range of the network rule of the orders channel.
fn network_key(time_range_index: u64) -> CellKey {
    CellKey::new(&format!("rest.orders:10.0.0.0/8:{time_range_index}"), "rest.orders:10.0.0.0/8:")
}

#[test]
fn bucket_allows_its_burst_then_denies() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = TokenBucketParams { rate: 1, burst: 3 };

    let first = view.token_bucket_check(&network_key(0), params, NOW_US)?;
    assert_eq!(first, CellCheck::allowed(2));

    view.token_bucket_check(&network_key(0), params, NOW_US)?;
    let third = view.token_bucket_check(&network_key(0), params, NOW_US)?;
    assert_eq!(third, CellCheck::allowed(0));

    let fourth = view.token_bucket_check(&network_key(0), params, NOW_US)?;
    assert!(!fourth.is_allowed);
    assert_eq!(fourth.retry_after_us, MICROS_PER_SECOND);

    Ok(())
}

#[test]
fn bucket_refills_one_token_per_interval() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = TokenBucketParams { rate: 2, burst: 1 };

    assert!(view.token_bucket_check(&orders_key(), params, NOW_US)?.is_allowed);
    assert!(!view.token_bucket_check(&orders_key(), params, NOW_US + 499_999)?.is_allowed);
    assert!(view.token_bucket_check(&orders_key(), params, NOW_US + 500_000)?.is_allowed);

    Ok(())
}

#[test]
fn earlier_clock_reading_adds_no_tokens() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = TokenBucketParams { rate: 1, burst: 1 };

    // The second worker's clock reads one second earlier than the first one's.
    assert!(
        view.token_bucket_check(&orders_key(), params, NOW_US + MICROS_PER_SECOND)?
            .is_allowed
    );
    assert!(!view.token_bucket_check(&orders_key(), params, NOW_US)?.is_allowed);

    // The first worker's next request a second later counts the interval once.
    assert!(
        view.token_bucket_check(&orders_key(), params, NOW_US + 2 * MICROS_PER_SECOND)?
            .is_allowed
    );
    assert!(
        !view
            .token_bucket_check(&orders_key(), params, NOW_US + 2 * MICROS_PER_SECOND)?
            .is_allowed
    );

    Ok(())
}

#[test]
fn bucket_with_zero_rate_never_refills() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = TokenBucketParams { rate: 0, burst: 2 };

    assert_eq!(view.token_bucket_check(&orders_key(), params, NOW_US)?, CellCheck::allowed(1));
    assert_eq!(view.token_bucket_check(&orders_key(), params, NOW_US)?, CellCheck::allowed(0));

    let later = NOW_US + 3600 * MICROS_PER_SECOND;
    assert_eq!(
        view.token_bucket_check(&orders_key(), params, later)?,
        CellCheck::denied(NO_REFILL_RETRY_US)
    );

    Ok(())
}

#[test]
fn bucket_with_zero_burst_allows_nothing() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = TokenBucketParams { rate: 4, burst: 0 };

    assert_eq!(view.token_bucket_check(&orders_key(), params, NOW_US)?, CellCheck::denied(250_001));

    Ok(())
}

#[test]
fn window_counts_up_to_its_limit() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let window_end_us = NOW_US + 60 * MICROS_PER_SECOND;
    let params = FixedWindowParams { limit: 2, window_end_us };

    assert_eq!(view.fixed_window_check(&orders_key(), params, NOW_US)?, CellCheck::allowed(1));
    assert_eq!(view.fixed_window_check(&orders_key(), params, NOW_US + 1)?, CellCheck::allowed(0));

    let denied = view.fixed_window_check(&orders_key(), params, NOW_US + 10 * MICROS_PER_SECOND)?;
    assert_eq!(denied, CellCheck::denied(50 * MICROS_PER_SECOND));

    Ok(())
}

#[test]
fn window_starts_again_after_its_end() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let first_end_us = NOW_US + 60 * MICROS_PER_SECOND;
    let second_end_us = first_end_us + 60 * MICROS_PER_SECOND;

    let first = FixedWindowParams {
        limit: 1,
        window_end_us: first_end_us,
    };
    let second = FixedWindowParams {
        limit: 1,
        window_end_us: second_end_us,
    };

    assert!(view.fixed_window_check(&orders_key(), first, NOW_US)?.is_allowed);
    assert!(!view.fixed_window_check(&orders_key(), first, NOW_US + 1)?.is_allowed);
    assert!(view.fixed_window_check(&orders_key(), second, first_end_us)?.is_allowed);

    Ok(())
}

#[test]
fn group_reset_clears_only_its_group() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = TokenBucketParams { rate: 1, burst: 1 };

    view.token_bucket_check(&network_key(0), params, NOW_US)?;
    view.token_bucket_check(&network_key(1), params, NOW_US)?;
    view.token_bucket_check(&invoices_key(), params, NOW_US)?;

    view.cell_reset_group("rest.orders:10.0.0.0/8:")?;

    assert!(view.token_bucket_check(&network_key(0), params, NOW_US)?.is_allowed);
    assert!(view.token_bucket_check(&network_key(1), params, NOW_US)?.is_allowed);
    assert!(!view.token_bucket_check(&invoices_key(), params, NOW_US)?.is_allowed);

    Ok(())
}

#[test]
fn group_reset_clears_a_cell_whose_claimer_stopped_before_storing_the_group() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = FixedWindowParams {
        limit: 1,
        window_end_us: NOW_US + 60 * MICROS_PER_SECOND,
    };

    // A worker claims the cell of the key and stops before it stores the group, as a terminated worker leaves it.
    let hash = key_hash(FIXED_WINDOW_KIND, "rest.orders:0");
    let entry = probe_start(hash, view.layout().params.cell_capacity);
    view.word(view.cell_word(entry, CELL_KEY)?)?.store(hash, Ordering::SeqCst);

    // Another worker spends the limit of the window in that cell.
    assert!(view.fixed_window_check(&orders_key(), params, NOW_US)?.is_allowed);
    assert!(!view.fixed_window_check(&orders_key(), params, NOW_US)?.is_allowed);

    // The clear of the counters of the rule gives the window its limit again.
    view.cell_reset_group("rest.orders:")?;
    assert!(view.fixed_window_check(&orders_key(), params, NOW_US)?.is_allowed);

    Ok(())
}

#[test]
fn key_reset_keeps_the_cell_of_a_later_key() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        cell_capacity: 2,
        ..small_params()
    })?;
    let params = TokenBucketParams { rate: 1, burst: 1 };

    view.token_bucket_check(&orders_key(), params, NOW_US)?;
    view.token_bucket_check(&invoices_key(), params, NOW_US)?;

    view.cell_reset("rest.orders:0")?;

    // Both keys still have their cells, so the table of two cells takes neither key a second time.
    assert!(view.token_bucket_check(&orders_key(), params, NOW_US)?.is_allowed);
    assert!(!view.token_bucket_check(&invoices_key(), params, NOW_US)?.is_allowed);

    Ok(())
}

#[test]
fn full_table_refuses_a_new_key() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        cell_capacity: 1,
        ..small_params()
    })?;
    let params = TokenBucketParams { rate: 1, burst: 1 };

    view.token_bucket_check(&orders_key(), params, NOW_US)?;
    let refused = view.token_bucket_check(&invoices_key(), params, NOW_US);

    assert_eq!(refused, Err(RegionError::TableFull));

    Ok(())
}

#[test]
fn concurrent_checks_allow_the_limit_exactly() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let params = FixedWindowParams {
        limit: 500,
        window_end_us: NOW_US + 60 * MICROS_PER_SECOND,
    };
    let allowed = AtomicU64::new(0);

    std::thread::scope(|scope| {
        for _ in 0..4 {
            scope.spawn(|| {
                for _ in 0..1000 {
                    if let Ok(check) = view.fixed_window_check(&orders_key(), params, NOW_US)
                        && check.is_allowed
                    {
                        allowed.fetch_add(1, Ordering::SeqCst);
                    }
                }
            });
        }
    });

    assert_eq!(allowed.load(Ordering::SeqCst), 500);

    Ok(())
}

proptest! {

    /// For clock readings that never go back, the shared bucket decides every request as the in-process bucket does.
    #[test]
    fn bucket_matches_in_process_bucket(
        rate in prop::sample::select(vec![1_u64, 2, 4, 5, 8, 10, 20, 25, 50, 100, 1000]),
        burst in 1_u64..20,
        steps in prop::collection::vec(0_u64..400_000, 1..200),
    ) {
        let view = new_view(small_params()).map_err(|error| TestCaseError::fail(error.to_string()))?;
        let params = TokenBucketParams { rate, burst };
        let mut in_process = InProcessBucket::new(params, NOW_US);
        let mut now_us = NOW_US;

        for step in steps {
            now_us += step;

            let shared = view.token_bucket_check(&orders_key(), params, now_us)
                .map_err(|error| TestCaseError::fail(error.to_string()))?;
            let expected = in_process.check(params, now_us);

            prop_assert_eq!(shared.is_allowed, expected);
        }
    }
}
