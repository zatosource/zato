use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};
use crate::inference::{infer_type, ElemType};
use crate::compat::{Elem, Bool, Int, Secret, Text, AsIs, Float, CSV, Date, DateTime, Decimal, Dict, DictList, List, UTC, UUID};

type PyObject = Py<PyAny>;

#[derive(Clone)]
pub struct ElemInfo {
    pub name: String,
    pub elem_type: ElemType,
    pub is_required: bool,
}

#[pyclass]
pub struct SIOProcessor {
    input_elems: Vec<ElemInfo>,
    output_elems: Vec<ElemInfo>,

    #[pyo3(get)]
    pub is_dataclass: bool,

    #[pyo3(get)]
    pub has_input_declared: bool,

    #[pyo3(get)]
    pub has_output_declared: bool,

    #[pyo3(get, set)]
    pub service_class: Option<PyObject>,
}

impl SIOProcessor {

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

    fn parse_single_elem(item: &Bound<'_, PyAny>) -> PyResult<ElemInfo> {
        if let Some(elem_type) = Self::elem_type_from_instance(item) {
            let name: String = item.getattr("name")?.extract()?;
            let is_required: bool = item.getattr("is_required")?.extract()?;
            return Ok(ElemInfo { name, elem_type, is_required });
        }

        let name_str: String = item.extract().map_err(|_| {
            pyo3::exceptions::PyTypeError::new_err(
                format!("SIO element must be a string or Elem instance, got {}", item.get_type())
            )
        })?;

        let is_required = !name_str.starts_with('-');
        let clean_name = if name_str.starts_with('-') {
            name_str[1..].to_string()
        } else {
            name_str
        };
        let elem_type = infer_type(&clean_name);
        Ok(ElemInfo {
            name: clean_name,
            elem_type,
            is_required,
        })
    }

    fn parse_elem_list(_py: Python<'_>, items: &Bound<'_, PyAny>) -> PyResult<Vec<ElemInfo>> {

        // Single Elem instance (e.g. input = AsIs('data'))
        if Self::elem_type_from_instance(items).is_some() {
            return Ok(vec![Self::parse_single_elem(items)?]);
        }

        // Single bare string (e.g. input = 'name') - do not iterate chars
        if items.is_instance_of::<PyString>() {
            return Ok(vec![Self::parse_single_elem(items)?]);
        }

        // Iterable (tuple or list)
        let mut elems = Vec::new();
        for item in items.try_iter()? {
            let item = item?;
            elems.push(Self::parse_single_elem(&item)?);
        }
        Ok(elems)
    }
}

#[pymethods]
impl SIOProcessor {

    #[new]
    fn new() -> Self {
        Self {
            input_elems: Vec::new(),
            output_elems: Vec::new(),
            is_dataclass: false,
            has_input_declared: false,
            has_output_declared: false,
            service_class: None,
        }
    }

    #[staticmethod]
    fn attach_sio(py: Python<'_>, _server: &Bound<'_, PyAny>, _server_config: &Bound<'_, PyAny>, class: &Bound<'_, PyAny>) -> PyResult<()> {
        let sio_input = class.getattr("input").ok();
        let sio_output = class.getattr("output").ok();

        let has_input = sio_input.as_ref().is_some_and(|v| !v.is_none());
        let has_output = sio_output.as_ref().is_some_and(|v| !v.is_none());

        if !has_input && !has_output {
            return Ok(());
        }

        let mut proc = SIOProcessor::new();
        proc.has_input_declared = has_input;
        proc.has_output_declared = has_output;
        proc.service_class = Some(class.clone().unbind());

        if has_input {
            let input = sio_input.unwrap();
            if input.getattr("__dataclass_fields__").is_ok() {
                proc.is_dataclass = true;
            } else {
                proc.input_elems = Self::parse_elem_list(py, &input)?;
            }
        }

        if has_output {
            let output = sio_output.unwrap();
            if output.getattr("__dataclass_fields__").is_ok() {
                proc.is_dataclass = true;
            } else {
                proc.output_elems = Self::parse_elem_list(py, &output)?;
            }
        }

        let proc_obj = Py::new(py, proc)?;
        class.setattr("_sio", &proc_obj)?;
        Ok(())
    }

    fn convert_to_elem_instance<'py>(&self, py: Python<'py>, name: String, _is_required: bool) -> PyResult<Bound<'py, PyAny>> {
        let clean_name = if name.starts_with('-') {
            name[1..].to_string()
        } else {
            name.clone()
        };

        let elem_type = infer_type(&clean_name);

        match elem_type {
            ElemType::Bool => {
                let init = Bool::create(name);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
            ElemType::Int => {
                let init = Int::create(name);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
            ElemType::Secret => {
                let init = Secret::create(name);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
            _ => {
                let init = Text::create(name);
                Ok(Py::new(py, init)?.into_bound(py).into_any())
            }
        }
    }

    #[pyo3(signature = (data, data_format, extra=None, service=None))]
    #[allow(unused_variables)]
    fn parse_input(
        &self,
        py: Python<'_>,
        data: &Bound<'_, PyAny>,
        data_format: &str,
        extra: Option<&Bound<'_, PyDict>>,
        service: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<PyObject> {
        if self.input_elems.is_empty() {
            return Ok(py.None().into());
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
            let mut value: Option<Bound<'_, PyAny>> = None;

            if let Some(extra_dict) = extra {
                if let Some(v) = extra_dict.get_item(&elem.name)? {
                    value = Some(v);
                }
            }

            if value.is_none() {
                if let Ok(dict) = parsed.cast::<PyDict>() {
                    if let Some(v) = dict.get_item(&elem.name)? {
                        value = Some(v);
                    }
                } else {
                    let py_name = PyString::new(py, &elem.name);
                    if let Ok(v) = parsed.getattr(&py_name) {
                        value = Some(v);
                    }
                }
            }

            match value {
                Some(v) => {
                    let coerced = self.coerce_value(py, &v, elem.elem_type)?;
                    result_dict.set_item(&elem.name, coerced.bind(py))?;
                }
                None => {
                    if elem.is_required {
                        return Err(pyo3::exceptions::PyValueError::new_err(
                            format!("Missing required input element: {}", elem.name)
                        ));
                    }
                    result_dict.set_item(&elem.name, py.None())?;
                }
            }
        }

        Ok(result_dict.into_any().unbind())
    }

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

    #[getter]
    fn all_output_elem_names(&self) -> Vec<String> {
        self.output_elems.iter().map(|e| e.name.clone()).collect()
    }

    #[getter]
    fn all_input_elem_names(&self) -> Vec<String> {
        self.input_elems.iter().map(|e| e.name.clone()).collect()
    }

    #[pyo3(signature = (elem_name, value, encrypt_func=None))]
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
                    let b = false;
                    return Ok(b.into_pyobject(py)?.to_owned().into_any().unbind());
                }
                if value.is_instance_of::<pyo3::types::PyBool>() {
                    return Ok(value.clone().unbind());
                }
                let s = value.str()?.to_string().to_lowercase();
                let b = matches!(s.as_str(), "true" | "1" | "yes" | "t" | "on");
                Ok(b.into_pyobject(py)?.to_owned().into_any().unbind())
            }
            ElemType::Int => {
                if value.is_none() || (value.is_instance_of::<PyString>() && value.str()?.to_string().is_empty()) {
                    return Ok(py.None().into());
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

impl SIOProcessor {
    fn coerce_value(&self, py: Python<'_>, value: &Bound<'_, PyAny>, elem_type: ElemType) -> PyResult<PyObject> {
        if value.is_none() {
            return Ok(py.None().into());
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
                let s = value.str()?.to_string().to_lowercase();
                let b = matches!(s.as_str(), "true" | "1" | "yes");
                Ok(b.into_pyobject(py)?.to_owned().into_any().unbind())
            }
            _ => Ok(value.clone().unbind()),
        }
    }

    fn filter_dict_to_output(&self, py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<PyObject> {
        let out = PyDict::new(py);
        if let Ok(dict) = value.cast::<PyDict>() {
            for elem in &self.output_elems {
                if let Some(v) = dict.get_item(&elem.name)? {
                    out.set_item(&elem.name, v)?;
                }
            }
        } else {
            for elem in &self.output_elems {
                let py_name = PyString::new(py, &elem.name);
                if let Ok(v) = value.getattr(&py_name) {
                    out.set_item(&elem.name, v)?;
                }
            }
        }
        Ok(out.into_any().unbind())
    }
}
