//! Keyed locks shared by the workers, one per outgoing connection, each with a counter and a first-in first-out queue.
//!
//! A key claims one entry of the lock table, whose block holds the hash of the key and the counter. The queue
//! of the entry follows the writer queues of the region and is taken in turns the way a writer queue is,
//! so the lock of a worker terminated at any instruction passes on once the arbiter abandons its tickets.
//! The counter starts unset, and the first worker that sets it from the database at startup does so only
//! while no worker has changed it, so a worker started later never overwrites a counter that is in use.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;
use crate::view::{EMPTY_KEY, RegionView, key_hash, probe_start};

/// Seed of the hash of the keys of locks.
const LOCK_KIND: u64 = 0x4C4F_434B;

/// Position of the key hash within a lock block.
const LOCK_KEY: usize = 0;

/// Position of the counter word within a lock block.
const LOCK_COUNTER: usize = 1;

/// Counter word of a lock whose counter no worker has set or changed.
const COUNTER_UNSET: u64 = 0;

/// Offset of a counter word from the value it holds, so that a value of zero differs from an unset counter.
const COUNTER_BIAS: u64 = 1 << 62;

/// Returns the value that a counter word holds, zero for an unset counter.
const fn counter_value(word: u64) -> i64 {
    if word == COUNTER_UNSET { 0 } else { word.wrapping_sub(COUNTER_BIAS).cast_signed() }
}

/// Returns the counter word that holds a value.
const fn counter_word(value: i64) -> u64 {
    COUNTER_BIAS.wrapping_add_signed(value)
}

impl RegionView<'_> {

    /// Returns the offset of one field of a lock block.
    fn lock_field(&self, entry: usize, field: usize) -> Result<usize, RegionError> {

        // An entry past the table would address the words of another table or none at all
        if entry >= self.layout().params.lock_capacity {
            return Err(RegionError::NoSuchLock(entry));
        }

        Self::block_word(self.layout().locks_start, entry, field)
    }

    /// Returns the entry of the lock of a key, claiming an empty entry for it when the key has none.
    pub fn lock_entry(&self, key: &str) -> Result<usize, RegionError> {
        let hash = key_hash(LOCK_KIND, key);
        let capacity = self.layout().params.lock_capacity;
        let start = probe_start(hash, capacity);

        for step in 0..capacity {
            // Linear probing visits every entry once, starting from the key's own
            let entry = start.wrapping_add(step) % capacity;
            let key_word = self.word(self.lock_field(entry, LOCK_KEY)?)?;
            let current = key_word.load(Ordering::SeqCst);

            let is_own = if current == hash {
                true
            } else if current == EMPTY_KEY {
                // Another worker may claim the same entry at this moment, for this key or for another one
                match key_word.compare_exchange(EMPTY_KEY, hash, Ordering::SeqCst, Ordering::SeqCst) {
                    Ok(_) => true,
                    Err(winner) => winner == hash,
                }
            } else {
                false
            };

            if is_own {
                return Ok(entry);
            }
        }

        Err(RegionError::TableFull)
    }

    /// Returns the queue of the lock of an entry, which follows the writer queues of the region.
    pub fn lock_queue(&self, entry: usize) -> Result<usize, RegionError> {
        let params = self.layout().params;

        if entry >= params.lock_capacity {
            return Err(RegionError::NoSuchLock(entry));
        }

        params.queue_count.checked_add(entry).ok_or(RegionError::OutOfBounds)
    }

    /// Returns the counter word of the lock of an entry.
    fn lock_counter_word(&self, entry: usize) -> Result<&AtomicU64, RegionError> {
        self.word(self.lock_field(entry, LOCK_COUNTER)?)
    }

    /// Returns the value of the counter of the lock of an entry.
    pub fn lock_counter(&self, entry: usize) -> Result<i64, RegionError> {
        let word = self.lock_counter_word(entry)?.load(Ordering::SeqCst);
        Ok(counter_value(word))
    }

    /// Adds a delta to the counter of the lock of an entry and returns the new value.
    pub fn lock_counter_add(&self, entry: usize, delta: i64) -> Result<i64, RegionError> {
        let word = self.lock_counter_word(entry)?;
        let mut current = word.load(Ordering::SeqCst);

        loop {
            let value = counter_value(current).saturating_add(delta);

            // A change of the counter by another worker since it was read makes the addition start again from its value
            match word.compare_exchange(current, counter_word(value), Ordering::SeqCst, Ordering::SeqCst) {
                Ok(_) => return Ok(value),
                Err(changed) => current = changed,
            }
        }
    }

    /// Sets the counter of the lock of an entry, if no worker has set or changed it yet, returning whether this call set it.
    pub fn lock_counter_init(&self, entry: usize, value: i64) -> Result<bool, RegionError> {
        let word = self.lock_counter_word(entry)?;
        let out = word
            .compare_exchange(COUNTER_UNSET, counter_word(value), Ordering::SeqCst, Ordering::SeqCst)
            .is_ok();

        Ok(out)
    }

    /// Replaces the value of the counter of the lock of an entry, if it still holds the value that the caller read,
    /// returning whether this call replaced it.
    pub fn lock_counter_replace(&self, entry: usize, expected: i64, value: i64) -> Result<bool, RegionError> {
        let word = self.lock_counter_word(entry)?;
        let current = word.load(Ordering::SeqCst);

        // A counter that another worker changed since the caller read it keeps the value of that worker
        if counter_value(current) != expected {
            return Ok(false);
        }

        // A change by another worker between the load and the exchange is reported in the same way
        let out = word
            .compare_exchange(current, counter_word(value), Ordering::SeqCst, Ordering::SeqCst)
            .is_ok();

        Ok(out)
    }
}

#[cfg(test)]
#[path = "locks_tests.rs"]
mod tests;
