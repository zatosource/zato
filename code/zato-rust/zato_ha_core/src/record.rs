// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee record and the node entries that the nodes publish next to it.

use serde::{Deserialize, Serialize};

/// The record that decides which node is active.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RefereeRecord {
    /// Raised by one on every change of the active node.
    pub generation: u64,

    /// The node that runs the Zato server.
    pub active_node: String,
}

impl RefereeRecord {
    /// Returns the record of a node that is active at a generation.
    pub fn new(generation: u64, active_node: &str) -> Self {
        Self {
            generation,
            active_node: active_node.to_owned(),
        }
    }
}

/// The entry a node publishes under its own key, which names it to the other node.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct NodeEntry {
    /// The name of the node, which is also the name of its pod.
    pub node_name: String,
}

/// A value read from the referee together with the version that a compare-and-set must name.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Versioned<T> {
    /// The value.
    pub value: T,

    /// The version of the value in the referee, which is opaque and is only compared for equality.
    pub version: String,
}
