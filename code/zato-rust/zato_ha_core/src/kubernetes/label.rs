// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The `zato-role=active` label of the pod of the active node, which the Service selects.
//!
//! The moment the node becomes active, it removes the label from the pod of the other node, which may have lost
//! its connection to the API server while it was being replaced, so the Service no longer selects a pod whose server
//! has been replaced. The node labels its own pod only once its own Zato server answers, and removes the label
//! when the node stops serving or its server stops answering. The peer is always unlabeled before the node labels
//! its own pod, so the Service never selects two pods at once. A server whose health policy finds it failed is no longer
//! ready, so the label leaves the pod at once, before the node resigns and before the other node takes over.

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

/// Removes the role label from the pod of every other node that published an entry.
fn unlabel_peers(shared: &Shared, labels: &PodLabels, own_pod: &str) -> Result<(), String> {
    let entries = shared.referee.read_entries().map_err(|error| error.to_string())?;
    for entry in entries.iter().filter(|entry| entry.node_name != own_pod) {
        labels.set(&entry.node_name, false)?;
        tracing::info!("Pod {} unlabeled as the peer of an active node", entry.node_name);
    }
    Ok(())
}

/// Keeps the label of the pod equal to whether the node serves traffic and its Zato server answers,
/// until the node stops and its own label is removed.
fn run(shared: &Shared, labels: &PodLabels) {
    let own_pod = shared.config.node_name.clone();
    let mut labeled: Option<bool> = None;

    // Whether the peers were unlabeled since the node last became active.
    let mut peers_unlabeled = false;

    loop {
        let (serving, answers, stopping) = {
            let mut state = shared.state.lock();
            let _ = shared.changed.wait_for(&mut state, CHECK_INTERVAL);
            (
                state.serves() && !state.stopping,
                state.answers() && !state.stopping,
                state.stopping,
            )
        };

        // The node unlabels its peers once per term as the active node, at the start of the term ..
        if !serving {
            peers_unlabeled = false;
        } else if !peers_unlabeled {
            match unlabel_peers(shared, labels, &own_pod) {
                Ok(()) => peers_unlabeled = true,

                // .. and retries at the next check, while its own pod remains unlabeled.
                Err(error) => tracing::warn!("Cannot remove the role label of a peer: {error}"),
            }
        }

        let desired = answers && peers_unlabeled;
        if labeled != Some(desired) {
            match labels.set(&own_pod, desired) {
                Ok(()) => {
                    tracing::info!("Pod {own_pod} labeled as serving: {desired}");
                    labeled = Some(desired);
                }

                // The next check retries, and until then the label keeps its previous value.
                Err(error) => tracing::warn!("Cannot update the role label: {error}"),
            }
        }

        // A stopping node has nothing more to label once its own label is gone.
        if stopping && labeled == Some(false) {
            return;
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

#[cfg(test)]
mod tests;
