//! Encoding of rows as a COPY stream in the binary format of `PostgreSQL`.
//!
//! The audit log of Zato and the deliveries of large publications are inserted with `COPY ... FROM STDIN`,
//! whose stream this module encodes in chunks, each large value being a chunk of its own, so that it is sent
//! without being copied into the chunk before it.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};

use crate::array::InsertColumn;
use crate::binary::ValueType;

/// The signature of a binary COPY stream, followed by its flags and the length of its extension area, both zero.
const COPY_HEADER: &[u8] = b"PGCOPY\n\xff\r\n\0\0\0\0\0\0\0\0\0";

/// The field count that ends a binary COPY stream.
const COPY_TRAILER: i16 = -1;

/// The length of a field that is NULL.
const NULL_LENGTH: i32 = -1;

/// One column of a COPY stream, ready for encoding.
struct CopyColumn<'py> {
    /// The key of the column in each row.
    name: String,

    /// The type by which the values of the column are encoded.
    value_type: ValueType,

    /// What converts each value for the driver, if the type of the column needs a conversion.
    processor: Option<Bound<'py, PyAny>>,
}

/// Returns the error raised for a field or a row that does not fit the lengths of the protocol.
fn too_large(what: &str, error: std::num::TryFromIntError) -> PyErr {
    PyValueError::new_err(format!("COPY stream has too large a {what}: {error}"))
}

/// Encodes rows that all have the keys of the columns given as a binary COPY stream, returned as a list of chunks.
/// Each value of at least `max_inline_size` bytes is a chunk of its own, a `bytea` value as the very object it is.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 extracts the Python list of columns into an owned vector"
)]
pub fn encode_copy_rows<'py>(
    rows: &Bound<'py, PyList>,
    columns: Vec<InsertColumn>,
    max_inline_size: usize,
) -> PyResult<Bound<'py, PyList>> {
    let py = rows.py();

    let mut copy_columns = Vec::with_capacity(columns.len());

    for (name, type_name, processor) in columns {
        let value_type = ValueType::from_name(&type_name)?;
        let processor = processor.map(|processor| processor.into_bound(py));
        copy_columns.push(CopyColumn {
            name,
            value_type,
            processor,
        });
    }

    let field_count = i16::try_from(copy_columns.len()).map_err(|error| too_large("field count", error))?;
    let field_count = field_count.to_be_bytes();

    let chunks = PyList::empty(py);
    let mut current = Vec::from(COPY_HEADER);
    let mut buffer = Vec::new();

    for row in rows.iter() {
        let row = row.cast::<PyDict>()?;
        current.extend_from_slice(&field_count);

        for column in &copy_columns {
            let value = row.as_any().get_item(&column.name)?;

            // A NULL value has only its length ..
            if value.is_none() {
                current.extend_from_slice(&NULL_LENGTH.to_be_bytes());
                continue;
            }

            // .. any other one is processed the way SQLAlchemy would process it ..
            let value = match &column.processor {
                Some(processor) => processor.call1((value,))?,
                None => value,
            };

            let data = column.value_type.encode(&value, &mut buffer)?;
            let size = data.len();
            let length = i32::try_from(size).map_err(|error| too_large("value", error))?;
            current.extend_from_slice(&length.to_be_bytes());

            // .. a small one is copied into the current chunk ..
            if size < max_inline_size {
                current.extend_from_slice(data);
                continue;
            }

            // .. and a large one follows the current chunk as a chunk of its own, after which a new chunk begins.
            chunks.append(PyBytes::new(py, &current))?;
            current.clear();

            if column.value_type == ValueType::Bytea {
                chunks.append(&value)?;
            } else {
                chunks.append(PyBytes::new(py, data))?;
            }
        }
    }

    current.extend_from_slice(&COPY_TRAILER.to_be_bytes());
    chunks.append(PyBytes::new(py, &current))?;

    Ok(chunks)
}
