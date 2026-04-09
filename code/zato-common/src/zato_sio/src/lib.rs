#![deny(warnings, dead_code)]

mod inference;
pub mod compat;
mod service_input;
pub mod payload;
pub mod response;
pub mod sio_processor;

use pyo3::prelude::*;

#[pyfunction]
fn is_sio_bool(value: &Bound<'_, PyAny>) -> bool {
    if let Ok(elem) = value.extract::<compat::Elem>() {
        elem.elem_type == inference::ElemType::Bool
    } else {
        false
    }
}

#[pyfunction]
fn is_sio_int(value: &Bound<'_, PyAny>) -> bool {
    if let Ok(elem) = value.extract::<compat::Elem>() {
        elem.elem_type == inference::ElemType::Int
    } else {
        false
    }
}

#[pymodule]
fn zato_sio(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<payload::Payload>()?;
    m.add_class::<response::Response>()?;
    m.add_class::<sio_processor::SIOProcessor>()?;
    m.add_class::<service_input::ServiceInput>()?;

    m.add_class::<compat::Elem>()?;
    m.add_class::<compat::Bool>()?;
    m.add_class::<compat::Int>()?;
    m.add_class::<compat::Secret>()?;
    m.add_class::<compat::Text>()?;
    m.add_class::<compat::AsIs>()?;
    m.add_class::<compat::Float>()?;
    m.add_class::<compat::CSV>()?;
    m.add_class::<compat::Date>()?;
    m.add_class::<compat::DateTime>()?;
    m.add_class::<compat::Decimal>()?;
    m.add_class::<compat::Dict>()?;
    m.add_class::<compat::DictList>()?;
    m.add_class::<compat::List>()?;
    m.add_class::<compat::UTC>()?;
    m.add_class::<compat::UUID>()?;

    m.add("Opaque", m.getattr("AsIs")?)?;
    m.add("Boolean", m.getattr("Bool")?)?;
    m.add("Integer", m.getattr("Int")?)?;
    m.add("Unicode", m.getattr("Text")?)?;
    m.add("ListOfDicts", m.getattr("DictList")?)?;

    m.add_function(wrap_pyfunction!(is_sio_bool, m)?)?;
    m.add_function(wrap_pyfunction!(is_sio_int, m)?)?;

    Ok(())
}
