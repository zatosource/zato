//! Table of the message control IDs that the MLLP channels of every worker received within their deduplication windows.
//!
//! A check runs under the lock word of the table, which holds the slot and the generation of the worker that holds it.
//! A worker holds the lock for one call only and never waits while it holds it. A worker that finds the lock held by a
//! worker that has exited, which the slot table shows as a stopped slot or as a later generation, takes the lock over
//! and empties the table, because the exited holder may have left the records and the index partially updated.
//!
//! The records are kept in the order they were recorded, the oldest first, so the expired records and the records
//! beyond the capacity leave from the front. The index is open-addressed with linear probing and holds the counter
//! of each record, and a record that leaves is removed from the index by backward shift deletion,
//! so every probe ends at an empty entry.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;
use crate::layout::DEDUP_RECORD_WORDS;
use crate::slots::STATE_STOPPED;
use crate::view::{RegionView, key_hash, probe_start};

/// Seed of the first hash of the key of a control ID.
const DEDUP_FIRST_KIND: u64 = 0x4444_5550_4649;

/// Seed of the second hash of the key of a control ID.
const DEDUP_SECOND_KIND: u64 = 0x4444_5550_5345;

/// Separates the scope of a control ID from the control ID in its key.
const KEY_SEPARATOR: char = '\u{0}';

/// Position of the lock word within the head block.
const HEAD_LOCK: usize = 0;

/// Position of the counter of the oldest record within the head block.
const HEAD_OLDEST: usize = 1;

/// Position of the counter of the next record within the head block.
const HEAD_NEXT: usize = 2;

/// Position of the first hash within a record.
const RECORD_FIRST_HASH: usize = 0;

/// Position of the second hash within a record.
const RECORD_SECOND_HASH: usize = 1;

/// Position of the expiry time within a record.
const RECORD_EXPIRY: usize = 2;

/// Lock word of a table that no worker holds.
const UNLOCKED: u64 = 0;

/// Index entry that holds no record.
const EMPTY_INDEX: u64 = 0;

/// Number of bits of a lock word that hold the slot of its holder, increased by one.
const OWNER_SLOT_BITS: u32 = 16;

/// Mask of the slot of the holder within a lock word.
const OWNER_SLOT_MASK: u64 = (1 << OWNER_SLOT_BITS) - 1;

/// The two hashes of the key of one control ID, which together identify it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DedupKey {

    /// Hash of the key under the first seed, which also places the key in the index.
    first: u64,

    /// Hash of the key under the second seed.
    second: u64,
}

impl DedupKey {

    /// Hashes a control ID within its scope, which is the channel that received it.
    #[must_use]
    pub fn new(scope: &str, control_id: &str) -> Self {
        let key = format!("{scope}{KEY_SEPARATOR}{control_id}");

        Self {
            first: key_hash(DEDUP_FIRST_KIND, &key),
            second: key_hash(DEDUP_SECOND_KIND, &key),
        }
    }
}

/// The worker that performs a check, as the slot table records it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DedupOwner {

    /// The slot of the worker.
    pub slot: usize,

    /// The generation of the slot that the worker was started as.
    pub generation: u64,
}

/// The outcome of one check of a control ID.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DedupCheck {

    /// Another worker that is alive holds the lock of the table, and the caller checks again.
    Busy,

    /// The control ID was recorded within its window, by this worker or by another one.
    Duplicate,

    /// The control ID was not recorded within its window, and it is recorded now.
    New,
}

/// Converts a counter of records to a position in a table of the given capacity.
fn counter_position(counter: u64, capacity: usize) -> Result<usize, RegionError> {
    let capacity_word = u64::try_from(capacity).map_err(|_conversion_error| RegionError::LayoutTooLarge)?;
    let remainder = counter.checked_rem(capacity_word).ok_or(RegionError::TableFull)?;
    let out = usize::try_from(remainder).map_err(|_conversion_error| RegionError::OutOfBounds)?;
    Ok(out)
}

/// Returns the distance that a probe travels from `origin` to `target` in an index of the given capacity.
const fn probe_distance(origin: usize, target: usize, capacity: usize) -> usize {
    target.wrapping_add(capacity).wrapping_sub(origin) % capacity
}

impl RegionView<'_> {

    /// Returns a word of the head block of the table.
    fn dedup_head(&self, field: usize) -> Result<&AtomicU64, RegionError> {
        let index = self.layout().dedup_start.checked_add(field).ok_or(RegionError::OutOfBounds)?;
        self.word(index)
    }

    /// Returns a word of the record with the given counter.
    fn dedup_record(&self, counter: u64, field: usize) -> Result<&AtomicU64, RegionError> {
        let position = counter_position(counter, self.layout().params.dedup_capacity)?;
        let offset = position.checked_mul(DEDUP_RECORD_WORDS).ok_or(RegionError::OutOfBounds)?;
        let index = self
            .layout()
            .dedup_records_start
            .checked_add(offset)
            .and_then(|record_start| record_start.checked_add(field))
            .ok_or(RegionError::OutOfBounds)?;
        self.word(index)
    }

    /// Returns an entry of the index.
    fn dedup_index(&self, entry: usize) -> Result<&AtomicU64, RegionError> {
        let index = self.layout().dedup_index_start.checked_add(entry).ok_or(RegionError::OutOfBounds)?;
        self.word(index)
    }

    /// Returns the lock word that names the given worker as the holder.
    fn dedup_owner_word(&self, owner: DedupOwner) -> Result<u64, RegionError> {
        self.check_slot(owner.slot)?;

        // The slot is stored increased by one, so no holder has the lock word of an unlocked table
        let slot_word = u64::try_from(owner.slot).map_err(|_conversion_error| RegionError::NoSuchSlot(owner.slot))?;
        let stored_slot = slot_word.checked_add(1).filter(|stored| *stored <= OWNER_SLOT_MASK);
        let stored_slot = stored_slot.ok_or(RegionError::NoSuchSlot(owner.slot))?;

        let out = (owner.generation << OWNER_SLOT_BITS) | stored_slot;
        Ok(out)
    }

    /// Returns whether the worker named by a lock word is still the worker of its slot.
    fn dedup_is_holder_alive(&self, lock_word: u64) -> Result<bool, RegionError> {
        let stored_slot = lock_word & OWNER_SLOT_MASK;
        let slot_word = stored_slot.checked_sub(1).ok_or(RegionError::OutOfBounds)?;
        let slot = usize::try_from(slot_word).map_err(|_conversion_error| RegionError::OutOfBounds)?;
        let generation = lock_word >> OWNER_SLOT_BITS;

        // The generation in the lock word lost its highest bits to the slot, so only the bits it kept are compared
        let current_generation = (self.slot_generation(slot)? << OWNER_SLOT_BITS) >> OWNER_SLOT_BITS;
        let state = self.slot_state(slot)?;

        let out = state != STATE_STOPPED && current_generation == generation;
        Ok(out)
    }

    /// Takes the lock of the table, returning whether the table must be emptied first, or `None` if a live worker holds it.
    fn dedup_lock(&self, owner: DedupOwner) -> Result<Option<bool>, RegionError> {
        let lock = self.dedup_head(HEAD_LOCK)?;
        let own_word = self.dedup_owner_word(owner)?;
        let current = lock.load(Ordering::SeqCst);

        // A table that no worker holds is taken as it is ..
        if current == UNLOCKED {
            let out = lock.compare_exchange(UNLOCKED, own_word, Ordering::SeqCst, Ordering::SeqCst).ok().map(|_unlocked| false);
            return Ok(out);
        }

        // .. a live holder completes its call without waiting, so the caller checks again later ..
        if self.dedup_is_holder_alive(current)? {
            return Ok(None);
        }

        // .. and the table of a holder that exited is taken over, by one worker only, and emptied.
        let out = lock.compare_exchange(current, own_word, Ordering::SeqCst, Ordering::SeqCst).ok().map(|_dead_holder| true);
        Ok(out)
    }

    /// Empties the index and the records, after a holder exited while it held the lock.
    fn dedup_clear(&self) -> Result<(), RegionError> {
        for entry in 0..self.layout().dedup_index_capacity {
            self.dedup_index(entry)?.store(EMPTY_INDEX, Ordering::SeqCst);
        }

        self.dedup_head(HEAD_OLDEST)?.store(0, Ordering::SeqCst);
        self.dedup_head(HEAD_NEXT)?.store(0, Ordering::SeqCst);

        Ok(())
    }

    /// Returns the index entry that holds the record with the given counter.
    fn dedup_find_entry(&self, counter: u64) -> Result<usize, RegionError> {
        let capacity = self.layout().dedup_index_capacity;
        let first_hash = self.dedup_record(counter, RECORD_FIRST_HASH)?.load(Ordering::SeqCst);
        let start = probe_start(first_hash, capacity);
        let stored = counter.wrapping_add(1);

        for step in 0..capacity {
            // The record is on the probe path of its first hash, ahead of the first empty entry
            let entry = start.wrapping_add(step) % capacity;

            if self.dedup_index(entry)?.load(Ordering::SeqCst) == stored {
                return Ok(entry);
            }
        }

        Err(RegionError::OutOfBounds)
    }

    /// Removes an index entry, moving back each later entry of its probe path whose own path passes the emptied entry.
    fn dedup_remove_entry(&self, entry: usize) -> Result<(), RegionError> {
        let capacity = self.layout().dedup_index_capacity;
        let mut vacant = entry;
        let mut probe = entry;

        for _ in 0..capacity {
            probe = probe.wrapping_add(1) % capacity;
            let stored = self.dedup_index(probe)?.load(Ordering::SeqCst);

            // An empty entry ends the probe path, so nothing beyond it can move into the vacant entry
            if stored == EMPTY_INDEX {
                self.dedup_index(vacant)?.store(EMPTY_INDEX, Ordering::SeqCst);
                return Ok(());
            }

            let counter = stored.wrapping_sub(1);
            let first_hash = self.dedup_record(counter, RECORD_FIRST_HASH)?.load(Ordering::SeqCst);
            let start = probe_start(first_hash, capacity);

            // The entry moves into the vacant entry only if that lies on the path from its start to where it is
            if probe_distance(start, probe, capacity) >= probe_distance(vacant, probe, capacity) {
                self.dedup_index(vacant)?.store(stored, Ordering::SeqCst);
                vacant = probe;
            }
        }

        Err(RegionError::TableFull)
    }

    /// Removes the oldest record from the index and from the records.
    fn dedup_drop_oldest(&self) -> Result<(), RegionError> {
        let oldest_word = self.dedup_head(HEAD_OLDEST)?;
        let oldest = oldest_word.load(Ordering::SeqCst);

        let entry = self.dedup_find_entry(oldest)?;
        self.dedup_remove_entry(entry)?;

        oldest_word.store(oldest.wrapping_add(1), Ordering::SeqCst);
        Ok(())
    }

    /// Returns whether a record of the key has not expired yet.
    fn dedup_has_live_record(&self, key: &DedupKey, now_us: u64) -> Result<bool, RegionError> {
        let capacity = self.layout().dedup_index_capacity;
        let start = probe_start(key.first, capacity);

        for step in 0..capacity {
            let entry = start.wrapping_add(step) % capacity;
            let stored = self.dedup_index(entry)?.load(Ordering::SeqCst);

            // The records of the key are all ahead of the first empty entry of its probe path
            if stored == EMPTY_INDEX {
                return Ok(false);
            }

            // A key with a record that expired behind an older record of a longer window may have a second record,
            // so the probe continues past a record of the key that expired
            let counter = stored.wrapping_sub(1);
            let first_hash = self.dedup_record(counter, RECORD_FIRST_HASH)?.load(Ordering::SeqCst);
            let second_hash = self.dedup_record(counter, RECORD_SECOND_HASH)?.load(Ordering::SeqCst);
            let expiry = self.dedup_record(counter, RECORD_EXPIRY)?.load(Ordering::SeqCst);

            if first_hash == key.first && second_hash == key.second && expiry > now_us {
                return Ok(true);
            }
        }

        Ok(false)
    }

    /// Records a key with the given expiry time, after the oldest record if the table is full.
    fn dedup_record_key(&self, key: &DedupKey, expiry_us: u64) -> Result<(), RegionError> {
        let capacity = self.layout().params.dedup_capacity;
        let capacity_word = u64::try_from(capacity).map_err(|_conversion_error| RegionError::LayoutTooLarge)?;

        let oldest = self.dedup_head(HEAD_OLDEST)?.load(Ordering::SeqCst);
        let next_word = self.dedup_head(HEAD_NEXT)?;
        let next = next_word.load(Ordering::SeqCst);

        // A full table makes room by dropping the record it has held longest, as the cache of one process does
        if next.wrapping_sub(oldest) >= capacity_word {
            self.dedup_drop_oldest()?;
        }

        self.dedup_record(next, RECORD_FIRST_HASH)?.store(key.first, Ordering::SeqCst);
        self.dedup_record(next, RECORD_SECOND_HASH)?.store(key.second, Ordering::SeqCst);
        self.dedup_record(next, RECORD_EXPIRY)?.store(expiry_us, Ordering::SeqCst);

        // The index has twice as many entries as there are records, so the probe finds an empty entry
        let index_capacity = self.layout().dedup_index_capacity;
        let start = probe_start(key.first, index_capacity);

        for step in 0..index_capacity {
            let entry = start.wrapping_add(step) % index_capacity;
            let entry_word = self.dedup_index(entry)?;

            if entry_word.load(Ordering::SeqCst) == EMPTY_INDEX {
                entry_word.store(next.wrapping_add(1), Ordering::SeqCst);
                next_word.store(next.wrapping_add(1), Ordering::SeqCst);
                return Ok(());
            }
        }

        Err(RegionError::TableFull)
    }

    /// Checks and records a key, under the lock of the table.
    fn dedup_check_locked(&self, key: &DedupKey, ttl_us: u64, now_us: u64) -> Result<DedupCheck, RegionError> {

        // The records that expired leave from the front, up to the first record that has not ..
        loop {
            let oldest = self.dedup_head(HEAD_OLDEST)?.load(Ordering::SeqCst);
            let next = self.dedup_head(HEAD_NEXT)?.load(Ordering::SeqCst);

            if oldest == next {
                break;
            }

            if self.dedup_record(oldest, RECORD_EXPIRY)?.load(Ordering::SeqCst) > now_us {
                break;
            }

            self.dedup_drop_oldest()?;
        }

        // .. a key with a live record is a duplicate ..
        if self.dedup_has_live_record(key, now_us)? {
            return Ok(DedupCheck::Duplicate);
        }

        // .. and any other is recorded until its window ends.
        let expiry_us = now_us.saturating_add(ttl_us);
        self.dedup_record_key(key, expiry_us)?;

        Ok(DedupCheck::New)
    }

    /// Checks whether a control ID was recorded within its window, recording it if it was not.
    ///
    /// The window of a control ID is `ttl_us` microseconds from `now_us`, both read from the monotonic clock,
    /// which every process of the host reads alike.
    pub fn dedup_check(&self, key: &DedupKey, owner: DedupOwner, ttl_us: u64, now_us: u64) -> Result<DedupCheck, RegionError> {
        if self.layout().params.dedup_capacity == 0 {
            return Err(RegionError::TableFull);
        }

        let Some(needs_clear) = self.dedup_lock(owner)? else {
            return Ok(DedupCheck::Busy);
        };

        // The holder that exited may have left the records and the index partially updated
        let cleared = if needs_clear { self.dedup_clear() } else { Ok(()) };
        let out = cleared.and_then(|()| self.dedup_check_locked(key, ttl_us, now_us));

        // The lock is released after an error too, which leaves the table as consistent as the operation that failed did
        self.dedup_head(HEAD_LOCK)?.store(UNLOCKED, Ordering::SeqCst);

        out
    }
}

#[cfg(test)]
#[path = "dedup_tests.rs"]
mod tests;
