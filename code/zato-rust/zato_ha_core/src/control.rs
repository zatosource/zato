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

use crate::generation;
use crate::record::{NodeAddress, RefereeRecord};
use crate::referee::{Transition, transition};
use crate::state::{Role, Shared};
use crate::wal;

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
}

impl Control {
    /// Returns the control loop of a node.
    pub fn new(shared: Arc<Shared>, stop_requested: Arc<AtomicBool>) -> Result<Self, ControlError> {
        let persisted_generation = generation::read(&shared.config.generation_file())?;
        Ok(Self {
            shared,
            stop_requested,
            persisted_generation,
            last_record_check: Instant::now(),
        })
    }

    /// Runs until a stop is requested or the referee is found to have lost data.
    pub fn run(mut self) -> Result<(), ControlError> {
        let outcome = self.bootstrap().and_then(|()| self.control_loop());
        let mut state = self.shared.state.lock();
        state.stopping = true;
        state.close_link();
        drop(state);
        self.shared.changed.notify_all();
        outcome
    }

    /// Whether a stop was requested.
    fn stop_requested(&self) -> bool {
        self.stop_requested.load(Ordering::Relaxed)
    }

    /// Publishes the address of the node and decides its first role from the referee record.
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

        // A node that was active alone holds every acknowledged frame on its own disk and resumes.
        if record.active_node == node_name && !record.standby_in_sync {
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
        let role = if record.is_standby_in_sync(&node_name) && record.generation == local {
            Role::StandbyInSync
        } else {
            Role::StandbyOut
        };

        let mut state = self.shared.state.lock();
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
            match role {
                Role::ActiveReplicated => self.check_standby()?,
                Role::StandbyInSync => self.check_active()?,
                Role::ActiveSolo => {
                    let mut state = self.shared.state.lock();
                    state.needs_mark_out = false;
                    state.isolated = false;
                }
                Role::Down | Role::StandbyOut | Role::Joining | Role::Fenced => {}
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
            let silent = state.last_peer_contact.elapsed() > mark_out_time;
            let lagging = state.oldest_unconfirmed.is_some_and(|since| since.elapsed() > mark_out_time);
            let due = silent || lagging || state.needs_mark_out;

            // A standby that answers again ends the isolation, since it confirms every acknowledgment.
            if !due && state.isolated {
                state.isolated = false;
                self.shared.changed.notify_all();
            }
            (state.generation, due)
        };
        if !due {
            return Ok(());
        }

        let node_name = self.shared.config.node_name.clone();
        let intended = RefereeRecord::solo(generation + 1, &node_name);
        let outcome = transition(self.shared.referee.as_ref(), &intended, |current| {
            current.is_some_and(|record| record.generation == generation && record.active_node == node_name)
        });

        match outcome {
            Transition::Applied => {
                // Acknowledgments that waited for the standby are now synced locally before any of them completes.
                self.sync_every_log();
                self.become_active_solo(generation + 1, "mark-out")
            }
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
