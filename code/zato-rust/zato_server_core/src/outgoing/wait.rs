//! Cooperative waits for socket readiness and host name resolution through gevent.
//!
//! The transport never blocks the process. A socket operation that would block is followed by a wait
//! through `gevent.socket.wait_read` or `wait_write`, so the hub schedules other greenlets until the socket
//! is ready, and host names are resolved through gevent's resolver.

use std::net::{IpAddr, SocketAddr, SocketAddrV4, SocketAddrV6};

use pyo3::exceptions::{PyOSError, PyTimeoutError};
use pyo3::prelude::*;
use pyo3::types::{PySequence, PyTuple};

/// The socket type `getaddrinfo` is asked for, `SOCK_STREAM`.
const SOCK_STREAM: i32 = 1;

/// The address family `getaddrinfo` is asked for, `AF_UNSPEC`, so IPv4 and IPv6 addresses are both returned.
const AF_UNSPEC: i32 = 0;

/// Position of the socket address in one entry returned by `getaddrinfo`.
const SOCKADDR_POSITION: usize = 4;

/// Position of the IPv6 flow information in an IPv6 socket address.
const FLOW_INFO_POSITION: usize = 2;

/// Position of the IPv6 scope ID in an IPv6 socket address.
const SCOPE_ID_POSITION: usize = 3;

/// The gevent functions a transport waits and resolves host names through, imported once per transport.
pub struct Gevent {
    /// `gevent.socket.wait_read`, which waits until a descriptor is readable or the timeout expires.
    wait_read: Py<PyAny>,

    /// `gevent.socket.wait_write`, which waits until a descriptor is writable or the timeout expires.
    wait_write: Py<PyAny>,

    /// `gevent.socket.getaddrinfo`, which resolves a host name without blocking the hub.
    getaddrinfo: Py<PyAny>,
}

/// Why a wait for socket readiness did not end with the socket ready.
pub enum WaitError {
    /// The socket did not become ready within the timeout.
    TimedOut,

    /// The wait raised a Python exception other than a timeout, e.g. a `gevent.Timeout` of the caller,
    /// which is propagated unchanged.
    Python(PyErr),
}

/// Why a host name could not be resolved into addresses.
pub enum ResolveError {
    /// The resolver reported that the name does not resolve, with its message.
    Failed(String),

    /// The resolver raised a Python exception other than an OS error, which is propagated unchanged.
    Python(PyErr),
}

impl Gevent {
    /// Imports the gevent socket functions the transport uses.
    pub fn import(py: Python<'_>) -> PyResult<Self> {
        let module = py.import("gevent.socket")?;

        Ok(Self {
            wait_read: module.getattr("wait_read")?.unbind(),
            wait_write: module.getattr("wait_write")?.unbind(),
            getaddrinfo: module.getattr("getaddrinfo")?.unbind(),
        })
    }

    /// Waits until the descriptor is readable, yielding to other greenlets in the meantime.
    pub fn wait_readable(&self, py: Python<'_>, fd: i32, timeout: Option<f64>) -> Result<(), WaitError> {
        wait_on(py, &self.wait_read, fd, timeout)
    }

    /// Waits until the descriptor is writable, yielding to other greenlets in the meantime.
    pub fn wait_writable(&self, py: Python<'_>, fd: i32, timeout: Option<f64>) -> Result<(), WaitError> {
        wait_on(py, &self.wait_write, fd, timeout)
    }

    /// Resolves a host name into the socket addresses to connect to, in the order the resolver returned them.
    pub fn resolve(&self, py: Python<'_>, host: &str, port: u16) -> Result<Vec<SocketAddr>, ResolveError> {
        let entries = match self.getaddrinfo.call1(py, (host, port, AF_UNSPEC, SOCK_STREAM)) {
            Ok(entries) => entries,

            // A name that does not resolve is reported by the resolver as an OS error ..
            Err(err) if err.is_instance_of::<PyOSError>(py) => {
                let message = err.value(py).to_string();
                return Err(ResolveError::Failed(message));
            }

            // .. whereas anything else, e.g. a timeout of the caller, is not the resolver's answer.
            Err(err) => return Err(ResolveError::Python(err)),
        };

        parse_entries(entries.bind(py), port).map_err(ResolveError::Python)
    }
}

/// Invokes one of the gevent wait functions and tells a timeout apart from any other exception.
fn wait_on(py: Python<'_>, func: &Py<PyAny>, fd: i32, timeout: Option<f64>) -> Result<(), WaitError> {
    match func.call1(py, (fd, timeout)) {
        Ok(_) => Ok(()),
        Err(err) if err.is_instance_of::<PyTimeoutError>(py) => Err(WaitError::TimedOut),
        Err(err) => Err(WaitError::Python(err)),
    }
}

/// Turns the entries `getaddrinfo` returned into socket addresses, skipping any whose address does not parse.
fn parse_entries(entries: &Bound<'_, PyAny>, port: u16) -> PyResult<Vec<SocketAddr>> {
    let mut out = Vec::new();

    for entry in entries.try_iter()? {
        let entry = entry?;
        let sockaddr = entry.cast::<PySequence>()?.get_item(SOCKADDR_POSITION)?;
        let sockaddr = sockaddr.cast::<PyTuple>()?;

        let ip_text: String = sockaddr.get_item(0)?.extract()?;

        // An address the resolver returned in a form that is not an IP address cannot be connected to
        let Ok(ip) = ip_text.parse::<IpAddr>() else {
            continue;
        };

        let address = match ip {
            IpAddr::V4(ipv4) => SocketAddr::V4(SocketAddrV4::new(ipv4, port)),
            IpAddr::V6(ipv6) => {
                let flow_info: u32 = sockaddr.get_item(FLOW_INFO_POSITION)?.extract()?;
                let scope_id: u32 = sockaddr.get_item(SCOPE_ID_POSITION)?.extract()?;
                SocketAddr::V6(SocketAddrV6::new(ipv6, port, flow_info, scope_id))
            }
        };

        out.push(address);
    }

    Ok(out)
}
