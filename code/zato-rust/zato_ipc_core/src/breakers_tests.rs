//! Unit tests of the circuit breakers.

use std::sync::Barrier;
use std::thread;

use super::*;
use crate::layout::RegionParams;
use crate::view::test_support::{new_words, small_params};

/// A reading of the monotonic clock, in microseconds.
const NOW_US: u64 = 5_000_000_000;

/// The reset period of the breakers of the tests, in microseconds.
const RESET_US: u64 = 60_000_000;

/// The outgoing connection of most tests.
const CONNECTION: &str = "outconn.lab";

/// How many threads ask for the trial message at once in the concurrency test.
const THREAD_COUNT: usize = 8;

/// How many times the threads of the concurrency test open the breaker and ask for its trial message.
const ROUND_COUNT: u64 = 200;

fn new_view(params: RegionParams) -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(params)?;
    RegionView::new(words, layout)
}

#[test]
fn new_breaker_is_closed() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    let state = view.breaker_state(CONNECTION)?;
    assert_eq!(state, BreakerState { state: BREAKER_CLOSED, opened_at_us: 0 });

    Ok(())
}

#[test]
fn breaker_opened_twice_keeps_its_first_opening_time() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    assert!(view.breaker_open(CONNECTION, NOW_US)?);
    assert!(!view.breaker_open(CONNECTION, NOW_US + 1)?);

    assert_eq!(view.breaker_state(CONNECTION)?, BreakerState { state: BREAKER_OPEN, opened_at_us: NOW_US });

    Ok(())
}

#[test]
fn trial_message_waits_for_the_reset_period_and_goes_out_once() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    view.breaker_open(CONNECTION, NOW_US)?;

    // The reset period is not over a microsecond before its end ..
    assert!(!view.breaker_begin_trial(CONNECTION, NOW_US + RESET_US - 1, RESET_US)?);

    // .. at its end one worker sends the trial message, and no other worker sends one while it is out.
    assert!(view.breaker_begin_trial(CONNECTION, NOW_US + RESET_US, RESET_US)?);
    assert!(!view.breaker_begin_trial(CONNECTION, NOW_US + RESET_US, RESET_US)?);

    assert_eq!(view.breaker_state(CONNECTION)?.state, BREAKER_HALF_OPEN);

    Ok(())
}

#[test]
fn successful_trial_closes_the_breaker() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    view.breaker_open(CONNECTION, NOW_US)?;
    view.breaker_begin_trial(CONNECTION, NOW_US + RESET_US, RESET_US)?;

    assert!(view.breaker_end_trial(CONNECTION, true, NOW_US + RESET_US + 1)?);
    assert_eq!(view.breaker_state(CONNECTION)?.state, BREAKER_CLOSED);

    Ok(())
}

#[test]
fn failed_trial_opens_the_breaker_for_another_reset_period() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    view.breaker_open(CONNECTION, NOW_US)?;
    view.breaker_begin_trial(CONNECTION, NOW_US + RESET_US, RESET_US)?;

    let failed_at = NOW_US + RESET_US + 1;
    assert!(view.breaker_end_trial(CONNECTION, false, failed_at)?);
    assert_eq!(view.breaker_state(CONNECTION)?, BreakerState { state: BREAKER_OPEN, opened_at_us: failed_at });

    assert!(!view.breaker_begin_trial(CONNECTION, failed_at + RESET_US - 1, RESET_US)?);
    assert!(view.breaker_begin_trial(CONNECTION, failed_at + RESET_US, RESET_US)?);

    Ok(())
}

#[test]
fn trial_outcome_of_a_breaker_that_is_not_half_open_changes_nothing() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    assert!(!view.breaker_end_trial(CONNECTION, false, NOW_US)?);
    assert_eq!(view.breaker_state(CONNECTION)?.state, BREAKER_CLOSED);

    Ok(())
}

#[test]
fn connections_keep_their_breakers_apart() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    view.breaker_open(CONNECTION, NOW_US)?;

    assert_eq!(view.breaker_state("outconn.pharmacy")?.state, BREAKER_CLOSED);

    Ok(())
}

#[test]
fn full_table_refuses_a_new_connection() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        breaker_capacity: 1,
        ..small_params()
    })?;

    view.breaker_open(CONNECTION, NOW_US)?;

    assert_eq!(view.breaker_state("outconn.pharmacy"), Err(RegionError::TableFull));

    Ok(())
}

#[test]
fn workers_asking_for_the_trial_message_at_once_send_it_once() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let barrier = Barrier::new(THREAD_COUNT);

    for round in 0..ROUND_COUNT {
        let opened_at = NOW_US + round * RESET_US * 2;
        view.breaker_open(CONNECTION, opened_at)?;

        let trial_at = opened_at + RESET_US;

        let results: Vec<Result<bool, RegionError>> = thread::scope(|scope| {
            let handles: Vec<_> = (0..THREAD_COUNT)
                .map(|_| {
                    let barrier = &barrier;

                    scope.spawn(move || {
                        let _ = barrier.wait();
                        view.breaker_begin_trial(CONNECTION, trial_at, RESET_US)
                    })
                })
                .collect();

            handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
        });

        let senders = results.into_iter().collect::<Result<Vec<bool>, RegionError>>()?;
        assert_eq!(senders.iter().filter(|is_sender| **is_sender).count(), 1);

        view.breaker_end_trial(CONNECTION, true, trial_at)?;
    }

    Ok(())
}
