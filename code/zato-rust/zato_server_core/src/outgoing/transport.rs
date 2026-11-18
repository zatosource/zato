//! `HTTPTransport`, the transport an outgoing REST connection sends its requests through.
//!
//! One transport belongs to one outgoing connection and keeps its pool of connections, its timeout,
//! the default headers of its requests session and its TLS configuration. A request reaches its endpoint
//! directly, through an HTTP proxy in absolute form for an `http` address, or through a tunnel the proxy opens
//! with `CONNECT` for an `https` address. An invocation the transport does not implement returns `None` before
//! anything is sent, and the connection then sends it through requests.

use std::sync::Arc;
use std::time::Instant;

use parking_lot::Mutex;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString, PyTuple};
use rustls::ClientConfig;

use super::address::{self, Target};
use super::error::{RequestsExceptions, TransportError};
use super::exchange::{OutgoingRequest, Peer, RawResponse, connect, exchange};
use super::headers::{HeadInput, HeadLayout, PROXY_AUTHORIZATION_HEADER, build_head, encode_text_value, is_valid_method, is_valid_name};
use super::pool::{OriginKey, Pool, ProxyKey};
use super::stream::IoContext;
use super::tls::{TlsSettings, build_config};
use super::wait::Gevent;

/// The largest body written in the same buffer as the head of its request rather than in a write of its own.
const MAX_INLINE_BODY_LEN: usize = 64 * 1024;

/// The lowercase name of the response header that sets a cookie.
const SET_COOKIE_HEADER: &str = "set-cookie";

/// The proxy of a call as Python passes it - the host, the port, and the value of the `Proxy-Authorization`
/// header the credentials of the proxy produce, if it has any.
type ProxyArgument = (String, u16, Option<String>);

/// The HTTP proxy a request is sent through.
struct Proxy {
    /// The host name or IP address of the proxy.
    host: String,

    /// The port of the proxy.
    port: u16,

    /// The value of the `Proxy-Authorization` header, as sent.
    authorization: Option<Vec<u8>>,
}

impl Proxy {
    /// The proxy of a call, or `NeedsRequests` if its credentials produce a header the transport does not send.
    fn from_argument(argument: &ProxyArgument) -> Result<Self, TransportError> {
        let (host, port, authorization) = argument;

        let authorization = match authorization {
            Some(text) => Some(encode_text_value(text).ok_or(TransportError::NeedsRequests)?),
            None => None,
        };

        Ok(Self {
            host: host.clone(),
            port: *port,
            authorization,
        })
    }

    /// The part of the key of a pooled connection that tells connections through different proxies apart.
    fn key(&self) -> ProxyKey {
        ProxyKey {
            host: self.host.clone(),
            port: self.port,
            authorization: self.authorization.clone(),
        }
    }
}

/// How a request reaches its endpoint.
enum Route<'call> {
    /// Over a connection to the endpoint itself.
    Direct,

    /// Over a connection to an HTTP proxy, with the address of the endpoint in the request line.
    Proxied(&'call Proxy),

    /// Over a tunnel to the endpoint an HTTP proxy opens in response to a `CONNECT` request.
    Tunnel {
        /// The proxy.
        proxy: &'call Proxy,

        /// The `CONNECT` request, its head complete.
        connect_request: &'call [u8],
    },
}

/// The default headers of a requests session, the name and the value as sent.
type DefaultHeaders = Arc<Vec<(String, Vec<u8>)>>;

/// The value of an `Authorization` header, as sent.
type Authorization = Arc<Vec<u8>>;

/// The configuration of a transport, replaced by the connection whenever its own configuration changes.
struct Settings {
    /// The timeout of each connect and each read, in seconds, or `None` for no timeout.
    timeout: Option<f64>,

    /// The default headers of the requests session of the connection.
    defaults: DefaultHeaders,

    /// The value of the `Authorization` header the credentials of the connection produce, if they produce one.
    authorization: Option<Authorization>,

    /// How TLS connections are established.
    tls: TlsSettings,

    /// The TLS configuration built from the settings, once a TLS connection needed it.
    tls_config: Option<Arc<ClientConfig>>,

    /// Incremented whenever the TLS settings change, so a configuration built from older settings is not kept.
    tls_generation: u64,
}

/// What one invocation needs of the settings, taken out so no lock is held while the invocation waits.
struct CallSettings {
    /// The timeout of each connect and each read.
    timeout: Option<f64>,

    /// The default headers of the requests session.
    defaults: DefaultHeaders,

    /// The value of the `Authorization` header, if the call uses the credentials of the connection.
    authorization: Option<Authorization>,

    /// The TLS configuration, if the request uses TLS.
    tls_config: Option<Arc<ClientConfig>>,
}

/// Where the TLS configuration of a TLS request comes from.
enum TlsSource {
    /// The configuration built for an earlier request.
    Built(Arc<ClientConfig>),

    /// The settings a configuration is built from, because none was built since they last changed.
    Settings(TlsSettings),
}

/// One call from Python, as received.
struct Call<'call, 'py> {
    /// The method, in whatever case the caller used.
    method: &'call str,

    /// The full address, including the query string.
    url: &'call str,

    /// The headers of the call.
    headers: &'call Bound<'py, PyDict>,

    /// The body, if any.
    body: Option<&'call Bound<'py, PyBytes>>,

    /// The `Content-Type` requests gives the body it encoded itself, sent unless the headers have one.
    content_type: Option<&'call str>,

    /// The HTTP proxy the request is sent through, if any.
    proxy: Option<&'call ProxyArgument>,

    /// Whether the request carries the `Authorization` header the credentials of the connection produce.
    is_authorized: bool,
}

/// The transport of one outgoing REST connection.
#[pyclass(module = "zato_server_core", frozen)]
pub struct HTTPTransport {
    /// The idle connections, per endpoint.
    pool: Pool,

    /// The configuration of the transport.
    settings: Mutex<Settings>,

    /// The gevent functions the transport waits and resolves host names through.
    gevent: Gevent,

    /// The requests exception classes errors are raised as.
    exceptions: RequestsExceptions,

    /// The `User-Agent` urllib3 sends in a request that has none of its own.
    user_agent: Vec<u8>,
}

#[pymethods]
impl HTTPTransport {
    /// Creates a transport that keeps up to `pool_size` idle connections per endpoint, without a timeout,
    /// without default headers and with TLS verified against no CA bundle until it is configured.
    #[new]
    fn new(py: Python<'_>, pool_size: usize) -> PyResult<Self> {
        let user_agent: String = py
            .import("urllib3.connection")?
            .getattr("_get_default_user_agent")?
            .call0()?
            .extract()?;

        Ok(Self {
            user_agent: user_agent.into_bytes(),
            pool: Pool::new(pool_size),
            settings: Mutex::new(Settings {
                timeout: None,
                defaults: Arc::new(Vec::new()),
                authorization: None,
                tls: TlsSettings::default(),
                tls_config: None,
                tls_generation: 0,
            }),
            gevent: Gevent::import(py)?,
            exceptions: RequestsExceptions::import(py)?,
        })
    }

    /// Sets the timeout of each connect and each read, in seconds, or `None` for no timeout.
    fn set_timeout(&self, timeout: Option<f64>) {
        self.settings.lock().timeout = timeout;
    }

    /// Sets the default headers of the requests session, in their order, returning whether the transport
    /// accepts all of them. A header whose value is `None` is not sent, as requests does not send it.
    fn set_default_headers(&self, headers: &Bound<'_, PyDict>) -> PyResult<bool> {
        let mut defaults = Vec::with_capacity(headers.len());

        for (key, value) in headers.iter() {
            if value.is_none() {
                continue;
            }

            // A header requests would send in a form the transport does not reproduce is not accepted
            let (Ok(name), Ok(text)) = (key.cast::<PyString>(), value.cast::<PyString>()) else {
                return Ok(false);
            };

            let name = name.to_str()?;
            if !is_valid_name(name) {
                return Ok(false);
            }

            let Some(encoded) = encode_text_value(text.to_str()?) else {
                return Ok(false);
            };

            defaults.push((name.to_owned(), encoded));
        }

        self.settings.lock().defaults = Arc::new(defaults);
        Ok(true)
    }

    /// Sets the value of the `Authorization` header the credentials of the connection produce, or `None`
    /// if they produce none, returning whether the transport accepts the value.
    ///
    /// A value the transport does not accept is stored as no value, so calls that use it are sent through requests.
    #[pyo3(signature = (value))]
    fn set_authorization(&self, value: Option<&str>) -> bool {
        let authorization = value.and_then(encode_text_value).map(Arc::new);
        let is_accepted = value.is_none() || authorization.is_some();

        self.settings.lock().authorization = authorization;
        is_accepted
    }

    /// Sets how TLS connections are established - the CA bundle to verify against, or `None` to not verify,
    /// and the client certificate with its key, if any. Changed settings close the idle connections.
    #[pyo3(signature = (ca_path, client_cert, client_key))]
    fn set_tls(&self, ca_path: Option<String>, client_cert: Option<String>, client_key: Option<String>) {
        let tls = TlsSettings {
            ca_path,
            client_cert,
            client_key,
        };

        {
            let mut settings = self.settings.lock();

            if settings.tls == tls {
                return;
            }

            settings.tls = tls;
            settings.tls_config = None;
            settings.tls_generation += 1;
        }

        // Connections established with the previous settings are not reused with the new ones
        self.pool.clear();
    }

    /// Closes the idle connections and discards the TLS configuration, so the certificate files are read again.
    fn clear_pool(&self) {
        {
            let mut settings = self.settings.lock();
            settings.tls_config = None;
            settings.tls_generation += 1;
        }

        self.pool.clear();
    }

    /// Sends a request and returns its response as a tuple of the status code, the reason phrase, the headers
    /// keyed by their lowercase names, the body, the elapsed time in microseconds, the values of each Set-Cookie
    /// header and the address as requests prepares it, or `None` if the request is to be sent through requests instead.
    ///
    /// `content_type` is the `Content-Type` of a body requests would encode itself, and `proxy` is the HTTP proxy
    /// the request is sent through, as the host, the port and the value of its `Proxy-Authorization` header.
    #[pyo3(signature = (method, url, headers, body, content_type = None, proxy = None))]
    fn invoke<'py>(
        &self,
        method: &str,
        url: &str,
        headers: &Bound<'py, PyDict>,
        body: Option<&Bound<'py, PyBytes>>,
        content_type: Option<&str>,
        proxy: Option<ProxyArgument>,
    ) -> PyResult<Option<Bound<'py, PyTuple>>> {
        let call = Call {
            method,
            url,
            headers,
            body,
            content_type,
            proxy: proxy.as_ref(),
            is_authorized: false,
        };

        self.complete(&call)
    }

    /// Sends a request with the `Authorization` header the credentials of the connection produce, applied
    /// after all the other headers, and returns what `invoke` returns.
    #[pyo3(signature = (method, url, headers, body, content_type = None, proxy = None))]
    fn invoke_with_auth<'py>(
        &self,
        method: &str,
        url: &str,
        headers: &Bound<'py, PyDict>,
        body: Option<&Bound<'py, PyBytes>>,
        content_type: Option<&str>,
        proxy: Option<ProxyArgument>,
    ) -> PyResult<Option<Bound<'py, PyTuple>>> {
        let call = Call {
            method,
            url,
            headers,
            body,
            content_type,
            proxy: proxy.as_ref(),
            is_authorized: true,
        };

        self.complete(&call)
    }
}

/// One invocation, its request already validated.
struct Invocation<'call> {
    /// The prepared address of the endpoint.
    target: &'call Target,

    /// How the request reaches the endpoint.
    route: Route<'call>,

    /// The request target, as the messages of errors name it.
    request_target: &'call str,

    /// The request as written to the connection.
    request: OutgoingRequest<'call>,

    /// The settings the invocation uses.
    settings: CallSettings,
}

impl HTTPTransport {
    /// Sends a call and converts its outcome to what Python receives.
    fn complete<'py>(&self, call: &Call<'_, 'py>) -> PyResult<Option<Bound<'py, PyTuple>>> {
        let py = call.headers.py();

        match self.send(call) {
            Ok((response, url)) => Ok(Some(build_response_tuple(py, response, &url)?)),
            Err(TransportError::NeedsRequests) => Ok(None),
            Err(error) => Err(self.exceptions.to_py_err(py, error)),
        }
    }

    /// Validates and sends a request, returning its response and the address as requests prepares it.
    fn send(&self, call: &Call<'_, '_>) -> Result<(RawResponse, String), TransportError> {
        let start = Instant::now();
        let py = call.headers.py();

        // requests sends the method in uppercase whatever case the caller used
        let method = call.method.to_ascii_uppercase();
        if !is_valid_method(&method) {
            return Err(TransportError::NeedsRequests);
        }

        let target = address::parse(call.url).ok_or(TransportError::NeedsRequests)?;
        let proxy = call.proxy.map(Proxy::from_argument).transpose()?;
        let settings = self.call_settings(target.is_tls, call.is_authorized)?;

        // requests reads the credentials in the address only for a call that has none of its own
        let authorization = match &settings.authorization {
            Some(value) => Some(value.as_slice()),
            None => target.authorization.as_deref(),
        };

        let content_type = match call.content_type {
            Some(text) => Some(encode_text_value(text).ok_or(TransportError::NeedsRequests)?),
            None => None,
        };

        // requests sends an empty body as no body at all
        let body = call.body.map(PyBytesMethods::as_bytes).filter(|body| !body.is_empty());

        // A request to an http endpoint goes to the proxy whole, and one to an https endpoint through a tunnel
        let is_proxied = proxy.is_some() && !target.is_tls;
        let is_tunneled = proxy.is_some() && target.is_tls;

        let absolute_form = is_proxied.then(|| target.absolute_form());
        let request_target = absolute_form.as_deref().unwrap_or(&target.path_and_query);

        let host_header = if is_tunneled {
            target.tunneled_host_header()
        } else {
            target.host_header()
        };

        let layout = match &proxy {
            Some(proxy) if is_proxied => HeadLayout::Proxied {
                netloc: target.netloc(),
                proxy_authorization: proxy.authorization.as_deref(),
            },
            _ => HeadLayout::Origin { host_header: &host_header },
        };

        let input = HeadInput {
            method: &method,
            request_target,
            layout,
            defaults: &settings.defaults,
            headers: call.headers,
            body_len: body.map(<[u8]>::len),
            content_type: content_type.as_deref(),
            authorization,
            user_agent: &self.user_agent,
        };

        let mut head = build_head(&input)
            .map_err(TransportError::Python)?
            .ok_or(TransportError::NeedsRequests)?;

        let connect_request = match &proxy {
            Some(proxy) if is_tunneled => Some(build_connect_request(&target, proxy)),
            _ => None,
        };

        let route = match (&proxy, &connect_request) {
            (Some(proxy), Some(connect_request)) => Route::Tunnel { proxy, connect_request },
            (Some(proxy), None) => Route::Proxied(proxy),
            (None, _) => Route::Direct,
        };

        // A small body is written together with the head, so the request takes a single write
        let separate_body = match body {
            Some(body) if body.len() <= MAX_INLINE_BODY_LEN => {
                head.extend_from_slice(body);
                None
            }
            other => other,
        };

        let invocation = Invocation {
            target: &target,
            route,
            request_target,
            request: OutgoingRequest {
                head: &head,
                body: separate_body,
                is_head: method == "HEAD",
                start,
            },
            settings,
        };

        let response = self.run(py, &invocation)?;
        Ok((response, target.url))
    }

    /// Takes what an invocation needs of the settings, building the TLS configuration if a TLS request needs it.
    fn call_settings(&self, is_tls: bool, is_authorized: bool) -> Result<CallSettings, TransportError> {
        let (timeout, defaults, authorization, tls_source, generation) = {
            let settings = self.settings.lock();

            // The TLS settings are copied only when a TLS configuration is to be built from them
            let tls_source = if !is_tls {
                None
            } else if let Some(config) = &settings.tls_config {
                Some(TlsSource::Built(Arc::clone(config)))
            } else {
                Some(TlsSource::Settings(settings.tls.clone()))
            };

            (
                settings.timeout,
                Arc::clone(&settings.defaults),
                settings.authorization.clone(),
                tls_source,
                settings.tls_generation,
            )
        };

        // A call that uses the credentials of a connection whose credentials produce no header is left to requests
        let authorization = if is_authorized {
            Some(authorization.ok_or(TransportError::NeedsRequests)?)
        } else {
            None
        };

        let tls_config = match tls_source {
            None => {
                return Ok(CallSettings {
                    timeout,
                    defaults,
                    authorization,
                    tls_config: None,
                });
            }

            Some(TlsSource::Built(config)) => config,

            Some(TlsSource::Settings(tls)) => {
                // A certificate file requests could not use either is left to requests, which reports it as it always has
                let config = build_config(&tls).map_err(|_build_error| TransportError::NeedsRequests)?;

                // The configuration is kept only if the settings did not change while it was being built
                let mut settings = self.settings.lock();
                if settings.tls_generation == generation {
                    settings.tls_config = Some(Arc::clone(&config));
                }

                config
            }
        };

        Ok(CallSettings {
            timeout,
            defaults,
            authorization,
            tls_config: Some(tls_config),
        })
    }

    /// Sends the request on a pooled connection or a new one and reads its response, repeating it once
    /// on a new connection if a pooled connection turns out to have been closed by the endpoint.
    fn run(&self, py: Python<'_>, invocation: &Invocation<'_>) -> Result<RawResponse, TransportError> {
        let target = invocation.target;

        let ctx = IoContext {
            py,
            gevent: &self.gevent,
            timeout: invocation.settings.timeout,
        };

        let (peer, key) = match &invocation.route {
            Route::Direct => (
                Peer {
                    is_tls: target.is_tls,
                    host: &target.host,
                    port: target.port,
                    pool_host: &target.host,
                    pool_port: target.port,
                    server_name: target.server_name(),
                    request_target: invocation.request_target,
                    timeout: invocation.settings.timeout,
                    tunnel: None,
                    is_proxied: false,
                },
                OriginKey {
                    is_tls: target.is_tls,
                    host: target.host.clone(),
                    port: target.port,
                    proxy: None,
                },
            ),

            // urllib3 keeps one pool per proxy for all http endpoints and names the proxy in its messages
            Route::Proxied(proxy) => (
                Peer {
                    is_tls: false,
                    host: &proxy.host,
                    port: proxy.port,
                    pool_host: &proxy.host,
                    pool_port: proxy.port,
                    server_name: &proxy.host,
                    request_target: invocation.request_target,
                    timeout: invocation.settings.timeout,
                    tunnel: None,
                    is_proxied: true,
                },
                OriginKey {
                    is_tls: false,
                    host: proxy.host.clone(),
                    port: proxy.port,
                    proxy: Some(proxy.key()),
                },
            ),

            // urllib3 keeps one pool per https endpoint and proxy, and verifies the endpoint's certificate
            Route::Tunnel { proxy, connect_request } => (
                Peer {
                    is_tls: true,
                    host: &proxy.host,
                    port: proxy.port,
                    pool_host: &target.host,
                    pool_port: target.port,
                    server_name: target.tunnel_server_name(),
                    request_target: invocation.request_target,
                    timeout: invocation.settings.timeout,
                    tunnel: Some(connect_request),
                    is_proxied: true,
                },
                OriginKey {
                    is_tls: true,
                    host: target.host.clone(),
                    port: target.port,
                    proxy: Some(proxy.key()),
                },
            ),
        };

        let tls_config = invocation.settings.tls_config.as_ref();

        let (mut stream, mut is_reused) = match self.pool.checkout(&key) {
            Some(stream) => (stream, true),
            None => (connect(&ctx, &peer, tls_config)?, false),
        };

        loop {
            match exchange(&ctx, &peer, &mut stream, &invocation.request) {
                Ok(response) => {
                    // A connection is kept only if the endpoint keeps it open and nothing else is left on it
                    if response.is_keep_alive {
                        self.pool.checkin(key, stream);
                    }
                    return Ok(response);
                }

                // An idle connection the endpoint closed in the meantime fails before any byte of the response,
                // and the request is sent again on a new connection, once
                Err(failure) if is_reused && failure.is_before_response => {
                    stream = connect(&ctx, &peer, tls_config)?;
                    is_reused = false;
                }

                Err(failure) => return Err(failure.error),
            }
        }
    }
}

/// Builds the `CONNECT` request that asks a proxy for a tunnel to the endpoint, as `http.client` builds it.
fn build_connect_request(target: &Target, proxy: &Proxy) -> Vec<u8> {
    let mut request = target.connect_line().into_bytes();

    if let Some(authorization) = &proxy.authorization {
        request.extend_from_slice(PROXY_AUTHORIZATION_HEADER.as_bytes());
        request.extend_from_slice(b": ");
        request.extend_from_slice(authorization);
        request.extend_from_slice(b"\r\n");
    }

    request.extend_from_slice(b"Host: ");
    request.extend_from_slice(target.connect_host_header().as_bytes());
    request.extend_from_slice(b"\r\n\r\n");

    request
}

/// Builds the tuple a response is returned to Python as.
fn build_response_tuple<'py>(py: Python<'py>, response: RawResponse, url: &str) -> PyResult<Bound<'py, PyTuple>> {
    let header_store = PyDict::new(py);

    // Repeated headers are joined with a comma, under the name the first of them was sent with, as urllib3 joins them
    let mut merged: Vec<(String, String, String)> = Vec::with_capacity(response.head.headers.len());

    // Cookie values may contain commas of their own, so the cookie jar receives each Set-Cookie header separately
    let mut set_cookie_list: Vec<String> = Vec::new();

    for (name, value) in response.head.headers {
        let lowercase = name.to_ascii_lowercase();

        if lowercase == SET_COOKIE_HEADER {
            set_cookie_list.push(value.clone());
        }

        if let Some(existing) = merged.iter_mut().find(|(key, _, _)| *key == lowercase) {
            existing.2.push_str(", ");
            existing.2.push_str(&value);
        } else {
            merged.push((lowercase, name, value));
        }
    }

    for (lowercase, name, value) in merged {
        header_store.set_item(lowercase, (name, value))?;
    }

    let elapsed_us = u64::try_from(response.elapsed.as_micros()).unwrap_or(u64::MAX);
    let body = PyBytes::new(py, &response.body);

    let set_cookies = PyTuple::new(py, set_cookie_list)?;

    let items: [Bound<'_, PyAny>; 7] = [
        response.head.status.into_pyobject(py)?.into_any(),
        PyString::new(py, &response.head.reason).into_any(),
        header_store.into_any(),
        body.into_any(),
        elapsed_us.into_pyobject(py)?.into_any(),
        set_cookies.into_any(),
        PyString::new(py, url).into_any(),
    ];

    PyTuple::new(py, items)
}
