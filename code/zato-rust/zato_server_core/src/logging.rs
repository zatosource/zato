use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::{Mutex, OnceLock};

use chrono::Local;
use pyo3::prelude::*;

pub struct LogWriter {
    file: File,
    path: PathBuf,
    pub written: u64,
    max_bytes: u64,
}

impl LogWriter {
    fn open(path: &PathBuf) -> std::io::Result<File> {
        OpenOptions::new().create(true).append(true).open(path)
    }

    pub fn new(path: PathBuf, max_bytes: u64) -> std::io::Result<Self> {
        let file = Self::open(&path)?;
        let written = file.metadata()?.len();
        Ok(Self { file, path, written, max_bytes })
    }

    fn rotate(&mut self) -> std::io::Result<()> {
        let backup2 = self.path.with_extension("log.2");
        let backup1 = self.path.with_extension("log.1");

        if backup1.exists() {
            std::fs::rename(&backup1, &backup2)?;
        }
        std::fs::rename(&self.path, &backup1)?;

        self.file = Self::open(&self.path)?;
        self.written = 0;
        Ok(())
    }

    pub fn write_line(&mut self, line: &[u8]) -> std::io::Result<()> {
        if self.max_bytes > 0 && self.written + line.len() as u64 > self.max_bytes {
            self.rotate()?;
        }
        self.file.write_all(line)?;
        self.written += line.len() as u64;
        Ok(())
    }
}

pub fn format_rest_line(pid: u32, cid: &str, status_code: &str, delta_sec: i64, delta_usec: i32, response_size: usize) -> String {
    let now = Local::now();
    format!(
        "{} - INFO - {}:Dummy - zato_rest:0 - REST cha \u{2190} cid={}; {} time=0:{:02}.{:06}; len={}\n",
        now.format("%Y-%m-%d %H:%M:%S,%3f"),
        pid, cid, status_code, delta_sec, delta_usec, response_size,
    )
}

#[expect(clippy::too_many_arguments)]
pub fn format_access_line(
    pid: u32, remote_ip: &str, cid: &str, resp_time: &str, channel_name: &str,
    req_timestamp: &str, method: &str, path: &str, http_version: &str,
    status_code: &str, response_size: usize, user_agent: &str,
) -> String {
    let now = Local::now();
    format!(
        "{} - INFO - {}:Dummy - zato_access_log:0 - \
        {} {}/{} \"{}\" [{}] \"{} {} {}\" {} {} \"-\" \"{}\"\n",
        now.format("%Y-%m-%d %H:%M:%S,%3f"),
        pid, remote_ip, cid, resp_time, channel_name, req_timestamp,
        method, path, http_version, status_code, response_size, user_agent,
    )
}

pub fn transform_header_key(wsgi_key: &str) -> Option<String> {
    let rest = wsgi_key.strip_prefix("HTTP_")?;
    let mut header = String::with_capacity(rest.len());
    for b in rest.bytes() {
        header.push(if b == b'_' { '-' } else { (b as char).to_ascii_lowercase() });
    }
    Some(header)
}

static REST_WRITER: OnceLock<Mutex<LogWriter>> = OnceLock::new();
static ACCESS_WRITER: OnceLock<Mutex<LogWriter>> = OnceLock::new();

fn init_writer(cell: &OnceLock<Mutex<LogWriter>>, path: &str, max_bytes: u64) -> PyResult<()> {
    if cell.get().is_some() {
        return Ok(());
    }
    let writer = LogWriter::new(PathBuf::from(path), max_bytes)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let _ = cell.set(Mutex::new(writer));
    Ok(())
}

#[pyfunction]
pub fn init_rest_log(path: &str, max_bytes: u64) -> PyResult<()> {
    init_writer(&REST_WRITER, path, max_bytes)
}

#[pyfunction]
pub fn init_access_log(path: &str, max_bytes: u64) -> PyResult<()> {
    init_writer(&ACCESS_WRITER, path, max_bytes)
}

#[pyfunction]
#[pyo3(signature = (cid, status_code, delta_sec, delta_usec, response_size))]
pub fn log_rest_summary(cid: &str, status_code: &str, delta_sec: i64, delta_usec: i32, response_size: usize) {
    let Some(writer_lock) = REST_WRITER.get() else { return };
    let Ok(mut writer) = writer_lock.lock() else { return };
    let line = format_rest_line(std::process::id(), cid, status_code, delta_sec, delta_usec, response_size);
    let _ = writer.write_line(line.as_bytes());
}

#[pyfunction]
#[pyo3(signature = (remote_ip, cid, resp_time, channel_name, req_timestamp, method, path, http_version, status_code, response_size, user_agent))]
#[expect(clippy::too_many_arguments)]
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
    let Ok(mut writer) = writer_lock.lock() else { return };
    let line = format_access_line(
        std::process::id(), remote_ip, cid, resp_time, channel_name,
        req_timestamp, method, path, http_version, status_code, response_size, user_agent,
    );
    let _ = writer.write_line(line.as_bytes());
}
