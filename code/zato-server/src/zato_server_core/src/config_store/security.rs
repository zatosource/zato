use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use subtle::ConstantTimeEq;

use crate::model::SecurityDef;
use super::store::ConfigStore;
use super::util::{struct_to_pydict, pydict_to_struct};

impl ConfigStore {

    fn rebuild_indexes_for_security(
        &self,
        sec: &SecurityDef,
        name: &str,
        by_username: &mut std::collections::HashMap<String, String>,
        by_apikey: &mut std::collections::HashMap<String, String>,
    ) {
        match sec {
            SecurityDef::BasicAuth(d) => {
                if !d.username.is_empty() {
                    by_username.insert(d.username.clone(), name.to_string());
                }
            }
            SecurityDef::ApiKey(d) => {
                if !d.password.is_empty() {
                    by_apikey.insert(d.password.clone(), name.to_string());
                }
            }
            _ => {}
        }
    }

    fn remove_from_indexes(
        &self,
        sec: &SecurityDef,
        by_username: &mut std::collections::HashMap<String, String>,
        by_apikey: &mut std::collections::HashMap<String, String>,
    ) {
        match sec {
            SecurityDef::BasicAuth(d) => {
                by_username.remove(&d.username);
            }
            SecurityDef::ApiKey(d) => {
                by_apikey.remove(&d.password);
            }
            _ => {}
        }
    }

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
        let mut by_username = self.security_by_username.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        let mut by_apikey = self.security_by_apikey_value.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;

        if let Some(old) = store.get(name) {
            self.remove_from_indexes(old, &mut by_username, &mut by_apikey);
        }
        self.rebuild_indexes_for_security(&sec_def, name, &mut by_username, &mut by_apikey);
        store.insert(name.to_string(), sec_def);
        Ok(())
    }

    pub(super) fn delete_security(&self, name: &str) -> PyResult<bool> {
        let mut store = self.security.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        let mut by_username = self.security_by_username.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        let mut by_apikey = self.security_by_apikey_value.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;

        match store.remove(name) {
            Some(old) => {
                self.remove_from_indexes(&old, &mut by_username, &mut by_apikey);
                Ok(true)
            }
            None => Ok(false),
        }
    }

    /// O(1) basic auth credential check with constant-time password comparison.
    /// Returns the security def's `id` on success, `None` on failure.
    pub fn check_basic_auth(&self, username: &str, password: &str) -> PyResult<Option<String>> {
        self.check_basic_auth_inner(username, password)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))
    }

    /// O(1) API key credential check with constant-time key comparison.
    /// Returns the security def's `id` on success, `None` on failure.
    pub fn check_apikey(&self, header_value: &str) -> PyResult<Option<String>> {
        self.check_apikey_inner(header_value)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))
    }

    /// Pure-Rust core of `check_basic_auth`, testable without Python.
    pub fn check_basic_auth_inner(&self, username: &str, password: &str) -> Result<Option<String>, String> {
        let by_username = self.security_by_username.read()
            .map_err(|_| "lock poisoned".to_string())?;
        let sec_name = match by_username.get(username) {
            Some(n) => n.clone(),
            None => return Ok(None),
        };
        drop(by_username);

        let store = self.security.read()
            .map_err(|_| "lock poisoned".to_string())?;
        match store.get(&sec_name) {
            Some(sec) => {
                let stored_password = sec.password();
                if bool::from(stored_password.as_bytes().ct_eq(password.as_bytes())) {
                    Ok(Some(sec.id().to_string()))
                } else {
                    Ok(None)
                }
            }
            None => Ok(None),
        }
    }

    /// Pure-Rust core of `check_apikey`, testable without Python.
    pub fn check_apikey_inner(&self, header_value: &str) -> Result<Option<String>, String> {
        let by_apikey = self.security_by_apikey_value.read()
            .map_err(|_| "lock poisoned".to_string())?;
        let sec_name = match by_apikey.get(header_value) {
            Some(n) => n.clone(),
            None => return Ok(None),
        };
        drop(by_apikey);

        let store = self.security.read()
            .map_err(|_| "lock poisoned".to_string())?;
        match store.get(&sec_name) {
            Some(sec) => {
                let stored_key = sec.password();
                if bool::from(stored_key.as_bytes().ct_eq(header_value.as_bytes())) {
                    Ok(Some(sec.id().to_string()))
                } else {
                    Ok(None)
                }
            }
            None => Ok(None),
        }
    }

    /// Insert a security def directly (no PyO3), for use in pure-Rust tests.
    pub fn set_security_direct(&self, name: &str, sec_def: SecurityDef) -> Result<(), String> {
        let mut store = self.security.write()
            .map_err(|_| "lock poisoned".to_string())?;
        let mut by_username = self.security_by_username.write()
            .map_err(|_| "lock poisoned".to_string())?;
        let mut by_apikey = self.security_by_apikey_value.write()
            .map_err(|_| "lock poisoned".to_string())?;

        if let Some(old) = store.get(name) {
            self.remove_from_indexes(old, &mut by_username, &mut by_apikey);
        }
        self.rebuild_indexes_for_security(&sec_def, name, &mut by_username, &mut by_apikey);
        store.insert(name.to_string(), sec_def);
        Ok(())
    }

    /// Delete a security def directly (no PyO3), for use in pure-Rust tests.
    pub fn delete_security_direct(&self, name: &str) -> Result<bool, String> {
        let mut store = self.security.write()
            .map_err(|_| "lock poisoned".to_string())?;
        let mut by_username = self.security_by_username.write()
            .map_err(|_| "lock poisoned".to_string())?;
        let mut by_apikey = self.security_by_apikey_value.write()
            .map_err(|_| "lock poisoned".to_string())?;

        match store.remove(name) {
            Some(old) => {
                self.remove_from_indexes(&old, &mut by_username, &mut by_apikey);
                Ok(true)
            }
            None => Ok(false),
        }
    }

    /// Read the username index snapshot, for test assertions.
    pub fn get_username_index_snapshot(&self) -> Result<std::collections::HashMap<String, String>, String> {
        let idx = self.security_by_username.read()
            .map_err(|_| "lock poisoned".to_string())?;
        Ok(idx.clone())
    }

    /// Read the apikey index snapshot, for test assertions.
    pub fn get_apikey_index_snapshot(&self) -> Result<std::collections::HashMap<String, String>, String> {
        let idx = self.security_by_apikey_value.read()
            .map_err(|_| "lock poisoned".to_string())?;
        Ok(idx.clone())
    }

    /// Snapshot of all security defs, for test assertions.
    pub fn get_security_snapshot(&self) -> Result<std::collections::HashMap<String, SecurityDef>, String> {
        let store = self.security.read()
            .map_err(|_| "lock poisoned".to_string())?;
        Ok(store.clone())
    }
}
