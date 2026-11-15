//! Unit tests of the word layout of the shared region.

use proptest::prelude::*;

use super::*;

/// A run of whole blocks that one table entry, one row of a slot or one packed area occupies.
struct BlockRun {

    /// Offset of the first word of the run.
    start: usize,

    /// Number of blocks of the run.
    blocks: usize,

    /// Number of words the run holds, which its blocks must cover.
    used_words: usize,
}

/// Appends the runs of `count` items shaped as `first`, laid out one after another from the start of `first`.
fn push_items(runs: &mut Vec<BlockRun>, count: usize, first: &BlockRun) {
    for item in 0..count {
        let item_start = first.start + item * first.blocks * BLOCK_WORDS;

        runs.push(BlockRun {
            start: item_start,
            blocks: first.blocks,
            used_words: first.used_words,
        });
    }
}

/// Returns the shape of one item of a table.
const fn item(start: usize, blocks: usize, used_words: usize) -> BlockRun {
    BlockRun { start, blocks, used_words }
}

/// Returns the runs of a layout in the order of the region, every entry that a worker writes being a run of its own.
fn layout_runs(layout: &Layout) -> Vec<BlockRun> {
    let params = &layout.params;
    let mut out = Vec::new();

    // The descriptive header and the overflow counter of the wake table ..
    push_items(&mut out, 1, &item(0, HEADER_BLOCKS, HEADER_LOCK_CAPACITY + 1));

    // .. the block of each slot, each wake counter and each rate limiting cell ..
    push_items(&mut out, params.slot_count, &item(layout.slots_start, 1, 1));
    push_items(&mut out, params.wake_capacity, &item(layout.wake_start, 1, 1));
    push_items(&mut out, params.cell_capacity, &item(layout.cells_start, 1, 1));

    // .. the head block and the block of each place of every writer queue and of the queue of every keyed lock ..
    let queue_blocks = layout.queue_total * layout.blocks_per_queue;
    push_items(&mut out, queue_blocks, &item(layout.queues_start, 1, 1));

    // .. the metric row of each slot ..
    let metric_row = item(layout.metrics_start, layout.metric_blocks_per_slot, params.metric_count);
    push_items(&mut out, params.slot_count, &metric_row);

    // .. the packed series entries and records, and the series value row of each slot ..
    let series_entry_blocks = params.series_capacity.div_ceil(BLOCK_WORDS);
    let series_key_blocks = layout.series_key_words.div_ceil(BLOCK_WORDS);

    push_items(&mut out, 1, &item(layout.series_start, series_entry_blocks, params.series_capacity));
    push_items(&mut out, 1, &item(layout.series_keys_start, series_key_blocks, layout.series_key_words));
    let series_row = item(layout.series_values_start, layout.series_blocks_per_slot, params.series_capacity);
    push_items(&mut out, params.slot_count, &series_row);

    // .. the head block, the packed records and the packed index of the message control IDs ..
    let dedup_record_words = params.dedup_capacity * DEDUP_RECORD_WORDS;
    let dedup_record_blocks = dedup_record_words.div_ceil(BLOCK_WORDS);
    let dedup_index_blocks = layout.dedup_index_capacity.div_ceil(BLOCK_WORDS);

    push_items(&mut out, 1, &item(layout.dedup_start, DEDUP_HEAD_BLOCKS, 1));
    push_items(&mut out, 1, &item(layout.dedup_records_start, dedup_record_blocks, dedup_record_words));
    push_items(&mut out, 1, &item(layout.dedup_index_start, dedup_index_blocks, layout.dedup_index_capacity));

    // .. and the block of each circuit breaker and each keyed lock.
    push_items(&mut out, params.breaker_capacity, &item(layout.breakers_start, 1, 1));
    push_items(&mut out, params.lock_capacity, &item(layout.locks_start, 1, 1));

    out
}

proptest! {

    /// Every run starts at a block boundary and covers the words it holds, and the runs follow one another
    /// without a gap or an overlap up to the end of the region, so no two of them share a block.
    #[test]
    fn every_entry_occupies_whole_blocks_of_its_own(
        slot_count in 1_usize..64,
        wake_capacity in 0_usize..40,
        cell_capacity in 0_usize..40,
        queue_count in 0_usize..6,
        metric_count in 0_usize..40,
        series_capacity in 0_usize..40,
        series_key_bytes in 0_usize..4096,
        dedup_capacity in 0_usize..40,
        breaker_capacity in 0_usize..12,
        lock_capacity in 0_usize..12,
    ) {
        let params = RegionParams {
            slot_count,
            wake_capacity,
            cell_capacity,
            queue_count,
            metric_count,
            series_capacity,
            series_key_bytes,
            dedup_capacity,
            breaker_capacity,
            lock_capacity,
        };

        let layout = Layout::new(params).map_err(|error| TestCaseError::fail(error.to_string()))?;
        let mut next_start = 0;

        for run in layout_runs(&layout) {
            prop_assert_eq!(run.start, next_start);
            prop_assert_eq!(run.start % BLOCK_WORDS, 0);
            prop_assert!(run.used_words <= run.blocks * BLOCK_WORDS);

            next_start = run.start + run.blocks * BLOCK_WORDS;
        }

        prop_assert_eq!(next_start, layout.total_words);
    }
}
