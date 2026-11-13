// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The lease of the shared storage mode, which the active node renews and the standby watches.
//!
//! The active node rewrites its record at every heartbeat interval, which raises its version, and is isolated once
//! no renewal was applied for the mark-out time. The standby measures on its own monotonic clock how long the version
//! has not changed, restarts the measure at every read that fails, and takes over after the takeover time.

use std::time::Instant;

use super::{Control, ControlError};
use crate::record::RefereeRecord;
use crate::referee::RefereeError;
use crate::state::Role;

impl Control {
    /// Renews the lease of the active node or watches it on the standby, once per heartbeat interval.
    pub(super) fn check_lease(&mut self, role: Role) -> Result<(), ControlError> {
        if self.last_lease_check.elapsed() < self.shared.config.timers.heartbeat {
            return Ok(());
        }
        self.last_lease_check = Instant::now();

        match role {
            Role::ActiveSolo => self.renew_lease(),
            Role::StandbyInSync => self.watch_lease(),

            // A node that is not active or a standby yet watches nothing, and its next role begins its measures afresh.
            Role::Down | Role::Fenced | Role::ActiveReplicated | Role::StandbyOut | Role::Joining => {
                self.lease_version = None;
                self.observed = None;
                Ok(())
            }
        }
    }

    /// Rewrites the record of the active node, which raises its version, on the condition that the version is the one
    /// this node last wrote and that the record still names it at its generation.
    fn renew_lease(&mut self) -> Result<(), ControlError> {
        self.observed = None;
        let generation = self.shared.state.lock().generation;
        let record = RefereeRecord::solo(generation, &self.shared.config.node_name);

        // A node that has just become active does not know the version of its record yet.
        let Some(version) = self.lease_version else {
            return self.adopt_lease(&record);
        };

        // The renewal counts from before it is sent, so that the isolation never begins later than the standby measures.
        let sent = Instant::now();
        match self.shared.referee.renew(&record, version) {
            Ok(Some(renewed)) => {
                self.lease_version = Some(renewed);
                self.last_renewal = sent;
                self.end_isolation();
                Ok(())
            }

            // A renewal whose answer was lost raised the version too, which the record then tells apart from a takeover.
            Ok(None) => self.adopt_lease(&record),
            Err(error) => {
                self.isolate_if_lapsed(&error);
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
            Err(error) => {
                self.isolate_if_lapsed(&error);
                Ok(())
            }
        }
    }

    /// Isolates the active node once its lease was not renewed for the mark-out time, which stops the Zato server
    /// before the standby may take over.
    fn isolate_if_lapsed(&self, error: &RefereeError) {
        let lapsed = self.last_renewal.elapsed();
        if lapsed <= self.shared.config.timers.mark_out {
            return;
        }
        let mut state = self.shared.state.lock();
        let newly_isolated = !state.isolated;
        state.isolated = true;
        drop(state);
        if newly_isolated {
            tracing::warn!("The lease was not renewed for {lapsed:?}, the Zato server stops: {error}");
            self.shared.changed.notify_all();
        }
    }

    /// Ends the isolation of an active node whose lease was renewed, which starts the Zato server again.
    fn end_isolation(&self) {
        let mut state = self.shared.state.lock();
        let was_isolated = state.isolated;
        state.isolated = false;
        drop(state);
        if was_isolated {
            tracing::info!("The lease was renewed, the Zato server starts again");
            self.shared.changed.notify_all();
        }
    }

    /// Reads the record on the standby and takes over once its version has not changed for the takeover time.
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
            self.become_active_solo(current.value.generation, "takeover")?;
            self.last_renewal = self.takeover_sent;
            return Ok(());
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

        let next = current.value.generation + 1;
        let intended = RefereeRecord::solo(next, &node_name);
        self.takeover_sent = Instant::now();
        match self.shared.referee.compare_and_set(&intended, current.version) {
            Ok(true) => {
                tracing::info!("Taking over at generation {next} after the lease was not renewed");
                self.become_active_solo(next, "takeover")?;
                self.last_renewal = self.takeover_sent;
                Ok(())
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
    use crate::record::{NodeAddress, Versioned};
    use crate::referee::Referee;
    use crate::referee::tests::MemoryReferee;
    use crate::test_support::{self, NODE_A, NODE_B};
    use std::sync::Arc;
    use std::sync::atomic::AtomicBool;
    use std::thread;
    use std::time::Duration;
    use tempfile::TempDir;

    /// Timers short enough for a test to let them expire.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_millis(10),
        mark_out: Duration::from_millis(20),
        takeover: Duration::from_millis(40),
    };

    /// How long a test waits for every timer to expire.
    const PAST_TIMERS: Duration = Duration::from_millis(60);

    /// The version of the record that a test starts with.
    const FIRST_VERSION: u64 = 1;

    /// The generation of the record that a test starts with.
    const FIRST_GENERATION: u64 = 3;

    impl Referee for Arc<MemoryReferee> {
        fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError> {
            self.as_ref().read()
        }

        fn compare_and_set(&self, record: &RefereeRecord, expected_version: u64) -> Result<bool, RefereeError> {
            self.as_ref().compare_and_set(record, expected_version)
        }

        fn renew(&self, record: &RefereeRecord, expected_version: u64) -> Result<Option<u64>, RefereeError> {
            self.as_ref().renew(record, expected_version)
        }

        fn publish_address(&self, address: &NodeAddress) -> Result<(), RefereeError> {
            self.as_ref().publish_address(address)
        }

        fn read_addresses(&self) -> Result<Vec<NodeAddress>, RefereeError> {
            self.as_ref().read_addresses()
        }
    }

    /// Node A of the shared storage mode, with its files for as long as it exists.
    struct TestNode {
        /// The control loop of the node.
        control: Control,

        /// The referee, which the test changes under the node.
        referee: Arc<MemoryReferee>,

        /// The directory of the node's files.
        _dir: TempDir,
    }

    impl TestNode {
        /// Returns node A with `record` in the referee and the generation of the record in its generation file.
        fn new(record: Option<RefereeRecord>) -> Self {
            let referee = Arc::new(MemoryReferee::default());
            *referee.record.lock() = record.map(|value| Versioned {
                value,
                version: FIRST_VERSION,
            });
            let dir = tempfile::tempdir().unwrap();
            let config = test_support::shared_storage_config(NODE_A, dir.path(), TIMERS);
            generation::write(&config.generation_file(), FIRST_GENERATION).unwrap();

            let shared = test_support::shared(config, Box::new(Arc::clone(&referee)));
            let control = Control::new(shared, Arc::new(AtomicBool::new(false))).unwrap();
            Self {
                control,
                referee,
                _dir: dir,
            }
        }

        /// Returns node A in `role` at the first generation, under a record that names `active_node`.
        fn in_role(role: Role, active_node: &str) -> Self {
            let out = Self::new(Some(RefereeRecord::solo(FIRST_GENERATION, active_node)));
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
        fn replace_record(&self, value: RefereeRecord, version: u64) {
            *self.referee.record.lock() = Some(Versioned { value, version });
        }

        /// Makes every operation of the referee fail or succeed.
        fn set_unreachable(&self, unreachable: bool) {
            *self.referee.unreachable.lock() = unreachable;
        }
    }

    #[test]
    fn a_node_starts_as_a_standby_in_sync_and_publishes_its_address() {
        let mut node = TestNode::new(Some(RefereeRecord::solo(FIRST_GENERATION, NODE_B)));
        node.control.bootstrap().unwrap();
        assert_eq!(node.role(), (Role::StandbyInSync, FIRST_GENERATION));

        // The node that takes over later finds the pod of this node among the addresses.
        let addresses = node.referee.addresses.lock().clone();
        let names: Vec<&str> = addresses.iter().map(|address| address.node_name.as_str()).collect();
        assert_eq!(names, [NODE_A]);
    }

    #[test]
    fn the_active_node_renews_its_lease() {
        let mut node = TestNode::in_role(Role::ActiveSolo, NODE_A);

        // The first renewal of a node learns the version of its record ..
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, FIRST_VERSION);

        // .. and every next one raises it.
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, FIRST_VERSION + 2);
        assert_eq!(node.role(), (Role::ActiveSolo, FIRST_GENERATION));
    }

    #[test]
    fn a_silent_active_node_is_taken_over() {
        let mut node = TestNode::in_role(Role::StandbyInSync, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.control.watch_lease().unwrap();

        let next = FIRST_GENERATION + 1;
        assert_eq!(node.role(), (Role::ActiveSolo, next));
        assert_eq!(node.record().value, RefereeRecord::solo(next, NODE_A));
    }

    #[test]
    fn a_renewed_lease_is_not_taken_over() {
        let mut node = TestNode::in_role(Role::StandbyInSync, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.replace_record(RefereeRecord::solo(FIRST_GENERATION, NODE_B), FIRST_VERSION + 1);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::StandbyInSync, FIRST_GENERATION));
        assert_eq!(node.record().value, RefereeRecord::solo(FIRST_GENERATION, NODE_B));
    }

    #[test]
    fn a_failed_read_restarts_the_measure_of_the_standby() {
        let mut node = TestNode::in_role(Role::StandbyInSync, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);

        // The referee returns after an outage that both nodes saw ..
        node.set_unreachable(true);
        node.control.watch_lease().unwrap();
        node.set_unreachable(false);

        // .. so the standby measures the silence of the active node again from the failed read.
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::StandbyInSync, FIRST_GENERATION));
    }

    #[test]
    fn a_takeover_whose_answer_was_lost_is_adopted() {
        let mut node = TestNode::in_role(Role::StandbyInSync, NODE_B);
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);

        // The record names the node, which the node does not know yet ..
        *node.referee.lose_next_answer.lock() = true;
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::StandbyInSync, FIRST_GENERATION));

        // .. until its next read.
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::ActiveSolo, FIRST_GENERATION + 1));
    }

    #[test]
    fn the_replaced_active_node_is_fenced() {
        let mut node = TestNode::in_role(Role::ActiveSolo, NODE_A);
        node.control.renew_lease().unwrap();
        let next = FIRST_GENERATION + 1;
        node.replace_record(RefereeRecord::solo(next, NODE_B), FIRST_VERSION + 1);
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Fenced, next));
    }

    #[test]
    fn a_record_created_again_by_the_other_node_fences_the_active_node() {
        let mut node = TestNode::in_role(Role::ActiveSolo, NODE_A);
        node.control.renew_lease().unwrap();
        node.replace_record(RefereeRecord::solo(FIRST_GENERATION, NODE_B), FIRST_VERSION);
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Fenced, FIRST_GENERATION));
        assert_eq!(node.record().version, FIRST_VERSION);
    }

    #[test]
    fn a_renewal_whose_answer_was_lost_is_adopted() {
        let mut node = TestNode::in_role(Role::ActiveSolo, NODE_A);
        node.control.renew_lease().unwrap();

        // The version is raised, which the node does not know yet ..
        *node.referee.lose_next_answer.lock() = true;
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, FIRST_VERSION + 1);

        // .. so its next renewal is refused, after which it continues under the version of its own record.
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.record().version, FIRST_VERSION + 2);
        assert_eq!(node.role(), (Role::ActiveSolo, FIRST_GENERATION));
    }

    #[test]
    fn an_active_node_without_the_referee_is_isolated_until_it_renews() {
        let mut node = TestNode::in_role(Role::ActiveSolo, NODE_A);
        node.control.renew_lease().unwrap();
        node.set_unreachable(true);
        thread::sleep(PAST_TIMERS);
        node.control.renew_lease().unwrap();
        assert!(node.is_isolated());

        node.set_unreachable(false);
        node.control.renew_lease().unwrap();
        assert!(!node.is_isolated());
        assert_eq!(node.role(), (Role::ActiveSolo, FIRST_GENERATION));
    }

    #[test]
    fn a_referee_without_the_record_stops_the_active_node() {
        let mut node = TestNode::new(None);
        node.control.shared.state.lock().role = Role::ActiveSolo;
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
