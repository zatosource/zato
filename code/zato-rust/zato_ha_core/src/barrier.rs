// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The replication barrier, answered over a Unix socket.
//!
//! A client writes the name of a database followed by a newline, and the node answers `ok` once every frame
//! of that database committed before the request is synced on the standby, or locally when the node runs
//! alone. A node that is no longer active answers `replaced`, and an unknown database is answered with
//! `error` followed by a description. A connection carries any number of requests, one after another.

use std::fs::File;
use std::io::{BufRead, BufReader, ErrorKind, Write};
use std::os::unix::net::{UnixListener, UnixStream};
use std::path::Path;
use std::sync::Arc;

use crate::config::ShippingMode;
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

/// Syncs the log of a database to the local disk.
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

/// Waits until the frames of `database` committed before the call are synced on the standby or locally.
pub fn wait(shared: &Shared, database: &str) -> BarrierOutcome {
    let Some(config) = shared
        .config
        .database(database)
        .filter(|config| config.shipping == ShippingMode::Synchronous)
    else {
        return BarrierOutcome::Failed(format!("unknown database `{database}`"));
    };

    let mut state = shared.state.lock();

    // A scan that starts after this point reads every frame committed before the call.
    state.scan_requested += 1;
    let ticket = state.scan_requested;
    shared.changed.notify_all();

    loop {
        match state.role {
            Role::ActiveSolo if !state.admitting => {
                drop(state);
                return sync_locally(&config.path);
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

    let Some(target) = state
        .databases
        .iter()
        .find(|progress| progress.name == database)
        .map(|progress| progress.scanned)
    else {
        return BarrierOutcome::Failed(format!("unknown database `{database}`"));
    };

    loop {
        match state.role {
            Role::ActiveReplicated => {
                let confirmed = state
                    .databases
                    .iter()
                    .find(|progress| progress.name == database)
                    .map(|progress| progress.confirmed);
                if confirmed.is_some_and(|confirmed| confirmed >= target) {
                    return BarrierOutcome::Synced;
                }
            }

            // A mark-out syncs every log before it moves the node to this role, and an admission in progress
            // holds the barrier until the standby is in sync.
            Role::ActiveSolo if !state.admitting => {
                drop(state);
                return sync_locally(&config.path);
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
        let Ok(database) = line else {
            return;
        };
        let answer = match wait(shared, database.trim()) {
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
