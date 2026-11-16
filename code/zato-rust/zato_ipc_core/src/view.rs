//! Access to the words of a shared memory region through its layout.

use std::sync::atomic::AtomicU64;

use xxhash_rust::xxh3::xxh3_64_with_seed;

use crate::error::RegionError;
use crate::layout::{Layout, PLACE_COUNT};

/// Key word of a table entry that no key has claimed yet.
pub const EMPTY_KEY: u64 = 0;

/// Key word stored in place of a hash that equals `EMPTY_KEY`.
const EMPTY_KEY_REPLACEMENT: u64 = 1;

/// The words of one region together with the layout that divides them into tables.
#[derive(Debug, Clone, Copy)]
pub struct RegionView<'region> {

    /// Every word of the region.
    words: &'region [AtomicU64],

    /// Offsets of the tables within `words`.
    layout: Layout,
}

impl<'region> RegionView<'region> {

    /// Returns a view of the given words, which must cover the whole layout.
    pub const fn new(words: &'region [AtomicU64], layout: Layout) -> Result<Self, RegionError> {
        if words.len() < layout.total_words {
            return Err(RegionError::OutOfBounds);
        }

        let out = Self { words, layout };
        Ok(out)
    }

    /// Returns the layout of the region.
    #[must_use]
    pub const fn layout(&self) -> &Layout {
        &self.layout
    }

    /// Returns every word of the region.
    #[must_use]
    pub const fn words(&self) -> &'region [AtomicU64] {
        self.words
    }

    /// Returns the word at the given offset.
    pub fn word(&self, index: usize) -> Result<&'region AtomicU64, RegionError> {
        let out = self.words.get(index).ok_or(RegionError::OutOfBounds)?;
        Ok(out)
    }

    /// Returns the offset of a word within a block that follows `start`.
    pub fn block_word(start: usize, block: usize, field: usize) -> Result<usize, RegionError> {
        let block_offset = block.checked_mul(crate::layout::BLOCK_WORDS).ok_or(RegionError::OutOfBounds)?;
        let block_start = start.checked_add(block_offset).ok_or(RegionError::OutOfBounds)?;
        let out = block_start.checked_add(field).ok_or(RegionError::OutOfBounds)?;
        Ok(out)
    }

    /// Confirms that a place exists in the queues, which is the place of the worker or that of the config process.
    pub const fn check_queue_place(place: usize) -> Result<(), RegionError> {
        if place < PLACE_COUNT {
            Ok(())
        } else {
            Err(RegionError::NoSuchPlace(place))
        }
    }
}

/// Returns the key word of a table entry for a key of the given kind.
///
/// Every process computes the same value for the same key, because the hash has no per-process seed.
/// The kind is the seed, so equal keys of different kinds occupy different entries.
#[must_use]
pub fn key_hash(kind: u64, key: &str) -> u64 {
    let hash = xxh3_64_with_seed(key.as_bytes(), kind);

    // Zero marks an unclaimed entry, so a key that hashes to it is stored under another value.
    if hash == EMPTY_KEY { EMPTY_KEY_REPLACEMENT } else { hash }
}

/// Returns the entry at which a probe for the given key starts in a table of the given capacity.
#[must_use]
pub fn probe_start(hash: u64, capacity: usize) -> usize {
    let capacity_word = u64::try_from(capacity).unwrap_or(u64::MAX);

    // A table of no entries has nowhere to start, and the probe that follows finds no entry.
    let remainder = hash.checked_rem(capacity_word).unwrap_or(0);

    usize::try_from(remainder).unwrap_or(0)
}

#[cfg(test)]
pub mod test_support {
    //! Regions held in ordinary memory for the unit tests of the tables.

    use std::sync::atomic::AtomicU64;

    use crate::error::RegionError;
    use crate::layout::{Layout, RegionParams};

    /// Returns the words and the layout of a region with the given sizes, held in leaked memory.
    pub fn new_words(params: RegionParams) -> Result<(&'static [AtomicU64], Layout), RegionError> {
        let layout = Layout::new(params)?;

        let mut words = Vec::with_capacity(layout.total_words);
        words.resize_with(layout.total_words, AtomicU64::default);

        let leaked: &'static [AtomicU64] = Vec::leak(words);
        Ok((leaked, layout))
    }

    /// Returns the sizes of a small region used by most tests.
    #[must_use]
    pub const fn small_params() -> RegionParams {
        RegionParams {
            queue_count: 2,
            lock_capacity: 4,
        }
    }
}
