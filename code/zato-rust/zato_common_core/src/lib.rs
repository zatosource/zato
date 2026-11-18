//! Core utilities shared across all Zato Rust crates.

/// Extraction of the words of audit log payloads that the free-text search indexes.
pub mod search_text;

/// Time-related helpers (UTC clock, datetime conversions).
pub mod time;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers all `#[pyfunction]`s exported by this crate.
#[pymodule]
fn zato_common_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(search_text::extract_search_text, module)?)?;
    module.add_function(wrap_pyfunction!(time::utc_now, module)?)?;
    Ok(())
}
