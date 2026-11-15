//! Wake-up descriptors of the workers, one `eventfd` per slot.
//!
//! A write to the descriptor of a slot makes it readable in the gevent hub of that slot's worker,
//! and writes that arrive before the worker reads coalesce into one readiness event.

use std::os::fd::{AsRawFd, OwnedFd, RawFd};

use rustix::event::{EventfdFlags, eventfd};
use rustix::io::{Errno, read, write};

use crate::error::RegionError;

/// Value written to a descriptor to wake its worker.
const WAKE_INCREMENT: u64 = 1;

/// Initial counter of every descriptor.
const INITIAL_COUNT: u32 = 0;

/// The wake-up descriptors of every slot, created by the arbiter before it forks the workers.
#[derive(Debug)]
pub struct WakeFds {

    /// One descriptor per slot, in slot order.
    descriptors: Vec<OwnedFd>,
}

impl WakeFds {

    /// Creates one descriptor per slot.
    pub fn create(slot_count: usize) -> Result<Self, RegionError> {
        let mut descriptors = Vec::with_capacity(slot_count);

        for _ in 0..slot_count {

            // A worker reads its descriptor from the gevent hub, which never blocks on a read.
            let descriptor = eventfd(INITIAL_COUNT, EventfdFlags::NONBLOCK | EventfdFlags::CLOEXEC)?;
            descriptors.push(descriptor);
        }

        let out = Self { descriptors };
        Ok(out)
    }

    /// Returns the descriptor of a slot.
    fn descriptor(&self, slot: usize) -> Result<&OwnedFd, RegionError> {
        self.descriptors.get(slot).ok_or(RegionError::NoSuchSlot(slot))
    }

    /// Returns the descriptor number of a slot, which its worker passes to the gevent hub.
    pub fn raw_fd(&self, slot: usize) -> Result<RawFd, RegionError> {
        let out = self.descriptor(slot)?.as_raw_fd();
        Ok(out)
    }

    /// Wakes the worker of a slot.
    pub fn wake(&self, slot: usize) -> Result<(), RegionError> {
        let bytes = WAKE_INCREMENT.to_ne_bytes();

        match write(self.descriptor(slot)?, &bytes) {

            // A counter at its maximum already wakes the worker, so a refused increment changes nothing.
            Ok(_) | Err(Errno::AGAIN) => Ok(()),

            Err(errno) => Err(RegionError::System(errno)),
        }
    }

    /// Reads and clears the wake-ups of a slot, returning how many arrived since the previous read.
    pub fn drain(&self, slot: usize) -> Result<u64, RegionError> {
        let mut bytes = [0_u8; 8];

        match read(self.descriptor(slot)?, &mut bytes) {
            Ok(_) => Ok(u64::from_ne_bytes(bytes)),

            // Nothing arrived since the previous read.
            Err(Errno::AGAIN) => Ok(0),

            Err(errno) => Err(RegionError::System(errno)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wake_ups_coalesce_until_drained() -> Result<(), RegionError> {
        let fds = WakeFds::create(2)?;

        fds.wake(1)?;
        fds.wake(1)?;

        assert_eq!(fds.drain(0)?, 0);
        assert_eq!(fds.drain(1)?, 2);
        assert_eq!(fds.drain(1)?, 0);
        assert_eq!(fds.wake(2), Err(RegionError::NoSuchSlot(2)));

        Ok(())
    }
}
