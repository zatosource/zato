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
//!
//! A stop of the node runs in this order. The node announces the stop, which makes the label thread remove the label
//! of the own pod and the supervisor stop the Zato server with SIGTERM, which drains it. An active node keeps renewing
//! its lease until the supervisor reports that no process of the server runs, so the other node does not take over
//! during the drain. It then writes the record as released, on the condition that the record still names it at its
//! generation, and exits, and the other node takes the released record over at its next heartbeat. A server that still
//! runs at the deadline leaves the record unreleased, so its lease lapses. A standby and a fenced node exit
//! without a write.

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::{Duration, Instant};

use crate::generation;
use crate::postgresql::DatabaseProbe;
use crate::record::{NodeEntry, RefereeRecord, Versioned};
use crate::referee::{Transition, transition};
use crate::state::{Role, Shared};
use crate::supervisor::STOP_GRACE;

mod lease;

/// How often the control loop evaluates the timers.
const TICK: Duration = Duration::from_millis(100);

/// How much longer than the stop grace of the Zato server an active node that stops waits for its server to exit
/// before it leaves the record unreleased.
///
/// The stop grace of 10 seconds, this margin and the read and the compare-and-set of the release, each within
/// the request timeout of 3 seconds under the default timers, 21 seconds in total, stay below
/// the `terminationGracePeriodSeconds` of the pod, 30 seconds, so the kubelet does not kill a node that is still
/// releasing its record.
const RELEASE_MARGIN: Duration = Duration::from_secs(5);

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

    /// How long an active node that stops waits for its Zato server to exit before it leaves the record unreleased.
    release_wait: Duration,
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
            release_wait: STOP_GRACE.saturating_add(RELEASE_MARGIN),
        })
    }

    /// Runs until a stop is requested or the referee is found to have lost data.
    pub fn run(mut self) -> Result<(), ControlError> {
        let outcome = self.bootstrap().and_then(|()| self.control_loop());
        if outcome.is_ok() {
            self.stop();
        } else {
            // A node that found the referee lost data writes nothing to it.
            self.shared.announce_stop();
        }
        outcome
    }

    /// Announces the stop to every thread and, on an active node, releases the record once its Zato server has exited.
    fn stop(&mut self) {
        // The role is read before the announcement, after which the supervisor stops the server of an active node.
        let is_active = self.shared.state.lock().role.is_active();
        self.shared.announce_stop();
        if is_active {
            self.release_on_stop();
        }
    }

    /// Keeps renewing the lease of an active node that stops until its Zato server has exited, and then releases
    /// the record, so the other node takes it over at its next heartbeat instead of after the takeover time.
    fn release_on_stop(&mut self) {
        if self.renew_until_server_exits() {
            self.release();
        }
    }

    /// Renews the lease at every heartbeat while a process of the Zato server runs, and returns whether the server
    /// exited before the release wait elapsed.
    fn renew_until_server_exits(&mut self) -> bool {
        let deadline = Instant::now() + self.release_wait;
        loop {
            // The role and the mark of the server are read under one lock, so the mark matches the role it was read with.
            let (role, is_running) = {
                let state = self.shared.state.lock();
                (state.role, state.server_running)
            };
            if !is_running {
                return true;
            }
            if Instant::now() >= deadline {
                tracing::error!(
                    "The Zato server still runs {} s after the stop began, the active role is not released",
                    self.release_wait.as_secs_f64()
                );
                return false;
            }

            // The renewals continue during the drain of the server, so the other node does not take over while
            // the server still runs, and a node that a renewal fenced renews no more.
            if role.is_active()
                && let Err(error) = self.check_lease(role)
            {
                tracing::error!("The active role is not released: {error}");
                return false;
            }

            // The supervisor notifies the end of the server, which ends the wait before the tick does.
            let mut state = self.shared.state.lock();
            if state.server_running {
                let _ = self.shared.changed.wait_for(&mut state, TICK);
            }
            drop(state);
        }
    }

    /// Writes the record as released on the condition that it still names this node at its generation, unreleased,
    /// so that a record that the other node took over during the drain stays as that node wrote it.
    fn release(&self) {
        let generation = self.shared.state.lock().generation;
        let held = RefereeRecord::new(generation, &self.shared.config.node_name);
        let released = held.released_by();
        match transition(self.shared.referee.as_ref(), &released, |current| current == Some(&held)) {
            Transition::Applied => tracing::info!("Released the active role at generation {generation}"),
            Transition::Refused(current) => {
                tracing::warn!("The active role is not released, the referee record is {current:?}");
            }
            Transition::Unreachable(error) => tracing::warn!("The active role is not released: {error}"),
        }
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
        // a takeover once its earlier lease lapsed, so the other node may take over first. A released record is taken
        // over at once, by this node or by the other one, at the first read of the lease.
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
    use crate::referee::Referee;
    use crate::referee::tests::MemoryReferee;
    use crate::test_support::{self, MemoryProbe, NODE_A, NODE_B};
    use tempfile::TempDir;

    /// Timers short enough for a test to let them expire.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_millis(10),
        takeover: Duration::from_millis(40),
    };

    /// The version of the record that a test starts with.
    const FIRST_VERSION: u64 = 1;

    /// The generation at which node A is active in the tests of its stop.
    const ACTIVE_GENERATION: u64 = 3;

    /// How long the Zato server of the tests of a stop drains, which spans several ticks of the control loop.
    const DRAIN: Duration = Duration::from_millis(500);

    /// The release wait of the test of a server that does not exit.
    const SHORT_RELEASE_WAIT: Duration = Duration::from_millis(50);

    /// Node A of a pair, with the files it needs for as long as it exists.
    struct TestNode {
        /// The control loop of the node.
        control: Control,

        /// The referee, which the test changes under the node.
        referee: Arc<MemoryReferee>,

        /// The directory of the node's files.
        _dir: TempDir,
    }

    /// Returns node A with `record` in the referee and `persisted` in its generation file.
    fn node(record: Option<RefereeRecord>, persisted: u64) -> TestNode {
        let referee = Arc::new(MemoryReferee::holding(record, FIRST_VERSION));
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_A, dir.path(), TIMERS);
        generation::write(&config.generation_file(), persisted).unwrap();

        let shared = test_support::shared(config, Box::new(Arc::clone(&referee)));
        let probe = Box::new(Arc::new(MemoryProbe::default()));
        let control = Control::new(shared, probe, Arc::new(AtomicBool::new(false))).unwrap();
        TestNode {
            control,
            referee,
            _dir: dir,
        }
    }

    /// Returns node A active at the active generation, with a running Zato server.
    fn active_node() -> TestNode {
        let node = node(Some(RefereeRecord::new(ACTIVE_GENERATION, NODE_A)), ACTIVE_GENERATION);
        set_role(&node.control, Role::Active, ACTIVE_GENERATION);
        node.control.shared.state.lock().server_running = true;
        node
    }

    /// Returns the number of the version of the record the referee holds.
    fn version_number(node: &TestNode) -> u64 {
        node.referee.read().unwrap().unwrap().version.parse().unwrap()
    }

    /// Ends the Zato server of a node after the drain, as the supervisor does once the process has exited,
    /// after `during_drain` has run while the server still runs.
    fn end_server_after_drain(shared: &Arc<Shared>, during_drain: impl FnOnce() + Send + 'static) -> thread::JoinHandle<()> {
        let shared = Arc::clone(shared);
        thread::spawn(move || {
            thread::sleep(DRAIN);
            during_drain();
            let mut state = shared.state.lock();
            state.server_running = false;
            drop(state);
            shared.changed.notify_all();
        })
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

    #[test]
    fn the_stop_of_an_active_node_renews_during_the_drain_and_releases_after_it() {
        let mut node = active_node();

        // While the server drains, the record stays unreleased and its lease is renewed ..
        let referee = Arc::clone(&node.referee);
        let draining = end_server_after_drain(&node.control.shared, move || {
            let current = referee.read().unwrap().unwrap();
            assert_eq!(current.value, RefereeRecord::new(ACTIVE_GENERATION, NODE_A));
            assert!(current.version.parse::<u64>().unwrap() > FIRST_VERSION);
        });
        node.control.stop();
        draining.join().unwrap();

        // .. and once the server has exited, the record is released at the generation of the node.
        assert!(node.control.shared.state.lock().stopping);
        assert_eq!(record(&node.control), RefereeRecord::new(ACTIVE_GENERATION, NODE_A).released_by());
    }

    #[test]
    fn a_server_that_runs_past_the_release_wait_leaves_the_record_unreleased() {
        let mut node = active_node();
        node.control.release_wait = SHORT_RELEASE_WAIT;
        node.control.stop();
        assert_eq!(record(&node.control), RefereeRecord::new(ACTIVE_GENERATION, NODE_A));
    }

    #[test]
    fn the_stop_of_a_standby_or_a_fenced_node_writes_nothing() {
        for role in [Role::Standby, Role::Fenced] {
            let mut node = node(Some(RefereeRecord::new(ACTIVE_GENERATION, NODE_B)), ACTIVE_GENERATION);
            set_role(&node.control, role, ACTIVE_GENERATION);
            node.control.stop();
            assert!(node.control.shared.state.lock().stopping);
            assert_eq!(record(&node.control), RefereeRecord::new(ACTIVE_GENERATION, NODE_B));
            assert_eq!(version_number(&node), FIRST_VERSION);
        }
    }

    #[test]
    fn a_record_that_the_other_node_took_over_during_the_drain_is_not_released() {
        let mut node = active_node();
        let taken_over = RefereeRecord::new(ACTIVE_GENERATION + 1, NODE_B);

        // The other node takes the record over while the server of this node drains ..
        let referee = Arc::clone(&node.referee);
        let written = taken_over.clone();
        let draining = end_server_after_drain(&node.control.shared, move || {
            let current = referee.read().unwrap().unwrap();
            assert!(referee.compare_and_set(&written, Some(&current.version)).unwrap());
        });
        node.control.stop();
        draining.join().unwrap();

        // .. so the record stays as the other node wrote it.
        assert_eq!(record(&node.control), taken_over);
    }
}
