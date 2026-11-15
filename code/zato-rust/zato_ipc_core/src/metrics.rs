//! Metric counters kept per worker slot and summed across the slots on scrape.

use std::sync::atomic::Ordering;

use crate::error::RegionError;
use crate::layout::BLOCK_WORDS;
use crate::view::RegionView;

impl RegionView<'_> {

    /// Returns the offset of a metric counter in the row of a slot.
    fn metric_word(&self, slot: usize, metric: usize) -> Result<usize, RegionError> {
        self.check_slot(slot)?;

        let layout = self.layout();

        if metric >= layout.params.metric_count {
            return Err(RegionError::NoSuchMetric(metric));
        }

        // Each row starts at a block of its own, and its counters follow one another within the row.
        let row_blocks = slot.checked_mul(layout.metric_blocks_per_slot).ok_or(RegionError::OutOfBounds)?;
        let block = row_blocks.checked_add(metric / BLOCK_WORDS).ok_or(RegionError::OutOfBounds)?;

        Self::block_word(layout.metrics_start, block, metric % BLOCK_WORDS)
    }

    /// Adds `delta` to a metric counter of the worker in a slot.
    pub fn metric_add(&self, slot: usize, metric: usize, delta: u64) -> Result<(), RegionError> {
        let index = self.metric_word(slot, metric)?;

        // Only the worker of the slot writes its row, so the order relative to other words does not matter.
        self.word(index)?.fetch_add(delta, Ordering::Relaxed);
        Ok(())
    }

    /// Returns the sum of a metric counter over every slot.
    pub fn metric_sum(&self, metric: usize) -> Result<u64, RegionError> {
        let mut out: u64 = 0;

        for slot in 0..self.layout().params.slot_count {
            let index = self.metric_word(slot, metric)?;
            let value = self.word(index)?.load(Ordering::Relaxed);
            out = out.wrapping_add(value);
        }

        Ok(out)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::layout::RegionParams;
    use crate::view::test_support::{new_words, small_params};

    #[test]
    fn sum_covers_every_slot() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        view.metric_add(0, 1, 5)?;
        view.metric_add(3, 1, 7)?;
        view.metric_add(3, 2, 100)?;

        assert_eq!(view.metric_sum(1)?, 12);
        assert_eq!(view.metric_sum(2)?, 100);
        assert_eq!(view.metric_sum(0)?, 0);

        Ok(())
    }

    #[test]
    fn rows_of_two_slots_never_share_a_block() -> Result<(), RegionError> {
        let params = RegionParams {
            metric_count: 20,
            ..small_params()
        };
        let (words, layout) = new_words(params)?;
        let view = RegionView::new(words, layout)?;

        let last_of_first = view.metric_word(0, 19)?;
        let first_of_second = view.metric_word(1, 0)?;

        assert_eq!(first_of_second % BLOCK_WORDS, 0);
        assert!(first_of_second > last_of_first);
        assert_eq!(view.metric_add(0, 20, 1), Err(RegionError::NoSuchMetric(20)));

        Ok(())
    }
}
