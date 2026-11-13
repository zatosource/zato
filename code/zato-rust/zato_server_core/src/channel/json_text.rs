//! JSON text of scalar values, written exactly as `json.dumps` of Python writes it.

use std::fmt::Write as _;

/// Text of a float that is not a number.
const NAN_TEXT: &str = "NaN";

/// Text of positive infinity.
const INFINITY_TEXT: &str = "Infinity";

/// Text of negative infinity.
const NEGATIVE_INFINITY_TEXT: &str = "-Infinity";

/// Lowest decimal point position at which `float.__repr__` still writes a float without an exponent.
const REPR_MIN_FIXED_DECIMAL_POINT: i32 = -3;

/// Highest decimal point position at which `float.__repr__` still writes a float without an exponent.
const REPR_MAX_FIXED_DECIMAL_POINT: i32 = 16;

/// First code point above the Basic Multilingual Plane.
const SUPPLEMENTARY_START: u32 = 0x1_0000;

/// First code point of the high surrogate range.
const HIGH_SURROGATE_START: u32 = 0xD800;

/// First code point of the low surrogate range.
const LOW_SURROGATE_START: u32 = 0xDC00;

/// Mask of the ten bits that each half of a surrogate pair holds.
const SURROGATE_BITS_MASK: u32 = 0x3FF;

/// Highest code point written to JSON text without an escape.
const MAX_PLAIN_CODE_POINT: u32 = 0x7E;

/// Lowest code point written to JSON text without an escape.
const MIN_PLAIN_CODE_POINT: u32 = 0x20;

/// Appends the text `float.__repr__` produces for a finite float.
pub fn push_float_repr(out: &mut String, value: f64) {
    // The shortest digits that read back as the same float, and the exponent of the first of them
    let scientific = format!("{value:e}");
    let (mantissa, exponent_text) = scientific.split_once('e').unwrap_or((scientific.as_str(), "0"));
    let exponent: i32 = exponent_text.parse().unwrap_or(0);

    let is_negative = mantissa.starts_with('-');
    let digits: String = mantissa.chars().filter(char::is_ascii_digit).collect();

    if is_negative {
        out.push('-');
    }

    // Zero has no first significant digit and is always written in the fixed form
    if digits == "0" {
        out.push_str("0.0");
        return;
    }

    let decimal_point = exponent + 1;

    if (REPR_MIN_FIXED_DECIMAL_POINT..=REPR_MAX_FIXED_DECIMAL_POINT).contains(&decimal_point) {
        push_fixed(out, &digits, decimal_point);
    } else {
        push_exponent(out, &digits, exponent);
    }
}

/// Appends digits in the fixed form, with at least one digit on each side of the decimal point.
fn push_fixed(out: &mut String, digits: &str, decimal_point: i32) {
    let digit_count = digits.len();

    // The decimal point is at or before the first digit
    let Ok(integer_length) = usize::try_from(decimal_point) else {
        let leading_zeros = usize::try_from(decimal_point.unsigned_abs()).unwrap_or_default();
        out.push_str("0.");
        out.extend(std::iter::repeat_n('0', leading_zeros));
        out.push_str(digits);
        return;
    };

    if integer_length == 0 {
        out.push_str("0.");
        out.push_str(digits);
        return;
    }

    // The decimal point is after the last digit, so zeros fill the integer part
    if integer_length >= digit_count {
        out.push_str(digits);
        out.extend(std::iter::repeat_n('0', integer_length - digit_count));
        out.push_str(".0");
        return;
    }

    let (integer_part, fraction_part) = digits.split_at(integer_length);
    out.push_str(integer_part);
    out.push('.');
    out.push_str(fraction_part);
}

/// Appends digits in the exponent form, with a signed exponent of at least two digits.
fn push_exponent(out: &mut String, digits: &str, exponent: i32) {
    let (first, rest) = digits.split_at(1);
    out.push_str(first);

    if !rest.is_empty() {
        out.push('.');
        out.push_str(rest);
    }

    let sign = if exponent < 0 { '-' } else { '+' };
    let _ = write!(out, "e{sign}{:02}", exponent.unsigned_abs());
}

/// Appends the JSON text of a float, which is the repr for a finite float and a name for the others.
pub fn push_json_float(out: &mut String, value: f64) {
    if value.is_nan() {
        out.push_str(NAN_TEXT);
    } else if value.is_infinite() {
        out.push_str(if value > 0.0 { INFINITY_TEXT } else { NEGATIVE_INFINITY_TEXT });
    } else {
        push_float_repr(out, value);
    }
}

/// Appends one code point as a `\u` escape with lowercase hex digits.
fn push_unicode_escape(out: &mut String, code_point: u32) {
    let _ = write!(out, "\\u{code_point:04x}");
}

/// Appends a code point the way `ensure_ascii` writes it, as a surrogate pair above the Basic Multilingual Plane.
fn push_escaped_code_point(out: &mut String, code_point: u32) {
    match code_point {
        0x22 => out.push_str("\\\""),
        0x5C => out.push_str("\\\\"),
        0x0A => out.push_str("\\n"),
        0x0D => out.push_str("\\r"),
        0x09 => out.push_str("\\t"),
        0x08 => out.push_str("\\b"),
        0x0C => out.push_str("\\f"),
        MIN_PLAIN_CODE_POINT..=MAX_PLAIN_CODE_POINT => {
            if let Some(character) = char::from_u32(code_point) {
                out.push(character);
            }
        }
        _ if code_point >= SUPPLEMENTARY_START => {
            let offset = code_point - SUPPLEMENTARY_START;
            push_unicode_escape(out, HIGH_SURROGATE_START | (offset >> 10));
            push_unicode_escape(out, LOW_SURROGATE_START | (offset & SURROGATE_BITS_MASK));
        }
        _ => push_unicode_escape(out, code_point),
    }
}

/// Whether a byte is written to JSON text as it is.
const fn is_plain_byte(byte: u8) -> bool {
    byte >= 0x20 && byte <= 0x7E && byte != b'"' && byte != b'\\'
}

/// Appends a string in double quotes, with every character outside of printable ASCII escaped.
pub fn push_json_string(out: &mut String, text: &str) {
    out.push('"');

    // Text without anything to escape is copied as a whole
    if text.bytes().all(is_plain_byte) {
        out.push_str(text);
    } else {
        for character in text.chars() {
            push_escaped_code_point(out, u32::from(character));
        }
    }

    out.push('"');
}

/// Appends code points in double quotes, which may include surrogates without a partner.
pub fn push_json_code_points(out: &mut String, code_points: &[u32]) {
    out.push('"');
    for code_point in code_points {
        push_escaped_code_point(out, *code_point);
    }
    out.push('"');
}
