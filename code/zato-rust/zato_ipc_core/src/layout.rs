//! Word layout of the shared memory region of a Zato server.
//!
//! The region is an array of 64-bit atomic words divided into blocks of 128 bytes.
//! Every part that one process writes on the path of a request starts at a block
//! of its own, so a write by one process never invalidates a cache line written by the other.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;

/// Number of bytes in one word of the region.
pub const BYTES_PER_WORD: usize = 8;

/// Number of words in one block, 128 bytes, which covers a pair of cache lines
/// that the adjacent-line prefetcher of x86 processors loads together.
pub const BLOCK_WORDS: usize = 16;

/// Value of the first word of every region, the ASCII text `ZATOSHM1`.
pub const REGION_MAGIC: u64 = 0x5A41_544F_5348_4D31;

/// Version of the layout described in this module.
pub const LAYOUT_VERSION: u64 = 7;

/// Position of the magic word within the header block.
pub const HEADER_MAGIC: usize = 0;

/// Position of the layout version within the header block.
pub const HEADER_VERSION: usize = 1;

/// Position of the number of writer queues within the header block.
pub const HEADER_QUEUE_COUNT: usize = 2;

/// Position of the number of entries of the table of keyed locks within the header block.
pub const HEADER_LOCK_CAPACITY: usize = 3;

/// Number of header blocks.
const HEADER_BLOCKS: usize = 1;

/// Number of blocks of the heartbeat of the worker.
const HEARTBEAT_BLOCKS: usize = 1;

/// Place of the worker in every writer queue and in the queue of every keyed lock.
pub const WORKER_PLACE: usize = 0;

/// Place of the config process in every writer queue and in the queue of every keyed lock.
pub const CONFIG_PLACE: usize = 1;

/// Number of places of every queue - the worker and the config process.
pub const PLACE_COUNT: usize = 2;

/// Sizes of the tables of one region, fixed when the arbiter creates it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RegionParams {

    /// Number of first-in first-out queues of `SQLite` writers, one per database file.
    pub queue_count: usize,

    /// Number of entries of the table of keyed locks, each with a counter and a first-in first-out queue.
    pub lock_capacity: usize,
}

/// Word offsets of every table of a region, computed from its parameters.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Layout {

    /// The sizes the offsets were computed from.
    pub params: RegionParams,

    /// Offset of the first word of the block of the heartbeat of the worker.
    pub heartbeat_start: usize,

    /// Offset of the first word of the writer queues.
    pub queues_start: usize,

    /// Offset of the first word of the table of keyed locks.
    pub locks_start: usize,

    /// Number of blocks of one queue - its head block and one block per place.
    pub blocks_per_queue: usize,

    /// Number of queues - the writer queues, followed by the queue of each keyed lock.
    pub queue_total: usize,

    /// Number of words of the whole region.
    pub total_words: usize,
}

/// Returns the number of words in the given number of blocks.
fn blocks_to_words(blocks: usize) -> Result<usize, RegionError> {
    let out = blocks.checked_mul(BLOCK_WORDS).ok_or(RegionError::LayoutTooLarge)?;
    Ok(out)
}

/// Returns `start` advanced by `count` items of `blocks_per_item` blocks each.
fn advance(start: usize, count: usize, blocks_per_item: usize) -> Result<usize, RegionError> {
    let blocks = count.checked_mul(blocks_per_item).ok_or(RegionError::LayoutTooLarge)?;
    let words = blocks_to_words(blocks)?;
    let out = start.checked_add(words).ok_or(RegionError::LayoutTooLarge)?;
    Ok(out)
}

/// Converts a size of the parameters to the value of a header word.
fn to_header_word(value: usize) -> u64 {
    u64::try_from(value).unwrap_or(u64::MAX)
}

impl Layout {

    /// Computes the offsets of every table of a region with the given sizes.
    pub fn new(params: RegionParams) -> Result<Self, RegionError> {

        // A queue has its head block followed by one ticket block per place ..
        let blocks_per_queue = PLACE_COUNT.checked_add(1).ok_or(RegionError::LayoutTooLarge)?;

        // .. and the queue of each keyed lock has the same blocks as a writer queue and follows the writer queues.
        let queue_total = params.queue_count.checked_add(params.lock_capacity).ok_or(RegionError::LayoutTooLarge)?;

        let heartbeat_start = blocks_to_words(HEADER_BLOCKS)?;
        let queues_start = advance(heartbeat_start, HEARTBEAT_BLOCKS, 1)?;
        let locks_start = advance(queues_start, queue_total, blocks_per_queue)?;

        // Each keyed lock occupies a block of its own.
        let total_words = advance(locks_start, params.lock_capacity, 1)?;

        let out = Self {
            params,
            heartbeat_start,
            queues_start,
            locks_start,
            blocks_per_queue,
            queue_total,
            total_words,
        };

        Ok(out)
    }

    /// Returns the number of bytes of the whole region.
    pub fn total_bytes(&self) -> Result<usize, RegionError> {
        let out = self.total_words.checked_mul(BYTES_PER_WORD).ok_or(RegionError::LayoutTooLarge)?;
        Ok(out)
    }

    /// Writes the header of a region that is created with this layout.
    pub fn write_header(&self, words: &[AtomicU64]) -> Result<(), RegionError> {
        let params = &self.params;

        let header = [
            (HEADER_MAGIC, REGION_MAGIC),
            (HEADER_VERSION, LAYOUT_VERSION),
            (HEADER_QUEUE_COUNT, to_header_word(params.queue_count)),
            (HEADER_LOCK_CAPACITY, to_header_word(params.lock_capacity)),
        ];

        for (index, value) in header {
            let word = words.get(index).ok_or(RegionError::OutOfBounds)?;
            word.store(value, Ordering::SeqCst);
        }

        Ok(())
    }

    /// Confirms that the header of a region describes this layout, which a process checks before it uses the region.
    pub fn verify_header(&self, words: &[AtomicU64]) -> Result<(), RegionError> {
        let params = &self.params;

        let expected = [
            (HEADER_MAGIC, REGION_MAGIC, "magic"),
            (HEADER_VERSION, LAYOUT_VERSION, "layout version"),
            (HEADER_QUEUE_COUNT, to_header_word(params.queue_count), "queue count"),
            (HEADER_LOCK_CAPACITY, to_header_word(params.lock_capacity), "lock capacity"),
        ];

        for (index, value, field) in expected {
            let word = words.get(index).ok_or(RegionError::OutOfBounds)?;

            if word.load(Ordering::SeqCst) != value {
                return Err(RegionError::LayoutMismatch(field));
            }
        }

        Ok(())
    }
}

#[cfg(test)]
#[path = "layout_tests.rs"]
mod tests;
