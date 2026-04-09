use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

type PyObject = Py<PyAny>;

#[pyclass(mapping)]
pub struct ServiceInput {
    data: HashMap<String, PyObject>,
}

impl ServiceInput {
    pub fn create(data: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut map = HashMap::new();
        if let Some(d) = data {
            for (key, value) in d.iter() {
                let k: String = key.extract()?;
                map.insert(k, value.unbind());
            }
        }
        Ok(Self { data: map })
    }
}

#[pymethods]
impl ServiceInput {

    #[new]
    #[pyo3(signature = (data=None))]
    fn new(data: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut map = HashMap::new();
        if let Some(d) = data {
            for (key, value) in d.iter() {
                let k: String = key.extract()?;
                map.insert(k, value.unbind());
            }
        }
        Ok(Self { data: map })
    }

    fn __getattr__(&self, py: Python<'_>, name: &str) -> PyResult<PyObject> {
        match self.data.get(name) {
            Some(v) => Ok(v.clone_ref(py)),
            None => Err(pyo3::exceptions::PyAttributeError::new_err(
                format!("No such key `{}` among `{:?}`", name, self.data.keys().collect::<Vec<_>>())
            )),
        }
    }

    fn __getitem__(&self, py: Python<'_>, key: &str) -> PyResult<PyObject> {
        match self.data.get(key) {
            Some(v) => Ok(v.clone_ref(py)),
            None => Err(pyo3::exceptions::PyKeyError::new_err(key.to_string())),
        }
    }

    fn __setattr__(&mut self, key: String, value: PyObject) {
        self.data.insert(key, value);
    }

    fn __setitem__(&mut self, key: String, value: PyObject) {
        self.data.insert(key, value);
    }

    fn __delitem__(&mut self, key: &str) -> PyResult<()> {
        self.data.remove(key);
        Ok(())
    }

    fn update(&mut self, other: &Bound<'_, PyAny>) -> PyResult<()> {
        if let Ok(dict) = other.downcast::<PyDict>() {
            for (key, value) in dict.iter() {
                let k: String = key.extract()?;
                self.data.insert(k, value.unbind());
            }
        } else if other.is_instance_of::<ServiceInput>() {
            let keys: Vec<String> = other.call_method0("keys")?.extract()?;
            for k in keys {
                let v = other.get_item(&k)?;
                self.data.insert(k, v.unbind());
            }
        } else {
            for item in other.try_iter()? {
                let item = item?;
                let k: String = item.get_item(0)?.extract()?;
                let v = item.get_item(1)?.unbind();
                self.data.insert(k, v);
            }
        }
        Ok(())
    }

    fn __contains__(&self, key: &str) -> bool {
        self.data.contains_key(key)
    }

    fn __len__(&self) -> usize {
        self.data.len()
    }

    fn __repr__(&self) -> String {
        format!("ServiceInput({:?})", self.data.keys().collect::<Vec<_>>())
    }

    #[pyo3(signature = (key, default=None))]
    fn get(&self, py: Python<'_>, key: &str, default: Option<PyObject>) -> PyObject {
        match self.data.get(key) {
            Some(v) => v.clone_ref(py),
            None => default.unwrap_or_else(|| py.None().into()),
        }
    }

    fn keys(&self) -> Vec<String> {
        self.data.keys().cloned().collect()
    }

    fn values(&self, py: Python<'_>) -> Vec<PyObject> {
        self.data.values().map(|v| v.clone_ref(py)).collect()
    }

    fn items(&self, py: Python<'_>) -> Vec<(String, PyObject)> {
        self.data.iter().map(|(k, v)| (k.clone(), v.clone_ref(py))).collect()
    }

    fn deepcopy(&self, py: Python<'_>) -> PyResult<Self> {
        let copy_mod = py.import("copy")?;
        let mut new_data = HashMap::new();
        for (k, v) in &self.data {
            let copied = copy_mod.call_method1("deepcopy", (v.bind(py),))?;
            new_data.insert(k.clone(), copied.unbind());
        }
        Ok(Self { data: new_data })
    }

    #[pyo3(signature = (*elems))]
    fn require_any(&self, elems: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<()> {
        for elem in elems.iter() {
            let name: String = elem.extract()?;
            if let Some(v) = self.data.get(&name) {
                let py = elems.py();
                if v.bind(py).is_truthy()? {
                    return Ok(());
                }
            }
        }
        let names: Vec<String> = elems
            .iter()
            .map(|e| e.extract::<String>())
            .collect::<PyResult<_>>()?;
        Err(pyo3::exceptions::PyValueError::new_err(
            format!("At least one of `{}` is required", names.join(", "))
        ))
    }
}
