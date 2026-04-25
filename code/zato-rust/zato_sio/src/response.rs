use pyo3::prelude::*;
use pyo3::types::PyDict;
use crate::payload::Payload;

/// Shorthand for a heap-allocated Python object reference.
type PyObject = Py<PyAny>;

/// Wraps HTTP response metadata and payload for a Zato service invocation.
///
/// Exposes result status, headers, content type, and the serialized payload
/// to Python callers via `PyO3` getter/setter attributes.
#[pyclass]
pub struct Response {
    /// `ZATO_OK` / `ZATO_ERROR` result indicator.
    #[pyo3(get, set)]
    pub result: String,

    /// Human-readable details accompanying the result code.
    #[pyo3(get, set)]
    pub result_details: String,

    /// Serialized payload body, either a raw Python object or a `Payload` instance.
    payload_inner: PyObject,

    /// Optional content encoding applied to the response body (e.g. gzip).
    #[pyo3(get, set)]
    pub content_encoding: Option<String>,

    /// Correlation identifier carried through the service invocation chain.
    #[pyo3(get, set)]
    pub cid: Option<String>,

    /// Wire format of the payload (e.g. "json", "xml").
    #[pyo3(get, set)]
    pub data_format: Option<String>,

    /// HTTP response headers as a Python dict.
    #[pyo3(get, set)]
    pub headers: PyObject,

    /// HTTP status code returned to the caller.
    #[pyo3(get, set)]
    pub status_code: i32,

    /// HTTP status message accompanying the status code.
    #[pyo3(get, set)]
    pub status_message: String,

    /// Reference to the SIO processor attached to the service, if any.
    sio: Option<PyObject>,

    /// Raw content-type string, managed through a custom getter/setter pair.
    content_type_inner: String,

    /// Whether the content type was explicitly changed by user code.
    #[pyo3(get, set)]
    pub content_type_changed: bool,

    /// Whether this response carries SIO-declared output elements.
    #[pyo3(get)]
    pub has_sio_output: bool,
}

#[pymethods]
impl Response {

    /// Creates a new response with default 200/OK status and empty payload.
    #[new]
    fn new(py: Python<'_>) -> PyResult<Self> {
        let headers = PyDict::new(py);
        Ok(Self {
            result: "ZATO_OK".to_string(),
            result_details: String::new(),
            payload_inner: "".into_pyobject(py)?.into_any().unbind(),
            content_encoding: None,
            cid: None,
            data_format: None,
            headers: headers.into_any().unbind(),
            status_code: 200,
            status_message: "OK".to_string(),
            sio: None,
            content_type_inner: "text/plain".to_string(),
            content_type_changed: false,
            has_sio_output: false,
        })
    }

    /// Initializes the response with a correlation id, SIO processor, and data format,
    /// building a `Payload` from output element names when SIO output is declared.
    fn init(&mut self, py: Python<'_>, cid: Option<String>, sio: Option<&Bound<'_, PyAny>>, data_format: Option<String>) -> PyResult<()> {
        self.cid = cid;
        self.data_format.clone_from(&data_format);

        if let Some(sio_obj) = sio {
            let is_dataclass = sio_obj.getattr("is_dataclass")
                .and_then(|val| val.extract::<bool>())
                .unwrap_or(false);

            if !is_dataclass {
                let has_output = sio_obj.getattr("has_output_declared")
                    .and_then(|val| val.extract::<bool>())
                    .unwrap_or(false);

                if has_output {
                    let output_names = sio_obj.getattr("all_output_elem_names")?
                        .extract::<Vec<String>>()?;

                    let payload = Payload::create(
                        output_names,
                        self.cid.clone(),
                        data_format,
                    );
                    self.payload_inner = Py::new(py, payload)?.into_any();
                    self.has_sio_output = true;
                }
            }

            self.sio = Some(sio_obj.clone().unbind());
        }

        Ok(())
    }

    /// Returns the current content-type header value.
    #[getter]
    fn get_content_type(&self) -> &str {
        &self.content_type_inner
    }

    /// Sets the content-type header and marks it as explicitly changed.
    #[setter]
    fn set_content_type(&mut self, value: String) {
        self.content_type_inner = value;
        self.content_type_changed = true;
    }

    /// Returns a reference to the inner payload Python object.
    #[getter]
    fn get_payload(&self, py: Python<'_>) -> PyObject {
        self.payload_inner.clone_ref(py)
    }

    /// Assigns a new payload, dispatching to the appropriate storage strategy
    /// based on the value type and whether SIO output is declared.
    #[setter]
    fn set_payload(&mut self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if value.is_instance_of::<pyo3::types::PyDict>()
            || value.is_instance_of::<pyo3::types::PyString>()
            || value.is_instance_of::<pyo3::types::PyBytes>()
        {
            self.payload_inner = value.clone().unbind();
        } else if self.has_sio_output {
            let payload = self.payload_inner.bind(py);
            payload.call_method1("set_payload_attrs", (value,))?;
        } else if !value.is_none() {
            if let Ok(to_dict) = value.call_method0("to_dict") {
                self.payload_inner = to_dict.unbind();
            } else if let Ok(to_json) = value.call_method0("to_json") {
                self.payload_inner = to_json.unbind();
            } else {
                self.payload_inner = value.clone().unbind();
            }
        }

        Ok(())
    }

    /// Returns the length of the inner payload, or 0 if the payload has no length.
    fn __len__(&self, py: Python<'_>) -> usize {
        let payload = self.payload_inner.bind(py);
        payload.len().unwrap_or(0)
    }
}
