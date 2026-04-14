use pyo3::prelude::*;
use pyo3::intern;

use super::{READ_BUF, MAX_REQUEST_SIZE, GEVENT_IO_READ, GEVENT_IO_WRITE};

fn with_gevent_io<F>(
    py: Python<'_>,
    fd: i32,
    event: i32,
    hub: &Bound<'_, PyAny>,
    loop_obj: &Bound<'_, PyAny>,
    mut op: F,
) -> PyResult<isize>
where
    F: FnMut() -> isize,
{
    loop {
        let n = op();
        if n >= 0 {
            return Ok(n);
        }
        let err = std::io::Error::last_os_error();
        if err.kind() == std::io::ErrorKind::WouldBlock {
            let w = loop_obj.call_method1(intern!(py, "io"), (fd, event))?;
            hub.call_method1(intern!(py, "wait"), (&w,))?;
            continue;
        }
        if err.raw_os_error() == Some(libc::EINTR) {
            continue;
        }
        return Err(pyo3::exceptions::PyConnectionError::new_err(
            format!("fd {}: {}", fd, err)
        ));
    }
}

pub(super) fn fd_read(
    py: Python<'_>,
    fd: i32,
    buf: &mut Vec<u8>,
    hub: &Bound<'_, PyAny>,
    loop_obj: &Bound<'_, PyAny>,
) -> PyResult<usize> {
    let mut tmp = [0u8; READ_BUF];
    let n = with_gevent_io(py, fd, GEVENT_IO_READ, hub, loop_obj, || unsafe {
        libc::read(fd, tmp.as_mut_ptr() as *mut libc::c_void, tmp.len())
    })? as usize;
    if n > 0 {
        buf.extend_from_slice(&tmp[..n]);
    }
    Ok(n)
}

pub(super) fn fd_write_all(
    py: Python<'_>,
    fd: i32,
    data: &[u8],
    hub: &Bound<'_, PyAny>,
    loop_obj: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let mut off = 0;
    while off < data.len() {
        let n = with_gevent_io(py, fd, GEVENT_IO_WRITE, hub, loop_obj, || unsafe {
            libc::write(fd, data[off..].as_ptr() as *const libc::c_void, data.len() - off)
        })?;
        if n == 0 {
            return Err(pyo3::exceptions::PyConnectionError::new_err("write returned 0"));
        }
        off += n as usize;
    }
    Ok(())
}

#[inline]
pub fn parse_content_length(b: &[u8]) -> usize {
    let mut n: usize = 0;
    for &c in b {
        match c {
            b'0'..=b'9' => {
                n = match n.checked_mul(10).and_then(|v| v.checked_add((c - b'0') as usize)) {
                    Some(v) if v <= MAX_REQUEST_SIZE => v,
                    _ => return MAX_REQUEST_SIZE,
                };
            }
            b' ' | b'\t' => {}
            _ => break,
        }
    }
    n
}

#[inline]
pub fn header_value_eq(raw: &[u8], target: &[u8]) -> bool {
    let trimmed = trim_ows(raw);
    if trimmed.len() != target.len() { return false; }
    trimmed.iter().zip(target).all(|(a, b)| a.to_ascii_lowercase() == *b)
}

#[inline]
pub fn trim_ows(b: &[u8]) -> &[u8] {
    let s = b.iter().position(|&c| c != b' ' && c != b'\t').unwrap_or(b.len());
    let e = b.iter().rposition(|&c| c != b' ' && c != b'\t').map_or(s, |p| p + 1);
    &b[s..e]
}
