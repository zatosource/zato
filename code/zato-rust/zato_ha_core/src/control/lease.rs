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
//! An active node that does not reach the referee is fenced once the database names a higher generation.
//!
//! An active node whose Zato server failed resigns, becomes the standby and stops renewing its lease, so that the other
//! node takes over after the takeover time. The node that resigned does not take over before its hold-off elapses,
//! which exceeds the takeover time, and which doubles with consecutive resignations up to its longest value.

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

    /// Makes an active node whose Zato server failed the standby, so that its lease lapses and the other node takes over,
    /// and holds it off a takeover of its own for the hold-off. A failure found in any other role is discarded,
    /// because the server of such a node is stopped already.
    pub(super) fn resign_if_server_failed(&mut self) {
        let now = Instant::now();
        let health = self.shared.config.server_health;

        // The role and the failure are read and changed under one lock, so that no takeover comes between.
        let mut state = self.shared.state.lock();

        // A server that has been ready for the exit window ends the run of consecutive resignations.
        let is_settled = state.role.is_active()
            && state
                .server_ready_since
                .is_some_and(|since| now.saturating_duration_since(since) >= health.exit_window);
        if is_settled {
            self.hold_off = health.hold_off;
            self.last_resigned_at = None;
        }

        let Some(failure) = state.server_failure.take() else {
            return;
        };

        // Only the active node has a lease to give up.
        if !state.role.is_active() {
            drop(state);
            self.shared.changed.notify_all();
            return;
        }

        // A resignation soon after the previous one doubles the hold-off, so that a node whose server keeps failing
        // takes its lease over less and less often while it runs alone.
        let is_consecutive = self
            .last_resigned_at
            .is_some_and(|resigned_at| now.saturating_duration_since(resigned_at) <= health.hold_off_max);
        if is_consecutive {
            self.hold_off = self.hold_off.saturating_mul(2).min(health.hold_off_max);
        } else {
            self.hold_off = health.hold_off;
        }
        self.last_resigned_at = Some(now);

        let hold_off = self.hold_off;
        state.role = Role::Standby;
        state.hold_off_until = Some(now + hold_off);
        let generation = state.generation;
        drop(state);

        // The standby measures the lease afresh, and the version of the record is read again at the next activation.
        self.lease_version = None;
        self.observed = None;
        self.observed_at = now;
        self.shared.changed.notify_all();

        tracing::warn!(
            "Resigned the active role at generation {generation} because {failure}, no takeover for {} s",
            hold_off.as_secs_f64()
        );
    }

    /// Returns whether the probe of the database succeeds, logging only a change of the outcome,
    /// and isolates the node while the database answers and is not durable.
    fn database_reachable(&mut self) -> bool {
        let outcome = self.probe.probe();
        let reachable = outcome.is_ok();

        // A probe that failed tells nothing of the generation, which only the next probe that succeeds reads again.
        self.database_generation = outcome.as_ref().ok().copied().flatten();

        // An isolated node stops its Zato server, so that no commit is acknowledged on a database that may lose it,
        // and the node serves again once the database is durable.
        let isolation_changed = match &outcome {
            Ok(_) => self.set_isolated(false),
            Err(ProbeError::NotDurable(_)) => self.set_isolated(true),

            // A database that does not answer tells nothing of its durability, so the last answer still applies.
            Err(ProbeError::Unreachable(_)) => false,
        };

        if reachable != self.database_reachable || isolation_changed {
            match outcome {
                Ok(_) => tracing::info!("The database is reachable and durable"),
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

            // The Zato server keeps running unless the database shows a takeover, and the next heartbeat renews again.
            Err(error) => {
                tracing::warn!("The lease was not renewed: {error}");
                self.fence_if_taken_over();
                Ok(())
            }
        }
    }

    /// Fences the active node if the generation guard in the database names a generation above the node's own,
    /// which the Zato server of the node that took over set. The referee tells the node of the takeover too,
    /// but a node that does not reach the referee would otherwise keep reporting itself as active
    /// while the database refuses every transaction of its server.
    fn fence_if_taken_over(&self) {
        let Some(database_generation) = self.database_generation else {
            return;
        };
        // The role and the generation are compared and changed under one lock, so that no other change comes between.
        let mut state = self.shared.state.lock();
        let generation = state.generation;
        if database_generation <= generation {
            return;
        }
        tracing::warn!("The database names generation {database_generation}, above generation {generation} of this node, fencing");

        // The node keeps its own generation, because only the referee raises it, and a generation that a Zato server
        // without an active-standby node raised is not one that the referee holds.
        self.shared.set_fenced(&mut state);
        drop(state);
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

            // The next heartbeat reads the record again, unless the database shows a takeover.
            Err(error) => {
                tracing::warn!("The lease was not read: {error}");
                self.fence_if_taken_over();
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

        // A node that resigned leaves its lease to the other node for the hold-off, which exceeds the takeover time.
        let hold_off_until = self.shared.state.lock().hold_off_until;
        if hold_off_until.is_some_and(|until| Instant::now() < until) {
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
    use crate::config::{ServerHealthConfig, Timers};
    use crate::generation;
    use crate::record::Versioned;
    use crate::referee::tests::{MemoryReferee, version};
    use crate::server_health::ServerFailure;
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

    /// The health of the server of the tests, with a hold-off longer than the takeover time and a short exit window.
    const HEALTH: ServerHealthConfig = ServerHealthConfig {
        liveness_timeout: Duration::from_secs(10),
        start_timeout: Duration::from_mins(5),
        exit_limit: 3,
        exit_window: Duration::from_secs(1),
        hold_off: Duration::from_millis(150),
        hold_off_max: Duration::from_millis(600),
    };

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
            let mut config = test_support::node_config(NODE_A, dir.path(), TIMERS);
            config.server_health = HEALTH;
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

        /// Sets the generation that the generation guard in the database names.
        fn set_database_generation(&self, generation: Option<u64>) {
            *self.probe.generation.lock() = generation;
        }

        /// Records a failure of the Zato server, as the supervisor does.
        fn set_server_failure(&self, failure: ServerFailure) {
            self.control.shared.state.lock().server_failure = Some(failure);
        }

        /// Returns the failure of the Zato server on which the control loop has not acted yet.
        fn server_failure(&self) -> Option<ServerFailure> {
            self.control.shared.state.lock().server_failure
        }

        /// Returns until when the node does not take over.
        fn hold_off_until(&self) -> Option<Instant> {
            self.control.shared.state.lock().hold_off_until
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
    fn an_active_node_without_the_referee_is_fenced_once_the_database_names_a_higher_generation() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.set_database_generation(Some(FIRST_GENERATION));
        node.control.renew_lease().unwrap();
        node.set_unreachable(true);

        // The database names the generation of the node while the other node takes over ..
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));

        // .. and the server of the other node sets its own, which fences the node at its own generation.
        node.set_database_generation(Some(FIRST_GENERATION + 1));
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Fenced, FIRST_GENERATION));
    }

    #[test]
    fn a_higher_generation_in_the_database_does_not_fence_a_node_that_the_referee_names() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.set_database_generation(Some(FIRST_GENERATION + 1));
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        assert_eq!(node.role(), (Role::Active, FIRST_GENERATION));
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

    #[test]
    fn an_active_node_whose_server_failed_resigns_and_its_lease_lapses() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        node.control.renew_lease().unwrap();
        let renewed = node.record().version;

        // The failure makes the node the standby at its own generation, with the hold-off ahead of it ..
        node.set_server_failure(ServerFailure::Unanswered);
        let before = Instant::now();
        node.control.resign_if_server_failed();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
        assert_eq!(node.server_failure(), None);
        let hold_off_until = node.hold_off_until().unwrap();
        assert!(hold_off_until >= before + HEALTH.hold_off);

        // .. and the standby no longer renews, so the version stays and the other node finds the lease lapsed.
        node.control.watch_lease().unwrap();
        node.control.watch_lease().unwrap();
        assert_eq!(node.record().version, renewed);
        assert_eq!(node.record().value, RefereeRecord::new(FIRST_GENERATION, NODE_A));
    }

    #[test]
    fn the_other_node_takes_over_the_lease_of_a_node_that_resigned() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        node.set_server_failure(ServerFailure::Exits);
        node.control.resign_if_server_failed();

        // The other node takes over within the hold-off, and the node that resigned stays the standby
        // under the higher generation ..
        let next = FIRST_GENERATION + 1;
        node.control.watch_lease().unwrap();
        node.replace_record(RefereeRecord::new(next, NODE_B), FIRST_VERSION + 2);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, next));

        // .. and once the other node renews no more and the hold-off elapsed, the node that resigned takes over
        // as any standby does.
        thread::sleep(HEALTH.hold_off);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Active, next + 1));
        assert_eq!(node.record().value, RefereeRecord::new(next + 1, NODE_A));
    }

    #[test]
    fn a_lone_node_that_resigned_takes_over_only_after_its_hold_off() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.control.renew_lease().unwrap();
        node.set_server_failure(ServerFailure::Unanswered);
        node.control.resign_if_server_failed();

        // The takeover time elapses without a renewal, and the hold-off still keeps the node the standby ..
        node.control.watch_lease().unwrap();
        thread::sleep(PAST_TIMERS);
        node.control.watch_lease().unwrap();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));

        // .. until the hold-off elapses.
        let hold_off_until = node.hold_off_until().unwrap();
        thread::sleep(hold_off_until.saturating_duration_since(Instant::now()));
        node.control.watch_lease().unwrap();
        let next = FIRST_GENERATION + 1;
        assert_eq!(node.role(), (Role::Active, next));
        assert_eq!(node.record().value, RefereeRecord::new(next, NODE_A));
    }

    #[test]
    fn consecutive_resignations_double_the_hold_off_up_to_its_longest_value() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        let mut expected = Vec::new();
        let mut held_off = Vec::new();

        for _ in 0..4 {
            node.control.shared.state.lock().role = Role::Active;
            node.set_server_failure(ServerFailure::Exits);
            node.control.resign_if_server_failed();
            held_off.push(node.control.hold_off);
        }

        let mut hold_off = HEALTH.hold_off;
        for _ in 0..4 {
            expected.push(hold_off);
            hold_off = hold_off.saturating_mul(2).min(HEALTH.hold_off_max);
        }
        assert_eq!(held_off, expected);
        assert_eq!(held_off.last().copied(), Some(HEALTH.hold_off_max));
    }

    #[test]
    fn a_server_ready_for_the_exit_window_resets_the_hold_off() {
        let mut node = TestNode::in_role(Role::Active, NODE_A);
        node.set_server_failure(ServerFailure::Exits);
        node.control.resign_if_server_failed();
        node.control.shared.state.lock().role = Role::Active;
        node.set_server_failure(ServerFailure::Exits);
        node.control.resign_if_server_failed();
        assert_eq!(node.control.hold_off, HEALTH.hold_off.saturating_mul(2));

        // A server that has been ready for the exit window ends the run of resignations ..
        {
            let mut state = node.control.shared.state.lock();
            state.role = Role::Active;
            state.server_ready_since = Instant::now().checked_sub(HEALTH.exit_window);
        }
        node.control.resign_if_server_failed();
        assert_eq!(node.control.hold_off, HEALTH.hold_off);

        // .. so the next resignation holds off for the hold-off itself.
        node.set_server_failure(ServerFailure::Unanswered);
        node.control.resign_if_server_failed();
        assert_eq!(node.control.hold_off, HEALTH.hold_off);
    }

    #[test]
    fn a_failure_found_by_a_standby_is_discarded() {
        let mut node = TestNode::in_role(Role::Standby, NODE_B);
        node.set_server_failure(ServerFailure::Unanswered);
        node.control.resign_if_server_failed();
        assert_eq!(node.role(), (Role::Standby, FIRST_GENERATION));
        assert_eq!(node.server_failure(), None);
        assert_eq!(node.hold_off_until(), None);
    }
}
