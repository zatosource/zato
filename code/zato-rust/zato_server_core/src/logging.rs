//! Rotating file loggers for Zato REST summary and access logs.
//!
//! Each writer rotates on overflow: the current file becomes `.log.1`, the previous `.log.1` becomes `.log.2`.

use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use chrono::Local;
use parking_lot::Mutex;
use pyo3::prelude::*;

/// Rotating file writer that keeps at most two backup files (`.log.1` and `.log.2`).
pub struct LogWriter {
    /// Currently open file handle.
    file: File,
    /// Path to the active log file.
    path: PathBuf,
    /// Bytes written to the current file so far (used to decide when to rotate).
    pub written: u64,
    /// Maximum file size in bytes before rotation (0 disables rotation).
    max_bytes: u64,
}

impl LogWriter {
    /// Opens or creates the log file in append mode.
    fn open(path: &Path) -> std::io::Result<File> {
        OpenOptions::new().create(true).append(true).open(path)
    }

    /// Creates a writer for `path`, resuming from the file's current size.
    pub fn new(path: PathBuf, max_bytes: u64) -> std::io::Result<Self> {
        let file = Self::open(&path)?;
        let written = file.metadata()?.len();
        Ok(Self { file, path, written, max_bytes })
    }

    /// Writes `line` to the log, rotating the file first if appending would exceed `max_bytes`.
    #[expect(
        clippy::as_conversions,
        reason = "line.len() is a buffer size that will never approach u64::MAX"
    )]
    pub fn write_line(&mut self, line: &[u8]) -> std::io::Result<()> {
        if self.max_bytes > 0 && self.written + line.len() as u64 > self.max_bytes {
            let backup2 = self.path.with_extension("log.2");
            let backup1 = self.path.with_extension("log.1");

            if backup1.exists() {
                std::fs::rename(&backup1, &backup2)?;
            }
            std::fs::rename(&self.path, &backup1)?;

            let new_file = Self::open(&self.path)?;
            // .. write into the new file first, only commit state if it succeeds.
            {
                let mut buf_writer = std::io::BufWriter::new(&new_file);
                buf_writer.write_all(line)?;
                buf_writer.flush()?;
            }

            self.file = new_file;
            self.written = line.len() as u64;
            return Ok(());
        }
        self.file.write_all(line)?;
        self.written += line.len() as u64;
        Ok(())
    }
}

/// Formats a Zato REST summary log line with timestamp, PID, CID, status, timing and response size.
pub fn format_rest_line(pid: u32, cid: &str, status_code: &str, delta_sec: i64, delta_usec: i32, response_size: usize) -> String {
    let now = Local::now();
    format!(
        "{} - INFO - {pid}:Dummy - zato_rest:0 - REST cha \u{2190} cid={cid}; {status_code} time=0:{delta_sec:02}.{delta_usec:06}; len={response_size}\n",
        now.format("%Y-%m-%d %H:%M:%S,%3f"),
    )
}

/// Formats a Zato access log line in combined log format.
#[expect(clippy::too_many_arguments, reason = "access log format requires all these fields")]
pub fn format_access_line(
    pid: u32, remote_ip: &str, cid: &str, resp_time: &str, channel_name: &str,
    req_timestamp: &str, method: &str, path: &str, http_version: &str,
    status_code: &str, response_size: usize, user_agent: &str,
) -> String {
    let now = Local::now();
    format!(
        "{} - INFO - {pid}:Dummy - zato_access_log:0 - \
        {remote_ip} {cid}/{resp_time} \"{channel_name}\" [{req_timestamp}] \"{method} {path} {http_version}\" {status_code} {response_size} \"-\" \"{user_agent}\"\n",
        now.format("%Y-%m-%d %H:%M:%S,%3f"),
    )
}

/// Converts a WSGI environ key like `HTTP_USER_AGENT` back to its HTTP header form `user-agent`.
/// Returns `None` if the key does not start with `HTTP_`.
pub fn transform_header_key(wsgi_key: &str) -> Option<String> {
    let rest = wsgi_key.strip_prefix("HTTP_")?;
    let mut header = String::with_capacity(rest.len());
    for byte in rest.bytes() {
        header.push(if byte == b'_' { '-' } else { (byte as char).to_ascii_lowercase() });
    }
    Some(header)
}

/// Global REST summary log writer, initialized once from Python via [`init_rest_log`].
static REST_WRITER: OnceLock<Mutex<LogWriter>> = OnceLock::new();

/// Global access log writer, initialized once from Python via [`init_access_log`].
static ACCESS_WRITER: OnceLock<Mutex<LogWriter>> = OnceLock::new();

/// Initializes a global log writer. No-op if the writer was already set (e.g. by another thread).
fn init_writer(cell: &OnceLock<Mutex<LogWriter>>, path: &str, max_bytes: u64) -> PyResult<()> {
    if cell.get().is_some() {
        return Ok(());
    }
    let writer = LogWriter::new(PathBuf::from(path), max_bytes)
        .map_err(|err| pyo3::exceptions::PyIOError::new_err(err.to_string()))?;
    let _already_set = cell.set(Mutex::new(writer));
    Ok(())
}

/// Python-callable initializer for the REST summary log writer.
#[pyfunction]
pub fn init_rest_log(path: &str, max_bytes: u64) -> PyResult<()> {
    init_writer(&REST_WRITER, path, max_bytes)
}

/// Python-callable initializer for the access log writer.
#[pyfunction]
pub fn init_access_log(path: &str, max_bytes: u64) -> PyResult<()> {
    init_writer(&ACCESS_WRITER, path, max_bytes)
}

/// Writes a formatted REST summary line. Silently drops errors (logging must not crash the server).
#[pyfunction]
#[pyo3(signature = (cid, status_code, delta_sec, delta_usec, response_size))]
pub fn log_rest_summary(cid: &str, status_code: &str, delta_sec: i64, delta_usec: i32, response_size: usize) {
    let Some(writer_lock) = REST_WRITER.get() else { return };
    let mut writer = writer_lock.lock();
    let line = format_rest_line(std::process::id(), cid, status_code, delta_sec, delta_usec, response_size);
    let _io_result = writer.write_line(line.as_bytes());
}

/// Writes a formatted access log line. Silently drops errors (logging must not crash the server).
#[pyfunction]
#[pyo3(signature = (remote_ip, cid, resp_time, channel_name, req_timestamp, method, path, http_version, status_code, response_size, user_agent))]
#[expect(clippy::too_many_arguments, reason = "access log format requires all these fields")]
pub fn log_access(
    remote_ip: &str,
    cid: &str,
    resp_time: &str,
    channel_name: &str,
    req_timestamp: &str,
    method: &str,
    path: &str,
    http_version: &str,
    status_code: &str,
    response_size: usize,
    user_agent: &str,
) {
    let Some(writer_lock) = ACCESS_WRITER.get() else { return };
    let mut writer = writer_lock.lock();
    let line = format_access_line(
        std::process::id(), remote_ip, cid, resp_time, channel_name,
        req_timestamp, method, path, http_version, status_code, response_size, user_agent,
    );
    let _io_result = writer.write_line(line.as_bytes());
}
