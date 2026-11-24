//! The identity of the `SQLite` library that the Python driver and the writers share.
//!
//! The writers operate on the handle of a `sqlite3.Connection`, which is valid only when the driver and the writers
//! are bound to one and the same `SQLite` library loaded in the process. The library of the driver is resolved
//! by the dynamic loader from the extension module of the driver, and its entry point must be the entry point
//! that the writers call.

use std::ffi::{CStr, CString, c_char, c_void};

use pyo3::exceptions::PyRuntimeError;
use pyo3::intern;
use pyo3::prelude::*;
use rusqlite::ffi;

/// The extension module of the Python driver, which is linked against `SQLite`.
const DRIVER_MODULE: &str = "_sqlite3";

/// The function of `SQLite` whose address identifies the library that a module is bound to.
const IDENTITY_SYMBOL: &CStr = c"sqlite3_libversion";

/// The signature of `sqlite3_libversion`, which returns the version of the library.
type LibVersionFn = unsafe extern "C" fn() -> *const c_char;

// ################################################################################################################################
// ################################################################################################################################

/// Confirms that the `SQLite` library of the Python driver is the library that the writers are linked to.
///
/// The writers are built only when it is, so that no connection handle is ever operated on by two libraries.
pub fn check_library_identity(py: Python<'_>) -> PyResult<()> {
    let driver_module = py.import(DRIVER_MODULE)?;
    let driver_spec = driver_module.getattr(intern!(py, "__spec__"))?;
    let driver_path: String = driver_spec.getattr(intern!(py, "origin"))?.extract()?;

    let driver_function = driver_symbol(&driver_path);
    let writer_function: LibVersionFn = ffi::sqlite3_libversion;

    compare_libraries(&driver_path, driver_function, writer_function).map_err(PyRuntimeError::new_err)
}

/// Returns `sqlite3_libversion` as the dynamic loader resolves it for an object loaded in the process.
///
/// `None` is returned if the object is not loaded or neither it nor its dependencies export the function.
fn driver_symbol(path: &str) -> Option<LibVersionFn> {
    // A path with a NUL byte names no object that can be loaded
    let path = CString::new(path).ok()?;

    #[expect(unsafe_code, reason = "the dynamic loader has no safe interface")]
    // SAFETY: the path is a NUL-terminated string, and with `RTLD_NOLOAD` the loader loads nothing,
    // it only returns a new reference to an object that is already loaded, or null.
    let handle = unsafe { libc::dlopen(path.as_ptr(), libc::RTLD_NOW | libc::RTLD_NOLOAD) };

    // An object not loaded in the process cannot be the library of the driver
    if handle.is_null() {
        return None;
    }

    #[expect(unsafe_code, reason = "the dynamic loader has no safe interface")]
    // SAFETY: the handle is open and the name is a NUL-terminated string. The lookup searches the object
    // and the dependencies it was loaded with, which is the scope that the object binds its own calls in.
    let symbol: *mut c_void = unsafe { libc::dlsym(handle, IDENTITY_SYMBOL.as_ptr()) };

    #[expect(unsafe_code, reason = "the dynamic loader returns the address of a function as a data pointer")]
    // SAFETY: a null address becomes `None`, and any other address is the entry point of `sqlite3_libversion`,
    // whose signature `SQLite` defines as `LibVersionFn`. The function is never called through it.
    let out = unsafe { std::mem::transmute::<*mut c_void, Option<LibVersionFn>>(symbol) };

    #[expect(unsafe_code, reason = "the dynamic loader has no safe interface")]
    // SAFETY: the handle is the reference that `dlopen` added, and the object stays loaded through the reference
    // that the interpreter holds to it. Only the address of the function is used afterwards, as a value to compare.
    unsafe {
        libc::dlclose(handle);
    }

    out
}

/// Compares the entry point of `SQLite` that the driver is bound to with the one that the writers call.
fn compare_libraries(driver_path: &str, driver_function: Option<LibVersionFn>, writer_function: LibVersionFn) -> Result<(), String> {
    let writer_version = rusqlite::version();

    // The driver links `SQLite` statically and exports nothing, or it was not loaded from a shared object at all
    let Some(driver_function) = driver_function else {
        return Err(format!(
            "SQLite of the driver `{driver_path}` cannot be resolved by the dynamic loader, so it cannot be confirmed to be SQLite `{writer_version}` of the writer"
        ));
    };

    // The same version is not enough, the two must be the same library loaded in the process
    if !std::ptr::fn_addr_eq(driver_function, writer_function) {
        return Err(format!(
            "SQLite of the driver `{driver_path}` is a different library than SQLite `{writer_version}` of the writer"
        ));
    }

    Ok(())
}

// ################################################################################################################################
// ################################################################################################################################

#[cfg(test)]
#[path = "sqlite_library_tests.rs"]
mod tests;
