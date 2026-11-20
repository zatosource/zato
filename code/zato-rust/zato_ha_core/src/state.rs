// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The role of the node and the state shared by its threads.

use parking_lot::{Condvar, Mutex};
use serde::Serialize;

use crate::config::NodeConfig;
use crate::referee::Referee;

/// The role of the node.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum Role {
    /// The node has not read the referee record yet.
    Down,

    /// The node holds the lease of the record and runs the Zato server.
    Active,

    /// The node waits for the lease of the active node to lapse and may take over.
    Standby,

    /// The node was replaced and stops everything it runs.
    Fenced,
}

impl Role {
    /// Whether the Zato server runs in this role.
    pub const fn is_active(self) -> bool {
        matches!(self, Self::Active)
    }
}

/// Everything the threads of the node share under one mutex.
pub struct NodeState {
    /// The current role.
    pub role: Role,

    /// The highest generation this node acts on.
    pub generation: u64,

    /// Whether the active node lost the referee or the database, which stops the Zato server.
    pub isolated: bool,

    /// Whether the Zato server that the supervisor started last has answered its ping endpoint.
    pub server_ready: bool,

    /// Whether the node is shutting down.
    pub stopping: bool,
}

impl NodeState {
    /// Whether the node holds the role in which its Zato server runs.
    pub const fn serves(&self) -> bool {
        self.role.is_active() && !self.isolated
    }

    /// Whether the node serves and its Zato server answers, which is when clients are sent to it.
    pub const fn answers(&self) -> bool {
        self.serves() && self.server_ready
    }
}

/// The state and services every thread of the node uses.
pub struct Shared {
    /// The configuration.
    pub config: NodeConfig,

    /// The referee.
    pub referee: Box<dyn Referee>,

    /// The mutable state.
    pub state: Mutex<NodeState>,

    /// Notified on every change of the state that a waiting thread may act on.
    pub changed: Condvar,
}

impl Shared {
    /// Returns the shared state of a node that has not read the referee record yet.
    pub fn new(config: NodeConfig, referee: Box<dyn Referee>) -> Self {
        let state = NodeState {
            role: Role::Down,
            generation: 0,
            isolated: false,
            server_ready: false,
            stopping: false,
        };
        Self {
            config,
            referee,
            state: Mutex::new(state),
            changed: Condvar::new(),
        }
    }

    /// Tells every thread that the node is stopping.
    pub fn announce_stop(&self) {
        let mut state = self.state.lock();
        state.stopping = true;
        drop(state);
        self.changed.notify_all();
    }

    /// Moves the node to `Fenced` after the referee showed a higher generation.
    pub fn fence(&self, state: &mut NodeState, generation: u64) {
        tracing::warn!(
            "Replaced by generation {generation} while at generation {} in role {:?}, fencing",
            state.generation,
            state.role
        );
        state.generation = state.generation.max(generation);
        self.set_fenced(state);
    }

    /// Moves the node to `Fenced` at its own generation.
    pub fn set_fenced(&self, state: &mut NodeState) {
        state.role = Role::Fenced;
        state.isolated = false;
        self.changed.notify_all();
    }
}
