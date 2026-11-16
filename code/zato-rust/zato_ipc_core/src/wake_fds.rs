//! Wake-up descriptors of the places of the queues, one `eventfd` per place.
//!
//! A write to the descriptor of a place makes it readable in the gevent hub of the process that holds the place,
//! and writes that arrive before the process reads coalesce into one readiness event.

use std::os::fd::{AsRawFd, OwnedFd, RawFd};

use rustix::event::{EventfdFlags, eventfd};
use rustix::io::{Errno, read, write};

use crate::error::RegionError;

/// Value written to a descriptor to wake its process.
const WAKE_INCREMENT: u64 = 1;

/// Initial counter of every descriptor.
const INITIAL_COUNT: u32 = 0;

/// The wake-up descriptors of the places of the queues, created by the arbiter before it forks its processes.
#[derive(Debug)]
pub struct WakeFds {

    /// One descriptor per place, in the order of the places.
    descriptors: Vec<OwnedFd>,
}

impl WakeFds {

    /// Creates the given number of descriptors.
    pub fn create(count: usize) -> Result<Self, RegionError> {
        let mut descriptors = Vec::with_capacity(count);

        for _ in 0..count {

            // A process reads its descriptor from the gevent hub, which never blocks on a read.
            let descriptor = eventfd(INITIAL_COUNT, EventfdFlags::NONBLOCK | EventfdFlags::CLOEXEC)?;
            descriptors.push(descriptor);
        }

        let out = Self { descriptors };
        Ok(out)
    }

    /// Returns the descriptor at a position.
    fn descriptor(&self, index: usize) -> Result<&OwnedFd, RegionError> {
        self.descriptors.get(index).ok_or(RegionError::OutOfBounds)
    }

    /// Returns the descriptor number at a position, which its process passes to the gevent hub.
    pub fn raw_fd(&self, index: usize) -> Result<RawFd, RegionError> {
        let out = self.descriptor(index)?.as_raw_fd();
        Ok(out)
    }

    /// Wakes the process that waits on the descriptor at a position.
    pub fn wake(&self, index: usize) -> Result<(), RegionError> {
        let bytes = WAKE_INCREMENT.to_ne_bytes();

        match write(self.descriptor(index)?, &bytes) {

            // A counter at its maximum already wakes the process, so a refused increment changes nothing.
            Ok(_) | Err(Errno::AGAIN) => Ok(()),

            Err(errno) => Err(RegionError::System(errno)),
        }
    }

    /// Reads and clears the wake-ups of the descriptor at a position, returning how many arrived since the previous read.
    pub fn drain(&self, index: usize) -> Result<u64, RegionError> {
        let mut bytes = [0_u8; 8];

        match read(self.descriptor(index)?, &mut bytes) {
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
        assert_eq!(fds.wake(2), Err(RegionError::OutOfBounds));

        Ok(())
    }
}
