use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};

use crate::model::SecurityDef;
use super::store::ConfigStore;
use super::util::{struct_to_pydict, pydict_to_struct};

impl ConfigStore {

    pub(super) fn get_security<'py>(&self, py: Python<'py>, name: &str) -> PyResult<Option<Py<PyDict>>> {
        let store = self.security.read()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        match store.get(name) {
            Some(sec) => {
                let d = struct_to_pydict(py, sec)?;
                let bound = d.bind(py);
                let _ = bound.set_item("sec_type", PyString::new(py, sec.sec_type()));
                Ok(Some(d))
            }
            None => Ok(None),
        }
    }

    pub(super) fn get_list_security<'py>(&self, py: Python<'py>) -> PyResult<Py<PyList>> {
        let store = self.security.read()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        let list = PyList::empty(py);
        for sec in store.values() {
            let d = struct_to_pydict(py, sec)?;
            let bound = d.bind(py);
            let _ = bound.set_item("sec_type", PyString::new(py, sec.sec_type()));
            let _ = list.append(bound);
        }
        Ok(list.unbind())
    }

    pub(super) fn set_security<'py>(&self, py: Python<'py>, name: &str, data: &Bound<'py, PyDict>) -> PyResult<()> {
        let sec_def: SecurityDef = pydict_to_struct(py, data)?;
        let mut store = self.security.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        store.insert(name.to_string(), sec_def);
        Ok(())
    }

    pub(super) fn delete_security(&self, name: &str) -> PyResult<bool> {
        let mut store = self.security.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        Ok(store.remove(name).is_some())
    }
}
