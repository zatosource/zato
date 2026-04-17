#[allow(unsafe_code)]
mod accept;
mod connection;
mod headers;
#[allow(unsafe_code)]
pub mod io;
pub mod request;
pub mod response;
#[allow(unsafe_code)]
mod server;
#[allow(unsafe_code)]
mod socket;

pub use server::HTTPServer;
pub use headers::extract_headers;
pub use request::handle_http_request;
pub use request::make_cid_public;

use pyo3::prelude::*;

pub(crate) type PyObject = Py<PyAny>;

use std::sync::atomic::AtomicI32;
use std::sync::Mutex;

pub(crate) static LISTEN_FD: AtomicI32 = AtomicI32::new(-1);
pub(crate) static ACCEPT_WATCHER: Mutex<Option<PyObject>> = Mutex::new(None);

pub(crate) const MAX_HEADERS: usize = 96;
pub(crate) const READ_BUF: usize = 16384;
pub(crate) const MAX_REQUEST_SIZE: usize = 1_048_576;
pub(crate) const LISTEN_BACKLOG: libc::c_int = 2048;
pub(crate) const MAX_BATCH_ACCEPT: usize = 256;
pub(crate) const GEVENT_IO_READ: i32 = 1;
pub(crate) const GEVENT_IO_WRITE: i32 = 2;
