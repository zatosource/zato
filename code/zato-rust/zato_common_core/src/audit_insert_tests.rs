//! The conversions of the audit writer against the values that the Python path stores.
//!
//! The tests cover the text of a time column, the compressed form of a payload,
//! the digest of a payload, the capped text of an attribute value and the exception classes of the Python driver that the errors of `SQLite` are raised as.

use std::fmt::Write as _;

use blake2::digest::consts::U16;
use blake2::{Blake2b, Digest};
use rusqlite::ffi;

use super::{ATTR_FALSE, ATTR_TRUE, ATTR_VALUE_MAX_LEN, UtcTime, capped_attr_text, compress_text, payload_digest, sqlite_error_class};

/// A text with characters outside of ASCII, whose length in characters differs from its length in bytes.
const TEXT_NON_ASCII: &str = "Zamówienie dla Marii Johnson – 5,50 € Jürgen";

/// A text of ASCII characters.
const TEXT_ASCII: &str = "Order ORD-0042 for Maria Johnson";

/// The line that the large text repeats, and how many times it repeats it, for a text of over 1 MB.
const LARGE_LINE: &str = "Invoice line for Maria Johnson 42.50 USD\n";
const LARGE_REPEAT: usize = 25_000;

/// Returns the hexadecimal blake2b digest of 16 bytes of some bytes, as `hashlib.blake2b(digest_size=16)` returns it.
fn hex_digest(data: &[u8]) -> String {
    let digest = Blake2b::<U16>::digest(data);
    let mut out = String::new();

    for byte in digest {
        // Writing to a string cannot fail
        write!(out, "{byte:02x}").ok();
    }

    out
}

/// Returns the bytes of a hexadecimal text.
fn from_hex(text: &str) -> Vec<u8> {
    let mut out = Vec::new();
    let mut index: usize = 0;

    while let Some(pair) = text.get(index..index.saturating_add(2)) {
        out.push(u8::from_str_radix(pair, 16).unwrap_or_default());
        index = index.saturating_add(2);
    }

    out
}

#[test]
fn formats_a_time_as_its_column_stores_it() {
    let time = UtcTime {
        year: 2026,
        month: 3,
        day: 1,
        hour: 9,
        minute: 5,
        second: 7,
        microsecond: 42,
    };

    assert_eq!(time.to_column_text(), "2026-03-01 09:05:07.000042");
}

#[test]
fn formats_the_last_microsecond_of_a_year() {
    let time = UtcTime {
        year: 2026,
        month: 12,
        day: 31,
        hour: 23,
        minute: 59,
        second: 59,
        microsecond: 999_999,
    };

    assert_eq!(time.to_column_text(), "2026-12-31 23:59:59.999999");
}

#[test]
fn compresses_as_zlib_at_level_one() {
    let cases = [
        ("", "7801030000000001"),
        (
            TEXT_ASCII,
            "7801f32f4a492d52f00f72d1353030315248cb2f52f04d2cca4c54f0cacfc82bcecf0300a25f0a65",
        ),
        (
            TEXT_NON_ASCII,
            "78018b4acc3dbcb93c33352f335521252751c137b1283353c12b3f23af383f4fe151c36405531d530385474d6b14bc0eef294a4fcd030000fe1442",
        ),
    ];

    for (text, expected) in cases {
        let compressed = compress_text(text).ok();
        assert_eq!(compressed, Some(from_hex(expected)), "{text}");
    }
}

#[test]
fn compresses_a_large_text_as_zlib_at_level_one() {
    let text = LARGE_LINE.repeat(LARGE_REPEAT);
    let compressed = compress_text(&text).ok().unwrap_or_default();

    assert_eq!(text.len(), 1_025_000);
    assert_eq!(compressed.len(), 7034);
    assert_eq!(hex_digest(&compressed), "41c99c4cd5f46015857afcddc83631a5");
}

#[test]
fn digests_a_payload_as_blake2b_of_sixteen_bytes() {
    let large = LARGE_LINE.repeat(LARGE_REPEAT);

    assert_eq!(payload_digest(TEXT_ASCII).as_deref(), Some("014db279f6fb94bb67bbf3dfdf170df7"));
    assert_eq!(payload_digest(TEXT_NON_ASCII).as_deref(), Some("487bceea365abfd65961332e0c256f5e"));
    assert_eq!(payload_digest(&large).as_deref(), Some("a11720082645484655eead3e50efe927"));
}

#[test]
fn stores_no_digest_of_an_empty_payload() {
    assert_eq!(payload_digest(""), None);
}

#[test]
fn stores_a_boolean_attribute_as_python_prints_it() {
    assert_eq!(ATTR_TRUE, "True");
    assert_eq!(ATTR_FALSE, "False");
}

#[test]
fn caps_the_text_of_an_attribute_by_characters() {
    let note = "Order note for Jane Doe ".repeat(20);
    let capped = capped_attr_text(&note);

    assert_eq!(note.chars().count(), 480);
    assert_eq!(capped.chars().count(), ATTR_VALUE_MAX_LEN);
    assert_eq!(capped, note.chars().take(ATTR_VALUE_MAX_LEN).collect::<String>());
}

#[test]
fn caps_a_text_outside_of_ascii_on_a_character_boundary() {
    let text = "Café order for María Johnson ".repeat(30);
    let capped = capped_attr_text(&text);

    assert_eq!(capped.chars().count(), ATTR_VALUE_MAX_LEN);
    assert!(text.starts_with(&capped));
}

#[test]
fn leaves_a_short_attribute_text_as_it_is() {
    assert_eq!(capped_attr_text(TEXT_NON_ASCII), TEXT_NON_ASCII);
}

/// Returns the error of `SQLite` with a result code, as a statement that failed with it returns it.
fn sqlite_failure(code: i32) -> rusqlite::Error {
    rusqlite::Error::SqliteFailure(ffi::Error::new(code), None)
}

#[test]
fn raises_a_constraint_violation_as_an_integrity_error() {
    assert_eq!(
        sqlite_error_class(&sqlite_failure(ffi::SQLITE_CONSTRAINT_NOTNULL)),
        "IntegrityError"
    );
}

#[test]
fn raises_a_type_mismatch_as_an_integrity_error() {
    assert_eq!(sqlite_error_class(&sqlite_failure(ffi::SQLITE_MISMATCH)), "IntegrityError");
}

#[test]
fn raises_a_value_too_big_as_a_data_error() {
    assert_eq!(sqlite_error_class(&sqlite_failure(ffi::SQLITE_TOOBIG)), "DataError");
}

#[test]
fn raises_a_corrupt_database_as_a_database_error() {
    assert_eq!(sqlite_error_class(&sqlite_failure(ffi::SQLITE_CORRUPT)), "DatabaseError");
}

#[test]
fn raises_a_locked_database_as_an_operational_error() {
    assert_eq!(sqlite_error_class(&sqlite_failure(ffi::SQLITE_BUSY)), "OperationalError");
}
