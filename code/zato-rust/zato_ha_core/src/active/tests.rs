// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the shipper - its sessions, snapshots, admissions and checkpoints.

use super::*;
use crate::barrier::{self, BarrierOutcome};
use crate::config::{DATABASE_FILE_NAME, Timers};
use crate::link::TlsContext;
use crate::record::NodeAddress;
use crate::referee::tests::MemoryReferee;
use crate::test_support::{self, Certificates, LOOPBACK, NODE_A, NODE_B};
use parking_lot::Mutex;
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

/// The report of the frames of the Zato database.
const FRAMES: &str = "frames";

/// The report of an admission.
const ADMIT: &str = "admit";

/// Rows whose frames make the log longer than the length at which it is checkpointed.
const LONG_LOG_ROWS: usize = 1100;

/// How many small transactions follow the checkpoint of the long log.
const SMALL_WRITES: usize = 5;

/// Held by each test that writes tens of megabytes to its database and by each test bound by a deadline,
/// so that the writeback of the one does not hold up the commits of the other.
static DISK: Mutex<()> = Mutex::new(());

/// How long the shipper may take to decide on a checkpoint that it does not take the write lock for.
const NO_LOCK_WAIT: Duration = Duration::from_secs(1);

/// How long a test lets the shipper run after each write.
const SHIPPER_ITERATIONS: Duration = Duration::from_millis(200);

/// How many threads of a test commit at once, each waiting at the barrier after every commit as a worker of the Zato server does.
const WRITERS: usize = 8;

/// How long the standby of a test takes to sync each message of frames before it confirms it.
const STANDBY_SYNC: Duration = Duration::from_millis(20);

/// How long a standby that keeps pace with the writers may take to be admitted.
const ADMISSION_TIMEOUT: Duration = Duration::from_secs(3);

/// The skew of the wall clock of a standby whose clock agrees with that of the active node.
const NO_CLOCK_SKEW_MS: u64 = 0;

/// A skew of the wall clock of a standby beyond the default bound.
const LARGE_CLOCK_SKEW_MS: u64 = 5000;

/// Fills the Zato database in its main file and leaves it without a log, as a checkpoint does.
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

    /// Receives the frames of the Zato database and the admissions, in the order they arrive.
    reports: mpsc::Sender<&'static str>,
}

/// Plays a standby that answers the Hello and confirms nothing.
fn run_standby(listener: &TcpListener, tls: &TlsContext, channels: &StandbyChannels) {
    let (tcp, _) = listener.accept().unwrap();
    let accepted = tls.accept(tcp).unwrap();
    let (_, mut receiver) = accepted.receiver.receive().unwrap();
    let reply = Message::HelloReply {
        position: None,
        clock_skew_ms: 0,
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
            Message::Frames { .. } => FRAMES,
            Message::Admit { .. } => ADMIT,
            _ => continue,
        };
        if channels.reports.send(report).is_err() {
            return;
        }
    }
}

/// Returns the position of the end of the log received in a snapshot, as a copy of the Zato database reads it.
fn snapshot_position(log: &[u8]) -> Position {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join(DATABASE_FILE_NAME);
    std::fs::write(wal::wal_path(&path), log).unwrap();
    let mut cursor = WalCursor::new(wal::wal_path(&path));
    while !matches!(cursor.scan().unwrap(), ScanOutcome::Unchanged | ScanOutcome::Unsettled) {}
    let header = cursor.header().unwrap();
    Position {
        salt_one: header.salt_one,
        salt_two: header.salt_two,
        end_frame: cursor.end_frame(),
    }
}

/// Plays a standby that confirms the snapshot and every message of frames once it synced them, reporting a skew of its wall clock.
fn run_confirming_standby(listener: &TcpListener, tls: &TlsContext, clock_skew_ms: u64) {
    let (tcp, _) = listener.accept().unwrap();
    let accepted = tls.accept(tcp).unwrap();
    let (_, mut receiver) = accepted.receiver.receive().unwrap();
    let reply = Message::HelloReply {
        position: None,
        clock_skew_ms,
    };
    accepted.sender.send(&reply, RECEIVE_TIMEOUT).unwrap();

    // The salts of the log, read from its file in the snapshot or from the header of a new cycle.
    let mut salts: Option<(u32, u32)> = None;
    let mut snapshot_log = Vec::new();
    while let Ok((message, next)) = receiver.receive() {
        receiver = next;
        let confirmation = match message {
            Message::SnapshotChunk {
                kind: FileKind::Wal,
                bytes,
            } => {
                snapshot_log.extend_from_slice(&bytes);
                continue;
            }
            Message::SnapshotEnd => {
                let position = snapshot_position(&snapshot_log);
                salts = Some((position.salt_one, position.salt_two));
                thread::sleep(STANDBY_SYNC);
                Message::Confirm(position)
            }
            Message::Frames { header, end_frame, .. } => {
                if let Some(raw) = header {
                    let header = wal::WalHeader::parse(raw[..].try_into().unwrap()).unwrap();
                    salts = Some((header.salt_one, header.salt_two));
                }
                let (salt_one, salt_two) = salts.unwrap();
                thread::sleep(STANDBY_SYNC);
                Message::Confirm(Position {
                    salt_one,
                    salt_two,
                    end_frame,
                })
            }
            Message::Heartbeat { .. } => Message::HeartbeatAck { clock_skew_ms },
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
fn a_refusal_at_the_generation_of_the_node_ends_only_the_session() {
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
    let port = listener.local_addr().unwrap().port();
    let shared = active_node(dir.path(), &certificates, port);

    // The standby refuses frames that the node sent before it wrote the generation of the refusal itself ..
    let standby_tls = TlsContext::load(&certificates.files(NODE_B)).unwrap();
    let standby = thread::spawn(move || {
        let (tcp, _) = listener.accept().unwrap();
        let accepted = standby_tls.accept(tcp).unwrap();
        accepted.sender.send(&Message::Refused { generation: 1 }, RECEIVE_TIMEOUT).unwrap();
        accepted
    });
    let tls = TlsContext::load(&certificates.files(NODE_A)).unwrap();
    let (_sender, receiver) = tls.connect(NODE_B, LOOPBACK, port).unwrap();
    let _accepted = standby.join().unwrap();
    let number = shared.state.lock().session;
    receive_loop(&shared, receiver, number);

    // .. so the node is not fenced and continues active.
    let state = shared.state.lock();
    let role_and_generation = (state.role, state.generation);
    drop(state);
    assert_eq!(role_and_generation, (Role::ActiveSolo, 1));
}

#[test]
fn a_publication_acknowledged_during_a_join_reaches_the_standby_before_its_admission() {
    let _disk = DISK.lock();
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let database_path = dir.path().join(DATABASE_FILE_NAME);
    fill_database(&database_path);

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
    let connection = Connection::open(&database_path).unwrap();
    connection.busy_timeout(RECEIVE_TIMEOUT).unwrap();
    let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
    assert_eq!(barrier::wait(&shared), BarrierOutcome::Synced);
    resume_sender.send(()).unwrap();

    // The standby confirms nothing, so the frames of the publication arrive and no admission follows them.
    let first = reports.recv_timeout(RECEIVE_TIMEOUT).unwrap();
    assert_eq!(first, FRAMES);

    shared.announce_stop();
    shipper.join().unwrap();
    standby.join().unwrap();
}

#[test]
fn a_standby_receiving_its_backup_is_reported_as_joining() {
    let _disk = DISK.lock();
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    fill_database(&dir.path().join(DATABASE_FILE_NAME));

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

/// Returns the cycle of the log of the Zato database at the most recent scan.
fn log_cycle(shared: &Shared) -> u64 {
    shared.state.lock().database.scanned.cycle
}

/// Commits one small transaction and lets the shipper scan it.
fn write_small(connection: &Connection) {
    let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
    thread::sleep(SHIPPER_ITERATIONS);
}

#[test]
fn a_log_that_restarted_is_not_checkpointed_again_until_its_cycle_is_long() {
    let _disk = DISK.lock();
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let database_path = dir.path().join(DATABASE_FILE_NAME);
    let connection = Connection::open(&database_path).unwrap();
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
    let first_cycle = log_cycle(&shared);
    let deadline = Instant::now() + RECEIVE_TIMEOUT;
    while log_cycle(&shared) == first_cycle {
        assert!(Instant::now() < deadline, "The long log was not checkpointed");
        write_small(&connection);
    }

    // .. and the short cycle that follows is not checkpointed, even though the file of the log keeps its length.
    let restarted_cycle = log_cycle(&shared);
    for _ in 0..SMALL_WRITES {
        write_small(&connection);
    }
    assert_eq!(log_cycle(&shared), restarted_cycle);

    shared.announce_stop();
    shipper.join().unwrap();
}

#[test]
fn a_log_whose_every_frame_was_checkpointed_leaves_the_write_lock_to_the_writers() {
    let _disk = DISK.lock();
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let database_path = dir.path().join(DATABASE_FILE_NAME);
    let connection = Connection::open(&database_path).unwrap();
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
    let mut shipper = Shipper::new(Arc::clone(&shared));

    // The first iteration copies every frame of the long log into the database file ..
    shipper.iteration().unwrap();
    assert_eq!(shipper.database.checkpointed, shipper.database.end());

    // .. and while a writer holds the write lock, the next decision does not wait for it.
    connection.execute_batch("begin immediate").unwrap();
    let started = Instant::now();
    shipper.checkpoint_if_due().unwrap();
    let elapsed = started.elapsed();
    connection.execute_batch("rollback").unwrap();

    assert!(elapsed < NO_LOCK_WAIT, "The checkpoint waited {elapsed:?} for the write lock");
}

/// Commits and waits at the barrier until the node is no longer active alone.
fn write_while_solo(shared: &Shared, path: &Path) {
    let connection = Connection::open(path).unwrap();
    connection.busy_timeout(RECEIVE_TIMEOUT).unwrap();
    while shared.state.lock().role == Role::ActiveSolo {
        let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
        assert_eq!(barrier::wait(shared), BarrierOutcome::Synced);
    }
}

#[test]
fn a_standby_that_keeps_pace_with_steady_writers_is_admitted() {
    let _disk = DISK.lock();
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let database_path = dir.path().join(DATABASE_FILE_NAME);
    let connection = Connection::open(&database_path).unwrap();
    connection
        .execute_batch("pragma journal_mode=wal; pragma wal_autocheckpoint=0; create table message (body blob);")
        .unwrap();

    let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
    let shared = active_node(dir.path(), &certificates, listener.local_addr().unwrap().port());
    let mut writers = Vec::new();
    for _ in 0..WRITERS {
        let writer_shared = Arc::clone(&shared);
        let writer_path = database_path.clone();
        writers.push(thread::spawn(move || write_while_solo(&writer_shared, &writer_path)));
    }
    let standby_tls = TlsContext::load(&certificates.files(NODE_B)).unwrap();
    let standby = thread::spawn(move || run_confirming_standby(&listener, &standby_tls, NO_CLOCK_SKEW_MS));
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
fn a_standby_whose_clock_is_skewed_beyond_the_bound_is_not_admitted() {
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let connection = Connection::open(dir.path().join(DATABASE_FILE_NAME)).unwrap();
    connection
        .execute_batch("pragma journal_mode=wal; create table message (body blob);")
        .unwrap();

    let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
    let shared = active_node(dir.path(), &certificates, listener.local_addr().unwrap().port());
    let standby_tls = TlsContext::load(&certificates.files(NODE_B)).unwrap();
    let standby = thread::spawn(move || run_confirming_standby(&listener, &standby_tls, LARGE_CLOCK_SKEW_MS));
    let shipper_shared = Arc::clone(&shared);
    let shipper = thread::spawn(move || Shipper::new(shipper_shared).run());

    // The standby receives its copy and keeps confirming, and it stays joining for as long as its clock is skewed.
    thread::sleep(ADMISSION_TIMEOUT);
    let state = shared.state.lock();
    let observed = (state.role, state.link_state, state.peer_clock_skew_ms);
    drop(state);
    assert_eq!(observed, (Role::ActiveSolo, LinkState::Joining, LARGE_CLOCK_SKEW_MS));

    shared.announce_stop();
    shipper.join().unwrap();
    standby.join().unwrap();
}

#[test]
fn a_standby_in_sync_whose_clock_is_skewed_beyond_the_bound_is_marked_out() {
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let shared = active_node(dir.path(), &certificates, 0);
    let max_clock_skew_ms = shared.config.max_clock_skew_ms;

    let mut state = shared.state.lock();
    state.role = Role::ActiveReplicated;

    // A skew within the bound is recorded and nothing more ..
    record_clock_skew(&shared, &mut state, max_clock_skew_ms);
    assert!(!state.needs_mark_out);

    // .. whereas one beyond it requests the mark-out.
    record_clock_skew(&shared, &mut state, max_clock_skew_ms + 1);
    let observed = (state.needs_mark_out, state.peer_clock_skew_ms);
    drop(state);
    assert_eq!(observed, (true, max_clock_skew_ms + 1));
}

#[test]
fn a_standby_in_sync_without_a_session_owes_every_frame_read() {
    let certificates = Certificates::issue();
    let dir = tempfile::tempdir().unwrap();
    let connection = Connection::open(dir.path().join(DATABASE_FILE_NAME)).unwrap();
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
    assert_eq!(barrier::wait(&shared), BarrierOutcome::Replaced);
}

#[test]
fn the_connections_of_the_node_sync_every_write() {
    let database_dir = tempfile::tempdir().unwrap();
    let database_path = database_dir.path().join(DATABASE_FILE_NAME);

    let connection = open_connection(&database_path).unwrap();
    let journal_mode: String = connection.query_row("pragma journal_mode", [], |row| row.get(0)).unwrap();
    let synchronous: i64 = connection.query_row("pragma synchronous", [], |row| row.get(0)).unwrap();

    // The value 2 is how SQLite reports the level `full`.
    assert_eq!(journal_mode, "wal");
    assert_eq!(synchronous, 2);
}

mod snapshot;
