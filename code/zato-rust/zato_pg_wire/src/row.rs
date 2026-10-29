//! Decoding of PostgreSQL `DataRow` messages into lists of Python values.
//!
//! Each column is read either natively, from the binary or the text format, or by the pg8000 converter
//! of its type, which receives the value in the text format.

use chrono::{DateTime, Datelike, Timelike, Utc};
use pyo3::IntoPyObjectExt;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyBytes, PyDateTime, PyList, PyString, PyTzInfo};

/// Type OID of `bool`.
const BOOL_OID: u32 = 16;

/// Type OID of `bytea`.
const BYTEA_OID: u32 = 17;

/// Type OID of `name`.
const NAME_OID: u32 = 19;

/// Type OID of `int8`.
const INT8_OID: u32 = 20;

/// Type OID of `int2`.
const INT2_OID: u32 = 21;

/// Type OID of `int4`.
const INT4_OID: u32 = 23;

/// Type OID of `text`.
const TEXT_OID: u32 = 25;

/// Type OID of `float8`.
const FLOAT8_OID: u32 = 701;

/// Type OID of `unknown`, the type of string literals in a select list.
const UNKNOWN_OID: u32 = 705;

/// Type OID of `bpchar`, the fixed-length character type.
const BPCHAR_OID: u32 = 1042;

/// Type OID of `varchar`.
const VARCHAR_OID: u32 = 1043;

/// Type OID of `timestamp`.
const TIMESTAMP_OID: u32 = 1114;

/// Type OID of `timestamptz`.
const TIMESTAMPTZ_OID: u32 = 1184;

/// Format code of a column received in the text format.
const TEXT_FORMAT: i16 = 0;

/// Format code of a column received in the binary format.
const BINARY_FORMAT: i16 = 1;

/// The length that a `DataRow` message gives for a NULL value.
const NULL_LENGTH: i32 = -1;

/// Where the first value of a `DataRow` message begins, after the count of its values.
const FIRST_VALUE_OFFSET: usize = 2;

/// The size of the length that precedes each value of a `DataRow` message.
const LENGTH_SIZE: usize = 4;

/// The binary value of a timestamp that is `infinity`.
const POSITIVE_INFINITY: i64 = i64::MAX;

/// The binary value of a timestamp that is `-infinity`.
const NEGATIVE_INFINITY: i64 = i64::MIN;

/// What pg8000 returns for a timestamp that is `infinity`.
const POSITIVE_INFINITY_TEXT: &str = "infinity";

/// What pg8000 returns for a timestamp that is `-infinity`.
const NEGATIVE_INFINITY_TEXT: &str = "-infinity";

/// Microseconds between the Unix epoch and 2000-01-01, the epoch of binary `PostgreSQL` timestamps.
const POSTGRESQL_EPOCH_OFFSET_MICROS: i64 = 946_684_800_000_000;

/// Nanoseconds in one microsecond.
const NANOS_PER_MICRO: u32 = 1_000;

/// A column type that is read without the pg8000 converter of the type.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum NativeKind {
    /// A character type received in the text format and returned as `str`.
    Text,

    /// `bytea` received in the binary format and returned as `bytes`.
    Bytes,

    /// `bool` received in the binary format.
    Bool,

    /// `int2` received in the binary format.
    Int2,

    /// `int4` received in the binary format.
    Int4,

    /// `int8` received in the binary format.
    Int8,

    /// `float8` received in the binary format.
    Float8,

    /// `timestamp` received in the binary format and returned as a naive `datetime`.
    Timestamp,

    /// `timestamptz` received in the binary format and returned as a `datetime` in UTC.
    TimestampTz,
}

impl NativeKind {
    /// Returns the native kind of a column type, or `None` for a type read by its pg8000 converter.
    const fn from_type_oid(type_oid: u32) -> Option<Self> {
        match type_oid {
            NAME_OID | TEXT_OID | UNKNOWN_OID | BPCHAR_OID | VARCHAR_OID => Some(Self::Text),
            BYTEA_OID => Some(Self::Bytes),
            BOOL_OID => Some(Self::Bool),
            INT2_OID => Some(Self::Int2),
            INT4_OID => Some(Self::Int4),
            INT8_OID => Some(Self::Int8),
            FLOAT8_OID => Some(Self::Float8),
            TIMESTAMP_OID => Some(Self::Timestamp),
            TIMESTAMPTZ_OID => Some(Self::TimestampTz),
            _ => None,
        }
    }

    /// Returns the format code the Bind message requests for a column of this kind.
    const fn result_format(self) -> i16 {
        match self {
            Self::Text => TEXT_FORMAT,
            Self::Bytes | Self::Bool | Self::Int2 | Self::Int4 | Self::Int8 | Self::Float8 | Self::Timestamp | Self::TimestampTz => {
                BINARY_FORMAT
            }
        }
    }

    /// Turns the bytes of one non-NULL value into the Python value pg8000 produces for it.
    fn decode<'py>(self, py: Python<'py>, value: &[u8]) -> PyResult<Bound<'py, PyAny>> {
        match self {
            Self::Text => Ok(PyString::new(py, utf8(value)?).into_any()),
            Self::Bytes => Ok(PyBytes::new(py, value).into_any()),
            Self::Bool => {
                // PostgreSQL sends a boolean as one byte, which is zero for false.
                let flag = value.iter().any(|byte| *byte != 0);
                Ok(PyBool::new(py, flag).to_owned().into_any())
            }
            Self::Int2 => i16::from_be_bytes(fixed(value)?).into_bound_py_any(py),
            Self::Int4 => i32::from_be_bytes(fixed(value)?).into_bound_py_any(py),
            Self::Int8 => i64::from_be_bytes(fixed(value)?).into_bound_py_any(py),
            Self::Float8 => f64::from_be_bytes(fixed(value)?).into_bound_py_any(py),
            Self::Timestamp => timestamp(py, i64::from_be_bytes(fixed(value)?), None),
            Self::TimestampTz => {
                let utc = PyTzInfo::utc(py)?;
                timestamp(py, i64::from_be_bytes(fixed(value)?), Some(&utc))
            }
        }
    }
}

/// How the value of one column is read.
enum ColumnKind {
    /// Read natively.
    Native(NativeKind),

    /// Read by the pg8000 converter of the column type, e.g. for `numeric` or `json`, from the text format.
    Converted(Py<PyAny>),
}

impl ColumnKind {
    /// Returns the format code the Bind message requests for this column.
    const fn result_format(&self) -> i16 {
        match self {
            Self::Native(kind) => kind.result_format(),
            Self::Converted(_) => TEXT_FORMAT,
        }
    }

    /// Turns the bytes of one non-NULL value into its Python value.
    fn decode<'py>(&self, py: Python<'py>, value: &[u8]) -> PyResult<Bound<'py, PyAny>> {
        match self {
            Self::Native(kind) => kind.decode(py, value),
            Self::Converted(converter) => converter.bind(py).call1((utf8(value)?,)),
        }
    }
}

/// The calendar fields of a timestamp, in the ranges that a Python `datetime` accepts.
#[derive(Debug, PartialEq, Eq)]
struct TimestampParts {
    /// The year, 1 to 9999 for any timestamp a `datetime` can hold.
    year: i32,

    /// The month, 1 to 12.
    month: u8,

    /// The day of the month, 1 to 31.
    day: u8,

    /// The hour, 0 to 23.
    hour: u8,

    /// The minute, 0 to 59.
    minute: u8,

    /// The second, 0 to 59.
    second: u8,

    /// The microsecond, 0 to 999999.
    microsecond: u32,
}

impl TimestampParts {
    /// Splits a binary `PostgreSQL` timestamp, in microseconds since 2000-01-01, into its calendar fields.
    fn from_postgresql(micros: i64) -> Option<Self> {
        // The binary format counts from 2000-01-01 and chrono counts from the Unix epoch.
        let unix_micros = micros.checked_add(POSTGRESQL_EPOCH_OFFSET_MICROS)?;
        let moment: DateTime<Utc> = DateTime::from_timestamp_micros(unix_micros)?;

        Some(Self {
            year: moment.year(),
            month: u8::try_from(moment.month()).ok()?,
            day: u8::try_from(moment.day()).ok()?,
            hour: u8::try_from(moment.hour()).ok()?,
            minute: u8::try_from(moment.minute()).ok()?,
            second: u8::try_from(moment.second()).ok()?,
            microsecond: moment.nanosecond() / NANOS_PER_MICRO,
        })
    }
}

/// Returns the Python value of a binary timestamp, with the time zone given or naive without one.
fn timestamp<'py>(py: Python<'py>, micros: i64, timezone: Option<&Bound<'py, PyTzInfo>>) -> PyResult<Bound<'py, PyAny>> {
    match micros {
        // The infinite timestamps are returned as the strings that pg8000 returns for them.
        POSITIVE_INFINITY => Ok(PyString::new(py, POSITIVE_INFINITY_TEXT).into_any()),
        NEGATIVE_INFINITY => Ok(PyString::new(py, NEGATIVE_INFINITY_TEXT).into_any()),
        _ => {
            let parts = TimestampParts::from_postgresql(micros)
                .ok_or_else(|| PyValueError::new_err(format!("Timestamp out of range: {micros}")))?;
            let value = PyDateTime::new(
                py,
                parts.year,
                parts.month,
                parts.day,
                parts.hour,
                parts.minute,
                parts.second,
                parts.microsecond,
                timezone,
            )?;
            Ok(value.into_any())
        }
    }
}

/// Returns the text of a value received in the text format, which the connection encodes in UTF-8.
fn utf8(value: &[u8]) -> PyResult<&str> {
    std::str::from_utf8(value).map_err(|error| PyValueError::new_err(error.to_string()))
}

/// Returns the bytes of a fixed-size binary value, which fails if the value has a different size.
fn fixed<const SIZE: usize>(value: &[u8]) -> PyResult<[u8; SIZE]> {
    <[u8; SIZE]>::try_from(value).map_err(|error| PyValueError::new_err(error.to_string()))
}

/// Reads the length that precedes a value, or `None` if the message ends before it.
fn read_length(data: &[u8], offset: usize) -> Option<i32> {
    let end = offset.checked_add(LENGTH_SIZE)?;
    let bytes = data.get(offset..end)?;
    let length_bytes = <[u8; LENGTH_SIZE]>::try_from(bytes).ok()?;
    Some(i32::from_be_bytes(length_bytes))
}

/// Returns the error raised for a `DataRow` message shorter than its own lengths declare.
fn truncated_row() -> PyErr {
    PyValueError::new_err("DataRow message ends before its last value")
}

/// Reads the `DataRow` messages of one prepared statement into lists of Python values.
#[pyclass(frozen, module = "zato_pg_wire")]
pub struct RowDecoder {
    /// How each column of the result is read, in the order of the columns.
    columns: Vec<ColumnKind>,
}

#[pymethods]
impl RowDecoder {
    /// Builds the decoder from the type OID and the pg8000 converter of each column of a result.
    #[new]
    fn new(column_types: Vec<(u32, Py<PyAny>)>) -> Self {
        let mut columns = Vec::with_capacity(column_types.len());

        for (type_oid, converter) in column_types {
            // A type without a native reader keeps the converter pg8000 has for it.
            let column = NativeKind::from_type_oid(type_oid).map_or_else(|| ColumnKind::Converted(converter), ColumnKind::Native);
            columns.push(column);
        }

        Self { columns }
    }

    /// The format code of each column for the Bind message, binary for the columns read from the binary format.
    #[getter]
    fn result_formats(&self) -> Vec<i16> {
        self.columns.iter().map(ColumnKind::result_format).collect()
    }

    /// Decodes the body of one `DataRow` message into the list of its values.
    fn decode<'py>(&self, py: Python<'py>, data: &[u8]) -> PyResult<Bound<'py, PyList>> {
        let mut values = Vec::with_capacity(self.columns.len());
        let mut offset = FIRST_VALUE_OFFSET;

        for column in &self.columns {
            let length = read_length(data, offset).ok_or_else(truncated_row)?;
            offset = offset.saturating_add(LENGTH_SIZE);

            // A NULL value has no bytes after its length.
            if length == NULL_LENGTH {
                values.push(py.None().into_bound(py));
                continue;
            }

            let size = usize::try_from(length).map_err(|error| PyValueError::new_err(error.to_string()))?;
            let end = offset.checked_add(size).ok_or_else(truncated_row)?;
            let value = data.get(offset..end).ok_or_else(truncated_row)?;

            values.push(column.decode(py, value)?);
            offset = end;
        }

        PyList::new(py, values)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn epoch_of_postgresql() {
        let parts = TimestampParts::from_postgresql(0);
        let expected = TimestampParts {
            year: 2000,
            month: 1,
            day: 1,
            hour: 0,
            minute: 0,
            second: 0,
            microsecond: 0,
        };
        assert_eq!(parts, Some(expected));
    }

    #[test]
    fn timestamp_before_the_epoch() {
        let parts = TimestampParts::from_postgresql(-1);
        let expected = TimestampParts {
            year: 1999,
            month: 12,
            day: 31,
            hour: 23,
            minute: 59,
            second: 59,
            microsecond: 999_999,
        };
        assert_eq!(parts, Some(expected));
    }

    #[test]
    fn timestamp_on_a_leap_day() {
        // 2024-02-29 12:34:56.789012 is 8825 days and 45296.789012 seconds after 2000-01-01.
        let micros = 8825 * 86_400_000_000 + 45_296_789_012;
        let parts = TimestampParts::from_postgresql(micros);
        let expected = TimestampParts {
            year: 2024,
            month: 2,
            day: 29,
            hour: 12,
            minute: 34,
            second: 56,
            microsecond: 789_012,
        };
        assert_eq!(parts, Some(expected));
    }

    #[test]
    fn infinite_timestamps_are_not_split() {
        assert_eq!(TimestampParts::from_postgresql(POSITIVE_INFINITY), None);
        assert_eq!(TimestampParts::from_postgresql(NEGATIVE_INFINITY), None);
    }

    #[test]
    fn native_kinds_and_formats() {
        assert_eq!(NativeKind::from_type_oid(TEXT_OID), Some(NativeKind::Text));
        assert_eq!(NativeKind::from_type_oid(TIMESTAMPTZ_OID), Some(NativeKind::TimestampTz));
        assert_eq!(NativeKind::from_type_oid(1700), None);
        assert_eq!(NativeKind::Text.result_format(), TEXT_FORMAT);
        assert_eq!(NativeKind::Bytes.result_format(), BINARY_FORMAT);
    }

    #[test]
    fn lengths_of_values() {
        let data = [0, 1, 0, 0, 0, 3, b'a', b'b', b'c', 255, 255, 255, 255];
        assert_eq!(read_length(&data, FIRST_VALUE_OFFSET), Some(3));
        assert_eq!(read_length(&data, 9), Some(NULL_LENGTH));
        assert_eq!(read_length(&data, 10), None);
    }
}
