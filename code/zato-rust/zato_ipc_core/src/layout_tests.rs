//! Unit tests of the word layout of the shared region.

use proptest::prelude::*;

use super::*;

/// A run of whole blocks that one table entry or the header occupies.
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

/// Returns the runs of a layout in the order of the region, every entry that a process writes being a run of its own.
fn layout_runs(layout: &Layout) -> Vec<BlockRun> {
    let params = &layout.params;
    let mut out = Vec::new();

    // The header and the heartbeat of the worker ..
    push_items(&mut out, 1, &item(0, HEADER_BLOCKS, HEADER_LOCK_CAPACITY + 1));
    push_items(&mut out, 1, &item(layout.heartbeat_start, HEARTBEAT_BLOCKS, 1));

    // .. the head block and the block of each place of the queue of every keyed lock ..
    let queue_blocks = layout.queue_total * layout.blocks_per_queue;
    push_items(&mut out, queue_blocks, &item(layout.queues_start, 1, 1));

    // .. and the block of each keyed lock.
    push_items(&mut out, params.lock_capacity, &item(layout.locks_start, 1, 1));

    out
}

proptest! {

    /// Every run starts at a block boundary and covers the words it holds, and the runs follow one another
    /// without a gap or an overlap up to the end of the region, so no two of them share a block.
    #[test]
    fn every_entry_occupies_whole_blocks_of_its_own(lock_capacity in 0_usize..12) {
        let params = RegionParams { lock_capacity };

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
