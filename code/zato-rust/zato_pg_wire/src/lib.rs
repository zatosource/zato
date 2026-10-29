//! Decoding of the rows that `PostgreSQL` returns to the pg8000 driver of Zato.
//!
//! Zato is an API, ESB, SOA and iPaaS integration platform. Its connections to `PostgreSQL` receive
//! the integer, floating-point, boolean, bytea and timestamp columns of a result in the binary format
//! of the extended query protocol, and this crate turns each `DataRow` message into the list
//! of Python values that pg8000 produces for the same row in the text format.

/// The decoder of `DataRow` messages and the kinds of columns it reads.
pub mod row;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers the row decoder class.
#[pymodule]
fn zato_pg_wire(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<row::RowDecoder>()?;
    Ok(())
}
