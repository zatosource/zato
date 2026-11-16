//! Heartbeat of the worker - the monotonic time at which the worker was last alive, which the arbiter checks.

use std::sync::atomic::Ordering;

use crate::error::RegionError;
use crate::view::RegionView;

/// Position of the heartbeat timestamp within the heartbeat block.
const HEARTBEAT_TIME: usize = 0;

impl RegionView<'_> {

    /// Records the monotonic time, in microseconds, at which the worker was last alive.
    pub fn set_heartbeat(&self, now_us: u64) -> Result<(), RegionError> {
        let index = Self::block_word(self.layout().heartbeat_start, 0, HEARTBEAT_TIME)?;
        self.word(index)?.store(now_us, Ordering::SeqCst);
        Ok(())
    }

    /// Returns the monotonic time, in microseconds, at which the worker was last alive.
    pub fn heartbeat(&self) -> Result<u64, RegionError> {
        let index = Self::block_word(self.layout().heartbeat_start, 0, HEARTBEAT_TIME)?;
        let out = self.word(index)?.load(Ordering::SeqCst);
        Ok(out)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::view::test_support::{new_words, small_params};

    #[test]
    fn heartbeat_holds_the_last_time_recorded() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        assert_eq!(view.heartbeat()?, 0);

        view.set_heartbeat(999_999)?;
        assert_eq!(view.heartbeat()?, 999_999);

        Ok(())
    }
}
