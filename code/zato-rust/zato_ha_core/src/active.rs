// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The opening end of the replication link on the active node.
//!
//! One thread, the shipper, reads every log, records the end of each for the barrier, ships the new frames
//! to the standby, sends snapshots to a standby that joins, admits a standby that caught up, and checkpoints
//! the logs. A second thread per session receives the confirmations, and a third sends the heartbeats.

use std::fs::File;
use std::io::{Error, ErrorKind, Read};
use std::os::unix::fs::FileExt;
use std::path::Path;
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use rusqlite::Connection;
use rusqlite::config::DbConfig;

use crate::config::{DatabaseConfig, ShippingMode};
use crate::link::{LinkReceiver, LinkSender};
use crate::protocol::{FileKind, Message, Position};
use crate::record::RefereeRecord;
use crate::referee::{Transition, transition};
use crate::state::{CycleRecord, LinkState, LogPosition, NodeState, Role, Shared};
use crate::wal::{self, MAX_SCAN_BYTES, ScanOutcome, WalCursor};

/// How often the logs are read when no barrier asks for it, which keeps the standby close to the active node.
const POLL_INTERVAL: Duration = Duration::from_millis(20);

/// How often a link to the standby is attempted while there is none.
const CONNECT_INTERVAL: Duration = Duration::from_secs(1);

/// The size of one chunk of a snapshot.
const SNAPSHOT_CHUNK_SIZE: usize = 1024 * 1024;

/// The size above which a log is checkpointed.
const CHECKPOINT_WAL_SIZE: u64 = 64 * 1024 * 1024;

/// How long the node's own connections wait for the write lock of a database.
const LOCK_BUSY_TIMEOUT: Duration = Duration::from_secs(5);

/// The connections the node keeps open to one database while it is active.
///
/// Keeping a connection open means no connection of the Zato server is ever the last one to close,
/// which would checkpoint and delete the log.
struct DatabaseConnections {
    /// Takes the write lock during a checkpoint and a snapshot.
    lock: Connection,

    /// Runs the checkpoint while the write lock is held by `lock`.
    checkpoint: Connection,
}

/// Opens a connection that never checkpoints by itself.
fn open_connection(path: &Path) -> Result<Connection, Error> {
    let connection = Connection::open(path).map_err(Error::other)?;
    let _ = connection
        .set_db_config(DbConfig::SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, true)
        .map_err(Error::other)?;
    connection.busy_timeout(LOCK_BUSY_TIMEOUT).map_err(Error::other)?;
    let _: String = connection
        .query_row("pragma journal_mode=wal", [], |row| row.get(0))
        .map_err(Error::other)?;
    connection.pragma_update(None, "wal_autocheckpoint", 0).map_err(Error::other)?;
    Ok(connection)
}

/// One replicated database as the shipper sees it.
struct Database {
    /// Its configuration.
    config: DatabaseConfig,

    /// The cursor whose end every barrier and every session refers to.
    cursor: WalCursor,

    /// The node's connections, opened while the node is active.
    connections: Option<DatabaseConnections>,
}

impl Database {
    /// Returns a database nothing was read from.
    fn new(config: &DatabaseConfig) -> Self {
        Self {
            cursor: WalCursor::new(wal::wal_path(&config.path)),
            config: config.clone(),
            connections: None,
        }
    }

    /// Opens the node's connections, creating the database if it does not exist.
    fn open(&mut self) -> Result<(), Error> {
        if self.connections.is_some() {
            return Ok(());
        }
        if let Some(parent) = self.config.path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let lock = open_connection(&self.config.path)?;
        let checkpoint = open_connection(&self.config.path)?;
        self.connections = Some(DatabaseConnections { lock, checkpoint });

        // A log read under another role describes files that may have been replaced since.
        self.cursor = WalCursor::new(wal::wal_path(&self.config.path));
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

/// What a session has sent of one database.
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

    /// What was sent of each database, in the order of the configuration.
    databases: Vec<SessionDatabase>,

    /// Whether the standby is joining, as opposed to being in sync.
    joining: bool,

    /// The name of the standby.
    peer: String,
}

/// The shipper thread.
pub struct Shipper {
    /// The shared state.
    shared: Arc<Shared>,

    /// The replicated databases.
    databases: Vec<Database>,

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
        let databases = shared.config.databases.iter().map(Database::new).collect();
        Self {
            shared,
            databases,
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
        for database in &mut self.databases {
            database.connections = None;
        }

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

        for database in &mut self.databases {
            database.open()?;
        }

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

    /// Reads every log to its end, ships what the session has not sent yet and completes the scan for the barrier.
    fn scan_and_ship(&mut self, ticket: u64) -> Result<(), Error> {
        let mut fresh = Vec::new();
        for database in &mut self.databases {
            fresh.push(scan_to_end(&mut database.cursor)?);
        }

        // The standby in sync owes the frames from the moment they are read, whether or not a session can ship them.
        self.record_reads();
        self.ship(&fresh)?;

        let mut state = self.shared.state.lock();
        for database in &self.databases {
            let end = database.end();
            let record = database.cycle_record();
            if let Some(progress) = state.database_mut(database.config.name) {
                progress.scanned = end;
                if let Some(record) = record {
                    progress.record_cycle(record);
                }
            }
        }
        state.scan_completed = state.scan_completed.max(ticket);
        drop(state);
        self.shared.changed.notify_all();
        Ok(())
    }

    /// Records the end of every log as read and not yet confirmed while a standby is in sync.
    fn record_reads(&self) {
        let read_at = Instant::now();
        let mut state = self.shared.state.lock();

        // Without a standby in sync, no barrier waits for a confirmation.
        if state.role != Role::ActiveReplicated {
            return;
        }
        for database in &self.databases {
            if let Some(progress) = state.database_mut(database.config.name) {
                progress.record_read(database.end(), read_at);
            }
        }
    }

    /// Sends the next chunk of the frames of each database that the session, if any, has not sent yet.
    fn ship(&mut self, fresh: &[Vec<FreshFrames>]) -> Result<(), Error> {
        let Some(session) = self.session.as_mut() else {
            return Ok(());
        };
        let generation = self.shared.state.lock().generation;
        let timeout = self.shared.config.timers.mark_out;

        for ((database, sent), fresh_frames) in self.databases.iter().zip(session.databases.iter_mut()).zip(fresh) {
            for message in frames_to_send(database, sent, fresh_frames, generation)? {
                session.sender.send(&message, timeout)?;
            }
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
            },
            timeout,
        )?;

        let (reply, receiver) = receiver.receive()?;
        let (in_sync, positions) = match reply {
            Message::HelloReply { in_sync, positions } => (in_sync, positions),
            Message::Refused { generation: higher } => {
                self.shared.fence(&mut self.shared.state.lock(), higher);
                return Ok(());
            }
            other => return Err(Error::new(ErrorKind::InvalidData, format!("unexpected answer {other:?}"))),
        };

        let number = {
            let mut state = self.shared.state.lock();
            state.session += 1;
            state.session
        };

        let session = if role == Role::ActiveReplicated {
            if !in_sync {
                // The record names this standby as in sync, so it may not join before it is marked out.
                self.request_mark_out(&peer.node_name, "the standby is not in sync");
                sender.close();
                return Ok(());
            }
            let Some(databases) = self.resume_positions(&positions) else {
                self.request_mark_out(&peer.node_name, "the standby cannot resume from its positions");
                sender.close();
                return Ok(());
            };
            Session {
                sender: sender.clone(),
                number,
                databases,
                joining: false,
                peer: peer.node_name.clone(),
            }
        } else {
            let databases = match self.send_snapshots(&sender, generation) {
                Ok(databases) => databases,
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
                databases,
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

    /// Returns what the standby holds of each database, if it can resume from its positions.
    fn resume_positions(&self, positions: &[Position]) -> Option<Vec<SessionDatabase>> {
        let progress_list = self.shared.state.lock().databases.clone();
        let mut out = Vec::new();

        for database in &self.databases {
            let position = positions.iter().find(|position| position.database == database.config.name)?;
            let progress = progress_list.iter().find(|progress| progress.name == database.config.name)?;

            // A standby without a log can resume only while the active node has none either.
            if position.salt_one == 0 && position.salt_two == 0 && position.end_frame == 0 {
                if database.cursor.header().is_some() {
                    return None;
                }
                out.push(SessionDatabase {
                    header: None,
                    sent: LogPosition::default(),
                });
                continue;
            }

            let record = progress.cycle_of(position.salt_one, position.salt_two)?;
            let is_current = record.cycle == database.cursor.cycle();

            // The standby holds a prefix of the current cycle, or the whole of the previous one.
            let holds_prefix = is_current && position.end_frame <= database.cursor.end_frame();
            let holds_previous = !is_current && position.end_frame == record.end_frame;
            if !holds_prefix && !holds_previous {
                return None;
            }

            let header = if is_current {
                database.cursor.header().map(|header| header.raw.to_vec())
            } else {
                None
            };
            out.push(SessionDatabase {
                header,
                sent: LogPosition {
                    cycle: record.cycle,
                    frame: position.end_frame,
                },
            });
        }
        Some(out)
    }

    /// Sends the files of every database to a joining standby and returns what it then holds.
    fn send_snapshots(&mut self, sender: &LinkSender, generation: u64) -> Result<Vec<SessionDatabase>, Error> {
        let timeout = self.shared.config.timers.mark_out;
        let mut out = Vec::new();

        {
            // What an earlier standby confirmed says nothing about this one, which is joining from here on.
            let mut state = self.shared.state.lock();
            for progress in &mut state.databases {
                progress.confirmed = LogPosition::default();
            }
            state.link_state = LinkState::Joining;
        }

        for database in &mut self.databases {
            let Some(connections) = database.connections.as_ref() else {
                return Err(Error::other("the database is not open"));
            };

            // Under the write lock, no frame is appended while the end of the log is recorded,
            // and with no checkpoint running, neither file changes below that end afterwards.
            connections.lock.execute_batch("begin immediate").map_err(Error::other)?;
            let scanned = scan_to_end(&mut database.cursor);
            connections.lock.execute_batch("rollback").map_err(Error::other)?;
            let _ = scanned?;

            let name = database.config.name.to_owned();
            sender.send(
                &Message::SnapshotBegin {
                    generation,
                    database: name.clone(),
                },
                timeout,
            )?;
            let database_file = SnapshotFile {
                database: &name,
                kind: FileKind::Database,
                path: &database.config.path,
                length: None,
            };
            send_file(sender, &database_file, timeout)?;

            let header = database.cursor.header().map(|header| header.raw.to_vec());
            if let Some(wal_header) = database.cursor.header() {
                let length = wal_header.frame_offset(database.cursor.end_frame());
                let wal_path = wal::wal_path(&database.config.path);
                let wal_file = SnapshotFile {
                    database: &name,
                    kind: FileKind::Wal,
                    path: &wal_path,
                    length: Some(length),
                };
                send_file(sender, &wal_file, timeout)?;
            }
            sender.send(&Message::SnapshotEnd { database: name }, timeout)?;
            out.push(SessionDatabase {
                header,
                sent: database.end(),
            });
        }
        Ok(out)
    }

    /// Admits a joining standby once it confirmed the end of every log.
    fn admit_if_caught_up(&mut self) -> Result<(), Error> {
        let Some(session) = self.session.as_ref().filter(|session| session.joining) else {
            self.resolve_abandoned_admission();
            return Ok(());
        };

        let Some(generation) = admission_generation(&self.shared, &self.databases, session, &mut self.admission_started) else {
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

    /// Checkpoints every log that exceeds the size limit.
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

        for index in 0..self.databases.len() {
            let Some(database) = self.databases.get(index) else {
                continue;
            };
            let end = database.end();

            // The standby confirms a log only once all of it was sent, which a long backlog takes several iterations for,
            // and a checkpoint would hold the write lock while it waited.
            let has_backlog = self
                .session
                .as_ref()
                .and_then(|session| session.databases.get(index))
                .is_some_and(|sent| sent.sent < end);
            if database.is_long() && !has_backlog {
                self.checkpoint(index, role)?;
            }
        }
        Ok(())
    }

    /// Checkpoints one log under its write lock, after the standby confirmed every frame of it.
    fn checkpoint(&mut self, index: usize, role: Role) -> Result<(), Error> {
        {
            let Some(connections) = self.databases.get(index).and_then(|database| database.connections.as_ref()) else {
                return Ok(());
            };

            // A writer holding the lock longer than the busy timeout only postpones the checkpoint.
            if connections.lock.execute_batch("begin immediate").is_err() {
                return Ok(());
            }
        }

        let outcome = self.checkpoint_under_lock(index, role);

        if let Some(connections) = self.databases.get(index).and_then(|database| database.connections.as_ref()) {
            connections.lock.execute_batch("rollback").map_err(Error::other)?;
        }
        outcome
    }

    /// Ships and confirms every frame, then checkpoints, while the write lock is held.
    fn checkpoint_under_lock(&mut self, index: usize, role: Role) -> Result<(), Error> {
        let ticket = self.shared.state.lock().scan_requested;
        self.scan_and_ship(ticket)?;

        let Some(database) = self.databases.get(index) else {
            return Ok(());
        };

        // A log that restarted since the previous scan is short again, and checkpointing it would only restart it once more.
        if !database.is_long() {
            return Ok(());
        }
        let name = database.config.name;
        let end = database.end();

        if role == Role::ActiveReplicated {
            let deadline = Instant::now() + self.shared.config.timers.mark_out;
            let mut state = self.shared.state.lock();
            loop {
                let confirmed = state
                    .databases
                    .iter()
                    .find(|progress| progress.name == name)
                    .map(|progress| progress.confirmed);
                if confirmed.is_some_and(|confirmed| confirmed >= end) {
                    break;
                }

                // A standby that does not confirm in time is marked out by the control loop, and the checkpoint waits.
                if state.role != Role::ActiveReplicated || Instant::now() >= deadline {
                    tracing::warn!("Checkpoint of {name} postponed, the standby confirmed {confirmed:?} of {end:?}");
                    return Ok(());
                }
                let _ = self.shared.changed.wait_until(&mut state, deadline);
            }
            drop(state);
        }

        if let Some(connections) = database.connections.as_ref() {
            let (busy, log_frames, checkpointed): (i64, i64, i64) = connections
                .checkpoint
                .query_row("pragma wal_checkpoint(passive)", [], |row| {
                    Ok((row.get(0)?, row.get(1)?, row.get(2)?))
                })
                .map_err(Error::other)?;
            tracing::debug!("Checkpoint of {name}: busy {busy}, log frames {log_frames}, checkpointed {checkpointed}");
        }
        Ok(())
    }
}

/// Returns the generation at which the joining standby of `session` is admitted, once it confirmed
/// the end of every synchronous log while the barriers were held.
///
/// Under steady writes, new frames are read before the standby confirms the previous ones, so the barriers
/// are held from the moment everything read was sent, which stops the writers until the standby confirms it.
fn admission_generation(shared: &Shared, databases: &[Database], session: &Session, admission_started: &mut Instant) -> Option<u64> {
    let mut state = shared.state.lock();
    if state.role != Role::ActiveSolo {
        return None;
    }

    if !state.admitting {
        // The copy of an asynchronous database may lag behind, so only the synchronous ones decide.
        let all_sent = databases
            .iter()
            .zip(&session.databases)
            .filter(|(database, _)| database.config.shipping == ShippingMode::Synchronous)
            .all(|(database, sent)| sent.sent >= database.end());

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

    let caught_up = state
        .databases
        .iter()
        .filter(|progress| progress.shipping == ShippingMode::Synchronous)
        .all(|progress| progress.confirmed >= progress.scanned);
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

/// Reads a log until no new committed frame remains.
fn scan_to_end(cursor: &mut WalCursor) -> Result<Vec<FreshFrames>, Error> {
    let mut out = Vec::new();
    loop {
        let outcome = cursor.scan().map_err(Error::other)?;
        let cycle = cursor.cycle();
        match outcome {
            ScanOutcome::Unchanged => return Ok(out),
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
    let name = database.config.name.to_owned();

    // The standby holds an earlier cycle, which it holds whole, so the current one is sent from its first frame.
    let is_new_cycle = sent.header.as_deref() != Some(&header.raw[..]);
    let start = if is_new_cycle { 0 } else { sent.sent.frame };
    if !is_new_cycle && start >= end.frame {
        return Ok(out);
    }

    // One call sends at most one chunk of a long backlog, so that the frames of the other databases do not wait behind it.
    let send_end = end.frame.min(start.saturating_add(frames_per_chunk(header)?));

    // The frames of the most recent scan are sent as they were read, and anything older is read again from the log.
    let fresh_match = fresh
        .iter()
        .find(|frames| frames.cycle == end.cycle && frames.first_frame == start && frames.end_frame == send_end);
    let chunks = match fresh_match {
        Some(frames) => vec![(frames.first_frame, frames.end_frame, frames.bytes.clone())],
        None => read_frames(&database.config.path, header, start, send_end)?,
    };

    let mut header_to_send = if is_new_cycle { Some(header.raw.to_vec()) } else { None };
    if chunks.is_empty() && header_to_send.is_some() {
        out.push(Message::Frames {
            generation,
            database: name.clone(),
            header: header_to_send.take(),
            first_frame: 0,
            end_frame: 0,
            bytes: Vec::new(),
        });
    }
    for (first_frame, end_frame, bytes) in chunks {
        out.push(Message::Frames {
            generation,
            database: name.clone(),
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
    /// The name of the database.
    database: &'snapshot str,

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
                database: snapshot_file.database.to_owned(),
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
    let Some(progress) = state.database_mut(&position.database) else {
        return;
    };
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
            Message::HeartbeatAck => {}
            Message::Refused { generation } => {
                shared.fence(&mut state, generation);
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
        if let Err(error) = sender.send(&Message::Heartbeat { generation }, shared.config.timers.mark_out) {
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
mod tests {
    use super::*;
    use crate::barrier::{self, BarrierOutcome};
    use crate::config::{DB_NAME_PUBSUB, Timers};
    use crate::link::TlsContext;
    use crate::record::NodeAddress;
    use crate::referee::tests::MemoryReferee;
    use crate::test_support::{self, Certificates, LOOPBACK, NODE_A, NODE_B};
    use std::collections::HashMap;
    use std::collections::hash_map::Entry;
    use std::net::TcpListener;
    use std::sync::mpsc;

    /// Rows that make the database file larger than the socket buffers, so that sending it blocks
    /// for as long as the standby does not read.
    const BULK_ROWS: usize = 1024;

    /// The size of each of these rows.
    const BULK_ROW_SIZE: usize = 64 * 1024;

    /// Timers that do not expire during a test.
    const TIMERS: Timers = Timers {
        heartbeat: Duration::from_millis(500),
        mark_out: Duration::from_mins(1),
        takeover: Duration::from_mins(2),
    };

    /// How long a test waits for a message of the link.
    const RECEIVE_TIMEOUT: Duration = Duration::from_secs(30);

    /// The body of the publication acknowledged while the snapshot is being sent.
    const PUBLICATION: &[u8] = b"acknowledged-publication";

    /// The report of the frames of the publish/subscribe database.
    const PUBSUB_FRAMES: &str = "frames of pubsub";

    /// The report of an admission.
    const ADMIT: &str = "admit";

    /// Rows whose frames make the log longer than the length at which it is checkpointed.
    const LONG_LOG_ROWS: usize = 1100;

    /// How many small transactions follow the checkpoint of the long log.
    const SMALL_WRITES: usize = 5;

    /// How long a test lets the shipper run after each write.
    const SHIPPER_ITERATIONS: Duration = Duration::from_millis(200);

    /// How many threads of a test commit at once, each waiting at the barrier after every commit as a worker of the Zato server does.
    const WRITERS: usize = 8;

    /// How long the standby of a test takes to sync each message of frames before it confirms it.
    const STANDBY_SYNC: Duration = Duration::from_millis(20);

    /// How long a standby that keeps pace with the writers may take to be admitted.
    const ADMISSION_TIMEOUT: Duration = Duration::from_secs(3);

    /// Fills the publish/subscribe database in its main file and leaves it without a log, as a checkpoint does.
    fn fill_database(path: &Path) {
        let connection = Connection::open(path).unwrap();
        connection
            .execute_batch("pragma journal_mode=delete; create table message (body blob); begin;")
            .unwrap();
        let body = vec![0_u8; BULK_ROW_SIZE];
        for _ in 0..BULK_ROWS {
            let _ = connection.execute("insert into message (body) values (?1)", [&body]).unwrap();
        }
        connection.execute_batch("commit").unwrap();
    }

    /// The channels between a test and the standby it plays.
    struct StandbyChannels {
        /// Told once the first message of the snapshot arrived, after which nothing is read until `resume`.
        paused: mpsc::Sender<()>,

        /// Tells the standby to read again.
        resume: mpsc::Receiver<()>,

        /// Receives the frames of the publish/subscribe database and the admissions, in the order they arrive.
        reports: mpsc::Sender<&'static str>,
    }

    /// Plays a standby that answers the Hello and confirms nothing.
    fn run_standby(listener: &TcpListener, tls: &TlsContext, channels: &StandbyChannels) {
        let (tcp, _) = listener.accept().unwrap();
        let accepted = tls.accept(tcp).unwrap();
        let (_, mut receiver) = accepted.receiver.receive().unwrap();
        let reply = Message::HelloReply {
            in_sync: false,
            positions: Vec::new(),
        };
        accepted.sender.send(&reply, RECEIVE_TIMEOUT).unwrap();

        let mut paused = false;
        while let Ok((message, next)) = receiver.receive() {
            receiver = next;
            if !paused {
                paused = true;
                channels.paused.send(()).unwrap();
                channels.resume.recv().unwrap();
            }
            let report = match message {
                Message::Frames { database, .. } if database == DB_NAME_PUBSUB => PUBSUB_FRAMES,
                Message::Admit { .. } => ADMIT,
                _ => continue,
            };
            if channels.reports.send(report).is_err() {
                return;
            }
        }
    }

    /// Plays a standby that confirms every message of frames once it synced it.
    fn run_confirming_standby(listener: &TcpListener, tls: &TlsContext) {
        let (tcp, _) = listener.accept().unwrap();
        let accepted = tls.accept(tcp).unwrap();
        let (_, mut receiver) = accepted.receiver.receive().unwrap();
        let reply = Message::HelloReply {
            in_sync: false,
            positions: Vec::new(),
        };
        accepted.sender.send(&reply, RECEIVE_TIMEOUT).unwrap();

        // The salts of each log, read from the start of its file in the snapshot or from the header of a new cycle.
        let mut salts: HashMap<String, (u32, u32)> = HashMap::new();
        while let Ok((message, next)) = receiver.receive() {
            receiver = next;
            let confirmation = match message {
                Message::SnapshotChunk {
                    database,
                    kind: FileKind::Wal,
                    bytes,
                } => {
                    if let Entry::Vacant(entry) = salts.entry(database) {
                        let header = wal::WalHeader::parse(bytes.get(..wal::HEADER_SIZE).unwrap().try_into().unwrap()).unwrap();
                        let _ = entry.insert((header.salt_one, header.salt_two));
                    }
                    continue;
                }
                Message::Frames {
                    database,
                    header,
                    end_frame,
                    ..
                } => {
                    if let Some(raw) = header {
                        let header = wal::WalHeader::parse(raw[..].try_into().unwrap()).unwrap();
                        let _ = salts.insert(database.clone(), (header.salt_one, header.salt_two));
                    }
                    let (salt_one, salt_two) = *salts.get(&database).unwrap();
                    thread::sleep(STANDBY_SYNC);
                    Message::Confirm(Position {
                        database,
                        salt_one,
                        salt_two,
                        end_frame,
                    })
                }
                Message::Heartbeat { .. } => Message::HeartbeatAck,
                _ => continue,
            };

            // A link that the active node closed ends the standby.
            if accepted.sender.send(&confirmation, RECEIVE_TIMEOUT).is_err() {
                return;
            }
        }
    }

    /// Returns the shared state of node A, active alone at generation 1, with node B listening on `port`.
    fn active_node(dir: &Path, certificates: &Certificates, port: u16) -> Arc<Shared> {
        let config = test_support::node_config(NODE_A, dir, certificates, TIMERS);
        let referee = MemoryReferee::holding(Some(RefereeRecord::solo(1, NODE_A)), 1);
        referee.addresses.lock().push(NodeAddress {
            node_name: NODE_B.to_owned(),
            host: LOOPBACK.to_owned(),
            port,
        });
        let shared = test_support::shared(config, Box::new(referee));
        {
            let mut state = shared.state.lock();
            state.role = Role::ActiveSolo;
            state.generation = 1;
        }
        shared
    }

    #[test]
    fn a_publication_acknowledged_during_a_join_reaches_the_standby_before_its_admission() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let pubsub_path = dir.path().join("pubsub.db");
        fill_database(&pubsub_path);

        let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
        let shared = active_node(dir.path(), &certificates, listener.local_addr().unwrap().port());

        let (paused_sender, paused) = mpsc::channel();
        let (resume_sender, resume) = mpsc::channel();
        let (reports_sender, reports) = mpsc::channel();
        let channels = StandbyChannels {
            paused: paused_sender,
            resume,
            reports: reports_sender,
        };
        let standby_tls = TlsContext::load(&certificates.files(NODE_B)).unwrap();
        let standby = thread::spawn(move || run_standby(&listener, &standby_tls, &channels));
        let shipper_shared = Arc::clone(&shared);
        let shipper = thread::spawn(move || Shipper::new(shipper_shared).run());

        // The shipper recorded the end of every log and is blocked sending the database file.
        paused.recv_timeout(RECEIVE_TIMEOUT).unwrap();
        let connection = Connection::open(&pubsub_path).unwrap();
        connection.busy_timeout(RECEIVE_TIMEOUT).unwrap();
        let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
        assert_eq!(barrier::wait(&shared, DB_NAME_PUBSUB), BarrierOutcome::Synced);
        resume_sender.send(()).unwrap();

        // The standby confirms nothing, so the frames of the publication arrive and no admission follows them.
        let first = reports.recv_timeout(RECEIVE_TIMEOUT).unwrap();
        assert_eq!(first, PUBSUB_FRAMES);

        shared.announce_stop();
        shipper.join().unwrap();
        standby.join().unwrap();
    }

    #[test]
    fn a_standby_receiving_its_backup_is_reported_as_joining() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        fill_database(&dir.path().join("pubsub.db"));

        let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
        let shared = active_node(dir.path(), &certificates, listener.local_addr().unwrap().port());

        let (paused_sender, paused) = mpsc::channel();
        let (resume_sender, resume) = mpsc::channel();
        let (reports_sender, _reports) = mpsc::channel();
        let channels = StandbyChannels {
            paused: paused_sender,
            resume,
            reports: reports_sender,
        };
        let standby_tls = TlsContext::load(&certificates.files(NODE_B)).unwrap();
        let standby = thread::spawn(move || run_standby(&listener, &standby_tls, &channels));
        let shipper_shared = Arc::clone(&shared);
        let shipper = thread::spawn(move || Shipper::new(shipper_shared).run());

        // The shipper is blocked sending the database file, which the standby does not read yet.
        paused.recv_timeout(RECEIVE_TIMEOUT).unwrap();
        assert_eq!(shared.state.lock().link_state, LinkState::Joining);
        resume_sender.send(()).unwrap();

        shared.announce_stop();
        shipper.join().unwrap();
        standby.join().unwrap();
    }

    /// Returns the cycle of the log of the publish/subscribe database at the most recent scan.
    fn pubsub_cycle(shared: &Shared) -> u64 {
        let state = shared.state.lock();
        state
            .databases
            .iter()
            .find(|progress| progress.name == DB_NAME_PUBSUB)
            .unwrap()
            .scanned
            .cycle
    }

    /// Commits one small transaction and lets the shipper scan it.
    fn write_small(connection: &Connection) {
        let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
        thread::sleep(SHIPPER_ITERATIONS);
    }

    #[test]
    fn a_log_that_restarted_is_not_checkpointed_again_until_its_cycle_is_long() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let pubsub_path = dir.path().join("pubsub.db");
        let connection = Connection::open(&pubsub_path).unwrap();
        connection.busy_timeout(RECEIVE_TIMEOUT).unwrap();
        connection
            .execute_batch("pragma journal_mode=wal; pragma wal_autocheckpoint=0; create table message (body blob); begin;")
            .unwrap();
        let body = vec![0_u8; BULK_ROW_SIZE];
        for _ in 0..LONG_LOG_ROWS {
            let _ = connection.execute("insert into message (body) values (?1)", [&body]).unwrap();
        }
        connection.execute_batch("commit").unwrap();

        // Nothing listens on the port of the standby, so the node stays active alone and checkpoints without a session.
        let port = TcpListener::bind((LOOPBACK, 0)).unwrap().local_addr().unwrap().port();
        let shared = active_node(dir.path(), &certificates, port);
        let shipper_shared = Arc::clone(&shared);
        let shipper = thread::spawn(move || Shipper::new(shipper_shared).run());

        // The first write after the checkpoint of the long log restarts it ..
        let first_cycle = pubsub_cycle(&shared);
        let deadline = Instant::now() + RECEIVE_TIMEOUT;
        while pubsub_cycle(&shared) == first_cycle {
            assert!(Instant::now() < deadline, "The long log was not checkpointed");
            write_small(&connection);
        }

        // .. and the short cycle that follows is not checkpointed, even though the file of the log keeps its length.
        let restarted_cycle = pubsub_cycle(&shared);
        for _ in 0..SMALL_WRITES {
            write_small(&connection);
        }
        assert_eq!(pubsub_cycle(&shared), restarted_cycle);

        shared.announce_stop();
        shipper.join().unwrap();
    }

    /// Commits and waits at the barrier until the node is no longer active alone.
    fn write_while_solo(shared: &Shared, path: &Path) {
        let connection = Connection::open(path).unwrap();
        connection.busy_timeout(RECEIVE_TIMEOUT).unwrap();
        while shared.state.lock().role == Role::ActiveSolo {
            let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
            assert_eq!(barrier::wait(shared, DB_NAME_PUBSUB), BarrierOutcome::Synced);
        }
    }

    #[test]
    fn a_standby_that_keeps_pace_with_steady_writers_is_admitted() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let pubsub_path = dir.path().join("pubsub.db");
        let connection = Connection::open(&pubsub_path).unwrap();
        connection
            .execute_batch("pragma journal_mode=wal; pragma wal_autocheckpoint=0; create table message (body blob);")
            .unwrap();

        let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
        let shared = active_node(dir.path(), &certificates, listener.local_addr().unwrap().port());
        let mut writers = Vec::new();
        for _ in 0..WRITERS {
            let writer_shared = Arc::clone(&shared);
            let writer_path = pubsub_path.clone();
            writers.push(thread::spawn(move || write_while_solo(&writer_shared, &writer_path)));
        }
        let standby_tls = TlsContext::load(&certificates.files(NODE_B)).unwrap();
        let standby = thread::spawn(move || run_confirming_standby(&listener, &standby_tls));
        let shipper_shared = Arc::clone(&shared);
        let shipper = thread::spawn(move || Shipper::new(shipper_shared).run());

        let deadline = Instant::now() + ADMISSION_TIMEOUT;
        while shared.state.lock().role != Role::ActiveReplicated {
            assert!(Instant::now() < deadline, "The standby was not admitted");
            thread::sleep(SHIPPER_ITERATIONS);
        }

        // The standby still confirms the commits whose barriers wait for it.
        for writer in writers {
            writer.join().unwrap();
        }
        shared.announce_stop();
        shipper.join().unwrap();
        standby.join().unwrap();
    }

    #[test]
    fn a_standby_in_sync_without_a_session_owes_every_frame_read() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let connection = Connection::open(dir.path().join("pubsub.db")).unwrap();
        connection.busy_timeout(RECEIVE_TIMEOUT).unwrap();
        connection
            .execute_batch("pragma journal_mode=wal; create table message (body blob);")
            .unwrap();

        // Nothing listens on the port of the standby, so no session ever opens.
        let port = TcpListener::bind((LOOPBACK, 0)).unwrap().local_addr().unwrap().port();
        let shared = active_node(dir.path(), &certificates, port);
        shared.state.lock().role = Role::ActiveReplicated;
        let shipper_shared = Arc::clone(&shared);
        let shipper = thread::spawn(move || Shipper::new(shipper_shared).run());

        write_small(&connection);
        let deadline = Instant::now() + RECEIVE_TIMEOUT;
        while shared.state.lock().oldest_unconfirmed().is_none() {
            assert!(Instant::now() < deadline, "The frames read were not recorded as owed");
            thread::sleep(SHIPPER_ITERATIONS);
        }

        shared.announce_stop();
        shipper.join().unwrap();
    }

    #[test]
    fn an_admission_abandoned_after_a_takeover_fences_the_node() {
        let certificates = Certificates::issue();
        let dir = tempfile::tempdir().unwrap();
        let config = test_support::node_config(NODE_A, dir.path(), &certificates, TIMERS);
        let referee = MemoryReferee::holding(Some(RefereeRecord::solo(3, NODE_B)), 3);
        let shared = test_support::shared(config, Box::new(referee));
        {
            let mut state = shared.state.lock();
            state.role = Role::ActiveSolo;
            state.generation = 1;
            state.admitting = true;
            state.pending_admission = Some(RefereeRecord::replicated(2, NODE_A, NODE_B));
        }

        // The admission was written, its answer was lost, and the standby it named in sync took over since.
        Shipper::new(Arc::clone(&shared)).resolve_abandoned_admission();
        let (role, generation) = {
            let state = shared.state.lock();
            (state.role, state.generation)
        };
        assert_eq!((role, generation), (Role::Fenced, 3));
        assert_eq!(barrier::wait(&shared, DB_NAME_PUBSUB), BarrierOutcome::Replaced);
    }
}
