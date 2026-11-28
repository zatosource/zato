//! Encoding of the messages that the pg8000 driver of Zato sends to `PostgreSQL` and decoding of the rows it receives.
//!
//! Zato is an API, ESB, SOA and iPaaS integration platform. Its connections to `PostgreSQL` bind the parameters
//! of each prepared statement with a `Bind` message that this crate encodes, lists of values as binary arrays
//! that this crate encodes too, and they insert rows in bulk with binary COPY streams that this crate encodes.
//! They receive the integer, floating-point, boolean, bytea and timestamp columns of a result in the binary format
//! of the extended query protocol, and this crate turns each `DataRow` message into the list of Python values
//! that pg8000 produces for the same row in the text format.

/// The binary array parameters of statements.
pub mod array;

/// The encoding of single values in the binary format.
pub mod binary;

/// The encoder of `Bind` messages.
pub mod bind;

/// The encoder of binary COPY streams.
pub mod copy;

/// The parser of the replies of the server.
pub mod reply;

/// The decoder of `DataRow` messages and the kinds of columns it reads.
pub mod row;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers the encoders of `Bind` messages, the array parameter class,
/// the encoders of column arrays and of COPY streams, the parser of replies and the row decoder class.
#[pymodule]
fn zato_pg_wire(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(bind::encode_bind, module)?)?;
    module.add_function(wrap_pyfunction!(bind::encode_bind_execute, module)?)?;
    module.add_function(wrap_pyfunction!(reply::read_replies, module)?)?;
    module.add_function(wrap_pyfunction!(array::encode_column_arrays, module)?)?;
    module.add_function(wrap_pyfunction!(copy::encode_copy_rows, module)?)?;
    module.add_class::<array::ArrayParameter>()?;
    module.add_class::<row::RowDecoder>()?;
    Ok(())
}
