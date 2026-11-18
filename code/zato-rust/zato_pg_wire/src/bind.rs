//! Encoding of the `Bind` messages of the extended query protocol of `PostgreSQL`.
//!
//! The pg8000 driver of Zato converts the parameters of a statement into `str`, `bytes` or `None`
//! before they are bound, and this module turns them, together with the name of the prepared statement
//! and the formats of the result columns, into one complete `Bind` message.

use std::num::TryFromIntError;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString, PyTuple};

/// The code of a `Bind` message.
const BIND_CODE: u8 = b'B';

/// Format code of a parameter sent in the text format.
const TEXT_FORMAT: i16 = 0;

/// Format code of a parameter sent in the binary format.
const BINARY_FORMAT: i16 = 1;

/// The length that a `Bind` message gives for a NULL parameter.
const NULL_LENGTH: i32 = -1;

/// The name of the unnamed portal, an empty string followed by its terminating NUL byte.
const UNNAMED_PORTAL: &[u8] = b"\0";

/// Where the length of a message begins, after its code.
const LENGTH_OFFSET: usize = 1;

/// The size of the length that precedes the body of a message and each of its values.
const LENGTH_SIZE: usize = 4;

/// The size of a count or of a format code in a `Bind` message.
const INT16_SIZE: usize = 2;

/// How many counts a `Bind` message has - of the parameter formats, of the values and of the result formats.
const COUNT_FIELDS: usize = 3;

/// One parameter of a statement, as the driver converted it.
enum Parameter<'value> {
    /// A NULL value.
    Null,

    /// A `bytea` value, sent in the binary format.
    Binary(&'value [u8]),

    /// Any other value, sent in the text format, which the connection encodes in UTF-8.
    Text(&'value str),
}

impl Parameter<'_> {
    /// Returns the format code the `Bind` message gives for this parameter.
    const fn format(&self) -> i16 {
        match self {
            Self::Binary(_) => BINARY_FORMAT,
            Self::Null | Self::Text(_) => TEXT_FORMAT,
        }
    }

    /// Returns the bytes of the value, or `None` for a NULL value.
    const fn data(&self) -> Option<&[u8]> {
        match self {
            Self::Null => None,
            Self::Binary(data) => Some(data),
            Self::Text(text) => Some(text.as_bytes()),
        }
    }
}

/// Returns the error raised for a message whose counts or lengths do not fit the fields of the protocol.
fn too_large(what: &str, error: TryFromIntError) -> PyErr {
    PyValueError::new_err(format!("Bind message has too large a {what}: {error}"))
}

/// Reads one parameter converted by the driver, which is `None`, `bytes` or `str`.
fn read_parameter<'value>(value: &'value Bound<'_, PyAny>) -> PyResult<Parameter<'value>> {
    if value.is_none() {
        return Ok(Parameter::Null);
    }

    // A bytea value is sent as it is ..
    if let Ok(data) = value.cast::<PyBytes>() {
        return Ok(Parameter::Binary(data.as_bytes()));
    }

    // .. and any other value is text that the driver converted already.
    let text = value.cast::<PyString>()?;
    Ok(Parameter::Text(text.to_str()?))
}

/// Builds the body of a `Bind` message, without its code and its length.
fn build_body(statement_name: &[u8], parameters: &[Parameter<'_>], result_formats: &[i16]) -> PyResult<Vec<u8>> {
    let parameter_count = u16::try_from(parameters.len()).map_err(|error| too_large("parameter count", error))?;
    let result_format_count = u16::try_from(result_formats.len()).map_err(|error| too_large("result format count", error))?;

    // The values are measured first, so that the body is allocated once.
    let int16_fields = parameters.len().saturating_add(result_formats.len()).saturating_add(COUNT_FIELDS);
    let mut size = UNNAMED_PORTAL.len().saturating_add(statement_name.len());
    size = size.saturating_add(INT16_SIZE.saturating_mul(int16_fields));

    for parameter in parameters {
        let data_size = parameter.data().map_or(0, <[u8]>::len);
        size = size.saturating_add(LENGTH_SIZE).saturating_add(data_size);
    }

    let mut body = Vec::with_capacity(size);

    // The portal is unnamed and the statement is the prepared one, whose name ends with its NUL byte already ..
    body.extend_from_slice(UNNAMED_PORTAL);
    body.extend_from_slice(statement_name);

    // .. each parameter has a format code of its own ..
    body.extend_from_slice(&parameter_count.to_be_bytes());

    for parameter in parameters {
        body.extend_from_slice(&parameter.format().to_be_bytes());
    }

    // .. each value follows its length, and a NULL value has no bytes after its length ..
    body.extend_from_slice(&parameter_count.to_be_bytes());

    for parameter in parameters {
        match parameter.data() {
            None => body.extend_from_slice(&NULL_LENGTH.to_be_bytes()),
            Some(data) => {
                let data_length = i32::try_from(data.len()).map_err(|error| too_large("value", error))?;
                body.extend_from_slice(&data_length.to_be_bytes());
                body.extend_from_slice(data);
            }
        }
    }

    // .. and each column of the result has a format code too.
    body.extend_from_slice(&result_format_count.to_be_bytes());

    for result_format in result_formats {
        body.extend_from_slice(&result_format.to_be_bytes());
    }

    Ok(body)
}

/// Builds a complete `Bind` message - its code, its length and its body.
fn build_message(statement_name: &[u8], parameters: &[Parameter<'_>], result_formats: &[i16]) -> PyResult<Vec<u8>> {
    let body = build_body(statement_name, parameters, result_formats)?;

    // The length of a message counts its own bytes and the body, but not the code.
    let message_length = body.len().saturating_add(LENGTH_SIZE);
    let message_length = i32::try_from(message_length).map_err(|error| too_large("body", error))?;

    let mut message = Vec::with_capacity(LENGTH_OFFSET.saturating_add(LENGTH_SIZE).saturating_add(body.len()));
    message.push(BIND_CODE);
    message.extend_from_slice(&message_length.to_be_bytes());
    message.extend_from_slice(&body);

    Ok(message)
}

/// Encodes the `Bind` message of a prepared statement from its name, terminated by a NUL byte,
/// the parameters that the driver converted and the format codes of the result columns.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 extracts the Python list of format codes into an owned vector"
)]
pub fn encode_bind<'py>(
    py: Python<'py>,
    statement_name: &[u8],
    parameters: &Bound<'py, PyTuple>,
    result_formats: Vec<i16>,
) -> PyResult<Bound<'py, PyBytes>> {
    let values: Vec<Bound<'py, PyAny>> = parameters.iter().collect();
    let mut read = Vec::with_capacity(values.len());

    for value in &values {
        read.push(read_parameter(value)?);
    }

    let message = build_message(statement_name, &read, &result_formats)?;
    Ok(PyBytes::new(py, &message))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn message_of_each_kind_of_parameter() {
        let parameters = [Parameter::Null, Parameter::Binary(b"\x01\x02"), Parameter::Text("abc")];
        let message = build_message(b"zato_1\0", &parameters, &[BINARY_FORMAT]);

        let mut expected: Vec<u8> = vec![BIND_CODE, 0, 0, 0, 43];
        expected.extend_from_slice(b"\0zato_1\0");
        expected.extend_from_slice(&[0, 3, 0, 0, 0, 1, 0, 0]);
        expected.extend_from_slice(&[0, 3]);
        expected.extend_from_slice(&[255, 255, 255, 255]);
        expected.extend_from_slice(&[0, 0, 0, 2, 1, 2]);
        expected.extend_from_slice(&[0, 0, 0, 3, b'a', b'b', b'c']);
        expected.extend_from_slice(&[0, 1, 0, 1]);

        assert_eq!(message.ok(), Some(expected));
    }

    #[test]
    fn message_without_parameters_or_result() {
        let message = build_message(b"zato_2\0", &[], &[]);

        let mut expected: Vec<u8> = vec![BIND_CODE, 0, 0, 0, 18];
        expected.extend_from_slice(b"\0zato_2\0");
        expected.extend_from_slice(&[0, 0, 0, 0, 0, 0]);

        assert_eq!(message.ok(), Some(expected));
    }
}
