//! Core utilities shared across all Zato Rust crates.

/// Time-related helpers (UTC clock, datetime conversions).
pub mod time;

use pyo3::prelude::*;

/// PyO3 module initialiser - registers all `#[pyfunction]`s exported by this crate.
#[pymodule]
fn zato_common_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(time::utc_now, module)?)?;
    Ok(())
}
