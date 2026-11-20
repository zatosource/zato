// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The checkpoints of the log of the Zato database, which the shipper alone runs.

use std::io::Error;
use std::time::Instant;

use super::Shipper;
use crate::state::{LinkState, Role};

impl Shipper {
    /// Checkpoints the log once it exceeds the size limit.
    pub(super) fn checkpoint_if_due(&mut self) -> Result<(), Error> {
        let (role, streaming) = {
            let state = self.shared.state.lock();
            (state.role, state.link_state == LinkState::Streaming)
        };

        // A joining standby depends on frames that a checkpoint would let the next writer overwrite,
        // and in sync, every frame must be confirmed first, which needs the link.
        let allowed = match role {
            Role::ActiveSolo => self.session.is_none(),
            Role::ActiveReplicated => streaming && self.session.is_some(),
            _ => false,
        };
        if !allowed {
            return Ok(());
        }

        // The standby confirms a log only once all of it was sent, which a long backlog takes several iterations for,
        // and a checkpoint would hold the write lock while it waited.
        let end = self.database.end();
        let has_backlog = self.session.as_ref().is_some_and(|session| session.database.sent < end);

        // A log whose every frame is in the database file already gains nothing from another checkpoint, which would
        // only take the write lock again before the next writer could restart the log.
        let is_checkpointed = self.database.checkpointed == end;
        if self.database.is_long() && !has_backlog && !is_checkpointed {
            self.checkpoint(role)?;
        }
        Ok(())
    }

    /// Checkpoints the log under its write lock, after the standby confirmed every frame of it.
    fn checkpoint(&mut self, role: Role) -> Result<(), Error> {
        {
            let Some(connections) = self.database.connections.as_ref() else {
                return Ok(());
            };

            // A writer holding the lock longer than the busy timeout only postpones the checkpoint.
            if connections.lock.execute_batch("begin immediate").is_err() {
                return Ok(());
            }
        }

        let outcome = self.checkpoint_under_lock(role);

        if let Some(connections) = self.database.connections.as_ref() {
            connections.lock.execute_batch("rollback").map_err(Error::other)?;
        }
        outcome
    }

    /// Ships and confirms every frame, then checkpoints, while the write lock is held.
    fn checkpoint_under_lock(&mut self, role: Role) -> Result<(), Error> {
        let ticket = self.shared.state.lock().scan_requested;
        self.scan_and_ship(ticket)?;

        let database = &self.database;

        // A log that restarted since the previous scan is short again, and checkpointing it would only restart it once more.
        if !database.is_long() {
            return Ok(());
        }
        let end = database.end();

        if role == Role::ActiveReplicated {
            let deadline = Instant::now() + self.shared.config.timers.mark_out;
            let mut state = self.shared.state.lock();
            loop {
                let confirmed = state.database.confirmed;
                if confirmed >= end {
                    break;
                }

                // A standby that does not confirm in time is marked out by the control loop, and the checkpoint waits.
                if state.role != Role::ActiveReplicated || Instant::now() >= deadline {
                    tracing::warn!("Checkpoint postponed, the standby confirmed {confirmed:?} of {end:?}");
                    return Ok(());
                }
                let _ = self.shared.changed.wait_until(&mut state, deadline);
            }
            drop(state);
        }

        let Some(connections) = database.connections.as_ref() else {
            return Ok(());
        };
        let (busy, log_frames, checkpointed): (i64, i64, i64) = connections
            .checkpoint
            .query_row("pragma wal_checkpoint(passive)", [], |row| {
                Ok((row.get(0)?, row.get(1)?, row.get(2)?))
            })
            .map_err(Error::other)?;
        tracing::debug!("Checkpoint: busy {busy}, log frames {log_frames}, checkpointed {checkpointed}");

        // A checkpoint that a reader held back leaves frames for the next one to copy.
        if checkpointed == log_frames {
            self.database.checkpointed = end;
        }
        Ok(())
    }
}
