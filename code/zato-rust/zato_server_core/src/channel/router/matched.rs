//! Handling of a request that matched a channel, up to the decision to invoke its service.

use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};

use super::super::checks::{SecurityOutcome, channel_needs_dispatcher, check_security, enrich_with_sec_data};
use super::{
    CHANNEL_ITEM_KEY, ChannelRouter, HEADER_RATE_LIMIT_LIMIT, HEADER_RATE_LIMIT_REMAINING, RATE_LIMIT_RESULT_KEY, RESPONSE_HEADERS_KEY,
    ROUTE_DISPATCHER, ROUTE_INVOKE, ROUTE_RESPONSE, RoutedRequest, begin_response, required,
};

impl ChannelRouter {
    /// Routes a request that matched a channel, declining it if the channel or its credentials need the dispatcher.
    pub(super) fn route_matched<'py>(
        &self,
        matched: &RoutedRequest<'py, '_>,
        item: &Bound<'py, PyAny>,
        match_target: &Bound<'py, PyAny>,
        parameters: Vec<(String, String)>,
    ) -> PyResult<(u8, Bound<'py, PyAny>)> {
        let py = matched.cid.py();

        if channel_needs_dispatcher(item) {
            return Ok((ROUTE_DISPATCHER, py.None().into_bound(py)));
        }

        let url_sec = self.config.url_data.bind(py).getattr("url_sec")?;
        let security = check_security(&url_sec, match_target, matched.request_ctx);

        // Credentials that do not match are reported by the dispatcher, with its log lines and its response
        if matches!(security, SecurityOutcome::Declined) {
            return Ok((ROUTE_DISPATCHER, py.None().into_bound(py)));
        }

        begin_response(matched.request_ctx, matched.request)?;
        matched.request_ctx.set_item(CHANNEL_ITEM_KEY, item)?;

        let service_name = item.get_item("service_name")?;
        let scope = self.enter_scope(matched.cid, &service_name)?;
        let result = self.handle_matched(matched, item, security, parameters);
        let restored = self.exit_scope(&scope);

        result.and_then(|out| restored.map(|()| out))
    }

    /// Logs the request, adds deprecation headers and applies the rate limits, with the logging context bound.
    fn handle_matched<'py>(
        &self,
        matched: &RoutedRequest<'py, '_>,
        item: &Bound<'py, PyAny>,
        security: SecurityOutcome<'py>,
        parameters: Vec<(String, String)>,
    ) -> PyResult<(u8, Bound<'py, PyAny>)> {
        let py = matched.cid.py();

        self.log_incoming(matched, Some(item))?;

        // Deprecated channels announce it on every response, including rate limited ones
        if item.call_method1("get", ("is_deprecated",))?.is_truthy()? {
            let deprecation_headers = self.config.get_deprecation_headers.bind(py).call1((item,))?;
            required(matched.request_ctx, RESPONSE_HEADERS_KEY)?.call_method1("update", (deprecation_headers,))?;
        }

        let now_us = self.config.current_time_us.bind(py).call0()?;

        match self.authorize(matched, item, security, &now_us) {
            Ok(Some(response)) => Ok((ROUTE_RESPONSE, response)),
            Ok(None) => {
                let url_params = PyDict::new(py);
                for (name, value) in parameters {
                    url_params.set_item(name, value)?;
                }
                let out = PyTuple::new(py, [item.clone(), url_params.into_any()])?;
                Ok((ROUTE_INVOKE, out.into_any()))
            }
            Err(error) => {
                // Only what the dispatcher catches as an exception becomes an error response
                if !error.is_instance_of::<PyException>(py) {
                    return Err(error);
                }
                let dispatcher = self.config.dispatcher.bind(py);
                let response =
                    dispatcher.call_method1("_handle_dispatch_error", (matched.cid, error.value(py), item, matched.request_ctx))?;
                Ok((ROUTE_RESPONSE, response))
            }
        }
    }

    /// Applies the channel rate limit, records the security context and applies the security definition rate limit.
    ///
    /// Returns the response of a rate limited request, or None if the service is to be invoked.
    fn authorize<'py>(
        &self,
        matched: &RoutedRequest<'py, '_>,
        item: &Bound<'py, PyAny>,
        security: SecurityOutcome<'py>,
        now_us: &Bound<'py, PyAny>,
    ) -> PyResult<Option<Bound<'py, PyAny>>> {
        let py = matched.cid.py();
        let dispatcher = self.config.dispatcher.bind(py);
        let remote_addr = matched.peer.1;

        // The channel limit is keyed by the address alone, so it applies before the credentials are taken into account
        let channel_id = item.get_item("id")?;
        let key_prefix = format!("rest{}:", channel_id.str()?);
        let manager = self.config.rate_limiting_manager.bind(py);
        let channel_result = manager.call_method1("check", (&channel_id, remote_addr, now_us, key_prefix))?;

        if channel_result.is_truthy()? && !channel_result.getattr("is_allowed")?.is_truthy()? {
            let out = dispatcher.call_method1(
                "_handle_rate_limit_result",
                (matched.cid, &channel_result, matched.request_ctx, remote_addr, item),
            )?;
            return Ok(Some(out));
        }

        if let SecurityOutcome::Passed(sec_def, sec_type) = security {
            enrich_with_sec_data(matched.request_ctx, &sec_def, &sec_type)?;
        }

        let sec_def_result = dispatcher.call_method1("check_sec_def_rate_limiting", (matched.request_ctx, remote_addr, now_us))?;

        if !sec_def_result.is_truthy()? {
            return Ok(None);
        }

        // An allowed request is told how much of its quota remains
        if sec_def_result.getattr("is_allowed")?.is_truthy()? {
            let headers = required(matched.request_ctx, RESPONSE_HEADERS_KEY)?;
            headers.set_item(HEADER_RATE_LIMIT_LIMIT, sec_def_result.getattr("limit")?.str()?)?;
            headers.set_item(HEADER_RATE_LIMIT_REMAINING, sec_def_result.getattr("remaining")?.str()?)?;
            return Ok(None);
        }

        let is_rejected_here = sec_def_result.getattr("is_disallowed")?.is_truthy()?
            || !dispatcher
                .call_method1("_service_handles_rate_limit_rejection", (item,))?
                .is_truthy()?;

        if is_rejected_here {
            let kwargs = PyDict::new(py);
            kwargs.set_item("needs_quota_headers", true)?;
            let args = (matched.cid, &sec_def_result, matched.request_ctx, remote_addr, item);
            let out = dispatcher.call_method("_handle_rate_limit_result", args, Some(&kwargs))?;
            return Ok(Some(out));
        }

        // A service that answers rejections itself receives the result and the request goes on to it
        matched.request_ctx.set_item(RATE_LIMIT_RESULT_KEY, sec_def_result)?;
        Ok(None)
    }
}
