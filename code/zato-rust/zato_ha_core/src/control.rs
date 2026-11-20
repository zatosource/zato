// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The control loop of the node: bootstrap, the lease, takeover, isolation, the checks of the referee record
//! and the resignation of an active node whose Zato server failed.
//!
//! A resignation runs in this order. The supervisor records the failure of the server and clears its readiness
//! under one lock, which makes the label thread remove the label of the own pod, and stops the server. At its next
//! tick, the control loop makes the node the standby, which stops the renewals, so the lease lapses and the other node
//! takes over after the takeover time. The node that resigned takes no lease over before its hold-off elapses.

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::{Duration, Instant};

use crate::generation;
use crate::postgresql::DatabaseProbe;
use crate::record::{NodeEntry, RefereeRecord, Versioned};
use crate::referee::{Transition, transition};
use crate::state::{Role, Shared};

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

    /// When the lease was last renewed or watched.
    last_lease_check: Instant,

    /// The version of the record that the active node last renewed, or `None` until it reads it.
    lease_version: Option<String>,

    /// The probe of the database.
    probe: Box<dyn DatabaseProbe>,

    /// Whether the last probe of the database succeeded, so that only a change of it is logged.
    database_reachable: bool,

    /// The generation that the generation guard in the database named at the last probe, if the probe succeeded
    /// and a Zato server took the database over.
    database_generation: Option<u64>,

    /// The record that the standby last saw change.
    observed: Option<Versioned<RefereeRecord>>,

    /// When the standby last saw the record change or failed to read it.
    observed_at: Instant,

    /// The hold-off of the next resignation, which doubles with consecutive resignations up to the longest hold-off.
    hold_off: Duration,

    /// When the node last resigned, while consecutive resignations double the hold-off.
    last_resigned_at: Option<Instant>,
}

impl Control {
    /// Returns the control loop of a node with the probe of its database.
    pub fn new(shared: Arc<Shared>, probe: Box<dyn DatabaseProbe>, stop_requested: Arc<AtomicBool>) -> Result<Self, ControlError> {
        let persisted_generation = generation::read(&shared.config.generation_file())?;

        // The node acts on no generation below the one it persisted, even before it reads the record.
        let mut state = shared.state.lock();
        state.generation = persisted_generation;
        drop(state);

        let hold_off = shared.config.server_health.hold_off;

        Ok(Self {
            shared,
            stop_requested,
            persisted_generation,
            last_record_check: Instant::now(),
            last_lease_check: Instant::now(),
            lease_version: None,
            probe,
            database_reachable: true,
            database_generation: None,
            observed: None,
            observed_at: Instant::now(),
            hold_off,
            last_resigned_at: None,
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

    /// Publishes the entry of the node and decides its first role from the referee record.
    ///
    /// The node that becomes active removes the role label from the pod of each other published node
    /// before it labels its own pod.
    fn bootstrap(&mut self) -> Result<(), ControlError> {
        let entry = NodeEntry {
            node_name: self.shared.config.node_name.clone(),
        };
        while let Err(error) = self.shared.referee.publish_entry(&entry) {
            if self.stop_requested() {
                return Ok(());
            }
            tracing::warn!("Cannot publish the entry of this node: {error}");
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
                let intended = RefereeRecord::new(1, &node_name);
                match transition(self.shared.referee.as_ref(), &intended, |current| current.is_none()) {
                    Transition::Applied => {
                        self.become_active(1, "bootstrap")?;
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

        // A node that the record names as active also starts as the standby, and it becomes active again only through
        // a takeover once its earlier lease lapsed, so the other node may take over first.
        let role = Role::Standby;

        let mut state = self.shared.state.lock();
        state.generation = record.generation;
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

    /// Persists a generation and makes the node active.
    fn become_active(&mut self, generation: u64, reason: &str) -> Result<(), ControlError> {
        self.persist(generation)?;
        let mut state = self.shared.state.lock();
        state.generation = generation;
        state.role = Role::Active;
        state.isolated = false;
        drop(state);
        self.lease_version = None;
        self.shared.changed.notify_all();
        tracing::info!("Active at generation {generation} after {reason}");
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

            self.resign_if_server_failed();

            let role = self.shared.state.lock().role;
            self.check_lease(role)?;

            if self.last_record_check.elapsed() >= RECORD_CHECK_INTERVAL {
                self.last_record_check = Instant::now();
                self.check_record()?;
            }
        }
        Ok(())
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
        let replaced = state.role.is_active() && record.generation > state.generation && record.active_node != self.shared.config.node_name;
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
    use crate::test_support::{self, MemoryProbe, NODE_A, NODE_B};
    use tempfile::TempDir;

    /// Timers short enough for a test to let them expire.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_millis(10),
        takeover: Duration::from_millis(40),
    };

    /// Node A of a pair, with the files it needs for as long as it exists.
    struct TestNode {
        /// The control loop of the node.
        control: Control,

        /// The directory of the node's files.
        _dir: TempDir,
    }

    /// Returns node A with `record` in the referee and `persisted` in its generation file.
    fn node(record: Option<RefereeRecord>, persisted: u64) -> TestNode {
        let referee = MemoryReferee::holding(record, 1);
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_A, dir.path(), TIMERS);
        generation::write(&config.generation_file(), persisted).unwrap();

        let shared = test_support::shared(config, Box::new(referee));
        let probe = Box::new(Arc::new(MemoryProbe::default()));
        let control = Control::new(shared, probe, Arc::new(AtomicBool::new(false))).unwrap();
        TestNode { control, _dir: dir }
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
    fn the_first_node_creates_the_record_and_becomes_active() {
        let mut node = node(None, 0);
        node.control.bootstrap().unwrap();
        assert_eq!(role(&node.control), (Role::Active, 1));
        assert_eq!(record(&node.control), RefereeRecord::new(1, NODE_A));
        assert_eq!(generation::read(&node.control.shared.config.generation_file()).unwrap(), 1);
    }

    #[test]
    fn a_referee_below_the_local_generation_stops_the_node() {
        let mut node = node(Some(RefereeRecord::new(2, NODE_B)), 5);
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
        let mut node = node(None, 5);
        let error = node.control.bootstrap().unwrap_err();
        assert!(matches!(error, ControlError::RefereeLostData { referee: None, local: 5 }));
    }

    #[test]
    fn an_active_node_that_the_record_no_longer_names_is_fenced() {
        let node = node(Some(RefereeRecord::new(5, NODE_B)), 3);
        set_role(&node.control, Role::Active, 3);
        node.control.check_record().unwrap();
        assert_eq!(role(&node.control), (Role::Fenced, 5));
    }
}
