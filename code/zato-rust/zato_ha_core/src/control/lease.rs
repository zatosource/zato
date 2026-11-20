// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The lease of the active node, which the active node renews and the standby watches.
//!
//! The active node rewrites its record at every heartbeat interval in which its probe of the database succeeds,
//! which raises its version. The probe and each request to the API server may take half of the takeover time,
//! so a slow path of the active node to either of them delays its renewals without ending them, while
//! a late renewal is refused by the compare-and-set on the version once the standby took over. The standby measures on its own monotonic clock how long the version has not changed,
//! restarts the measure at every read that fails, and takes over after the takeover time if its own probe of the
//! database succeeds. A standby whose probe failed restarts the measure at its first probe that succeeds, so that
//! after an outage of the database that both nodes saw, the active node renews before the takeover time elapses again. The active node is never isolated by the lease, because the generation guard of the Zato
//! server refuses every transaction of a replaced server, so an outage of the referee alone does not stop it.
//! An active node that does not reach the referee is fenced once the database names a higher generation.
//!
//! An active node whose Zato server failed resigns, becomes the standby and stops renewing its lease, so that the other
//! node takes over after the takeover time. The node that resigned does not take over before its hold-off elapses,
//! which exceeds the takeover time, and which doubles with consecutive resignations up to its longest value.
//!
//! An active node that stops removes the label of its own pod, keeps renewing its lease while its Zato server drains,
//! and releases the record once the server has exited. A standby takes a released record over at the first read that
//! shows it, without the takeover time, once its hold-off has elapsed and its probe of the database succeeds.
//! The node that the released record names takes it over in the same way after it starts again, because its own
//! server is stopped, and the compare-and-set on the version admits one of the two nodes.

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

    /// Reads the record on the standby and takes over once its version has not changed for the takeover time,
    /// or at once if its active node released it, provided that the database is reachable from this node.
    fn watch_lease(&mut self) -> Result<(), ControlError> {
        self.lease_version = None;
        let node_name = self.shared.config.node_name.clone();

        // A failed read restarts the measure, so that after an outage of the referee that both nodes see,
        // the active node renews before the takeover time elapses again.
        let Ok(Some(current)) = self.shared.referee.read() else {
            self.observed_at = Instant::now();
            return Ok(());
        };

        // A takeover whose answer was lost wrote the record that names this node at a higher generation,
        // which a takeover never writes as released.
        let generation = self.shared.state.lock().generation;
        let is_own_takeover = current.value.active_node == node_name && current.value.generation > generation;
        if is_own_takeover && !current.value.released {
            tracing::info!(
                "Taking over at generation {}, written by an earlier attempt",
                current.value.generation
            );
            return self.become_active(current.value.generation, "takeover");
        }

        // A change of the record restarts the measure, which also ends the wait for the return of the database.
        let changed = self.observed.as_ref() != Some(&current);
        if changed {
            let mut state = self.shared.state.lock();
            state.generation = state.generation.max(current.value.generation);
            drop(state);
            self.observed = Some(current.clone());
            self.observed_at = Instant::now();
            self.database_lost = false;
        }

        // A lease that its active node renews is taken over only after the takeover time without a renewal,
        // while a released record has no server running under it and is taken over at the first read that shows it.
        let is_released = current.value.released;
        if !is_released {
            if changed {
                return Ok(());
            }
            if self.observed_at.elapsed() <= self.shared.config.timers.takeover {
                return Ok(());
            }
        }

        // A node that resigned leaves its lease to the other node for the hold-off, which exceeds the takeover time.
        let hold_off_until = self.shared.state.lock().hold_off_until;
        if hold_off_until.is_some_and(|until| Instant::now() < until) {
            return Ok(());
        }

        // A standby that does not reach the database would start a Zato server that cannot work, so it waits.
        if !self.database_reachable() {
            self.database_lost = true;
            return Ok(());
        }

        // The active node renews at its first probe that succeeds once the database returns, so the standby
        // measures the silence again from the return rather than from before the outage. A released record
        // has no server running under it and is taken over at once.
        let database_returned = std::mem::take(&mut self.database_lost);
        if database_returned && !is_released {
            self.observed_at = Instant::now();
            return Ok(());
        }

        let next = current.value.generation + 1;
        let intended = RefereeRecord::new(next, &node_name);
        match self.shared.referee.compare_and_set(&intended, Some(&current.version)) {
            Ok(true) => {
                if is_released {
                    tracing::info!(
                        "Taking over at generation {next} after the release by {}",
                        current.value.active_node
                    );
                } else {
                    tracing::info!("Taking over at generation {next} after the lease was not renewed");
                }
                self.become_active(next, "takeover")
            }

            // A renewal of the active node or a takeover by the other node in the meantime changed the version,
            // which the next read observes.
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
mod tests;
