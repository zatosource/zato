use pyo3::prelude::*;
use pyo3::Borrowed;

use crate::inference::ElemType;

/// Base SIO element exposed to Python, carrying the element name, whether it
/// is required, and the inferred (or explicit) element type.
#[pyclass(subclass, skip_from_py_object)]
#[derive(Clone)]
pub struct Elem {
    /// Element name as declared by the Zato service.
    #[pyo3(get, set)]
    pub name: String,
    /// Whether the element is required (`true`) or optional (name prefixed with `-`).
    #[pyo3(get, set)]
    pub is_required: bool,
    /// Resolved SIO type for this element.
    pub elem_type: ElemType,
}

impl<'obj, 'py> FromPyObject<'obj, 'py> for Elem {
    type Error = PyErr;

    /// Extracts an `Elem` by cloning the Rust struct out of its Python wrapper.
    fn extract(obj: Borrowed<'obj, 'py, PyAny>) -> Result<Self, Self::Error> {
        let borrowed: Borrowed<'obj, 'py, Self> = obj.cast()?;
        Ok(borrowed.borrow().clone())
    }
}

#[pymethods]
impl Elem {
    /// Creates a new `Elem`, stripping a leading `-` to mark the element as optional.
    #[new]
    #[expect(clippy::option_if_let_else, reason = "strip_prefix borrows name, preventing move into closure")]
    fn new(name: String) -> Self {
        let (is_required, clean_name) = if let Some(stripped) = name.strip_prefix('-') {
            (false, stripped.to_string())
        } else {
            (true, name)
        };
        Self {
            name: clean_name,
            is_required,
            elem_type: ElemType::Text,
        }
    }

    /// Python `repr()` showing the element name and whether it is required.
    fn __repr__(&self) -> String {
        format!("Elem(name='{}', required={})", self.name, self.is_required)
    }
}

/// Defines a concrete SIO element subtype exposed to Python that extends `Elem`.
macro_rules! define_elem_type {
    ($name:ident, $variant:expr) => {
        #[doc = concat!("SIO element subtype `", stringify!($name), "` exposed to Python.")]
        #[allow(clippy::upper_case_acronyms, reason = "Python-visible type names must match existing API")]
        #[pyclass(extends=Elem, skip_from_py_object)]
        #[derive(Clone)]
        pub struct $name;

        impl $name {
            /// Builds the subtype together with its parent `Elem`, handling the optional `-` prefix.
            pub fn create(name: String) -> (Self, Elem) {
                let (is_required, clean_name) = if let Some(stripped) = name.strip_prefix('-') {
                    (false, stripped.to_string())
                } else {
                    (true, name)
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
            /// Creates a new instance from the element name, delegating to `create`.
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
