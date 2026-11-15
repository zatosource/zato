//! Worker slot table - the process, generation, heartbeat and state of each worker.

use std::sync::atomic::Ordering;

use crate::error::RegionError;
use crate::view::RegionView;

/// Position of the process ID within a slot block.
const SLOT_PID: usize = 0;

/// Position of the generation within a slot block.
const SLOT_GENERATION: usize = 1;

/// Position of the heartbeat timestamp within a slot block.
const SLOT_HEARTBEAT: usize = 2;

/// Position of the state within a slot block.
const SLOT_STATE: usize = 3;

/// State word of a slot whose worker was never started.
pub const STATE_EMPTY: u64 = 0;

/// State word of a slot whose worker loads its configuration.
pub const STATE_STARTING: u64 = 1;

/// State word of a slot whose worker serves requests.
pub const STATE_READY: u64 = 2;

/// State word of a slot whose worker completes its requests before it exits.
pub const STATE_DRAINING: u64 = 3;

/// State word of a slot whose worker has exited.
pub const STATE_STOPPED: u64 = 4;

/// Every state word a slot can hold.
const STATES: [u64; 5] = [STATE_EMPTY, STATE_STARTING, STATE_READY, STATE_DRAINING, STATE_STOPPED];

impl RegionView<'_> {

    /// Returns the offset of one field of a slot block.
    fn slot_word(&self, slot: usize, field: usize) -> Result<usize, RegionError> {
        self.check_slot(slot)?;
        Self::block_word(self.layout().slots_start, slot, field)
    }

    /// Records the process ID of the worker started in a slot.
    pub fn set_slot_pid(&self, slot: usize, pid: u64) -> Result<(), RegionError> {
        let index = self.slot_word(slot, SLOT_PID)?;
        self.word(index)?.store(pid, Ordering::SeqCst);
        Ok(())
    }

    /// Returns the process ID of the worker started in a slot.
    pub fn slot_pid(&self, slot: usize) -> Result<u64, RegionError> {
        let index = self.slot_word(slot, SLOT_PID)?;
        let out = self.word(index)?.load(Ordering::SeqCst);
        Ok(out)
    }

    /// Increments the generation of a slot before its replacement worker starts, and returns the new generation.
    pub fn next_slot_generation(&self, slot: usize) -> Result<u64, RegionError> {
        let index = self.slot_word(slot, SLOT_GENERATION)?;
        let previous = self.word(index)?.fetch_add(1, Ordering::SeqCst);
        let out = previous.wrapping_add(1);
        Ok(out)
    }

    /// Returns the generation of a slot, which a worker compares with the one it recorded at start to learn that it was replaced.
    pub fn slot_generation(&self, slot: usize) -> Result<u64, RegionError> {
        let index = self.slot_word(slot, SLOT_GENERATION)?;
        let out = self.word(index)?.load(Ordering::SeqCst);
        Ok(out)
    }

    /// Records the monotonic time, in microseconds, at which the worker of a slot was last alive.
    pub fn set_slot_heartbeat(&self, slot: usize, now_us: u64) -> Result<(), RegionError> {
        let index = self.slot_word(slot, SLOT_HEARTBEAT)?;
        self.word(index)?.store(now_us, Ordering::SeqCst);
        Ok(())
    }

    /// Returns the monotonic time, in microseconds, at which the worker of a slot was last alive.
    pub fn slot_heartbeat(&self, slot: usize) -> Result<u64, RegionError> {
        let index = self.slot_word(slot, SLOT_HEARTBEAT)?;
        let out = self.word(index)?.load(Ordering::SeqCst);
        Ok(out)
    }

    /// Records the state of the worker of a slot.
    pub fn set_slot_state(&self, slot: usize, state: u64) -> Result<(), RegionError> {
        if !STATES.contains(&state) {
            return Err(RegionError::LayoutMismatch("slot state"));
        }

        let index = self.slot_word(slot, SLOT_STATE)?;
        self.word(index)?.store(state, Ordering::SeqCst);
        Ok(())
    }

    /// Returns the state of the worker of a slot.
    pub fn slot_state(&self, slot: usize) -> Result<u64, RegionError> {
        let index = self.slot_word(slot, SLOT_STATE)?;
        let out = self.word(index)?.load(Ordering::SeqCst);
        Ok(out)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::view::test_support::{new_words, small_params};

    #[test]
    fn slot_fields_are_independent() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        view.set_slot_pid(1, 4321)?;
        view.set_slot_heartbeat(1, 999_999)?;
        view.set_slot_state(1, STATE_READY)?;

        assert_eq!(view.slot_pid(1)?, 4321);
        assert_eq!(view.slot_heartbeat(1)?, 999_999);
        assert_eq!(view.slot_state(1)?, STATE_READY);

        // The neighboring slots keep their own values.
        assert_eq!(view.slot_pid(0)?, 0);
        assert_eq!(view.slot_state(2)?, STATE_EMPTY);

        Ok(())
    }

    #[test]
    fn generation_increases_per_replacement() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        assert_eq!(view.next_slot_generation(3)?, 1);
        assert_eq!(view.next_slot_generation(3)?, 2);
        assert_eq!(view.slot_generation(3)?, 2);
        assert_eq!(view.slot_generation(0)?, 0);

        Ok(())
    }

    #[test]
    fn slot_beyond_count_is_refused() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        assert_eq!(view.slot_pid(4), Err(RegionError::NoSuchSlot(4)));
        assert_eq!(view.set_slot_state(0, 99), Err(RegionError::LayoutMismatch("slot state")));

        Ok(())
    }

    #[test]
    fn slot_blocks_do_not_share_a_cache_line() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        let first = view.slot_word(0, SLOT_PID)?;
        let second = view.slot_word(1, SLOT_PID)?;

        assert_eq!(second - first, crate::layout::BLOCK_WORDS);
        assert_eq!(first % crate::layout::BLOCK_WORDS, 0);

        Ok(())
    }
}
