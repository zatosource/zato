//! The confirmation that the `SQLite` library of the Python driver is the library that the writers are linked to.
//!
//! The tests resolve `sqlite3_libversion` through the dynamic loader from the shared `SQLite` library
//! that the tests themselves are linked to, from an object that does not export `SQLite`, and from a path
//! that is not loaded, and compare the result with the entry point that the writers call.

use rusqlite::ffi;

use super::{LibVersionFn, compare_libraries, driver_symbol};

/// The shared `SQLite` library, by the name that the dynamic loader knows it under once it is loaded.
const SHARED_SQLITE: &str = "libsqlite3.so.0";

/// A shared object loaded in every process that neither contains `SQLite` nor depends on it.
const OBJECT_WITHOUT_SQLITE: &str = "libc.so.6";

/// The path of an extension module of the driver that is not loaded in the process.
const DRIVER_NOT_LOADED: &str = "/opt/zato/python/lib-dynload/_sqlite3.cpython-312-x86_64-linux-gnu.so";

/// Returns the entry point of `sqlite3_libversion` that the writers call.
fn writer_function() -> LibVersionFn {
    ffi::sqlite3_libversion
}

#[test]
fn accepts_the_shared_library_that_the_writer_is_linked_to() {
    let driver_function = driver_symbol(SHARED_SQLITE);

    assert!(driver_function.is_some());
    assert_eq!(compare_libraries(SHARED_SQLITE, driver_function, writer_function()), Ok(()));
}

#[test]
fn refuses_an_object_that_exports_no_sqlite() {
    let driver_function = driver_symbol(OBJECT_WITHOUT_SQLITE);
    let refused = compare_libraries(OBJECT_WITHOUT_SQLITE, driver_function, writer_function());

    assert!(driver_function.is_none());
    assert_eq!(
        refused,
        Err(format!(
            "SQLite of the driver `{OBJECT_WITHOUT_SQLITE}` cannot be resolved by the dynamic loader, so it cannot be confirmed to be SQLite `{}` of the writer",
            rusqlite::version()
        ))
    );
}

#[test]
fn refuses_a_module_that_is_not_loaded() {
    assert!(driver_symbol(DRIVER_NOT_LOADED).is_none());
}

#[test]
fn refuses_a_path_with_a_nul_byte() {
    assert!(driver_symbol("libsqlite3.so.0\0_sqlite3").is_none());
}

#[test]
fn refuses_a_different_library_of_the_same_version() {
    let other_library_function: LibVersionFn = ffi::sqlite3_sourceid;
    let refused = compare_libraries(SHARED_SQLITE, Some(other_library_function), writer_function());

    assert_eq!(
        refused,
        Err(format!(
            "SQLite of the driver `{SHARED_SQLITE}` is a different library than SQLite `{}` of the writer",
            rusqlite::version()
        ))
    );
}
