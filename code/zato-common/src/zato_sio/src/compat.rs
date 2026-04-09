use pyo3::prelude::*;
use crate::inference::ElemType;

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct Elem {
    #[pyo3(get, set)]
    pub name: String,
    #[pyo3(get, set)]
    pub is_required: bool,
    pub elem_type: ElemType,
}

#[pymethods]
impl Elem {
    #[new]
    fn new(name: String) -> Self {
        let is_required = !name.starts_with('-');
        let clean_name = if name.starts_with('-') {
            name[1..].to_string()
        } else {
            name
        };
        Self {
            name: clean_name,
            is_required,
            elem_type: ElemType::Text,
        }
    }

    fn __repr__(&self) -> String {
        format!("Elem(name='{}', required={})", self.name, self.is_required)
    }
}

macro_rules! define_elem_type {
    ($name:ident, $variant:expr) => {
        #[pyclass(extends=Elem, from_py_object)]
        #[derive(Clone)]
        pub struct $name;

        impl $name {
            pub fn create(name: String) -> (Self, Elem) {
                let is_required = !name.starts_with('-');
                let clean_name = if name.starts_with('-') {
                    name[1..].to_string()
                } else {
                    name
                };
                ($name, Elem {
                    name: clean_name,
                    is_required,
                    elem_type: $variant,
                })
            }
        }

        #[pymethods]
        impl $name {
            #[new]
            fn new(name: String) -> (Self, Elem) {
                Self::create(name)
            }
        }
    };
}

define_elem_type!(Bool, ElemType::Bool);
define_elem_type!(Int, ElemType::Int);
define_elem_type!(Secret, ElemType::Secret);
define_elem_type!(Text, ElemType::Text);
define_elem_type!(AsIs, ElemType::AsIs);

// Backward-compat types - all behave like AsIs (no conversion)
define_elem_type!(Float, ElemType::AsIs);
define_elem_type!(CSV, ElemType::AsIs);
define_elem_type!(Date, ElemType::AsIs);
define_elem_type!(DateTime, ElemType::AsIs);
define_elem_type!(Decimal, ElemType::AsIs);
define_elem_type!(Dict, ElemType::AsIs);
define_elem_type!(DictList, ElemType::AsIs);
define_elem_type!(List, ElemType::AsIs);
define_elem_type!(UTC, ElemType::AsIs);
define_elem_type!(UUID, ElemType::AsIs);
