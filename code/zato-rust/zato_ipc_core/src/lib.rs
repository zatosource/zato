//! Shared memory region of the workers of a Zato server.
//!
//! The arbiter of a Zato server creates one region before it forks its workers, and every worker
//! inherits it. The region holds the worker slot table, the wake counters of pub/sub subscription
//! keys, the rate limiting cells of REST channels and security definitions, the metric counters and
//! the labeled metric series of each slot, the first-in first-out queues of the `SQLite` writers,
//! the message control IDs of MLLP channels, the circuit breakers of outgoing connections, the keyed locks
//! of outgoing connections with their counters and the flags of the server. Every field is an atomic word, the lock word of the control IDs
//! names its holder, and the queue of each keyed lock records the ticket of each slot, so the lock of a worker
//! terminated at any instruction is taken over. Each slot also has a wake-up descriptor that makes the gevent hub
//! of its worker return from waiting.

pub mod breakers;
pub mod cells;
pub mod dedup;
pub mod error;
pub mod flags;
pub mod layout;
pub mod locks;
pub mod metrics;
pub mod python;
pub mod queue;
pub mod region;
pub mod series;
pub mod slots;
pub mod view;
pub mod wake;
pub mod wake_fds;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers the region class, its result class, its exceptions, the slot states,
/// the states of circuit breakers and the flags of the server.
#[pymodule]
fn zato_ipc_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();

    module.add_class::<python::SharedRegion>()?;
    module.add_class::<python::CellCheckResult>()?;
    module.add_class::<python::RateLimitKey>()?;
    module.add_class::<python::ControlIdKey>()?;
    module.add_class::<python::LockOwner>()?;
    module.add("SharedRegionError", py.get_type::<python::SharedRegionError>())?;
    module.add("SharedRegionFull", py.get_type::<python::SharedRegionFull>())?;

    module.add("STATE_EMPTY", slots::STATE_EMPTY)?;
    module.add("STATE_STARTING", slots::STATE_STARTING)?;
    module.add("STATE_READY", slots::STATE_READY)?;
    module.add("STATE_DRAINING", slots::STATE_DRAINING)?;
    module.add("STATE_STOPPED", slots::STATE_STOPPED)?;

    module.add("BREAKER_CLOSED", breakers::BREAKER_CLOSED)?;
    module.add("BREAKER_OPEN", breakers::BREAKER_OPEN)?;
    module.add("BREAKER_HALF_OPEN", breakers::BREAKER_HALF_OPEN)?;

    module.add("FLAG_LOG_STREAMING", flags::FLAG_LOG_STREAMING)?;

    Ok(())
}
