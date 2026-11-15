//! Errors of the shared memory region of the Zato server workers.

use std::fmt;

/// Why an operation on the shared memory region failed.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RegionError {

    /// The sizes of the region overflow the address space of the process.
    LayoutTooLarge,

    /// A word index computed from the layout lies outside of the region.
    OutOfBounds,

    /// A slot number is not below the slot count of the region.
    NoSuchSlot(usize),

    /// A queue number is not below the queue count of the region.
    NoSuchQueue(usize),

    /// A lock entry is not below the lock capacity of the region.
    NoSuchLock(usize),

    /// A metric number is not below the metric count of the region.
    NoSuchMetric(usize),

    /// Every entry of a fixed table is claimed by another key.
    TableFull,

    /// The key of a series record is not valid UTF-8.
    InvalidSeriesKey,

    /// A slot that has a ticket of a queue asked for another one.
    AlreadyQueued(usize),

    /// A slot released a queue whose turn it does not hold.
    NotHoldingTurn(usize),

    /// The header of the region does not describe the layout the caller expects.
    LayoutMismatch(&'static str),

    /// A system call on the memory file or on a wake-up descriptor failed.
    System(rustix::io::Errno),
}

impl fmt::Display for RegionError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::LayoutTooLarge => write!(formatter, "Shared region layout exceeds the address space"),
            Self::OutOfBounds => write!(formatter, "Shared region word index out of bounds"),
            Self::NoSuchSlot(slot) => write!(formatter, "No such worker slot: {slot}"),
            Self::NoSuchQueue(queue) => write!(formatter, "No such queue: {queue}"),
            Self::NoSuchLock(entry) => write!(formatter, "No such lock: {entry}"),
            Self::NoSuchMetric(metric) => write!(formatter, "No such metric: {metric}"),
            Self::TableFull => write!(formatter, "Shared region table is full"),
            Self::InvalidSeriesKey => write!(formatter, "Shared region series key is not valid UTF-8"),
            Self::AlreadyQueued(slot) => write!(formatter, "Slot {slot} already has a ticket of this queue"),
            Self::NotHoldingTurn(slot) => write!(formatter, "Slot {slot} does not hold the turn of this queue"),
            Self::LayoutMismatch(field) => write!(formatter, "Shared region header mismatch: {field}"),
            Self::System(errno) => write!(formatter, "Shared region system call failed: {errno}"),
        }
    }
}

impl std::error::Error for RegionError {}

impl From<rustix::io::Errno> for RegionError {
    fn from(errno: rustix::io::Errno) -> Self {
        Self::System(errno)
    }
}
