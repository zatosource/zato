//! Main `handle_http_request` Python entrypoint.
//!
//! Timestamps the request, dispatches to the worker, logs access/REST summaries,
//! collects Prometheus metrics, and returns `(status, headers, body)`.

use std::sync::OnceLock;

use chrono::{DateTime, Datelike, FixedOffset, TimeDelta, Timelike, Utc};
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDateTime, PyDict, PyString, PyTuple, PyTzInfo};

use crate::logging::{AccessLogEntry, RestLogEntry, log_access, log_rest_summary};

/// Sentinel used when no remote address can be determined from headers.
const NO_REMOTE_ADDRESS: &str = "(None)";

/// Sentinel used when the client sent no `User-Agent` header.
const NO_USER_AGENT: &str = "(None)";

/// Placeholder logged when the channel item carries no name or no service name.
const NO_CHANNEL_VALUE: &str = "-";

/// Status line assumed when the dispatcher did not set one.
const DEFAULT_STATUS: &str = "200 OK";

/// Status code assumed when the status line is empty.
const DEFAULT_STATUS_CODE: &str = "200";

/// Value used for optional WSGI keys, such as `PATH_INFO`, that the request context lacks.
const NO_CTX_VALUE: &str = "";

/// Microseconds in one second, for splitting a duration into whole seconds and a remainder.
const MICROS_PER_SECOND: i64 = 1_000_000;

/// Microseconds assumed when a duration is too long to be expressed in them.
const NO_MICROS: i64 = 0;

/// Server attributes cached once at first request to avoid repeated Python attribute lookups.
struct CachedServerAttrs {
    /// Whether to add `X-Zato-CID` to response headers.
    needs_x_zato_cid: bool,
    /// Whether access logging is enabled at all.
    needs_access_log: bool,
    /// Whether to log all paths (true) or check `access_log_ignore` (false).
    needs_all_access_log: bool,
    /// Ordered list of request context keys to check for the client IP (e.g. `HTTP_X_FORWARDED_FOR`).
    client_address_headers: Vec<String>,
    /// Path prefixes excluded from access logging.
    access_log_ignore: Vec<String>,
}

/// Lazily initialized server attributes.
static CACHED_ATTRS: OnceLock<CachedServerAttrs> = OnceLock::new();

/// What the access log, the REST summary and the Prometheus metrics report about one finished request.
struct RequestSummary<'req> {
    /// Correlation ID of the request.
    cid: &'req str,
    /// Client address resolved from the configured request headers.
    remote_addr: &'req str,
    /// Name of the REST channel the request arrived on.
    channel_name: &'req str,
    /// Name of the service the channel invoked.
    service_name: &'req str,
    /// Request path, matched against the access log and REST log ignore lists.
    path_info: &'req str,
    /// Numeric part of the response status line.
    status_code: &'req str,
    /// Size of a regular response body in bytes, zero for a streaming one.
    response_size: usize,
    /// Value of the client's `User-Agent` header.
    user_agent: &'req str,
    /// When the request arrived, in UTC.
    request_ts_utc: DateTime<Utc>,
    /// When the request arrived, in the server's local timezone.
    request_ts_local: DateTime<FixedOffset>,
    /// Whether the dispatcher raised an exception instead of returning a payload.
    dispatch_had_error: bool,
}

/// Collects the string items of a Python iterable, skipping any item that is not a string.
fn extract_string_list(iterable: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    let mut items = Vec::new();
    for item in iterable.try_iter()? {
        if let Ok(val) = item?.extract::<String>() {
            items.push(val);
        }
    }
    Ok(items)
}

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
        access_log_ignore: extract_string_list(&server.getattr("access_log_ignore")?)?,
    };
    let _already_set = CACHED_ATTRS.set(attrs);
    CACHED_ATTRS
        .get()
        .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("failed to initialize cached server attrs"))
}

/// Truncates an internal correlation ID for external visibility.
///
/// Keeps only the first four dash-separated segments (e.g. for `X-Zato-CID`).
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

/// Reads a string from the request context, falling back to `default` when the key is absent.
fn get_ctx_string(request_ctx: &Bound<'_, PyDict>, key: &str, default: &str) -> PyResult<String> {
    request_ctx
        .get_item(key)?
        .map_or_else(|| Ok(default.to_owned()), |val| val.extract())
}

/// Reads a field of the channel item, falling back to a placeholder when the item or the field is missing.
fn get_channel_field(channel_item: Option<&Bound<'_, PyAny>>, key: &str) -> PyResult<String> {
    channel_item
        .and_then(|chan_item| chan_item.call_method1("get", (key, NO_CHANNEL_VALUE)).ok())
        .map_or_else(|| Ok(NO_CHANNEL_VALUE.to_owned()), |val| val.extract())
}

/// Sub-second part of a duration in microseconds, for `seconds.micros` style log fields.
fn fractional_micros(delta: TimeDelta) -> i64 {
    delta.num_microseconds().unwrap_or(NO_MICROS) % MICROS_PER_SECOND
}

/// Calls `inc` or `dec` on the gauge counting requests currently being processed.
fn adjust_requests_in_flight(py: Python<'_>, method: &str) -> PyResult<()> {
    let prom_mod = py.import("zato.server.metrics")?;
    let in_flight = prom_mod.getattr("zato_server_requests_in_flight")?;
    in_flight.call_method0(method)?;
    Ok(())
}

/// Stores the UTC and local request timestamps and the local timezone in the request context.
///
/// Returns the UTC timestamp, which the dispatcher also receives directly.
fn set_request_timestamps<'py>(
    request_ctx: &Bound<'py, PyDict>,
    request_ts_utc: &DateTime<Utc>,
    request_ts_local: &DateTime<FixedOffset>,
) -> PyResult<Bound<'py, PyDateTime>> {
    let py = request_ctx.py();
    let tz_utc: Bound<'_, PyTzInfo> = py.import("datetime")?.getattr("timezone")?.getattr("utc")?.cast_into()?;

    let zero_offset = FixedOffset::east_opt(0).ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("cannot create UTC offset"))?;

    let py_ts_utc = chrono_to_py_datetime(py, &request_ts_utc.with_timezone(&zero_offset), &tz_utc)?;
    let py_ts_local = chrono_to_py_datetime(py, request_ts_local, &tz_utc)?;

    request_ctx.set_item("zato.local_tz", &py_ts_local.getattr("tzinfo")?)?;
    request_ctx.set_item("zato.request_timestamp_utc", &py_ts_utc)?;
    request_ctx.set_item("zato.request_timestamp", &py_ts_local)?;

    Ok(py_ts_utc)
}

/// Returns the first non-empty client address found under the configured request context keys.
fn resolve_remote_addr(request_ctx: &Bound<'_, PyDict>, cached: &CachedServerAttrs) -> PyResult<String> {
    for name in &cached.client_address_headers {
        if let Some(val) = request_ctx.get_item(name.as_str())? {
            let addr_str: String = val.extract()?;
            if !addr_str.is_empty() {
                return Ok(addr_str);
            }
        }
    }
    Ok(NO_REMOTE_ADDRESS.to_owned())
}

/// Logs an exception raised by the dispatcher and builds the body of the 500 response it turns into.
///
/// The body is the traceback itself if the server returns tracebacks, or its default error message otherwise.
fn build_error_body(server: &Bound<'_, PyAny>, request_ctx: &Bound<'_, PyDict>, cid: &str, err: &PyErr) -> PyResult<Py<PyBytes>> {
    let py = server.py();
    let traceback = err
        .traceback(py)
        .map_or_else(String::new, |trace| trace.format().unwrap_or_default());
    let error_msg = format!("`{cid}` Exception caught `{err}{traceback}`");

    let logger = py.import("logging")?.call_method1("getLogger", ("zato_rest",))?;
    logger.call_method1("error", (&error_msg,))?;

    request_ctx.set_item("zato.http.response.status", "500 Internal Server Error")?;

    let return_tracebacks: bool = server.getattr("return_tracebacks")?.extract()?;
    let payload_str = if return_tracebacks {
        error_msg
    } else {
        server.getattr("default_error_message")?.extract()?
    };
    Ok(PyBytes::new(py, payload_str.as_bytes()).unbind())
}

/// Converts what the dispatcher returned for a regular, non-streaming response into the response body.
fn payload_to_bytes(payload: &Bound<'_, PyAny>) -> PyResult<Py<PyBytes>> {
    let py = payload.py();
    if payload.is_none() {
        Ok(PyBytes::new(py, b"").unbind())
    } else if payload.is_instance_of::<PyBytes>() {
        Ok(payload.extract::<Py<PyBytes>>()?)
    } else if payload.is_instance_of::<PyString>() {
        let text: String = payload.extract()?;
        Ok(PyBytes::new(py, text.as_bytes()).unbind())
    } else {
        Ok(payload.call_method1("encode", ("utf-8",))?.extract::<Py<PyBytes>>()?)
    }
}

/// Copies the response headers the service set into a fresh dict, turning each value into a string.
fn collect_response_headers<'py>(request_ctx: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyDict>> {
    let final_headers = PyDict::new(request_ctx.py());
    if let Some(raw_headers) = request_ctx.get_item("zato.http.response.headers")? {
        let raw_dict: &Bound<'_, PyDict> = raw_headers.cast()?;
        for (key, val) in raw_dict.iter() {
            let val_str: String = val.str()?.extract()?;
            final_headers.set_item(key, val_str)?;
        }
    }
    Ok(final_headers)
}

/// Writes the access log line for the request, unless its path is on the ignore list.
fn write_access_log(request_ctx: &Bound<'_, PyDict>, cached: &CachedServerAttrs, summary: &RequestSummary<'_>) -> PyResult<()> {
    // The ignore list only applies when the server is not configured to log every path
    let is_ignored = !cached.needs_all_access_log && cached.access_log_ignore.iter().any(|ignored| ignored == summary.path_info);
    if is_ignored {
        return Ok(());
    }

    let access_delta = Utc::now() - summary.request_ts_utc;
    let resp_time = format!(
        "{}.{:06}",
        access_delta.num_seconds(),
        fractional_micros(access_delta).unsigned_abs(),
    );

    let req_ts_str = summary.request_ts_local.format("%d/%b/%Y:%H:%M:%S %z").to_string();

    let method = get_ctx_string(request_ctx, "REQUEST_METHOD", NO_CTX_VALUE)?;
    let http_version = get_ctx_string(request_ctx, "SERVER_PROTOCOL", NO_CTX_VALUE)?;

    log_access(&AccessLogEntry {
        pid: std::process::id(),
        remote_ip: summary.remote_addr,
        cid: summary.cid,
        resp_time: &resp_time,
        channel_name: summary.channel_name,
        req_timestamp: &req_ts_str,
        method: &method,
        path: summary.path_info,
        http_version: &http_version,
        status_code: summary.status_code,
        response_size: summary.response_size,
        user_agent: summary.user_agent,
    });
    Ok(())
}

/// Records the REST channel and service metrics for the request, if Prometheus is enabled on the server.
fn record_prometheus_metrics(server: &Bound<'_, PyAny>, summary: &RequestSummary<'_>, elapsed: TimeDelta) -> PyResult<()> {
    let has_prometheus: bool = server.getattr("has_prometheus")?.extract()?;
    if !has_prometheus {
        return Ok(());
    }

    let py = server.py();
    let prom_mod = py.import("zato.server.metrics")?;
    let counter = prom_mod.getattr("zato_rest_channel_requests_total")?;
    let hist = prom_mod.getattr("zato_rest_channel_request_duration_seconds")?;
    let response_time_secs = elapsed.as_seconds_f64();

    let get_status_code_class = prom_mod.getattr("get_status_code_class")?;
    let status_class: String = get_status_code_class.call1((summary.status_code,))?.extract()?;

    let get_error_source = prom_mod.getattr("get_error_source_from_status_class")?;
    let error_source: String = get_error_source.call1((&status_class,))?.extract()?;

    let labels_kwargs = PyDict::new(py);
    labels_kwargs.set_item("channel_name", summary.channel_name)?;
    labels_kwargs.set_item("status_code", &status_class)?;
    labels_kwargs.set_item("error_source", &error_source)?;
    counter.call_method("labels", (), Some(&labels_kwargs))?.call_method0("inc")?;

    let hist_kwargs = PyDict::new(py);
    hist_kwargs.set_item("channel_name", summary.channel_name)?;
    hist.call_method("labels", (), Some(&hist_kwargs))?
        .call_method1("observe", (response_time_secs,))?;

    let svc_counter = prom_mod.getattr("zato_service_invocations_total")?;
    let svc_hist = prom_mod.getattr("zato_service_duration_seconds")?;
    let outcome = if summary.dispatch_had_error { "error" } else { "ok" };

    let svc_labels = PyDict::new(py);
    svc_labels.set_item("service_name", summary.service_name)?;
    svc_labels.set_item("outcome", outcome)?;
    svc_counter.call_method("labels", (), Some(&svc_labels))?.call_method0("inc")?;

    let svc_hist_labels = PyDict::new(py);
    svc_hist_labels.set_item("service_name", summary.service_name)?;
    svc_hist
        .call_method("labels", (), Some(&svc_hist_labels))?
        .call_method1("observe", (response_time_secs,))?;

    Ok(())
}

/// Writes the REST summary line for the request, unless it is an internal invocation or its path is ignored.
fn write_rest_summary(server: &Bound<'_, PyAny>, summary: &RequestSummary<'_>, elapsed: TimeDelta) -> PyResult<()> {
    let rest_log_ignore = extract_string_list(&server.getattr("rest_log_ignore")?)?;

    let is_internal_invoke = summary.channel_name == "zato.api.invoke" && summary.path_info.starts_with("/zato");
    let is_ignored = rest_log_ignore.iter().any(|prefix| summary.path_info.starts_with(prefix.as_str()));
    if is_internal_invoke || is_ignored {
        return Ok(());
    }

    // The remainder of a modulo by one second always fits, the fallback only satisfies the type
    let delta_usec = i32::try_from(fractional_micros(elapsed)).unwrap_or(i32::MAX);

    log_rest_summary(&RestLogEntry {
        pid: std::process::id(),
        cid: summary.cid,
        status_code: summary.status_code,
        delta_sec: elapsed.num_seconds(),
        delta_usec,
        response_size: summary.response_size,
    });
    Ok(())
}

/// Main request handler called from Python for every HTTP request.
///
/// Timestamps the request, dispatches to the worker's request dispatcher,
/// logs access and REST summaries, collects Prometheus metrics if enabled,
/// and returns `(status_str, headers_dict, body_bytes)`.
#[pyfunction]
#[pyo3(signature = (server, request_ctx, new_cid_func, local_tz_offset_secs, **kwargs))]
pub fn handle_http_request<'py>(
    server: &Bound<'py, PyAny>,
    request_ctx: &Bound<'py, PyDict>,
    new_cid_func: &Bound<'py, PyAny>,
    local_tz_offset_secs: i32,
    kwargs: Option<&Bound<'py, PyDict>>,
) -> PyResult<Py<PyTuple>> {
    // The interpreter handle rides along with any argument already bound to it,
    // so taking it from `server` keeps the parameter list within the lint's limit.
    let py = server.py();

    let cached = get_cached_attrs(server)?;

    let user_agent = get_ctx_string(request_ctx, "HTTP_USER_AGENT", NO_USER_AGENT)?;

    let cid: String = kwargs
        .and_then(|kwargs_dict| kwargs_dict.get_item("cid").ok().flatten())
        .map_or_else(|| new_cid_func.call0()?.extract(), |val| val.extract())?;

    adjust_requests_in_flight(py, "inc")?;

    let request_ts_utc = Utc::now();
    let local_offset =
        FixedOffset::east_opt(local_tz_offset_secs).ok_or_else(|| pyo3::exceptions::PyValueError::new_err("invalid timezone offset"))?;
    let request_ts_local = request_ts_utc.with_timezone(&local_offset);

    let py_ts_utc = set_request_timestamps(request_ctx, &request_ts_utc, &request_ts_local)?;

    let response_headers = PyDict::new(py);
    request_ctx.set_item("zato.http.response.headers", &response_headers)?;

    if cached.needs_x_zato_cid {
        let pub_cid = make_cid_public(&cid);
        response_headers.set_item("X-Zato-CID", &pub_cid)?;
    }

    let remote_addr = resolve_remote_addr(request_ctx, cached)?;
    request_ctx.set_item("zato.http.remote_addr", &remote_addr)?;

    let config_manager = server.getattr("config_manager")?;
    let dispatcher = config_manager.getattr("request_dispatcher")?;

    let payload_result = dispatcher.call_method1(
        "dispatch",
        (&cid, &py_ts_utc, request_ctx, &config_manager, &user_agent, &remote_addr),
    );

    // Check whether the dispatch returned a streaming iterator or a regular payload ..
    let is_streaming = match &payload_result {
        Ok(payload) => payload.hasattr(intern!(py, "__next__"))?,
        Err(_) => false,
    };

    let dispatch_had_error = payload_result.is_err();

    // .. for streaming responses, pass the iterator object through as-is ..
    let payload_obj: Py<PyAny> = if is_streaming {
        payload_result?.unbind()
    } else {
        // .. for regular responses, convert to PyBytes, or to an error body if the dispatch raised.
        let payload_bytes = match &payload_result {
            Ok(payload) => payload_to_bytes(payload)?,
            Err(err) => build_error_body(server, request_ctx, &cid, err)?,
        };
        payload_bytes.into_any()
    };

    let channel_item = request_ctx.get_item("zato.channel_item")?;
    let channel_name = get_channel_field(channel_item.as_ref(), "name")?;
    let service_name = get_channel_field(channel_item.as_ref(), "service_name")?;

    let status = get_ctx_string(request_ctx, "zato.http.response.status", DEFAULT_STATUS)?;
    let final_headers = collect_response_headers(request_ctx)?;
    let status_code: &str = status.split_whitespace().next().map_or(DEFAULT_STATUS_CODE, |code| code);

    // Streaming responses have unknown size at this point ..
    let response_size: usize = if is_streaming {
        0
    } else {
        payload_obj.bind(py).cast::<PyBytes>().map_or(0, |bytes| bytes.as_bytes().len())
    };

    let path_info = get_ctx_string(request_ctx, "PATH_INFO", NO_CTX_VALUE)?;

    let summary = RequestSummary {
        cid: &cid,
        remote_addr: &remote_addr,
        channel_name: &channel_name,
        service_name: &service_name,
        path_info: &path_info,
        status_code,
        response_size,
        user_agent: &user_agent,
        request_ts_utc,
        request_ts_local,
        dispatch_had_error,
    };

    if cached.needs_access_log {
        write_access_log(request_ctx, cached, &summary)?;
    }

    let elapsed = Utc::now() - request_ts_utc;
    record_prometheus_metrics(server, &summary, elapsed)?;
    write_rest_summary(server, &summary, elapsed)?;

    adjust_requests_in_flight(py, "dec")?;

    Ok(PyTuple::new(
        py,
        &[
            PyString::new(py, &status).into_any(),
            final_headers.into_any(),
            payload_obj.into_bound(py).into_any(),
        ],
    )?
    .unbind())
}
