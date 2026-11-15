//! Circuit breakers of outgoing connections shared by the workers.
//!
//! Each breaker keeps its state and the time it was opened in one word, updated with a single compare-and-swap,
//! so of the workers that find the reset period over only one moves the breaker to half-open and sends the trial message,
//! and a worker terminated at any instruction leaves no breaker in an intermediate state.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;
use crate::view::{EMPTY_KEY, RegionView, key_hash, probe_start};

/// Seed of the hash of the keys of breakers.
const BREAKER_KIND: u64 = 0x4252_4541_4B52;

/// Position of the key hash within a breaker block.
const BREAKER_KEY: usize = 0;

/// Position of the state word within a breaker block.
const BREAKER_STATE: usize = 1;

/// State of a breaker that lets every message through.
pub const BREAKER_CLOSED: u64 = 0;

/// State of a breaker that lets no message through until its reset period is over.
pub const BREAKER_OPEN: u64 = 1;

/// State of a breaker whose one trial message is being sent.
pub const BREAKER_HALF_OPEN: u64 = 2;

/// Number of bits of a state word that hold the state.
const STATE_BITS: u32 = 2;

/// Mask of the state within a state word.
const STATE_MASK: u64 = (1 << STATE_BITS) - 1;

/// The state of one breaker and the time it was last opened.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BreakerState {

    /// One of `BREAKER_CLOSED`, `BREAKER_OPEN` and `BREAKER_HALF_OPEN`.
    pub state: u64,

    /// Reading of the monotonic clock, in microseconds, at which the breaker was last opened.
    pub opened_at_us: u64,
}

/// Unpacks a state word.
const fn parse_state(word: u64) -> BreakerState {
    BreakerState {
        state: word & STATE_MASK,
        opened_at_us: word >> STATE_BITS,
    }
}

/// Packs a state and the time the breaker was opened into a state word.
const fn state_word(state: u64, opened_at_us: u64) -> u64 {
    (opened_at_us << STATE_BITS) | state
}

impl RegionView<'_> {

    /// Returns the offset of one field of a breaker block.
    fn breaker_field(&self, entry: usize, field: usize) -> Result<usize, RegionError> {
        Self::block_word(self.layout().breakers_start, entry, field)
    }

    /// Returns the state word of the breaker of a key, claiming an empty entry for it when the key has none.
    fn breaker_word(&self, key: &str) -> Result<&AtomicU64, RegionError> {
        let hash = key_hash(BREAKER_KIND, key);
        let capacity = self.layout().params.breaker_capacity;
        let start = probe_start(hash, capacity);

        for step in 0..capacity {
            // Linear probing visits every entry once, starting from the key's own
            let entry = start.wrapping_add(step) % capacity;
            let key_word = self.word(self.breaker_field(entry, BREAKER_KEY)?)?;
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
                let out = self.word(self.breaker_field(entry, BREAKER_STATE)?)?;
                return Ok(out);
            }
        }

        Err(RegionError::TableFull)
    }

    /// Moves a breaker from `from` to the state that `next` returns for its current state, if it is in `from`,
    /// returning whether this call moved it.
    fn breaker_move<Next>(&self, key: &str, from: u64, next: Next) -> Result<bool, RegionError>
    where
        Next: Fn(BreakerState) -> Option<u64>,
    {
        let word = self.breaker_word(key)?;
        let mut current = word.load(Ordering::SeqCst);

        loop {
            let parsed = parse_state(current);

            // A breaker in another state was moved by another worker, or is not due to move yet
            if parsed.state != from {
                return Ok(false);
            }

            let Some(next_word) = next(parsed) else {
                return Ok(false);
            };

            // Another worker changed the breaker since it was read, so the decision is made again on its value
            match word.compare_exchange(current, next_word, Ordering::SeqCst, Ordering::SeqCst) {
                Ok(_) => return Ok(true),
                Err(changed) => current = changed,
            }
        }
    }

    /// Returns the state of the breaker of a key.
    pub fn breaker_state(&self, key: &str) -> Result<BreakerState, RegionError> {
        let word = self.breaker_word(key)?.load(Ordering::SeqCst);
        Ok(parse_state(word))
    }

    /// Opens a closed breaker, for a worker whose share of failed sends reached its limit.
    pub fn breaker_open(&self, key: &str, now_us: u64) -> Result<bool, RegionError> {
        self.breaker_move(key, BREAKER_CLOSED, |_closed| Some(state_word(BREAKER_OPEN, now_us)))
    }

    /// Moves an open breaker whose reset period is over to half-open, returning whether this worker sends the trial message.
    pub fn breaker_begin_trial(&self, key: &str, now_us: u64, reset_us: u64) -> Result<bool, RegionError> {
        self.breaker_move(key, BREAKER_OPEN, |open| {
            let elapsed_us = now_us.saturating_sub(open.opened_at_us);

            // The breaker stays open until its reset period is over
            if elapsed_us >= reset_us { Some(state_word(BREAKER_HALF_OPEN, open.opened_at_us)) } else { None }
        })
    }

    /// Concludes the trial message of a half-open breaker, closing it after a success and opening it again after a failure.
    pub fn breaker_end_trial(&self, key: &str, is_success: bool, now_us: u64) -> Result<bool, RegionError> {
        let next_word = if is_success { state_word(BREAKER_CLOSED, 0) } else { state_word(BREAKER_OPEN, now_us) };
        self.breaker_move(key, BREAKER_HALF_OPEN, |_half_open| Some(next_word))
    }
}

#[cfg(test)]
#[path = "breakers_tests.rs"]
mod tests;
