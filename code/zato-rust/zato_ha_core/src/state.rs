// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The role of the node and the replication progress shared by its threads.

use std::collections::VecDeque;
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

    /// The end of what the standby confirmed.
    pub confirmed: LogPosition,

    /// Each end of the log read while a standby was in sync that it has not confirmed yet and when it was read, the oldest first.
    pub unconfirmed: VecDeque<(LogPosition, Instant)>,

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
            confirmed: LogPosition { cycle: 0, frame: 0 },
            unconfirmed: VecDeque::new(),
            cycles: Vec::new(),
        }
    }

    /// Records that the log was read up to `end` at `read_at`, which the standby in sync owes a confirmation of.
    pub fn record_read(&mut self, end: LogPosition, read_at: Instant) {
        let newest = self.unconfirmed.back().map_or(self.confirmed, |(newest, _)| *newest);
        if end > newest {
            self.unconfirmed.push_back((end, read_at));
        }
    }

    /// Records that the standby holds the frames up to `confirmed`.
    pub fn record_confirmation(&mut self, confirmed: LogPosition) {
        self.confirmed = self.confirmed.max(confirmed);

        // A read that ends at or before the confirmed position is entirely in the standby.
        while self.unconfirmed.front().is_some_and(|(end, _)| *end <= self.confirmed) {
            let _ = self.unconfirmed.pop_front();
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

    /// When the oldest read of a synchronous database that the standby has not confirmed yet took place, if there is one.
    /// The copy of an asynchronous database may lag behind the active node.
    pub fn oldest_unconfirmed(&self) -> Option<Instant> {
        self.databases
            .iter()
            .filter(|database| database.shipping == ShippingMode::Synchronous)
            .filter_map(|database| database.unconfirmed.front().map(|(_, read_at)| *read_at))
            .min()
    }

    /// Closes the link of the current session, if any.
    ///
    /// The reads the standby in sync has not confirmed stay recorded, so that a standby which
    /// reconnects without ever confirming them is still marked out once they are older than the mark-out time.
    pub fn close_link(&mut self) {
        if let Some(link) = self.link.take() {
            link.close();
        }
        self.link_state = LinkState::Disconnected;
        self.peer_name = None;

        // Outside of `ActiveReplicated`, no standby is in sync, so nothing waits for these reads.
        if self.role != Role::ActiveReplicated {
            for database in &mut self.databases {
                database.unconfirmed.clear();
            }
        }
    }
}

/// The state and services every thread of the node uses.
pub struct Shared {
    /// The configuration.
    pub config: NodeConfig,

    /// The referee.
    pub referee: Box<dyn Referee>,

    /// The TLS configuration of the link, which the shared storage mode does not open.
    pub tls: Option<TlsContext>,

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
    pub fn new(config: NodeConfig, referee: Box<dyn Referee>, tls: Option<TlsContext>) -> Self {
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

    /// Returns the TLS configuration of the replication link.
    pub fn link_tls(&self) -> Result<&TlsContext, std::io::Error> {
        self.tls
            .as_ref()
            .ok_or_else(|| std::io::Error::other("the shared storage mode opens no replication link"))
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{DB_NAME_AUDIT, DB_NAME_PUBSUB, Timers};
    use crate::referee::tests::MemoryReferee;
    use crate::test_support::{self, Certificates, NODE_A};
    use std::time::Duration;

    /// The timers of a node whose loops do not run in a test.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_secs(1),
        mark_out: Duration::from_secs(3),
        takeover: Duration::from_secs(6),
    };

    /// How far apart the two reads of a test are.
    const READ_GAP: Duration = Duration::from_millis(100);

    /// Returns the position of `frame` in the first cycle of a log.
    const fn position(frame: u32) -> LogPosition {
        LogPosition { cycle: 1, frame }
    }

    #[test]
    fn a_confirmation_leaves_only_the_reads_after_it_unconfirmed() {
        let mut progress = DatabaseProgress::new("pubsub", ShippingMode::Synchronous);
        let first = Instant::now();
        let second = first + READ_GAP;

        progress.record_read(position(10), first);
        progress.record_read(position(20), second);
        progress.record_confirmation(position(10));

        let pending: Vec<Instant> = progress.unconfirmed.iter().map(|(_, read_at)| *read_at).collect();
        assert_eq!(pending, [second]);

        progress.record_confirmation(position(20));
        assert!(progress.unconfirmed.is_empty());
    }

    #[test]
    fn an_end_already_recorded_or_confirmed_is_not_a_new_read() {
        let mut progress = DatabaseProgress::new("pubsub", ShippingMode::Synchronous);
        let now = Instant::now();

        progress.record_read(position(10), now);
        progress.record_read(position(10), now + READ_GAP);
        assert_eq!(progress.unconfirmed.len(), 1);

        progress.record_confirmation(position(10));
        progress.record_read(position(10), now + READ_GAP);
        assert!(progress.unconfirmed.is_empty());
    }

    #[test]
    fn only_the_reads_of_synchronous_databases_make_a_standby_lag() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_A, dir.path(), &certificates, TIMERS);
        let shared = test_support::shared(config, Box::new(MemoryReferee::default()));
        let mut state = shared.state.lock();
        let audit_read_at = Instant::now();
        let pubsub_read_at = audit_read_at + READ_GAP;

        state.database_mut(DB_NAME_AUDIT).unwrap().record_read(position(10), audit_read_at);
        assert_eq!(state.oldest_unconfirmed(), None);

        state
            .database_mut(DB_NAME_PUBSUB)
            .unwrap()
            .record_read(position(10), pubsub_read_at);
        assert_eq!(state.oldest_unconfirmed(), Some(pubsub_read_at));
        drop(state);
    }

    #[test]
    fn a_session_that_ends_keeps_the_lag_of_a_standby_in_sync_until_it_is_marked_out() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_A, dir.path(), &certificates, TIMERS);
        let shared = test_support::shared(config, Box::new(MemoryReferee::default()));
        let mut state = shared.state.lock();
        let read_at = Instant::now();

        state.role = Role::ActiveReplicated;
        state.database_mut(DB_NAME_PUBSUB).unwrap().record_read(position(10), read_at);
        state.close_link();
        assert_eq!(state.oldest_unconfirmed(), Some(read_at));

        state.role = Role::ActiveSolo;
        state.close_link();
        assert_eq!(state.oldest_unconfirmed(), None);
        drop(state);
    }
}
