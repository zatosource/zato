//! Core utilities shared across all Zato Rust crates.

/// Bulk insert of the events of the audit log into SQLite with the GIL released.
pub mod audit_insert;

/// Encoding of the pull responses and push bodies of pub/sub into JSON with the GIL released.
pub mod json;

/// Building of the messages that pulls of pub/sub hand out.
pub mod pulled_messages;

/// Extraction of the words of audit log payloads that the free-text search indexes.
pub mod search_text;

/// Time-related helpers (UTC clock, datetime conversions).
pub mod time;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers all `#[pyfunction]`s exported by this crate.
#[pymodule]
fn zato_common_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<audit_insert::SqliteAuditWriter>()?;
    module.add_class::<pulled_messages::PulledMessageBuilder>()?;
    module.add_function(wrap_pyfunction!(json::encode_pull_response, module)?)?;
    module.add_function(wrap_pyfunction!(json::encode_push_envelope, module)?)?;
    module.add_function(wrap_pyfunction!(search_text::extract_search_text, module)?)?;
    module.add_function(wrap_pyfunction!(time::utc_now, module)?)?;
    Ok(())
}
