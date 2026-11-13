//! Per-request checks of a matched channel and of its security definition.
//!
//! The checks read the channel item and the security definition as they are at the time of the request,
//! since both are edited in place when their configuration changes. A channel or a request that the
//! Rust router does not handle is reported as such and handed, unchanged, to the Python dispatcher.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString};

use super::security::{check_basic_auth, constant_time_eq, extract_bearer_token};

/// Transport of REST channels.
const TRANSPORT_PLAIN_HTTP: &str = "plain_http";

/// Data formats whose requests need the Python dispatcher.
const DISPATCHER_DATA_FORMATS: [&str; 3] = ["form", "hl7-v2", "hl7-ccda"];

/// Value of a security definition field that stands for no definition.
const ZATO_NONE: &str = "ZATO_NONE";

/// Security definition type of HTTP Basic Auth.
const SEC_TYPE_BASIC_AUTH: &str = "basic_auth";

/// Security definition type of API keys.
const SEC_TYPE_APIKEY: &str = "apikey";

/// Security definition type of bearer tokens.
const SEC_TYPE_OAUTH: &str = "oauth";

/// Request context key of the Authorization header.
const AUTHORIZATION_KEY: &str = "HTTP_AUTHORIZATION";

/// Fields of a security definition that the security context of a request never contains.
const SECRET_FIELDS: [&str; 2] = ["password", "static_token"];

/// Request context key of the security context.
const SEC_DEF_KEY: &str = "zato.sec_def";

/// Channel item fields, always present, any of which when true makes the Python dispatcher handle the request.
const DISPATCHER_REQUIRED_FLAGS: [&str; 3] = ["is_internal", "is_audit_log_active", "use_queue"];

/// Channel item fields, present only if configured, any of which when true makes the Python dispatcher handle the request.
const DISPATCHER_OPTIONAL_FLAGS: [&str; 2] = ["response_cache", "security_groups_ctx"];

/// Outcome of the security check of a request.
pub enum SecurityOutcome<'py> {
    /// The channel has no security definition.
    NoSecurity,

    /// The credentials match the definition, which is given with its type.
    Passed(Bound<'py, PyAny>, String),

    /// The request is handed to the Python dispatcher.
    Declined,
}

/// Returns the value of a field read with `.get`, or None if the field is missing, None, or cannot be read.
fn field<'py>(item: &Bound<'py, PyAny>, key: &str) -> Option<Bound<'py, PyAny>> {
    item.call_method1("get", (key,)).ok().filter(|value| !value.is_none())
}

/// Whether a field read with `.get` is set to a true value.
fn is_set(item: &Bound<'_, PyAny>, key: &str) -> bool {
    field(item, key).is_some_and(|value| value.is_truthy().unwrap_or(false))
}

/// Truth value of a field read as `item[key]`, None if reading it or its truth value raises an error.
fn required_truth(item: &Bound<'_, PyAny>, key: &str) -> Option<bool> {
    item.get_item(key).ok()?.is_truthy().ok()
}

/// Truth value of a field read with `.get`, None if reading it or its truth value raises an error.
fn optional_truth(item: &Bound<'_, PyAny>, key: &str) -> Option<bool> {
    item.call_method1("get", (key,)).ok()?.is_truthy().ok()
}

/// Returns a field read as `item[key]` if it is a string, None if it is not one or cannot be read.
fn required_text(item: &Bound<'_, PyAny>, key: &str) -> Option<String> {
    item.get_item(key).ok().as_ref().and_then(as_text)
}

/// Whether a matched channel is one whose requests the Python dispatcher handles.
pub fn channel_needs_dispatcher(item: &Bound<'_, PyAny>) -> bool {
    if required_truth(item, "is_active") != Some(true) {
        return true;
    }

    if required_text(item, "transport").as_deref() != Some(TRANSPORT_PLAIN_HTTP) {
        return true;
    }

    if DISPATCHER_REQUIRED_FLAGS
        .iter()
        .any(|flag| required_truth(item, flag) != Some(false))
    {
        return true;
    }

    if DISPATCHER_OPTIONAL_FLAGS
        .iter()
        .any(|flag| optional_truth(item, flag) != Some(false))
    {
        return true;
    }

    // A memoized response cache configuration means one was configured, whereas a memoized None means none was
    let memoized_cache = item.call_method1("get", ("response_cache_parsed",));
    if !memoized_cache.is_ok_and(|value| value.is_none()) {
        return true;
    }

    // A data format that is not a string is never one of those the dispatcher is needed for
    let Ok(data_format) = item.get_item("data_format") else {
        return true;
    };
    as_text(&data_format).is_some_and(|text| DISPATCHER_DATA_FORMATS.contains(&text.as_str()))
}

/// Returns a value as a string, if it is one that can be read as UTF-8.
fn as_text(value: &Bound<'_, PyAny>) -> Option<String> {
    value.cast::<PyString>().ok()?.to_str().ok().map(str::to_owned)
}

/// Checks the credentials of a request against the security definition of its channel.
pub fn check_security<'py>(
    url_sec: &Bound<'py, PyAny>,
    match_target: &Bound<'py, PyAny>,
    request_ctx: &Bound<'py, PyDict>,
) -> SecurityOutcome<'py> {
    check_security_definition(url_sec, match_target, request_ctx).unwrap_or(SecurityOutcome::Declined)
}

/// Checks the credentials of a request, with any error raised by Python meaning the request is declined.
fn check_security_definition<'py>(
    url_sec: &Bound<'py, PyAny>,
    match_target: &Bound<'py, PyAny>,
    request_ctx: &Bound<'py, PyDict>,
) -> PyResult<SecurityOutcome<'py>> {
    let sec_def = url_sec.get_item(match_target)?.getattr("sec_def")?;

    if as_text(&sec_def).is_some_and(|text| text == ZATO_NONE) {
        return Ok(SecurityOutcome::NoSecurity);
    }

    let sec_type: String = sec_def.get_item("sec_type")?.extract()?;

    // An inactive definition is reported by the dispatcher
    if !sec_def.get_item("is_active")?.is_truthy()? {
        return Ok(SecurityOutcome::Declined);
    }

    let is_passed = match sec_type.as_str() {
        SEC_TYPE_BASIC_AUTH => check_basic_auth_definition(&sec_def, request_ctx)?,
        SEC_TYPE_APIKEY => check_apikey_definition(&sec_def, request_ctx)?,
        SEC_TYPE_OAUTH => check_static_bearer_definition(&sec_def, request_ctx)?,
        _ => false,
    };

    if is_passed {
        return Ok(SecurityOutcome::Passed(sec_def, sec_type));
    }

    Ok(SecurityOutcome::Declined)
}

/// Returns the Authorization header of a request, if it has one that is a string.
fn authorization_header(request_ctx: &Bound<'_, PyDict>) -> PyResult<Option<String>> {
    let header = request_ctx.get_item(AUTHORIZATION_KEY)?;
    Ok(header.as_ref().and_then(as_text))
}

/// Checks HTTP Basic Auth credentials.
fn check_basic_auth_definition(sec_def: &Bound<'_, PyAny>, request_ctx: &Bound<'_, PyDict>) -> PyResult<bool> {
    let expected_username: String = sec_def.getattr("username")?.extract()?;
    let expected_password: String = sec_def.getattr("password")?.extract()?;
    let header = authorization_header(request_ctx)?;

    Ok(check_basic_auth(header.as_deref(), &expected_username, &expected_password))
}

/// Checks an API key sent in the header the definition names.
fn check_apikey_definition(sec_def: &Bound<'_, PyAny>, request_ctx: &Bound<'_, PyDict>) -> PyResult<bool> {
    let header_name = sec_def.get_item("header")?;

    let Some(given) = request_ctx.get_item(&header_name)? else {
        return Ok(false);
    };

    // A definition without a key is reported by the dispatcher
    let Some(expected) = field(sec_def, "password").filter(|value| value.is_truthy().unwrap_or(false)) else {
        return Ok(false);
    };

    let (Some(given_text), Some(expected_text)) = (as_text(&given), as_text(&expected)) else {
        return Ok(false);
    };

    Ok(constant_time_eq(given_text.as_bytes(), expected_text.as_bytes()))
}

/// Checks a static bearer token, leaving JWT definitions and definitions with claims to the dispatcher.
fn check_static_bearer_definition(sec_def: &Bound<'_, PyAny>, request_ctx: &Bound<'_, PyDict>) -> PyResult<bool> {
    // The verification config of these definitions is built with parsers whose errors the dispatcher reports
    if is_set(sec_def, "claims") || (is_set(sec_def, "auth_server_url") && !is_set(sec_def, "issuer")) {
        return Ok(false);
    }

    let header = authorization_header(request_ctx)?.unwrap_or_default();
    let token = extract_bearer_token(&header);

    if token.is_empty() {
        return Ok(false);
    }

    let mut static_token = field(sec_def, "static_token").filter(|value| value.is_truthy().unwrap_or(false));

    if static_token.is_none() && is_set(sec_def, "is_static_token") {
        static_token = Some(sec_def.get_item("password")?);
    }

    let Some(expected) = static_token.as_ref().and_then(as_text).filter(|text| !text.is_empty()) else {
        return Ok(false);
    };

    Ok(constant_time_eq(token.as_bytes(), expected.as_bytes()))
}

/// Writes the security context of an authenticated request, as `enrich_with_sec_data` of Python writes it.
pub fn enrich_with_sec_data(request_ctx: &Bound<'_, PyDict>, sec_def: &Bound<'_, PyAny>, sec_type: &str) -> PyResult<()> {
    let py = request_ctx.py();

    let implementation = PyDict::new(py);
    for item in sec_def.call_method0("items")?.try_iter()? {
        let (key, value) = item?.extract::<(Bound<'_, PyAny>, Bound<'_, PyAny>)>()?;
        let is_secret = as_text(&key).is_some_and(|name| SECRET_FIELDS.contains(&name.as_str()));
        if !is_secret {
            implementation.set_item(key, value)?;
        }
    }

    let sec_def_info = PyDict::new(py);
    request_ctx.set_item(SEC_DEF_KEY, &sec_def_info)?;

    sec_def_info.set_item("id", sec_def.get_item("id")?)?;
    sec_def_info.set_item("name", sec_def.get_item("name")?)?;
    sec_def_info.set_item("username", sec_def.call_method1("get", ("username",))?)?;
    sec_def_info.set_item("impl", implementation)?;
    sec_def_info.set_item("type", sec_type)?;

    Ok(())
}
