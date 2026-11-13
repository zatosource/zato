//! Router of REST channel requests, from the request context of the HTTP server to the service invocation.
//!
//! The router takes the steps of `RequestDispatcher.dispatch` up to the invocation of a service - URL
//! matching, CORS, the channel rate limit, security and the security definition rate limit - and writes
//! to the request context what the dispatcher writes. A request it does not handle is reported as such,
//! with the request context unchanged, and the Python dispatcher handles it in full.

/// Handling of a request that matched a channel.
mod matched;

/// Methods of the router exposed to Python.
mod python;

use parking_lot::Mutex;
use pyo3::exceptions::PyKeyError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString, PyTuple};

use super::cors::{EXPOSE_HEADERS, HEADER_ALLOW_ORIGIN, HEADER_EXPOSE_HEADERS, PREFLIGHT_HEADERS, is_allowed_origin};
use super::json_text::push_json_string;
use super::matcher::{ChannelPattern, ChannelSpec};
use super::path::{normalize_path_info, to_internal_accept};
use super::table::{ChannelTable, TableEntry};

/// Outcome of a request that the Python dispatcher handles.
pub const ROUTE_DISPATCHER: u8 = 0;

/// Outcome of a request answered by the router, with the response body.
pub const ROUTE_RESPONSE: u8 = 1;

/// Outcome of a request whose service is to be invoked, with the channel item and the path parameters.
pub const ROUTE_INVOKE: u8 = 2;

/// Level of informational log records.
const LOG_LEVEL_INFO: i32 = 20;

/// Level of warning log records.
const LOG_LEVEL_WARNING: i32 = 30;

/// Status line of a preflight response.
const STATUS_NO_CONTENT: &str = "204 No Content";

/// Status line of a request that matched no channel.
const STATUS_NOT_FOUND: &str = "404 Not Found";

/// Status line of a request with a method that no channel at its path accepts.
const STATUS_METHOD_NOT_ALLOWED: &str = "405 Method Not Allowed";

/// HTTP method of preflight requests.
const METHOD_OPTIONS: &str = "OPTIONS";

/// Response header that lists the methods a path accepts.
const HEADER_ALLOW: &str = "Allow";

/// Response header with the request limit of a security definition.
const HEADER_RATE_LIMIT_LIMIT: &str = "X-RateLimit-Limit";

/// Response header with the requests a security definition has left.
const HEADER_RATE_LIMIT_REMAINING: &str = "X-RateLimit-Remaining";

/// Request context key under which a rate limit result is handed to a service that answers it itself.
const RATE_LIMIT_RESULT_KEY: &str = "zato.http.rate_limit.result";

/// Request context key of the caller identified by the API portal.
const PORTAL_CALLER_KEY: &str = "zato.api_portal.caller";

/// Request context key of the response headers.
const RESPONSE_HEADERS_KEY: &str = "zato.http.response.headers";

/// Request context key of the response status line.
const RESPONSE_STATUS_KEY: &str = "zato.http.response.status";

/// Request context key of the matched channel item.
const CHANNEL_ITEM_KEY: &str = "zato.channel_item";

/// Request context key of the request body.
const RAW_REQUEST_KEY: &str = "zato.http.raw_request";

/// Channel name logged for a request that matched no channel.
const NO_CHANNEL_NAME: &str = "(None)";

/// Service name logged for a request that matched no channel.
const NO_CHANNEL_SERVICE: &str = "<no-channel>";

/// Name of the channel whose requests to internal paths are not logged.
const API_INVOKE_CHANNEL: &str = "zato.api.invoke";

/// Path prefix of internal channels.
const INTERNAL_PATH_PREFIX: &str = "/zato";

/// Log message of a request that matched no channel.
const RESPONSE_404_LOG: &str = "URL not found `%s` (Method:%s; Accept:%s; CID:%s)";

/// Log message of a request with a method that no channel at its path accepts.
const RESPONSE_405_LOG: &str = "Method not allowed `%s` (Method:%s; Allow:%s; CID:%s)";

/// Error details of a request with a method the server does not allow.
const UNSUPPORTED_METHOD_DETAILS: &str = "Unsupported HTTP method";

/// Source location attributed to the log records of one kind, which is the line of the dispatcher that emits them.
struct LogSite {
    /// Path of the source file.
    pathname: Py<PyAny>,

    /// Line number.
    lineno: Py<PyAny>,

    /// Function name.
    func_name: Py<PyAny>,
}

impl LogSite {
    /// Reads a site given as a `(pathname, lineno, func_name)` tuple.
    fn from_tuple(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        let (pathname, lineno, func_name) = value.extract::<(Py<PyAny>, Py<PyAny>, Py<PyAny>)>()?;
        Ok(Self {
            pathname,
            lineno,
            func_name,
        })
    }
}

/// Objects of the server that the router works with.
struct RouterConfig {
    /// Methods the server accepts requests with.
    methods_allowed: Vec<String>,

    /// The `zato_rest` logger.
    logger: Py<PyAny>,

    /// Site of the log record of an incoming request.
    incoming_site: LogSite,

    /// Site of the log record of a request that matched no channel.
    not_found_site: LogSite,

    /// Site of the log record of a request with a method no channel at its path accepts.
    method_not_allowed_site: LogSite,

    /// Paths whose incoming requests are not logged.
    rest_log_ignore: Py<PyAny>,

    /// `escape_nonprintable` of `zato.common.util.logging_`.
    escape_nonprintable: Py<PyAny>,

    /// Rate limiting manager of the server.
    rate_limiting_manager: Py<PyAny>,

    /// The request dispatcher, whose rate limit responses and error responses the router uses.
    dispatcher: Py<PyAny>,

    /// The URL data, whose security definitions the router reads.
    url_data: Py<PyAny>,

    /// Context variable with the correlation ID of the request being handled.
    current_cid: Py<PyAny>,

    /// Context variable with the name of the service handling the request.
    current_service_name: Py<PyAny>,

    /// Function returning the current time in microseconds.
    current_time_us: Py<PyAny>,

    /// Function returning the response headers of a deprecated channel.
    get_deprecation_headers: Py<PyAny>,
}

/// Returns a required entry of the configuration dict.
fn required<'py>(config: &Bound<'py, PyDict>, key: &str) -> PyResult<Bound<'py, PyAny>> {
    config.get_item(key)?.ok_or_else(|| PyKeyError::new_err(key.to_owned()))
}

impl RouterConfig {
    /// Reads the configuration dict.
    fn from_dict(config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let log_sites = required(config, "log_sites")?;

        Ok(Self {
            methods_allowed: required(config, "http_methods_allowed")?.extract()?,
            logger: required(config, "logger")?.unbind(),
            incoming_site: LogSite::from_tuple(&log_sites.get_item("incoming")?)?,
            not_found_site: LogSite::from_tuple(&log_sites.get_item("not_found")?)?,
            method_not_allowed_site: LogSite::from_tuple(&log_sites.get_item("method_not_allowed")?)?,
            rest_log_ignore: required(config, "rest_log_ignore")?.unbind(),
            escape_nonprintable: required(config, "escape_nonprintable")?.unbind(),
            rate_limiting_manager: required(config, "rate_limiting_manager")?.unbind(),
            dispatcher: required(config, "dispatcher")?.unbind(),
            url_data: required(config, "url_data")?.unbind(),
            current_cid: required(config, "current_cid")?.unbind(),
            current_service_name: required(config, "current_service_name")?.unbind(),
            current_time_us: required(config, "current_time_us")?.unbind(),
            get_deprecation_headers: required(config, "get_deprecation_headers")?.unbind(),
        })
    }
}

/// What the router keeps for one channel.
struct ChannelRecord {
    /// The channel item.
    item: Py<PyAny>,

    /// Match target of the channel, the key of its security in the URL data.
    match_target: Py<PyAny>,
}

/// Channel table together with what decides whether the router handles requests at all.
struct RouterState {
    /// Channels in matching order.
    table: ChannelTable<ChannelRecord>,

    /// Channels whose matching the router does not reproduce, by name, with the reason.
    unsupported: Vec<(String, String)>,

    /// Whether channels were loaded and the URL data does not trace its matching.
    is_ready: bool,
}

impl RouterState {
    /// Whether the router handles requests, which it does only if it reproduces the matching of every channel.
    const fn is_complete(&self) -> bool {
        self.is_ready && self.unsupported.is_empty()
    }
}

/// The parts of a request that routing reads.
struct RequestLine {
    /// HTTP method.
    method: String,

    /// Internal form of the Accept header.
    accept: String,

    /// Normalized path.
    path: String,

    /// Origin of a cross-origin request from an allowed origin.
    origin: Option<String>,
}

/// Result of looking a request up in the channel table.
enum Lookup {
    /// The router does not handle requests now.
    Declined,

    /// No channel matched, with the methods channels at the path accept.
    NotMatched(Vec<String>),

    /// A channel matched, with its item, its match target and the path parameters.
    Matched(Py<PyAny>, Py<PyAny>, Vec<(String, String)>),
}

/// Returns a value as a string, if it is one.
fn as_text(value: &Bound<'_, PyAny>) -> Option<String> {
    value.cast::<PyString>().ok()?.to_str().ok().map(str::to_owned)
}

/// Returns an entry of the request context read with `.get`, None if it is missing, Err(()) if it is not a string.
fn optional_text(request_ctx: &Bound<'_, PyDict>, key: &str) -> PyResult<Result<Option<String>, ()>> {
    let Some(value) = request_ctx.get_item(key)? else {
        return Ok(Ok(None));
    };

    if value.is_none() {
        return Ok(Ok(None));
    }

    Ok(as_text(&value).map(Some).ok_or(()))
}

/// Reads the parts of a request that routing needs, None if they are not the strings they normally are.
fn read_request(request_ctx: &Bound<'_, PyDict>) -> PyResult<Option<RequestLine>> {
    let Some(method) = request_ctx.get_item("REQUEST_METHOD")?.as_ref().and_then(as_text) else {
        return Ok(None);
    };
    let Some(raw_path) = request_ctx.get_item("PATH_INFO")?.as_ref().and_then(as_text) else {
        return Ok(None);
    };
    let Ok(http_accept) = optional_text(request_ctx, "HTTP_ACCEPT")? else {
        return Ok(None);
    };
    let Ok(origin) = optional_text(request_ctx, "HTTP_ORIGIN")? else {
        return Ok(None);
    };

    Ok(Some(RequestLine {
        method,
        accept: to_internal_accept(http_accept.as_deref()),
        path: normalize_path_info(&raw_path),
        origin: origin.filter(|value| is_allowed_origin(value)),
    }))
}

/// Whether path parameters of a channel match across slashes, as `resolve_match_slash` of Python decides.
fn resolve_match_slash(value: &Bound<'_, PyAny>) -> PyResult<bool> {
    if value.is_none() || as_text(value).is_some_and(|text| text.is_empty()) {
        return Ok(true);
    }
    value.is_truthy()
}

/// Returns a channel field read with `.get` as a string, None if it is missing or None.
fn optional_field(item: &Bound<'_, PyAny>, key: &str) -> PyResult<Option<String>> {
    let value = item.call_method1("get", (key,))?;
    if value.is_none() {
        return Ok(None);
    }
    Ok(Some(value.extract()?))
}

/// Builds the table entry of one channel, verifying that it matches what the Python matcher of the channel matches.
fn build_entry(item: &Bound<'_, PyAny>, methods_allowed: &[String]) -> PyResult<Result<TableEntry<ChannelRecord>, String>> {
    let method = optional_field(item, "method")?.unwrap_or_default();
    let http_accept = optional_field(item, "http_accept")?;
    let url_path: String = item.get_item("url_path")?.extract()?;
    let match_target_object = item.get_item("match_target")?;
    let match_target: String = match_target_object.extract()?;
    let match_slash = resolve_match_slash(&item.call_method1("get", ("match_slash",))?)?;

    let spec = ChannelSpec {
        method: &method,
        http_accept: http_accept.as_deref(),
        url_path: &url_path,
        match_slash,
    };

    let pattern = match ChannelPattern::compile(&spec, methods_allowed, &match_target) {
        Ok(pattern) => pattern,
        Err(error) => return Ok(Err(error.to_string())),
    };

    // The Python matcher in use has to be the one the definition produces
    let compiled = item.get_item("match_target_compiled")?;
    let group_names: Vec<String> = compiled.getattr("group_names")?.extract()?;
    let is_internal: bool = compiled.getattr("is_internal")?.extract()?;

    if group_names != pattern.parameter_names() || is_internal != pattern.is_internal() {
        return Ok(Err("compiled matcher differs from the channel definition".to_owned()));
    }

    Ok(Ok(TableEntry {
        pattern,
        method,
        accept_internal: to_internal_accept(http_accept.as_deref()),
        payload: ChannelRecord {
            item: item.clone().unbind(),
            match_target: match_target_object.unbind(),
        },
    }))
}

/// A request being routed, with what its handling needs.
struct RoutedRequest<'py, 'request> {
    /// Correlation ID of the request.
    cid: &'request Bound<'py, PyString>,

    /// The request context.
    request_ctx: &'request Bound<'py, PyDict>,

    /// The parts of the request that routing read.
    request: &'request RequestLine,

    /// User agent and remote address of the caller.
    peer: (&'request Bound<'py, PyAny>, &'request Bound<'py, PyAny>),
}

/// Context variables of the logging context of one request, restored when the request is done.
struct LogScope<'py> {
    /// Token restoring the correlation ID.
    cid_token: Bound<'py, PyAny>,

    /// Token restoring the service name.
    service_name_token: Bound<'py, PyAny>,
}

/// Router of REST channel requests.
#[pyclass(module = "zato_server_core", frozen)]
pub struct ChannelRouter {
    /// Objects of the server.
    config: RouterConfig,

    /// Channels and their caches.
    state: Mutex<RouterState>,
}

impl ChannelRouter {
    /// Binds the logging context of a request, as `dispatch` binds it.
    fn enter_scope<'py>(&self, cid: &Bound<'py, PyString>, service_name: &Bound<'py, PyAny>) -> PyResult<LogScope<'py>> {
        let py = cid.py();
        let cid_token = self.config.current_cid.bind(py).call_method1("set", (cid,))?;
        let service_name_token = self.config.current_service_name.bind(py).call_method1("set", (service_name,))?;
        Ok(LogScope {
            cid_token,
            service_name_token,
        })
    }

    /// Restores the logging context that was in place before the request.
    fn exit_scope(&self, scope: &LogScope<'_>) -> PyResult<()> {
        let py = scope.cid_token.py();
        self.config.current_cid.bind(py).call_method1("reset", (&scope.cid_token,))?;
        self.config
            .current_service_name
            .bind(py)
            .call_method1("reset", (&scope.service_name_token,))?;
        Ok(())
    }

    /// Emits a log record attributed to the given site of the dispatcher.
    fn emit(&self, level: i32, site: &LogSite, message: &str, args: &Bound<'_, PyTuple>) -> PyResult<()> {
        let py = args.py();
        let logger = self.config.logger.bind(py);

        if !logger.call_method1("isEnabledFor", (level,))?.is_truthy()? {
            return Ok(());
        }

        let name = logger.getattr("name")?;
        let record_args = (
            name,
            level,
            site.pathname.bind(py),
            site.lineno.bind(py),
            message,
            args,
            py.None(),
            site.func_name.bind(py),
        );
        let record = logger.call_method1("makeRecord", record_args)?;
        logger.call_method1("handle", (record,))?;

        Ok(())
    }

    /// Returns a value with its non-printable characters escaped, as `escape_nonprintable` returns it.
    fn escape(&self, value: &Bound<'_, PyAny>) -> PyResult<String> {
        // Printable ASCII is returned as it is, anything else goes through the Python function
        if let Some(text) = as_text(value).filter(|text| text.bytes().all(|byte| (b' '..=b'~').contains(&byte))) {
            return Ok(text);
        }
        self.config.escape_nonprintable.bind(value.py()).call1((value,))?.extract()
    }

    /// Logs the summary of an incoming request, as `_log_incoming_request` logs it.
    fn log_incoming(&self, routed: &RoutedRequest<'_, '_>, item: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        let RoutedRequest {
            cid,
            request_ctx,
            request,
            peer,
        } = routed;
        let py = cid.py();

        if !self
            .config
            .logger
            .bind(py)
            .call_method1("isEnabledFor", (LOG_LEVEL_INFO,))?
            .is_truthy()?
        {
            return Ok(());
        }
        if self.config.rest_log_ignore.bind(py).contains(&request.path)? {
            return Ok(());
        }

        let (channel_name, service_name) = match item {
            Some(channel_item) => (
                channel_item.get_item("name")?.str()?.to_string(),
                channel_item.get_item("service_name")?.str()?.to_string(),
            ),
            None => (NO_CHANNEL_NAME.to_owned(), NO_CHANNEL_SERVICE.to_owned()),
        };

        if channel_name == API_INVOKE_CHANNEL && request.path.starts_with(INTERNAL_PATH_PREFIX) {
            return Ok(());
        }

        let payload_length = required(request_ctx, RAW_REQUEST_KEY)?.len()?;
        let raw_uri = self.escape(&required(request_ctx, "RAW_URI")?)?;
        let user_agent = self.escape(peer.0)?;
        let remote_addr = self.escape(peer.1)?;
        let remote_port = required(request_ctx, "REMOTE_PORT")?.str()?;
        let method = &request.method;

        let message = format!(
            "REST cha \u{2192} cid={cid}; {method} {raw_uri} name={channel_name}; service={service_name}; len={payload_length}; agent={user_agent}; remote-addr={remote_addr}:{remote_port}"
        );

        self.emit(LOG_LEVEL_INFO, &self.config.incoming_site, &message, &PyTuple::empty(py))
    }

    /// Answers a request that matched no channel with a 405 or a 404 response and its log records.
    fn respond_not_matched<'py>(&self, routed: &RoutedRequest<'py, '_>, allow_methods: &[String]) -> PyResult<(u8, Bound<'py, PyAny>)> {
        let py = routed.cid.py();

        begin_response(routed.request_ctx, routed.request)?;
        routed.request_ctx.set_item(CHANNEL_ITEM_KEY, py.None())?;

        let scope = self.enter_scope(routed.cid, &PyString::new(py, ""))?;
        let result = self.respond_not_matched_in_scope(routed, allow_methods);
        let restored = self.exit_scope(&scope);

        result.and_then(|out| restored.map(|()| out))
    }

    /// Logs and builds the response to a request that matched no channel, with the logging context bound.
    fn respond_not_matched_in_scope<'py>(
        &self,
        routed: &RoutedRequest<'py, '_>,
        allow_methods: &[String],
    ) -> PyResult<(u8, Bound<'py, PyAny>)> {
        let RoutedRequest {
            cid, request_ctx, request, ..
        } = routed;
        let py = cid.py();
        self.log_incoming(routed, None)?;

        // A path that channels are at, reached with a method none of them accepts
        if !allow_methods.is_empty() {
            let allow_header = allow_methods.join(", ");
            request_ctx.set_item(RESPONSE_STATUS_KEY, STATUS_METHOD_NOT_ALLOWED)?;
            required(request_ctx, RESPONSE_HEADERS_KEY)?.set_item(HEADER_ALLOW, &allow_header)?;

            let body = format!("Method not allowed (CID:{cid})");
            let args = PyTuple::new(
                py,
                [request.path.as_str(), request.method.as_str(), allow_header.as_str(), cid.to_str()?],
            )?;
            self.emit(LOG_LEVEL_WARNING, &self.config.method_not_allowed_site, RESPONSE_405_LOG, &args)?;

            return Ok((ROUTE_RESPONSE, PyString::new(py, &body).into_any()));
        }

        request_ctx.set_item(RESPONSE_STATUS_KEY, STATUS_NOT_FOUND)?;

        let body = format!("URL not found (CID:{cid})");
        let args = PyTuple::new(
            py,
            [
                request.path.as_str(),
                request.method.as_str(),
                request.accept.as_str(),
                cid.to_str()?,
            ],
        )?;
        self.emit(LOG_LEVEL_WARNING, &self.config.not_found_site, RESPONSE_404_LOG, &args)?;

        Ok((ROUTE_RESPONSE, PyString::new(py, &body).into_any()))
    }

    /// Looks a request up in the channel table.
    fn lookup(&self, py: Python<'_>, request: &RequestLine) -> Lookup {
        let mut state = self.state.lock();

        if !state.is_complete() {
            return Lookup::Declined;
        }

        let Some(matched) = state.table.find(&request.path, &request.method, &request.accept) else {
            return Lookup::NotMatched(
                state
                    .table
                    .allow_methods(&request.path, &request.method, &request.accept)
                    .into_iter()
                    .collect(),
            );
        };

        match state.table.entry(matched.index) {
            Some(entry) => Lookup::Matched(
                entry.payload.item.clone_ref(py),
                entry.payload.match_target.clone_ref(py),
                matched.parameters,
            ),
            None => Lookup::Declined,
        }
    }
}

/// Writes the normalized path, and the CORS headers of a cross-origin request, as every dispatched request has them.
fn begin_response(request_ctx: &Bound<'_, PyDict>, request: &RequestLine) -> PyResult<()> {
    request_ctx.set_item("PATH_INFO", &request.path)?;

    if let Some(origin) = &request.origin {
        let headers = required(request_ctx, RESPONSE_HEADERS_KEY)?;
        headers.set_item(HEADER_ALLOW_ORIGIN, origin)?;
        headers.set_item(HEADER_EXPOSE_HEADERS, EXPOSE_HEADERS)?;
    }

    Ok(())
}

/// Answers a preflight request, as `handle_preflight_request` answers it.
fn respond_preflight<'py>(request_ctx: &Bound<'py, PyDict>, request: &RequestLine, origin: &str) -> PyResult<(u8, Bound<'py, PyAny>)> {
    request_ctx.set_item("PATH_INFO", &request.path)?;

    let headers = required(request_ctx, RESPONSE_HEADERS_KEY)?;
    headers.set_item(HEADER_ALLOW_ORIGIN, origin)?;
    for (name, value) in PREFLIGHT_HEADERS {
        headers.set_item(name, value)?;
    }

    request_ctx.set_item(RESPONSE_STATUS_KEY, STATUS_NO_CONTENT)?;
    Ok((ROUTE_RESPONSE, PyString::new(request_ctx.py(), "").into_any()))
}

/// Answers a request with a method the server does not allow, as `client_json_error` builds the body.
fn respond_unsupported_method<'py>(
    cid: &Bound<'py, PyString>,
    request_ctx: &Bound<'py, PyDict>,
    request: &RequestLine,
) -> PyResult<(u8, Bound<'py, PyAny>)> {
    begin_response(request_ctx, request)?;
    request_ctx.set_item(RESPONSE_STATUS_KEY, STATUS_METHOD_NOT_ALLOWED)?;

    let mut body = String::from("{\n    \"result\": \"Error\",\n    \"cid\": ");
    push_json_string(&mut body, cid.to_str()?);
    body.push_str(",\n    \"details\": ");
    push_json_string(&mut body, UNSUPPORTED_METHOD_DETAILS);
    body.push_str("\n}");

    Ok((ROUTE_RESPONSE, PyString::new(request_ctx.py(), &body).into_any()))
}
