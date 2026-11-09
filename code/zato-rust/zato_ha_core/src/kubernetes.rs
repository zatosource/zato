// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The `zato-role=active` label of the pod of the active node, which the Service selects.
//!
//! The node labels its own pod while it serves traffic and removes the label otherwise. Before it labels
//! its own pod, it removes the label from the pod of the other node, which may have lost its connection to the
//! API server while it was being replaced, so that the Service never selects two pods at once.

use std::sync::Arc;
use std::time::Duration;

use serde::Serialize;
use ureq::tls::{Certificate, RootCerts, TlsConfig};

use crate::state::Shared;
use crate::wire;

/// The environment variable that is set in every pod.
const ENV_SERVICE_HOST: &str = "KUBERNETES_SERVICE_HOST";

/// The environment variable with the port of the API server.
const ENV_SERVICE_PORT: &str = "KUBERNETES_SERVICE_PORT";

/// The directory of the service account credentials.
const SERVICE_ACCOUNT_DIR: &str = "/var/run/secrets/kubernetes.io/serviceaccount";

/// The label the Service selects.
pub const ROLE_LABEL: &str = "zato-role";

/// The value of the label on the active pod.
pub const ROLE_LABEL_ACTIVE: &str = "active";

/// How long one request to the API server may take.
const REQUEST_TIMEOUT: Duration = Duration::from_secs(2);

/// How often the label is compared with the role when nothing notifies the thread.
const CHECK_INTERVAL: Duration = Duration::from_millis(500);

/// The labels of a merge patch, in which `None` removes the label.
#[derive(Serialize)]
struct Labels {
    /// The role label.
    #[serde(rename = "zato-role")]
    role: Option<&'static str>,
}

/// The metadata of a merge patch.
#[derive(Serialize)]
struct Metadata {
    /// The labels.
    labels: Labels,
}

/// A merge patch of a pod.
#[derive(Serialize)]
struct Patch {
    /// The metadata.
    metadata: Metadata,
}

/// A client of the API server that patches the labels of pods in the namespace of the node.
struct PodLabels {
    /// The HTTP client.
    agent: ureq::Agent,

    /// The URL of the pods of the namespace.
    pods_url: String,

    /// The bearer token of the service account.
    token: String,
}

impl PodLabels {
    /// Builds a client from the service account of the pod, if the node runs in Kubernetes.
    fn from_service_account() -> Option<Result<Self, String>> {
        let host = std::env::var(ENV_SERVICE_HOST).ok()?;
        let port = std::env::var(ENV_SERVICE_PORT).ok()?;
        Some(Self::build(&host, &port))
    }

    /// Builds the client.
    fn build(host: &str, port: &str) -> Result<Self, String> {
        let read =
            |name: &str| std::fs::read(format!("{SERVICE_ACCOUNT_DIR}/{name}")).map_err(|error| format!("service account {name}: {error}"));
        let token = String::from_utf8(read("token")?).map_err(|error| error.to_string())?;
        let namespace = String::from_utf8(read("namespace")?).map_err(|error| error.to_string())?;
        let ca_pem = read("ca.crt")?;
        let certificate = Certificate::from_pem(&ca_pem).map_err(|error| error.to_string())?;
        let agent = ureq::Agent::config_builder()
            .timeout_global(Some(REQUEST_TIMEOUT))
            .http_status_as_error(false)
            .tls_config(
                TlsConfig::builder()
                    .root_certs(RootCerts::new_with_certs(&[certificate]))
                    .unversioned_rustls_crypto_provider(Arc::new(rustls::crypto::ring::default_provider()))
                    .build(),
            )
            .build()
            .into();
        Ok(Self {
            agent,
            pods_url: format!("https://{host}:{port}/api/v1/namespaces/{}/pods", namespace.trim()),
            token: token.trim().to_owned(),
        })
    }

    /// Sets or removes the role label of a pod.
    fn set(&self, pod: &str, active: bool) -> Result<(), String> {
        let patch = Patch {
            metadata: Metadata {
                labels: Labels {
                    role: active.then_some(ROLE_LABEL_ACTIVE),
                },
            },
        };
        let body = wire::encode(&patch).map_err(|error| error.to_string())?;
        let url = format!("{}/{pod}", self.pods_url);
        let response = self
            .agent
            .patch(&url)
            .header("Authorization", &format!("Bearer {}", self.token))
            .header("Content-Type", "application/merge-patch+json")
            .send(&body[..])
            .map_err(|error| format!("PATCH {url}: {error}"))?;
        let status = response.status().as_u16();
        if (200..300).contains(&status) {
            Ok(())
        } else {
            Err(format!("PATCH {url}: status {status}"))
        }
    }
}

/// Keeps the label of the pod equal to whether the node serves traffic.
fn run(shared: &Shared, client: &PodLabels) {
    let own_pod = shared.config.node_name.clone();
    let mut labeled: Option<bool> = None;

    loop {
        let serving = {
            let mut state = shared.state.lock();
            let _ = shared.changed.wait_for(&mut state, CHECK_INTERVAL);
            if state.stopping {
                false
            } else {
                state.role.is_active() && !state.isolated
            }
        };
        if labeled == Some(serving) {
            continue;
        }

        let outcome = if serving {
            let peers = shared.referee.read_addresses().map_err(|error| error.to_string());
            peers.and_then(|addresses| {
                for address in addresses.iter().filter(|address| address.node_name != own_pod) {
                    client.set(&address.node_name, false)?;
                }
                client.set(&own_pod, true)
            })
        } else {
            client.set(&own_pod, false)
        };

        match outcome {
            Ok(()) => {
                tracing::info!("Pod {own_pod} labeled as serving: {serving}");
                labeled = Some(serving);
            }

            // The next check retries, and until then the label keeps its previous value.
            Err(error) => tracing::warn!("Cannot update the role label: {error}"),
        }
    }
}

/// Starts the label thread if the node runs in Kubernetes.
pub fn start(shared: &Arc<Shared>) -> Result<(), std::io::Error> {
    let Some(client) = PodLabels::from_service_account() else {
        return Ok(());
    };
    let client = client.map_err(std::io::Error::other)?;
    let shared = Arc::clone(shared);
    let _ = std::thread::Builder::new()
        .name("kubernetes-label".to_owned())
        .spawn(move || run(&shared, &client))?;
    Ok(())
}
