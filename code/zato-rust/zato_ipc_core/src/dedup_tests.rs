//! Unit tests of the table of message control IDs.

use std::collections::VecDeque;
use std::sync::Barrier;
use std::thread;

use proptest::prelude::*;

use super::*;
use crate::layout::RegionParams;
use crate::slots::{STATE_READY, STATE_STARTING};
use crate::view::test_support::{new_words, small_params};

/// A reading of the monotonic clock, in microseconds.
const NOW_US: u64 = 5_000_000_000;

/// The deduplication window of most tests, in microseconds.
const TTL_US: u64 = 60_000_000;

/// The channel that received the messages of most tests.
const SCOPE: &str = "hl7.orders";

/// The slot of the worker that performs the checks of most tests.
const CHECKING_SLOT: usize = 0;

/// The slot of a worker that holds the lock in the tests of the lock.
const HOLDING_SLOT: usize = 1;

/// How many threads check the same control IDs at once in the concurrency test.
const THREAD_COUNT: usize = 4;

/// How many control IDs each thread checks in the concurrency test.
const CONTROL_ID_COUNT: usize = 200;

/// Returns a view of a region with the given sizes, whose slots are all started and ready.
fn new_view(params: RegionParams) -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(params)?;
    let view = RegionView::new(words, layout)?;

    for slot in 0..params.slot_count {
        view.next_slot_generation(slot)?;
        view.set_slot_state(slot, STATE_READY)?;
    }

    Ok(view)
}

/// Returns the worker of a slot, with the generation that the slot holds.
fn owner_of(view: &RegionView<'static>, slot: usize) -> Result<DedupOwner, RegionError> {
    let generation = view.slot_generation(slot)?;
    Ok(DedupOwner { slot, generation })
}

/// Checks a control ID of the default channel from the default slot.
fn check(view: &RegionView<'static>, control_id: &str, now_us: u64) -> Result<DedupCheck, RegionError> {
    let owner = owner_of(view, CHECKING_SLOT)?;
    view.dedup_check(&DedupKey::new(SCOPE, control_id), owner, TTL_US, now_us)
}

/// The cache of the control IDs of one process, as `MessageDeduplicator` keeps it, for comparison with the table.
struct InProcessCache {

    /// The keys and their expiry times, the oldest first.
    entries: VecDeque<(String, u64)>,

    /// How many keys the cache holds.
    capacity: usize,
}

impl InProcessCache {

    /// Checks and records a key as `MessageDeduplicator.is_duplicate` does, with the window of the key given per check.
    fn check(&mut self, key: &str, ttl_us: u64, now_us: u64) -> DedupCheck {
        while let Some((_, expiry)) = self.entries.front() {
            if *expiry > now_us {
                break;
            }
            self.entries.pop_front();
        }

        if self.entries.iter().any(|(entry_key, expiry)| entry_key == key && *expiry > now_us) {
            return DedupCheck::Duplicate;
        }

        if self.entries.len() >= self.capacity {
            self.entries.pop_front();
        }

        self.entries.push_back((key.to_owned(), now_us.saturating_add(ttl_us)));
        DedupCheck::New
    }
}

#[test]
fn control_id_is_a_duplicate_within_its_window_only() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::New);
    assert_eq!(check(&view, "MSG-1", NOW_US + TTL_US - 1)?, DedupCheck::Duplicate);

    // The window ends at its last microsecond, after which the control ID is new again
    assert_eq!(check(&view, "MSG-1", NOW_US + TTL_US)?, DedupCheck::New);

    Ok(())
}

#[test]
fn channels_keep_their_control_ids_apart() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let owner = owner_of(&view, CHECKING_SLOT)?;

    let orders = DedupKey::new("hl7.orders", "MSG-1");
    let results = DedupKey::new("hl7.results", "MSG-1");

    assert_eq!(view.dedup_check(&orders, owner, TTL_US, NOW_US)?, DedupCheck::New);
    assert_eq!(view.dedup_check(&results, owner, TTL_US, NOW_US)?, DedupCheck::New);
    assert_eq!(view.dedup_check(&results, owner, TTL_US, NOW_US)?, DedupCheck::Duplicate);

    Ok(())
}

#[test]
fn full_table_drops_its_oldest_control_id() -> Result<(), RegionError> {
    let params = small_params();
    let view = new_view(params)?;

    for index in 0..=params.dedup_capacity {
        assert_eq!(check(&view, &format!("MSG-{index}"), NOW_US)?, DedupCheck::New);
    }

    // The first control ID made room for the last one, and every other one is still held
    assert_eq!(check(&view, "MSG-0", NOW_US)?, DedupCheck::New);
    assert_eq!(check(&view, &format!("MSG-{}", params.dedup_capacity), NOW_US)?, DedupCheck::Duplicate);

    Ok(())
}

#[test]
fn live_holder_makes_another_worker_check_again() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let holder = owner_of(&view, HOLDING_SLOT)?;

    assert_eq!(view.dedup_lock(holder)?, Some(false));
    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::Busy);

    // Once the holder releases the lock, the same check records the control ID
    view.dedup_head(HEAD_LOCK)?.store(UNLOCKED, Ordering::SeqCst);
    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::New);

    Ok(())
}

/// Takes the lock for the holding slot and leaves a partially updated index behind, as a holder that exits does.
fn leave_partial_update(view: &RegionView<'static>) -> Result<(), RegionError> {
    let holder = owner_of(view, HOLDING_SLOT)?;
    assert_eq!(view.dedup_lock(holder)?, Some(false));

    // The index names a record that was never written
    view.dedup_index(0)?.store(1, Ordering::SeqCst);
    view.dedup_head(HEAD_NEXT)?.store(1, Ordering::SeqCst);

    Ok(())
}

#[test]
fn lock_of_a_stopped_holder_is_taken_over_and_the_table_emptied() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::New);
    leave_partial_update(&view)?;
    view.set_slot_state(HOLDING_SLOT, STATE_STOPPED)?;

    // The table is emptied, so the control ID recorded before the holder exited is new again ..
    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::New);

    // .. the table holds that control ID only, and the lock is free.
    let mut used_entries = 0;

    for entry in 0..view.layout().dedup_index_capacity {
        if view.dedup_index(entry)?.load(Ordering::SeqCst) != EMPTY_INDEX {
            used_entries += 1;
        }
    }

    assert_eq!(used_entries, 1);
    assert_eq!(view.dedup_head(HEAD_OLDEST)?.load(Ordering::SeqCst), 0);
    assert_eq!(view.dedup_head(HEAD_NEXT)?.load(Ordering::SeqCst), 1);
    assert_eq!(view.dedup_head(HEAD_LOCK)?.load(Ordering::SeqCst), UNLOCKED);
    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::Duplicate);

    Ok(())
}

#[test]
fn lock_of_a_replaced_holder_is_taken_over() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    leave_partial_update(&view)?;

    // The replacement worker of the slot starts with the next generation
    view.next_slot_generation(HOLDING_SLOT)?;
    view.set_slot_state(HOLDING_SLOT, STATE_STARTING)?;

    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::New);
    assert_eq!(check(&view, "MSG-1", NOW_US)?, DedupCheck::Duplicate);

    Ok(())
}

#[test]
fn table_of_no_capacity_refuses_a_check() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        dedup_capacity: 0,
        ..small_params()
    })?;

    assert_eq!(check(&view, "MSG-1", NOW_US), Err(RegionError::TableFull));

    Ok(())
}

/// Checks every control ID from threads of different slots that start together, returning how many each found new.
fn check_from_threads(view: &RegionView<'static>, control_ids: &[String]) -> Result<Vec<usize>, RegionError> {
    let barrier = Barrier::new(THREAD_COUNT);

    let results: Vec<Result<usize, RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = (0..THREAD_COUNT)
            .map(|slot| {
                let barrier = &barrier;

                scope.spawn(move || {
                    let owner = owner_of(view, slot)?;
                    let mut new_count = 0;
                    let _ = barrier.wait();

                    for control_id in control_ids {
                        let key = DedupKey::new(SCOPE, control_id);

                        // A busy table is checked again, as the worker does after it yields to its hub
                        let outcome = loop {
                            let outcome = view.dedup_check(&key, owner, TTL_US, NOW_US)?;
                            if outcome != DedupCheck::Busy {
                                break outcome;
                            }
                            thread::yield_now();
                        };

                        if outcome == DedupCheck::New {
                            new_count += 1;
                        }
                    }

                    Ok(new_count)
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect()
}

#[test]
fn workers_checking_the_same_control_ids_at_once_find_each_new_once() -> Result<(), RegionError> {
    let view = new_view(RegionParams {
        dedup_capacity: CONTROL_ID_COUNT,
        ..small_params()
    })?;

    let control_ids: Vec<String> = (0..CONTROL_ID_COUNT).map(|index| format!("MSG-{index}")).collect();
    let new_counts = check_from_threads(&view, &control_ids)?;

    assert_eq!(new_counts.iter().sum::<usize>(), CONTROL_ID_COUNT);

    Ok(())
}

proptest! {

    /// For clock readings that never go back, the table decides every check as the cache of one process does,
    /// with control IDs that collide in the index of a small table and windows that differ per check.
    #[test]
    fn table_matches_in_process_cache(
        capacity in 1_usize..6,
        steps in prop::collection::vec((0_usize..8, prop::sample::select(vec![10_u64, 30, 100]), 0_u64..40), 1..300),
    ) {
        let params = RegionParams { dedup_capacity: capacity, ..small_params() };
        let view = new_view(params).map_err(|error| TestCaseError::fail(error.to_string()))?;
        let owner = owner_of(&view, CHECKING_SLOT).map_err(|error| TestCaseError::fail(error.to_string()))?;

        let mut in_process = InProcessCache { entries: VecDeque::new(), capacity };
        let mut now_us = NOW_US;

        for (key_index, ttl_us, step) in steps {
            now_us += step;

            let control_id = format!("MSG-{key_index}");
            let shared = view.dedup_check(&DedupKey::new(SCOPE, &control_id), owner, ttl_us, now_us)
                .map_err(|error| TestCaseError::fail(error.to_string()))?;
            let expected = in_process.check(&control_id, ttl_us, now_us);

            prop_assert_eq!(shared, expected);
        }
    }
}
