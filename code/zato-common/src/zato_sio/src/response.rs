use pyo3::prelude::*;
use pyo3::types::PyDict;
use crate::payload::Payload;

type PyObject = Py<PyAny>;

#[pyclass]
pub struct Response {
    #[pyo3(get, set)]
    pub result: String,

    #[pyo3(get, set)]
    pub result_details: String,

    payload_inner: PyObject,

    #[pyo3(get, set)]
    pub content_encoding: Option<String>,

    #[pyo3(get, set)]
    pub cid: Option<String>,

    #[pyo3(get, set)]
    pub data_format: Option<String>,

    #[pyo3(get, set)]
    pub headers: PyObject,

    #[pyo3(get, set)]
    pub status_code: i32,

    #[pyo3(get, set)]
    pub status_message: String,

    sio: Option<PyObject>,

    content_type_inner: String,

    #[pyo3(get, set)]
    pub content_type_changed: bool,

    #[pyo3(get)]
    pub _has_sio_output: bool,
}

#[pymethods]
impl Response {

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
            _has_sio_output: false,
        })
    }

    fn init(&mut self, py: Python<'_>, cid: Option<String>, sio: Option<&Bound<'_, PyAny>>, data_format: Option<String>) -> PyResult<()> {
        self.cid = cid;
        self.data_format = data_format.clone();

        if let Some(sio_obj) = sio {
            let is_dataclass = sio_obj.getattr("is_dataclass")
                .and_then(|v| v.extract::<bool>())
                .unwrap_or(false);

            if !is_dataclass {
                let has_output = sio_obj.getattr("has_output_declared")
                    .and_then(|v| v.extract::<bool>())
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
                    self._has_sio_output = true;
                }
            }

            self.sio = Some(sio_obj.clone().unbind());
        }

        Ok(())
    }

    #[getter]
    fn get_content_type(&self) -> &str {
        &self.content_type_inner
    }

    #[setter]
    fn set_content_type(&mut self, value: String) {
        self.content_type_inner = value;
        self.content_type_changed = true;
    }

    #[getter]
    fn get_payload(&self, py: Python<'_>) -> PyObject {
        self.payload_inner.clone_ref(py)
    }

    #[setter]
    fn set_payload(&mut self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if value.is_instance_of::<pyo3::types::PyDict>() {
            self.payload_inner = value.clone().unbind();
        } else if value.is_instance_of::<pyo3::types::PyString>() || value.is_instance_of::<pyo3::types::PyBytes>() {
            self.payload_inner = value.clone().unbind();
        } else if self._has_sio_output {
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

    fn __len__(&self, py: Python<'_>) -> PyResult<usize> {
        let payload = self.payload_inner.bind(py);
        match payload.len() {
            Ok(n) => Ok(n),
            Err(_) => Ok(0),
        }
    }
}
