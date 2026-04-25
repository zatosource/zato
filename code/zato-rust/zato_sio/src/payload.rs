use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use std::collections::HashMap;

/// Shorthand alias for a heap-allocated Python object reference.
type PyObject = Py<PyAny>;

/// Manages the output data of a Zato service response.
///
/// Supports both dict and list output modes - dict mode stores named
/// attributes while list mode collects ordered result rows. Handles
/// serialisation via `getvalue` and optional `_meta` envelope wrapping.
#[pyclass]
pub struct Payload {
    /// Declared output element names that govern which attributes are extracted.
    output_elem_names: Vec<String>,
    /// Named attributes for dict-mode output.
    user_attrs_dict: HashMap<String, PyObject>,
    /// Ordered items for list-mode output.
    user_attrs_list: Vec<PyObject>,
    /// Whether the payload is operating in list output mode.
    is_list_output: bool,

    /// Optional Zato metadata attached to the response (e.g. search pagination).
    #[pyo3(get, set)]
    pub zato_meta: Option<PyObject>,

    /// Correlation ID of the current request/response.
    #[pyo3(get)]
    pub cid: Option<String>,

    /// Data format hint (e.g. `"dict"`) controlling serialisation behaviour.
    #[pyo3(get)]
    pub data_format: Option<String>,
}

impl Payload {
    /// Creates a new `Payload` with the given output element names and optional metadata fields.
    pub fn create(
        output_elem_names: Vec<String>,
        cid: Option<String>,
        data_format: Option<String>,
    ) -> Self {
        Self {
            output_elem_names,
            user_attrs_dict: HashMap::new(),
            user_attrs_list: Vec::new(),
            is_list_output: false,
            zato_meta: None,
            cid,
            data_format,
        }
    }
}

#[pymethods]
impl Payload {

    /// Constructs a `Payload` from Python with declared output element names.
    #[new]
    fn new(
        output_elem_names: Vec<String>,
        cid: Option<String>,
        data_format: Option<String>,
    ) -> Self {
        Self {
            output_elem_names,
            user_attrs_dict: HashMap::new(),
            user_attrs_list: Vec::new(),
            is_list_output: false,
            zato_meta: None,
            cid,
            data_format,
        }
    }

    /// Replaces all payload attributes from the given Python value (dict, list, or object with `to_zato`).
    fn set_payload_attrs(&mut self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        self.user_attrs_dict.clear();
        self.user_attrs_list.clear();
        self.is_list_output = false;

        if value.is_instance_of::<PyDict>() {
            let dict_ref: &Bound<'_, PyDict> = value.cast()?;
            self.extract_from_dict(py, dict_ref)?;
        } else if value.is_instance_of::<PyList>() {
            self.is_list_output = true;
            for item in value.try_iter()? {
                let item = item?;
                let py_dict = PyDict::new(py);
                if item.is_instance_of::<PyDict>() {
                    let dict_ref: &Bound<'_, PyDict> = item.cast()?;
                    let extracted = self.extract_dict_attrs(py, dict_ref)?;
                    for (key_name, val) in &extracted {
                        py_dict.set_item(key_name, val.bind(py))?;
                    }
                } else {
                    let extracted = self.extract_obj_attrs(py, &item)?;
                    for (key_name, val) in &extracted {
                        py_dict.set_item(key_name, val.bind(py))?;
                    }
                }
                self.user_attrs_list.push(py_dict.into_any().unbind());
            }
        } else if let Ok(to_zato) = value.getattr("to_zato") {
            let converted = to_zato.call0()?;
            return self.set_payload_attrs(py, &converted);
        } else {
            for name in &self.output_elem_names {
                let py_name = PyString::new(py, name);
                if let Ok(val) = value.getattr(&py_name) {
                    self.user_attrs_dict.insert(name.clone(), val.unbind());
                }
            }
        }

        Ok(())
    }

    /// Serialises and returns the payload value, optionally as JSON.
    #[pyo3(signature = (serialize=None, force_dict_serialisation=true))]
    fn getvalue(&self, py: Python<'_>, serialize: Option<bool>, force_dict_serialisation: bool) -> PyResult<PyObject> {
        let do_serialize = match serialize {
            Some(false) => false,
            Some(true) => true,
            None => self.data_format.as_deref() == Some("dict") && force_dict_serialisation,
        };

        if let Some(ref meta) = self.zato_meta {
            let meta_bound = meta.bind(py);
            let search = meta_bound.call_method1("get", ("search",))?;

            if !search.is_none() {
                let output = self.build_output_value(py)?;

                let envelope = PyDict::new(py);
                envelope.set_item("data", &output)?;
                envelope.set_item("_meta", &search)?;

                if do_serialize {
                    let json_mod = py.import("zato.common.json_internal")?;
                    let result = json_mod.call_method1("dumps", (envelope,))?;
                    return Ok(result.unbind());
                }
                return Ok(envelope.into_any().unbind());
            }
        }

        let value = self.build_output_value(py)?;
        if do_serialize {
            let json_mod = py.import("zato.common.json_internal")?;
            let result = json_mod.call_method1("dumps", (&value,))?;
            Ok(result.unbind())
        } else {
            Ok(value.unbind())
        }
    }

    /// Returns `true` if the payload contains any user-set attributes (dict or list).
    fn has_data(&self) -> bool {
        !self.user_attrs_dict.is_empty() || !self.user_attrs_list.is_empty()
    }

    /// Appends a value to the list-mode output, extracting declared output elements.
    fn append(&mut self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if self.output_elem_names.is_empty() {
            self.user_attrs_list.push(value.clone().unbind());
        } else if let Ok(dict_ref) = value.cast::<PyDict>() {
            let filtered = PyDict::new(py);
            for name in &self.output_elem_names {
                match dict_ref.get_item(name)? {
                    Some(val) => filtered.set_item(name, val)?,
                    None => filtered.set_item(name, py.None())?,
                }
            }
            self.user_attrs_list.push(filtered.into_any().unbind());
        } else {
            let filtered = PyDict::new(py);
            for name in &self.output_elem_names {
                let py_name = PyString::new(py, name);
                match value.getattr(&py_name) {
                    Ok(val) => filtered.set_item(name, val)?,
                    Err(_) => filtered.set_item(name, py.None())?,
                }
            }
            self.user_attrs_list.push(filtered.into_any().unbind());
        }
        self.is_list_output = true;
        Ok(())
    }

    /// Sets a named attribute or `zato_meta` on the payload.
    fn __setattr__(&mut self, key: String, value: PyObject) {
        if key == "zato_meta" {
            self.zato_meta = Some(value);
        } else {
            self.user_attrs_dict.insert(key, value);
        }
    }

    /// Returns the value for the given attribute key, raising `KeyError` if absent.
    fn __getattr__(&self, py: Python<'_>, key: &str) -> PyResult<PyObject> {
        self.user_attrs_dict.get(key).map_or_else(
            || Err(pyo3::exceptions::PyKeyError::new_err(
                format!("No such key `{}` among `{:?}`", key, self.user_attrs_dict.keys().collect::<Vec<_>>())
            )),
            |val| Ok(val.clone_ref(py)),
        )
    }

    /// Sets an item by key (string) or replaces a slice range (for list-mode output).
    fn __setitem__(&mut self, py: Python<'_>, key: &Bound<'_, PyAny>, value: PyObject) -> PyResult<()> {
        if key.is_instance_of::<pyo3::types::PySlice>() {
            let slice: &Bound<'_, pyo3::types::PySlice> = key.cast()?;

            #[expect(clippy::cast_possible_wrap, reason = "Python list length is within isize range")]
            let list_len = self.user_attrs_list.len() as isize;

            let indices = slice.indices(list_len)?;

            #[expect(clippy::cast_sign_loss, reason = "Python normalizes slice indices to non-negative values")]
            let start = indices.start as usize;

            #[expect(clippy::cast_sign_loss, reason = "Python normalizes slice indices to non-negative values")]
            let stop = indices.stop as usize;

            let items: Vec<PyObject> = value.bind(py).try_iter()?.map(|result| result.map(Bound::unbind)).collect::<PyResult<_>>()?;
            self.user_attrs_list.splice(start..stop, items);
            self.is_list_output = true;
            Ok(())
        } else {
            let key_name: String = key.extract()?;
            self.user_attrs_dict.insert(key_name, value);
            Ok(())
        }
    }

    /// Returns the value for the given key, delegating to `__getattr__`.
    fn __getitem__(&self, py: Python<'_>, key: &str) -> PyResult<PyObject> {
        self.__getattr__(py, key)
    }

    /// Returns the value for a key, or `None` if absent.
    fn get(&self, py: Python<'_>, key: &str) -> Option<PyObject> {
        self.user_attrs_dict.get(key).map(|val| val.clone_ref(py))
    }

    /// Returns an iterator over list items (list mode) or dict keys (dict mode).
    fn __iter__(&self, py: Python<'_>) -> PyResult<PyObject> {
        if self.is_list_output {
            let list = PyList::new(py, self.user_attrs_list.iter().map(|val| val.bind(py)))?;
            Ok(list.call_method0("__iter__")?.unbind())
        } else {
            let keys: Vec<&str> = self.user_attrs_dict.keys().map(String::as_str).collect();
            let list = PyList::new(py, &keys)?;
            Ok(list.call_method0("__iter__")?.unbind())
        }
    }
}

impl Payload {
    /// Extracts declared output element values from a Python dict into `user_attrs_dict`.
    fn extract_from_dict(&mut self, _py: Python<'_>, dict_ref: &Bound<'_, PyDict>) -> PyResult<()> {
        for name in &self.output_elem_names {
            if let Some(value) = dict_ref.get_item(name)? {
                self.user_attrs_dict.insert(name.clone(), value.unbind());
            }
        }
        Ok(())
    }

    /// Extracts declared output element values from a Python dict into a list of pairs.
    fn extract_dict_attrs(&self, _py: Python<'_>, dict_ref: &Bound<'_, PyDict>) -> PyResult<Vec<(String, PyObject)>> {
        let mut out = Vec::new();
        for name in &self.output_elem_names {
            if let Some(value) = dict_ref.get_item(name)? {
                out.push((name.clone(), value.unbind()));
            }
        }
        Ok(out)
    }

    /// Extracts declared output element values from a Python object's attributes into a list of pairs.
    fn extract_obj_attrs(&self, py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<Vec<(String, PyObject)>> {
        let mut out = Vec::new();
        for name in &self.output_elem_names {
            let py_name = PyString::new(py, name);
            if let Ok(value) = obj.getattr(&py_name) {
                out.push((name.clone(), value.unbind()));
            }
        }
        Ok(out)
    }

    /// Builds the final output value as either a Python list or dict.
    fn build_output_value<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        if self.is_list_output {
            let list = PyList::new(py, self.user_attrs_list.iter().map(|val| val.bind(py)))?;
            Ok(list.into_any())
        } else {
            let dict_ref = PyDict::new(py);
            for (key_name, val) in &self.user_attrs_dict {
                dict_ref.set_item(key_name, val.bind(py))?;
            }
            Ok(dict_ref.into_any())
        }
    }
}
