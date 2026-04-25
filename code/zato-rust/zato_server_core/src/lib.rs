//! Rust core of the Zato server.
//!
//! Exposes HTTP handling, logging and ID generation to Python via `PyO3`.

/// HTTP/1.x server built on raw `libc` sockets.
///
/// Uses gevent cooperative scheduling.
pub mod http;

/// Rotating file loggers for REST summary and access logs.
pub mod logging;

/// Utility functions shared across the crate.
pub mod utils;

use pyo3::prelude::*;

/// Generates a unique correlation ID.
///
/// Combines a UTC timestamp with a random hex suffix.
#[pyfunction]
fn next_id() -> String {
    utils::next_id()
}

/// `PyO3` module initializer.
///
/// Registers all classes and functions exported to Python.
#[pymodule]
fn zato_server_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<http::HTTPServer>()?;
    module.add_function(wrap_pyfunction!(next_id, module)?)?;
    module.add_function(wrap_pyfunction!(logging::init_rest_log, module)?)?;
    module.add_function(wrap_pyfunction!(logging::init_access_log, module)?)?;
    module.add_function(wrap_pyfunction!(logging::log_rest_summary, module)?)?;
    module.add_function(wrap_pyfunction!(logging::log_access, module)?)?;
    module.add_function(wrap_pyfunction!(http::extract_headers, module)?)?;
    module.add_function(wrap_pyfunction!(http::handle_http_request, module)?)?;
    Ok(())
}
