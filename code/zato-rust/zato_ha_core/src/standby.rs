// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The accepting end of the replication link, which applies the frames and snapshots of the active node.
//!
//! The listener runs in every role. A node that is active answers a link opened by a node of a lower
//! generation with [`Message::Refused`], which fences that node, and a node that receives a link of a
//! higher generation was replaced and is fenced itself.

use std::io::{Error, ErrorKind};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::time::Instant;

use crate::config::DatabaseConfig;
use crate::copy::DatabaseCopy;
use crate::link::{AcceptedLink, LinkReceiver, LinkSender, verify_peer_name};
use crate::protocol::{Message, Position};
use crate::state::{Role, Shared};

/// The databases of the copy of one session, in the order of the configuration.
struct Copies {
    /// The copy of each database.
    databases: Vec<DatabaseCopy>,
}

impl Copies {
    /// Opens the copies of the databases written by `active_node`.
    fn open(configs: &[DatabaseConfig], active_node: &str) -> Result<Self, Error> {
        let mut databases = Vec::new();
        for config in configs {
            databases.push(DatabaseCopy::open(config.name, &config.copy_path(active_node))?);
        }
        Ok(Self { databases })
    }

    /// Returns the copy of a database.
    fn get(&mut self, name: &str) -> Result<&mut DatabaseCopy, Error> {
        self.databases
            .iter_mut()
            .find(|copy| copy.name == name)
            .ok_or_else(|| Error::new(ErrorKind::InvalidData, format!("unknown database `{name}`")))
    }

    /// Returns the positions of every copy.
    fn positions(&self) -> Vec<Position> {
        self.databases.iter().map(DatabaseCopy::position).collect()
    }
}

/// Answers a link opened by a node of a lower generation, which fences that node.
fn refuse(sender: &LinkSender, generation: u64, shared: &Shared) {
    let _ = sender.send(&Message::Refused { generation }, shared.config.timers.mark_out);
    sender.close();
}

/// Decides how a session opened by `active_node` at `generation` begins, returning whether the standby resumes in sync.
fn open_session(shared: &Shared, sender: &LinkSender, generation: u64) -> Option<(u64, bool)> {
    let mut state = shared.state.lock();

    if generation < state.generation {
        let own = state.generation;
        drop(state);
        tracing::info!("Refusing a link of generation {generation} below the generation {own} of this node");
        refuse(sender, own, shared);
        return None;
    }

    // An equal generation on an active node is the node's own record, which another node cannot hold.
    if state.role.is_active() && generation == state.generation {
        let own = state.generation;
        drop(state);
        refuse(sender, own, shared);
        return None;
    }

    // A link of a higher generation means the other node took over, so an active node here was replaced.
    if state.role.is_active() {
        shared.fence(&mut state, generation);
    }

    // The previous session, if any, ends, and this one becomes the current one.
    state.close_link();
    state.session += 1;
    let session = state.session;
    state.link = Some(sender.clone());
    state.last_peer_contact = Instant::now();

    let resumes = state.role == Role::StandbyInSync && generation == state.generation;
    if !resumes && state.role != Role::Fenced {
        state.role = Role::StandbyOut;
    }
    state.generation = state.generation.max(generation);
    drop(state);
    shared.changed.notify_all();
    Some((session, resumes))
}

/// Whether a session is still the current one.
fn is_current(shared: &Shared, session: u64) -> bool {
    let state = shared.state.lock();
    state.session == session && !state.stopping
}

/// Applies the messages of one session until it ends.
fn run_session(shared: &Shared, sender: &LinkSender, receiver: &mut LinkReceiver, active_node: &str, generation: u64) -> Result<(), Error> {
    let Some((session, resumes)) = open_session(shared, sender, generation) else {
        return Ok(());
    };
    let timeout = shared.config.timers.mark_out;

    let mut copies = Copies::open(&shared.config.databases, active_node)?;
    let positions = if resumes { copies.positions() } else { Vec::new() };
    sender.send(
        &Message::HelloReply {
            in_sync: resumes,
            positions,
        },
        timeout,
    )?;
    tracing::info!("Session with {active_node} at generation {generation} opened, resuming in sync: {resumes}");

    loop {
        let message = receiver.receive()?;
        if !is_current(shared, session) {
            return Ok(());
        }

        // Every message from the active node shows it is alive.
        shared.state.lock().last_peer_contact = Instant::now();

        match message {
            Message::Frames {
                generation: frames_generation,
                database,
                header,
                first_frame,
                end_frame,
                bytes,
            } => {
                let gate = shared.apply_gate.lock();
                let own = shared.state.lock().generation;
                if frames_generation < own {
                    drop(gate);
                    refuse(sender, own, shared);
                    return Ok(());
                }
                let position = copies
                    .get(&database)?
                    .apply_frames(header.as_deref(), first_frame, end_frame, &bytes)?;

                // The confirmation is sent only after the frames are synced and only under the gate, so that
                // a takeover written in the meantime is never followed by a confirmation of the old generation.
                sender.send(&Message::Confirm(position), timeout)?;
                drop(gate);
            }
            Message::Heartbeat {
                generation: heartbeat_generation,
            } => {
                let own = shared.state.lock().generation;
                if heartbeat_generation < own {
                    refuse(sender, own, shared);
                    return Ok(());
                }
                sender.send(&Message::HeartbeatAck, timeout)?;
            }
            Message::SnapshotBegin { database, .. } => {
                {
                    let mut state = shared.state.lock();

                    // A fenced node replaces its files only once its Zato server has stopped.
                    while state.role == Role::Fenced && !state.stopping {
                        shared.changed.wait(&mut state);
                    }
                    if !state.role.is_standby() {
                        return Err(Error::new(
                            ErrorKind::InvalidData,
                            format!("a snapshot arrived in role {:?}", state.role),
                        ));
                    }
                    state.role = Role::Joining;
                    drop(state);
                    shared.changed.notify_all();
                }
                copies.get(&database)?.begin_snapshot()?;
            }
            Message::SnapshotChunk { database, kind, bytes } => copies.get(&database)?.append_snapshot(kind, &bytes)?,
            Message::SnapshotEnd { database } => {
                let position = copies.get(&database)?.end_snapshot()?;
                sender.send(&Message::Confirm(position), timeout)?;
            }
            Message::Admit { generation: admitted } => {
                let mut state = shared.state.lock();
                state.generation = admitted;
                state.role = Role::StandbyInSync;
                state.last_peer_contact = Instant::now();
                drop(state);
                shared.changed.notify_all();
                tracing::info!("Admitted as the standby in sync at generation {admitted}");
            }
            other => {
                return Err(Error::new(ErrorKind::InvalidData, format!("unexpected message {other:?}")));
            }
        }
    }
}

/// Handles one accepted connection.
fn handle_connection(shared: &Shared, tcp: TcpStream) -> Result<(), Error> {
    let AcceptedLink {
        sender,
        mut receiver,
        peer_certificate,
    } = shared.tls.accept(tcp)?;

    let Message::Hello { generation, active_node } = receiver.receive()? else {
        return Err(Error::new(ErrorKind::InvalidData, "the link did not begin with a hello"));
    };

    // The certificate must name the node the peer claims to be, and that node must be the other one.
    verify_peer_name(&peer_certificate, &active_node)?;
    if active_node == shared.config.node_name {
        return Err(Error::new(ErrorKind::InvalidData, "the peer claims the name of this node"));
    }

    let outcome = run_session(shared, &sender, &mut receiver, &active_node, generation);
    sender.close();
    outcome
}

/// Listens for links from the active node.
pub fn serve(shared: &Arc<Shared>) -> Result<(), Error> {
    let listener = TcpListener::bind(("0.0.0.0", shared.config.replication_port))?;
    tracing::info!("Replication link listening on port {}", shared.config.replication_port);

    let shared = Arc::clone(shared);
    let _ = std::thread::Builder::new().name("link-listener".to_owned()).spawn(move || {
        for tcp in listener.incoming() {
            let Ok(tcp) = tcp else {
                continue;
            };
            let connection_shared = Arc::clone(&shared);
            let spawned = std::thread::Builder::new().name("link-session".to_owned()).spawn(move || {
                if let Err(error) = handle_connection(&connection_shared, tcp) {
                    tracing::warn!("Replication session ended: {error}");
                }
            });
            if let Err(error) = spawned {
                tracing::error!("Cannot start a replication session thread: {error}");
            }
        }
    })?;
    Ok(())
}
