//! One job of the push engine, run on a thread of the engine without the GIL.
//!
//! The requests of a job are sent one after another, each on a pooled connection or a new one,
//! following its redirects, and the job stops at the first request that was not fully concluded.

use std::sync::Arc;
use std::time::Instant;

use parking_lot::Mutex;
use rustls::ClientConfig;

use super::job::{ErrorKind, FollowedRedirect, PushJob, PushRequest, RequestOutcome};
use super::redirect::next_redirect;
use super::reply::parse_accepted_ids;
use crate::outgoing::address::{self, Target};
use crate::outgoing::error::TransportError;
use crate::outgoing::exchange::{OutgoingRequest, Peer, RawResponse};
use crate::outgoing::headers::{ListHeadInput, build_list_head};
use crate::outgoing::pool::{OriginKey, Pool};
use crate::outgoing::scope::NetworkScope;
use crate::outgoing::send::{PooledSend, ScopedResponse, send_pooled};
use crate::outgoing::stream::{IoContext, Waiter};
use crate::outgoing::tls::{TlsSettings, build_config};
use crate::outgoing::transport::MAX_INLINE_BODY_LEN;

/// The method of every push request.
const PUSH_METHOD: &str = "POST";

/// The lowest status of a success.
const SUCCESS_MIN: u16 = 200;

/// The lowest status after the successes.
const SUCCESS_END: u16 = 300;

/// The lowest status of a client error.
const CLIENT_ERROR_MIN: u16 = 400;

/// The lowest status of a server error.
const SERVER_ERROR_MIN: u16 = 500;

/// The lowest status after the server errors.
const SERVER_ERROR_END: u16 = 600;

/// The lowercase name of the header that names the target of a redirect.
const LOCATION_HEADER: &str = "location";

/// The lowercase name of the header that declares the length of a body.
const CONTENT_LENGTH_HEADER: &str = "content-length";

/// The TLS configuration built from one set of TLS settings, with the idle connections established with it.
struct TlsEntry {

    /// The settings the configuration was built from.
    settings: TlsSettings,

    /// The generation of the TLS material the configuration was built from.
    generation: u64,

    /// The configuration.
    config: Arc<ClientConfig>,

    /// The idle TLS connections established with the configuration, per endpoint.
    pool: Arc<Pool>,
}

/// The idle connections of the engine, kept open between jobs.
pub struct EnginePools {

    /// The idle plain TCP connections, per endpoint.
    plain: Arc<Pool>,

    /// The TLS configurations and their idle connections, one entry per set of TLS settings in use.
    tls: Mutex<Vec<TlsEntry>>,

    /// How many idle connections are kept per endpoint.
    size: usize,
}

impl EnginePools {

    /// Creates empty pools that keep up to the given number of idle connections per endpoint.
    pub fn new(size: usize) -> Self {
        Self {
            plain: Arc::new(Pool::new(size)),
            tls: Mutex::new(Vec::new()),
            size,
        }
    }

    /// Returns the pool of a request and its TLS configuration, building the configuration on its first use
    /// and again when the generation of the TLS material is newer than the one it was built from.
    fn select(&self, is_tls: bool, settings: &TlsSettings, generation: u64) -> Result<(Arc<Pool>, Option<Arc<ClientConfig>>), String> {
        if !is_tls {
            return Ok((Arc::clone(&self.plain), None));
        }

        // The lock is held only to look the entry up, never while a configuration is built from files
        {
            let entries = self.tls.lock();

            if let Some(entry) = find_entry(&entries, settings, generation) {
                return Ok((Arc::clone(&entry.pool), Some(Arc::clone(&entry.config))));
            }
        }

        let config = build_config(settings)?;
        let pool = Arc::new(Pool::new(self.size));

        let mut entries = self.tls.lock();

        // Another thread may have built the same configuration in the meantime, and its entry is the one kept
        if let Some(entry) = find_entry(&entries, settings, generation) {
            return Ok((Arc::clone(&entry.pool), Some(Arc::clone(&entry.config))));
        }

        // An entry of an older generation of the same files is replaced, and its connections are closed
        // after the lock is released, since they present the material read before
        let position = entries.iter().position(|entry| entry.settings == *settings && entry.generation < generation);
        let replaced = position.map(|idx| entries.swap_remove(idx));

        entries.push(TlsEntry {
            settings: settings.clone(),
            generation,
            config: Arc::clone(&config),
            pool: Arc::clone(&pool),
        });

        drop(entries);

        if let Some(entry) = replaced {
            entry.pool.clear();
        }

        Ok((pool, Some(config)))
    }

    /// Closes the idle connections of every pool.
    pub fn clear(&self) {
        self.plain.clear();

        // The entries are taken out first, so their connections are closed after the lock is released
        let entries = std::mem::take(&mut *self.tls.lock());
        for entry in entries {
            entry.pool.clear();
        }
    }
}

/// Returns the TLS entry of the given settings, provided that it is of the given generation or a newer one.
fn find_entry<'entries>(entries: &'entries [TlsEntry], settings: &TlsSettings, generation: u64) -> Option<&'entries TlsEntry> {
    entries.iter().find(|entry| entry.settings == *settings && entry.generation >= generation)
}

/// Runs the requests of a job in order and returns the outcome of each request sent,
/// stopping at the first request that was not fully concluded.
pub fn run_job(pools: &EnginePools, job: &PushJob) -> Vec<RequestOutcome> {
    let mut out = Vec::with_capacity(job.requests.len());

    for request in &job.requests {
        let outcome = run_request(pools, job, request);
        let is_concluded = outcome.is_fully_concluded(request);

        out.push(outcome);

        // What follows a request that was not fully concluded is not sent, so the order of the messages holds
        if !is_concluded {
            break;
        }
    }

    out
}

/// Sends one request, following its redirects, and returns what it concluded.
fn run_request(pools: &EnginePools, job: &PushJob, request: &PushRequest) -> RequestOutcome {
    let mut outcome = RequestOutcome::new(&request.url);

    let Some(scoped) = send_following_redirects(pools, job, request, &mut outcome) else {
        return outcome;
    };

    let response = scoped.response;
    let status = response.head.status;

    outcome.status = Some(status);
    outcome.reason.clone_from(&response.head.reason);
    outcome.elapsed_us = u64::try_from(response.elapsed.as_micros()).unwrap_or(u64::MAX);

    // A push is delivered only when its endpoint accepts it with a 2xx status ..
    if !(SUCCESS_MIN..SUCCESS_END).contains(&status) {
        let message = status_error(&outcome.url, status, &response.head.reason);
        outcome.fail(ErrorKind::Status, message);
        return outcome;
    }

    // .. and its response arrived in full, since an endpoint that closed the connection in the middle of it
    // .. may not have processed the messages ..
    if let Some(message) = incomplete_error(&outcome.url, &response) {
        outcome.fail(ErrorKind::Incomplete, message);
        return outcome;
    }

    // .. a single message is concluded by the status, while a list names the messages it accepted.
    if request.is_list {
        match parse_accepted_ids(&response.body, &request.msg_ids) {
            Ok(accepted) => outcome.concluded = accepted,
            Err(message) => outcome.fail(ErrorKind::Reply, message),
        }
    } else {
        outcome.concluded.clone_from(&request.msg_ids);
    }

    outcome
}

/// Sends a request to its address and to each address its redirects lead to, within the scope of the first push,
/// and returns the final response, or `None` with the error recorded in the outcome.
fn send_following_redirects(
    pools: &EnginePools,
    job: &PushJob,
    request: &PushRequest,
    outcome: &mut RequestOutcome,
) -> Option<ScopedResponse> {
    let mut url = request.url.clone();
    let mut hop_count = 0;
    let mut first_scope: Option<NetworkScope> = None;

    loop {
        // Each redirect followed is sent only to an address of the scope of the first push
        let required_scope = if hop_count == 0 { None } else { first_scope };

        let scoped = match send_once(pools, job, request, &url, required_scope) {
            Ok(scoped) => scoped,
            Err((kind, message)) => {
                outcome.url = url;
                outcome.fail(kind, message);
                return None;
            }
        };

        if hop_count == 0 {
            first_scope = scoped.peer_scope;
            outcome.peer_scope = first_scope;
        }

        let status = scoped.response.head.status;
        let location = find_header(&scoped.response, LOCATION_HEADER);

        match next_redirect(&url, status, location.as_deref(), hop_count, first_scope) {
            Ok(Some(next_url)) => {
                outcome.redirects.push(FollowedRedirect {
                    status,
                    from_url: url,
                    to_url: next_url.clone(),
                });
                hop_count += 1;
                url = next_url;
            }
            Ok(None) => {
                outcome.url = url;
                return Some(scoped);
            }
            Err(message) => {
                outcome.url = url;
                outcome.fail(ErrorKind::Redirect, message);
                return None;
            }
        }
    }
}

/// Sends a request to one address and reads its response.
fn send_once(
    pools: &EnginePools,
    job: &PushJob,
    request: &PushRequest,
    url: &str,
    required_scope: Option<NetworkScope>,
) -> Result<ScopedResponse, (ErrorKind, String)> {
    let start = Instant::now();

    let target = address::parse(url).ok_or_else(|| (ErrorKind::Address, format!("Push to `{url}` not sent, the address is not supported")))?;

    let (pool, tls_config) = pools.select(target.is_tls, &job.tls, job.tls_generation).map_err(|message| (ErrorKind::TlsConfig, message))?;

    // Empty parts carry nothing to write
    let parts: Vec<&[u8]> = request.parts.iter().map(Vec::as_slice).filter(|part| !part.is_empty()).collect();
    let total_len: usize = parts.iter().map(|part| part.len()).sum();
    let body_len = (!parts.is_empty()).then_some(total_len);

    let mut head = build_list_head(&ListHeadInput {
        method: PUSH_METHOD,
        request_target: &target.path_and_query,
        host_header: &target.host_header,
        headers: &request.headers,
        body_len,
    });

    // A small body is written together with the head, so the request takes a single write
    let separate_parts: &[&[u8]] = if total_len <= MAX_INLINE_BODY_LEN {
        for part in &parts {
            head.extend_from_slice(part);
        }
        &[]
    } else {
        &parts
    };

    let outgoing = OutgoingRequest {
        head: &head,
        body: separate_parts,
        is_head: false,
        start,
    };

    let ctx = IoContext {
        waiter: Waiter::Blocking,
        timeout: job.timeout,
    };

    let peer = Peer {
        is_tls: target.is_tls,
        host: target.host,
        port: target.port,
        request_target: &target.path_and_query,
        timeout: job.timeout,
        required_scope,
    };

    let send = PooledSend {
        peer: &peer,
        key: origin_key(&target),
        tls_config: tls_config.as_ref(),
        request: &outgoing,
    };

    send_pooled(&ctx, &pool, send).map_err(transport_error)
}

/// The key of the idle connections to the endpoint of an address.
fn origin_key(target: &Target<'_>) -> OriginKey {
    OriginKey {
        is_tls: target.is_tls,
        host: target.host.to_owned(),
        port: target.port,
    }
}

/// The value of a response header, repeated headers joined with a comma as urllib3 joins them.
fn find_header(response: &RawResponse, lowercase_name: &str) -> Option<String> {
    let mut values = response
        .head
        .headers
        .iter()
        .filter(|(name, _)| name.eq_ignore_ascii_case(lowercase_name))
        .map(|(_, value)| value.as_str());

    let first = values.next()?;
    let mut out = first.to_owned();

    for value in values {
        out.push_str(", ");
        out.push_str(value);
    }

    Some(out)
}

/// The error of a response whose status is not a success, worded as requests words it.
fn status_error(url: &str, status: u16, reason: &str) -> String {
    if (CLIENT_ERROR_MIN..SERVER_ERROR_MIN).contains(&status) {
        return format!("{status} Client Error: {reason} for url: {url}");
    }

    if (SERVER_ERROR_MIN..SERVER_ERROR_END).contains(&status) {
        return format!("{status} Server Error: {reason} for url: {url}");
    }

    format!("{status} Not a success: {reason} for url: {url}")
}

/// The error of a response that ended before the length it declared, if it did.
fn incomplete_error(url: &str, response: &RawResponse) -> Option<String> {
    let declared = find_header(response, CONTENT_LENGTH_HEADER)?;
    let expected: usize = declared.trim().parse().ok()?;
    let received = response.body.len();

    (received < expected).then(|| format!("Incomplete response from {url}, received {received} of {expected} bytes"))
}

/// The kind of a transport error and its message, as requests words the same failure.
fn transport_error(error: TransportError) -> (ErrorKind, String) {
    match error {
        TransportError::ConnectTimeout(message) => (ErrorKind::ConnectTimeout, message),
        TransportError::ReadTimeout(message) => (ErrorKind::ReadTimeout, message),
        TransportError::Connection(message) => (ErrorKind::Connection, message),
        TransportError::Tls(message) => (ErrorKind::Tls, message),
        TransportError::ChunkedEncoding(message) => (ErrorKind::Chunked, message),
        TransportError::ScopeRefused(message) => (ErrorKind::ScopeRefused, message),

        // A thread of the engine runs no Python code, so neither of these occurs, but each still has a message
        TransportError::Python(err) => (ErrorKind::Connection, err.to_string()),
        TransportError::NeedsRequests => (ErrorKind::Address, String::from("Request not supported by the push engine")),
    }
}

#[cfg(test)]
#[path = "run_tests.rs"]
mod tests;
