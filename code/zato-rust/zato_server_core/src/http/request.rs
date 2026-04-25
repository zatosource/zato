//! Main `handle_http_request` Python entrypoint - timestamps the request,
//! dispatches to the worker, logs access/REST summaries, collects Prometheus metrics,
//! and returns `(status, headers, body)`.

use std::sync::OnceLock;

use chrono::{Datelike, FixedOffset, Timelike, Utc};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDateTime, PyDict, PyString, PyTuple, PyTzInfo};

use crate::logging::{log_access, log_rest_summary};

/// Sentinel used when no remote address can be determined from headers.
const NO_REMOTE_ADDRESS: &str = "(None)";

/// Server attributes cached once at first request to avoid repeated Python attribute lookups.
struct CachedServerAttrs {
    /// Whether to add `X-Zato-CID` to response headers.
    needs_x_zato_cid: bool,
    /// Whether access logging is enabled at all.
    needs_access_log: bool,
    /// Whether to log all paths (true) or check `access_log_ignore` (false).
    needs_all_access_log: bool,
    /// Ordered list of environ keys to check for the client IP (e.g. `HTTP_X_FORWARDED_FOR`).
    client_address_headers: Vec<String>,
    /// Path prefixes excluded from access logging.
    access_log_ignore: Vec<String>,
}

/// Lazily initialized server attributes.
static CACHED_ATTRS: OnceLock<CachedServerAttrs> = OnceLock::new();

/// Extracts and caches server attributes from the Python server object.
fn get_cached_attrs(server: &Bound<'_, PyAny>) -> PyResult<&'static CachedServerAttrs> {
    if let Some(cached) = CACHED_ATTRS.get() {
        return Ok(cached);
    }

    let attrs = CachedServerAttrs {
        needs_x_zato_cid: server.getattr("needs_x_zato_cid")?.extract()?,
        needs_access_log: server.getattr("needs_access_log")?.extract()?,
        needs_all_access_log: server.getattr("needs_all_access_log")?.extract()?,
        client_address_headers: server.getattr("client_address_headers")?.extract()?,
        access_log_ignore: {
            let mut items = Vec::new();
            for item in server.getattr("access_log_ignore")?.try_iter()? {
                if let Ok(val) = item?.extract::<String>() {
                    items.push(val);
                }
            }
            items
        },
    };
    let _already_set = CACHED_ATTRS.set(attrs);
    CACHED_ATTRS.get().ok_or_else(|| {
        pyo3::exceptions::PyRuntimeError::new_err("failed to initialize cached server attrs")
    })
}

/// Truncates an internal correlation ID to its first four dash-separated segments
/// for external visibility (e.g. in the `X-Zato-CID` response header).
pub fn make_cid_public(cid: &str) -> String {
    cid.splitn(5, '-').take(4).collect::<Vec<_>>().join("-")
}

/// Converts a chrono `DateTime<FixedOffset>` to a Python `datetime.datetime` with timezone.
#[expect(
    clippy::cast_possible_truncation,
    clippy::as_conversions,
    reason = "chrono month/day/hour/minute/second values are guaranteed to fit in u8"
)]
fn chrono_to_py_datetime<'py>(
    py: Python<'py>,
    dt: &chrono::DateTime<FixedOffset>,
    tz_utc: &Bound<'py, PyTzInfo>,
) -> PyResult<Bound<'py, PyDateTime>> {
    let offset_secs = dt.offset().local_minus_utc();
    let py_offset = if offset_secs == 0 {
        tz_utc.clone().into_any()
    } else {
        let timedelta = py.import("datetime")?.getattr("timedelta")?;
        let delta = timedelta.call1((0, offset_secs))?;
        py.import("datetime")?.getattr("timezone")?.call1((delta,))?
    };
    let py_tz: &Bound<'_, PyTzInfo> = py_offset.cast()?;
    PyDateTime::new(
        py,
        dt.year(),
        dt.month() as u8,
        dt.day() as u8,
        dt.hour() as u8,
        dt.minute() as u8,
        dt.second() as u8,
        dt.timestamp_subsec_micros(),
        Some(py_tz),
    )
}

/// Main request handler called from Python for every HTTP request.
///
/// Timestamps the request, dispatches to the worker's request dispatcher,
/// logs access and REST summaries, collects Prometheus metrics if enabled,
/// and returns `(status_str, headers_dict, body_bytes)`.
#[pyfunction]
#[pyo3(signature = (server, http_environ, new_cid_func, local_tz_offset_secs, **kwargs))]
#[expect(
    clippy::too_many_arguments,
    clippy::too_many_lines,
    clippy::similar_names,
    reason = "PyO3 entrypoint mirrors the Python call signature which requires all these parameters"
)]
#[expect(
    clippy::cast_precision_loss,
    clippy::as_conversions,
    reason = "millisecond-to-float conversion for Prometheus histogram - sub-ms precision loss is acceptable"
)]
pub fn handle_http_request(
    py: Python<'_>,
    server: &Bound<'_, PyAny>,
    http_environ: &Bound<'_, PyDict>,
    new_cid_func: &Bound<'_, PyAny>,
    local_tz_offset_secs: i32,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyTuple>> {

    let cached = get_cached_attrs(server)?;

    let user_agent: String = http_environ
        .get_item("HTTP_USER_AGENT")?
        .map_or_else(|| Ok("(None)".to_owned()), |val| val.extract())?;

    let cid: String = kwargs
        .and_then(|kwargs_dict| kwargs_dict.get_item("cid").ok().flatten())
        .map_or_else(|| new_cid_func.call0()?.extract(), |val| val.extract())?;

    let request_ts_utc = Utc::now();
    let local_offset = FixedOffset::east_opt(local_tz_offset_secs)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("invalid timezone offset"))?;
    let request_ts_local = request_ts_utc.with_timezone(&local_offset);

    let tz_utc: Bound<'_, PyTzInfo> = py
        .import("datetime")?
        .getattr("timezone")?
        .getattr("utc")?
        .cast_into()?;

    let zero_offset = FixedOffset::east_opt(0)
        .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("cannot create UTC offset"))?;

    let py_ts_utc = chrono_to_py_datetime(py, &request_ts_utc.with_timezone(&zero_offset), &tz_utc)?;
    let py_ts_local = chrono_to_py_datetime(py, &request_ts_local, &tz_utc)?;

    http_environ.set_item("zato.local_tz", &py_ts_local.getattr("tzinfo")?)?;
    http_environ.set_item("zato.request_timestamp_utc", &py_ts_utc)?;
    http_environ.set_item("zato.request_timestamp", &py_ts_local)?;

    let response_headers = PyDict::new(py);
    http_environ.set_item("zato.http.response.headers", &response_headers)?;

    if cached.needs_x_zato_cid {
        let pub_cid = make_cid_public(&cid);
        response_headers.set_item("X-Zato-CID", &pub_cid)?;
    }

    let mut remote_addr = NO_REMOTE_ADDRESS.to_owned();
    for name in &cached.client_address_headers {
        if let Some(val) = http_environ.get_item(name.as_str())? {
            let addr_str: String = val.extract()?;
            if !addr_str.is_empty() {
                remote_addr = addr_str;
                break;
            }
        }
    }
    http_environ.set_item("zato.http.remote_addr", &remote_addr)?;

    let worker_store = server.getattr("worker_store")?;
    let dispatcher = worker_store.getattr("request_dispatcher")?;

    let payload_result = dispatcher.call_method1(
        "dispatch",
        (&cid, &py_ts_utc, http_environ, &worker_store, &user_agent, &remote_addr),
    );

    let payload_bytes: Py<PyBytes> = match &payload_result {
        Ok(payload) => {
            if payload.is_none() {
                PyBytes::new(py, b"").unbind()
            } else if payload.is_instance_of::<PyBytes>() {
                payload.extract::<Py<PyBytes>>()?
            } else if payload.is_instance_of::<PyString>() {
                let text: String = payload.extract()?;
                PyBytes::new(py, text.as_bytes()).unbind()
            } else {
                payload.call_method1("encode", ("utf-8",))?.extract::<Py<PyBytes>>()?
            }
        }
        Err(err) => {
            let traceback = err.traceback(py).map_or_else(String::new, |trace| {
                trace.format().unwrap_or_default()
            });
            let error_msg = format!("`{cid}` Exception caught `{err}{traceback}`");

            let logger = py.import("logging")?.call_method1("getLogger", ("zato_rest",))?;
            logger.call_method1("error", (&error_msg,))?;

            http_environ.set_item("zato.http.response.status", "500 Internal Server Error")?;

            let return_tracebacks: bool = server.getattr("return_tracebacks")?.extract()?;
            let payload_str = if return_tracebacks {
                error_msg
            } else {
                server.getattr("default_error_message")?.extract()?
            };
            PyBytes::new(py, payload_str.as_bytes()).unbind()
        }
    };

    let channel_item = http_environ.get_item("zato.channel_item")?;
    let channel_name: String = channel_item
        .and_then(|chan_item| chan_item.call_method1("get", ("name", "-")).ok())
        .map_or_else(|| Ok("-".to_owned()), |val| val.extract())?;

    let status: String = http_environ
        .get_item("zato.http.response.status")?
        .map_or_else(|| Ok("200 OK".to_owned()), |val| val.extract())?;

    let resp_headers_raw = http_environ.get_item("zato.http.response.headers")?;
    let final_headers = PyDict::new(py);
    if let Some(raw_headers) = resp_headers_raw {
        let raw_dict: &Bound<'_, PyDict> = raw_headers.cast()?;
        for (key, val) in raw_dict.iter() {
            let val_str: String = val.str()?.extract()?;
            final_headers.set_item(key, val_str)?;
        }
    }

    let status_code: &str = status.split_whitespace().next().map_or("200", |code| code);
    let response_size: usize = payload_bytes.bind(py).as_bytes().len();

    let path_info: String = http_environ.get_item("PATH_INFO")?
        .map_or_else(|| Ok(String::new()), |val| val.extract())?;

    if cached.needs_access_log {
        let mut should_log = cached.needs_all_access_log;
        if !should_log {
            should_log = !cached.access_log_ignore.contains(&path_info);
        }

        if should_log {
            let access_now = Utc::now();
            let access_delta = access_now - request_ts_utc;
            let resp_time = format!("{}.{:06}",
                access_delta.num_seconds(),
                (access_delta.num_microseconds().unwrap_or(0) % 1_000_000).unsigned_abs(),
            );

            let req_ts_str = request_ts_local.format("%d/%b/%Y:%H:%M:%S %z").to_string();

            let method: String = http_environ.get_item("REQUEST_METHOD")?
                .map_or_else(|| Ok(String::new()), |val| val.extract())?;
            let http_version: String = http_environ.get_item("SERVER_PROTOCOL")?
                .map_or_else(|| Ok(String::new()), |val| val.extract())?;

            log_access(
                &remote_addr, &cid, &resp_time, &channel_name, &req_ts_str,
                &method, &path_info, &http_version, status_code, response_size, &user_agent,
            );
        }
    }

    let delta = Utc::now() - request_ts_utc;

    let has_prometheus: bool = server.getattr("has_prometheus")?.extract()?;
    if has_prometheus {
        let prom_mod = py.import("zato.server.base.parallel.http")?;
        let counter = prom_mod.getattr("zato_http_requests_total")?;
        let hist = prom_mod.getattr("zato_http_request_duration_seconds")?;
        let response_time_secs = delta.num_milliseconds() as f64 / 1000.0;
        let labels_kwargs = PyDict::new(py);
        labels_kwargs.set_item("channel_name", &channel_name)?;
        labels_kwargs.set_item("status_code", status_code)?;
        counter.call_method("labels", (), Some(&labels_kwargs))?.call_method0("inc")?;
        let hist_kwargs = PyDict::new(py);
        hist_kwargs.set_item("channel_name", &channel_name)?;
        hist.call_method("labels", (), Some(&hist_kwargs))?.call_method1("observe", (response_time_secs,))?;
    }

    let rest_log_ignore_obj = server.getattr("rest_log_ignore")?;
    let mut rest_log_ignore: Vec<String> = Vec::new();
    for item in rest_log_ignore_obj.try_iter()? {
        if let Ok(val) = item?.extract::<String>() {
            rest_log_ignore.push(val);
        }
    }

    let should_log_rest = !rest_log_ignore.iter().any(|prefix| path_info.starts_with(prefix));
    if should_log_rest {
        let delta_sec = delta.num_seconds();
        #[expect(clippy::as_conversions, reason = "modulo 1_000_000 guarantees the result fits in i32")]
        let delta_usec = (delta.num_microseconds().unwrap_or(0) % 1_000_000) as i32;
        log_rest_summary(&cid, status_code, delta_sec, delta_usec, response_size);
    }

    Ok(PyTuple::new(py, &[
        PyString::new(py, &status).into_any(),
        final_headers.into_any(),
        payload_bytes.into_bound(py).into_any(),
    ])?.unbind())
}
