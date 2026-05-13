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
        Ok(Self {
            file,
            path,
            written,
            max_bytes,
        })
    }

    /// Writes `line` to the log, rotating the file first if appending would exceed `max_bytes`.
    #[expect(clippy::as_conversions, reason = "line.len() is a buffer size that will never approach u64::MAX")]
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

/// Fields needed to format a REST summary log line.
pub struct RestLogEntry<'entry> {
    /// OS process ID.
    pub pid: u32,
    /// Correlation ID for the request.
    pub cid: &'entry str,
    /// HTTP status code as a string.
    pub status_code: &'entry str,
    /// Elapsed whole seconds.
    pub delta_sec: i64,
    /// Elapsed microseconds remainder.
    pub delta_usec: i32,
    /// Response body size in bytes.
    pub response_size: usize,
}

/// Formats a Zato REST summary log line.
///
/// Includes timestamp, PID, CID, status, timing and response size.
pub fn format_rest_line(entry: &RestLogEntry<'_>) -> String {
    let now = Local::now();
    let pid = entry.pid;
    let cid = entry.cid;
    let status_code = entry.status_code;
    let delta_sec = entry.delta_sec;
    let delta_usec = entry.delta_usec;
    let response_size = entry.response_size;
    format!(
        "{} - INFO - {pid}:Dummy - zato_rest:0 - REST cha \u{2190} cid={cid}; {status_code} time=0:{delta_sec:02}.{delta_usec:06}; len={response_size}\n",
        now.format("%Y-%m-%d %H:%M:%S,%3f"),
    )
}

/// Fields needed to format an access log line.
pub struct AccessLogEntry<'entry> {
    /// OS process ID.
    pub pid: u32,
    /// Client IP address.
    pub remote_ip: &'entry str,
    /// Correlation ID.
    pub cid: &'entry str,
    /// Response time as a string.
    pub resp_time: &'entry str,
    /// Channel name the request arrived on.
    pub channel_name: &'entry str,
    /// Request timestamp as a string.
    pub req_timestamp: &'entry str,
    /// HTTP method (GET, POST, etc.).
    pub method: &'entry str,
    /// Request path.
    pub path: &'entry str,
    /// HTTP version (HTTP/1.0, HTTP/1.1).
    pub http_version: &'entry str,
    /// HTTP status code as a string.
    pub status_code: &'entry str,
    /// Response body size in bytes.
    pub response_size: usize,
    /// User-Agent header value.
    pub user_agent: &'entry str,
}

/// Formats a Zato access log line in combined log format.
pub fn format_access_line(entry: &AccessLogEntry<'_>) -> String {
    let now = Local::now();
    let pid = entry.pid;
    let remote_ip = entry.remote_ip;
    let cid = entry.cid;
    let resp_time = entry.resp_time;
    let channel_name = entry.channel_name;
    let req_timestamp = entry.req_timestamp;
    let method = entry.method;
    let path = entry.path;
    let http_version = entry.http_version;
    let status_code = entry.status_code;
    let response_size = entry.response_size;
    let user_agent = entry.user_agent;
    format!(
        "{} - INFO - {pid}:Dummy - zato_access_log:0 - \
        {remote_ip} {cid}/{resp_time} \"{channel_name}\" [{req_timestamp}] \"{method} {path} {http_version}\" {status_code} {response_size} \"-\" \"{user_agent}\"\n",
        now.format("%Y-%m-%d %H:%M:%S,%3f"),
    )
}

/// Converts a WSGI environ key back to HTTP header form.
///
/// E.g. `HTTP_USER_AGENT` becomes `user-agent`. Returns `None` if the key lacks the `HTTP_` prefix.
pub fn transform_header_key(wsgi_key: &str) -> Option<String> {
    let rest = wsgi_key.strip_prefix("HTTP_")?;
    let mut header = String::with_capacity(rest.len());
    for byte in rest.bytes() {
        header.push(if byte == b'_' { '-' } else { char::from(byte).to_ascii_lowercase() });
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
    let writer = LogWriter::new(PathBuf::from(path), max_bytes).map_err(|err| pyo3::exceptions::PyIOError::new_err(err.to_string()))?;
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
pub fn log_rest_summary(entry: &RestLogEntry<'_>) {
    let Some(writer_lock) = REST_WRITER.get() else { return };
    let mut writer = writer_lock.lock();
    let line = format_rest_line(entry);
    let _io_result = writer.write_line(line.as_bytes());
}

/// Writes a formatted access log line. Silently drops errors (logging must not crash the server).
pub fn log_access(entry: &AccessLogEntry<'_>) {
    let Some(writer_lock) = ACCESS_WRITER.get() else { return };
    let mut writer = writer_lock.lock();
    let line = format_access_line(entry);
    let _io_result = writer.write_line(line.as_bytes());
}
