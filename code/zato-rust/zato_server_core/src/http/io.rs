//! Low-level fd I/O with gevent yield-on-block.
//!
//! Each operation retries on `EWOULDBLOCK` by registering a gevent IO watcher and
//! yielding the current greenlet until the fd becomes ready.

use pyo3::intern;
use pyo3::prelude::*;

use super::{GEVENT_IO_READ, GEVENT_IO_WRITE, MAX_REQUEST_SIZE, READ_BUF};

/// Gevent event loop references needed for non-blocking I/O.
pub(super) struct GeventLoop<'py> {
    /// The gevent hub instance.
    pub hub: Bound<'py, PyAny>,
    /// The underlying event loop from the hub.
    pub loop_obj: Bound<'py, PyAny>,
}

/// Retries a raw fd operation, yielding to gevent on `EWOULDBLOCK` and retrying on `EINTR`.
fn with_gevent_io<F>(py: Python<'_>, fd: i32, event: i32, gev: &GeventLoop<'_>, mut op_fn: F) -> PyResult<isize>
where
    F: FnMut() -> isize,
{
    loop {
        let result = op_fn();
        if result >= 0 {
            return Ok(result);
        }
        let err = std::io::Error::last_os_error();
        if err.kind() == std::io::ErrorKind::WouldBlock {
            let io_watcher = gev.loop_obj.call_method1(intern!(py, "io"), (fd, event))?;
            gev.hub.call_method1(intern!(py, "wait"), (&io_watcher,))?;
            continue;
        }
        if err.raw_os_error() == Some(libc::EINTR) {
            continue;
        }
        return Err(pyo3::exceptions::PyConnectionError::new_err(format!("fd {fd}: {err}")));
    }
}

/// Reads bytes from `fd` into `buf`, yielding to gevent if the fd would block.
/// Returns the number of bytes read (0 means EOF).
pub(super) fn fd_read(py: Python<'_>, fd: i32, buf: &mut Vec<u8>, gev: &GeventLoop<'_>) -> PyResult<usize> {
    let mut read_buf = [0u8; READ_BUF];
    let bytes_read = with_gevent_io(py, fd, GEVENT_IO_READ, gev, || {
        // SAFETY: fd is a valid socket, read_buf is a stack-local array whose pointer
        // and length are correctly passed. libc::read returns -1 on error (handled above)
        // or the number of bytes read.
        unsafe { libc::read(fd, read_buf.as_mut_ptr().cast::<libc::c_void>(), read_buf.len()) }
    })?
    .cast_unsigned();
    if bytes_read > 0 {
        buf.extend_from_slice(read_buf.get(..bytes_read).unwrap_or(&read_buf));
    }
    Ok(bytes_read)
}

/// Writes all of `data` to `fd`, yielding to gevent as needed until everything is flushed.
pub(super) fn fd_write_all(py: Python<'_>, fd: i32, data: &[u8], gev: &GeventLoop<'_>) -> PyResult<()> {
    let mut offset = 0;
    while offset < data.len() {
        let written = with_gevent_io(py, fd, GEVENT_IO_WRITE, gev, || {
            // SAFETY: fd is a valid socket, data[offset..] is a valid slice whose pointer
            // and remaining length are correctly passed. libc::write returns -1 on error
            // (handled above) or the number of bytes written.
            unsafe { libc::write(fd, data.as_ptr().add(offset).cast::<libc::c_void>(), data.len() - offset) }
        })?;
        if written == 0 {
            return Err(pyo3::exceptions::PyConnectionError::new_err("write returned 0"));
        }
        offset += written.cast_unsigned();
    }
    Ok(())
}

/// Hand-rolled ASCII decimal parser for Content-Length header values.
/// Returns `MAX_REQUEST_SIZE` on overflow to trigger the request-too-large path.
#[inline]
#[expect(clippy::as_conversions, reason = "ASCII digit subtraction yields 0..=9, always fits in usize")]
pub fn parse_content_length(raw: &[u8]) -> usize {
    let mut result: usize = 0;
    for &byte in raw {
        match byte {
            b'0'..=b'9' => {
                result = match result.checked_mul(10).and_then(|val| val.checked_add((byte - b'0') as usize)) {
                    Some(val) if val <= MAX_REQUEST_SIZE => val,
                    _ => return MAX_REQUEST_SIZE,
                };
            }
            b' ' | b'\t' => {}
            _ => break,
        }
    }
    result
}

/// Case-insensitive HTTP header value comparison.
///
/// Strips leading/trailing optional whitespace (OWS) before comparing.
#[inline]
pub fn header_value_eq(raw: &[u8], target: &[u8]) -> bool {
    let trimmed = trim_ows(raw);
    if trimmed.len() != target.len() {
        return false;
    }
    trimmed
        .iter()
        .zip(target)
        .all(|(actual, expected)| actual.to_ascii_lowercase() == *expected)
}

/// Trims optional whitespace (spaces and tabs) from both ends of a byte slice.
#[inline]
#[expect(
    clippy::indexing_slicing,
    reason = "start and end are computed from position/rposition which guarantee they are within bounds"
)]
pub fn trim_ows(raw: &[u8]) -> &[u8] {
    let start = raw.iter().position(|&byte| byte != b' ' && byte != b'\t').unwrap_or(raw.len());
    let end = raw
        .iter()
        .rposition(|&byte| byte != b' ' && byte != b'\t')
        .map_or(start, |pos| pos + 1);
    &raw[start..end]
}
