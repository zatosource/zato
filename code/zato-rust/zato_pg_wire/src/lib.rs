//! Encoding of the messages that the pg8000 driver of Zato sends to `PostgreSQL` and decoding of the rows it receives.
//!
//! Zato is an API, ESB, SOA and iPaaS integration platform. Its connections to `PostgreSQL` bind the parameters
//! of each prepared statement with a `Bind` message that this crate encodes, and they receive the integer,
//! floating-point, boolean, bytea and timestamp columns of a result in the binary format of the extended
//! query protocol, and this crate turns each `DataRow` message into the list of Python values that pg8000
//! produces for the same row in the text format.

/// The encoder of `Bind` messages.
pub mod bind;

/// The decoder of `DataRow` messages and the kinds of columns it reads.
pub mod row;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers the `Bind` message encoder and the row decoder class.
#[pymodule]
fn zato_pg_wire(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(bind::encode_bind, module)?)?;
    module.add_class::<row::RowDecoder>()?;
    Ok(())
}
