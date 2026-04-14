pub mod model;
pub mod config_store;
pub mod http;

use pyo3::prelude::*;

#[pyfunction]
fn next_id() -> String {
    model::next_id()
}

#[pymodule]
fn zato_server_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<http::HTTPServer>()?;
    m.add_class::<config_store::ConfigStore>()?;
    m.add_function(wrap_pyfunction!(next_id, m)?)?;
    Ok(())
}
