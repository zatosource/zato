// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The control loop of the node: bootstrap, takeover, mark-out, isolation and the checks of the referee record.

use std::fs::File;
use std::io::ErrorKind;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::{Duration, Instant};

use crate::config::StorageMode;
use crate::generation;
use crate::postgresql::DatabaseProbe;
use crate::record::{NodeAddress, RefereeRecord, Versioned};
use crate::referee::{Transition, transition};
use crate::state::{Role, Shared};
use crate::wal;

mod lease;

/// How often the control loop evaluates the timers.
const TICK: Duration = Duration::from_millis(100);

/// How often the referee record is read to detect a lost referee or a missed replacement.
const RECORD_CHECK_INTERVAL: Duration = Duration::from_secs(2);

/// How long the node waits between attempts to reach the referee at startup.
const STARTUP_RETRY_INTERVAL: Duration = Duration::from_secs(1);

/// Errors that stop the node.
#[derive(Debug)]
pub enum ControlError {
    /// The referee holds a lower generation than this node has seen, or no record at all.
    RefereeLostData {
        /// The generation in the referee, if there is a record.
        referee: Option<u64>,

        /// The highest generation this node has seen.
        local: u64,
    },

    /// A file of the node could not be read or written.
    File(std::io::Error),
}

impl std::fmt::Display for ControlError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::RefereeLostData {
                referee: Some(referee),
                local,
            } => write!(
                formatter,
                "The referee holds generation {referee}, below generation {local} seen by this node, so the referee lost data"
            ),
            Self::RefereeLostData { referee: None, local } => {
                write!(
                    formatter,
                    "The referee holds no record while this node has seen generation {local}, so the referee lost data"
                )
            }
            Self::File(error) => write!(formatter, "File error: {error}"),
        }
    }
}

impl std::error::Error for ControlError {}

impl From<std::io::Error> for ControlError {
    fn from(error: std::io::Error) -> Self {
        Self::File(error)
    }
}

/// The control loop.
pub struct Control {
    /// The shared state.
    shared: Arc<Shared>,

    /// Set by the signal handlers.
    stop_requested: Arc<AtomicBool>,

    /// The generation last written to the generation file.
    persisted_generation: u64,

    /// When the referee record was last read.
    last_record_check: Instant,

    /// When the lease was last renewed or watched, in the shared storage mode.
    last_lease_check: Instant,

    /// The version of the record that the active node last renewed, or `None` until it reads it, in the shared storage mode.
    lease_version: Option<String>,

    /// The probe of the database, which only the shared storage mode has.
    probe: Option<Box<dyn DatabaseProbe>>,

    /// Whether the last probe of the database succeeded, so that only a change of it is logged.
    database_reachable: bool,

    /// The record that the standby last saw change, in the shared storage mode.
    observed: Option<Versioned<RefereeRecord>>,

    /// When the standby last saw the record change or failed to read it, in the shared storage mode.
    observed_at: Instant,
}

impl Control {
    /// Returns the control loop of a node, with the probe of the database in the shared storage mode.
    pub fn new(shared: Arc<Shared>, probe: Option<Box<dyn DatabaseProbe>>, stop_requested: Arc<AtomicBool>) -> Result<Self, ControlError> {
        let persisted_generation = generation::read(&shared.config.generation_file())?;

        // Links of a generation below the persisted one are refused before the record is read, because the snapshot
        // of such a link would replace frames that this node acknowledged at the persisted generation.
        let mut state = shared.state.lock();
        state.generation = persisted_generation;
        drop(state);

        Ok(Self {
            shared,
            stop_requested,
            persisted_generation,
            last_record_check: Instant::now(),
            last_lease_check: Instant::now(),
            lease_version: None,
            probe,
            database_reachable: true,
            observed: None,
            observed_at: Instant::now(),
        })
    }

    /// Runs until a stop is requested or the referee is found to have lost data.
    pub fn run(mut self) -> Result<(), ControlError> {
        let outcome = self.bootstrap().and_then(|()| self.control_loop());
        self.shared.announce_stop();
        outcome
    }

    /// Whether a stop was requested.
    fn stop_requested(&self) -> bool {
        self.stop_requested.load(Ordering::Relaxed)
    }

    /// Publishes the address of the node and decides its first role from the referee record.
    ///
    /// The other node opens the replication link to the address, and in both storage modes the node that becomes
    /// active removes the role label from the pod of each other published node before it labels its own pod.
    fn bootstrap(&mut self) -> Result<(), ControlError> {
        let config = &self.shared.config;
        let address = NodeAddress {
            node_name: config.node_name.clone(),
            host: config.advertised_address.clone(),
            port: config.replication_port,
        };
        while let Err(error) = self.shared.referee.publish_address(&address) {
            if self.stop_requested() {
                return Ok(());
            }
            tracing::warn!("Cannot publish the address of this node: {error}");
            thread::sleep(STARTUP_RETRY_INTERVAL);
        }

        loop {
            if self.stop_requested() {
                return Ok(());
            }
            match self.decide_first_role()? {
                Some(()) => return Ok(()),
                None => thread::sleep(STARTUP_RETRY_INTERVAL),
            }
        }
    }

    /// Reads the record and sets the first role, returning `None` if the referee did not answer.
    fn decide_first_role(&mut self) -> Result<Option<()>, ControlError> {
        let node_name = self.shared.config.node_name.clone();
        let local = self.persisted_generation;

        let current = match self.shared.referee.read() {
            Ok(current) => current.map(|versioned| versioned.value),
            Err(error) => {
                tracing::warn!("Cannot read the referee record: {error}");
                return Ok(None);
            }
        };

        let record = match current {
            None if local > 0 => return Err(ControlError::RefereeLostData { referee: None, local }),

            // The first node to create the record becomes active, and the other one finds the record below.
            None => {
                let intended = RefereeRecord::solo(1, &node_name);
                match transition(self.shared.referee.as_ref(), &intended, |current| current.is_none()) {
                    Transition::Applied => {
                        self.become_active_solo(1, "bootstrap")?;
                        return Ok(Some(()));
                    }
                    Transition::Refused(Some(record)) => record,
                    Transition::Refused(None) | Transition::Unreachable(_) => return Ok(None),
                }
            }
            Some(record) => record,
        };

        if record.generation < local {
            return Err(ControlError::RefereeLostData {
                referee: Some(record.generation),
                local,
            });
        }

        // A node that was active alone holds every acknowledged frame on its own disk and resumes. In the shared
        // storage mode, the standby is always in sync, so the node waits for the takeover as one with a standby in sync.
        let is_shared = self.shared.config.storage == StorageMode::Shared;
        if record.active_node == node_name && !record.standby_in_sync && !is_shared {
            let intended = RefereeRecord::solo(record.generation + 1, &node_name);
            let expected = record.clone();
            return match transition(self.shared.referee.as_ref(), &intended, |current| current == Some(&expected)) {
                Transition::Applied => {
                    self.become_active_solo(record.generation + 1, "restart")?;
                    Ok(Some(()))
                }
                Transition::Refused(_) | Transition::Unreachable(_) => Ok(None),
            };
        }

        // A standby in sync that restarts still holds every frame it confirmed, since it confirms only synced frames.
        // An active node that had a standby in sync may lack frames it never synced, so it waits for the takeover.
        // A standby of the shared storage mode reads the one database, so it may always take over.
        let was_in_sync = record.is_standby_in_sync(&node_name) && record.generation == local;
        let role = if is_shared || was_in_sync {
            Role::StandbyInSync
        } else {
            Role::StandbyOut
        };

        let mut state = self.shared.state.lock();

        // The replication link accepts sessions before the record can be read, and a role that a session set is newer
        // than the record read above, since an admission is written to the referee before the standby learns of it.
        if state.role != Role::Down {
            tracing::info!(
                "Starting as {:?} at generation {}, set by the replication link",
                state.role,
                state.generation
            );
            return Ok(Some(()));
        }
        state.generation = record.generation;
        state.last_peer_contact = Instant::now();
        state.role = role;
        drop(state);
        self.shared.changed.notify_all();
        tracing::info!(
            "Starting as {role:?} at generation {}, active node {}",
            record.generation,
            record.active_node
        );
        Ok(Some(()))
    }

    /// Persists a generation and makes the node active without a standby.
    fn become_active_solo(&mut self, generation: u64, reason: &str) -> Result<(), ControlError> {
        self.persist(generation)?;
        let mut state = self.shared.state.lock();
        state.generation = generation;
        state.role = Role::ActiveSolo;
        state.isolated = false;
        state.needs_mark_out = false;
        state.close_link();
        drop(state);
        self.lease_version = None;
        self.shared.changed.notify_all();
        tracing::info!("Active alone at generation {generation} after {reason}");
        Ok(())
    }

    /// Writes a generation to the generation file if it is higher than the one written last.
    fn persist(&mut self, generation: u64) -> Result<(), ControlError> {
        if generation > self.persisted_generation {
            generation::write(&self.shared.config.generation_file(), generation)?;
            self.persisted_generation = generation;
        }
        Ok(())
    }

    /// Evaluates the timers at every tick.
    fn control_loop(&mut self) -> Result<(), ControlError> {
        while !self.stop_requested() {
            thread::sleep(TICK);

            let generation = self.shared.state.lock().generation;
            self.persist(generation)?;

            let role = self.shared.state.lock().role;
            match self.shared.config.storage {
                StorageMode::Replicated => match role {
                    Role::ActiveReplicated => self.check_standby()?,
                    Role::StandbyInSync => self.check_active()?,
                    Role::ActiveSolo => {
                        let mut state = self.shared.state.lock();
                        state.needs_mark_out = false;
                        state.isolated = false;
                    }
                    Role::Down | Role::StandbyOut | Role::Joining | Role::Fenced => {}
                },
                StorageMode::Shared => self.check_lease(role)?,
            }

            if self.last_record_check.elapsed() >= RECORD_CHECK_INTERVAL {
                self.last_record_check = Instant::now();
                self.check_record()?;
            }
        }
        Ok(())
    }

    /// Marks the standby out once it stops confirming, and isolates the node while the referee does not answer.
    fn check_standby(&mut self) -> Result<(), ControlError> {
        let mark_out_time = self.shared.config.timers.mark_out;
        let (generation, due) = {
            let mut state = self.shared.state.lock();
            let silence = state.last_peer_contact.elapsed();
            let lag = state.oldest_unconfirmed().map(|since| since.elapsed());
            let silent = silence > mark_out_time;
            let lagging = lag.is_some_and(|lag| lag > mark_out_time);
            let due = silent || lagging || state.needs_mark_out;

            if due && !state.isolated {
                tracing::warn!(
                    "Marking out the standby, silent for {silence:?}, oldest unconfirmed shipment {lag:?}, requested: {}",
                    state.needs_mark_out
                );
            }

            // The referee may name this node alone from the write on, even when its answer is lost, so the mark-out
            // stays due until the referee answers it, and no barrier completes on a confirmation of the standby until then.
            if due {
                state.needs_mark_out = true;
            }
            (state.generation, due)
        };
        if !due {
            return Ok(());
        }

        // Acknowledgments completed on confirmations of the standby alone are synced locally before the write, because
        // a write whose answer is lost names this node alone, and a restart under that record serves only the local logs.
        self.sync_every_log();

        let node_name = self.shared.config.node_name.clone();
        let intended = RefereeRecord::solo(generation + 1, &node_name);
        let outcome = transition(self.shared.referee.as_ref(), &intended, |current| {
            current.is_some_and(|record| record.generation == generation && record.active_node == node_name)
        });

        match outcome {
            Transition::Applied => self.become_active_solo(generation + 1, "mark-out"),
            Transition::Refused(current) => {
                let higher = current.map_or(generation, |record| record.generation);
                self.shared.fence(&mut self.shared.state.lock(), higher);
                Ok(())
            }
            Transition::Unreachable(error) => {
                let mut state = self.shared.state.lock();
                let newly_isolated = !state.isolated;
                state.isolated = true;
                drop(state);
                if newly_isolated {
                    tracing::warn!("Neither the standby nor the referee answers, the Zato server stops: {error}");
                    self.shared.changed.notify_all();
                }
                Ok(())
            }
        }
    }

    /// Syncs the log of every database to the local disk.
    fn sync_every_log(&self) {
        for database in &self.shared.config.databases {
            let path = wal::wal_path(&database.path);
            match File::open(&path).and_then(|file| file.sync_data()) {
                Ok(()) => {}
                Err(error) if error.kind() == ErrorKind::NotFound => {}
                Err(error) => tracing::error!("Cannot sync {}: {error}", path.display()),
            }
        }
    }

    /// Takes over once the active node has been silent for the takeover time.
    fn check_active(&mut self) -> Result<(), ControlError> {
        let takeover_time = self.shared.config.timers.takeover;
        let silent = self.shared.state.lock().last_peer_contact.elapsed() > takeover_time;
        if !silent {
            return Ok(());
        }

        let node_name = self.shared.config.node_name.clone();

        // No frame of the old generation is applied between the write and the change of the generation.
        let gate = self.shared.apply_gate.lock();
        let generation = self.shared.state.lock().generation;
        let intended = RefereeRecord::solo(generation + 1, &node_name);
        let outcome = transition(self.shared.referee.as_ref(), &intended, |current| {
            current.is_some_and(|record| record.generation == generation && record.is_standby_in_sync(&node_name))
        });

        match outcome {
            Transition::Applied => {
                {
                    let mut state = self.shared.state.lock();
                    state.generation = generation + 1;
                    state.close_link();
                    drop(state);
                }
                drop(gate);
                tracing::info!("Taking over from the silent active node at generation {}", generation + 1);
                self.become_active_solo(generation + 1, "takeover")
            }
            Transition::Refused(current) => {
                drop(gate);
                let mut state = self.shared.state.lock();
                if let Some(record) = current {
                    state.generation = state.generation.max(record.generation);
                }
                state.role = Role::StandbyOut;
                drop(state);
                self.shared.changed.notify_all();
                tracing::info!("Takeover refused by the referee, waiting to join again");
                Ok(())
            }

            // The takeover is attempted again at the next tick.
            Transition::Unreachable(error) => {
                tracing::warn!("Takeover not confirmed by the referee: {error}");
                Ok(())
            }
        }
    }

    /// Stops the node if the referee lost data and fences an active node that the record no longer names.
    fn check_record(&self) -> Result<(), ControlError> {
        let current = match self.shared.referee.read() {
            Ok(current) => current.map(|versioned| versioned.value),

            // A referee that does not answer changes nothing, and the timers decide what happens.
            Err(_) => return Ok(()),
        };
        let local = self.persisted_generation;
        let Some(record) = current else {
            return Err(ControlError::RefereeLostData { referee: None, local });
        };
        if record.generation < local {
            return Err(ControlError::RefereeLostData {
                referee: Some(record.generation),
                local,
            });
        }

        let mut state = self.shared.state.lock();
        let replaced = state.role.is_active()
            && !state.admitting
            && record.generation > state.generation
            && record.active_node != self.shared.config.node_name;
        if replaced {
            self.shared.fence(&mut state, record.generation);
        }
        drop(state);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::Timers;
    use crate::referee::tests::MemoryReferee;
    use crate::test_support::{self, Certificates, NODE_A, NODE_B};
    use tempfile::TempDir;

    /// Timers short enough for a test to let them expire.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_millis(10),
        mark_out: Duration::from_millis(20),
        takeover: Duration::from_millis(40),
    };

    /// How long a test waits for every timer to expire.
    const PAST_TIMERS: Duration = Duration::from_millis(60);

    /// Node A of a pair, with the files it needs for as long as it exists.
    struct TestNode {
        /// The control loop of the node.
        control: Control,

        /// The directory of the node's files.
        _dir: TempDir,

        /// The certificates of the pair.
        _certificates: Certificates,
    }

    /// Returns node A with `record` in the referee and `persisted` in its generation file.
    fn node(record: Option<RefereeRecord>, persisted: u64, unreachable: bool) -> TestNode {
        let referee = MemoryReferee::holding(record, 1);
        *referee.unreachable.lock() = unreachable;
        node_with_referee(referee, persisted)
    }

    /// Returns node A with `referee` and `persisted` in its generation file.
    fn node_with_referee(referee: MemoryReferee, persisted: u64) -> TestNode {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_A, dir.path(), &certificates, TIMERS);
        generation::write(&config.generation_file(), persisted).unwrap();

        let shared = test_support::shared(config, Box::new(referee));
        let control = Control::new(shared, None, Arc::new(AtomicBool::new(false))).unwrap();
        TestNode {
            control,
            _dir: dir,
            _certificates: certificates,
        }
    }

    /// Returns the record the referee holds.
    fn record(control: &Control) -> RefereeRecord {
        control.shared.referee.read().unwrap().unwrap().value
    }

    /// Returns the role and the generation of the node.
    fn role(control: &Control) -> (Role, u64) {
        let state = control.shared.state.lock();
        (state.role, state.generation)
    }

    /// Sets the role and the generation of the node, as after its first decision.
    fn set_role(control: &Control, role: Role, generation: u64) {
        let mut state = control.shared.state.lock();
        state.role = role;
        state.generation = generation;
    }

    #[test]
    fn the_first_node_creates_the_record_and_runs_alone() {
        let mut node = node(None, 0, false);
        node.control.bootstrap().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveSolo, 1));
        assert_eq!(record(&node.control), RefereeRecord::solo(1, NODE_A));
        assert_eq!(generation::read(&node.control.shared.config.generation_file()).unwrap(), 1);
    }

    #[test]
    fn a_node_that_was_active_alone_resumes_at_the_next_generation() {
        let mut node = node(Some(RefereeRecord::solo(3, NODE_A)), 3, false);
        node.control.bootstrap().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveSolo, 4));
        assert_eq!(record(&node.control), RefereeRecord::solo(4, NODE_A));
    }

    #[test]
    fn a_standby_in_sync_restarts_in_sync() {
        let mut node = node(Some(RefereeRecord::replicated(3, NODE_B, NODE_A)), 3, false);
        node.control.bootstrap().unwrap();
        assert_eq!(role(&node.control), (Role::StandbyInSync, 3));
    }

    #[test]
    fn a_standby_that_did_not_persist_its_admission_restarts_out() {
        let mut node = node(Some(RefereeRecord::replicated(3, NODE_B, NODE_A)), 2, false);
        node.control.bootstrap().unwrap();
        assert_eq!(role(&node.control), (Role::StandbyOut, 3));
    }

    #[test]
    fn a_standby_admitted_before_its_first_read_keeps_its_role() {
        let mut node = node(Some(RefereeRecord::replicated(4, NODE_B, NODE_A)), 3, false);

        // The replication link admitted the node while the referee could not be read ..
        set_role(&node.control, Role::StandbyInSync, 4);
        node.control.bootstrap().unwrap();

        // .. so the first read does not put it out of sync again.
        assert_eq!(role(&node.control), (Role::StandbyInSync, 4));
    }

    #[test]
    fn an_active_node_that_had_a_standby_in_sync_waits_for_the_takeover() {
        let mut node = node(Some(RefereeRecord::replicated(3, NODE_A, NODE_B)), 3, false);
        node.control.bootstrap().unwrap();
        assert_eq!(role(&node.control), (Role::StandbyOut, 3));
        assert_eq!(record(&node.control), RefereeRecord::replicated(3, NODE_A, NODE_B));
    }

    #[test]
    fn a_referee_below_the_local_generation_stops_the_node() {
        let mut node = node(Some(RefereeRecord::solo(2, NODE_B)), 5, false);
        let error = node.control.bootstrap().unwrap_err();
        assert!(matches!(
            error,
            ControlError::RefereeLostData {
                referee: Some(2),
                local: 5
            }
        ));
    }

    #[test]
    fn a_referee_without_the_record_stops_a_node_that_saw_a_generation() {
        let mut node = node(None, 5, false);
        let error = node.control.bootstrap().unwrap_err();
        assert!(matches!(error, ControlError::RefereeLostData { referee: None, local: 5 }));
    }

    #[test]
    fn a_silent_active_node_is_taken_over() {
        let mut node = node(Some(RefereeRecord::replicated(3, NODE_B, NODE_A)), 3, false);
        set_role(&node.control, Role::StandbyInSync, 3);
        thread::sleep(PAST_TIMERS);
        node.control.check_active().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveSolo, 4));
        assert_eq!(record(&node.control), RefereeRecord::solo(4, NODE_A));
    }

    #[test]
    fn a_takeover_refused_by_the_referee_leaves_the_standby_out() {
        let mut node = node(Some(RefereeRecord::solo(4, NODE_B)), 3, false);
        set_role(&node.control, Role::StandbyInSync, 3);
        thread::sleep(PAST_TIMERS);
        node.control.check_active().unwrap();
        assert_eq!(role(&node.control), (Role::StandbyOut, 4));
        assert_eq!(record(&node.control), RefereeRecord::solo(4, NODE_B));
    }

    #[test]
    fn a_silent_standby_is_marked_out() {
        let mut node = node(Some(RefereeRecord::replicated(3, NODE_A, NODE_B)), 3, false);
        set_role(&node.control, Role::ActiveReplicated, 3);
        thread::sleep(PAST_TIMERS);
        node.control.check_standby().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveSolo, 4));
        assert_eq!(record(&node.control), RefereeRecord::solo(4, NODE_A));
    }

    #[test]
    fn a_mark_out_refused_by_the_referee_fences_the_node() {
        let mut node = node(Some(RefereeRecord::solo(4, NODE_B)), 3, false);
        set_role(&node.control, Role::ActiveReplicated, 3);
        thread::sleep(PAST_TIMERS);
        node.control.check_standby().unwrap();
        assert_eq!(role(&node.control), (Role::Fenced, 4));
    }

    #[test]
    fn an_active_node_that_reaches_neither_the_standby_nor_the_referee_is_isolated() {
        let mut node = node(Some(RefereeRecord::replicated(3, NODE_A, NODE_B)), 3, true);
        set_role(&node.control, Role::ActiveReplicated, 3);
        thread::sleep(PAST_TIMERS);
        node.control.check_standby().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveReplicated, 3));
        assert!(node.control.shared.state.lock().isolated);
    }

    #[test]
    fn a_mark_out_whose_answer_was_lost_stays_due_until_the_referee_answers() {
        let referee = MemoryReferee::holding(Some(RefereeRecord::replicated(3, NODE_A, NODE_B)), 1);
        *referee.lose_next_answer.lock() = true;
        let mut node = node_with_referee(referee, 3);
        set_role(&node.control, Role::ActiveReplicated, 3);
        thread::sleep(PAST_TIMERS);

        // The record names the node alone, which the node does not know yet ..
        node.control.check_standby().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveReplicated, 3));
        assert_eq!(record(&node.control), RefereeRecord::solo(4, NODE_A));
        assert!(node.control.shared.state.lock().needs_mark_out);

        // .. so a standby that confirms again leaves the mark-out due, and the next attempt completes it.
        node.control.shared.state.lock().last_peer_contact = Instant::now();
        node.control.check_standby().unwrap();
        assert_eq!(role(&node.control), (Role::ActiveSolo, 4));
    }

    #[test]
    fn an_active_node_that_the_record_no_longer_names_is_fenced() {
        let node = node(Some(RefereeRecord::solo(5, NODE_B)), 3, false);
        set_role(&node.control, Role::ActiveSolo, 3);
        node.control.check_record().unwrap();
        assert_eq!(role(&node.control), (Role::Fenced, 5));
    }
}
