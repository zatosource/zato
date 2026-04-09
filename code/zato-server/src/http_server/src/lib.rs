use pyo3::prelude::*;

pub mod handler;
pub mod http_parser;
pub mod http_response;

#[pymodule]
fn zato_server_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<handler::ConnectionHandler>()?;
    Ok(())
}
