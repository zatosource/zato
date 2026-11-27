//! Binary array parameters of the statements of Zato.
//!
//! A list of values bound as one array parameter gives a statement a single text whatever the number
//! of its values, e.g. `id = ANY(CAST($1 AS BIGINT[]))` in place of an `IN` list, or one array per column
//! of a multi-row insert through `unnest`.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use crate::binary::ValueType;

/// The number of dimensions of the array of a non-empty list.
const ONE_DIMENSION: i32 = 1;

/// The number of dimensions of an empty array, which has no dimension fields.
const NO_DIMENSIONS: i32 = 0;

/// The flags of an array without NULL elements.
const NO_NULLS: i32 = 0;

/// The flags of an array with at least one NULL element.
const HAS_NULLS: i32 = 1;

/// The lower bound of the dimension of an array, which `PostgreSQL` counts from one.
const LOWER_BOUND: i32 = 1;

/// The length that an array gives for a NULL element.
const NULL_LENGTH: i32 = -1;

/// Where the flags of an array begin, after its number of dimensions.
const FLAGS_OFFSET: usize = 4;

/// Where the flags of an array end.
const FLAGS_END: usize = 8;

/// The name, the type and the bind processor, if any, of one column of a multi-row insert or of a COPY stream.
pub type InsertColumn = (String, String, Option<Py<PyAny>>);

/// A list of values encoded as a one-dimensional binary array of `PostgreSQL`, which a `Bind` message
/// sends as it is, in the binary format.
#[pyclass(frozen, module = "zato_pg_wire")]
pub struct ArrayParameter {
    /// The binary array - its header, its dimension and its elements.
    data: Vec<u8>,
}

impl ArrayParameter {
    /// Returns the binary array.
    pub fn data(&self) -> &[u8] {
        self.data.as_slice()
    }
}

#[pymethods]
impl ArrayParameter {
    /// Encodes a list of values of the column type given, e.g. the IDs of the delivery rows that a statement reads.
    #[new]
    fn new(type_name: &str, values: &Bound<'_, PyList>) -> PyResult<Self> {
        let value_type = ValueType::from_name(type_name)?;
        let data = encode_array(value_type, values.iter(), values.len(), None)?;
        Ok(Self { data })
    }
}

/// Returns the error raised for an array whose length does not fit its header.
fn too_long(error: std::num::TryFromIntError) -> PyErr {
    PyValueError::new_err(format!("Array too long for a binary array: {error}"))
}

/// Encodes values as a one-dimensional binary array, each value through the bind processor given, if any.
fn encode_array<'py>(
    value_type: ValueType,
    values: impl Iterator<Item = Bound<'py, PyAny>>,
    count: usize,
    processor: Option<&Bound<'py, PyAny>>,
) -> PyResult<Vec<u8>> {
    let element_count = i32::try_from(count).map_err(too_long)?;
    let mut out = Vec::new();

    // An empty array has no dimension at all ..
    let dimensions = if count == 0 { NO_DIMENSIONS } else { ONE_DIMENSION };

    out.extend_from_slice(&dimensions.to_be_bytes());
    out.extend_from_slice(&NO_NULLS.to_be_bytes());
    out.extend_from_slice(&value_type.oid().to_be_bytes());

    if count > 0 {
        out.extend_from_slice(&element_count.to_be_bytes());
        out.extend_from_slice(&LOWER_BOUND.to_be_bytes());
    }

    // .. and each element follows its length, a NULL one without any bytes.
    let mut has_nulls = false;
    let mut buffer = Vec::new();

    for value in values {
        if value.is_none() {
            has_nulls = true;
            out.extend_from_slice(&NULL_LENGTH.to_be_bytes());
            continue;
        }

        // A value is converted by the processor of its column first, as `SQLAlchemy` would convert it.
        let value = match processor {
            Some(processor) => processor.call1((value,))?,
            None => value,
        };

        let data = value_type.encode(&value, &mut buffer)?;
        let length = i32::try_from(data.len()).map_err(too_long)?;

        out.extend_from_slice(&length.to_be_bytes());
        out.extend_from_slice(data);
    }

    // The flags in the header are set once the elements show whether any of them is NULL.
    if has_nulls {
        if let Some(flags) = out.get_mut(FLAGS_OFFSET..FLAGS_END) {
            flags.copy_from_slice(&HAS_NULLS.to_be_bytes());
        }
    }

    Ok(out)
}

/// Encodes the values of each column of rows that all have the same keys as one binary array per column,
/// in the order of the columns given, for a multi-row insert through `unnest`.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 extracts the Python list of columns into an owned vector"
)]
pub fn encode_column_arrays(rows: &Bound<'_, PyList>, columns: Vec<InsertColumn>) -> PyResult<Vec<ArrayParameter>> {
    let py = rows.py();
    let row_count = rows.len();
    let mut out = Vec::with_capacity(columns.len());

    for (name, type_name, processor) in &columns {
        let value_type = ValueType::from_name(type_name)?;
        let processor = processor.as_ref().map(|processor| processor.bind(py));
        let mut values = Vec::with_capacity(row_count);

        // Each row has a value for each column.
        for row in rows.iter() {
            let row = row.cast::<PyDict>()?;
            let value = row.as_any().get_item(name)?;
            values.push(value);
        }

        let data = encode_array(value_type, values.into_iter(), row_count, processor)?;
        out.push(ArrayParameter { data });
    }

    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[expect(clippy::unwrap_used, reason = "test assertions need direct access")]
    fn empty_array_has_no_dimension() {
        let values: std::iter::Empty<Bound<'static, PyAny>> = std::iter::empty();
        let data = encode_array(ValueType::Int8, values, 0, None).unwrap();

        let mut expected = Vec::new();
        expected.extend_from_slice(&NO_DIMENSIONS.to_be_bytes());
        expected.extend_from_slice(&NO_NULLS.to_be_bytes());
        expected.extend_from_slice(&ValueType::Int8.oid().to_be_bytes());

        assert_eq!(data, expected);
    }
}
