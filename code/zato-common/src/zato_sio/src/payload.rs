use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use std::collections::HashMap;

type PyObject = Py<PyAny>;

#[pyclass]
pub struct Payload {
    output_elem_names: Vec<String>,
    user_attrs_dict: HashMap<String, PyObject>,
    user_attrs_list: Vec<PyObject>,
    is_list_output: bool,

    #[pyo3(get, set)]
    pub zato_meta: Option<PyObject>,

    #[pyo3(get)]
    pub cid: Option<String>,

    #[pyo3(get)]
    pub data_format: Option<String>,
}

impl Payload {
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

    fn set_payload_attrs(&mut self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        self.user_attrs_dict.clear();
        self.user_attrs_list.clear();
        self.is_list_output = false;

        if value.is_instance_of::<PyDict>() {
            let dict: &Bound<'_, PyDict> = value.cast()?;
            self.extract_from_dict(py, dict)?;
        } else if value.is_instance_of::<PyList>() {
            self.is_list_output = true;
            for item in value.try_iter()? {
                let item = item?;
                if item.is_instance_of::<PyDict>() {
                    let dict: &Bound<'_, PyDict> = item.cast()?;
                    let extracted = self.extract_dict_attrs(py, dict)?;
                    let py_dict = PyDict::new(py);
                    for (k, v) in &extracted {
                        py_dict.set_item(k, v.bind(py))?;
                    }
                    self.user_attrs_list.push(py_dict.into_any().unbind());
                } else {
                    let extracted = self.extract_obj_attrs(py, &item)?;
                    let py_dict = PyDict::new(py);
                    for (k, v) in &extracted {
                        py_dict.set_item(k, v.bind(py))?;
                    }
                    self.user_attrs_list.push(py_dict.into_any().unbind());
                }
            }
        } else {
            if let Ok(to_zato) = value.getattr("to_zato") {
                let converted = to_zato.call0()?;
                return self.set_payload_attrs(py, &converted);
            }
            for name in &self.output_elem_names {
                let py_name = PyString::new(py, name);
                if let Ok(v) = value.getattr(&py_name) {
                    self.user_attrs_dict.insert(name.clone(), v.unbind());
                }
            }
        }

        Ok(())
    }

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
                if let Ok(dict) = output.cast::<PyDict>() {
                    dict.set_item("_meta", &search)?;
                    if do_serialize {
                        let json_mod = py.import("zato.common.json_internal")?;
                        let result = json_mod.call_method1("dumps", (dict,))?;
                        return Ok(result.unbind());
                    }
                    return Ok(dict.clone().into_any().unbind());
                }
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

    fn has_data(&self) -> bool {
        !self.user_attrs_dict.is_empty() || !self.user_attrs_list.is_empty()
    }

    fn append(&mut self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        if self.output_elem_names.is_empty() {
            self.user_attrs_list.push(value.clone().unbind());
        } else if let Ok(dict) = value.cast::<PyDict>() {
            let filtered = PyDict::new(py);
            for name in &self.output_elem_names {
                match dict.get_item(name)? {
                    Some(v) => filtered.set_item(name, v)?,
                    None => filtered.set_item(name, py.None())?,
                }
            }
            self.user_attrs_list.push(filtered.into_any().unbind());
        } else {
            let filtered = PyDict::new(py);
            for name in &self.output_elem_names {
                let py_name = PyString::new(py, name);
                match value.getattr(&py_name) {
                    Ok(v) => filtered.set_item(name, v)?,
                    Err(_) => filtered.set_item(name, py.None())?,
                }
            }
            self.user_attrs_list.push(filtered.into_any().unbind());
        }
        self.is_list_output = true;
        Ok(())
    }

    fn __setattr__(&mut self, key: String, value: PyObject) {
        if key == "zato_meta" {
            self.zato_meta = Some(value);
        } else {
            self.user_attrs_dict.insert(key, value);
        }
    }

    fn __getattr__(&self, py: Python<'_>, key: &str) -> PyResult<PyObject> {
        match self.user_attrs_dict.get(key) {
            Some(v) => Ok(v.clone_ref(py)),
            None => Err(pyo3::exceptions::PyKeyError::new_err(
                format!("No such key `{}` among `{:?}`", key, self.user_attrs_dict.keys().collect::<Vec<_>>())
            )),
        }
    }

    fn __setitem__(&mut self, py: Python<'_>, key: &Bound<'_, PyAny>, value: PyObject) -> PyResult<()> {
        if key.is_instance_of::<pyo3::types::PySlice>() {
            let slice: &Bound<'_, pyo3::types::PySlice> = key.cast()?;
            let indices = slice.indices(self.user_attrs_list.len() as isize)?;
            let start = indices.start as usize;
            let stop = indices.stop as usize;
            let items: Vec<PyObject> = value.bind(py).try_iter()?.map(|r| r.map(|v| v.unbind())).collect::<PyResult<_>>()?;
            self.user_attrs_list.splice(start..stop, items);
            self.is_list_output = true;
            Ok(())
        } else {
            let k: String = key.extract()?;
            self.user_attrs_dict.insert(k, value);
            Ok(())
        }
    }

    fn __getitem__(&self, py: Python<'_>, key: &str) -> PyResult<PyObject> {
        self.__getattr__(py, key)
    }

    fn get(&self, py: Python<'_>, key: &str) -> Option<PyObject> {
        self.user_attrs_dict.get(key).map(|v| v.clone_ref(py))
    }

    fn __iter__(&self, py: Python<'_>) -> PyResult<PyObject> {
        if self.is_list_output {
            let list = PyList::new(py, self.user_attrs_list.iter().map(|v| v.bind(py)))?;
            Ok(list.call_method0("__iter__")?.unbind())
        } else {
            let keys: Vec<&str> = self.user_attrs_dict.keys().map(|s| s.as_str()).collect();
            let list = PyList::new(py, &keys)?;
            Ok(list.call_method0("__iter__")?.unbind())
        }
    }
}

impl Payload {
    fn extract_from_dict(&mut self, _py: Python<'_>, dict: &Bound<'_, PyDict>) -> PyResult<()> {
        for name in &self.output_elem_names {
            if let Some(value) = dict.get_item(name)? {
                self.user_attrs_dict.insert(name.clone(), value.unbind());
            }
        }
        Ok(())
    }

    fn extract_dict_attrs(&self, _py: Python<'_>, dict: &Bound<'_, PyDict>) -> PyResult<Vec<(String, PyObject)>> {
        let mut out = Vec::new();
        for name in &self.output_elem_names {
            if let Some(value) = dict.get_item(name)? {
                out.push((name.clone(), value.unbind()));
            }
        }
        Ok(out)
    }

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

    fn build_output_value<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        if self.is_list_output {
            let list = PyList::new(py, self.user_attrs_list.iter().map(|v| v.bind(py)))?;
            Ok(list.into_any())
        } else {
            let dict = PyDict::new(py);
            for (k, v) in &self.user_attrs_dict {
                dict.set_item(k, v.bind(py))?;
            }
            Ok(dict.into_any())
        }
    }
}
