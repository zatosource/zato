//! Python interface of the shared memory region.

use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyKeyError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::atomic::Ordering;

use crate::cells::{CellCheck, CellKey, FixedWindowParams, TokenBucketParams};
use crate::dedup::{DedupCheck, DedupKey, DedupOwner};
use crate::error::RegionError;
use crate::layout::RegionParams;
use crate::region::Region;
use crate::view::RegionView;
use crate::wake_fds::WakeFds;

create_exception!(
    zato_ipc_core,
    SharedRegionError,
    PyException,
    "An operation on the shared memory region of the workers failed."
);
create_exception!(
    zato_ipc_core,
    SharedRegionFull,
    SharedRegionError,
    "A table of the shared memory region has no entry left for a new key."
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

/// The outcome of one check of a rate limiting cell.
#[pyclass(get_all, frozen, skip_from_py_object, module = "zato_ipc_core")]
#[derive(Debug, Clone, Copy)]
pub struct CellCheckResult {

    /// Whether the request is allowed.
    pub is_allowed: bool,

    /// Whole tokens, or requests of the window, left after this check.
    pub remaining: u64,

    /// Microseconds until a request would be allowed, zero for an allowed request.
    pub retry_after_us: u64,
}

impl From<CellCheck> for CellCheckResult {
    fn from(check: CellCheck) -> Self {
        Self {
            is_allowed: check.is_allowed,
            remaining: check.remaining,
            retry_after_us: check.retry_after_us,
        }
    }
}

/// A rate limiting key with the group that a clear of counters resets it with, hashed once.
#[pyclass(frozen, skip_from_py_object, module = "zato_ipc_core")]
#[derive(Debug, Clone, Copy)]
pub struct RateLimitKey {

    /// The hashes of the key and of its group.
    hashes: CellKey,
}

#[pymethods]
impl RateLimitKey {

    /// Hashes a key and its group, for example `rest.orders:10.0.0.0/8:0` and `rest.orders:10.0.0.0/8:`.
    #[new]
    fn new(key: &str, group: &str) -> Self {
        Self {
            hashes: CellKey::new(key, group),
        }
    }
}

/// A message control ID within the channel that received it, hashed once.
#[pyclass(frozen, skip_from_py_object, module = "zato_ipc_core")]
#[derive(Debug, Clone, Copy)]
pub struct ControlIdKey {

    /// The hashes of the channel and the control ID.
    hashes: DedupKey,
}

#[pymethods]
impl ControlIdKey {

    /// Hashes a control ID within its channel, for example `hl7.orders` and `MSG-00001`.
    #[new]
    fn new(scope: &str, control_id: &str) -> Self {
        Self {
            hashes: DedupKey::new(scope, control_id),
        }
    }
}

/// The worker that holds the lock of the table of control IDs, as the slot table records it.
#[pyclass(frozen, skip_from_py_object, module = "zato_ipc_core")]
#[derive(Debug, Clone, Copy)]
pub struct LockOwner {

    /// The slot and the generation of the worker.
    owner: DedupOwner,
}

#[pymethods]
impl LockOwner {

    /// Names the worker started in a slot as the given generation.
    #[new]
    const fn new(slot: usize, generation: u64) -> Self {
        Self {
            owner: DedupOwner { slot, generation },
        }
    }
}

/// The shared memory region of the workers of one server, with the wake-up descriptor of each slot.
#[pyclass(frozen, module = "zato_ipc_core")]
#[derive(Debug)]
pub struct SharedRegion {

    /// The mapped region.
    region: Region,

    /// The wake-up descriptor of each slot.
    wake_fds: WakeFds,

    /// The wake-up descriptor of each slot in each writer queue, so that the waiters of two queues
    /// in one worker never take each other's wake-ups.
    queue_wake_fds: WakeFds,

    /// The wake-up descriptor of each slot for the keyed locks, which every waiter for a keyed lock in its worker shares.
    lock_wake_fds: WakeFds,
}

impl SharedRegion {

    /// Returns a view of the tables of the region.
    fn view(&self) -> PyResult<RegionView<'static>> {
        let out = self.region.view()?;
        Ok(out)
    }

    /// Returns the position of the wake-up descriptor of a slot in a writer queue.
    fn queue_wake_index(&self, queue: usize, slot: usize) -> PyResult<usize> {
        let layout = *self.view()?.layout();
        let place_count = layout.queue_place_count;

        if queue >= layout.params.queue_count {
            return Err(RegionError::NoSuchQueue(queue).into());
        }

        if slot >= place_count {
            return Err(RegionError::NoSuchSlot(slot).into());
        }

        let out = queue
            .checked_mul(place_count)
            .and_then(|start| start.checked_add(slot))
            .ok_or(RegionError::OutOfBounds)?;

        Ok(out)
    }

    /// Wakes the worker of a slot in a writer queue, if the queue named one whose turn it is.
    fn wake_turn(&self, queue: usize, turn: Option<usize>) -> PyResult<()> {
        if let Some(slot) = turn {
            let index = self.queue_wake_index(queue, slot)?;
            self.queue_wake_fds.wake(index)?;
        }

        Ok(())
    }

    /// Returns the queue of the lock of an entry, for a slot of a worker, which the place of the writer process is not.
    fn lock_slot_queue(&self, entry: usize, slot: usize) -> PyResult<usize> {
        let view = self.view()?;

        if slot >= view.layout().params.slot_count {
            return Err(RegionError::NoSuchSlot(slot).into());
        }

        let out = view.lock_queue(entry)?;
        Ok(out)
    }

    /// Wakes the worker of a slot for the keyed locks, if a lock queue named one whose turn it is.
    fn wake_lock_turn(&self, turn: Option<usize>) -> PyResult<()> {
        if let Some(slot) = turn {
            self.lock_wake_fds.wake(slot)?;
        }

        Ok(())
    }
}

#[pymethods]
impl SharedRegion {

    /// Creates the region of a server from a dictionary with the keys `slot_count`, `wake_capacity`,
    /// `cell_capacity`, `queue_count`, `metric_count`, `series_capacity`, `series_key_bytes`, `dedup_capacity`,
    /// `breaker_capacity`, `lock_capacity` and `start_id`.
    #[new]
    fn new(config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let params = RegionParams {
            slot_count: required(config, "slot_count")?,
            wake_capacity: required(config, "wake_capacity")?,
            cell_capacity: required(config, "cell_capacity")?,
            queue_count: required(config, "queue_count")?,
            metric_count: required(config, "metric_count")?,
            series_capacity: required(config, "series_capacity")?,
            series_key_bytes: required(config, "series_key_bytes")?,
            dedup_capacity: required(config, "dedup_capacity")?,
            breaker_capacity: required(config, "breaker_capacity")?,
            lock_capacity: required(config, "lock_capacity")?,
        };

        let start_id: u64 = required(config, "start_id")?;

        let region = Region::create(params, start_id)?;
        let wake_fds = WakeFds::create(params.slot_count)?;

        let place_count = region.view()?.layout().queue_place_count;
        let queue_wake_count = params.queue_count.checked_mul(place_count).ok_or(RegionError::LayoutTooLarge)?;
        let queue_wake_fds = WakeFds::create(queue_wake_count)?;
        let lock_wake_fds = WakeFds::create(params.slot_count)?;

        let out = Self {
            region,
            wake_fds,
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

    /// The number of worker slots of the region.
    #[getter]
    fn slot_count(&self) -> PyResult<usize> {
        let out = self.view()?.layout().params.slot_count;
        Ok(out)
    }

    /// The place of the `SQLite` writer process in every writer queue, which follows the places of the worker slots.
    #[getter]
    fn writer_place(&self) -> PyResult<usize> {
        let out = self.view()?.layout().writer_place();
        Ok(out)
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

    /// The start ID of the arbiter that created the region, which differs from that of every earlier arbiter.
    #[getter]
    fn start_id(&self) -> PyResult<u64> {
        let out = self.view()?.start_id()?;
        Ok(out)
    }

    /// Records the process ID of the worker started in a slot.
    fn set_slot_pid(&self, slot: usize, pid: u64) -> PyResult<()> {
        self.view()?.set_slot_pid(slot, pid)?;
        Ok(())
    }

    /// Returns the process ID of the worker started in a slot.
    fn slot_pid(&self, slot: usize) -> PyResult<u64> {
        let out = self.view()?.slot_pid(slot)?;
        Ok(out)
    }

    /// Increments the generation of a slot before its replacement worker starts, and returns the new generation.
    fn next_slot_generation(&self, slot: usize) -> PyResult<u64> {
        let out = self.view()?.next_slot_generation(slot)?;
        Ok(out)
    }

    /// Returns the generation of a slot.
    fn slot_generation(&self, slot: usize) -> PyResult<u64> {
        let out = self.view()?.slot_generation(slot)?;
        Ok(out)
    }

    /// Records the monotonic time, in microseconds, at which the worker of a slot was last alive.
    fn set_slot_heartbeat(&self, slot: usize, now_us: u64) -> PyResult<()> {
        self.view()?.set_slot_heartbeat(slot, now_us)?;
        Ok(())
    }

    /// Returns the monotonic time, in microseconds, at which the worker of a slot was last alive.
    fn slot_heartbeat(&self, slot: usize) -> PyResult<u64> {
        let out = self.view()?.slot_heartbeat(slot)?;
        Ok(out)
    }

    /// Records the state of the worker of a slot, one of the `STATE_*` constants of this module.
    fn set_slot_state(&self, slot: usize, state: u64) -> PyResult<()> {
        self.view()?.set_slot_state(slot, state)?;
        Ok(())
    }

    /// Returns the state of the worker of a slot, one of the `STATE_*` constants of this module.
    fn slot_state(&self, slot: usize) -> PyResult<u64> {
        let out = self.view()?.slot_state(slot)?;
        Ok(out)
    }

    /// Increments the wake counter of a subscription key after a committed publication.
    fn wake_increment(&self, sub_key: &str) -> PyResult<()> {
        self.view()?.wake_increment(sub_key)?;
        Ok(())
    }

    /// Returns the value a delivery loop compares with the one it saw last for its subscription key.
    fn wake_value(&self, sub_key: &str) -> PyResult<u64> {
        let out = self.view()?.wake_value(sub_key)?;
        Ok(out)
    }

    /// Takes one token from the bucket of a key.
    fn token_bucket_check(&self, key: &RateLimitKey, rate: u64, burst: u64, now_us: u64) -> PyResult<CellCheckResult> {
        let params = TokenBucketParams { rate, burst };
        let check = self.view()?.token_bucket_check(&key.hashes, params, now_us)?;

        let out = CellCheckResult::from(check);
        Ok(out)
    }

    /// Counts one request in the fixed window of a key.
    fn fixed_window_check(&self, key: &RateLimitKey, limit: u64, window_end_us: u64, now_us: u64) -> PyResult<CellCheckResult> {
        let params = FixedWindowParams { limit, window_end_us };
        let check = self.view()?.fixed_window_check(&key.hashes, params, now_us)?;

        let out = CellCheckResult::from(check);
        Ok(out)
    }

    /// Resets the token bucket and the fixed window of a key.
    fn cell_reset(&self, key: &str) -> PyResult<()> {
        self.view()?.cell_reset(key)?;
        Ok(())
    }

    /// Resets every cell of a group.
    fn cell_reset_group(&self, group: &str) -> PyResult<()> {
        self.view()?.cell_reset_group(group)?;
        Ok(())
    }

    /// Resets every cell of the table.
    fn cell_reset_all(&self) -> PyResult<()> {
        self.view()?.cell_reset_all()?;
        Ok(())
    }

    /// Adds `delta` to a metric counter of the worker in a slot.
    fn metric_add(&self, slot: usize, metric: usize, delta: u64) -> PyResult<()> {
        self.view()?.metric_add(slot, metric, delta)?;
        Ok(())
    }

    /// Returns the sum of a metric counter over every slot.
    fn metric_sum(&self, metric: usize) -> PyResult<u64> {
        let out = self.view()?.metric_sum(metric)?;
        Ok(out)
    }

    /// Returns the value cell of the series of a key, registering the series if no worker has registered it yet.
    fn series_register(&self, kind: u64, key: &str) -> PyResult<usize> {
        let out = self.view()?.series_register(kind, key)?;
        Ok(out)
    }

    /// Returns the key, the kind and the value cell of every registered series.
    fn series_list(&self) -> PyResult<Vec<(String, u64, usize)>> {
        let mut out = Vec::new();

        for record in self.view()?.series_list()? {
            out.push((record.key, record.kind, record.index));
        }

        Ok(out)
    }

    /// Adds `delta` to an integer value cell of a series in the row of a slot.
    fn series_add(&self, slot: usize, index: usize, delta: u64) -> PyResult<()> {
        self.view()?.series_add(slot, index, delta)?;
        Ok(())
    }

    /// Adds `delta` to a floating-point value cell of a series in the row of a slot.
    fn series_add_float(&self, slot: usize, index: usize, delta: f64) -> PyResult<()> {
        self.view()?.series_add_float(slot, index, delta)?;
        Ok(())
    }

    /// Sets a floating-point value cell of a series in the row of a slot.
    fn series_set_float(&self, slot: usize, index: usize, value: f64) -> PyResult<()> {
        self.view()?.series_set_float(slot, index, value)?;
        Ok(())
    }

    /// Checks whether a channel received a control ID within its window, recording it if it did not.
    ///
    /// Returns `None` while another worker that is alive holds the table, after which the caller checks again.
    fn dedup_check(&self, key: &ControlIdKey, owner: &LockOwner, ttl_us: u64, now_us: u64) -> PyResult<Option<bool>> {
        let out = match self.view()?.dedup_check(&key.hashes, owner.owner, ttl_us, now_us)? {
            DedupCheck::Busy => None,
            DedupCheck::Duplicate => Some(true),
            DedupCheck::New => Some(false),
        };
        Ok(out)
    }

    /// Returns the state of the circuit breaker of a connection and the time it was last opened.
    fn breaker_state(&self, key: &str) -> PyResult<(u64, u64)> {
        let state = self.view()?.breaker_state(key)?;
        Ok((state.state, state.opened_at_us))
    }

    /// Opens a closed circuit breaker, returning whether this call opened it.
    fn breaker_open(&self, key: &str, now_us: u64) -> PyResult<bool> {
        let out = self.view()?.breaker_open(key, now_us)?;
        Ok(out)
    }

    /// Moves an open circuit breaker whose reset period is over to half-open, returning whether the caller sends the trial message.
    fn breaker_begin_trial(&self, key: &str, now_us: u64, reset_us: u64) -> PyResult<bool> {
        let out = self.view()?.breaker_begin_trial(key, now_us, reset_us)?;
        Ok(out)
    }

    /// Concludes the trial message of a half-open circuit breaker, returning whether this call moved it.
    fn breaker_end_trial(&self, key: &str, is_success: bool, now_us: u64) -> PyResult<bool> {
        let out = self.view()?.breaker_end_trial(key, is_success, now_us)?;
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

    /// Adds a delta to the counter of a keyed lock and returns the new value.
    fn lock_counter_add(&self, entry: usize, delta: i64) -> PyResult<i64> {
        let out = self.view()?.lock_counter_add(entry, delta)?;
        Ok(out)
    }

    /// Sets the counter of a keyed lock if no worker has set or changed it yet, returning whether this call set it.
    fn lock_counter_init(&self, entry: usize, value: i64) -> PyResult<bool> {
        let out = self.view()?.lock_counter_init(entry, value)?;
        Ok(out)
    }

    /// Replaces the value of the counter of a keyed lock if it still holds the value that the caller read,
    /// returning whether this call replaced it.
    fn lock_counter_replace(&self, entry: usize, expected: i64, value: i64) -> PyResult<bool> {
        let out = self.view()?.lock_counter_replace(entry, expected, value)?;
        Ok(out)
    }

    /// Returns whether a flag of the server is set.
    fn flag_is_set(&self, flag: u64) -> PyResult<bool> {
        let out = self.view()?.flag_is_set(flag)?;
        Ok(out)
    }

    /// Inverts a flag of the server for every worker and returns whether it is set after the inversion.
    fn flag_invert(&self, flag: u64) -> PyResult<bool> {
        let out = self.view()?.flag_invert(flag)?;
        Ok(out)
    }

    /// Returns whether a slot holds a ticket of the queue of a keyed lock that the queue still serves.
    fn lock_has_place(&self, entry: usize, slot: usize) -> PyResult<bool> {
        let queue = self.lock_slot_queue(entry, slot)?;
        let out = self.view()?.queue_has_place(queue, slot)?;
        Ok(out)
    }

    /// Takes a ticket of the queue of a keyed lock for a slot.
    fn lock_enter(&self, entry: usize, slot: usize) -> PyResult<u64> {
        let queue = self.lock_slot_queue(entry, slot)?;
        let out = self.view()?.queue_enter(queue, slot)?;
        Ok(out)
    }

    /// Returns whether a slot holds a keyed lock, waking the slot whose turn it is when that is another one.
    fn lock_poll(&self, entry: usize, slot: usize) -> PyResult<bool> {
        let queue = self.lock_slot_queue(entry, slot)?;
        let (has_turn, other) = self.view()?.queue_poll(queue, slot)?;
        self.wake_lock_turn(other)?;

        Ok(has_turn)
    }

    /// Releases a keyed lock that a slot holds, waking the slot whose turn it is next.
    fn lock_release(&self, entry: usize, slot: usize) -> PyResult<()> {
        let queue = self.lock_slot_queue(entry, slot)?;
        let turn = self.view()?.queue_release(queue, slot)?;
        self.wake_lock_turn(turn)?;

        Ok(())
    }

    /// Withdraws the ticket of a slot from the queue of a keyed lock, waking the slot whose turn it is next.
    fn lock_abandon(&self, entry: usize, slot: usize) -> PyResult<()> {
        let queue = self.lock_slot_queue(entry, slot)?;
        let turn = self.view()?.queue_abandon(queue, slot)?;
        self.wake_lock_turn(turn)?;

        Ok(())
    }

    /// Returns the wake-up descriptor number of a slot for the keyed locks.
    fn lock_wake_fd(&self, slot: usize) -> PyResult<i32> {
        let out = self.lock_wake_fds.raw_fd(slot)?;
        Ok(out)
    }

    /// Reads and clears the wake-ups of a slot for the keyed locks, returning how many arrived since the previous read.
    fn lock_drain(&self, slot: usize) -> PyResult<u64> {
        let out = self.lock_wake_fds.drain(slot)?;
        Ok(out)
    }

    /// Returns the integer value cell of a series in the row of a slot.
    fn series_value(&self, slot: usize, index: usize) -> PyResult<u64> {
        // The value of one cell is read alone, with no other memory that it must be ordered against
        let out = self.view()?.series_value(slot, index)?.load(Ordering::Relaxed);
        Ok(out)
    }

    /// Returns the sum of an integer value cell of a series over every slot.
    fn series_sum(&self, index: usize) -> PyResult<u64> {
        let out = self.view()?.series_sum(index)?;
        Ok(out)
    }

    /// Returns the sum of a floating-point value cell of a series over every slot.
    fn series_sum_float(&self, index: usize) -> PyResult<f64> {
        let out = self.view()?.series_sum_float(index)?;
        Ok(out)
    }

    /// Returns the largest value of a floating-point value cell of a series over every slot.
    fn series_max_float(&self, index: usize) -> PyResult<f64> {
        let out = self.view()?.series_max_float(index)?;
        Ok(out)
    }

    /// Returns whether a slot holds a ticket of a writer queue that the queue still serves.
    fn queue_has_place(&self, queue: usize, slot: usize) -> PyResult<bool> {
        let out = self.view()?.queue_has_place(queue, slot)?;
        Ok(out)
    }

    /// Takes a ticket of the writer queue of a database file for a slot.
    fn queue_enter(&self, queue: usize, slot: usize) -> PyResult<u64> {
        let out = self.view()?.queue_enter(queue, slot)?;
        Ok(out)
    }

    /// Returns whether a slot holds the turn of a writer queue, waking the slot whose turn it is when that is another one.
    fn queue_poll(&self, queue: usize, slot: usize) -> PyResult<bool> {
        let (has_turn, other) = self.view()?.queue_poll(queue, slot)?;
        self.wake_turn(queue, other)?;

        Ok(has_turn)
    }

    /// Releases the turn of a writer queue that a slot holds, waking the slot whose turn it is next.
    fn queue_release(&self, queue: usize, slot: usize) -> PyResult<()> {
        let turn = self.view()?.queue_release(queue, slot)?;
        self.wake_turn(queue, turn)?;

        Ok(())
    }

    /// Withdraws the ticket of a slot from a writer queue, waking the slot whose turn it is next.
    fn queue_abandon(&self, queue: usize, slot: usize) -> PyResult<()> {
        let turn = self.view()?.queue_abandon(queue, slot)?;
        self.wake_turn(queue, turn)?;

        Ok(())
    }

    /// Returns the wake-up descriptor number of a slot in a writer queue, which the waiter of that queue polls.
    fn queue_wake_fd(&self, queue: usize, slot: usize) -> PyResult<i32> {
        let index = self.queue_wake_index(queue, slot)?;
        let out = self.queue_wake_fds.raw_fd(index)?;
        Ok(out)
    }

    /// Reads and clears the wake-ups of a slot in a writer queue, returning how many arrived since the previous read.
    fn queue_drain(&self, queue: usize, slot: usize) -> PyResult<u64> {
        let index = self.queue_wake_index(queue, slot)?;
        let out = self.queue_wake_fds.drain(index)?;
        Ok(out)
    }

    /// Returns the wake-up descriptor number of a slot, which its worker passes to the gevent hub.
    fn wake_fd(&self, slot: usize) -> PyResult<i32> {
        let out = self.wake_fds.raw_fd(slot)?;
        Ok(out)
    }

    /// Wakes the worker of a slot.
    fn wake_slot(&self, slot: usize) -> PyResult<()> {
        self.wake_fds.wake(slot)?;
        Ok(())
    }

    /// Reads and clears the wake-ups of a slot, returning how many arrived since the previous read.
    fn drain_slot(&self, slot: usize) -> PyResult<u64> {
        let out = self.wake_fds.drain(slot)?;
        Ok(out)
    }
}
