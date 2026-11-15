//! Flags of the server, each of which is one bit of a word of the header that any worker inverts for all of them.
//!
//! A worker reads a flag when it starts and whenever another worker announces a change, so the state of
//! the flag, not the order of the announcements, decides what each worker applies.

use std::sync::atomic::Ordering;

use crate::error::RegionError;
use crate::layout::SERVER_FLAGS_WORD;
use crate::view::RegionView;

/// Flag that is set while the log records of the server are streamed.
pub const FLAG_LOG_STREAMING: u64 = 1;

impl RegionView<'_> {
    /// Returns whether a flag of the server is set.
    pub fn flag_is_set(&self, flag: u64) -> Result<bool, RegionError> {
        let flags = self.word(SERVER_FLAGS_WORD)?.load(Ordering::SeqCst);
        Ok(flags & flag != 0)
    }

    /// Inverts a flag of the server and returns whether it is set after the inversion.
    pub fn flag_invert(&self, flag: u64) -> Result<bool, RegionError> {
        // The inversion is one atomic step, so two workers that invert a flag at once leave it as it was
        let previous = self.word(SERVER_FLAGS_WORD)?.fetch_xor(flag, Ordering::SeqCst);
        Ok(previous & flag == 0)
    }
}

#[cfg(test)]
#[path = "flags_tests.rs"]
mod tests;
