//! Unit tests of the flags of the server.

use std::sync::Barrier;
use std::thread;

use super::*;
use crate::view::test_support::{new_words, small_params};

/// A flag of the tests other than the one of log streaming.
const OTHER_FLAG: u64 = 1 << 1;

/// How many threads invert one flag at once in the concurrency test.
const THREAD_COUNT: usize = 4;

/// How many times each thread of the concurrency test inverts the flag.
const ROUND_COUNT: usize = 501;

/// How many series keys the tests register, which is the capacity of the series table of the region of the tests.
const SERIES_KEY_COUNT: usize = 8;

/// By how many bytes each series key that the tests register is longer than the previous one.
const KEY_LEN_STEP: usize = 7;

fn new_view() -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(small_params())?;
    RegionView::new(words, layout)
}

#[test]
fn flag_starts_clear_and_each_inversion_reports_its_new_state() -> Result<(), RegionError> {
    let view = new_view()?;

    assert!(!view.flag_is_set(FLAG_LOG_STREAMING)?);

    assert!(view.flag_invert(FLAG_LOG_STREAMING)?);
    assert!(view.flag_is_set(FLAG_LOG_STREAMING)?);

    assert!(!view.flag_invert(FLAG_LOG_STREAMING)?);
    assert!(!view.flag_is_set(FLAG_LOG_STREAMING)?);

    Ok(())
}

#[test]
fn inversion_of_one_flag_leaves_the_other_flags_as_they_are() -> Result<(), RegionError> {
    let view = new_view()?;

    assert!(view.flag_invert(OTHER_FLAG)?);
    assert!(view.flag_invert(FLAG_LOG_STREAMING)?);
    assert!(!view.flag_invert(FLAG_LOG_STREAMING)?);

    assert!(view.flag_is_set(OTHER_FLAG)?);
    assert!(!view.flag_is_set(FLAG_LOG_STREAMING)?);

    Ok(())
}

#[test]
fn flag_is_kept_apart_from_the_words_that_other_parts_change() -> Result<(), RegionError> {
    let view = new_view()?;

    view.wake_increment("sub-key")?;

    // Keys of growing lengths move the cursor of the series records by every count of words up to a few
    for key_number in 1..=SERIES_KEY_COUNT {
        let key = "k".repeat(key_number * KEY_LEN_STEP);
        let _ = view.series_register(1, &key)?;

        assert!(!view.flag_is_set(FLAG_LOG_STREAMING)?);
    }

    Ok(())
}

#[test]
fn concurrent_inversions_are_all_applied() -> Result<(), RegionError> {
    let view = new_view()?;
    let barrier = Barrier::new(THREAD_COUNT);

    let results: Vec<Result<(), RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..THREAD_COUNT)
            .map(|_| {
                let barrier = &barrier;

                scope.spawn(move || {
                    let _ = barrier.wait();

                    for _ in 0..ROUND_COUNT {
                        let _ = view.flag_invert(FLAG_LOG_STREAMING)?;
                    }
                    Ok(())
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect::<Result<Vec<()>, RegionError>>()?;

    // An even number of inversions in total leaves the flag clear
    assert!(!view.flag_is_set(FLAG_LOG_STREAMING)?);

    Ok(())
}
