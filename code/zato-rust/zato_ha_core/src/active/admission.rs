// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The admission of a joining standby that caught up with the log of the Zato database.

use std::io::Error;
use std::time::Instant;

use super::{Database, Session, Shipper};
use crate::protocol::Message;
use crate::record::RefereeRecord;
use crate::referee::{Transition, transition};
use crate::state::{LinkState, Role, Shared};

impl Shipper {
    /// Admits a joining standby once it confirmed the end of the log.
    pub(super) fn admit_if_caught_up(&mut self) -> Result<(), Error> {
        let Some(session) = self.session.as_ref().filter(|session| session.joining) else {
            self.resolve_abandoned_admission();
            return Ok(());
        };

        let Some(generation) = admission_generation(&self.shared, &self.database, session, &mut self.admission_started) else {
            return Ok(());
        };

        let node_name = self.shared.config.node_name.clone();
        let intended = RefereeRecord::replicated(generation + 1, &node_name, &session.peer);
        self.shared.state.lock().pending_admission = Some(intended.clone());

        let outcome = transition(self.shared.referee.as_ref(), &intended, |current| {
            current.is_some_and(|record| record.generation == generation && record.active_node == node_name)
        });

        match outcome {
            Transition::Applied => {
                // The standby takes the new generation before any frame of it arrives.
                let sent = session.sender.send(
                    &Message::Admit {
                        generation: generation + 1,
                    },
                    self.shared.config.timers.mark_out,
                );
                let mut state = self.shared.state.lock();
                state.generation = generation + 1;
                state.role = Role::ActiveReplicated;
                state.admitting = false;
                state.pending_admission = None;
                state.link_state = LinkState::Streaming;
                state.last_peer_contact = Instant::now();
                drop(state);
                self.shared.changed.notify_all();
                if let Some(session) = self.session.as_mut() {
                    session.joining = false;
                }
                tracing::info!("Standby admitted in sync at generation {}", generation + 1);
                sent
            }
            Transition::Refused(current) => {
                let higher = current.map_or(generation, |record| record.generation);
                self.shared.fence(&mut self.shared.state.lock(), higher);
                Ok(())
            }

            // The barriers stay held and the admission is attempted again on the next iteration.
            Transition::Unreachable(error) => {
                tracing::warn!("Admission not confirmed by the referee: {error}");
                Ok(())
            }
        }
    }

    /// Resolves an admission whose standby went away before the referee answered.
    pub(super) fn resolve_abandoned_admission(&self) {
        let pending = {
            let state = self.shared.state.lock();
            if !state.admitting {
                return;
            }
            state.pending_admission.clone()
        };
        let current = match self.shared.referee.read() {
            Ok(current) => current.map(|versioned| versioned.value),

            // An unknown outcome keeps the barriers held.
            Err(_) => return,
        };

        let mut state = self.shared.state.lock();
        if current.is_some() && current == pending {
            // The record names the standby in sync, and the mark-out of a standby that went away follows.
            if let Some(record) = current {
                state.generation = record.generation;
            }
            state.role = Role::ActiveReplicated;
            state.last_peer_contact = Instant::now();
        } else if let Some(record) = current {
            // The standby that the written admission named in sync may have taken over since, and a node active alone
            // completes barriers on its own disk, so it is fenced before any barrier completes under the newer record.
            let replaced = record.generation > state.generation && record.active_node != self.shared.config.node_name;
            if replaced {
                self.shared.fence(&mut state, record.generation);
            }
        }
        state.admitting = false;
        state.pending_admission = None;
        drop(state);
        self.shared.changed.notify_all();
    }
}

/// Returns the generation at which the joining standby of `session` is admitted, once it confirmed
/// the end of the log while the barriers were held.
///
/// Under steady writes, new frames are read before the standby confirms the previous ones, so the barriers
/// are held from the moment everything read was sent, which stops the writers until the standby confirms it.
fn admission_generation(shared: &Shared, database: &Database, session: &Session, admission_started: &mut Instant) -> Option<u64> {
    let mut state = shared.state.lock();
    if state.role != Role::ActiveSolo {
        return None;
    }

    if !state.admitting {
        // A standby whose wall clock is too far from that of this node would move the time of the database
        // by that skew once it took over, so it stays joining until its clock is corrected.
        if state.peer_clock_skew_ms > shared.config.max_clock_skew_ms {
            return None;
        }

        let all_sent = session.database.sent >= database.end();

        // From here on, no barrier completes until the standby is in sync or the admission is abandoned.
        // A barrier that completed before this point synced locally frames that the last scan may not
        // have read, so the admission waits for a later iteration, whose scan reads them.
        if all_sent {
            state.admitting = true;
            state.link_state = LinkState::CaughtUp;
            *admission_started = Instant::now();
        }
        return None;
    }

    let caught_up = state.database.confirmed >= state.database.scanned;
    if caught_up {
        return Some(state.generation);
    }

    // A standby that does not confirm in time releases the barriers and the admission begins again on a later iteration,
    // unless the referee may already hold the record of this admission.
    let mark_out = shared.config.timers.mark_out;
    if admission_started.elapsed() >= mark_out && state.pending_admission.is_none() {
        tracing::warn!("Admission postponed, the standby did not confirm within {mark_out:?}");
        state.admitting = false;
        state.link_state = LinkState::Joining;
        drop(state);
        shared.changed.notify_all();
    }
    None
}
