//! Encoding of single Python values in the binary format of `PostgreSQL`.
//!
//! The fields of a binary COPY stream and the elements of a binary array parameter have the same encoding,
//! which this module provides for each column type that the pub/sub and audit log tables of Zato use.

use jiff::civil::DateTime;
use jiff::tz::TimeZone;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyBytes, PyDateAccess, PyDateTime, PyDelta, PyDeltaAccess, PyFloat, PyString, PyTimeAccess, PyType};

/// Type OID of `bool`.
const BOOL_OID: u32 = 16;

/// Type OID of `bytea`.
const BYTEA_OID: u32 = 17;

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

/// Type OID of `varchar`.
const VARCHAR_OID: u32 = 1043;

/// Type OID of `timestamp`.
const TIMESTAMP_OID: u32 = 1114;

/// Type OID of `timestamptz`.
const TIMESTAMPTZ_OID: u32 = 1184;

/// Type OID of `numeric`.
const NUMERIC_OID: u32 = 1700;

/// Microseconds between the Unix epoch and 2000-01-01, the epoch of binary `PostgreSQL` timestamps.
const POSTGRESQL_EPOCH_OFFSET_MICROS: i64 = 946_684_800_000_000;

/// Microseconds in one second.
const MICROS_PER_SECOND: i64 = 1_000_000;

/// Seconds in one day.
const SECONDS_PER_DAY: i64 = 86_400;

/// Nanoseconds in one microsecond.
const NANOS_PER_MICRO: u32 = 1_000;

/// The binary value of `true`.
const TRUE_BYTE: u8 = 1;

/// The binary value of `false`.
const FALSE_BYTE: u8 = 0;

/// The sign of a positive binary `numeric`.
const NUMERIC_POSITIVE: u16 = 0x0000;

/// The sign of a negative binary `numeric`.
const NUMERIC_NEGATIVE: u16 = 0x4000;

/// The sign of a binary `numeric` that is `NaN`.
const NUMERIC_NAN: u16 = 0xC000;

/// The sign of a binary `numeric` that is `Infinity`.
const NUMERIC_POSITIVE_INFINITY: u16 = 0xD000;

/// The sign of a binary `numeric` that is `-Infinity`.
const NUMERIC_NEGATIVE_INFINITY: u16 = 0xF000;

/// How many decimal digits one digit of a binary `numeric` covers.
const NUMERIC_BASE_DIGITS: usize = 4;

/// The base of the digits of a Python `Decimal`.
const DECIMAL_BASE: u16 = 10;

/// The class `decimal.Decimal`, through which every number is encoded as a binary `numeric`.
static DECIMAL_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();

/// The type of a column, by which its values are encoded.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ValueType {
    /// `int2`, from a Python `int`.
    Int2,

    /// `int4`, from a Python `int`.
    Int4,

    /// `int8`, from a Python `int`.
    Int8,

    /// `float8`, from a Python `float` or `int`.
    Float8,

    /// `bool`, from a Python `bool`.
    Bool,

    /// `bytea`, from Python `bytes`.
    Bytea,

    /// `text`, from a Python `str`.
    Text,

    /// `varchar`, from a Python `str`.
    Varchar,

    /// `numeric`, from a Python `Decimal`, `int` or `float`.
    Numeric,

    /// `timestamp`, from a naive Python `datetime`.
    Timestamp,

    /// `timestamptz`, from a Python `datetime` with a time zone.
    TimestampTz,
}

impl ValueType {
    /// Returns the type of a column from the name that `SQLAlchemy` compiles for it, without its length.
    pub fn from_name(name: &str) -> PyResult<Self> {
        match name {
            "SMALLINT" => Ok(Self::Int2),
            "INTEGER" => Ok(Self::Int4),
            "BIGINT" => Ok(Self::Int8),
            "DOUBLE PRECISION" => Ok(Self::Float8),
            "BOOLEAN" => Ok(Self::Bool),
            "BYTEA" => Ok(Self::Bytea),
            "TEXT" => Ok(Self::Text),
            "VARCHAR" => Ok(Self::Varchar),
            "NUMERIC" => Ok(Self::Numeric),
            "TIMESTAMP WITHOUT TIME ZONE" => Ok(Self::Timestamp),
            "TIMESTAMP WITH TIME ZONE" => Ok(Self::TimestampTz),
            // Any other type has no binary encoding here.
            _ => Err(PyValueError::new_err(format!("No binary encoding for type `{name}`"))),
        }
    }

    /// Returns the OID of the type, which the header of a binary array gives for its elements.
    pub const fn oid(self) -> u32 {
        match self {
            Self::Int2 => INT2_OID,
            Self::Int4 => INT4_OID,
            Self::Int8 => INT8_OID,
            Self::Float8 => FLOAT8_OID,
            Self::Bool => BOOL_OID,
            Self::Bytea => BYTEA_OID,
            Self::Text => TEXT_OID,
            Self::Varchar => VARCHAR_OID,
            Self::Numeric => NUMERIC_OID,
            Self::Timestamp => TIMESTAMP_OID,
            Self::TimestampTz => TIMESTAMPTZ_OID,
        }
    }

    /// Returns the bytes of a non-NULL value - those of the value itself for `bytea` and the character types,
    /// or the encoding written into the buffer given for any other type.
    pub fn encode<'value>(self, value: &'value Bound<'_, PyAny>, buffer: &'value mut Vec<u8>) -> PyResult<&'value [u8]> {
        // A bytea value and the UTF-8 of a string are sent as they are ..
        match self {
            Self::Bytea => return Ok(value.cast::<PyBytes>()?.as_bytes()),
            Self::Text | Self::Varchar => return Ok(value.cast::<PyString>()?.to_str()?.as_bytes()),
            _ => {}
        }

        // .. while any other value is converted first and then replaces the value in the buffer,
        // which holds one value at a time, so that a value that cannot be converted leaves the buffer as it was.
        match self {
            Self::Int2 => replace_value(buffer, &value.extract::<i16>()?.to_be_bytes()),
            Self::Int4 => replace_value(buffer, &value.extract::<i32>()?.to_be_bytes()),
            Self::Int8 => replace_value(buffer, &value.extract::<i64>()?.to_be_bytes()),
            Self::Float8 => replace_value(buffer, &value.extract::<f64>()?.to_be_bytes()),
            Self::Bool => {
                let flag = value.extract::<bool>()?;
                let byte = if flag { TRUE_BYTE } else { FALSE_BYTE };
                replace_value(buffer, &[byte]);
            }
            Self::Numeric => {
                let encoded = encode_numeric(value)?;
                replace_value(buffer, &encoded);
            }
            Self::Timestamp => {
                let micros = timestamp_micros(value, false)?;
                replace_value(buffer, &micros.to_be_bytes());
            }
            Self::TimestampTz => {
                let micros = timestamp_micros(value, true)?;
                replace_value(buffer, &micros.to_be_bytes());
            }
            // The types sent as they are returned above.
            Self::Bytea | Self::Text | Self::Varchar => {}
        }

        Ok(buffer.as_slice())
    }
}

/// Returns the error raised for a `numeric` whose digits or weight do not fit its binary header.
fn numeric_too_large(number: &Bound<'_, PyAny>) -> PyErr {
    PyValueError::new_err(format!("Number too large for a binary numeric: {number}"))
}

/// Encodes a finite number as a binary `numeric` - the count of its base 10000 digits, the weight of the first one,
/// its sign, its display scale and the digits, most significant first.
fn numeric_from_decimal(is_negative: bool, decimal_digits: &[u8], exponent: i64) -> Option<Vec<u8>> {
    let digit_count = decimal_digits.len();

    // The display scale is the number of decimal digits after the decimal point ..
    let scale = if exponent < 0 { exponent.unsigned_abs() } else { 0 };
    let scale = usize::try_from(scale).ok()?;

    // .. and the digits are split at the decimal point, with the zeros that a positive exponent implies ..
    let mut integer_part: Vec<u8> = Vec::new();
    let mut fraction_part: Vec<u8> = Vec::new();

    if exponent >= 0 {
        let trailing_zeros = usize::try_from(exponent).ok()?;
        integer_part.extend_from_slice(decimal_digits);
        integer_part.resize(digit_count.checked_add(trailing_zeros)?, 0);
    } else if digit_count >= scale {
        let split = digit_count.checked_sub(scale)?;
        let (integer_digits, fraction_digits) = decimal_digits.split_at(split);
        integer_part.extend_from_slice(integer_digits);
        fraction_part.extend_from_slice(fraction_digits);
    } else {
        let leading_zeros = scale.checked_sub(digit_count)?;
        fraction_part.resize(leading_zeros, 0);
        fraction_part.extend_from_slice(decimal_digits);
    }

    // .. the integer part is padded on the left and the fraction on the right to whole base 10000 digits ..
    let integer_padding = integer_part.len().wrapping_neg() % NUMERIC_BASE_DIGITS;
    let fraction_padding = fraction_part.len().wrapping_neg() % NUMERIC_BASE_DIGITS;

    let mut aligned: Vec<u8> = vec![0; integer_padding];
    aligned.extend_from_slice(&integer_part);
    aligned.extend_from_slice(&fraction_part);
    aligned.resize(aligned.len().checked_add(fraction_padding)?, 0);

    let mut digits: Vec<u16> = Vec::with_capacity(aligned.len() / NUMERIC_BASE_DIGITS);

    for chunk in aligned.chunks(NUMERIC_BASE_DIGITS) {
        let mut digit: u16 = 0;
        for decimal_digit in chunk {
            digit = digit.checked_mul(DECIMAL_BASE)?.checked_add(u16::from(*decimal_digit))?;
        }
        digits.push(digit);
    }

    // .. the weight of the first digit counts the base 10000 digits of the integer part ..
    let integer_digit_count = (integer_padding.checked_add(integer_part.len())?) / NUMERIC_BASE_DIGITS;
    let mut weight = i64::try_from(integer_digit_count).ok()?.checked_sub(1)?;

    // .. the leading zero digits are left out, each lowering the weight ..
    let first_nonzero = digits.iter().position(|digit| *digit != 0).unwrap_or(digits.len());
    let leading_zero_count = i64::try_from(first_nonzero).ok()?;
    weight = weight.checked_sub(leading_zero_count)?;

    // .. as are the trailing ones, which the weight implies ..
    let last_nonzero = digits
        .iter()
        .rposition(|digit| *digit != 0)
        .map_or(first_nonzero, |position| position.saturating_add(1));
    let significant = digits.get(first_nonzero..last_nonzero)?;

    // .. and a zero has no digits at all, no weight and no sign.
    let (weight, sign) = if significant.is_empty() {
        (0, NUMERIC_POSITIVE)
    } else if is_negative {
        (weight, NUMERIC_NEGATIVE)
    } else {
        (weight, NUMERIC_POSITIVE)
    };

    let significant_count = i16::try_from(significant.len()).ok()?;
    let weight = i16::try_from(weight).ok()?;
    let scale = i16::try_from(scale).ok()?;

    let mut out = Vec::with_capacity(significant.len().saturating_mul(2).saturating_add(NUMERIC_BASE_DIGITS * 2));
    out.extend_from_slice(&significant_count.to_be_bytes());
    out.extend_from_slice(&weight.to_be_bytes());
    out.extend_from_slice(&sign.to_be_bytes());
    out.extend_from_slice(&scale.to_be_bytes());

    for digit in significant {
        out.extend_from_slice(&digit.to_be_bytes());
    }

    Some(out)
}

/// Returns the header of a binary `numeric` that is `NaN` or an infinity, which has no digits.
fn special_numeric(sign: u16) -> Vec<u8> {
    let mut out = Vec::with_capacity(NUMERIC_BASE_DIGITS * 2);
    out.extend_from_slice(&0_i16.to_be_bytes());
    out.extend_from_slice(&0_i16.to_be_bytes());
    out.extend_from_slice(&sign.to_be_bytes());
    out.extend_from_slice(&0_i16.to_be_bytes());
    out
}

/// Replaces the value that a buffer holds with the bytes given.
fn replace_value(buffer: &mut Vec<u8>, bytes: &[u8]) {
    buffer.clear();
    buffer.extend_from_slice(bytes);
}

/// Encodes a Python number as a binary `numeric` through its `Decimal`, a float through its shortest representation.
fn encode_numeric(value: &Bound<'_, PyAny>) -> PyResult<Vec<u8>> {
    let py = value.py();
    let decimal_class = DECIMAL_CLASS.import(py, "decimal", "Decimal")?;

    let number = if value.is_instance_of::<PyFloat>() {
        let shortest = value.repr()?;
        decimal_class.call1((shortest,))?
    } else {
        decimal_class.call1((value,))?
    };

    // NaN and the infinities have no digits ..
    let is_finite: bool = number.call_method0("is_finite")?.extract()?;

    if !is_finite {
        let is_nan: bool = number.call_method0("is_nan")?.extract()?;
        let is_signed: bool = number.call_method0("is_signed")?.extract()?;

        let sign = if is_nan {
            NUMERIC_NAN
        } else if is_signed {
            NUMERIC_NEGATIVE_INFINITY
        } else {
            NUMERIC_POSITIVE_INFINITY
        };

        return Ok(special_numeric(sign));
    }

    // .. while any other number has the digits, the sign and the exponent of its decimal tuple.
    let (sign, decimal_digits, exponent): (u8, Vec<u8>, i64) = number.call_method0("as_tuple")?.extract()?;
    let is_negative = sign != 0;

    numeric_from_decimal(is_negative, &decimal_digits, exponent).ok_or_else(|| numeric_too_large(&number))
}

/// Returns the microseconds of a `timedelta`.
fn delta_micros(delta: &Bound<'_, PyDelta>) -> i64 {
    let days = i64::from(delta.get_days());
    let seconds = i64::from(delta.get_seconds());
    let micros = i64::from(delta.get_microseconds());

    let day_seconds = days.saturating_mul(SECONDS_PER_DAY);
    let total_seconds = day_seconds.saturating_add(seconds);

    total_seconds.saturating_mul(MICROS_PER_SECOND).saturating_add(micros)
}

/// Returns the microseconds since 2000-01-01 of a `datetime`, with a time zone for `timestamptz`
/// and without one for `timestamp`.
fn timestamp_micros(value: &Bound<'_, PyAny>, has_time_zone: bool) -> PyResult<i64> {
    let moment = value.cast::<PyDateTime>()?;

    // The type of the column decides whether the value must have a time zone.
    let offset = moment.call_method0("utcoffset")?;
    let is_aware = !offset.is_none();

    if is_aware != has_time_zone {
        let expected = if has_time_zone { "with" } else { "without" };
        return Err(PyTypeError::new_err(format!(
            "Expected a datetime {expected} a time zone: {moment}"
        )));
    }

    let year = i16::try_from(moment.get_year())?;
    let month = i8::try_from(moment.get_month())?;
    let day = i8::try_from(moment.get_day())?;
    let hour = i8::try_from(moment.get_hour())?;
    let minute = i8::try_from(moment.get_minute())?;
    let second = i8::try_from(moment.get_second())?;
    let nanosecond = i32::try_from(moment.get_microsecond().saturating_mul(NANOS_PER_MICRO))?;

    // The calendar fields are counted as if they were in UTC ..
    let civil =
        DateTime::new(year, month, day, hour, minute, second, nanosecond).map_err(|error| PyValueError::new_err(error.to_string()))?;
    let utc = TimeZone::UTC
        .to_timestamp(civil)
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    let unix_micros = utc.as_microsecond();
    let mut out = unix_micros.saturating_sub(POSTGRESQL_EPOCH_OFFSET_MICROS);

    // .. and a value with a time zone is moved by its offset from UTC.
    if is_aware {
        let offset = offset.cast::<PyDelta>()?;
        out = out.saturating_sub(delta_micros(offset));
    }

    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn numeric(is_negative: bool, digits: &[u8], exponent: i64) -> Vec<u8> {
        numeric_from_decimal(is_negative, digits, exponent).unwrap()
    }

    fn expected(digit_count: i16, weight: i16, sign: u16, scale: i16, digits: &[u16]) -> Vec<u8> {
        let mut out = Vec::new();
        out.extend_from_slice(&digit_count.to_be_bytes());
        out.extend_from_slice(&weight.to_be_bytes());
        out.extend_from_slice(&sign.to_be_bytes());
        out.extend_from_slice(&scale.to_be_bytes());
        for digit in digits {
            out.extend_from_slice(&digit.to_be_bytes());
        }
        out
    }

    #[test]
    fn numeric_integer() {
        // 123456789 is 1 2345 6789 in base 10000.
        assert_eq!(
            numeric(false, &[1, 2, 3, 4, 5, 6, 7, 8, 9], 0),
            expected(3, 2, NUMERIC_POSITIVE, 0, &[1, 2345, 6789])
        );
    }

    #[test]
    fn numeric_fraction() {
        // -12.5 is 12 . 5000 with a display scale of 1.
        assert_eq!(numeric(true, &[1, 2, 5], -1), expected(2, 0, NUMERIC_NEGATIVE, 1, &[12, 5000]));
    }

    #[test]
    fn numeric_small_fraction() {
        // 0.00005 is 0 . 0000 5000, whose first significant digit has a weight of -2.
        assert_eq!(numeric(false, &[5], -5), expected(1, -2, NUMERIC_POSITIVE, 5, &[5000]));
    }

    #[test]
    fn numeric_trailing_zeros() {
        // 1E+8 is 1 0000 0000, whose zero digits the weight implies.
        assert_eq!(numeric(false, &[1], 8), expected(1, 2, NUMERIC_POSITIVE, 0, &[1]));
    }

    #[test]
    fn numeric_zero() {
        // -0.00 has no digits, a positive sign and a display scale of 2.
        assert_eq!(numeric(true, &[0], -2), expected(0, 0, NUMERIC_POSITIVE, 2, &[]));
    }

    #[test]
    fn numeric_specials() {
        assert_eq!(special_numeric(NUMERIC_NAN), expected(0, 0, NUMERIC_NAN, 0, &[]));
    }

    #[test]
    fn type_names_and_oids() {
        assert_eq!(ValueType::from_name("BIGINT").ok(), Some(ValueType::Int8));
        assert_eq!(ValueType::from_name("TIMESTAMP WITH TIME ZONE").ok(), Some(ValueType::TimestampTz));
        assert_eq!(ValueType::Varchar.oid(), VARCHAR_OID);
        assert_eq!(ValueType::Numeric.oid(), NUMERIC_OID);
    }
}
