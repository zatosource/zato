// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The threads of a session that receive the confirmations of the standby and send it the heartbeats.

use std::sync::Arc;
use std::thread;
use std::time::Instant;

use crate::clock;
use crate::link::{LinkReceiver, LinkSender};
use crate::protocol::{Message, Position};
use crate::state::{LogPosition, NodeState, Role, Shared};

/// Whether a session is still the current one.
fn is_current(shared: &Shared, number: u64) -> bool {
    let state = shared.state.lock();
    state.session == number && state.role.is_active() && !state.stopping
}

/// Ends a session from one of its threads, if it is still the current one.
fn end_from_thread(shared: &Shared, number: u64, reason: &str) {
    let mut state = shared.state.lock();
    if state.session == number {
        tracing::warn!("Session {number} ended: {reason}");
        state.close_link();
        drop(state);
        shared.changed.notify_all();
    }
}

/// Applies a confirmation of the standby.
fn apply_confirmation(state: &mut NodeState, position: &Position) {
    let progress = &mut state.database;
    let confirmed = if position.salt_one == 0 && position.salt_two == 0 {
        Some(LogPosition {
            cycle: 0,
            frame: position.end_frame,
        })
    } else {
        progress.cycle_of(position.salt_one, position.salt_two).map(|record| LogPosition {
            cycle: record.cycle,
            frame: position.end_frame,
        })
    };
    if let Some(confirmed) = confirmed {
        progress.record_confirmation(confirmed);
    }
}

/// Records the skew of the wall clock that the standby reported.
///
/// A standby in sync whose skew exceeds the bound is marked out, since it would move the time of the database
/// by that skew once it took over.
pub(super) fn record_clock_skew(shared: &Shared, state: &mut NodeState, clock_skew_ms: u64) {
    state.peer_clock_skew_ms = clock_skew_ms;

    let max_clock_skew_ms = shared.config.max_clock_skew_ms;
    let exceeds_bound = clock_skew_ms > max_clock_skew_ms;

    // The mark-out is requested once, and the control loop carries it out.
    if exceeds_bound && state.role == Role::ActiveReplicated && !state.needs_mark_out {
        tracing::warn!(
            "The wall clock of the standby is {clock_skew_ms} ms away from that of this node, above the bound of {max_clock_skew_ms} ms"
        );
        state.needs_mark_out = true;
    }
}

/// Receives the confirmations and heartbeat answers of one session.
pub(super) fn receive_loop(shared: &Shared, mut receiver: LinkReceiver, number: u64) {
    loop {
        let message = match receiver.receive() {
            Ok((message, next)) => {
                receiver = next;
                message
            }
            Err(error) => {
                end_from_thread(shared, number, &error.to_string());
                return;
            }
        };
        let mut state = shared.state.lock();
        if state.session != number {
            return;
        }
        state.last_peer_contact = Instant::now();
        match message {
            Message::Confirm(position) => apply_confirmation(&mut state, &position),
            Message::HeartbeatAck { clock_skew_ms } => record_clock_skew(shared, &mut state, clock_skew_ms),
            // The standby refuses the frames of a generation it left behind, and a node that wrote the newer generation
            // itself in the meantime, by a mark-out or an admission, was not replaced, so only a higher one fences it.
            Message::Refused { generation } if generation > state.generation => {
                shared.fence(&mut state, generation);
                return;
            }
            Message::Refused { generation } => {
                drop(state);
                end_from_thread(shared, number, &format!("frames refused at generation {generation}"));
                return;
            }
            other => {
                drop(state);
                end_from_thread(shared, number, &format!("unexpected message {other:?}"));
                return;
            }
        }
        drop(state);
        shared.changed.notify_all();
    }
}

/// Sends a heartbeat at every interval for as long as the session is current.
fn heartbeat_loop(shared: &Shared, sender: &LinkSender, number: u64) {
    let interval = shared.config.timers.heartbeat;
    loop {
        thread::sleep(interval);
        if !is_current(shared, number) {
            return;
        }
        let generation = shared.state.lock().generation;
        let heartbeat = Message::Heartbeat {
            generation,
            wall_ms: clock::wall_ms(),
        };
        if let Err(error) = sender.send(&heartbeat, shared.config.timers.mark_out) {
            end_from_thread(shared, number, &error.to_string());
            return;
        }
    }
}

/// Starts the receiving and the heartbeat threads of a session.
pub(super) fn start_session_threads(shared: &Arc<Shared>, receiver: LinkReceiver, sender: LinkSender, number: u64) {
    let receive_shared = Arc::clone(shared);
    let receiving = thread::Builder::new()
        .name("link-receive".to_owned())
        .spawn(move || receive_loop(&receive_shared, receiver, number));
    let heartbeat_shared = Arc::clone(shared);
    let heartbeats = thread::Builder::new()
        .name("link-heartbeat".to_owned())
        .spawn(move || heartbeat_loop(&heartbeat_shared, &sender, number));
    if let Err(error) = receiving.and(heartbeats) {
        tracing::error!("Cannot start the threads of session {number}: {error}");
        end_from_thread(shared, number, "no threads");
    }
}
