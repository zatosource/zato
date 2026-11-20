// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the order of the label patches against a stub of the API server.

use super::*;
use crate::config::Timers;
use crate::record::NodeEntry;
use crate::referee::Referee;
use crate::referee::tests::MemoryReferee;
use crate::server_health::ServerFailure;
use crate::state::Role;
use crate::test_support::{HttpStub, LOOPBACK, NODE_A, NODE_B, node_config, shared, wait_until};
use std::collections::HashMap;
use std::thread;

/// The namespace of the pods of the tests.
const NAMESPACE: &str = "default";

/// The status of a patch that the API server applied.
const STATUS_OK: u16 = 200;

/// The method of a label patch.
const PATCH_METHOD: &str = "PATCH";

/// The body of a patch that sets the role label.
const LABEL_SET: &str = r#"{"metadata":{"labels":{"zato-role":"active"}}}"#;

/// The body of a patch that removes the role label.
const LABEL_REMOVED: &str = r#"{"metadata":{"labels":{"zato-role":null}}}"#;

/// How long a node whose server has not answered is watched to confirm that its own pod remains unlabeled.
const UNANSWERED_PERIOD: Duration = Duration::from_secs(1);

/// The timers of the node, which the label thread does not read.
const TIMERS: Timers = Timers {
    heartbeat: Duration::from_millis(500),
    takeover: Duration::from_secs(6),
};

/// The generation of the active node of the tests.
const GENERATION: u64 = 2;

/// A label patch that the stub received, as the pod and whether the patch set the label.
#[derive(Debug, Clone, PartialEq, Eq)]
struct LabelPatch {
    /// The name of the pod.
    pod: String,

    /// Whether the label was set rather than removed.
    active: bool,
}

/// Returns the label patches that the stub received, in their order.
fn patches(stub: &HttpStub) -> Vec<LabelPatch> {
    stub.requests()
        .iter()
        .filter_map(|request| {
            let mut parts = request.request_line.split_whitespace();
            let method = parts.next()?;
            let path = parts.next()?;
            if method != PATCH_METHOD {
                return None;
            }
            let pod = path.rsplit('/').next()?.to_owned();
            let active = match request.body.as_str() {
                LABEL_SET => true,
                LABEL_REMOVED => false,
                _ => return None,
            };
            Some(LabelPatch { pod, active })
        })
        .collect()
}

/// Returns the patch of `pod` that sets the label to `active`.
fn patch(pod: &str, active: bool) -> LabelPatch {
    LabelPatch {
        pod: pod.to_owned(),
        active,
    }
}

/// Returns whether the patches, applied in order after `labeled_pod` was labeled, ever leave two pods labeled at once.
fn labels_two_pods(labeled_pod: &str, patches: &[LabelPatch]) -> bool {
    let mut labeled: HashMap<&str, bool> = HashMap::from([(labeled_pod, true)]);
    patches.iter().any(|item| {
        let _ = labeled.insert(item.pod.as_str(), item.active);
        labeled.values().filter(|active| **active).count() > 1
    })
}

#[test]
fn the_peer_is_unlabeled_at_takeover_and_the_own_pod_only_once_the_server_answers() {
    let dir = tempfile::tempdir().unwrap();
    let stub = HttpStub::start(STATUS_OK);
    let referee = MemoryReferee::default();
    for node in [NODE_A, NODE_B] {
        referee
            .publish_entry(&NodeEntry {
                node_name: node.to_owned(),
            })
            .unwrap();
    }
    let shared = shared(node_config(NODE_A, dir.path(), TIMERS), Box::new(referee));
    let client = ApiClient::new(&format!("http://{LOOPBACK}:{}", stub.port), NAMESPACE, None, None).unwrap();
    let labels = PodLabels {
        pods_url: client.collection_url(PODS_GROUP_VERSION, PODS_RESOURCE),
        client,
    };
    let running = {
        let shared = Arc::clone(&shared);
        thread::spawn(move || run(&shared, &labels))
    };

    // A node that is not active removes its own label ..
    assert!(wait_until(|| patches(&stub) == [patch(NODE_A, false)]));

    // .. at takeover, it removes the label of the peer and leaves its own pod unlabeled while its server does not answer ..
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.generation = GENERATION;
    }
    shared.changed.notify_all();
    assert!(wait_until(|| patches(&stub).contains(&patch(NODE_B, false))));
    thread::sleep(UNANSWERED_PERIOD);
    assert!(!patches(&stub).contains(&patch(NODE_A, true)));

    // .. it labels its own pod once the server answers ..
    shared.state.lock().server_ready = true;
    shared.changed.notify_all();
    assert!(wait_until(|| patches(&stub).contains(&patch(NODE_A, true))));

    // .. and removes the label once the server no longer answers, after which the thread ends with the node.
    shared.state.lock().server_ready = false;
    shared.changed.notify_all();
    assert!(wait_until(|| patches(&stub).last() == Some(&patch(NODE_A, false))));
    shared.announce_stop();
    running.join().unwrap();

    let expected = [
        patch(NODE_A, false),
        patch(NODE_B, false),
        patch(NODE_A, true),
        patch(NODE_A, false),
    ];
    let received = patches(&stub);
    assert_eq!(received, expected);
    assert!(!labels_two_pods(NODE_B, &received));
}

#[test]
fn an_isolated_node_removes_its_label() {
    let dir = tempfile::tempdir().unwrap();
    let stub = HttpStub::start(STATUS_OK);
    let shared = shared(node_config(NODE_A, dir.path(), TIMERS), Box::new(MemoryReferee::default()));
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.generation = GENERATION;
        state.server_ready = true;
    }
    let client = ApiClient::new(&format!("http://{LOOPBACK}:{}", stub.port), NAMESPACE, None, None).unwrap();
    let labels = PodLabels {
        pods_url: client.collection_url(PODS_GROUP_VERSION, PODS_RESOURCE),
        client,
    };
    let running = {
        let shared = Arc::clone(&shared);
        thread::spawn(move || run(&shared, &labels))
    };

    // An active node whose server answers labels its pod ..
    assert!(wait_until(|| patches(&stub) == [patch(NODE_A, true)]));

    // .. and removes the label once it is isolated, even though its server still answered last.
    shared.state.lock().isolated = true;
    shared.changed.notify_all();
    assert!(wait_until(|| patches(&stub) == [patch(NODE_A, true), patch(NODE_A, false)]));

    shared.announce_stop();
    running.join().unwrap();
}

#[test]
fn a_node_whose_server_failed_removes_its_label_before_it_resigns() {
    let dir = tempfile::tempdir().unwrap();
    let stub = HttpStub::start(STATUS_OK);
    let shared = shared(node_config(NODE_A, dir.path(), TIMERS), Box::new(MemoryReferee::default()));
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.generation = GENERATION;
        state.server_ready = true;
    }
    let client = ApiClient::new(&format!("http://{LOOPBACK}:{}", stub.port), NAMESPACE, None, None).unwrap();
    let labels = PodLabels {
        pods_url: client.collection_url(PODS_GROUP_VERSION, PODS_RESOURCE),
        client,
    };
    let running = {
        let shared = Arc::clone(&shared);
        thread::spawn(move || run(&shared, &labels))
    };
    assert!(wait_until(|| patches(&stub) == [patch(NODE_A, true)]));

    // The supervisor records the failure and ends the readiness under one lock, while the node is still active ..
    {
        let mut state = shared.state.lock();
        state.server_failure = Some(ServerFailure::Unanswered);
        state.server_ready = false;
    }
    shared.changed.notify_all();
    assert!(wait_until(|| patches(&stub) == [patch(NODE_A, true), patch(NODE_A, false)]));

    // .. and the resignation that follows leaves the pod unlabeled.
    {
        let mut state = shared.state.lock();
        state.server_failure = None;
        state.role = Role::Standby;
    }
    shared.changed.notify_all();
    thread::sleep(UNANSWERED_PERIOD);
    assert!(!patches(&stub).iter().skip(1).any(|item| item.active));

    shared.announce_stop();
    running.join().unwrap();
}
