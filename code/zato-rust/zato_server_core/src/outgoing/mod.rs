//! The transport of outgoing REST connections.
//!
//! HTTP/1.1 over plain TCP and TLS, with a pool of connections per endpoint, driven cooperatively through gevent.

/// Parsing of the address of a request.
mod address;

/// Errors of an invocation and the requests exceptions they are raised as.
mod error;

/// New connections, and one request and its response on a connection.
mod exchange;

/// The head of a request.
mod headers;

/// The pool of idle connections.
mod pool;

/// Parsing of a response and decoding of a chunked body.
mod response;

/// Connections read and written without blocking the process.
mod stream;

/// The TLS configuration of connections.
mod tls;

/// The transport class exported to Python.
mod transport;

/// Cooperative waits and name resolution through gevent.
mod wait;

pub use transport::HTTPTransport;
