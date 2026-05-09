use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};
use crate::inference::{infer_type, ElemType};
use crate::compat::{Elem, Bool, Int, Secret, Text, AsIs, Float, CSV, Date, DateTime, Decimal, Dict, DictList, List, UTC, UUID};

/// Shorthand for a heap-allocated Python object reference.
type PyObject = Py<PyAny>;

/// Holds parsed metadata about a single I/O element - its name, inferred
/// or explicit type, and whether the element is required on input/output.
#[derive(Clone)]
pub struct ElemInfo {
    /// Element name as declared in the service class.
    pub name: String,

    /// Resolved element type used for coercion and serialization.
    pub elem_type: ElemType,

    /// Whether the element must be present (true) or is optional (false).
    pub is_required: bool,
}

/// Processes I/O declarations on Zato service classes, parsing input/output
/// element definitions and handling type coercion between Python and the
/// wire format during request/response processing.
#[pyclass]
pub struct IOProcessor {
    /// Parsed input element descriptors for the attached service.
    input_elems: Vec<ElemInfo>,

    /// Parsed output element descriptors for the attached service.
    output_elems: Vec<ElemInfo>,

    /// Whether the service uses a Python dataclass for its input/output model.
    #[pyo3(get)]
    pub is_dataclass: bool,

    /// Whether the service declared any input elements.
    #[pyo3(get)]
    pub has_input_declared: bool,

    /// Whether the service declared any output elements.
    #[pyo3(get)]
    pub has_output_declared: bool,

    /// Reference to the Python service class this processor is attached to.
    #[pyo3(get, set)]
    pub service_class: Option<PyObject>,
}

impl IOProcessor {

    /// Resolves the `ElemType` for a bound Python object by checking whether
    /// it is an instance of one of the known I/O element classes.
    fn elem_type_from_instance(item: &Bound<'_, PyAny>) -> Option<ElemType> {
        if item.is_instance_of::<Bool>() { return Some(ElemType::Bool); }
        if item.is_instance_of::<Int>() { return Some(ElemType::Int); }
        if item.is_instance_of::<Secret>() { return Some(ElemType::Secret); }
        if item.is_instance_of::<AsIs>()
            || item.is_instance_of::<Float>()
            || item.is_instance_of::<CSV>()
            || item.is_instance_of::<Date>()
            || item.is_instance_of::<DateTime>()
            || item.is_instance_of::<Decimal>()
            || item.is_instance_of::<Dict>()
            || item.is_instance_of::<DictList>()
            || item.is_instance_of::<List>()
            || item.is_instance_of::<UTC>()
            || item.is_instance_of::<UUID>()
        {
            return Some(ElemType::AsIs);
        }
        if item.is_instance_of::<Text>() { return Some(ElemType::Text); }
        if item.is_instance_of::<Elem>() { return Some(ElemType::Text); }
        None
    }

    /// Parses a single I/O element from either an Elem instance or a bare
    /// string name, extracting the element name, type, and required flag.
    fn parse_single_elem(item: &Bound<'_, PyAny>) -> PyResult<ElemInfo> {
        if let Some(elem_type) = Self::elem_type_from_instance(item) {
            let name: String = item.getattr("name")?.extract()?;
            let is_required: bool = item.getattr("is_required")?.extract()?;
            return Ok(ElemInfo { name, elem_type, is_required });
        }

        let name_str: String = item.extract().map_err(|_extract_err| {
            pyo3::exceptions::PyTypeError::new_err(
                format!("I/O element must be a string or Elem instance, got {}", item.get_type())
            )
        })?;

        #[expect(clippy::option_if_let_else, reason = "strip_prefix borrows name_str, preventing move into closure")]
        let (is_required, clean_name) = if let Some(stripped) = name_str.strip_prefix('-') {
            (false, stripped.to_string())
        } else {
            (true, name_str)
        };
        let elem_type = infer_type(&clean_name);
        Ok(ElemInfo {
            name: clean_name,
            elem_type,
            is_required,
        })
    }

    /// Parses a Python value into a list of `ElemInfo` descriptors, handling
    /// single Elem instances, bare strings, and iterables (tuples, lists).
    fn parse_elem_list(_py: Python<'_>, items: &Bound<'_, PyAny>) -> PyResult<Vec<ElemInfo>> {

        if Self::elem_type_from_instance(items).is_some() {
            return Ok(vec![Self::parse_single_elem(items)?]);
        }

        if items.is_instance_of::<PyString>() {
            return Ok(vec![Self::parse_single_elem(items)?]);
        }

        let mut elems = Vec::new();
        for item in items.try_iter()? {
            let item = item?;
            elems.push(Self::parse_single_elem(&item)?);
        }
        Ok(elems)
    }
}

#[pymethods]
impl IOProcessor {

    /// Creates a new, empty I/O processor with no declared elements.
    #[new]
    const fn new() -> Self {
        Self {
            input_elems: Vec::new(),
            output_elems: Vec::new(),
            is_dataclass: false,
            has_input_declared: false,
            has_output_declared: false,
            service_class: None,
        }
    }

    /// Inspects a Python service class for `input`/`output` attributes, builds
    /// element metadata, and attaches the resulting processor as `_io` on the class.
    #[staticmethod]
    fn attach_io(py: Python<'_>, _server: &Bound<'_, PyAny>, class: &Bound<'_, PyAny>) -> PyResult<()> {
        let io_input = class.getattr("input").ok();
        let io_output = class.getattr("output").ok();

        let has_input = io_input.as_ref().is_some_and(|val| !val.is_none());
        let has_output = io_output.as_ref().is_some_and(|val| !val.is_none());

        if !has_input && !has_output {
            return Ok(());
        }

        let mut proc = Self::new();
        proc.has_input_declared = has_input;
        proc.has_output_declared = has_output;
        proc.service_class = Some(class.clone().unbind());

        if let Some(input) = io_input.filter(|val| !val.is_none()) {
            proc.has_input_declared = true;
            if input.getattr("__dataclass_fields__").is_ok() {
                proc.is_dataclass = true;
            } else {
                proc.input_elems = Self::parse_elem_list(py, &input)?;
            }
        }

        if let Some(output) = io_output.filter(|val| !val.is_none()) {
            proc.has_output_declared = true;
            if output.getattr("__dataclass_fields__").is_ok() {
                proc.is_dataclass = true;
            } else {
                proc.output_elems = Self::parse_elem_list(py, &output)?;
            }
        }

        let proc_obj = Py::new(py, proc)?;
        class.setattr("_io", &proc_obj)?;
        Ok(())
    }

    /// Converts a bare element name into the appropriate typed Elem instance
    /// (Bool, Int, Secret, or Text) based on name-based type inference.
    #[expect(clippy::unused_self, reason = "PyO3 method signature requires &self")]
    fn convert_to_elem_instance<'py>(&self, py: Python<'py>, name: String, _is_required: bool) -> PyResult<Bound<'py, PyAny>> {
        let clean_name = name.strip_prefix('-').map_or_else(
            || name.clone(),
            ToString::to_string,
        );

        let elem_type = infer_type(&clean_name);

        match elem_type {
            ElemType::Bool => {
                let init = Bool::create(name, None);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
            ElemType::Int => {
                let init = Int::create(name, None);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
            ElemType::Secret => {
                let init = Secret::create(name, None);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
            _ => {
                let init = Text::create(name, None);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
        }
    }

    /// Parses raw input data against the declared input elements, coercing
    /// values to their declared types and raising on missing required elements.
    #[pyo3(signature = (data, data_format, extra=None, service=None))]
    #[expect(unused_variables, reason = "data_format and service parameters reserved for future use")]
    fn parse_input(
        &self,
        py: Python<'_>,
        data: &Bound<'_, PyAny>,
        data_format: &str,
        extra: Option<&Bound<'_, PyDict>>,
        service: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<PyObject> {
        if self.input_elems.is_empty() {
            return Ok(py.None());
        }

        let parsed: Bound<'_, PyAny> = if data.is_instance_of::<PyString>() {
            let json_mod = py.import("zato.common.json_internal")?;
            json_mod.call_method1("loads", (data,))?
        } else if data.is_instance_of::<PyDict>() {
            data.clone()
        } else if data.is_none() {
            PyDict::new(py).into_any()
        } else {
            data.clone()
        };

        let result_dict = PyDict::new(py);

        for elem in &self.input_elems {
            let mut value: Option<Bound<'_, PyAny>> = if let Some(extra_dict) = extra
                && let Some(val) = extra_dict.get_item(&elem.name)? {
                Some(val)
            } else {
                None
            };

            if value.is_none() {
                if let Ok(dict) = parsed.cast::<PyDict>() {
                    if let Some(val) = dict.get_item(&elem.name)? {
                        value = Some(val);
                    }
                } else {
                    let py_name = PyString::new(py, &elem.name);
                    if let Ok(val) = parsed.getattr(&py_name) {
                        value = Some(val);
                    }
                }
            }

            if let Some(val) = value {
                let coerced = Self::coerce_value(py, &val, elem.elem_type)?;
                result_dict.set_item(&elem.name, coerced.bind(py))?;
            } else {
                if elem.is_required {
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        format!("Missing required input element: {}", elem.name)
                    ));
                }
                result_dict.set_item(&elem.name, py.None())?;
            }
        }

        Ok(result_dict.into_any().unbind())
    }

    /// Filters a response value through the declared output elements, keeping
    /// only the fields that appear in the output declaration.
    fn get_output<'py>(&self, py: Python<'py>, value: &Bound<'py, PyAny>) -> PyResult<PyObject> {
        if self.output_elems.is_empty() {
            return Ok(value.clone().unbind());
        }

        if value.is_instance_of::<PyList>() || value.cast::<PyTuple>().is_ok() {
            let out = PyList::empty(py);
            for item in value.try_iter()? {
                let item = item?;
                let filtered = self.filter_dict_to_output(py, &item)?;
                out.append(filtered.bind(py))?;
            }
            return Ok(out.into_any().unbind());
        }

        if value.is_instance_of::<PyDict>() {
            return self.filter_dict_to_output(py, value);
        }

        Ok(value.clone().unbind())
    }

    /// Returns the names of all declared output elements.
    #[getter]
    fn all_output_elem_names(&self) -> Vec<String> {
        self.output_elems.iter().map(|elem| elem.name.clone()).collect()
    }

    /// Returns the names of all declared input elements.
    #[getter]
    fn all_input_elem_names(&self) -> Vec<String> {
        self.input_elems.iter().map(|elem| elem.name.clone()).collect()
    }

    /// Evaluates and coerces a single element value according to its inferred
    /// type, optionally encrypting secrets via a caller-supplied function.
    #[pyo3(signature = (elem_name, value, encrypt_func=None))]
    #[expect(clippy::unused_self, reason = "PyO3 method signature requires &self")]
    fn eval_<'py>(
        &self,
        py: Python<'py>,
        elem_name: &str,
        value: &Bound<'py, PyAny>,
        encrypt_func: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<PyObject> {
        let elem_type = infer_type(elem_name);

        match elem_type {
            ElemType::Bool => {
                if value.is_none() || (value.is_instance_of::<PyString>() && value.str()?.to_string().is_empty()) {
                    let bool_val = false;
                    return Ok(bool_val.into_pyobject(py)?.to_owned().into_any().unbind());
                }
                if value.is_instance_of::<pyo3::types::PyBool>() {
                    return Ok(value.clone().unbind());
                }
                let text = value.str()?.to_string().to_lowercase();
                let bool_val = matches!(text.as_str(), "true" | "1" | "yes" | "t" | "on");
                Ok(bool_val.into_pyobject(py)?.to_owned().into_any().unbind())
            }
            ElemType::Int => {
                if value.is_none() || (value.is_instance_of::<PyString>() && value.str()?.to_string().is_empty()) {
                    return Ok(py.None());
                }
                if value.is_instance_of::<pyo3::types::PyInt>() {
                    Ok(value.clone().unbind())
                } else {
                    let builtins = py.import("builtins")?;
                    let result = builtins.call_method1("int", (value,))?;
                    Ok(result.unbind())
                }
            }
            ElemType::Secret => {
                if let Some(func) = encrypt_func {
                    let result = func.call1((value,))?;
                    Ok(result.unbind())
                } else {
                    Ok(value.clone().unbind())
                }
            }
            _ => {
                if value.is_none() || (value.is_instance_of::<PyString>() && value.str()?.to_string().is_empty()) {
                    Ok("".into_pyobject(py)?.into_any().unbind())
                } else {
                    Ok(value.clone().unbind())
                }
            }
        }
    }
}

impl IOProcessor {
    /// Coerces a Python value to the target element type (int, bool, or pass-through).
    fn coerce_value(py: Python<'_>, value: &Bound<'_, PyAny>, elem_type: ElemType) -> PyResult<PyObject> {
        if value.is_none() {
            return Ok(py.None());
        }

        match elem_type {
            ElemType::Int => {
                if value.is_instance_of::<pyo3::types::PyInt>() {
                    Ok(value.clone().unbind())
                } else {
                    let builtins = py.import("builtins")?;
                    let result = builtins.call_method1("int", (value,))?;
                    Ok(result.unbind())
                }
            }
            ElemType::Bool => {
                if value.is_instance_of::<pyo3::types::PyBool>() {
                    return Ok(value.clone().unbind());
                }
                let text = value.str()?.to_string().to_lowercase();
                let bool_val = matches!(text.as_str(), "true" | "1" | "yes");
                Ok(bool_val.into_pyobject(py)?.to_owned().into_any().unbind())
            }
            _ => Ok(value.clone().unbind()),
        }
    }

    /// Extracts only the declared output elements from a dict or object,
    /// returning a filtered Python dict.
    fn filter_dict_to_output(&self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<PyObject> {
        let out = PyDict::new(py);
        if let Ok(dict) = value.cast::<PyDict>() {
            for elem in &self.output_elems {
                if let Some(val) = dict.get_item(&elem.name)? {
                    out.set_item(&elem.name, val)?;
                }
            }
        } else {
            for elem in &self.output_elems {
                let py_name = PyString::new(py, &elem.name);
                if let Ok(val) = value.getattr(&py_name) {
                    out.set_item(&elem.name, val)?;
                }
            }
        }
        Ok(out.into_any().unbind())
    }
}
