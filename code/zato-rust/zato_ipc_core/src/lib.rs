//! Shared memory region of a Zato server.
//!
//! The arbiter of a Zato server creates one region before it forks the worker and the config process,
//! and both inherit it. The region holds the heartbeat of the worker, the first-in first-out queues
//! through which the two processes take turns writing to each `SQLite` database file, and the keyed locks
//! of outgoing connections with their counters. Every field is an atomic word, and each queue records
//! the ticket of each place, so the turn of a process terminated at any instruction is taken over.
//! Each place of each queue also has a wake-up descriptor that makes the gevent hub of its process return from waiting.

pub mod error;
pub mod heartbeat;
pub mod layout;
pub mod locks;
pub mod python;
pub mod queue;
pub mod region;
pub mod view;
pub mod wake_fds;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers the region class and its exceptions.
#[pymodule]
fn zato_ipc_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();

    module.add_class::<python::SharedRegion>()?;
    module.add("SharedRegionError", py.get_type::<python::SharedRegionError>())?;
    module.add("SharedRegionFull", py.get_type::<python::SharedRegionFull>())?;

    Ok(())
}
