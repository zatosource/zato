use indexmap::IndexMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Shorthand alias for a heap-allocated Python object reference.
type PyObject = Py<PyAny>;

/// Python iterator that yields key names from a `ServiceInput` snapshot.
#[pyclass]
pub struct ServiceInputKeyIter {
    /// Pre-collected key names taken at iteration start.
    keys: Vec<String>,

    /// Current position in the keys vector.
    pos: usize,
}

#[pymethods]
impl ServiceInputKeyIter {
    /// Python iterator protocol - the iterator is its own iterable.
    const fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    /// Yields the next key name, or `None` once the snapshot is exhausted.
    fn __next__(&mut self) -> Option<String> {
        // A key is only handed out while the position is still within the snapshot,
        // so exhaustion and out-of-range collapse into the same `None` branch.
        let out = self.keys.get(self.pos).cloned();

        if out.is_some() {
            self.pos += 1;
        }

        out
    }
}

/// Dict-like Python container for incoming Zato service request parameters.
///
/// Implements Python's mapping protocol (`__getitem__`, `__setitem__`, etc.)
/// so that service code can access request data by key or attribute name.
/// Keys keep the order in which the request listed them.
#[pyclass(mapping)]
pub struct ServiceInput {
    /// Key-value store holding the request parameters received from the caller, in request order.
    data: IndexMap<String, PyObject>,
}

impl ServiceInput {
    /// Creates a new `ServiceInput`, optionally pre-populated from a Python dict.
    pub fn create(data: Option<&Bound<'_, PyDict>>) -> PyResult<Self> {
        let mut map = IndexMap::new();
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
            || {
                Err(pyo3::exceptions::PyAttributeError::new_err(format!(
                    "No such key `{}` among `{:?}`",
                    name,
                    self.data.keys().collect::<Vec<_>>()
                )))
            },
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
        // The remaining keys keep their relative order, which is what the service's caller sent.
        self.data.shift_remove(key);
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

    /// Iterates over key names, matching Python dict iteration semantics.
    fn __iter__(&self, py: Python<'_>) -> PyResult<Py<ServiceInputKeyIter>> {
        let iter = ServiceInputKeyIter {
            keys: self.data.keys().cloned().collect(),
            pos: 0,
        };
        Py::new(py, iter)
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
        self.data
            .get(key)
            .map_or_else(|| default.unwrap_or_else(|| py.None()), |val| val.clone_ref(py))
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
        self.data
            .iter()
            .map(|(key_name, val)| (key_name.clone(), val.clone_ref(py)))
            .collect()
    }

    /// Returns the request parameters as a Python dict, in request order.
    ///
    /// The dict is what a service hands to another service, writes to a file
    /// or publishes to a queue when it forwards the request it received.
    fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let out = PyDict::new(py);
        for (key_name, val) in &self.data {
            out.set_item(key_name, val.bind(py))?;
        }
        Ok(out)
    }

    /// Produces a deep copy of this container using Python's `copy.deepcopy`.
    fn deepcopy(&self, py: Python<'_>) -> PyResult<Self> {
        let copy_mod = py.import("copy")?;
        let mut new_data = IndexMap::new();
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
        let new_data = self
            .data
            .iter()
            .map(|(key_name, val)| (key_name.clone(), val.clone_ref(py)))
            .collect();
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
        let names: Vec<String> = elems.iter().map(|elem| elem.extract::<String>()).collect::<PyResult<_>>()?;
        Err(pyo3::exceptions::PyValueError::new_err(format!(
            "At least one of `{}` is required",
            names.join(", ")
        )))
    }
}

#[cfg(test)]
mod tests {
    use super::ServiceInput;
    use pyo3::exceptions::PyKeyError;
    use pyo3::prelude::*;
    use pyo3::types::PyDict;

    /// Builds a `ServiceInput` from the given pairs, in the order they are listed.
    fn build_input(py: Python<'_>, pairs: &[(&str, i64)]) -> PyResult<ServiceInput> {
        let dict = PyDict::new(py);
        for (key_name, value) in pairs {
            dict.set_item(*key_name, *value)?;
        }
        ServiceInput::create(Some(&dict))
    }

    /// Keys come back in the order the request listed them, with later additions at the end.
    #[test]
    fn keys_follow_request_order() -> PyResult<()> {
        Python::attach(|py| {
            let mut input = build_input(py, &[("customer_id", 1001), ("quantity", 3), ("region", 7)])?;
            let priority = 2_i64.into_pyobject(py)?.into_any().unbind();
            input.__setitem__("priority".to_owned(), priority);

            assert_eq!(input.keys(), vec!["customer_id", "quantity", "region", "priority"]);
            Ok(())
        })
    }

    /// Removing a key keeps the relative order of the keys that remain.
    #[test]
    fn delete_keeps_remaining_order() -> PyResult<()> {
        Python::attach(|py| {
            let mut input = build_input(py, &[("customer_id", 1001), ("quantity", 3), ("region", 7)])?;
            input.__delitem__("quantity")?;

            assert_eq!(input.keys(), vec!["customer_id", "region"]);
            Ok(())
        })
    }

    /// The dict returned by `to_dict` has the same keys, values and order as the input.
    #[test]
    fn to_dict_keeps_order_and_values() -> PyResult<()> {
        Python::attach(|py| {
            let input = build_input(py, &[("customer_id", 1001), ("quantity", 3)])?;
            let dict = input.to_dict(py)?;

            let keys: Vec<String> = dict.keys().extract()?;
            assert_eq!(keys, vec!["customer_id", "quantity"]);

            let quantity = dict.get_item("quantity")?.ok_or_else(|| PyKeyError::new_err("quantity"))?;
            assert_eq!(quantity.extract::<i64>()?, 3);
            Ok(())
        })
    }
}
