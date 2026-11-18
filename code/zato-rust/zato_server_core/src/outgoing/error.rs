//! Errors of an outgoing invocation and the requests exceptions they are raised as.
//!
//! A failed invocation raises the same requests exception class requests itself raises for the same
//! failure, so the retry loop and the transport status classification of Zato outgoing connections
//! treat both transports alike.

use pyo3::prelude::*;

/// Why an invocation did not produce a response.
pub enum TransportError {
    /// A Python exception raised while the transport waited, e.g. a `gevent.Timeout` of the caller,
    /// propagated unchanged.
    Python(PyErr),

    /// The request uses something the transport does not implement and nothing was sent yet,
    /// so the invocation is made through requests instead.
    NeedsRequests,

    /// A connection could not be established within the timeout.
    ConnectTimeout(String),

    /// The endpoint did not send the next part of its response within the timeout.
    ReadTimeout(String),

    /// The connection could not be established, or it was closed or reset before the response arrived.
    Connection(String),

    /// The TLS handshake failed or the endpoint ended the TLS session with an alert.
    Tls(String),

    /// The connection was closed or reset while the body of the response was being read.
    ChunkedEncoding(String),
}

/// The requests exception classes the errors are raised as, imported once per transport.
pub struct RequestsExceptions {
    /// `requests.exceptions.ConnectionError`.
    connection_error: Py<PyAny>,

    /// `requests.exceptions.ConnectTimeout`.
    connect_timeout: Py<PyAny>,

    /// `requests.exceptions.ReadTimeout`.
    read_timeout: Py<PyAny>,

    /// `requests.exceptions.SSLError`.
    ssl_error: Py<PyAny>,

    /// `requests.exceptions.ChunkedEncodingError`.
    chunked_encoding_error: Py<PyAny>,
}

impl RequestsExceptions {
    /// Imports the exception classes from `requests.exceptions`.
    pub fn import(py: Python<'_>) -> PyResult<Self> {
        let module = py.import("requests.exceptions")?;

        Ok(Self {
            connection_error: module.getattr("ConnectionError")?.unbind(),
            connect_timeout: module.getattr("ConnectTimeout")?.unbind(),
            read_timeout: module.getattr("ReadTimeout")?.unbind(),
            ssl_error: module.getattr("SSLError")?.unbind(),
            chunked_encoding_error: module.getattr("ChunkedEncodingError")?.unbind(),
        })
    }

    /// Turns an error into the Python exception it is raised as.
    ///
    /// `NeedsRequests` never reaches this point, because the caller answers it by returning `None` to Python.
    pub fn to_py_err(&self, py: Python<'_>, error: TransportError) -> PyErr {
        let (class, message) = match error {
            TransportError::Python(err) => return err,
            TransportError::NeedsRequests => (&self.connection_error, String::from("Request not supported by the transport")),
            TransportError::ConnectTimeout(message) => (&self.connect_timeout, message),
            TransportError::ReadTimeout(message) => (&self.read_timeout, message),
            TransportError::Connection(message) => (&self.connection_error, message),
            TransportError::Tls(message) => (&self.ssl_error, message),
            TransportError::ChunkedEncoding(message) => (&self.chunked_encoding_error, message),
        };

        // Instantiating a requests exception does not fail for a message argument, but if it ever did,
        // the error of the instantiation is what the caller receives
        match class.call1(py, (message,)) {
            Ok(instance) => PyErr::from_value(instance.into_bound(py)),
            Err(err) => err,
        }
    }
}
