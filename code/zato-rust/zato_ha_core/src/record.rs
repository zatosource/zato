// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee record and the node entries that the nodes publish next to it.
//!
//! An active node that stops writes its record as released once its Zato server has exited, and the other node
//! takes a released record over at its next heartbeat instead of after the takeover time. A record that is not
//! released is encoded without the `released` field, exactly as a node without releases encodes it, and a record
//! without the field is read as not released.

use serde::{Deserialize, Serialize};

/// The record that decides which node is active.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RefereeRecord {

    /// Raised by one on every change of the active node.
    pub generation: u64,

    /// The node that runs the Zato server, or that ran it until it released the record.
    pub active_node: String,

    /// Whether the active node stopped its Zato server and gave the active role up.
    #[serde(default, skip_serializing_if = "is_unreleased")]
    pub released: bool,
}

impl RefereeRecord {
    /// Returns the record of a node that is active at a generation.
    pub fn new(generation: u64, active_node: &str) -> Self {
        Self {
            generation,
            active_node: active_node.to_owned(),
            released: false,
        }
    }

    /// Returns the copy of the record that its active node writes once its Zato server has exited.
    #[must_use]
    pub fn released_by(&self) -> Self {
        Self {
            released: true,
            ..self.clone()
        }
    }
}

/// Whether a record is not released, which leaves the `released` field out of its encoding.
#[expect(clippy::trivially_copy_pass_by_ref, reason = "serde passes the field to skip_serializing_if by reference")]
const fn is_unreleased(released: &bool) -> bool {
    !*released
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

#[cfg(test)]
mod tests;
