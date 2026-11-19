// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The replication barrier, answered over a Unix socket.
//!
//! A request is a single newline, and the node answers `ok` once every frame of the Zato database committed
//! before the request is synced on the standby, or locally when the node runs alone. A node that is no longer
//! active answers `replaced`, and a barrier that cannot be answered is answered with `error` followed by
//! a description. A connection accepts any number of requests, one after another.

use std::fs::File;
use std::io::{BufRead, BufReader, ErrorKind, Write};
use std::os::unix::net::{UnixListener, UnixStream};
use std::path::Path;
use std::sync::Arc;

use crate::state::{Role, Shared};
use crate::wal;

/// The answer to a barrier that completed.
const ANSWER_OK: &str = "ok\n";

/// The answer of a node that is no longer active.
const ANSWER_REPLACED: &str = "replaced\n";

/// The outcome of one barrier.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BarrierOutcome {
    /// The frames are synced.
    Synced,

    /// The node is no longer active.
    Replaced,

    /// The barrier could not be answered.
    Failed(String),
}

/// Syncs the log of the Zato database to the local disk.
fn sync_locally(db_path: &Path) -> BarrierOutcome {
    let path = wal::wal_path(db_path);
    let outcome = File::open(&path).and_then(|file| file.sync_data());
    match outcome {
        Ok(()) => BarrierOutcome::Synced,

        // A database whose log does not exist yet has nothing to sync.
        Err(error) if error.kind() == ErrorKind::NotFound => BarrierOutcome::Synced,
        Err(error) => BarrierOutcome::Failed(format!("sync of {}: {error}", path.display())),
    }
}

/// Waits until the frames of the Zato database committed before the call are synced on the standby or locally.
pub fn wait(shared: &Shared) -> BarrierOutcome {
    let db_path = &shared.config.database_path;
    let mut state = shared.state.lock();

    // A scan that starts after this point reads every frame committed before the call.
    state.scan_requested += 1;
    let ticket = state.scan_requested;
    shared.changed.notify_all();

    loop {
        match state.role {
            // A writer that would go on to its next commit at once waits while the shipper needs the write lock,
            // which a steady stream of commits would otherwise keep from it.
            Role::ActiveSolo if !state.admitting && !state.taking_snapshot_lock => {
                drop(state);
                return sync_locally(db_path);
            }
            Role::ActiveSolo | Role::ActiveReplicated => {
                if state.scan_completed >= ticket {
                    break;
                }
            }
            _ => return BarrierOutcome::Replaced,
        }
        shared.changed.wait(&mut state);
    }

    let target = state.database.scanned;

    loop {
        match state.role {
            // The record may already name this node alone, and the mark-out syncs the log before the node is active alone.
            Role::ActiveReplicated if state.needs_mark_out => {}
            Role::ActiveReplicated => {
                if state.database.confirmed >= target {
                    return BarrierOutcome::Synced;
                }
            }

            // A mark-out syncs the log before it moves the node to this role, and an admission in progress
            // holds the barrier until the standby is in sync.
            Role::ActiveSolo if !state.admitting && !state.taking_snapshot_lock => {
                drop(state);
                return sync_locally(db_path);
            }
            Role::ActiveSolo => {}
            _ => return BarrierOutcome::Replaced,
        }
        shared.changed.wait(&mut state);
    }
}

/// Answers the requests of one connection.
fn serve_connection(shared: &Shared, stream: UnixStream) {
    let Ok(mut writer) = stream.try_clone() else {
        return;
    };
    let reader = BufReader::new(stream);

    for line in reader.lines() {
        // A connection that fails to read ends.
        if line.is_err() {
            return;
        }
        let answer = match wait(shared) {
            BarrierOutcome::Synced => ANSWER_OK.to_owned(),
            BarrierOutcome::Replaced => ANSWER_REPLACED.to_owned(),
            BarrierOutcome::Failed(reason) => format!("error {}\n", reason.replace('\n', " ")),
        };

        // A client that went away ends the connection.
        if writer.write_all(answer.as_bytes()).is_err() {
            return;
        }
    }
}

/// Listens on the barrier socket and answers each connection in a thread of its own.
pub fn serve(shared: &Arc<Shared>) -> Result<(), std::io::Error> {
    let path = &shared.config.barrier_socket;

    // A socket file left by an earlier process would make the bind fail.
    match std::fs::remove_file(path) {
        Ok(()) => {}
        Err(error) if error.kind() == ErrorKind::NotFound => {}
        Err(error) => return Err(error),
    }
    let listener = UnixListener::bind(path)?;
    tracing::info!("Barrier socket listening on {}", path.display());

    let shared = Arc::clone(shared);
    let _ = std::thread::Builder::new().name("barrier".to_owned()).spawn(move || {
        for stream in listener.incoming() {
            let Ok(stream) = stream else {
                continue;
            };
            let connection_shared = Arc::clone(&shared);
            let spawned = std::thread::Builder::new()
                .name("barrier-connection".to_owned())
                .spawn(move || serve_connection(&connection_shared, stream));
            if let Err(error) = spawned {
                tracing::error!("Cannot start a barrier connection thread: {error}");
            }
        }
    })?;
    Ok(())
}
