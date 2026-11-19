//! Encoding of the responses of pub/sub pulls and of the bodies of pub/sub pushes into JSON with the GIL released.
//!
//! The payload of each message is the text that the publisher sent and the database stored. In a pull response,
//! a payload that is valid JSON is placed as it stands, and any other payload is placed as a JSON string. In a push body,
//! the payload is always placed as a JSON string. The fields are copied while the GIL is held, and the payloads
//! are validated and the JSON is written after the GIL is released.

use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyInt, PyList, PyString};
use serde::ser::{Serialize, SerializeMap, SerializeStruct, Serializer};
use serde_json::value::RawValue;

/// The value of one field of a pulled message's meta or of a push envelope.
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
        match serde_json::from_str::<&RawValue>(&self.0) {
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
    let encoded = py.detach(|| serde_json::to_string(&response));

    encoded.map_err(|err| PyValueError::new_err(err.to_string()))
}

/// Encodes the envelope of a pub/sub push, a flat dict of text, integers and `None`, into the UTF-8 body of the request.
///
/// The fields are copied while the GIL is held, and the body is written after the GIL is released.
#[pyfunction]
pub fn encode_push_envelope<'py>(py: Python<'py>, envelope: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyBytes>> {
    let fields = Fields::from_python(envelope)?;

    // The payload is escaped and the body is written without the GIL, so the other threads of the interpreter run in the meantime
    let encoded = py.detach(|| serde_json::to_vec(&fields));
    let body = encoded.map_err(|err| PyValueError::new_err(err.to_string()))?;

    Ok(PyBytes::new(py, &body))
}
