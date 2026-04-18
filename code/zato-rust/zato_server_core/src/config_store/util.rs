use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

pub(crate) fn value_to_py(py: Python<'_>, v: &serde_yaml::Value) -> PyResult<Py<PyAny>> {
    match v {
        serde_yaml::Value::Null => Ok(py.None().into_pyobject(py).unwrap().unbind()),
        serde_yaml::Value::Bool(b) => Ok((*b).into_pyobject(py).unwrap().to_owned().unbind().into_any()),
        serde_yaml::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py).unwrap().unbind().into_any())
            } else if let Some(u) = n.as_u64() {
                Ok(u.into_pyobject(py).unwrap().unbind().into_any())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py).unwrap().unbind().into_any())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(
                    format!("YAML number {:?} is not representable as i64, u64, or f64", n)
                ))
            }
        }
        serde_yaml::Value::String(s) => Ok(s.into_pyobject(py).unwrap().unbind().into_any()),
        serde_yaml::Value::Sequence(seq) => {
            let list = PyList::empty(py);
            for item in seq {
                let _ = list.append(value_to_py(py, item)?);
            }
            Ok(list.unbind().into_any())
        }
        serde_yaml::Value::Mapping(map) => {
            let dict = PyDict::new(py);
            for (k, val) in map {
                match k {
                    serde_yaml::Value::String(ks) => {
                        let _ = dict.set_item(ks, value_to_py(py, val)?);
                    }
                    other => {
                        return Err(pyo3::exceptions::PyValueError::new_err(
                            format!("YAML mapping key {:?} is not a string", other)
                        ));
                    }
                }
            }
            Ok(dict.unbind().into_any())
        }
        serde_yaml::Value::Tagged(t) => value_to_py(py, &t.value),
    }
}

pub(crate) fn struct_to_pydict<T: serde::Serialize>(py: Python<'_>, item: &T) -> PyResult<Py<PyDict>> {
    let yaml_val = serde_yaml::to_value(item)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("serialize: {}", e)))?;
    if let serde_yaml::Value::Mapping(map) = yaml_val {
        let dict = PyDict::new(py);
        for (k, v) in &map {
            match k {
                serde_yaml::Value::String(ks) => {
                    let _ = dict.set_item(ks, value_to_py(py, v)?);
                }
                other => {
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        format!("YAML mapping key {:?} is not a string", other)
                    ));
                }
            }
        }
        Ok(dict.unbind())
    } else {
        Err(pyo3::exceptions::PyValueError::new_err("expected mapping"))
    }
}

pub(crate) fn pydict_to_struct<T: serde::de::DeserializeOwned>(py: Python<'_>, dict: &Bound<'_, PyDict>) -> PyResult<T> {
    let mut map = serde_yaml::Mapping::new();
    for (k, v) in dict.iter() {
        let key_str: String = k.extract()?;
        let yaml_key = serde_yaml::Value::String(key_str);
        let yaml_val = py_to_value(py, &v)?;
        map.insert(yaml_key, yaml_val);
    }
    let yaml_val = serde_yaml::Value::Mapping(map.clone());
    serde_yaml::from_value::<T>(yaml_val)
        .map_err(|e| {
            let mut fields = String::new();
            let mut suspects = String::new();

            for (k, v) in &map {
                if let serde_yaml::Value::String(ks) = k {
                    fields.push_str(&format!("  {}={:?}\n", ks, v));
                    if v.is_null() {
                        suspects.push_str(&format!("  -> suspect (null): {}\n", ks));
                    }
                }
            }

            pyo3::exceptions::PyValueError::new_err(
                format!("deserialize: {}\n{}Fields:\n{}", e, suspects, fields)
            )
        })
}

fn py_to_value(_py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<serde_yaml::Value> {
    if obj.is_none() {
        Ok(serde_yaml::Value::Null)
    } else if let Ok(b) = obj.extract::<bool>() {
        Ok(serde_yaml::Value::Bool(b))
    } else if let Ok(i) = obj.extract::<i64>() {
        Ok(serde_yaml::Value::Number(i.into()))
    } else if let Ok(f) = obj.extract::<f64>() {
        Ok(serde_yaml::Value::Number(serde_yaml::Number::from(f)))
    } else if let Ok(s) = obj.extract::<String>() {
        Ok(serde_yaml::Value::String(s))
    } else if let Ok(list) = obj.cast::<PyList>() {
        let mut seq = Vec::new();
        for item in list.iter() {
            seq.push(py_to_value(_py, &item)?);
        }
        Ok(serde_yaml::Value::Sequence(seq))
    } else if let Ok(dict) = obj.cast::<PyDict>() {
        let mut map = serde_yaml::Mapping::new();
        for (k, v) in dict.iter() {
            let key_str: String = k.extract()?;
            map.insert(serde_yaml::Value::String(key_str), py_to_value(_py, &v)?);
        }
        Ok(serde_yaml::Value::Mapping(map))
    } else {
        let s = obj.str()?.to_string();
        Ok(serde_yaml::Value::String(s))
    }
}

pub(crate) fn lock_err<T>(_: T) -> PyErr {
    pyo3::exceptions::PyRuntimeError::new_err("lock poisoned")
}
