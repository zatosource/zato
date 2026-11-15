//! Rate limiting cells shared by the workers - token buckets and fixed windows.
//!
//! Each cell keeps its whole state in one word, updated with a single compare-and-swap,
//! so the workers together count every request once and a worker terminated at any
//! instruction leaves no cell in an intermediate state.
//!
//! A token bucket is kept as the theoretical arrival time of the generic cell rate algorithm,
//! in nanoseconds since the epoch, which is equivalent to a bucket that refills continuously
//! and is clamped at its burst. The time stored never moves back, because the algorithm
//! works from the later of the stored time and the caller's clock reading.
//! A bucket whose rate is zero never refills and keeps the number of tokens it handed out instead.
//!
//! A fixed window keeps the end of its window, in whole seconds since the epoch, and the number of requests counted in it.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;
use crate::view::{EMPTY_KEY, RegionView, key_hash, probe_start};

/// Seed of the hash of token bucket keys.
const TOKEN_BUCKET_KIND: u64 = 0x544F_4B45_4E42;

/// Seed of the hash of fixed window keys.
const FIXED_WINDOW_KIND: u64 = 0x4649_5845_4457;

/// Seed of the hash of the groups that a clear of counters resets together.
const GROUP_KIND: u64 = 0x4752_4F55_5053;

/// Position of the key hash within a cell block.
const CELL_KEY: usize = 0;

/// Position of the group hash within a cell block.
const CELL_GROUP: usize = 1;

/// Position of the state within a cell block.
const CELL_STATE: usize = 2;

/// State word of a cell that was never used or was reset - a full bucket or a window that has ended.
const RESET_STATE: u64 = 0;

/// Marks the state of a token bucket whose rate is zero, the rest of the word being the tokens handed out.
const NO_REFILL_FLAG: u64 = 1 << 63;

/// Nanoseconds in one second.
const NANOS_PER_SECOND: u64 = 1_000_000_000;

/// Nanoseconds in one microsecond.
const NANOS_PER_MICRO: u64 = 1_000;

/// Microseconds in one second.
const MICROS_PER_SECOND: u64 = 1_000_000;

/// Shortest interval between two tokens, for rates above one token per nanosecond.
const MIN_EMISSION_NANOS: u64 = 1;

/// How long a caller waits for a bucket that never refills, as the in-process registry reports it.
const NO_REFILL_RETRY_US: u64 = MICROS_PER_SECOND;

/// Number of bits of a fixed window state that hold the count.
const WINDOW_COUNT_BITS: u32 = 32;

/// Mask of the count within a fixed window state.
const WINDOW_COUNT_MASK: u64 = (1 << WINDOW_COUNT_BITS) - 1;

/// The outcome of one check of a cell.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CellCheck {

    /// Whether the request is allowed.
    pub is_allowed: bool,

    /// Whole tokens, or requests of the window, left after this check.
    pub remaining: u64,

    /// Microseconds until a request would be allowed, zero for an allowed request.
    pub retry_after_us: u64,
}

impl CellCheck {

    /// Returns the outcome of an allowed request.
    const fn allowed(remaining: u64) -> Self {
        Self {
            is_allowed: true,
            remaining,
            retry_after_us: 0,
        }
    }

    /// Returns the outcome of a denied request.
    const fn denied(retry_after_us: u64) -> Self {
        Self {
            is_allowed: false,
            remaining: 0,
            retry_after_us,
        }
    }
}

/// The configuration of a token bucket, as the rule of a channel gives it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TokenBucketParams {

    /// Tokens added per second.
    pub rate: u64,

    /// Most tokens the bucket holds.
    pub burst: u64,
}

/// The configuration of one check of a fixed window.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FixedWindowParams {

    /// Most requests allowed within one window.
    pub limit: u64,

    /// End, in microseconds since the epoch, of the window that starts at the caller's clock reading.
    pub window_end_us: u64,
}

/// The hashes of one rate limiting key and of the group a clear of counters resets it with.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CellKey {

    /// Hash of the key in the token bucket namespace.
    token_bucket: u64,

    /// Hash of the key in the fixed window namespace.
    fixed_window: u64,

    /// Hash of the group of the key.
    group: u64,
}

impl CellKey {

    /// Hashes a key and its group, for example `rest.orders:10.0.0.0/8:0` and `rest.orders:10.0.0.0/8:`.
    #[must_use]
    pub fn new(key: &str, group: &str) -> Self {
        Self {
            token_bucket: key_hash(TOKEN_BUCKET_KIND, key),
            fixed_window: key_hash(FIXED_WINDOW_KIND, key),
            group: key_hash(GROUP_KIND, group),
        }
    }
}

/// Converts a wide intermediate value back to a word, saturating at the largest word.
fn narrow(value: u128) -> u64 {
    u64::try_from(value).unwrap_or(u64::MAX)
}

/// Decides one request against a token bucket whose state is `state`, returning the outcome and the state to store.
fn decide_token_bucket(state: u64, params: TokenBucketParams, now_us: u64) -> (CellCheck, Option<u64>) {
    // A bucket with no capacity allows nothing, and waits as long as one token takes to arrive.
    if params.burst == 0 {
        let retry_after_us = MICROS_PER_SECOND
            .checked_div(params.rate)
            .map_or(NO_REFILL_RETRY_US, |interval| interval.saturating_add(1));
        return (CellCheck::denied(retry_after_us), None);
    }

    // A bucket that never refills counts the tokens it handed out, from zero after a change from a positive rate.
    if params.rate == 0 {
        let used = if state & NO_REFILL_FLAG == 0 { 0 } else { state & !NO_REFILL_FLAG };

        if used < params.burst {
            let next_used = used.saturating_add(1);
            let remaining = params.burst.saturating_sub(next_used);
            return (CellCheck::allowed(remaining), Some(NO_REFILL_FLAG | next_used));
        }

        return (CellCheck::denied(NO_REFILL_RETRY_US), None);
    }

    let emission = u128::from((NANOS_PER_SECOND / params.rate).max(MIN_EMISSION_NANOS));
    let burst_minus_one = u128::from(params.burst.saturating_sub(1));
    let tolerance = emission.saturating_mul(burst_minus_one);
    let reading_ns = u128::from(now_us).saturating_mul(u128::from(NANOS_PER_MICRO));

    // A state left by a rate of zero is read as a full bucket.
    let arrival = if state & NO_REFILL_FLAG == 0 { u128::from(state) } else { 0 };

    // The later of the stored time and the caller's reading, so a caller with an earlier reading never moves time back.
    let base = arrival.max(reading_ns);
    let backlog = base.saturating_sub(reading_ns);

    if backlog > tolerance {
        let wait_ns = backlog.saturating_sub(tolerance);
        let retry_after_us = narrow(wait_ns.div_ceil(u128::from(NANOS_PER_MICRO)));
        return (CellCheck::denied(retry_after_us), None);
    }

    let next_arrival = narrow(base.saturating_add(emission));
    let remaining = narrow(tolerance.saturating_sub(backlog) / emission);

    (CellCheck::allowed(remaining), Some(next_arrival))
}

/// Decides one request against a fixed window whose state is `state`, returning the outcome and the state to store.
fn decide_fixed_window(state: u64, params: FixedWindowParams, now_us: u64) -> (CellCheck, Option<u64>) {
    let stored_end_seconds = state >> WINDOW_COUNT_BITS;
    let stored_end_micros = stored_end_seconds.saturating_mul(MICROS_PER_SECOND);

    // A window that has ended is replaced by the one the caller computed from its clock reading.
    let (end_seconds, count) = if now_us >= stored_end_micros {
        (params.window_end_us / MICROS_PER_SECOND, 0)
    } else {
        (stored_end_seconds, state & WINDOW_COUNT_MASK)
    };

    let limit = params.limit.min(WINDOW_COUNT_MASK);

    if count < limit {
        let next_count = count.saturating_add(1);
        let remaining = limit.saturating_sub(next_count);
        let next_state = (end_seconds << WINDOW_COUNT_BITS) | next_count;
        return (CellCheck::allowed(remaining), Some(next_state));
    }

    let end_micros = end_seconds.saturating_mul(MICROS_PER_SECOND);
    let retry_after_us = end_micros.saturating_sub(now_us);

    (CellCheck::denied(retry_after_us), None)
}

impl RegionView<'_> {

    /// Returns the offset of one field of a cell block.
    fn cell_word(&self, entry: usize, field: usize) -> Result<usize, RegionError> {
        Self::block_word(self.layout().cells_start, entry, field)
    }

    /// Returns the state word of the cell of a key, claiming an empty cell for it when the key has none.
    fn cell_state(&self, hash: u64, group: u64) -> Result<&AtomicU64, RegionError> {
        let capacity = self.layout().params.cell_capacity;
        let start = probe_start(hash, capacity);

        for step in 0..capacity {
            // Linear probing visits every cell once, starting from the key's own.
            let entry = start.wrapping_add(step) % capacity;
            let key_word = self.word(self.cell_word(entry, CELL_KEY)?)?;
            let current = key_word.load(Ordering::SeqCst);

            let is_own = if current == hash {
                true
            } else if current == EMPTY_KEY {
                // Another worker may claim the same cell at this moment, for this key or for another one.
                match key_word.compare_exchange(EMPTY_KEY, hash, Ordering::SeqCst, Ordering::SeqCst) {
                    Ok(_) => true,
                    Err(winner) => winner == hash,
                }
            } else {
                false
            };

            if is_own {
                // The claimer may be terminated before it stores the group, or be about to store it, so every worker
                // of the key stores it before its count, which a clear of the group then always finds.
                let group_word = self.word(self.cell_word(entry, CELL_GROUP)?)?;

                if group_word.load(Ordering::SeqCst) == EMPTY_KEY {
                    group_word.store(group, Ordering::SeqCst);
                }

                let out = self.word(self.cell_word(entry, CELL_STATE)?)?;
                return Ok(out);
            }
        }

        Err(RegionError::TableFull)
    }

    /// Applies `decide` to the state of a cell until its compare-and-swap succeeds.
    fn check_cell<Decide>(&self, hash: u64, group: u64, decide: Decide) -> Result<CellCheck, RegionError>
    where
        Decide: Fn(u64) -> (CellCheck, Option<u64>),
    {
        let state_word = self.cell_state(hash, group)?;
        let mut state = state_word.load(Ordering::SeqCst);

        loop {
            let (check, next_state) = decide(state);

            // A denied request changes nothing, so there is nothing to store.
            let Some(next_state) = next_state else {
                return Ok(check);
            };

            // Another worker changed the cell since it was read, so the decision is made again on its value.
            match state_word.compare_exchange(state, next_state, Ordering::SeqCst, Ordering::SeqCst) {
                Ok(_) => return Ok(check),
                Err(current) => state = current,
            }
        }
    }

    /// Takes one token from the bucket of a key.
    pub fn token_bucket_check(&self, key: &CellKey, params: TokenBucketParams, now_us: u64) -> Result<CellCheck, RegionError> {
        self.check_cell(key.token_bucket, key.group, |state| decide_token_bucket(state, params, now_us))
    }

    /// Counts one request in the fixed window of a key.
    pub fn fixed_window_check(&self, key: &CellKey, params: FixedWindowParams, now_us: u64) -> Result<CellCheck, RegionError> {
        self.check_cell(key.fixed_window, key.group, |state| decide_fixed_window(state, params, now_us))
    }

    /// Resets the token bucket and the fixed window of a key.
    ///
    /// The key keeps its cell, because an emptied cell ahead of another key's cell
    /// would end a later probe for that key early and give it a second cell.
    pub fn cell_reset(&self, key: &str) -> Result<(), RegionError> {
        let hashes = [key_hash(TOKEN_BUCKET_KIND, key), key_hash(FIXED_WINDOW_KIND, key)];
        let capacity = self.layout().params.cell_capacity;

        for entry in 0..capacity {
            let current = self.word(self.cell_word(entry, CELL_KEY)?)?.load(Ordering::SeqCst);

            if hashes.contains(&current) {
                self.word(self.cell_word(entry, CELL_STATE)?)?.store(RESET_STATE, Ordering::SeqCst);
            }
        }

        Ok(())
    }

    /// Resets every cell of a group, which is what a clear of the counters of one rule does in every worker at once.
    pub fn cell_reset_group(&self, group: &str) -> Result<(), RegionError> {
        let group_hash = key_hash(GROUP_KIND, group);
        let capacity = self.layout().params.cell_capacity;

        for entry in 0..capacity {
            let current = self.word(self.cell_word(entry, CELL_GROUP)?)?.load(Ordering::SeqCst);

            if current == group_hash {
                self.word(self.cell_word(entry, CELL_STATE)?)?.store(RESET_STATE, Ordering::SeqCst);
            }
        }

        Ok(())
    }

    /// Resets every cell of the table.
    pub fn cell_reset_all(&self) -> Result<(), RegionError> {
        let capacity = self.layout().params.cell_capacity;

        for entry in 0..capacity {
            self.word(self.cell_word(entry, CELL_STATE)?)?.store(RESET_STATE, Ordering::SeqCst);
        }

        Ok(())
    }
}

#[cfg(test)]
#[path = "cells_tests.rs"]
mod tests;
