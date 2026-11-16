//! Python interface of the shared memory region.

use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyKeyError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::error::RegionError;
use crate::layout::{CONFIG_PLACE, PLACE_COUNT, RegionParams, WORKER_PLACE};
use crate::region::Region;
use crate::view::RegionView;
use crate::wake_fds::WakeFds;

create_exception!(
    zato_ipc_core,
    SharedRegionError,
    PyException,
    "An operation on the shared memory region of the server failed."
);
create_exception!(
    zato_ipc_core,
    SharedRegionFull,
    SharedRegionError,
    "The table of keyed locks of the shared memory region has no entry left for a new key."
);

impl From<RegionError> for PyErr {
    fn from(error: RegionError) -> Self {
        let message = error.to_string();

        match error {
            RegionError::TableFull => SharedRegionFull::new_err(message),
            _ => SharedRegionError::new_err(message),
        }
    }
}

/// Reads one required value from the dictionary of region parameters.
fn required<'py, Value>(config: &Bound<'py, PyDict>, key: &str) -> PyResult<Value>
where
    Value: for<'item> FromPyObject<'item, 'py, Error = PyErr>,
{
    let item = config.get_item(key)?.ok_or_else(|| PyKeyError::new_err(key.to_owned()))?;
    let out = item.extract::<Value>()?;
    Ok(out)
}

/// The shared memory region of the worker and the config process of one server, with the wake-up descriptors of their places.
#[pyclass(frozen, module = "zato_ipc_core")]
#[derive(Debug)]
pub struct SharedRegion {

    /// The mapped region.
    region: Region,

    /// The wake-up descriptor of each place in each writer queue, so that the waiters of two queues
    /// in one process never take each other's wake-ups.
    queue_wake_fds: WakeFds,

    /// The wake-up descriptor of each place of the queues of the keyed locks, which every waiter
    /// for a keyed lock in its process shares.
    lock_wake_fds: WakeFds,
}

impl SharedRegion {

    /// Returns a view of the tables of the region.
    fn view(&self) -> PyResult<RegionView<'static>> {
        let out = self.region.view()?;
        Ok(out)
    }

    /// Returns the position of the wake-up descriptor of a place in a writer queue.
    fn queue_wake_index(&self, queue: usize, place: usize) -> PyResult<usize> {
        let layout = *self.view()?.layout();

        if queue >= layout.params.queue_count {
            return Err(RegionError::NoSuchQueue(queue).into());
        }

        RegionView::check_queue_place(place)?;

        let out = queue
            .checked_mul(PLACE_COUNT)
            .and_then(|start| start.checked_add(place))
            .ok_or(RegionError::OutOfBounds)?;

        Ok(out)
    }

    /// Wakes the process of a place in a writer queue, if the queue named one whose turn it is.
    fn wake_turn(&self, queue: usize, turn: Option<usize>) -> PyResult<()> {
        if let Some(place) = turn {
            let index = self.queue_wake_index(queue, place)?;
            self.queue_wake_fds.wake(index)?;
        }

        Ok(())
    }

    /// Returns the queue of the lock of an entry, for the place of the worker or that of the config process.
    fn lock_place_queue(&self, entry: usize, place: usize) -> PyResult<usize> {
        RegionView::check_queue_place(place)?;

        let out = self.view()?.lock_queue(entry)?;
        Ok(out)
    }

    /// Wakes the process of a place for the keyed locks, if a lock queue named one whose turn it is.
    fn wake_lock_turn(&self, turn: Option<usize>) -> PyResult<()> {
        if let Some(place) = turn {
            self.lock_wake_fds.wake(place)?;
        }

        Ok(())
    }
}

#[pymethods]
impl SharedRegion {

    /// Creates the region of a server from a dictionary with the keys `queue_count` and `lock_capacity`.
    #[new]
    fn new(config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let params = RegionParams {
            queue_count: required(config, "queue_count")?,
            lock_capacity: required(config, "lock_capacity")?,
        };

        let region = Region::create(params)?;

        let queue_wake_count = params.queue_count.checked_mul(PLACE_COUNT).ok_or(RegionError::LayoutTooLarge)?;
        let queue_wake_fds = WakeFds::create(queue_wake_count)?;
        let lock_wake_fds = WakeFds::create(PLACE_COUNT)?;

        let out = Self {
            region,
            queue_wake_fds,
            lock_wake_fds,
        };
        Ok(out)
    }

    /// Confirms that the header of the region describes the layout this build of the crate uses.
    fn verify(&self) -> PyResult<()> {
        self.region.verify()?;
        Ok(())
    }

    /// The place of the worker in every writer queue and in the queue of every keyed lock.
    #[getter]
    #[expect(clippy::unused_self, reason = "PyO3 method signature requires &self")]
    const fn worker_place(&self) -> usize {
        WORKER_PLACE
    }

    /// The place of the config process in every writer queue and in the queue of every keyed lock.
    #[getter]
    #[expect(clippy::unused_self, reason = "PyO3 method signature requires &self")]
    const fn config_place(&self) -> usize {
        CONFIG_PLACE
    }

    /// The number of writer queues of the region.
    #[getter]
    fn queue_count(&self) -> PyResult<usize> {
        let out = self.view()?.layout().params.queue_count;
        Ok(out)
    }

    /// The number of entries of the table of keyed locks of the region.
    #[getter]
    fn lock_capacity(&self) -> PyResult<usize> {
        let out = self.view()?.layout().params.lock_capacity;
        Ok(out)
    }

    /// Records the monotonic time, in microseconds, at which the worker was last alive.
    fn set_heartbeat(&self, now_us: u64) -> PyResult<()> {
        self.view()?.set_heartbeat(now_us)?;
        Ok(())
    }

    /// Returns the monotonic time, in microseconds, at which the worker was last alive.
    fn heartbeat(&self) -> PyResult<u64> {
        let out = self.view()?.heartbeat()?;
        Ok(out)
    }

    /// Returns the entry of the keyed lock of a key, claiming a free entry for a key that has none.
    fn lock_entry(&self, key: &str) -> PyResult<usize> {
        let out = self.view()?.lock_entry(key)?;
        Ok(out)
    }

    /// Returns the value of the counter of a keyed lock.
    fn lock_counter(&self, entry: usize) -> PyResult<i64> {
        let out = self.view()?.lock_counter(entry)?;
        Ok(out)
    }

    /// Replaces the value of the counter of a keyed lock if it still holds the value that the caller read,
    /// returning whether this call replaced it.
    fn lock_counter_replace(&self, entry: usize, expected: i64, value: i64) -> PyResult<bool> {
        let out = self.view()?.lock_counter_replace(entry, expected, value)?;
        Ok(out)
    }

    /// Returns whether a place holds a ticket of the queue of a keyed lock that the queue still serves.
    fn lock_has_place(&self, entry: usize, place: usize) -> PyResult<bool> {
        let queue = self.lock_place_queue(entry, place)?;
        let out = self.view()?.queue_has_place(queue, place)?;
        Ok(out)
    }

    /// Takes a ticket of the queue of a keyed lock for a place.
    fn lock_enter(&self, entry: usize, place: usize) -> PyResult<u64> {
        let queue = self.lock_place_queue(entry, place)?;
        let out = self.view()?.queue_enter(queue, place)?;
        Ok(out)
    }

    /// Returns whether a place holds a keyed lock, waking the other place when the turn is its own.
    fn lock_poll(&self, entry: usize, place: usize) -> PyResult<bool> {
        let queue = self.lock_place_queue(entry, place)?;
        let (has_turn, other) = self.view()?.queue_poll(queue, place)?;
        self.wake_lock_turn(other)?;

        Ok(has_turn)
    }

    /// Releases a keyed lock that a place holds, waking the place whose turn it is next.
    fn lock_release(&self, entry: usize, place: usize) -> PyResult<()> {
        let queue = self.lock_place_queue(entry, place)?;
        let turn = self.view()?.queue_release(queue, place)?;
        self.wake_lock_turn(turn)?;

        Ok(())
    }

    /// Withdraws the ticket of a place from the queue of a keyed lock, waking the place whose turn it is next.
    fn lock_abandon(&self, entry: usize, place: usize) -> PyResult<()> {
        let queue = self.lock_place_queue(entry, place)?;
        let turn = self.view()?.queue_abandon(queue, place)?;
        self.wake_lock_turn(turn)?;

        Ok(())
    }

    /// Returns the wake-up descriptor number of a place for the keyed locks.
    fn lock_wake_fd(&self, place: usize) -> PyResult<i32> {
        RegionView::check_queue_place(place)?;

        let out = self.lock_wake_fds.raw_fd(place)?;
        Ok(out)
    }

    /// Reads and clears the wake-ups of a place for the keyed locks, returning how many arrived since the previous read.
    fn lock_drain(&self, place: usize) -> PyResult<u64> {
        RegionView::check_queue_place(place)?;

        let out = self.lock_wake_fds.drain(place)?;
        Ok(out)
    }

    /// Returns whether a place holds a ticket of a writer queue that the queue still serves.
    fn queue_has_place(&self, queue: usize, place: usize) -> PyResult<bool> {
        let out = self.view()?.queue_has_place(queue, place)?;
        Ok(out)
    }

    /// Takes a ticket of the writer queue of a database file for a place.
    fn queue_enter(&self, queue: usize, place: usize) -> PyResult<u64> {
        let out = self.view()?.queue_enter(queue, place)?;
        Ok(out)
    }

    /// Returns whether a place holds the turn of a writer queue, waking the other place when the turn is its own.
    fn queue_poll(&self, queue: usize, place: usize) -> PyResult<bool> {
        let (has_turn, other) = self.view()?.queue_poll(queue, place)?;
        self.wake_turn(queue, other)?;

        Ok(has_turn)
    }

    /// Releases the turn of a writer queue that a place holds, waking the place whose turn it is next.
    fn queue_release(&self, queue: usize, place: usize) -> PyResult<()> {
        let turn = self.view()?.queue_release(queue, place)?;
        self.wake_turn(queue, turn)?;

        Ok(())
    }

    /// Withdraws the ticket of a place from a writer queue, waking the place whose turn it is next.
    fn queue_abandon(&self, queue: usize, place: usize) -> PyResult<()> {
        let turn = self.view()?.queue_abandon(queue, place)?;
        self.wake_turn(queue, turn)?;

        Ok(())
    }

    /// Returns the wake-up descriptor number of a place in a writer queue, which the waiter of that queue polls.
    fn queue_wake_fd(&self, queue: usize, place: usize) -> PyResult<i32> {
        let index = self.queue_wake_index(queue, place)?;
        let out = self.queue_wake_fds.raw_fd(index)?;
        Ok(out)
    }

    /// Reads and clears the wake-ups of a place in a writer queue, returning how many arrived since the previous read.
    fn queue_drain(&self, queue: usize, place: usize) -> PyResult<u64> {
        let index = self.queue_wake_index(queue, place)?;
        let out = self.queue_wake_fds.drain(index)?;
        Ok(out)
    }
}
