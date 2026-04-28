use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

/// Shorthand alias for a heap-allocated Python object reference.
type PyObject = Py<PyAny>;

/// Dict-like Python container for incoming Zato service request parameters.
///
/// Implements Python's mapping protocol (`__getitem__`, `__setitem__`, etc.)
/// so that service code can access request data by key or attribute name.
#[pyclass(mapping)]
pub struct ServiceInput {
    /// Key-value store holding the request parameters received from the caller.
    data: HashMap<String, PyObject>,
}

impl ServiceInput {
    /// Creates a new `ServiceInput`, optionally pre-populated from a Python dict.
    pub fn create(data: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut map = HashMap::new();
        if let Some(dict_ref) = data {
            for (key, value) in dict_ref.iter() {
                let key_name: String = key.extract()?;
                map.insert(key_name, value.unbind());
            }
        }
        Ok(Self { data: map })
    }
}

#[pymethods]
impl ServiceInput {

    /// Constructs a `ServiceInput` from Python, optionally accepting an initial dict.
    #[new]
    #[pyo3(signature = (data=None))]
    fn new(data: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        Self::create(data)
    }

    /// Returns the value for the given attribute name, raising `AttributeError` if absent.
    fn __getattr__(&self, py: Python<'_>, name: &str) -> PyResult<PyObject> {
        self.data.get(name).map_or_else(
            || Err(pyo3::exceptions::PyAttributeError::new_err(
                format!("No such key `{}` among `{:?}`", name, self.data.keys().collect::<Vec<_>>())
            )),
            |val| Ok(val.clone_ref(py)),
        )
    }

    /// Returns the value for the given key, raising `KeyError` if absent.
    fn __getitem__(&self, py: Python<'_>, key: &str) -> PyResult<PyObject> {
        self.data.get(key).map_or_else(
            || Err(pyo3::exceptions::PyKeyError::new_err(key.to_string())),
            |val| Ok(val.clone_ref(py)),
        )
    }

    /// Sets an attribute (key) to the given value.
    fn __setattr__(&mut self, key: String, value: PyObject) {
        self.data.insert(key, value);
    }

    /// Sets an item (key) to the given value, same as attribute assignment.
    fn __setitem__(&mut self, key: String, value: PyObject) {
        self.data.insert(key, value);
    }

    /// Removes the given key from the container. Silently ignores missing keys.
    #[expect(clippy::unnecessary_wraps, reason = "PyO3 __delitem__ protocol requires PyResult return")]
    fn __delitem__(&mut self, key: &str) -> PyResult<()> {
        self.data.remove(key);
        Ok(())
    }

    /// Merges entries from another mapping (dict, `ServiceInput`, or iterable of pairs).
    fn update(&mut self, other: &Bound<'_, PyAny>) -> PyResult<()> {
        if let Ok(dict) = other.cast::<PyDict>() {
            for (key, value) in dict.iter() {
                let key_name: String = key.extract()?;
                self.data.insert(key_name, value.unbind());
            }
        } else if other.is_instance_of::<Self>() {
            let keys: Vec<String> = other.call_method0("keys")?.extract()?;
            for key_name in keys {
                let val = other.get_item(&key_name)?;
                self.data.insert(key_name, val.unbind());
            }
        } else {
            for item in other.try_iter()? {
                let item = item?;
                let key_name: String = item.get_item(0)?.extract()?;
                let val = item.get_item(1)?.unbind();
                self.data.insert(key_name, val);
            }
        }
        Ok(())
    }

    /// Returns `true` if the given key exists in the container.
    fn __contains__(&self, key: &str) -> bool {
        self.data.contains_key(key)
    }

    /// Returns the number of entries in the container.
    fn __len__(&self) -> usize {
        self.data.len()
    }

    /// Debug representation showing all stored key names.
    fn __repr__(&self) -> String {
        format!("ServiceInput({:?})", self.data.keys().collect::<Vec<_>>())
    }

    /// Returns the value for a key, falling back to `default` (or `None`) if absent.
    #[pyo3(signature = (key, default=None))]
    fn get(&self, py: Python<'_>, key: &str, default: Option<PyObject>) -> PyObject {
        self.data.get(key).map_or_else(
            || default.unwrap_or_else(|| py.None()),
            |val| val.clone_ref(py),
        )
    }

    /// Returns all key names as a list of strings.
    fn keys(&self) -> Vec<String> {
        self.data.keys().cloned().collect()
    }

    /// Returns all values as a list of Python objects.
    fn values(&self, py: Python<'_>) -> Vec<PyObject> {
        self.data.values().map(|val| val.clone_ref(py)).collect()
    }

    /// Returns all (key, value) pairs as a list of tuples.
    fn items(&self, py: Python<'_>) -> Vec<(String, PyObject)> {
        self.data.iter().map(|(key_name, val)| (key_name.clone(), val.clone_ref(py))).collect()
    }

    /// Produces a deep copy of this container using Python's `copy.deepcopy`.
    fn deepcopy(&self, py: Python<'_>) -> PyResult<Self> {
        let copy_mod = py.import("copy")?;
        let mut new_data = HashMap::new();
        for (key_name, val) in &self.data {
            let copied = copy_mod.call_method1("deepcopy", (val.bind(py),))?;
            new_data.insert(key_name.clone(), copied.unbind());
        }
        Ok(Self { data: new_data })
    }

    /// Python `__deepcopy__` protocol, delegates to `deepcopy`.
    #[pyo3(signature = (_memo=None))]
    fn __deepcopy__(&self, py: Python<'_>, _memo: Option<&Bound<'_, PyAny>>) -> PyResult<Self> {
        self.deepcopy(py)
    }

    /// Produces a shallow copy of this container (Python object references are shared).
    fn __copy__(&self, py: Python<'_>) -> Self {
        let new_data = self.data.iter().map(|(key_name, val)| (key_name.clone(), val.clone_ref(py))).collect();
        Self { data: new_data }
    }

    /// Raises `ValueError` unless at least one of the named elements has a truthy value.
    #[pyo3(signature = (*elems))]
    fn require_any(&self, elems: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<()> {
        for elem in elems.iter() {
            let name: String = elem.extract()?;
            if let Some(val) = self.data.get(&name) {
                let py = elems.py();
                if val.bind(py).is_truthy()? {
                    return Ok(());
                }
            }
        }
        let names: Vec<String> = elems
            .iter()
            .map(|elem| elem.extract::<String>())
            .collect::<PyResult<_>>()?;
        Err(pyo3::exceptions::PyValueError::new_err(
            format!("At least one of `{}` is required", names.join(", "))
        ))
    }
}
