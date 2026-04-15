pub mod time;

use pyo3::prelude::*;

#[pymodule]
fn zato_common_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(time::utc_now, m)?)?;
    Ok(())
}
