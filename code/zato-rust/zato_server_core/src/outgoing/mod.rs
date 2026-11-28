//! The transport of outgoing REST connections.
//!
//! HTTP/1.1 over plain TCP and TLS, with a pool of connections per endpoint, driven cooperatively through gevent.

/// Parsing of the address of a request.
pub(crate) mod address;

/// Errors of an invocation and the requests exceptions they are raised as.
pub(crate) mod error;

/// New connections, and one request and its response on a connection.
pub(crate) mod exchange;

/// The head of a request.
pub(crate) mod headers;

/// The pool of idle connections.
pub(crate) mod pool;

/// Parsing of a response and decoding of a chunked body.
mod response;

/// One request sent on a pooled connection or a new one.
pub(crate) mod send;

/// The network scopes of the addresses connections are established to.
pub(crate) mod scope;

/// Connections read and written without blocking the process.
pub(crate) mod stream;

/// The TLS configuration of connections.
pub(crate) mod tls;

/// The transport class exported to Python.
pub(crate) mod transport;

/// Cooperative waits and name resolution through gevent.
mod wait;

pub use transport::HTTPTransport;
