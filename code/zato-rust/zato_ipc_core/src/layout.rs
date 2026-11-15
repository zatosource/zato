//! Word layout of the shared memory region of the Zato server workers.
//!
//! The region is an array of 64-bit atomic words divided into blocks of 128 bytes.
//! Every part that one worker writes on the path of a request starts at a block
//! of its own, so a write by one worker never invalidates a cache line written by another.

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
pub const LAYOUT_VERSION: u64 = 6;

/// Position of the magic word within the first block.
pub const HEADER_MAGIC: usize = 0;

/// Position of the layout version within the first block.
pub const HEADER_VERSION: usize = 1;

/// Position of the number of worker slots within the first block.
pub const HEADER_SLOT_COUNT: usize = 2;

/// Position of the capacity of the wake table within the first block.
pub const HEADER_WAKE_CAPACITY: usize = 3;

/// Position of the capacity of the rate limiting table within the first block.
pub const HEADER_CELL_CAPACITY: usize = 4;

/// Position of the number of writer queues within the first block.
pub const HEADER_QUEUE_COUNT: usize = 5;

/// Position of the number of metric counters of each slot within the first block.
pub const HEADER_METRIC_COUNT: usize = 6;

/// Position of the start ID of the arbiter within the first block.
pub const HEADER_START_ID: usize = 7;

/// Position of the number of entries of the series table within the first block.
pub const HEADER_SERIES_CAPACITY: usize = 8;

/// Position of the size in bytes of the area of series records within the first block.
pub const HEADER_SERIES_KEY_BYTES: usize = 9;

/// Position of the number of entries of the table of message control IDs in the header.
pub const HEADER_DEDUP_CAPACITY: usize = 10;

/// Position of the number of entries of the table of circuit breakers in the header.
pub const HEADER_BREAKER_CAPACITY: usize = 11;

/// Position of the number of entries of the table of keyed locks in the header.
pub const HEADER_LOCK_CAPACITY: usize = 12;

/// Number of header blocks - the descriptive header, and the words that the workers change in the second block.
const HEADER_BLOCKS: usize = 2;

/// Block, counted from the start of the region, that holds the overflow counter of the wake table.
const WAKE_OVERFLOW_BLOCK: usize = 1;

/// Offset of the word that counts the wake-ups of keys the full wake table could not record.
pub const WAKE_OVERFLOW_WORD: usize = WAKE_OVERFLOW_BLOCK * BLOCK_WORDS;

/// Offset of the word that counts the words of the area of series records that registrations have taken.
pub const SERIES_KEY_CURSOR_WORD: usize = WAKE_OVERFLOW_WORD + 1;

/// Offset of the word that holds the flags of the server, each of which is one bit that any worker inverts for all of them.
pub const SERVER_FLAGS_WORD: usize = SERIES_KEY_CURSOR_WORD + 1;

/// Number of places of a writer queue beyond those of the worker slots, which are the place of the `SQLite` writer process
/// followed by the place of the config process.
const EXTRA_PLACES: usize = 2;

/// Position of the place of the config process after the places of the worker slots.
const CONFIG_PLACE_OFFSET: usize = 1;

/// Number of blocks of the head of the table of message control IDs, which holds its lock and its two counters.
const DEDUP_HEAD_BLOCKS: usize = 1;

/// Number of words of one record of a message control ID - two hashes of its key and its expiry time.
pub const DEDUP_RECORD_WORDS: usize = 3;

/// Number of index entries for each record of a message control ID.
const DEDUP_INDEX_RATIO: usize = 2;

/// Sizes of the tables of one region, fixed when the arbiter creates it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RegionParams {

    /// Number of worker slots.
    pub slot_count: usize,

    /// Number of entries of the wake counter table of subscription keys.
    pub wake_capacity: usize,

    /// Number of entries of the rate limiting cell table.
    pub cell_capacity: usize,

    /// Number of first-in first-out queues of `SQLite` writers, one per database file.
    pub queue_count: usize,

    /// Number of metric counters kept per slot.
    pub metric_count: usize,

    /// Number of entries of the table of labeled metric series, which is also the number of value cells of each slot.
    pub series_capacity: usize,

    /// Size in bytes of the area that holds the records of labeled metric series with their keys.
    pub series_key_bytes: usize,

    /// Number of message control IDs that the table of duplicates holds, across every channel.
    pub dedup_capacity: usize,

    /// Number of entries of the table of circuit breakers of outgoing connections.
    pub breaker_capacity: usize,

    /// Number of entries of the table of keyed locks, each with a counter and a first-in first-out queue.
    pub lock_capacity: usize,
}

/// Word offsets of every table of a region, computed from its parameters.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Layout {

    /// The sizes the offsets were computed from.
    pub params: RegionParams,

    /// Offset of the first word of the worker slot table.
    pub slots_start: usize,

    /// Offset of the first word of the wake counter table.
    pub wake_start: usize,

    /// Offset of the first word of the rate limiting cell table.
    pub cells_start: usize,

    /// Offset of the first word of the writer queues.
    pub queues_start: usize,

    /// Offset of the first word of the metric counter table.
    pub metrics_start: usize,

    /// Number of blocks each slot's row of the metric table occupies.
    pub metric_blocks_per_slot: usize,

    /// Offset of the first word of the table of series entries, one word per entry.
    pub series_start: usize,

    /// Offset of the first word of the area of series records.
    pub series_keys_start: usize,

    /// Number of words of the area of series records.
    pub series_key_words: usize,

    /// Offset of the first word of the series value table.
    pub series_values_start: usize,

    /// Number of blocks each slot's row of the series value table occupies.
    pub series_blocks_per_slot: usize,

    /// Offset of the first word of the head block of the table of message control IDs.
    pub dedup_start: usize,

    /// Offset of the first word of the records of message control IDs, in the order they were recorded.
    pub dedup_records_start: usize,

    /// Offset of the first word of the index of the records of message control IDs.
    pub dedup_index_start: usize,

    /// Number of entries of the index of the records of message control IDs.
    pub dedup_index_capacity: usize,

    /// Offset of the first word of the table of circuit breakers.
    pub breakers_start: usize,

    /// Offset of the first word of the table of keyed locks.
    pub locks_start: usize,

    /// Number of places of one writer queue - one per worker slot, followed by the places of the writer process
    /// and of the config process.
    pub queue_place_count: usize,

    /// Number of blocks of one writer queue - its head block and one block per place.
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

        // A metric row is rounded up to whole blocks, so the rows of two slots never share a block ..
        let metric_blocks_per_slot = params.metric_count.div_ceil(BLOCK_WORDS);

        // .. and a writer queue has its head block followed by one ticket block per place,
        // the writer process and the config process holding the places after those of the slots.
        let queue_place_count = params.slot_count.checked_add(EXTRA_PLACES).ok_or(RegionError::LayoutTooLarge)?;
        let blocks_per_queue = queue_place_count.checked_add(1).ok_or(RegionError::LayoutTooLarge)?;

        // The queue of each keyed lock has the same blocks as a writer queue and follows the writer queues.
        let queue_total = params.queue_count.checked_add(params.lock_capacity).ok_or(RegionError::LayoutTooLarge)?;

        let slots_start = blocks_to_words(HEADER_BLOCKS)?;
        let wake_start = advance(slots_start, params.slot_count, 1)?;
        let cells_start = advance(wake_start, params.wake_capacity, 1)?;
        let queues_start = advance(cells_start, params.cell_capacity, 1)?;
        let metrics_start = advance(queues_start, queue_total, blocks_per_queue)?;

        // The series entries and records are written once per series, so they are packed into whole blocks,
        // and the series value rows of two slots never share a block, as the metric rows do not.
        let series_entry_blocks = params.series_capacity.div_ceil(BLOCK_WORDS);
        let series_key_words = params.series_key_bytes.div_ceil(BYTES_PER_WORD);
        let series_key_blocks = series_key_words.div_ceil(BLOCK_WORDS);
        let series_blocks_per_slot = params.series_capacity.div_ceil(BLOCK_WORDS);

        // The records of control IDs follow the head block of their table, packed into whole blocks,
        // and the index holds twice as many entries as there are records, so a probe of it ends early ..
        let dedup_record_words = params.dedup_capacity.checked_mul(DEDUP_RECORD_WORDS).ok_or(RegionError::LayoutTooLarge)?;
        let dedup_record_blocks = dedup_record_words.div_ceil(BLOCK_WORDS);
        let dedup_index_capacity = params.dedup_capacity.checked_mul(DEDUP_INDEX_RATIO).ok_or(RegionError::LayoutTooLarge)?;
        let dedup_index_blocks = dedup_index_capacity.div_ceil(BLOCK_WORDS);

        let series_start = advance(metrics_start, params.slot_count, metric_blocks_per_slot)?;
        let series_keys_start = advance(series_start, series_entry_blocks, 1)?;
        let series_values_start = advance(series_keys_start, series_key_blocks, 1)?;
        let dedup_start = advance(series_values_start, params.slot_count, series_blocks_per_slot)?;
        let dedup_records_start = advance(dedup_start, DEDUP_HEAD_BLOCKS, 1)?;
        let dedup_index_start = advance(dedup_records_start, dedup_record_blocks, 1)?;

        // .. and each circuit breaker and each keyed lock occupies a block of its own, as a rate limiting cell does.
        let breakers_start = advance(dedup_index_start, dedup_index_blocks, 1)?;
        let locks_start = advance(breakers_start, params.breaker_capacity, 1)?;
        let total_words = advance(locks_start, params.lock_capacity, 1)?;

        let out = Self {
            params,
            slots_start,
            wake_start,
            cells_start,
            queues_start,
            metrics_start,
            metric_blocks_per_slot,
            series_start,
            series_keys_start,
            series_key_words,
            series_values_start,
            series_blocks_per_slot,
            dedup_start,
            dedup_records_start,
            dedup_index_start,
            dedup_index_capacity,
            breakers_start,
            locks_start,
            queue_place_count,
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

    /// Returns the place of the writer process in every writer queue, which follows the places of the worker slots.
    #[must_use]
    pub const fn writer_place(&self) -> usize {
        self.params.slot_count
    }

    /// Returns the place of the config process in every writer queue, which follows the place of the writer process.
    #[must_use]
    pub const fn config_place(&self) -> usize {
        self.params.slot_count.saturating_add(CONFIG_PLACE_OFFSET)
    }

    /// Writes the header of a region that is created with this layout.
    pub fn write_header(&self, words: &[AtomicU64], start_id: u64) -> Result<(), RegionError> {
        let params = &self.params;

        let header = [
            (HEADER_MAGIC, REGION_MAGIC),
            (HEADER_VERSION, LAYOUT_VERSION),
            (HEADER_SLOT_COUNT, to_header_word(params.slot_count)),
            (HEADER_WAKE_CAPACITY, to_header_word(params.wake_capacity)),
            (HEADER_CELL_CAPACITY, to_header_word(params.cell_capacity)),
            (HEADER_QUEUE_COUNT, to_header_word(params.queue_count)),
            (HEADER_METRIC_COUNT, to_header_word(params.metric_count)),
            (HEADER_START_ID, start_id),
            (HEADER_SERIES_CAPACITY, to_header_word(params.series_capacity)),
            (HEADER_SERIES_KEY_BYTES, to_header_word(params.series_key_bytes)),
            (HEADER_DEDUP_CAPACITY, to_header_word(params.dedup_capacity)),
            (HEADER_BREAKER_CAPACITY, to_header_word(params.breaker_capacity)),
            (HEADER_LOCK_CAPACITY, to_header_word(params.lock_capacity)),
        ];

        for (index, value) in header {
            let word = words.get(index).ok_or(RegionError::OutOfBounds)?;
            word.store(value, Ordering::SeqCst);
        }

        Ok(())
    }

    /// Confirms that the header of a region describes this layout, which a worker checks before it uses the region.
    pub fn verify_header(&self, words: &[AtomicU64]) -> Result<(), RegionError> {
        let params = &self.params;

        let expected = [
            (HEADER_MAGIC, REGION_MAGIC, "magic"),
            (HEADER_VERSION, LAYOUT_VERSION, "layout version"),
            (HEADER_SLOT_COUNT, to_header_word(params.slot_count), "slot count"),
            (HEADER_WAKE_CAPACITY, to_header_word(params.wake_capacity), "wake capacity"),
            (HEADER_CELL_CAPACITY, to_header_word(params.cell_capacity), "cell capacity"),
            (HEADER_QUEUE_COUNT, to_header_word(params.queue_count), "queue count"),
            (HEADER_METRIC_COUNT, to_header_word(params.metric_count), "metric count"),
            (HEADER_SERIES_CAPACITY, to_header_word(params.series_capacity), "series capacity"),
            (HEADER_SERIES_KEY_BYTES, to_header_word(params.series_key_bytes), "series key bytes"),
            (HEADER_DEDUP_CAPACITY, to_header_word(params.dedup_capacity), "dedup capacity"),
            (HEADER_BREAKER_CAPACITY, to_header_word(params.breaker_capacity), "breaker capacity"),
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
