//! First-in first-out queues of the `SQLite` writers of the worker and the config process.
//!
//! There is one queue per database file, followed by the queue of each keyed lock,
//! which the two processes take turns through in the same way.
//!
//! A place takes a ticket and writes when the queue serves its ticket. A place never holds
//! more than one ticket of one queue, so a process orders its own greenlets before it enters.
//!
//! Each place records its ticket in a block of its own. Before it takes a ticket, the place marks
//! the block as entering, so that a ticket which no block records, while no live place is entering,
//! belongs to a process that terminated, and the queue passes over it. The arbiter marks the block
//! of a terminated process, and a waiter whose deadline passed marks its own block, as abandoned.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;
use crate::layout::PLACE_COUNT;
use crate::view::RegionView;

/// Position, within the head block of a queue, of the next ticket to hand out.
const HEAD_NEXT_TICKET: usize = 0;

/// Position, within the head block of a queue, of the ticket being served.
const HEAD_NOW_SERVING: usize = 1;

/// Position of the ticket record within the block of a place.
const PLACE_RECORD: usize = 0;

/// Record of a place that holds no ticket.
const RECORD_NONE: u64 = 0;

/// Record of a live place between the start of its entry and the recording of its ticket.
const RECORD_ENTERING: u64 = u64::MAX;

/// Record of a place whose process terminated while it was entering.
const RECORD_DEAD_ENTERING: u64 = u64::MAX - 1;

/// Marks a ticket record whose place no longer waits for its turn.
const ABANDONED_FLAG: u64 = 1 << 62;

/// What the record of a place says about one ticket.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Record {

    /// The place holds no ticket, or its process terminated while it was entering.
    Nothing,

    /// The place is between the start of its entry and the recording of its ticket.
    Entering,

    /// The place waits for, or holds the turn of, this ticket.
    Waiting(u64),

    /// The place no longer waits for this ticket.
    Abandoned(u64),
}

/// Reads a ticket record.
const fn parse_record(word: u64) -> Record {
    match word {
        RECORD_NONE | RECORD_DEAD_ENTERING => Record::Nothing,
        RECORD_ENTERING => Record::Entering,
        _ if word & ABANDONED_FLAG == 0 => Record::Waiting(word - 1),
        _ => Record::Abandoned((word & !ABANDONED_FLAG) - 1),
    }
}

/// Returns the record of a place that waits for a ticket.
const fn waiting_record(ticket: u64) -> u64 {
    ticket + 1
}

impl RegionView<'_> {

    /// Returns the head words of a queue - the next ticket and the ticket being served.
    fn queue_head(&self, queue: usize) -> Result<(&AtomicU64, &AtomicU64), RegionError> {
        let layout = self.layout();

        if queue >= layout.queue_total {
            return Err(RegionError::NoSuchQueue(queue));
        }

        let head_block = queue.checked_mul(layout.blocks_per_queue).ok_or(RegionError::OutOfBounds)?;
        let next = self.word(Self::block_word(layout.queues_start, head_block, HEAD_NEXT_TICKET)?)?;
        let serving = self.word(Self::block_word(layout.queues_start, head_block, HEAD_NOW_SERVING)?)?;

        Ok((next, serving))
    }

    /// Returns the record word of a place in a queue.
    fn queue_record(&self, queue: usize, place: usize) -> Result<&AtomicU64, RegionError> {
        Self::check_queue_place(place)?;

        let layout = self.layout();
        let head_block = queue.checked_mul(layout.blocks_per_queue).ok_or(RegionError::OutOfBounds)?;

        // The block of a place follows the head block of its queue.
        let place_block = head_block
            .checked_add(place)
            .and_then(|block| block.checked_add(1))
            .ok_or(RegionError::OutOfBounds)?;

        self.word(Self::block_word(layout.queues_start, place_block, PLACE_RECORD)?)
    }

    /// Returns whether a place holds a ticket of a queue that the queue still serves.
    pub fn queue_has_place(&self, queue: usize, place: usize) -> Result<bool, RegionError> {
        let record = self.queue_record(queue, place)?;
        let out = matches!(parse_record(record.load(Ordering::SeqCst)), Record::Waiting(_));
        Ok(out)
    }

    /// Takes a ticket of a queue for a place and returns it. The place then polls the queue until it has the turn.
    pub fn queue_enter(&self, queue: usize, place: usize) -> Result<u64, RegionError> {
        let (next, _) = self.queue_head(queue)?;
        let record = self.queue_record(queue, place)?;

        // A previous process of this place may have left a record that the queue passes over, which a new entry replaces.
        if let Record::Waiting(_) | Record::Entering = parse_record(record.load(Ordering::SeqCst)) {
            return Err(RegionError::AlreadyQueued(place));
        }

        // The mark comes first, so a process that terminates after it took its ticket is known to have been entering.
        record.store(RECORD_ENTERING, Ordering::SeqCst);

        let ticket = next.fetch_add(1, Ordering::SeqCst);
        record.store(waiting_record(ticket), Ordering::SeqCst);

        Ok(ticket)
    }

    /// Moves the queue past the tickets of places that no longer wait, and returns the place whose turn it is, if one records it.
    pub fn queue_advance(&self, queue: usize) -> Result<Option<usize>, RegionError> {
        let (next, serving) = self.queue_head(queue)?;

        loop {
            let current = serving.load(Ordering::SeqCst);

            // The next ticket is read before the records, so a place that starts entering later takes a ticket above `current`.
            if current >= next.load(Ordering::SeqCst) {
                return Ok(None);
            }

            let mut is_any_entering = false;

            for place in 0..PLACE_COUNT {
                match parse_record(self.queue_record(queue, place)?.load(Ordering::SeqCst)) {
                    // Every ticket is recorded by one place at most, so its record settles whose turn it is.
                    Record::Waiting(ticket) if ticket == current => return Ok(Some(place)),

                    Record::Entering => is_any_entering = true,
                    Record::Waiting(_) | Record::Abandoned(_) | Record::Nothing => {}
                }
            }

            // A place that is entering may have taken the ticket being served without having recorded it yet,
            // and it polls the queue itself once it has recorded it.
            if is_any_entering {
                return Ok(None);
            }

            // No live place waits for the ticket being served, which therefore belongs to a place that abandoned it
            // or to a process that terminated while entering, so the queue moves past it. A failed exchange means
            // that the other place moved the queue at the same moment, and the records are read again either way.
            let _ = serving.compare_exchange(current, current + 1, Ordering::SeqCst, Ordering::SeqCst);
        }
    }

    /// Returns whether a place holds the turn of a queue, after moving the queue past the tickets of places that no longer wait.
    pub fn queue_poll(&self, queue: usize, place: usize) -> Result<(bool, Option<usize>), RegionError> {
        let turn = self.queue_advance(queue)?;
        let has_turn = turn == Some(place);

        // The place whose turn it is, when it is the other one, is returned so that the caller wakes it.
        let other = turn.filter(|turn_place| *turn_place != place);

        Ok((has_turn, other))
    }

    /// Releases the turn that a place holds, and returns the place whose turn it is next, if one records it.
    pub fn queue_release(&self, queue: usize, place: usize) -> Result<Option<usize>, RegionError> {
        let (_, serving) = self.queue_head(queue)?;
        let record = self.queue_record(queue, place)?;

        let Record::Waiting(ticket) = parse_record(record.load(Ordering::SeqCst)) else {
            return Err(RegionError::NotHoldingTurn(place));
        };

        // The queue moves on first, so that a place that polls meanwhile never sees the ticket being served without its record.
        if serving
            .compare_exchange(ticket, ticket + 1, Ordering::SeqCst, Ordering::SeqCst)
            .is_err()
        {
            return Err(RegionError::NotHoldingTurn(place));
        }

        record.store(RECORD_NONE, Ordering::SeqCst);

        self.queue_advance(queue)
    }

    /// Withdraws the ticket of a place, which a waiter does when its deadline passes and the arbiter does
    /// for a process that terminated, and returns the place whose turn it is next, if one records it.
    pub fn queue_abandon(&self, queue: usize, place: usize) -> Result<Option<usize>, RegionError> {
        let record = self.queue_record(queue, place)?;

        match parse_record(record.load(Ordering::SeqCst)) {
            Record::Waiting(ticket) => record.store(waiting_record(ticket) | ABANDONED_FLAG, Ordering::SeqCst),

            // Only the arbiter abandons a place that is entering, after its process terminated.
            Record::Entering => record.store(RECORD_DEAD_ENTERING, Ordering::SeqCst),

            Record::Nothing | Record::Abandoned(_) => {}
        }

        self.queue_advance(queue)
    }
}

#[cfg(test)]
#[path = "queue_tests.rs"]
mod tests;
