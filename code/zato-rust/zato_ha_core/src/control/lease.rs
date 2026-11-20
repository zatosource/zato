// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The lease of the active node, which the active node renews and the standby watches.
//!
//! The active node rewrites its record at every heartbeat interval in which its probe of the database succeeds,
//! which raises its version. The standby measures on its own monotonic clock how long the version has not changed,
//! restarts the measure at every read that fails, and takes over after the takeover time if its own probe of the
//! database succeeds. The active node is never isolated by the lease, because the generation guard of the Zato
//! server refuses every transaction of a replaced server, so an outage of the referee alone does not stop it.

use std::time::Instant;

use super::{Control, ControlError};
use crate::postgresql::ProbeError;
use crate::record::RefereeRecord;
use crate::state::Role;

impl Control {
    /// Renews the lease of the active node or watches it on the standby, once per heartbeat interval.
    pub(super) fn check_lease(&mut self, role: Role) -> Result<(), ControlError> {
        if self.last_lease_check.elapsed() < self.shared.config.timers.heartbeat {
            return Ok(());
        }
        self.last_lease_check = Instant::now();

        match role {
            Role::Active => self.renew_lease(),
            Role::Standby => self.watch_lease(),

            // A node that is not active or a standby yet watches nothing, and its next role begins its measures afresh.
            Role::Down | Role::Fenced => {
                self.lease_version = None;
                self.observed = None;
                Ok(())
            }
        }
    }

    /// Returns whether the probe of the database succeeds, logging only a change of the outcome,
    /// and isolates the node while the database answers and is not durable.
    fn database_reachable(&mut self) -> bool {
        let outcome = self.probe.probe();
        let reachable = outcome.is_ok();

        // An isolated node stops its Zato server, so that no commit is acknowledged on a database that may lose it,
        // and the node serves again once the database is durable.
        let isolation_changed = match &outcome {
            Ok(()) => self.set_isolated(false),
            Err(ProbeError::NotDurable(_)) => self.set_isolated(true),

            // A database that does not answer tells nothing of its durability, so the last answer still applies.
            Err(ProbeError::Unreachable(_)) => false,
        };

        if reachable != self.database_reachable || isolation_changed {
            match outcome {
                Ok(()) => tracing::info!("The database is reachable and durable"),
                Err(ProbeError::NotDurable(reason)) => {
                    tracing::error!("The database is not durable, the Zato server stops: {reason}");
                }
                Err(error) => tracing::warn!("The database is not reachable: {error}"),
            }
        }
        self.database_reachable = reachable;
        reachable
    }

    /// Sets whether the node is isolated, waking the supervisor of the Zato server on a change,
    /// and returns whether it changed.
    fn set_isolated(&self, isolated: bool) -> bool {
        let mut state = self.shared.state.lock();
        let changed = state.isolated != isolated;
        state.isolated = isolated;
        drop(state);
        if changed {
            self.shared.changed.notify_all();
        }
        changed
    }

    /// Rewrites the record of the active node, which raises its version, on the condition that the version is the one
    /// this node last wrote and that the record still names it at its generation.
    fn renew_lease(&mut self) -> Result<(), ControlError> {
        self.observed = None;

        // A node that does not reach the database lets its lease lapse, so that a standby that reaches it takes over.
        if !self.database_reachable() {
            return Ok(());
        }

        let generation = self.shared.state.lock().generation;
        let record = RefereeRecord::new(generation, &self.shared.config.node_name);

        // A node that has just become active does not know the version of its record yet.
        let Some(version) = self.lease_version.clone() else {
            return self.adopt_lease(&record);
        };

        match self.shared.referee.renew(&record, &version) {
            Ok(Some(renewed)) => {
                self.lease_version = Some(renewed);
                Ok(())
            }

            // A renewal whose answer was lost raised the version too, which the record then tells apart from a takeover.
            Ok(None) => self.adopt_lease(&record),

            // The Zato server keeps running, and the next heartbeat renews again.
            Err(error) => {
                tracing::warn!("The lease was not renewed: {error}");
                Ok(())
            }
        }
    }

    /// Continues under the version of the record if it still names this node at its generation, and fences the node
    /// if it names another one.
    fn adopt_lease(&mut self, record: &RefereeRecord) -> Result<(), ControlError> {
        match self.shared.referee.read() {
            Ok(Some(current)) if current.value == *record => {
                self.lease_version = Some(current.version);
                Ok(())
            }
            Ok(Some(current)) => {
                self.lease_version = None;
                let higher = current.value.generation;
                self.shared.fence(&mut self.shared.state.lock(), higher);
                Ok(())
            }
            Ok(None) => Err(ControlError::RefereeLostData {
                referee: None,
                local: self.persisted_generation,
            }),

            // The next heartbeat reads the record again.
            Err(error) => {
                tracing::warn!("The lease was not read: {error}");
                Ok(())
            }
        }
    }

    /// Reads the record on the standby and takes over once its version has not changed for the takeover time
    /// and the database is reachable from this node.
    fn watch_lease(&mut self) -> Result<(), ControlError> {
        self.lease_version = None;
        let node_name = self.shared.config.node_name.clone();

        // A failed read restarts the measure, so that after an outage of the referee that both nodes see,
        // the active node renews before the takeover time elapses again.
        let Ok(Some(current)) = self.shared.referee.read() else {
            self.observed_at = Instant::now();
            return Ok(());
        };

        // A takeover whose answer was lost wrote the record that names this node at a higher generation.
        let generation = self.shared.state.lock().generation;
        if current.value.active_node == node_name && current.value.generation > generation {
            tracing::info!(
                "Taking over at generation {}, written by an earlier attempt",
                current.value.generation
            );
            return self.become_active(current.value.generation, "takeover");
        }

        let changed = self.observed.as_ref() != Some(&current);
        if changed {
            let mut state = self.shared.state.lock();
            state.generation = state.generation.max(current.value.generation);
            drop(state);
            self.observed = Some(current);
            self.observed_at = Instant::now();
            return Ok(());
        }
        if self.observed_at.elapsed() <= self.shared.config.timers.takeover {
            return Ok(());
        }

        // A standby that does not reach the database would start a Zato server that cannot work, so it waits.
        if !self.database_reachable() {
            return Ok(());
        }

        let next = current.value.generation + 1;
        let intended = RefereeRecord::new(next, &node_name);
        match self.shared.referee.compare_and_set(&intended, Some(&current.version)) {
            Ok(true) => {
                tracing::info!("Taking over at generation {next} after the lease was not renewed");
                self.become_active(next, "takeover")
            }

            // A renewal of the active node in the meantime changed the version, which the next read observes.
            Ok(false) => Ok(()),

            // The next read tells whether the takeover was written.
            Err(error) => {
                tracing::warn!("Takeover not confirmed by the referee: {error}");
                Ok(())
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::Timers;
    use crate::generation;
    use crate::record::Versioned;
    use crate::referee::tests::{MemoryReferee, version};
    use crate::test_support::{self, MemoryProbe, NODE_A, NODE_B};
    use std::sync::Arc;
    use std::sync::atomic::AtomicBool;
    use std::thread;
    use std::time::Duration;
    use tempfile::TempDir;

    /// Timers short enough for a test to let them expire.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_millis(10),
        takeover: Duration::from_millis(40),
    };

    /// How long a test waits for every timer to expire.
    const PAST_TIMERS: Duration = Duration::from_millis(60);

    /// The version of the record that a test starts with.
    const FIRST_VERSION: u64 = 1;

    /// The generation of the record that a test starts with.
    const FIRST_GENERATION: u64 = 3;

    /// Node A of a pair, with its files for as long as it exists.
    struct TestNode {
        /// The control loop of the node.
        control: Control,

        /// The referee, which the test changes under the node.
        referee: Arc<MemoryReferee>,

        /// The probe of the database, which the test makes fail or succeed.
        probe: Arc<MemoryProbe>,

        /// The directory of the node's files.
        _dir: TempDir,
    }

    impl TestNode {
        /// Returns node A with `record` in the referee and the generation of the record in its generation file.
        fn new(record: Option<RefereeRecord>) -> Self {
            let referee = Arc::new(MemoryReferee::holding(record, FIRST_VERSION));
            let probe = Arc::new(MemoryProbe::default());
            let dir = tempfile::tempdir().unwrap();
            let config = test_support::node_config(NODE_A, dir.path(), TIMERS);
            generation::write(&config.generation_file(), FIRST_GENERATION).unwrap();

            let shared = test_support::shared(config, Box::new(Arc::clone(&referee)));
            let control = Control::new(shared, Box::new(Arc::clone(&probe)), Arc::new(AtomicBool::new(false))).unwrap();
            Self {
                control,
                referee,
                probe,
                _dir: dir,
            }
        }

        /// Returns node A in `role` at the first generation, under a record that names `active_node`.
        fn in_role(role: Role, active_node: &str) -> Self {
            let out = Self::new(Some(RefereeRecord::new(FIRST_GENERATION, active_node)));
            let mut state = out.control.shared.state.lock();
            state.role = role;
            drop(state);
            out
        }

        /// Returns the role and the generation of the node.
        fn role(&self) -> (Role, u64) {
            let state = self.control.shared.state.lock();
            (state.role, state.generation)
        }

        /// Returns whether the node is isolated.
        fn is_isolated(&self) -> bool {
            self.control.shared.state.lock().isolated
        }

        /// Returns the record the referee holds.
        fn record(&self) -> Versioned<RefereeRecord> {
            self.referee.record.lock().clone().unwrap()
        }

        /// Replaces the record the referee holds, as the other node or a failover of the database does.
        fn replace_record(&self, value: RefereeRecord, number: u64) {
            *self.referee.record.lock() = Some(Versioned {
                value,
                version: version(number),
            });
            *self.referee.last_version.lock() = number;
        }

        /// Makes every operation of the referee fail or succeed.
        fn set_unreachable(&self, unreachable: bool) {
            *self.referee.unreachable.lock() = unreachable;
        }

        /// Makes every probe of the database fail or succeed.
        fn set_database_unreachable(&self, unreachable: bool) {
            *self.probe.unreachable.lock() = unreachable;
        }

        /// Makes every probe of the database find it not durable, or durable.
        fn set_database_not_durable(&self, not_durable: bool) {
            *self.probe.not_durable.lock() = not_durable;
        }
    }

    #[test]
    fn a_node_starts_as_the_standby_and_publishes_its_entry() {
        let mut node = TestNode::new(Some(RefereeRecord::new(FIRST_GENERATION, NODE_B)));
        node.control.bootstrap().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));

        // The node that takes over later finds the pod of this node among the entries.
        let entries = node.referee.entries.lock().clone();
        let names: Vec<&str> = entries.iter().map(|entry| entry.node_name.as_str()).collect();
        assert_eq!(names, [NODE_A]);
    }

    #[test]
    fn a_restarted_active_node_waits_for_the_takeover_as_the_standby_does() {
        let mut node = TestNode::new(Some(RefereeRecord::new(FIRST_GENERATION, NODE_A)));
        node.control.bootstrap().unwrap();

        // The node does not resume at once, so the standby that watched the lease takes over first ..
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
        assert_eq!(node.record().version, version(FIRST_VERSION));

        // .. and without a standby, the node takes over its own record once the takeover time elapses.
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.control.watch_lease().unwrap();

        let next = FIRST_GENERATION + 1;
        assert_eq!(node.role(), (Role::Active, next));
        assert_eq!(node.record().value, RefereeRecord::new(next, NODE_A));
    }

    #[test]
    fn the_active_node_renews_its_lease() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);

        // The first renewal of a node learns the version of its record ..
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION));

        // .. and every next one raises it.
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 2));
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));
    }

    #[test]
    fn an_active_node_without_the_database_does_not_renew_its_lease() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 1));

        // The version stays as it was, so the standby that reaches the database takes over ..
        node.set_database_unreachable(true);
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 1));
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));

        // .. unless the database is reachable again first.
        node.set_database_unreachable(false);
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 2));
    }

    #[test]
    fn an_active_node_on_a_database_that_is_not_durable_stops_serving() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        assert!(!node.is_isolated());

        // The node stops its Zato server at the first probe that finds the database not durable ..
        node.set_database_not_durable(true);
        node.control.renew_lease().unwrap();
        assert!(node.is_isolated());
        assert_eq!(node.record().version, version(FIRST_VERSION));

        // .. stays stopped while the database does not answer ..
        node.set_database_unreachable(true);
        node.control.renew_lease().unwrap();
        assert!(node.is_isolated());
        node.set_database_unreachable(false);

        // .. and serves again once the database is durable.
        node.set_database_not_durable(false);
        node.control.renew_lease().unwrap();
        assert!(!node.is_isolated());
        assert_eq!(node.record().version, version(FIRST_VERSION + 1));
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));
    }

    #[test]
    fn an_unreachable_database_does_not_isolate_the_active_node() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.set_database_unreachable(true);
        node.control.renew_lease().unwrap();
        assert!(!node.is_isolated());
    }

    #[test]
    fn a_standby_on_a_database_that_is_not_durable_does_not_take_over() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.set_database_not_durable(true);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
        assert_eq!(node.record().value, RefereeRecord::new(FIRST_GENERATION, NODE_B));
    }

    #[test]
    fn a_silent_active_node_is_taken_over() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.control.watch_lease().unwrap();

        let next = FIRST_GENERATION + 1;
        assert_eq!(node.role(), (Role::Active, next));
        assert_eq!(node.record().value, RefereeRecord::new(next, NODE_A));
    }

    #[test]
    fn a_standby_without_the_database_does_not_take_over() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.set_database_unreachable(true);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
        assert_eq!(node.record().value, RefereeRecord::new(FIRST_GENERATION, NODE_B));

        // The lease is still not renewed when the database is reachable again, so the standby takes over at once.
        node.set_database_unreachable(false);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION + 1));
    }

    #[test]
    fn a_renewed_lease_is_not_taken_over() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.replace_record(RefereeRecord::new(FIRST_GENERATION, NODE_B), FIRST_VERSION + 1);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
        assert_eq!(node.record().value, RefereeRecord::new(FIRST_GENERATION, NODE_B));
    }

    #[test]
    fn a_failed_read_restarts_the_measure_of_the_standby() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);

        // The referee returns after an outage that both nodes saw ..
        node.set_unreachable(true);
        node.control.watch_lease().unwrap();
        node.set_unreachable(false);

        // .. so the standby measures the silence of the active node again from the failed read.
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
    }

    #[test]
    fn a_takeover_whose_answer_was_lost_is_adopted() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);

        // The record names the node, which the node does not know yet ..
        *node.referee.lose_next_answer.lock() = true;
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));

        // .. until its next read.
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION + 1));
    }

    #[test]
    fn the_replaced_active_node_is_fenced() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        let next = FIRST_GENERATION + 1;
        node.replace_record(RefereeRecord::new(next, NODE_B), FIRST_VERSION + 1);
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Fenced, next));
    }

    #[test]
    fn a_record_created_again_by_the_other_node_fences_the_active_node() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        node.replace_record(RefereeRecord::new(FIRST_GENERATION, NODE_B), FIRST_VERSION);
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Fenced, FIRST_GENERATION));
        assert_eq!(node.record().version, version(FIRST_VERSION));
    }

    #[test]
    fn a_renewal_whose_answer_was_lost_is_adopted() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();

        // The version is raised, which the node does not know yet ..
        *node.referee.lose_next_answer.lock() = true;
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 1));

        // .. so its next renewal is refused, after which it continues under the version of its own record.
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 2));
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));
    }

    #[test]
    fn an_active_node_without_the_referee_keeps_serving() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        node.set_unreachable(true);
        thread::sleep(PAST_TIMERS);
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert!(!node.is_isolated());
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));

        node.set_unreachable(false);
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, version(FIRST_VERSION + 1));
    }

    #[test]
    fn a_referee_without_the_record_stops_the_active_node() {
        let mut node = TestNode::new(None);
        node.control.shared.state.lock().role = Role::Active;
        let error = node.control.renew_lease().unwrap_err();
        assert!(matches!(
            error,
            ControlError::RefereeLostData {
                referee: None,
                local: FIRST_GENERATION
            }
        ));
    }
}
