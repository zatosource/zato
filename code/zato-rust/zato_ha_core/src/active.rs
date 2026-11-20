// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The opening end of the replication link on the active node.
//!
//! One thread, the shipper, reads the log of the Zato database, records its end for the barrier, ships the new
//! frames to the standby, sends a snapshot to a standby that joins, admits a standby that caught up, and checkpoints
//! the log. A second thread per session receives the confirmations, and a third sends the heartbeats.

use std::fs::File;
use std::io::{Error, ErrorKind, Read};
use std::os::unix::fs::FileExt;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use rusqlite::Connection;
use rusqlite::config::DbConfig;

use crate::clock;
use crate::link::{LinkReceiver, LinkSender};
use crate::protocol::{FileKind, Message, Position};
use crate::record::RefereeRecord;
use crate::referee::{Transition, transition};
use crate::state::{CycleRecord, LinkState, LogPosition, NodeState, Role, Shared};
use crate::wal::{self, MAX_SCAN_BYTES, ScanOutcome, WalCursor};

/// How often the log is read when no barrier asks for it, which keeps the standby close to the active node.
const POLL_INTERVAL: Duration = Duration::from_millis(20);

/// How often a link to the standby is attempted while there is none.
const CONNECT_INTERVAL: Duration = Duration::from_secs(1);

/// The size of one chunk of a snapshot.
const SNAPSHOT_CHUNK_SIZE: usize = 1024 * 1024;

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
    /// Takes the write lock during a checkpoint and a snapshot.
    lock: Connection,

    /// Runs the checkpoint while the write lock is held by `lock`.
    checkpoint: Connection,
}

/// Returns a busy handler that tries to take the write lock again at a short fixed interval, until `LOCK_BUSY_TIMEOUT` elapses.
///
/// The busy handler of SQLite sleeps longer after each attempt, up to a tenth of a second, while the writers
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

        // Under the write lock, no frame is appended while the end of the log is recorded,
        // and with no checkpoint running, neither file changes below that end afterwards.
        // Writers wait at their barriers until the lock is taken, so that their commits leave it free ..
        self.shared.state.lock().taking_snapshot_lock = true;
        let locked = connections.lock.execute_batch("begin immediate");

        // .. and they go on once it is taken or the attempt gives up.
        self.shared.state.lock().taking_snapshot_lock = false;
        self.shared.changed.notify_all();
        locked.map_err(Error::other)?;
        let scanned = scan_to_end(&mut database.cursor, &connections.checkpoint);
        connections.lock.execute_batch("rollback").map_err(Error::other)?;
        let _ = scanned?;

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

    /// Admits a joining standby once it confirmed the end of the log.
    fn admit_if_caught_up(&mut self) -> Result<(), Error> {
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
    fn resolve_abandoned_admission(&self) {
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

    /// Checkpoints the log once it exceeds the size limit.
    fn checkpoint_if_due(&mut self) -> Result<(), Error> {
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

/// The committed frames one scan returned, in the order they were read.
#[derive(Debug, Clone)]
struct FreshFrames {
    /// The cycle the frames belong to.
    cycle: u64,

    /// The index of the first frame.
    first_frame: u32,

    /// The index after the last frame.
    end_frame: u32,

    /// The raw frames.
    bytes: Vec<u8>,
}

/// Reads a log until no new committed frame remains, using `connection` to settle its shared-memory index.
fn scan_to_end(cursor: &mut WalCursor, connection: &Connection) -> Result<Vec<FreshFrames>, Error> {
    let mut out = Vec::new();
    loop {
        let outcome = cursor.scan().map_err(Error::other)?;
        let cycle = cursor.cycle();
        match outcome {
            ScanOutcome::Unchanged => return Ok(out),

            // A read of the database waits for the writer that is updating the header of the index, or rebuilds
            // the index that a stopped writer left half-written, and the scan is repeated after it.
            ScanOutcome::Unsettled => {
                let _: i64 = connection
                    .query_row("select count(*) from sqlite_master", [], |row| row.get(0))
                    .map_err(Error::other)?;
            }
            ScanOutcome::Frames(frames) | ScanOutcome::Restarted { frames, .. } => out.push(FreshFrames {
                cycle,
                first_frame: frames.first_frame,
                end_frame: frames.end_frame,
                bytes: frames.bytes,
            }),
        }
    }
}

/// Returns the messages that bring the standby from `sent` towards the end of the log, at most one chunk of it,
/// and advances `sent`.
fn frames_to_send(database: &Database, sent: &mut SessionDatabase, fresh: &[FreshFrames], generation: u64) -> Result<Vec<Message>, Error> {
    let mut out = Vec::new();
    let Some(header) = database.cursor.header() else {
        return Ok(out);
    };
    let end = database.end();

    // The standby holds an earlier cycle, which it holds whole, so the current one is sent from its first frame.
    let is_new_cycle = sent.header.as_deref() != Some(&header.raw[..]);
    let start = if is_new_cycle { 0 } else { sent.sent.frame };
    if !is_new_cycle && start >= end.frame {
        return Ok(out);
    }

    // One call sends at most one chunk of a long backlog, so that each iteration completes its scan for the barrier
    // without waiting for the whole backlog to be sent.
    let send_end = end.frame.min(start.saturating_add(frames_per_chunk(header)?));

    // The frames of the most recent scan are sent as they were read, and anything older is read again from the log.
    let fresh_match = fresh
        .iter()
        .find(|frames| frames.cycle == end.cycle && frames.first_frame == start && frames.end_frame == send_end);
    let chunks = match fresh_match {
        Some(frames) => vec![(frames.first_frame, frames.end_frame, frames.bytes.clone())],
        None => read_frames(&database.path, header, start, send_end)?,
    };

    let mut header_to_send = if is_new_cycle { Some(header.raw.to_vec()) } else { None };
    if chunks.is_empty() && header_to_send.is_some() {
        out.push(Message::Frames {
            generation,
            header: header_to_send.take(),
            first_frame: 0,
            end_frame: 0,
            bytes: Vec::new(),
        });
    }
    for (first_frame, end_frame, bytes) in chunks {
        out.push(Message::Frames {
            generation,
            header: header_to_send.take(),
            first_frame,
            end_frame,
            bytes,
        });
    }

    sent.header = Some(header.raw.to_vec());
    sent.sent = LogPosition {
        cycle: end.cycle,
        frame: send_end,
    };
    Ok(out)
}

/// How many frames of a log one chunk holds at most.
fn frames_per_chunk(header: &wal::WalHeader) -> Result<u32, Error> {
    let max_bytes = u64::try_from(MAX_SCAN_BYTES).map_err(Error::other)?;
    u32::try_from((max_bytes / header.frame_size()).max(1)).map_err(Error::other)
}

/// Reads the frames `start..end` of a log in chunks of a bounded size.
fn read_frames(db_path: &Path, header: &wal::WalHeader, start: u32, end: u32) -> Result<Vec<(u32, u32, Vec<u8>)>, Error> {
    let mut out = Vec::new();
    if start >= end {
        return Ok(out);
    }
    let file = File::open(wal::wal_path(db_path))?;
    let frame_size = header.frame_size();
    let frames_per_chunk = frames_per_chunk(header)?;

    let mut first = start;
    while first < end {
        let last = end.min(first.saturating_add(frames_per_chunk));
        let length = usize::try_from(u64::from(last - first) * frame_size).map_err(Error::other)?;
        let mut bytes = vec![0_u8; length];
        file.read_exact_at(&mut bytes, header.frame_offset(first))?;
        out.push((first, last, bytes));
        first = last;
    }
    Ok(out)
}

/// One file of a snapshot.
struct SnapshotFile<'snapshot> {
    /// Which file of the database it is.
    kind: FileKind,

    /// The path of the file.
    path: &'snapshot Path,

    /// How many bytes from its beginning are sent, or `None` for the whole file.
    length: Option<u64>,
}

/// Sends a file of a snapshot in chunks.
fn send_file(sender: &LinkSender, snapshot_file: &SnapshotFile<'_>, timeout: Duration) -> Result<(), Error> {
    let file = match File::open(snapshot_file.path) {
        Ok(file) => file,

        // A file that does not exist is sent as an empty one.
        Err(error) if error.kind() == ErrorKind::NotFound => return Ok(()),
        Err(error) => return Err(error),
    };
    let mut reader: Box<dyn Read> = match snapshot_file.length {
        Some(limit) => Box::new(file.take(limit)),
        None => Box::new(file),
    };
    let mut chunk = vec![0_u8; SNAPSHOT_CHUNK_SIZE];
    loop {
        let count = reader.read(&mut chunk)?;
        if count == 0 {
            return Ok(());
        }
        let bytes = chunk.get(..count).ok_or_else(|| Error::other("read past the buffer"))?.to_vec();
        sender.send(
            &Message::SnapshotChunk {
                kind: snapshot_file.kind,
                bytes,
            },
            timeout,
        )?;
    }
}

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
fn record_clock_skew(shared: &Shared, state: &mut NodeState, clock_skew_ms: u64) {
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
fn receive_loop(shared: &Shared, mut receiver: LinkReceiver, number: u64) {
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
fn start_session_threads(shared: &Arc<Shared>, receiver: LinkReceiver, sender: LinkSender, number: u64) {
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

#[cfg(test)]
mod tests;
