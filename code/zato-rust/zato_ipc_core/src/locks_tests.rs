//! Unit tests of the keyed locks.

use std::sync::Barrier;
use std::sync::atomic::AtomicUsize;
use std::thread;

use super::*;
use crate::layout::{CONFIG_PLACE, PLACE_COUNT, RegionParams, WORKER_PLACE};
use crate::view::test_support::{new_words, small_params};

/// The outgoing connection of most tests.
const CONNECTION: &str = "outconn-rest.1";

/// How many times each thread of the concurrency tests changes the counter or takes the lock.
const ROUND_COUNT: usize = 500;

/// The value of the counter that the config process sets in the tests.
const NAME_MARK: i64 = 7;

fn new_view(params: RegionParams) -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(params)?;
    RegionView::new(words, layout)
}

/// Takes the lock of an entry for a place, polling until the place has the turn.
fn take_lock(view: &RegionView<'_>, queue: usize, place: usize) -> Result<(), RegionError> {
    let _ = view.queue_enter(queue, place)?;

    // The turn passes on only when its holder releases it, so the poll is repeated until it comes
    while !view.queue_poll(queue, place)?.0 {
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
    assert_eq!(view.lock_counter_replace(capacity, 0, 1), Err(RegionError::NoSuchLock(capacity)));
    assert_eq!(view.lock_queue(capacity), Err(RegionError::NoSuchLock(capacity)));

    Ok(())
}

#[test]
fn replacement_happens_only_while_the_counter_holds_the_value_read() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let entry = view.lock_entry(CONNECTION)?;

    // A new counter holds zero
    assert_eq!(view.lock_counter(entry)?, 0);
    assert!(view.lock_counter_replace(entry, 0, NAME_MARK)?);
    assert_eq!(view.lock_counter(entry)?, NAME_MARK);

    // A caller that read an earlier value leaves the counter as it is, and one that read the current value replaces it
    assert!(!view.lock_counter_replace(entry, 0, 1)?);
    assert!(view.lock_counter_replace(entry, NAME_MARK, -1)?);
    assert_eq!(view.lock_counter(entry)?, -1);

    Ok(())
}

#[test]
fn one_of_concurrent_replacements_of_a_value_succeeds() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let entry = view.lock_entry(CONNECTION)?;
    let barrier = Barrier::new(PLACE_COUNT);
    let replaced_count = AtomicUsize::new(0);

    let results: Vec<Result<(), RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..PLACE_COUNT)
            .map(|_| {
                let barrier = &barrier;
                let replaced_count = &replaced_count;

                scope.spawn(move || {
                    for round in 0..ROUND_COUNT {
                        let expected = i64::try_from(round).unwrap_or(i64::MAX);
                        let _ = barrier.wait();

                        // Both threads of a round expect the value that the previous round left, and only one of them replaces it
                        if view.lock_counter_replace(entry, expected, expected + 1)? {
                            let _ = replaced_count.fetch_add(1, Ordering::SeqCst);
                        }

                        // The next round starts once both threads have tried this one
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
fn queue_of_a_lock_follows_the_writer_queues_and_serves_in_order() -> Result<(), RegionError> {
    let params = small_params();
    let view = new_view(params)?;
    let entry = view.lock_entry(CONNECTION)?;
    let queue = view.lock_queue(entry)?;

    assert_eq!(queue, params.queue_count + entry);

    let _ = view.queue_enter(queue, CONFIG_PLACE)?;
    let _ = view.queue_enter(queue, WORKER_PLACE)?;

    // A writer queue is not affected by the lock
    let _ = view.queue_enter(0, WORKER_PLACE)?;
    assert!(view.queue_poll(0, WORKER_PLACE)?.0);

    assert_eq!(view.queue_poll(queue, WORKER_PLACE)?, (false, Some(CONFIG_PLACE)));
    assert!(view.queue_poll(queue, CONFIG_PLACE)?.0);
    assert_eq!(view.queue_release(queue, CONFIG_PLACE)?, Some(WORKER_PLACE));
    assert!(view.queue_poll(queue, WORKER_PLACE)?.0);

    Ok(())
}

#[test]
fn lock_of_a_terminated_holder_passes_on() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let queue = view.lock_queue(view.lock_entry(CONNECTION)?)?;

    take_lock(&view, queue, CONFIG_PLACE)?;
    let _ = view.queue_enter(queue, WORKER_PLACE)?;

    assert!(!view.queue_poll(queue, WORKER_PLACE)?.0);
    assert_eq!(view.queue_abandon(queue, CONFIG_PLACE)?, Some(WORKER_PLACE));
    assert!(view.queue_poll(queue, WORKER_PLACE)?.0);

    Ok(())
}

#[test]
fn one_place_at_a_time_holds_the_lock() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let queue = view.lock_queue(view.lock_entry(CONNECTION)?)?;

    let holders = AtomicUsize::new(0);
    let overlaps = AtomicUsize::new(0);
    let sections = AtomicUsize::new(0);

    let results: Vec<Result<(), RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..PLACE_COUNT)
            .map(|place| {
                let (holders, overlaps, sections) = (&holders, &overlaps, &sections);

                scope.spawn(move || {
                    for _ in 0..ROUND_COUNT {
                        take_lock(&view, queue, place)?;

                        // Another holder inside the section at the same time would have raised the count first
                        if holders.fetch_add(1, Ordering::SeqCst) != 0 {
                            let _ = overlaps.fetch_add(1, Ordering::SeqCst);
                        }

                        let _ = sections.fetch_add(1, Ordering::SeqCst);
                        let _ = holders.fetch_sub(1, Ordering::SeqCst);

                        let _ = view.queue_release(queue, place)?;
                    }
                    Ok(())
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect::<Result<Vec<()>, RegionError>>()?;

    assert_eq!(overlaps.load(Ordering::SeqCst), 0);
    assert_eq!(sections.load(Ordering::SeqCst), PLACE_COUNT * ROUND_COUNT);

    Ok(())
}
