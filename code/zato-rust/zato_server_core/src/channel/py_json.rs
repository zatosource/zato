//! Conversion between JSON text and Python objects with the results of `json.loads` and `json.dumps` of Python.
//!
//! Documents and objects whose conversion the Rust code does not reproduce exactly - other encodings than
//! UTF-8, nesting above the depth limit, circular references, invalid input of any kind - are converted
//! by the Python functions themselves, so the result, or the exception raised, is always the one of Python.

use std::collections::HashSet;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyBool, PyBytes, PyDict, PyFloat, PyInt, PyList, PyString, PyTuple};

use super::json_parse::{JsonBuilder, MAX_DEPTH, parse};
use super::json_text::{push_json_float, push_json_string};

/// Number of decimal digits that always fit in a 64-bit signed integer.
const MAX_FAST_INTEGER_DIGITS: usize = 18;

/// Number of spaces of one indentation level of the response JSON.
const INDENT_WIDTH: usize = 4;

/// Codec that turns code points, surrogates included, into a Python string.
const CODE_POINT_CODEC: &str = "utf-32-le";

/// Error handler under which surrogates are decoded as they are.
const SURROGATE_ERRORS: &str = "surrogatepass";

/// `json.loads` of Python.
static JSON_LOADS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

/// `json.dumps` of Python.
static JSON_DUMPS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

/// `json.encoder.encode_basestring_ascii` of Python, which quotes and escapes one string.
static ENCODE_BASESTRING_ASCII: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

/// Produces Python objects from a parsed document.
struct PyJsonBuilder<'py> {
    /// Token of the attached interpreter.
    py: Python<'py>,
}

impl<'py> JsonBuilder for PyJsonBuilder<'py> {
    type Value = Bound<'py, PyAny>;
    type Error = PyErr;

    fn null(&mut self) -> PyResult<Self::Value> {
        Ok(self.py.None().into_bound(self.py))
    }

    fn boolean(&mut self, value: bool) -> PyResult<Self::Value> {
        Ok(PyBool::new(self.py, value).to_owned().into_any())
    }

    fn integer(&mut self, literal: &str) -> PyResult<Self::Value> {
        // Short literals fit into a machine integer, the others are left to int() with its digit limit
        if literal.len() <= MAX_FAST_INTEGER_DIGITS
            && let Ok(value) = literal.parse::<i64>()
        {
            return Ok(value.into_pyobject(self.py)?.into_any());
        }
        self.py.get_type::<PyInt>().call1((literal,))
    }

    fn float(&mut self, literal: &str) -> PyResult<Self::Value> {
        let value: f64 = literal
            .parse()
            .map_err(|error| PyValueError::new_err(format!("{literal}: {error}")))?;
        Ok(PyFloat::new(self.py, value).into_any())
    }

    fn string(&mut self, text: &str) -> PyResult<Self::Value> {
        Ok(PyString::new(self.py, text).into_any())
    }

    fn string_with_surrogates(&mut self, code_points: &[u32]) -> PyResult<Self::Value> {
        let mut encoded = Vec::with_capacity(code_points.len() * 4);
        for code_point in code_points {
            encoded.extend_from_slice(&code_point.to_le_bytes());
        }
        PyBytes::new(self.py, &encoded).call_method1("decode", (CODE_POINT_CODEC, SURROGATE_ERRORS))
    }

    fn array(&mut self, items: Vec<Self::Value>) -> PyResult<Self::Value> {
        Ok(PyList::new(self.py, items)?.into_any())
    }

    fn object(&mut self, members: Vec<(Self::Value, Self::Value)>) -> PyResult<Self::Value> {
        let out = PyDict::new(self.py);
        for (key, value) in members {
            out.set_item(key, value)?;
        }
        Ok(out.into_any())
    }
}

/// Whether `json.loads` would decode the document with another codec than plain UTF-8.
fn needs_codec_detection(payload: &[u8]) -> bool {
    // A byte order mark, or a null byte among the first two, selects UTF-8 with a signature, UTF-16 or UTF-32
    let first = payload.first().copied();
    let second = payload.get(1).copied();
    matches!(first, Some(0x00 | 0xEF | 0xFE | 0xFF)) || second == Some(0x00)
}

/// Parses a request body with the result of `json.loads` of Python.
pub fn parse_json<'py>(py: Python<'py>, payload: &[u8]) -> PyResult<Bound<'py, PyAny>> {
    // Any document the parser does not take as it is goes to Python
    if !needs_codec_detection(payload)
        && let Ok(text) = std::str::from_utf8(payload)
        && let Ok(out) = parse(text, &mut PyJsonBuilder { py })
    {
        return Ok(out);
    }

    // Python parses the document itself and raises the error that belongs to it
    let loads = JSON_LOADS.import(py, "json", "loads")?;
    loads.call1((PyBytes::new(py, payload),))
}

/// Serializes an object with the result of `json.dumps(value, indent=4, default=default)` of Python.
pub fn dump_json(value: &Bound<'_, PyAny>, default: &Bound<'_, PyAny>) -> PyResult<String> {
    let mut encoder = Encoder {
        default,
        markers: HashSet::new(),
        out: String::new(),
    };

    if encoder.encode(value, 0).is_ok() {
        return Ok(encoder.out);
    }

    // Python serializes the object itself and raises the error that belongs to it
    let py = value.py();
    let dumps = JSON_DUMPS.import(py, "json", "dumps")?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("indent", INDENT_WIDTH)?;
    kwargs.set_item("default", default)?;
    dumps.call((value,), Some(&kwargs))?.extract()
}

/// State of one serialization.
struct Encoder<'py, 'default> {
    /// Function that turns an object of an unsupported type into one that can be serialized.
    default: &'default Bound<'py, PyAny>,

    /// Identities of the containers being serialized, for finding circular references.
    markers: HashSet<usize>,

    /// Text produced so far.
    out: String,
}

impl<'py> Encoder<'py, '_> {
    /// Appends the text of one object at the given indentation level.
    fn encode(&mut self, value: &Bound<'py, PyAny>, level: usize) -> PyResult<()> {
        if let Ok(text) = value.cast::<PyString>() {
            return self.push_string(text);
        }
        if value.is_none() {
            self.out.push_str("null");
            return Ok(());
        }
        if let Ok(flag) = value.cast::<PyBool>() {
            self.out.push_str(if flag.is_true() { "true" } else { "false" });
            return Ok(());
        }
        if value.is_instance_of::<PyInt>() {
            return self.push_int(value);
        }
        if let Ok(number) = value.cast::<PyFloat>() {
            push_json_float(&mut self.out, number.value());
            return Ok(());
        }
        self.encode_container(value, level)
    }

    /// Appends the text of a list, a tuple, a dict or an object serialized through the default function.
    fn encode_container(&mut self, value: &Bound<'py, PyAny>, level: usize) -> PyResult<()> {
        // Deeper documents are left to Python, whose recursion limit decides what happens to them
        if level > MAX_DEPTH {
            return Err(PyValueError::new_err("nesting depth exceeded"));
        }

        let marker = value.as_ptr().addr();
        if !self.markers.insert(marker) {
            return Err(PyValueError::new_err("Circular reference detected"));
        }

        let result = if value.is_instance_of::<PyList>() || value.is_instance_of::<PyTuple>() {
            self.encode_list(value, level)
        } else if value.is_instance_of::<PyDict>() {
            self.encode_dict(value, level)
        } else {
            let converted = self.default.call1((value,))?;
            self.encode(&converted, level)
        };

        self.markers.remove(&marker);
        result
    }

    /// Appends a string, quoting it with Python itself if it contains surrogates.
    fn push_string(&mut self, text: &Bound<'py, PyString>) -> PyResult<()> {
        if let Ok(plain) = text.to_str() {
            push_json_string(&mut self.out, plain);
            return Ok(());
        }
        let encode = ENCODE_BASESTRING_ASCII.import(text.py(), "json.encoder", "encode_basestring_ascii")?;
        let quoted: String = encode.call1((text,))?.extract()?;
        self.out.push_str(&quoted);
        Ok(())
    }

    /// Appends an integer as `int.__repr__` writes it.
    fn push_int(&mut self, value: &Bound<'py, PyAny>) -> PyResult<()> {
        if let Ok(small) = value.extract::<i64>() {
            self.out.push_str(&small.to_string());
            return Ok(());
        }
        let repr = value.py().get_type::<PyInt>().getattr("__repr__")?.call1((value,))?;
        self.out.push_str(&repr.extract::<String>()?);
        Ok(())
    }

    /// Appends a new line followed by the indentation of the given level.
    fn push_newline_indent(&mut self, level: usize) {
        self.out.push('\n');
        self.out.extend(std::iter::repeat_n(' ', level * INDENT_WIDTH));
    }

    /// Appends a list or a tuple.
    fn encode_list(&mut self, value: &Bound<'py, PyAny>, level: usize) -> PyResult<()> {
        if !value.is_truthy()? {
            self.out.push_str("[]");
            return Ok(());
        }

        let inner_level = level + 1;
        self.out.push('[');

        for (position, item) in value.try_iter()?.enumerate() {
            if position > 0 {
                self.out.push(',');
            }
            self.push_newline_indent(inner_level);
            self.encode(&item?, inner_level)?;
        }

        self.push_newline_indent(level);
        self.out.push(']');
        Ok(())
    }

    /// Appends a dict.
    fn encode_dict(&mut self, value: &Bound<'py, PyAny>, level: usize) -> PyResult<()> {
        if !value.is_truthy()? {
            self.out.push_str("{}");
            return Ok(());
        }

        let inner_level = level + 1;
        self.out.push('{');

        let items = value.call_method0("items")?;

        for (position, item) in items.try_iter()?.enumerate() {
            let (key, member) = item?.extract::<(Bound<'py, PyAny>, Bound<'py, PyAny>)>()?;
            if position > 0 {
                self.out.push(',');
            }
            self.push_newline_indent(inner_level);
            self.push_key(&key)?;
            self.out.push_str(": ");
            self.encode(&member, inner_level)?;
        }

        self.push_newline_indent(level);
        self.out.push('}');
        Ok(())
    }

    /// Appends a dict key, converted to a string the way `json.dumps` converts keys that are not strings.
    fn push_key(&mut self, key: &Bound<'py, PyAny>) -> PyResult<()> {
        if let Ok(text) = key.cast::<PyString>() {
            return self.push_string(text);
        }

        let mut converted = String::new();

        if let Ok(number) = key.cast::<PyFloat>() {
            push_json_float(&mut converted, number.value());
        } else if let Ok(flag) = key.cast::<PyBool>() {
            converted.push_str(if flag.is_true() { "true" } else { "false" });
        } else if key.is_none() {
            converted.push_str("null");
        } else if key.is_instance_of::<PyInt>() {
            let start = self.out.len();
            self.push_int(key)?;
            converted = self.out.split_off(start);
        } else {
            return Err(PyValueError::new_err("unsupported key type"));
        }

        push_json_string(&mut self.out, &converted);
        Ok(())
    }
}
