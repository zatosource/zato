pub mod model;
pub mod http;
pub mod logging;
use pyo3::prelude::*;

#[pyfunction]
fn next_id() -> String {
    model::next_id()
}

#[pymodule]
fn zato_server_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<http::HTTPServer>()?;
    m.add_function(wrap_pyfunction!(next_id, m)?)?;
    m.add_function(wrap_pyfunction!(logging::init_rest_log, m)?)?;
    m.add_function(wrap_pyfunction!(logging::init_access_log, m)?)?;
    m.add_function(wrap_pyfunction!(logging::log_rest_summary, m)?)?;
    m.add_function(wrap_pyfunction!(logging::log_access, m)?)?;
    m.add_function(wrap_pyfunction!(http::extract_headers, m)?)?;
    m.add_function(wrap_pyfunction!(http::handle_http_request, m)?)?;
    Ok(())
}
