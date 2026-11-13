//! Methods of the router exposed to Python, together with the routing primitives it is built from.

use parking_lot::Mutex;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString};

use super::super::base64::decode_lenient;
use super::super::cors::is_allowed_origin;
use super::super::matcher::{ChannelSpec, get_match_target};
use super::super::path::{normalize_path_info, to_internal_accept};
use super::super::py_json::{dump_json, parse_json};
use super::super::security::{extract_basic_auth, extract_bearer_token};
use super::super::table::ChannelTable;
use super::{
    ChannelRouter, Lookup, METHOD_OPTIONS, PORTAL_CALLER_KEY, ROUTE_DISPATCHER, ROUTE_INVOKE, ROUTE_RESPONSE, RoutedRequest, RouterConfig,
    RouterState, build_entry, read_request, respond_preflight, respond_unsupported_method,
};

#[pymethods]
impl ChannelRouter {
    /// Outcome of a request that the Python dispatcher handles.
    #[classattr]
    const DISPATCHER: u8 = ROUTE_DISPATCHER;

    /// Outcome of a request answered by the router.
    #[classattr]
    const RESPONSE: u8 = ROUTE_RESPONSE;

    /// Outcome of a request whose service is to be invoked.
    #[classattr]
    const INVOKE: u8 = ROUTE_INVOKE;

    /// Creates a router with no channels, which hands every request to the dispatcher until channels are loaded.
    #[new]
    fn new(config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let state = RouterState {
            table: ChannelTable::new(Vec::new()),
            unsupported: Vec::new(),
            is_ready: false,
        };
        Ok(Self {
            config: RouterConfig::from_dict(config)?,
            state: Mutex::new(state),
        })
    }

    /// Loads the channels of the URL data, in its matching order, replacing the channels loaded before.
    fn load(&self, py: Python<'_>, channel_data: &Bound<'_, PyAny>) -> PyResult<()> {
        let mut entries = Vec::new();
        let mut unsupported = Vec::new();

        for item in channel_data.try_iter()? {
            let item = item?;
            match build_entry(&item, &self.config.methods_allowed)? {
                Ok(entry) => entries.push(entry),
                Err(reason) => unsupported.push((item.get_item("name")?.str()?.to_string(), reason)),
            }
        }

        // Matching traced by the URL data is a log record per match, which the router does not emit
        let is_traced = self.config.url_data.bind(py).getattr("has_trace1")?.is_truthy()?;

        let state = RouterState {
            table: ChannelTable::new(entries),
            unsupported,
            is_ready: !is_traced,
        };
        *self.state.lock() = state;

        Ok(())
    }

    /// Whether the router handles requests, which it does only if it reproduces the matching of every channel.
    fn is_complete(&self) -> bool {
        self.state.lock().is_complete()
    }

    /// Returns the channels whose matching the router does not reproduce, as name and reason pairs.
    fn unsupported_channels(&self) -> Vec<(String, String)> {
        self.state.lock().unsupported.clone()
    }

    /// Routes one request, returning the outcome code and the response body or the invocation data.
    fn route<'py>(
        &self,
        cid: &Bound<'py, PyString>,
        request_ctx: &Bound<'py, PyDict>,
        user_agent: &Bound<'py, PyAny>,
        remote_addr: &Bound<'py, PyAny>,
    ) -> PyResult<(u8, Bound<'py, PyAny>)> {
        let py = cid.py();
        let declined = (ROUTE_DISPATCHER, py.None().into_bound(py));

        // Requests relayed by the API portal have their access checked by the portal
        if request_ctx.contains(PORTAL_CALLER_KEY)? {
            return Ok(declined);
        }

        let Some(request) = read_request(request_ctx)? else {
            return Ok(declined);
        };

        if !self.is_complete() {
            return Ok(declined);
        }

        // A preflight request is answered before anything else, since preflights never have credentials
        if let Some(origin) = request.origin.as_deref()
            && request.method == METHOD_OPTIONS
        {
            return respond_preflight(request_ctx, &request, origin);
        }

        if !self.config.methods_allowed.contains(&request.method) {
            return respond_unsupported_method(cid, request_ctx, &request);
        }

        let routed = RoutedRequest {
            cid,
            request_ctx,
            request: &request,
            peer: (user_agent, remote_addr),
        };

        match self.lookup(py, &request) {
            Lookup::Declined => Ok(declined),
            Lookup::NotMatched(allow_methods) => self.respond_not_matched(&routed, &allow_methods),
            Lookup::Matched(item, match_target, parameters) => {
                self.route_matched(&routed, item.bind(py), match_target.bind(py), parameters)
            }
        }
    }

    /// Returns the canonical form of a request path, as `normalize_path_info` of Python returns it.
    #[staticmethod]
    #[pyo3(name = "normalize_path_info")]
    fn py_normalize_path_info(path_info: &str) -> String {
        normalize_path_info(path_info)
    }

    /// Returns the internal form of an Accept header, as `to_internal_accept` of Python returns it.
    #[staticmethod]
    #[pyo3(name = "to_internal_accept")]
    #[pyo3(signature = (http_accept=None))]
    fn py_to_internal_accept(http_accept: Option<&str>) -> String {
        to_internal_accept(http_accept)
    }

    /// Returns the match target of a channel, as `get_match_target` of Python returns it.
    #[staticmethod]
    #[pyo3(name = "get_match_target")]
    #[pyo3(signature = (method, http_accept, url_path, methods_allowed))]
    #[expect(clippy::needless_pass_by_value, reason = "PyO3 extracts the Python list into an owned vector")]
    fn py_get_match_target(method: &str, http_accept: Option<&str>, url_path: &str, methods_allowed: Vec<String>) -> String {
        let spec = ChannelSpec {
            method,
            http_accept,
            url_path,
            match_slash: true,
        };
        get_match_target(&spec, &methods_allowed)
    }

    /// Parses a request body, with the result of `json.loads` of Python.
    #[staticmethod]
    #[pyo3(name = "parse_json")]
    fn py_parse_json<'py>(py: Python<'py>, payload: &[u8]) -> PyResult<Bound<'py, PyAny>> {
        parse_json(py, payload)
    }

    /// Serializes an object, with the result of `json.dumps(value, indent=4, default=default)` of Python.
    #[staticmethod]
    #[pyo3(name = "dump_json")]
    fn py_dump_json(value: &Bound<'_, PyAny>, default: &Bound<'_, PyAny>) -> PyResult<String> {
        dump_json(value, default)
    }

    /// Returns the credentials of a Basic Auth header, or None if `extract_basic_auth` of Python reports an error.
    #[staticmethod]
    #[pyo3(name = "extract_basic_auth")]
    fn py_extract_basic_auth(header: &str) -> Option<(String, String)> {
        extract_basic_auth(header)
    }

    /// Returns the token of a bearer Authorization header, as `extract_bearer_token` of Python returns it.
    #[staticmethod]
    #[pyo3(name = "extract_bearer_token")]
    fn py_extract_bearer_token(header: &str) -> String {
        extract_bearer_token(header).to_owned()
    }

    /// Decodes a base64 text, or returns None if `base64.b64decode` of Python raises an error.
    #[staticmethod]
    #[pyo3(name = "decode_base64")]
    fn py_decode_base64<'py>(py: Python<'py>, text: &str) -> Option<Bound<'py, PyBytes>> {
        decode_lenient(text).ok().map(|decoded| PyBytes::new(py, &decoded))
    }

    /// Whether an Origin header value is one that cross-origin requests are accepted from.
    #[staticmethod]
    #[pyo3(name = "is_allowed_origin")]
    fn py_is_allowed_origin(origin: &str) -> bool {
        is_allowed_origin(origin)
    }
}
