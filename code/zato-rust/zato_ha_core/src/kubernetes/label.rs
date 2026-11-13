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

use super::client::{ApiClient, CONTENT_TYPE_MERGE_PATCH};
use crate::state::Shared;
use crate::wire;

/// The label the Service selects.
pub const ROLE_LABEL: &str = "zato-role";

/// The value of the label on the active pod.
pub const ROLE_LABEL_ACTIVE: &str = "active";

/// The API group and version of pods.
const PODS_GROUP_VERSION: &str = "api/v1";

/// The resource of pods.
const PODS_RESOURCE: &str = "pods";

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
    /// The client of the API server.
    client: ApiClient,

    /// The URL of the pods of the namespace.
    pods_url: String,
}

impl PodLabels {
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
        let response = self.client.patch(&url, CONTENT_TYPE_MERGE_PATCH, &body)?;
        if (200..300).contains(&response.status) {
            Ok(())
        } else {
            Err(format!("PATCH {url}: status {}", response.status))
        }
    }
}

/// Keeps the label of the pod equal to whether the node serves traffic.
fn run(shared: &Shared, labels: &PodLabels) {
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
                    labels.set(&address.node_name, false)?;
                }
                labels.set(&own_pod, true)
            })
        } else {
            labels.set(&own_pod, false)
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

/// Starts the label thread, which patches the pods through `client`.
pub fn start(shared: &Arc<Shared>, client: ApiClient) -> Result<(), std::io::Error> {
    let labels = PodLabels {
        pods_url: client.collection_url(PODS_GROUP_VERSION, PODS_RESOURCE),
        client,
    };
    let shared = Arc::clone(shared);
    let _ = std::thread::Builder::new()
        .name("kubernetes-label".to_owned())
        .spawn(move || run(&shared, &labels))?;
    Ok(())
}
