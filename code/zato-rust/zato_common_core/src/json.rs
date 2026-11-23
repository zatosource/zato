//! Encoding of the responses of pub/sub pulls and of the bodies of pub/sub pushes into JSON.
//!
//! The JSON is written with the GIL released. The payload of each message is the text that the publisher sent and the database stored. In a pull response,
//! a payload that is valid JSON is placed as it stands, and any other payload is placed as a JSON string. In a push body,
//! the payload is always placed as a JSON string. The fields are copied while the GIL is held, and the payloads
//! are validated and the JSON is written after the GIL is released.
//!
//! A push body is encoded in three parts. The payload is escaped once per message and shared by every subscriber,
//! and only the envelope fields around it, which carry the attempt of each delivery, are encoded for each subscriber.

use pyo3::exceptions::{PyKeyError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyInt, PyList, PyString};
use serde::ser::{Serialize, SerializeMap, SerializeStruct, Serializer};
use serde_json::value::RawValue;

/// The number of bytes that the two quotes add to a payload written as a JSON string.
const PAYLOAD_QUOTES_LEN: usize = 2;

/// The value of one field of a pulled message's meta or of a push envelope.
#[derive(Clone, Debug)]
enum FieldValue {
    /// A field without a value, such as a message without an expiration time.
    Null,

    /// A numeric field, such as the size or the priority.
    Int(i64),

    /// A text field, such as the topic name, a timestamp or the payload of a push.
    Text(String),
}

impl FieldValue {
    /// Copies the value of one field.
    fn from_python(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        if value.is_none() {
            return Ok(Self::Null);
        }

        if value.is_instance_of::<PyInt>() {
            return Ok(Self::Int(value.extract()?));
        }

        if let Ok(text) = value.cast::<PyString>() {
            return Ok(Self::Text(text.to_str()?.to_owned()));
        }

        let type_name = value.get_type().name()?;
        Err(PyTypeError::new_err(format!("Unsupported type of a message field `{type_name}`")))
    }
}

impl Serialize for FieldValue {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        match self {
            Self::Null => serializer.serialize_unit(),
            Self::Int(number) => serializer.serialize_i64(*number),
            Self::Text(text) => serializer.serialize_str(text),
        }
    }
}

/// The fields of a flat dict, in the order in which the backend set them.
struct Fields(Vec<(String, FieldValue)>);

impl Fields {
    /// Copies the fields of a flat dict whose keys are strings.
    fn from_python(dict: &Bound<'_, PyDict>) -> PyResult<Self> {
        let mut fields = Vec::with_capacity(dict.len());
        for (key, value) in dict.iter() {
            let key: String = key.extract()?;
            fields.push((key, FieldValue::from_python(&value)?));
        }
        Ok(Self(fields))
    }
}

impl Serialize for Fields {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        let mut map = serializer.serialize_map(Some(self.0.len()))?;
        for (key, value) in &self.0 {
            map.serialize_entry(key, value)?;
        }
        map.end()
    }
}

/// The text of a payload as the database stored it.
struct Payload(String);

impl Serialize for Payload {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        // A payload that parses as JSON is written as it stands, without being decoded into values
        #[expect(
            clippy::disallowed_methods,
            reason = "the payload is validated as JSON in place and borrowed into the response, no value crosses the Python boundary as JSON"
        )]
        let parsed = serde_json::from_str::<&RawValue>(&self.0);
        match parsed {
            Ok(raw) => raw.serialize(serializer),
            Err(_) => serializer.serialize_str(&self.0),
        }
    }
}

/// One message of a pull response.
struct PulledMessage {
    /// The payload of the message.
    data: Payload,

    /// The meta fields of the message.
    meta: Fields,
}

impl PulledMessage {
    /// Copies a message formatted by the backend, a dict with the payload text under `data` and the meta fields under `meta`.
    fn from_python(message: &Bound<'_, PyAny>) -> PyResult<Self> {
        let message = message.cast::<PyDict>()?;

        let data_item = message.as_any().get_item("data")?;
        let data: String = data_item.extract()?;

        let meta_item = message.as_any().get_item("meta")?;
        let meta = Fields::from_python(meta_item.cast::<PyDict>()?)?;

        Ok(Self { data: Payload(data), meta })
    }
}

impl Serialize for PulledMessage {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        let mut state = serializer.serialize_struct("PulledMessage", 2)?;
        state.serialize_field("data", &self.data)?;
        state.serialize_field("meta", &self.meta)?;
        state.end()
    }
}

/// The response of a pull.
struct PullResponse {
    /// The correlation ID of the request.
    cid: String,

    /// The messages that the pull leased.
    messages: Vec<PulledMessage>,

    /// The HTTP status of the response.
    status: String,
}

impl Serialize for PullResponse {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        let mut state = serializer.serialize_struct("PullResponse", 5)?;
        state.serialize_field("is_ok", &true)?;
        state.serialize_field("cid", &self.cid)?;
        state.serialize_field("messages", &self.messages)?;
        state.serialize_field("message_count", &self.messages.len())?;
        state.serialize_field("status", &self.status)?;
        state.end()
    }
}

/// Encodes the response of a pub/sub pull into JSON text.
///
/// The fields are copied while the GIL is held, and the response is written after the GIL is released.
#[pyfunction]
pub fn encode_pull_response(py: Python<'_>, cid: String, status: String, messages: &Bound<'_, PyList>) -> PyResult<String> {
    let messages: PyResult<Vec<PulledMessage>> = messages.iter().map(|message| PulledMessage::from_python(&message)).collect();
    let response = PullResponse {
        cid,
        messages: messages?,
        status,
    };

    // The payloads are validated and the text is written without the GIL, so the other threads of the interpreter run in the meantime
    #[expect(
        clippy::disallowed_methods,
        reason = "the JSON text is the HTTP response body itself, not an intermediate format between Python and Rust"
    )]
    let encoded = py.detach(|| serde_json::to_string(&response));

    encoded.map_err(|err| PyValueError::new_err(err.to_string()))
}

/// The fields of a push envelope on either side of its payload, in the order in which the backend set them.
struct EnvelopeFields {
    /// The fields that precede the payload.
    before: Vec<(String, FieldValue)>,

    /// The key under which the envelope carries the payload.
    payload_key: String,

    /// The fields that follow the payload.
    after: Vec<(String, FieldValue)>,
}

impl EnvelopeFields {
    /// Copies every field of a push envelope except its payload, which is never copied.
    fn from_python(envelope: &Bound<'_, PyDict>, payload_key: &str) -> PyResult<Self> {
        let mut before = Vec::with_capacity(envelope.len());
        let mut after = Vec::new();
        let mut has_payload = false;

        for (key, value) in envelope.iter() {
            let key: String = key.extract()?;

            // The payload is escaped once per message by escape_push_payload, the envelope holds only its position
            if key == payload_key {
                has_payload = true;
                continue;
            }

            let field = (key, FieldValue::from_python(&value)?);
            if has_payload {
                after.push(field);
            } else {
                before.push(field);
            }
        }

        // An envelope without a payload has no position to splice the escaped payload into
        if !has_payload {
            return Err(PyKeyError::new_err(payload_key.to_owned()));
        }

        Ok(Self {
            before,
            payload_key: payload_key.to_owned(),
            after,
        })
    }
}

/// Writes one key and its value as a compact JSON object member.
fn write_member(out: &mut Vec<u8>, key: &str, value: &FieldValue) -> serde_json::Result<()> {
    serde_json::to_writer(&mut *out, key)?;
    out.push(b':');
    serde_json::to_writer(&mut *out, value)
}

/// Writes the compact JSON of a push envelope as the bytes that precede its payload and the bytes that follow it.
///
/// The prefix, the payload escaped as a JSON string and the suffix, joined, are byte for byte
/// the compact JSON object of all the fields in their original order.
fn split_envelope(fields: &EnvelopeFields) -> serde_json::Result<(Vec<u8>, Vec<u8>)> {
    let mut prefix = vec![b'{'];
    for (key, value) in &fields.before {
        write_member(&mut prefix, key, value)?;
        prefix.push(b',');
    }
    serde_json::to_writer(&mut prefix, &fields.payload_key)?;
    prefix.push(b':');

    let mut suffix = Vec::new();
    for (key, value) in &fields.after {
        suffix.push(b',');
        write_member(&mut suffix, key, value)?;
    }
    suffix.push(b'}');

    Ok((prefix, suffix))
}

/// Writes the payload of a push as a JSON string, with its quotes and escapes.
fn escape_payload(data: &str) -> serde_json::Result<Vec<u8>> {
    let mut escaped = Vec::with_capacity(data.len().saturating_add(PAYLOAD_QUOTES_LEN));
    serde_json::to_writer(&mut escaped, data)?;
    Ok(escaped)
}

/// Escapes the payload of a pub/sub push into a JSON string, the part of the body that every subscriber of a message shares.
///
/// The payload is borrowed from the Python string without a copy, and it is escaped after the GIL is released.
#[pyfunction]
pub fn escape_push_payload<'py>(py: Python<'py>, data: &Bound<'py, PyString>) -> PyResult<Bound<'py, PyBytes>> {
    let text = data.to_str()?;

    // The payload is escaped without the GIL, so the other threads of the interpreter run in the meantime
    let escaped = py.detach(|| escape_payload(text));
    let escaped = escaped.map_err(|err| PyValueError::new_err(err.to_string()))?;

    Ok(PyBytes::new(py, &escaped))
}

/// Encodes the envelope of a pub/sub push, a flat dict of text, integers and `None`, into the bytes around its payload.
///
/// Returns the prefix, which ends with the payload key and its colon, and the suffix, which closes the object.
/// The envelope without its payload is small, so it is encoded while the GIL is held.
#[pyfunction]
pub fn encode_push_envelope_parts<'py>(
    py: Python<'py>,
    envelope: &Bound<'py, PyDict>,
    payload_key: &str,
) -> PyResult<(Bound<'py, PyBytes>, Bound<'py, PyBytes>)> {
    let fields = EnvelopeFields::from_python(envelope, payload_key)?;
    let (prefix, suffix) = split_envelope(&fields).map_err(|err| PyValueError::new_err(err.to_string()))?;

    Ok((PyBytes::new(py, &prefix), PyBytes::new(py, &suffix)))
}

#[cfg(test)]
#[path = "json_tests.rs"]
mod tests;
