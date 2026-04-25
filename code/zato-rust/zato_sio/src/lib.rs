//! Zato SimpleIO (SIO) - type-aware serialisation layer for Zato service definitions.
//!
//! Provides element types (`Bool`, `Int`, `Text`, etc.) that Zato services use
//! to declare their input/output contracts and a processor that drives
//! serialisation, deserialisation, and type inference at runtime.

/// Name-based type inference for SIO element names.
mod inference;

/// Backward-compatible Python element types exposed via PyO3.
pub mod compat;

/// Internal service-input handling.
mod service_input;

/// Payload construction and access.
pub mod payload;

/// Response envelope construction.
pub mod response;

/// Core SIO processing logic.
pub mod sio_processor;

use pyo3::prelude::*;

/// Returns `true` if the given Python value is an SIO `Bool` element.
#[pyfunction]
fn is_sio_bool(value: &Bound<'_, PyAny>) -> bool {
    if let Ok(elem) = value.extract::<compat::Elem>() {
        elem.elem_type == inference::ElemType::Bool
    } else {
        false
    }
}

/// Returns `true` if the given Python value is an SIO `Int` element.
#[pyfunction]
fn is_sio_int(value: &Bound<'_, PyAny>) -> bool {
    if let Ok(elem) = value.extract::<compat::Elem>() {
        elem.elem_type == inference::ElemType::Int
    } else {
        false
    }
}

/// Registers all SIO types, aliases, and helper functions with the Python module.
#[pymodule]
fn zato_sio(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<payload::Payload>()?;
    module.add_class::<response::Response>()?;
    module.add_class::<sio_processor::SIOProcessor>()?;
    module.add_class::<service_input::ServiceInput>()?;

    module.add_class::<compat::Elem>()?;
    module.add_class::<compat::Bool>()?;
    module.add_class::<compat::Int>()?;
    module.add_class::<compat::Secret>()?;
    module.add_class::<compat::Text>()?;
    module.add_class::<compat::AsIs>()?;
    module.add_class::<compat::Float>()?;
    module.add_class::<compat::CSV>()?;
    module.add_class::<compat::Date>()?;
    module.add_class::<compat::DateTime>()?;
    module.add_class::<compat::Decimal>()?;
    module.add_class::<compat::Dict>()?;
    module.add_class::<compat::DictList>()?;
    module.add_class::<compat::List>()?;
    module.add_class::<compat::UTC>()?;
    module.add_class::<compat::UUID>()?;

    module.add("Opaque", module.getattr("AsIs")?)?;
    module.add("Boolean", module.getattr("Bool")?)?;
    module.add("Integer", module.getattr("Int")?)?;
    module.add("Unicode", module.getattr("Text")?)?;
    module.add("ListOfDicts", module.getattr("DictList")?)?;

    module.add_function(wrap_pyfunction!(is_sio_bool, module)?)?;
    module.add_function(wrap_pyfunction!(is_sio_int, module)?)?;

    Ok(())
}
