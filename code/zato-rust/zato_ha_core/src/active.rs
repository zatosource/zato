// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The opening end of the replication link on the active node.
//!
//! One thread, the shipper, reads the log of the Zato database, records its end for the barrier, ships the new
//! frames to the standby, sends a snapshot to a standby that joins, admits a standby that caught up, and checkpoints
//! the log. A second thread per session receives the confirmations, and a third sends the heartbeats.

use std::io::{Error, ErrorKind};
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use rusqlite::Connection;
use rusqlite::config::DbConfig;

use crate::clock;
use crate::link::LinkSender;
use crate::protocol::{FileKind, Message, Position};
use crate::state::{CycleRecord, LinkState, LogPosition, Role, Shared};
use crate::wal::{self, WalCursor};

mod admission;
mod checkpoint;
mod frames;
mod session;

use frames::{FreshFrames, SnapshotFile, frames_to_send, scan_to_end, send_file};
use session::start_session_threads;

/// How often the log is read when no barrier asks for it, which keeps the standby close to the active node.
const POLL_INTERVAL: Duration = Duration::from_millis(20);

/// How often a link to the standby is attempted while there is none.
const CONNECT_INTERVAL: Duration = Duration::from_secs(1);

/// The size above which a log is checkpointed.
const CHECKPOINT_WAL_SIZE: u64 = 64 * 1024 * 1024;

/// How long the node's own connections wait for the write lock of the Zato database.
const LOCK_BUSY_TIMEOUT: Duration = Duration::from_secs(5);

/// How long the node's own connections sleep between two attempts to take the write lock.
const LOCK_RETRY_INTERVAL: Duration = Duration::from_millis(1);

/// The connections the node keeps open to the Zato database while it is active.
///
/// Keeping a connection open means no connection of the Zato server is ever the last one to close,
/// which would checkpoint and delete the log.
struct DatabaseConnections {
    /// Takes the write lock during a checkpoint.
    lock: Connection,

    /// Runs the checkpoint while the write lock is held by `lock`.
    checkpoint: Connection,
}

/// Returns a busy handler that tries to take the write lock again at a short fixed interval, until `LOCK_BUSY_TIMEOUT` elapses.
///
/// The busy handler of `SQLite` sleeps longer after each attempt, up to a tenth of a second, while the writers
/// of the Zato server commit one after another, so it takes the lock only once the writes pause. An attempt
/// at a short fixed interval takes it in one of the gaps between their transactions.
fn lock_retry() -> impl FnMut(i32) -> bool + Send + 'static {
    let mut first_attempt = Instant::now();
    move |attempts| {
        // Each locking event counts its attempts from zero, and its wait starts with the first of them.
        if attempts == 0 {
            first_attempt = Instant::now();
        }
        thread::sleep(LOCK_RETRY_INTERVAL);
        first_attempt.elapsed() < LOCK_BUSY_TIMEOUT
    }
}

/// Opens a connection that never checkpoints by itself.
fn open_connection(path: &Path) -> Result<Connection, Error> {
    let mut connection = Connection::open(path).map_err(Error::other)?;
    let _ = connection
        .set_db_config(DbConfig::SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, true)
        .map_err(Error::other)?;
    connection.busy_handler(Some(lock_retry())).map_err(Error::other)?;
    let _: String = connection
        .query_row("pragma journal_mode=wal", [], |row| row.get(0))
        .map_err(Error::other)?;
    // A checkpoint of this connection syncs the database file before it truncates the log, whatever the compiled default.
    connection.pragma_update(None, "synchronous", "full").map_err(Error::other)?;
    connection.pragma_update(None, "wal_autocheckpoint", 0).map_err(Error::other)?;
    Ok(connection)
}

/// The replicated Zato database as the shipper sees it.
struct Database {
    /// The path of the database file.
    path: PathBuf,

    /// The cursor whose end every barrier and every session refers to.
    cursor: WalCursor,

    /// The node's connections, opened while the node is active.
    connections: Option<DatabaseConnections>,

    /// The end of the log at the last checkpoint that copied every frame of the log into the database file.
    checkpointed: LogPosition,
}

impl Database {
    /// Returns a database nothing was read from.
    fn new(path: &Path) -> Self {
        Self {
            cursor: WalCursor::of_database(path),
            path: path.to_owned(),
            connections: None,
            checkpointed: LogPosition::default(),
        }
    }

    /// Opens the node's connections, creating the database if it does not exist.
    fn open(&mut self) -> Result<(), Error> {
        if self.connections.is_some() {
            return Ok(());
        }
        if let Some(parent) = self.path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let lock = open_connection(&self.path)?;
        let checkpoint = open_connection(&self.path)?;
        self.connections = Some(DatabaseConnections { lock, checkpoint });

        // A log read under another role describes files that may have been replaced since.
        self.cursor = WalCursor::of_database(&self.path);
        self.checkpointed = LogPosition::default();
        Ok(())
    }

    /// Returns the cycle record of the cursor's current cycle.
    fn cycle_record(&self) -> Option<CycleRecord> {
        self.cursor.header().map(|header| CycleRecord {
            cycle: self.cursor.cycle(),
            salt_one: header.salt_one,
            salt_two: header.salt_two,
            end_frame: self.cursor.end_frame(),
        })
    }

    /// Returns the current end of the log.
    const fn end(&self) -> LogPosition {
        LogPosition {
            cycle: self.cursor.cycle(),
            frame: self.cursor.end_frame(),
        }
    }

    /// Whether the current cycle of the log reached the length at which it is checkpointed.
    fn is_long(&self) -> bool {
        // A log that restarts keeps the length of its file, so only the frames of the current cycle count.
        let frame_size = self.cursor.header().map_or(0, wal::WalHeader::frame_size);
        let size = u64::from(self.cursor.end_frame()).saturating_mul(frame_size);
        size >= CHECKPOINT_WAL_SIZE
    }
}

/// What a session has sent of the Zato database.
#[derive(Debug, Clone)]
struct SessionDatabase {
    /// The header of the log the standby holds.
    header: Option<Vec<u8>>,

    /// The end of what was sent.
    sent: LogPosition,
}

/// A link to the standby.
struct Session {
    /// The sending half.
    sender: LinkSender,

    /// The session number, which tells the receiving and the heartbeat threads that they belong to it.
    number: u64,

    /// What was sent of the Zato database.
    database: SessionDatabase,

    /// Whether the standby is joining, as opposed to being in sync.
    joining: bool,

    /// The name of the standby.
    peer: String,
}

/// The shipper thread.
pub struct Shipper {
    /// The shared state.
    shared: Arc<Shared>,

    /// The replicated Zato database.
    database: Database,

    /// The current session, if any.
    session: Option<Session>,

    /// When a link was last attempted.
    last_connect: Option<Instant>,

    /// When the barriers were last held for an admission.
    admission_started: Instant,
}

impl Shipper {
    /// Returns a shipper that has not read anything yet.
    pub fn new(shared: Arc<Shared>) -> Self {
        let database = Database::new(&shared.config.database_path);
        Self {
            shared,
            database,
            session: None,
            last_connect: None,
            admission_started: Instant::now(),
        }
    }

    /// Runs the shipper until the node stops.
    pub fn run(mut self) {
        loop {
            if !self.wait_until_active() {
                return;
            }
            if let Err(error) = self.iteration() {
                tracing::warn!("Shipping error: {error}");
                self.end_session();
                thread::sleep(POLL_INTERVAL);
            }
        }
    }

    /// Waits until the node is active, closing what the shipper holds while it is not, and returns `false` on a stop.
    fn wait_until_active(&mut self) -> bool {
        let mut state = self.shared.state.lock();
        if state.role.is_active() && !state.stopping {
            return true;
        }
        drop(state);

        // A node that is no longer active keeps neither a session nor connections to files that a snapshot will replace.
        self.end_session();
        self.database.connections = None;

        state = self.shared.state.lock();
        while !state.role.is_active() && !state.stopping {
            self.shared.changed.wait(&mut state);
        }
        !state.stopping
    }

    /// Reads, ships, joins, admits and checkpoints once.
    fn iteration(&mut self) -> Result<(), Error> {
        // A session that its receiving or heartbeat thread ended is dropped here as well.
        if let Some(session) = &self.session {
            let state = self.shared.state.lock();
            let is_current = state.session == session.number && state.link.is_some();
            drop(state);
            if !is_current {
                self.session = None;
            }
        }

        self.database.open()?;

        let ticket = {
            let mut state = self.shared.state.lock();
            if state.scan_requested == state.scan_completed {
                let _ = self.shared.changed.wait_for(&mut state, POLL_INTERVAL);
            }
            state.scan_requested
        };

        self.scan_and_ship(ticket)?;

        if self.session.is_none() {
            self.connect_if_due();
        }
        self.admit_if_caught_up()?;
        self.checkpoint_if_due()?;
        Ok(())
    }

    /// Reads the log to its end, ships what the session has not sent yet and completes the scan for the barrier.
    fn scan_and_ship(&mut self, ticket: u64) -> Result<(), Error> {
        let Some(connections) = self.database.connections.as_ref() else {
            return Err(Error::other("the database is not open"));
        };
        let fresh = scan_to_end(&mut self.database.cursor, &connections.checkpoint)?;

        // The standby in sync owes the frames from the moment they are read, whether or not a session can ship them.
        self.record_read();
        self.ship(&fresh)?;

        let end = self.database.end();
        let record = self.database.cycle_record();
        let mut state = self.shared.state.lock();
        state.database.scanned = end;
        if let Some(record) = record {
            state.database.record_cycle(record);
        }
        state.scan_completed = state.scan_completed.max(ticket);
        drop(state);
        self.shared.changed.notify_all();
        Ok(())
    }

    /// Records the end of the log as read and not yet confirmed while a standby is in sync.
    fn record_read(&self) {
        let read_at = Instant::now();
        let end = self.database.end();
        let mut state = self.shared.state.lock();

        // Without a standby in sync, no barrier waits for a confirmation.
        if state.role != Role::ActiveReplicated {
            return;
        }
        state.database.record_read(end, read_at);
    }

    /// Sends the next chunk of the frames that the session, if any, has not sent yet.
    fn ship(&mut self, fresh: &[FreshFrames]) -> Result<(), Error> {
        let Some(session) = self.session.as_mut() else {
            return Ok(());
        };
        let generation = self.shared.state.lock().generation;
        let timeout = self.shared.config.timers.mark_out;

        for message in frames_to_send(&self.database, &mut session.database, fresh, generation)? {
            session.sender.send(&message, timeout)?;
        }
        Ok(())
    }

    /// Ends the current session, if any.
    fn end_session(&mut self) {
        if self.session.take().is_some() {
            self.shared.state.lock().close_link();
            self.shared.changed.notify_all();
        }
    }

    /// Opens a link to the other node if one was not attempted recently.
    fn connect_if_due(&mut self) {
        let now = Instant::now();
        if self.last_connect.is_some_and(|last| now.duration_since(last) < CONNECT_INTERVAL) {
            return;
        }
        self.last_connect = Some(now);

        match self.open_session() {
            Ok(()) => {}
            Err(error) if error.kind() == ErrorKind::NotFound => {}
            Err(error) => tracing::debug!("No link to the standby: {error}"),
        }
    }

    /// Opens a link to the other node, resumes it in sync or sends it a snapshot.
    fn open_session(&mut self) -> Result<(), Error> {
        let config = &self.shared.config;
        let addresses = self.shared.referee.read_addresses().map_err(Error::other)?;
        let Some(peer) = addresses.into_iter().find(|address| address.node_name != config.node_name) else {
            return Err(Error::new(ErrorKind::NotFound, "the other node has not published its address"));
        };

        let (sender, receiver) = self.shared.link_tls()?.connect(&peer.node_name, &peer.host, peer.port)?;
        let (generation, role) = {
            let state = self.shared.state.lock();
            (state.generation, state.role)
        };
        let timeout = config.timers.mark_out;
        sender.send(
            &Message::Hello {
                generation,
                active_node: config.node_name.clone(),
                wall_ms: clock::wall_ms(),
            },
            timeout,
        )?;

        let (reply, receiver) = receiver.receive()?;
        let (position, clock_skew_ms) = match reply {
            Message::HelloReply { position, clock_skew_ms } => (position, clock_skew_ms),
            Message::Refused { generation: higher } => {
                self.shared.fence(&mut self.shared.state.lock(), higher);
                return Ok(());
            }
            other => return Err(Error::new(ErrorKind::InvalidData, format!("unexpected answer {other:?}"))),
        };

        let number = {
            let mut state = self.shared.state.lock();
            state.session += 1;
            state.peer_clock_skew_ms = clock_skew_ms;
            state.session
        };

        let session = if role == Role::ActiveReplicated {
            let Some(position) = position else {
                // The record names this standby as in sync, so it may not join before it is marked out.
                self.request_mark_out(&peer.node_name, "the standby is not in sync");
                sender.close();
                return Ok(());
            };
            let Some(database) = self.resume_position(&position) else {
                self.request_mark_out(&peer.node_name, "the standby cannot resume from its position");
                sender.close();
                return Ok(());
            };
            Session {
                sender: sender.clone(),
                number,
                database,
                joining: false,
                peer: peer.node_name.clone(),
            }
        } else {
            let database = match self.send_snapshot(&sender, generation) {
                Ok(database) => database,
                Err(error) => {
                    // A backup that did not complete leaves no standby joining.
                    self.shared.state.lock().close_link();
                    self.shared.changed.notify_all();
                    return Err(error);
                }
            };
            Session {
                sender: sender.clone(),
                number,
                database,
                joining: true,
                peer: peer.node_name.clone(),
            }
        };

        {
            let mut state = self.shared.state.lock();
            state.link = Some(sender.clone());
            state.peer_name = Some(peer.node_name);
            state.link_state = if session.joining {
                LinkState::Joining
            } else {
                LinkState::Streaming
            };
            state.last_peer_contact = Instant::now();
            drop(state);
            self.shared.changed.notify_all();
        }

        start_session_threads(&self.shared, receiver, sender, number);
        tracing::info!("Session {number} with {} opened, joining: {}", session.peer, session.joining);
        self.session = Some(session);
        Ok(())
    }

    /// Records that the standby must be marked out before it joins again.
    fn request_mark_out(&self, peer: &str, reason: &str) {
        tracing::warn!("Marking out {peer}: {reason}");
        self.shared.state.lock().needs_mark_out = true;
        self.shared.changed.notify_all();
    }

    /// Returns what the standby holds of the Zato database, if it can resume from its position.
    fn resume_position(&self, position: &Position) -> Option<SessionDatabase> {
        let progress = self.shared.state.lock().database.clone();
        let cursor = &self.database.cursor;

        // A standby without a log can resume only while the active node has none either.
        if position.salt_one == 0 && position.salt_two == 0 && position.end_frame == 0 {
            if cursor.header().is_some() {
                return None;
            }
            return Some(SessionDatabase {
                header: None,
                sent: LogPosition::default(),
            });
        }

        let record = progress.cycle_of(position.salt_one, position.salt_two)?;
        let is_current = record.cycle == cursor.cycle();

        // The standby holds a prefix of the current cycle, or the whole of the previous one.
        let holds_prefix = is_current && position.end_frame <= cursor.end_frame();
        let holds_previous = !is_current && position.end_frame == record.end_frame;
        if !holds_prefix && !holds_previous {
            return None;
        }

        let header = if is_current {
            cursor.header().map(|header| header.raw.to_vec())
        } else {
            None
        };
        Some(SessionDatabase {
            header,
            sent: LogPosition {
                cycle: record.cycle,
                frame: position.end_frame,
            },
        })
    }

    /// Sends the files of the Zato database to a joining standby and returns what it then holds.
    fn send_snapshot(&mut self, sender: &LinkSender, generation: u64) -> Result<SessionDatabase, Error> {
        let timeout = self.shared.config.timers.mark_out;

        {
            // What an earlier standby confirmed says nothing about this one, which is joining from here on.
            let mut state = self.shared.state.lock();
            state.database.confirmed = LogPosition::default();
            state.link_state = LinkState::Joining;
        }

        let database = &mut self.database;
        let Some(connections) = database.connections.as_ref() else {
            return Err(Error::other("the database is not open"));
        };

        // Only this thread checkpoints the Zato database, so the database file does not change while it is sent,
        // and a commit restarts the log only once every frame of it is in that file. Frames committed after
        // the recorded end reach the standby with the frames that follow the snapshot.
        let _ = scan_to_end(&mut database.cursor, &connections.checkpoint)?;

        sender.send(&Message::SnapshotBegin { generation }, timeout)?;
        let database_file = SnapshotFile {
            kind: FileKind::Database,
            path: &database.path,
            length: None,
        };
        send_file(sender, &database_file, timeout)?;

        let header = database.cursor.header().map(|header| header.raw.to_vec());
        if let Some(wal_header) = database.cursor.header() {
            let length = wal_header.frame_offset(database.cursor.end_frame());
            let wal_path = wal::wal_path(&database.path);
            let wal_file = SnapshotFile {
                kind: FileKind::Wal,
                path: &wal_path,
                length: Some(length),
            };
            send_file(sender, &wal_file, timeout)?;
        }
        sender.send(&Message::SnapshotEnd, timeout)?;
        Ok(SessionDatabase {
            header,
            sent: database.end(),
        })
    }
}

#[cfg(test)]
mod tests;

#[cfg(test)]
mod snapshot_tests;
