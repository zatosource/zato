// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the snapshot that a joining standby receives while the Zato server keeps committing.

use super::*;
use crate::standby;
use std::io::Write;
use std::net::{Shutdown, TcpStream};

/// How many bytes of a file the relay passes to the standby before it holds back the rest, which is less than either file
/// of the snapshot, so that the shipper is still sending that file.
const HELD_INTO_FILE: u64 = 4 * 1024 * 1024;

/// The size of each read of the relay.
const RELAY_BUFFER_SIZE: usize = 64 * 1024;

/// How long a test waits for the admission of a standby that received a snapshot of tens of megabytes.
const SNAPSHOT_ADMISSION_TIMEOUT: Duration = Duration::from_secs(30);

/// How often a test reads the role of a node that it waits for.
const ROLE_POLL_INTERVAL: Duration = Duration::from_millis(10);

/// The file of the snapshot that the shipper is sending when the log is restarted.
#[derive(Clone, Copy)]
enum RestartedDuring {
    /// The database file, sent first.
    DatabaseFile,

    /// The log, sent after the database file.
    Log,
}

/// The channels between a test and the relay of its link.
struct RelayChannels {
    /// How many bytes the relay passes to the standby before it holds back the rest.
    held_after: u64,

    /// Told once the relay holds back what the active node sends.
    held: mpsc::Sender<()>,

    /// Tells the relay to pass everything again.
    release: mpsc::Receiver<()>,
}

/// Relays one link from the active node to the standby on `standby_port`, holding back what the active node sends
/// once `held_after` bytes passed until the test releases it.
fn relay(listener: &TcpListener, standby_port: u16, channels: &RelayChannels) {
    let (mut from_active, _) = listener.accept().unwrap();
    let mut to_standby = TcpStream::connect((LOOPBACK, standby_port)).unwrap();

    let mut from_standby = to_standby.try_clone().unwrap();
    let mut to_active = from_active.try_clone().unwrap();
    let _ = thread::spawn(move || {
        let _ = std::io::copy(&mut from_standby, &mut to_active);
        let _ = to_active.shutdown(Shutdown::Write);
    });

    let mut buffer = vec![0_u8; RELAY_BUFFER_SIZE];
    let mut passed: u64 = 0;
    let mut is_held = false;
    while let Ok(count) = from_active.read(&mut buffer) {
        if count == 0 {
            break;
        }
        if to_standby.write_all(buffer.get(..count).unwrap()).is_err() {
            break;
        }
        passed += u64::try_from(count).unwrap();
        if !is_held && passed >= channels.held_after {
            is_held = true;
            channels.held.send(()).unwrap();
            channels.release.recv().unwrap();
        }
    }
    let _ = to_standby.shutdown(Shutdown::Write);
}

/// Returns the salts of the log of the database at `path`.
fn log_salts(path: &Path) -> (u32, u32) {
    let mut raw = [0_u8; wal::HEADER_SIZE];
    File::open(wal::wal_path(path)).unwrap().read_exact(&mut raw).unwrap();
    let header = wal::WalHeader::parse(raw).unwrap();
    (header.salt_one, header.salt_two)
}

/// Returns how many rows the table of messages of the database at `path` holds and how many bytes their bodies hold,
/// once the integrity check of the database passed.
fn message_totals(path: &Path) -> (i64, i64) {
    let connection = Connection::open(path).unwrap();
    let integrity: String = connection.query_row("pragma integrity_check", [], |row| row.get(0)).unwrap();
    assert_eq!(integrity, "ok", "The integrity check of {} failed", path.display());
    connection
        .query_row("select count(*), sum(length(body)) from message", [], |row| {
            Ok((row.get(0)?, row.get(1)?))
        })
        .unwrap()
}

/// Restarts the log, checkpointed whole, while the shipper sends a file of the snapshot to a joining standby, and checks
/// that the standby is admitted and that its copy holds every row of the Zato database.
fn restart_the_log_while_the_snapshot_is_sent(restarted_during: RestartedDuring) {
    let _disk = DISK.lock();
    let certificates = Certificates::issue();
    let active_dir = tempfile::tempdir().unwrap();
    let standby_dir = tempfile::tempdir().unwrap();
    let database_path = active_dir.path().join(DATABASE_FILE_NAME);
    let connection = Connection::open(&database_path).unwrap();
    connection
        .execute_batch("pragma journal_mode=wal; pragma wal_autocheckpoint=0; create table message (body blob); begin;")
        .unwrap();
    let body = vec![0_u8; BULK_ROW_SIZE];
    for _ in 0..LONG_LOG_ROWS {
        let _ = connection.execute("insert into message (body) values (?1)", [&body]).unwrap();
    }
    connection.execute_batch("commit").unwrap();

    // Nothing listens on the port of the standby yet, so the shipper checkpoints every frame without a session.
    let relay_port = TcpListener::bind((LOOPBACK, 0)).unwrap().local_addr().unwrap().port();
    let shared = active_node(active_dir.path(), &certificates, relay_port);
    let mut shipper = Shipper::new(Arc::clone(&shared));
    shipper.iteration().unwrap();
    assert_eq!(shipper.database.checkpointed, shipper.database.end());
    let held_after = match restarted_during {
        RestartedDuring::DatabaseFile => HELD_INTO_FILE,
        RestartedDuring::Log => std::fs::metadata(&database_path).unwrap().len() + HELD_INTO_FILE,
    };

    let standby_config = test_support::node_config(NODE_B, standby_dir.path(), &certificates, TIMERS);
    let standby_path = standby_config.database_path.clone();
    let standby_shared = test_support::shared(standby_config, Box::new(MemoryReferee::default()));
    let standby_listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
    let standby_port = standby_listener.local_addr().unwrap().port();
    let accepting_shared = Arc::clone(&standby_shared);
    let _ = thread::spawn(move || {
        for tcp in standby_listener.incoming() {
            let _ = standby::handle_connection(&accepting_shared, tcp.unwrap());
        }
    });

    let relay_listener = TcpListener::bind((LOOPBACK, relay_port)).unwrap();
    let (held, held_receiver) = mpsc::channel();
    let (release, release_receiver) = mpsc::channel();
    let _ = thread::spawn(move || {
        let channels = RelayChannels {
            held_after,
            held,
            release: release_receiver,
        };
        relay(&relay_listener, standby_port, &channels);
    });
    let shipper_thread = thread::spawn(move || shipper.run());

    // The shipper is sending the database file, and the next commit restarts the log that was checkpointed whole.
    held_receiver.recv_timeout(RECEIVE_TIMEOUT).unwrap();
    let salts_before = log_salts(&database_path);
    let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
    assert_ne!(log_salts(&database_path), salts_before, "The commit did not restart the log");
    release.send(()).unwrap();

    let deadline = Instant::now() + SNAPSHOT_ADMISSION_TIMEOUT;
    while shared.state.lock().role != Role::ActiveReplicated {
        assert!(
            Instant::now() < deadline,
            "The standby was not admitted within {SNAPSHOT_ADMISSION_TIMEOUT:?}"
        );
        thread::sleep(ROLE_POLL_INTERVAL);
    }

    for _ in 0..SMALL_WRITES {
        let _ = connection.execute("insert into message (body) values (?1)", [PUBLICATION]).unwrap();
        assert_eq!(barrier::wait(&shared), BarrierOutcome::Synced);
    }

    shared.announce_stop();
    standby_shared.announce_stop();
    shipper_thread.join().unwrap();

    assert_eq!(message_totals(&standby_path), message_totals(&database_path));
}

#[test]
fn a_log_restarted_while_the_database_file_is_sent_reaches_the_standby_whole() {
    restart_the_log_while_the_snapshot_is_sent(RestartedDuring::DatabaseFile);
}

#[test]
fn a_log_restarted_while_the_log_is_sent_reaches_the_standby_whole() {
    restart_the_log_while_the_snapshot_is_sent(RestartedDuring::Log);
}
