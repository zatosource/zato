// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The role of the node and the replication progress shared by its threads.

use std::time::Instant;

use parking_lot::{Condvar, Mutex};
use serde::Serialize;

use crate::config::{NodeConfig, ShippingMode};
use crate::link::{LinkSender, TlsContext};
use crate::record::RefereeRecord;
use crate::referee::Referee;

/// The role of the node.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum Role {
    /// The node has not read the referee record yet.
    Down,

    /// The node is active and every barrier waits for the standby.
    ActiveReplicated,

    /// The node is active without a standby in sync and every barrier waits for a local sync.
    ActiveSolo,

    /// The node holds every acknowledged frame and may take over.
    StandbyInSync,

    /// The node holds no usable copy and waits for the active node to send one.
    StandbyOut,

    /// The node is receiving a copy and the frames after it.
    Joining,

    /// The node was replaced and stops everything it runs.
    Fenced,
}

impl Role {
    /// Whether the Zato server runs in this role.
    pub const fn is_active(self) -> bool {
        matches!(self, Self::ActiveReplicated | Self::ActiveSolo)
    }

    /// Whether the node receives frames in this role.
    pub const fn is_standby(self) -> bool {
        matches!(self, Self::StandbyInSync | Self::StandbyOut | Self::Joining)
    }
}

/// A position in the log of a database, ordered by the cycle of the log and then by the frame.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Default, Serialize)]
pub struct LogPosition {
    /// The cycle of the log, raised on every restart of it.
    pub cycle: u64,

    /// The index after the last frame.
    pub frame: u32,
}

/// The salts of one cycle of a log and the position at which it ended.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CycleRecord {
    /// The cycle number.
    pub cycle: u64,

    /// The first salt.
    pub salt_one: u32,

    /// The second salt.
    pub salt_two: u32,

    /// The last end frame seen in this cycle.
    pub end_frame: u32,
}

/// The replication progress of one database on the active node.
#[derive(Debug, Clone)]
pub struct DatabaseProgress {
    /// The name of the database.
    pub name: &'static str,

    /// How its frames reach the standby.
    pub shipping: ShippingMode,

    /// The end of the log at the most recent completed scan.
    pub scanned: LogPosition,

    /// The end of what was sent to the standby.
    pub sent: LogPosition,

    /// The end of what the standby confirmed.
    pub confirmed: LogPosition,

    /// The current cycle and the one before it, which map the salts of a confirmation to a cycle.
    pub cycles: Vec<CycleRecord>,
}

/// How many cycles of each log are remembered for mapping confirmations.
const REMEMBERED_CYCLES: usize = 2;

impl DatabaseProgress {
    /// Returns the progress of a database nothing was read from.
    pub const fn new(name: &'static str, shipping: ShippingMode) -> Self {
        Self {
            name,
            shipping,
            scanned: LogPosition { cycle: 0, frame: 0 },
            sent: LogPosition { cycle: 0, frame: 0 },
            confirmed: LogPosition { cycle: 0, frame: 0 },
            cycles: Vec::new(),
        }
    }

    /// Records the salts and the end of the current cycle.
    pub fn record_cycle(&mut self, record: CycleRecord) {
        if let Some(existing) = self.cycles.iter_mut().find(|existing| existing.cycle == record.cycle) {
            *existing = record;
            return;
        }
        self.cycles.push(record);

        // Only the current cycle and the one before it can still be confirmed.
        while self.cycles.len() > REMEMBERED_CYCLES {
            let _ = self.cycles.remove(0);
        }
    }

    /// Returns the cycle that the salts of a confirmation belong to.
    pub fn cycle_of(&self, salt_one: u32, salt_two: u32) -> Option<&CycleRecord> {
        self.cycles
            .iter()
            .find(|record| record.salt_one == salt_one && record.salt_two == salt_two)
    }
}

/// The state of the replication link as seen by the active node.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum LinkState {
    /// No standby is connected.
    Disconnected,

    /// The standby is receiving a copy or the frames after it.
    Joining,

    /// The standby confirmed the end of every log and is being admitted.
    CaughtUp,

    /// The standby is in sync.
    Streaming,
}

/// Everything the threads of the node share under one mutex.
#[expect(
    clippy::struct_excessive_bools,
    reason = "each flag is an independent condition read by a different thread"
)]
pub struct NodeState {
    /// The current role.
    pub role: Role,

    /// The highest generation this node acts on.
    pub generation: u64,

    /// Whether barriers are held during an admission.
    pub admitting: bool,

    /// Whether the active node lost both the standby and the referee, which stops the Zato server.
    pub isolated: bool,

    /// Whether the standby could not resume and must be marked out before it joins again.
    pub needs_mark_out: bool,

    /// The progress of each replicated database, in the order of the configuration.
    pub databases: Vec<DatabaseProgress>,

    /// Raised by every barrier that needs a fresh scan.
    pub scan_requested: u64,

    /// The value of `scan_requested` at the start of the most recent completed scan.
    pub scan_completed: u64,

    /// When the other node was last heard from.
    pub last_peer_contact: Instant,

    /// When the oldest frame not yet confirmed was sent.
    pub oldest_unconfirmed: Option<Instant>,

    /// The state of the replication link on the active node.
    pub link_state: LinkState,

    /// The name of the node at the other end of the link.
    pub peer_name: Option<String>,

    /// The sending half of the link of the current session, on the active node or on the standby.
    pub link: Option<LinkSender>,

    /// Raised on every new session of the standby, which tells older sessions to end.
    pub session: u64,

    /// The record an admission in progress writes, which identifies it if its answer was lost.
    pub pending_admission: Option<RefereeRecord>,

    /// Whether the node is shutting down.
    pub stopping: bool,
}

impl NodeState {
    /// Returns the progress of the database with the given name.
    pub fn database_mut(&mut self, name: &str) -> Option<&mut DatabaseProgress> {
        self.databases.iter_mut().find(|database| database.name == name)
    }

    /// Whether the standby confirmed everything that was sent.
    pub fn all_confirmed(&self) -> bool {
        self.databases.iter().all(|database| database.confirmed >= database.sent)
    }

    /// Closes the link of the current session, if any.
    pub fn close_link(&mut self) {
        if let Some(link) = self.link.take() {
            link.close();
        }
        self.link_state = LinkState::Disconnected;
        self.peer_name = None;
        self.oldest_unconfirmed = None;
    }
}

/// The state and services every thread of the node uses.
pub struct Shared {
    /// The configuration.
    pub config: NodeConfig,

    /// The referee.
    pub referee: Box<dyn Referee>,

    /// The TLS configuration of the link.
    pub tls: TlsContext,

    /// The mutable state.
    pub state: Mutex<NodeState>,

    /// Notified on every change of the state that a waiting thread may act on.
    pub changed: Condvar,

    /// Held while the standby applies a batch and while it attempts a takeover, so that no frame of the
    /// old generation is applied once the takeover was written.
    pub apply_gate: Mutex<()>,
}

impl Shared {
    /// Returns the shared state of a node that has not read the referee record yet.
    pub fn new(config: NodeConfig, referee: Box<dyn Referee>, tls: TlsContext) -> Self {
        let databases = config
            .databases
            .iter()
            .map(|database| DatabaseProgress::new(database.name, database.shipping))
            .collect();
        let state = NodeState {
            role: Role::Down,
            generation: 0,
            admitting: false,
            isolated: false,
            needs_mark_out: false,
            databases,
            scan_requested: 0,
            scan_completed: 0,
            last_peer_contact: Instant::now(),
            oldest_unconfirmed: None,
            link_state: LinkState::Disconnected,
            peer_name: None,
            link: None,
            session: 0,
            pending_admission: None,
            stopping: false,
        };
        Self {
            config,
            referee,
            tls,
            state: Mutex::new(state),
            changed: Condvar::new(),
            apply_gate: Mutex::new(()),
        }
    }

    /// Tells every thread that the node is stopping and closes the replication link.
    pub fn announce_stop(&self) {
        let mut state = self.state.lock();
        state.stopping = true;
        state.close_link();
        drop(state);
        self.changed.notify_all();
    }

    /// Moves the node to `Fenced` after a peer or the referee showed a higher generation.
    pub fn fence(&self, state: &mut NodeState, generation: u64) {
        tracing::warn!(
            "Replaced by generation {generation} while at generation {} in role {:?}, fencing",
            state.generation,
            state.role
        );
        state.role = Role::Fenced;
        state.generation = state.generation.max(generation);
        state.admitting = false;
        state.isolated = false;
        state.close_link();
        self.changed.notify_all();
    }
}
