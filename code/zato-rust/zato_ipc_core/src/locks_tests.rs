//! Unit tests of the keyed locks.

use std::sync::Barrier;
use std::sync::atomic::AtomicUsize;
use std::thread;

use super::*;
use crate::layout::RegionParams;
use crate::view::test_support::{new_words, small_params};

/// The outgoing connection of most tests.
const CONNECTION: &str = "outconn-rest.1";

/// How many threads use one lock at once in the concurrency tests.
const THREAD_COUNT: usize = 4;

/// How many times each thread of the concurrency tests changes the counter or takes the lock.
const ROUND_COUNT: usize = 500;

/// The value the counter of the tests is set to at startup.
const STARTUP_DEPTH: i64 = 7;

fn new_view(params: RegionParams) -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(params)?;
    RegionView::new(words, layout)
}

/// Takes the lock of an entry for a slot, polling until the slot has the turn.
fn take_lock(view: &RegionView<'_>, queue: usize, slot: usize) -> Result<(), RegionError> {
    let _ = view.queue_enter(queue, slot)?;

    // The turn passes on only when its holder releases it, so the poll is repeated until it comes
    while !view.queue_poll(queue, slot)?.0 {
        thread::yield_now();
    }

    Ok(())
}

#[test]
fn a_key_keeps_its_entry_and_two_keys_have_two() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    let first = view.lock_entry(CONNECTION)?;
    let second = view.lock_entry("outconn-rest.2")?;

    assert_eq!(view.lock_entry(CONNECTION)?, first);
    assert_ne!(first, second);

    Ok(())
}

#[test]
fn full_table_refuses_a_new_key() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        lock_capacity: 1,
        ..small_params()
    })?;

    let _ = view.lock_entry(CONNECTION)?;

    assert_eq!(view.lock_entry("outconn-rest.2"), Err(RegionError::TableFull));

    Ok(())
}

#[test]
fn table_of_no_entries_refuses_every_key() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        lock_capacity: 0,
        ..small_params()
    })?;

    assert_eq!(view.lock_entry(CONNECTION), Err(RegionError::TableFull));
    assert_eq!(view.lock_queue(0), Err(RegionError::NoSuchLock(0)));

    Ok(())
}

#[test]
fn entry_past_the_table_is_refused() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let capacity = small_params().lock_capacity;

    assert_eq!(view.lock_counter(capacity), Err(RegionError::NoSuchLock(capacity)));
    assert_eq!(view.lock_counter_add(capacity, 1), Err(RegionError::NoSuchLock(capacity)));
    assert_eq!(view.lock_queue(capacity), Err(RegionError::NoSuchLock(capacity)));

    Ok(())
}

#[test]
fn startup_value_is_set_once_and_never_over_a_changed_counter() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let first = view.lock_entry(CONNECTION)?;
    let second = view.lock_entry("outconn-rest.2")?;

    assert_eq!(view.lock_counter(first)?, 0);

    // The first worker sets the value it read, and the next one leaves it as it is
    assert!(view.lock_counter_init(first, STARTUP_DEPTH)?);
    assert!(!view.lock_counter_init(first, 0)?);
    assert_eq!(view.lock_counter(first)?, STARTUP_DEPTH);

    // A counter that a worker changed is in use, including one that came back to zero
    assert_eq!(view.lock_counter_add(second, 1)?, 1);
    assert_eq!(view.lock_counter_add(second, -1)?, 0);
    assert!(!view.lock_counter_init(second, STARTUP_DEPTH)?);
    assert_eq!(view.lock_counter(second)?, 0);

    Ok(())
}

#[test]
fn replacement_happens_only_while_the_counter_holds_the_value_read() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let unset = view.lock_entry(CONNECTION)?;
    let zero = view.lock_entry("outconn-rest.2")?;

    // An unset counter holds zero, which a worker replaces
    assert!(view.lock_counter_replace(unset, 0, STARTUP_DEPTH)?);
    assert_eq!(view.lock_counter(unset)?, STARTUP_DEPTH);

    // A worker that read an earlier value leaves the counter as it is, and one that read the current value replaces it
    assert!(!view.lock_counter_replace(unset, 0, 1)?);
    assert!(view.lock_counter_replace(unset, STARTUP_DEPTH, 1)?);
    assert_eq!(view.lock_counter(unset)?, 1);

    // A counter that a worker set to zero is replaced as an unset one is
    assert!(view.lock_counter_init(zero, 0)?);
    assert!(view.lock_counter_replace(zero, 0, STARTUP_DEPTH)?);
    assert_eq!(view.lock_counter(zero)?, STARTUP_DEPTH);

    Ok(())
}

#[test]
fn one_of_concurrent_replacements_of_a_value_succeeds() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let entry = view.lock_entry(CONNECTION)?;
    let barrier = Barrier::new(THREAD_COUNT);
    let replaced_count = AtomicUsize::new(0);

    let results: Vec<Result<(), RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..THREAD_COUNT)
            .map(|_| {
                let barrier = &barrier;
                let replaced_count = &replaced_count;

                scope.spawn(move || {
                    for round in 0..ROUND_COUNT {
                        let expected = i64::try_from(round).unwrap_or(i64::MAX);
                        let _ = barrier.wait();

                        // Every thread of a round expects the value that the previous round left, and only one of them replaces it
                        if view.lock_counter_replace(entry, expected, expected + 1)? {
                            let _ = replaced_count.fetch_add(1, Ordering::SeqCst);
                        }

                        // The next round starts once every thread has tried this one
                        let _ = barrier.wait();
                    }
                    Ok(())
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect::<Result<Vec<()>, RegionError>>()?;

    let expected = i64::try_from(ROUND_COUNT).unwrap_or(i64::MAX);

    assert_eq!(replaced_count.load(Ordering::SeqCst), ROUND_COUNT);
    assert_eq!(view.lock_counter(entry)?, expected);

    Ok(())
}

#[test]
fn counter_holds_negative_values() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let entry = view.lock_entry(CONNECTION)?;

    assert_eq!(view.lock_counter_add(entry, -3)?, -3);
    assert_eq!(view.lock_counter(entry)?, -3);
    assert_eq!(view.lock_counter_add(entry, 5)?, 2);

    Ok(())
}

#[test]
fn queue_of_a_lock_follows_the_writer_queues_and_serves_in_order() -> Result<(), RegionError> {
    let params = small_params();
    let view = new_view(params)?;
    let entry = view.lock_entry(CONNECTION)?;
    let queue = view.lock_queue(entry)?;

    assert_eq!(queue, params.queue_count + entry);

    let _ = view.queue_enter(queue, 1)?;
    let _ = view.queue_enter(queue, 2)?;

    // A writer queue is not affected by the lock
    let _ = view.queue_enter(0, 2)?;
    assert!(view.queue_poll(0, 2)?.0);

    assert_eq!(view.queue_poll(queue, 2)?, (false, Some(1)));
    assert!(view.queue_poll(queue, 1)?.0);
    assert_eq!(view.queue_release(queue, 1)?, Some(2));
    assert!(view.queue_poll(queue, 2)?.0);

    Ok(())
}

#[test]
fn lock_of_a_terminated_holder_passes_on() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let queue = view.lock_queue(view.lock_entry(CONNECTION)?)?;

    take_lock(&view, queue, 0)?;
    let _ = view.queue_enter(queue, 3)?;

    assert!(!view.queue_poll(queue, 3)?.0);
    assert_eq!(view.queue_abandon(queue, 0)?, Some(3));
    assert!(view.queue_poll(queue, 3)?.0);

    Ok(())
}

#[test]
fn concurrent_changes_of_the_counter_are_all_counted() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let entry = view.lock_entry(CONNECTION)?;
    let _ = view.lock_counter_init(entry, STARTUP_DEPTH)?;
    let barrier = Barrier::new(THREAD_COUNT);

    let results: Vec<Result<(), RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..THREAD_COUNT)
            .map(|_| {
                let barrier = &barrier;

                scope.spawn(move || {
                    let _ = barrier.wait();

                    // Each round raises the counter twice and lowers it once
                    for _ in 0..ROUND_COUNT {
                        let _ = view.lock_counter_add(entry, 2)?;
                        let _ = view.lock_counter_add(entry, -1)?;
                    }
                    Ok(())
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect::<Result<Vec<()>, RegionError>>()?;

    let expected = STARTUP_DEPTH + i64::try_from(THREAD_COUNT * ROUND_COUNT).unwrap_or(i64::MAX);
    assert_eq!(view.lock_counter(entry)?, expected);

    Ok(())
}

#[test]
fn one_slot_at_a_time_holds_the_lock() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let queue = view.lock_queue(view.lock_entry(CONNECTION)?)?;

    let holders = AtomicUsize::new(0);
    let overlaps = AtomicUsize::new(0);
    let sections = AtomicUsize::new(0);

    let results: Vec<Result<(), RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..THREAD_COUNT)
            .map(|slot| {
                let (holders, overlaps, sections) = (&holders, &overlaps, &sections);

                scope.spawn(move || {
                    for _ in 0..ROUND_COUNT {
                        take_lock(&view, queue, slot)?;

                        // Another holder inside the section at the same time would have raised the count first
                        if holders.fetch_add(1, Ordering::SeqCst) != 0 {
                            let _ = overlaps.fetch_add(1, Ordering::SeqCst);
                        }

                        let _ = sections.fetch_add(1, Ordering::SeqCst);
                        let _ = holders.fetch_sub(1, Ordering::SeqCst);

                        let _ = view.queue_release(queue, slot)?;
                    }
                    Ok(())
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect::<Result<Vec<()>, RegionError>>()?;

    assert_eq!(overlaps.load(Ordering::SeqCst), 0);
    assert_eq!(sections.load(Ordering::SeqCst), THREAD_COUNT * ROUND_COUNT);

    Ok(())
}
