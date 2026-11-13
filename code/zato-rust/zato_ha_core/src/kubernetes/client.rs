// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The client of the Kubernetes API server that the referee and the label thread share.
//!
//! In a pod, the client authenticates with the token of the service account and verifies the API server against
//! the CA of the cluster, and every request is made in the namespace of the service account.

use std::sync::Arc;
use std::time::Duration;

use ureq::RequestBuilder;
use ureq::tls::{Certificate, RootCerts, TlsConfig};

/// The environment variable with the host of the API server, which Kubernetes sets in every pod.
pub const ENV_SERVICE_HOST: &str = "KUBERNETES_SERVICE_HOST";

/// The environment variable with the port of the API server.
pub const ENV_SERVICE_PORT: &str = "KUBERNETES_SERVICE_PORT";

/// The directory of the service account credentials.
const SERVICE_ACCOUNT_DIR: &str = "/var/run/secrets/kubernetes.io/serviceaccount";

/// How long one request to the API server may take, which remains shorter than the gap between the mark-out
/// and the takeover timers.
pub const REQUEST_TIMEOUT: Duration = Duration::from_secs(1);

/// The content type of a JSON document.
pub const CONTENT_TYPE_JSON: &str = "application/json";

/// The content type of a JSON Patch.
pub const CONTENT_TYPE_JSON_PATCH: &str = "application/json-patch+json";

/// The content type of a JSON merge patch.
pub const CONTENT_TYPE_MERGE_PATCH: &str = "application/merge-patch+json";

/// The status and the body of a response of the API server.
pub struct Response {
    /// The HTTP status.
    pub status: u16,

    /// The body.
    pub body: Vec<u8>,
}

/// A client of the API server in one namespace.
#[derive(Clone)]
pub struct ApiClient {
    /// The HTTP client.
    agent: ureq::Agent,

    /// The scheme, the host and the port of the API server.
    base_url: String,

    /// The namespace of every request.
    namespace: String,

    /// The bearer token, or `None` for an API server reached through `kubectl proxy`.
    token: Option<String>,
}

impl ApiClient {
    /// Returns the client of the service account of the pod, or an error if the node does not run in Kubernetes.
    pub fn from_service_account() -> Result<Self, String> {
        let host = std::env::var(ENV_SERVICE_HOST).map_err(|_| format!("{ENV_SERVICE_HOST} is not set"))?;
        let port = std::env::var(ENV_SERVICE_PORT).map_err(|_| format!("{ENV_SERVICE_PORT} is not set"))?;
        let read =
            |name: &str| std::fs::read(format!("{SERVICE_ACCOUNT_DIR}/{name}")).map_err(|error| format!("Service account {name}: {error}"));
        let token = String::from_utf8(read("token")?).map_err(|error| error.to_string())?;
        let namespace = String::from_utf8(read("namespace")?).map_err(|error| error.to_string())?;
        let ca_pem = read("ca.crt")?;
        Self::new(
            &format!("https://{host}:{port}"),
            namespace.trim(),
            Some(token.trim().to_owned()),
            Some(&ca_pem),
        )
    }

    /// Returns a client of the API server at `base_url`, verified against `ca_pem` if it is reached over TLS.
    pub fn new(base_url: &str, namespace: &str, token: Option<String>, ca_pem: Option<&[u8]>) -> Result<Self, String> {
        let mut builder = ureq::Agent::config_builder()
            .timeout_global(Some(REQUEST_TIMEOUT))
            .http_status_as_error(false);
        if let Some(ca_pem) = ca_pem {
            let certificate = Certificate::from_pem(ca_pem).map_err(|error| error.to_string())?;
            builder = builder.tls_config(
                TlsConfig::builder()
                    .root_certs(RootCerts::new_with_certs(&[certificate]))
                    .unversioned_rustls_crypto_provider(Arc::new(rustls::crypto::ring::default_provider()))
                    .build(),
            );
        }
        Ok(Self {
            agent: builder.build().into(),
            base_url: base_url.to_owned(),
            namespace: namespace.to_owned(),
            token,
        })
    }

    /// Returns the URL of a collection of the namespace, e.g. `apis/coordination.k8s.io/v1` and `leases`.
    pub fn collection_url(&self, group_version: &str, resource: &str) -> String {
        format!("{}/{group_version}/namespaces/{}/{resource}", self.base_url, self.namespace)
    }

    /// Sends a `GET` to `url`.
    pub fn get(&self, url: &str) -> Result<Response, String> {
        let request = self.authorize(self.agent.get(url));
        Self::receive("GET", url, request.call())
    }

    /// Sends a `POST` of a JSON document to `url`.
    pub fn post(&self, url: &str, body: &[u8]) -> Result<Response, String> {
        let request = self.authorize(self.agent.post(url)).header("Content-Type", CONTENT_TYPE_JSON);
        Self::receive("POST", url, request.send(body))
    }

    /// Sends a `PUT` of a JSON document to `url`.
    pub fn put(&self, url: &str, body: &[u8]) -> Result<Response, String> {
        let request = self.authorize(self.agent.put(url)).header("Content-Type", CONTENT_TYPE_JSON);
        Self::receive("PUT", url, request.send(body))
    }

    /// Sends a `PATCH` of `content_type` to `url`.
    pub fn patch(&self, url: &str, content_type: &str, body: &[u8]) -> Result<Response, String> {
        let request = self.authorize(self.agent.patch(url)).header("Content-Type", content_type);
        Self::receive("PATCH", url, request.send(body))
    }

    /// Adds the bearer token to a request if the client has one.
    fn authorize<B>(&self, request: RequestBuilder<B>) -> RequestBuilder<B> {
        match &self.token {
            Some(token) => request.header("Authorization", &format!("Bearer {token}")),
            None => request,
        }
    }

    /// Reads the status and the body of a response, in which a failure to receive either is an error.
    fn receive(
        method: &str,
        url: &str,
        outcome: Result<ureq::http::Response<ureq::Body>, ureq::Error>,
    ) -> Result<Response, String> {
        let mut response = outcome.map_err(|error| format!("{method} {url}: {error}"))?;
        let status = response.status().as_u16();
        let body = response
            .body_mut()
            .read_to_vec()
            .map_err(|error| format!("{method} {url}: {error}"))?;
        Ok(Response { status, body })
    }
}
