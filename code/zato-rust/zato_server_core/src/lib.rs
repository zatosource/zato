//! Rust core of the Zato server - exposes HTTP handling, logging and ID generation to Python via `PyO3`.

/// Data model for enmasse YAML configuration (channels, security, outgoing connections, etc.).
pub mod model;

/// HTTP/1.x server built on raw `libc` sockets with gevent cooperative scheduling.
pub mod http;

/// Rotating file loggers for REST summary and access logs.
pub mod logging;

use pyo3::prelude::*;

/// Generates a unique correlation ID by combining a UTC timestamp with a random hex suffix.
#[pyfunction]
fn next_id() -> String {
    model::next_id()
}

/// `PyO3` module initializer - registers all classes and functions exported to Python.
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
