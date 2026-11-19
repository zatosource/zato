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

use parking_lot::MutexGuard;

use crate::clock::SkewEstimate;
use crate::copy::DatabaseCopy;
use crate::link::{AcceptedLink, LinkReceiver, LinkSender, verify_peer_name};
use crate::protocol::Message;
use crate::state::{Role, Shared};

/// What the hello of the active node that opened a session tells about that node.
struct Opening<'hello> {
    /// The name of the active node.
    active_node: &'hello str,

    /// The generation of the active node.
    generation: u64,

    /// The skew of the wall clock of this node from that of the active node.
    skew: SkewEstimate,
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

/// Takes the gate of the copy for one message of `session`, or returns `None` once a newer session replaced it.
///
/// A message received before a newer session opened is thus never applied after the messages of that session.
fn enter_gate(shared: &Shared, session: u64) -> Option<MutexGuard<'_, ()>> {
    let gate = shared.apply_gate.lock();
    is_current(shared, session).then_some(gate)
}

/// Begins replacing the copy with the files of the active node, returning `false` once a newer session replaced `session`.
fn begin_snapshot(shared: &Shared, session: u64, copy: &mut DatabaseCopy) -> Result<bool, Error> {
    {
        let mut state = shared.state.lock();

        // A fenced node replaces its files only once its Zato server has stopped.
        while state.role == Role::Fenced && !state.stopping {
            shared.changed.wait(&mut state);
        }
    }
    let Some(gate) = enter_gate(shared, session) else {
        return Ok(false);
    };
    {
        let mut state = shared.state.lock();
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
    copy.begin_snapshot()?;
    drop(gate);
    Ok(true)
}

/// Applies the messages of one session until it ends.
fn run_session(shared: &Shared, sender: &LinkSender, mut receiver: LinkReceiver, mut opening: Opening<'_>) -> Result<(), Error> {
    let generation = opening.generation;
    let active_node = opening.active_node;
    let Some((session, resumes)) = open_session(shared, sender, generation) else {
        return Ok(());
    };
    let timeout = shared.config.timers.mark_out;
    let max_clock_skew_ms = shared.config.max_clock_skew_ms;

    // The position is read only once an earlier session finished the message it was applying.
    let Some(gate) = enter_gate(shared, session) else {
        return Ok(());
    };
    let mut copy = DatabaseCopy::open(&shared.config.database_path)?;
    let position = resumes.then(|| copy.position());
    drop(gate);

    // The skew measured from the hello tells the active node whether this node may be admitted.
    let clock_skew_ms = opening.skew.current();
    sender.send(&Message::HelloReply { position, clock_skew_ms }, timeout)?;
    tracing::info!("Session with {active_node} at generation {generation} opened, resuming in sync: {resumes}");

    loop {
        let (message, next) = receiver.receive()?;
        receiver = next;
        if !is_current(shared, session) {
            return Ok(());
        }

        // Every message from the active node shows it is alive.
        shared.state.lock().last_peer_contact = Instant::now();

        match message {
            Message::Frames {
                generation: frames_generation,
                header,
                first_frame,
                end_frame,
                bytes,
            } => {
                let Some(gate) = enter_gate(shared, session) else {
                    return Ok(());
                };
                let own = shared.state.lock().generation;
                if frames_generation < own {
                    drop(gate);
                    refuse(sender, own, shared);
                    return Ok(());
                }
                let position = copy.apply_frames(header.as_deref(), first_frame, end_frame, &bytes)?;

                // The confirmation is sent only after the frames are synced and only under the gate, so that
                // a takeover written in the meantime is never followed by a confirmation of the old generation.
                sender.send(&Message::Confirm(position), timeout)?;
                drop(gate);
            }
            Message::Heartbeat {
                generation: heartbeat_generation,
                wall_ms,
            } => {
                let own = shared.state.lock().generation;
                if heartbeat_generation < own {
                    refuse(sender, own, shared);
                    return Ok(());
                }

                // The active node marks this node out if its wall clock moved too far from its own.
                let clock_skew_ms = opening.skew.record(wall_ms, max_clock_skew_ms);
                sender.send(&Message::HeartbeatAck { clock_skew_ms }, timeout)?;
            }
            Message::SnapshotBegin { .. } => {
                if !begin_snapshot(shared, session, &mut copy)? {
                    return Ok(());
                }
            }
            Message::SnapshotChunk { kind, bytes } => {
                let Some(gate) = enter_gate(shared, session) else {
                    return Ok(());
                };
                copy.append_snapshot(kind, &bytes)?;
                drop(gate);
            }
            Message::SnapshotEnd => {
                let Some(gate) = enter_gate(shared, session) else {
                    return Ok(());
                };
                let position = copy.end_snapshot()?;
                sender.send(&Message::Confirm(position), timeout)?;
                drop(gate);
            }
            Message::Admit { generation: admitted } => {
                let Some(gate) = enter_gate(shared, session) else {
                    return Ok(());
                };
                let mut state = shared.state.lock();
                state.generation = admitted;
                state.role = Role::StandbyInSync;
                state.last_peer_contact = Instant::now();
                drop(state);
                drop(gate);
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
        receiver,
        peer_certificate,
    } = shared.link_tls()?.accept(tcp)?;

    let (hello, receiver) = receiver.receive()?;
    let Message::Hello {
        generation,
        active_node,
        wall_ms,
    } = hello
    else {
        return Err(Error::new(ErrorKind::InvalidData, "the link did not begin with a hello"));
    };

    // The certificate must name the node the peer claims to be, and that node must be the other one.
    verify_peer_name(&peer_certificate, &active_node)?;
    if active_node == shared.config.node_name {
        return Err(Error::new(ErrorKind::InvalidData, "the peer claims the name of this node"));
    }

    let mut skew = SkewEstimate::default();
    let _ = skew.record(wall_ms, shared.config.max_clock_skew_ms);
    let opening = Opening {
        active_node: &active_node,
        generation,
        skew,
    };
    let outcome = run_session(shared, &sender, receiver, opening);
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::Timers;
    use crate::control::Control;
    use crate::generation;
    use crate::link::TlsContext;
    use crate::referee::tests::MemoryReferee;
    use crate::test_support::{self, Certificates, LOOPBACK, NODE_A, NODE_B};
    use std::sync::atomic::AtomicBool;
    use std::time::Duration;

    /// The timers of a node whose loops do not run in a test.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_secs(1),
        mark_out: Duration::from_secs(3),
        takeover: Duration::from_secs(6),
    };

    #[test]
    fn a_session_that_a_newer_one_replaced_no_longer_applies_anything() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_B, dir.path(), &certificates, TIMERS);
        let shared = test_support::shared(config, Box::new(MemoryReferee::default()));
        let earlier = {
            let mut state = shared.state.lock();
            state.session += 1;
            state.session
        };
        assert!(enter_gate(&shared, earlier).is_some());

        shared.state.lock().session += 1;
        assert!(enter_gate(&shared, earlier).is_none());
    }

    #[test]
    fn a_restarted_node_refuses_a_link_below_its_persisted_generation() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_B, dir.path(), &certificates, TIMERS);
        generation::write(&config.generation_file(), 3).unwrap();
        let shared = test_support::shared(config, Box::new(MemoryReferee::default()));
        let _control = Control::new(Arc::clone(&shared), None, Arc::new(AtomicBool::new(false))).unwrap();

        let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let accepting = Arc::clone(&shared);
        let server = std::thread::spawn(move || {
            let (tcp, _) = listener.accept().unwrap();
            let _ = handle_connection(&accepting, tcp);
        });

        let tls = TlsContext::load(&certificates.files(NODE_A)).unwrap();
        let (sender, receiver) = tls.connect(NODE_B, LOOPBACK, port).unwrap();
        let hello = Message::Hello {
            generation: 1,
            active_node: NODE_A.to_owned(),
            wall_ms: crate::clock::wall_ms(),
        };
        sender.send(&hello, TIMERS.mark_out).unwrap();
        let (reply, _receiver) = receiver.receive().unwrap();
        server.join().unwrap();

        assert_eq!(reply, Message::Refused { generation: 3 });
        let state = shared.state.lock();
        let role_and_generation = (state.role, state.generation);
        drop(state);
        assert_eq!(role_and_generation, (Role::Down, 3));
    }
}
