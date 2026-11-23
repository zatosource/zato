//! The encoding of push bodies in three parts.
//!
//! The tests cover the equality of the joined parts with the compact JSON of the whole envelope, for any fields
//! and any position of the payload, the escaping of each class of characters, and an envelope of a payload alone.

use proptest::prelude::*;

use super::{EnvelopeFields, FieldValue, Fields, escape_payload, split_envelope};

/// The key under which the envelopes of the tests hold the payload.
const PAYLOAD_KEY: &str = "data";

/// The highest code point of the control characters that JSON strings escape.
const LAST_CONTROL_CHARACTER: u32 = 0x1F;

/// The line separator, which JSON leaves unescaped.
const LINE_SEPARATOR: char = '\u{2028}';

/// A character outside of the Basic Multilingual Plane.
const NON_BMP_CHARACTER: char = '\u{1F680}';

/// The most fields an envelope of the property test has.
const MAX_FIELD_COUNT: usize = 16;

/// Returns a payload with every character that JSON escapes and with characters that it leaves as they are.
fn payload_of_every_escape_class() -> String {
    let mut out = String::from("Order \"12345\" for C:\\customers\\john.smith - ");
    for code_point in 0..=LAST_CONTROL_CHARACTER {
        if let Some(character) = char::from_u32(code_point) {
            out.push(character);
        }
    }
    out.push(LINE_SEPARATOR);
    out.push(NON_BMP_CHARACTER);
    out.push_str("naïve café /path");
    out
}

/// Builds the envelope with the payload key at the given position among the fields.
fn envelope_fields(fields: &[(String, FieldValue)], position: usize) -> EnvelopeFields {
    let position = position.min(fields.len());
    let (before, after) = fields.split_at(position);

    EnvelopeFields {
        before: before.to_vec(),
        payload_key: PAYLOAD_KEY.to_owned(),
        after: after.to_vec(),
    }
}

/// Writes the compact JSON of the whole envelope, with the payload among the fields at the given position.
fn whole_envelope(fields: &[(String, FieldValue)], position: usize, data: &str) -> serde_json::Result<Vec<u8>> {
    let position = position.min(fields.len());
    let mut all = fields.to_vec();
    all.insert(position, (PAYLOAD_KEY.to_owned(), FieldValue::Text(data.to_owned())));

    let mut out = Vec::new();
    serde_json::to_writer(&mut out, &Fields(all))?;
    Ok(out)
}

/// Joins the prefix, the escaped payload and the suffix as the transport writes them.
fn joined_parts(fields: &EnvelopeFields, data: &str) -> serde_json::Result<Vec<u8>> {
    let (prefix, suffix) = split_envelope(fields)?;
    let escaped = escape_payload(data)?;

    let mut out = prefix;
    out.extend_from_slice(&escaped);
    out.extend_from_slice(&suffix);
    Ok(out)
}

/// Generates the value of one field.
fn field_value() -> impl Strategy<Value = FieldValue> {
    prop_oneof![
        Just(FieldValue::Null),
        any::<i64>().prop_map(FieldValue::Int),
        any::<String>().prop_map(FieldValue::Text),
    ]
}

/// Generates the fields of an envelope other than its payload.
fn envelope_field_list() -> impl Strategy<Value = Vec<(String, FieldValue)>> {
    let key = any::<String>().prop_filter("the payload key is placed by the test", |key| key != PAYLOAD_KEY);
    prop::collection::vec((key, field_value()), 0..MAX_FIELD_COUNT)
}

proptest! {
    #[test]
    fn joined_parts_equal_the_whole_envelope(
        fields in envelope_field_list(),
        position in 0..=MAX_FIELD_COUNT,
        data in any::<String>(),
    ) {
        let envelope = envelope_fields(&fields, position);

        let joined = joined_parts(&envelope, &data).map_err(|err| TestCaseError::fail(err.to_string()))?;
        let whole = whole_envelope(&fields, position, &data).map_err(|err| TestCaseError::fail(err.to_string()))?;

        prop_assert_eq!(joined, whole);
    }
}

#[test]
fn payload_first_middle_and_last() -> serde_json::Result<()> {
    let fields = vec![
        ("msg_id".to_owned(), FieldValue::Text("zpsm.0192d3a1b2c3".to_owned())),
        ("priority".to_owned(), FieldValue::Int(5)),
        ("expiration_time_iso".to_owned(), FieldValue::Null),
    ];
    let data = payload_of_every_escape_class();

    // The payload goes before every field, between two of them and after every one of them
    for position in [0, 1, fields.len()] {
        let envelope = envelope_fields(&fields, position);
        assert_eq!(joined_parts(&envelope, &data)?, whole_envelope(&fields, position, &data)?);
    }

    Ok(())
}

#[test]
fn every_escape_class() -> serde_json::Result<()> {
    assert_eq!(escape_payload("")?, br#""""#);
    assert_eq!(escape_payload("\"")?, br#""\"""#);
    assert_eq!(escape_payload("\\")?, br#""\\""#);
    assert_eq!(escape_payload("\n\r\t")?, br#""\n\r\t""#);
    assert_eq!(escape_payload("\u{0}\u{1F}")?, br#""\u0000\u001f""#);
    assert_eq!(escape_payload("/")?, br#""/""#);

    // The line separator and characters outside of the Basic Multilingual Plane are written as UTF-8
    let unescaped = format!("{LINE_SEPARATOR}{NON_BMP_CHARACTER}");
    let mut expected = vec![b'"'];
    expected.extend_from_slice(unescaped.as_bytes());
    expected.push(b'"');
    assert_eq!(escape_payload(&unescaped)?, expected);

    // Every control character is escaped, so the escaped payload holds none
    let escaped = escape_payload(&payload_of_every_escape_class())?;
    let last_control_byte = u8::try_from(LAST_CONTROL_CHARACTER).unwrap_or(u8::MAX);
    assert!(escaped.iter().all(|byte| *byte > last_control_byte));

    Ok(())
}

#[test]
fn envelope_of_the_payload_alone() -> serde_json::Result<()> {
    let envelope = envelope_fields(&[], 0);
    let (prefix, suffix) = split_envelope(&envelope)?;

    assert_eq!(prefix, br#"{"data":"#);
    assert_eq!(suffix, b"}");

    Ok(())
}
