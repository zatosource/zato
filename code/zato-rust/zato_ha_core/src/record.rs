// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee record and the address records that the nodes publish next to it.

use serde::{Deserialize, Serialize};

/// The record that decides which node is active.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RefereeRecord {
    /// Raised by one on every change of the active node or of the standby's state.
    pub generation: u64,

    /// The node that may acknowledge anything.
    pub active_node: String,

    /// The node that receives the frames, if there is one.
    pub standby_node: Option<String>,

    /// Whether the standby holds every frame the active node acknowledged, which allows it to take over.
    pub standby_in_sync: bool,
}

impl RefereeRecord {
    /// Returns the record of a node that runs alone at a generation.
    pub fn solo(generation: u64, active_node: &str) -> Self {
        Self {
            generation,
            active_node: active_node.to_owned(),
            standby_node: None,
            standby_in_sync: false,
        }
    }

    /// Returns the record of a pair with the standby in sync.
    pub fn replicated(generation: u64, active_node: &str, standby_node: &str) -> Self {
        Self {
            generation,
            active_node: active_node.to_owned(),
            standby_node: Some(standby_node.to_owned()),
            standby_in_sync: true,
        }
    }

    /// Whether `node` is the standby in sync of this record.
    pub fn is_standby_in_sync(&self, node: &str) -> bool {
        self.standby_in_sync && self.standby_node.as_deref() == Some(node)
    }
}

/// The address a node publishes under its own key, from which the other node reaches it.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct NodeAddress {
    /// The name of the node, which is also the DNS name in its certificate.
    pub node_name: String,

    /// The host name or IP address of the replication link.
    pub host: String,

    /// The port of the replication link.
    pub port: u16,
}

/// A value read from the referee together with the version that a compare-and-set must name.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Versioned<T> {
    /// The value.
    pub value: T,

    /// The version of the value in the referee, which is opaque and is only compared for equality.
    pub version: String,
}
