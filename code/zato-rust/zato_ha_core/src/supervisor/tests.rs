// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the readiness of the Zato server against a stub of its ping endpoint.

use super::*;
use crate::config::Timers;
use crate::referee::tests::MemoryReferee;
use crate::test_support::{HttpStub, NODE_A, node_config, shared, wait_until};

/// The status of a ping that a server which cannot answer yet returns.
const STATUS_UNAVAILABLE: u16 = 503;

/// The request line of a ping.
const PING_REQUEST_LINE: &str = "GET /zato/ping HTTP/1.1";

/// How long a server that does not answer 200 is watched to confirm that it is never marked as ready.
const UNANSWERED_PERIOD: Duration = Duration::from_secs(1);

/// The timers of the node, which the supervisor does not read.
const TIMERS: Timers = Timers {
    heartbeat: Duration::from_millis(500),
    takeover: Duration::from_secs(6),
};

/// The generation of the active node of the tests.
const GENERATION: u64 = 1;

/// The file whose presence ends the server of the tests.
const EXIT_FILE_NAME: &str = "exit";

/// The server of the tests, a shell that runs until the file named by its first argument exists.
const SERVER_SCRIPT: &str = r#"while [ ! -e "$0" ]; do sleep 0.05; done"#;

#[test]
fn the_server_is_ready_only_after_its_ping_answers_and_until_it_exits() {
    let dir = tempfile::tempdir().unwrap();
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let mut config = node_config(NODE_A, dir.path(), TIMERS);
    config.server_port = stub.port;
    let shared = shared(config, Box::new(MemoryReferee::default()));
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.generation = GENERATION;
    }

    let exit_file = dir.path().join(EXIT_FILE_NAME);
    let command = vec![
        "sh".to_owned(),
        "-c".to_owned(),
        SERVER_SCRIPT.to_owned(),
        exit_file.display().to_string(),
    ];
    let supervisor = Supervisor::new(Arc::clone(&shared), command);
    let running = thread::spawn(move || supervisor.run());

    // A started server is pinged, and one that answers 503 is never marked as ready ..
    assert!(wait_until(|| stub
        .requests()
        .iter()
        .any(|request| request.request_line == PING_REQUEST_LINE)));
    thread::sleep(UNANSWERED_PERIOD);
    assert!(!shared.state.lock().server_ready);

    // .. the first 200 marks it as ready ..
    stub.set_status(STATUS_OK);
    assert!(wait_until(|| shared.state.lock().server_ready));

    // .. its exit clears the mark, and a server started again that does not answer 200 remains unmarked ..
    stub.set_status(STATUS_UNAVAILABLE);
    std::fs::write(&exit_file, b"").unwrap();
    assert!(wait_until(|| !shared.state.lock().server_ready));
    thread::sleep(UNANSWERED_PERIOD);
    assert!(!shared.state.lock().server_ready);

    // .. and the supervisor ends once the node stops.
    shared.announce_stop();
    running.join().unwrap();
}

#[test]
fn a_standby_starts_no_server_and_sends_no_ping() {
    let dir = tempfile::tempdir().unwrap();
    let stub = HttpStub::start(STATUS_OK);
    let mut config = node_config(NODE_A, dir.path(), TIMERS);
    config.server_port = stub.port;
    let shared = shared(config, Box::new(MemoryReferee::default()));
    shared.state.lock().role = Role::Standby;

    let exit_file = dir.path().join(EXIT_FILE_NAME);
    let command = vec![
        "sh".to_owned(),
        "-c".to_owned(),
        SERVER_SCRIPT.to_owned(),
        exit_file.display().to_string(),
    ];
    let supervisor = Supervisor::new(Arc::clone(&shared), command);
    let running = thread::spawn(move || supervisor.run());

    thread::sleep(UNANSWERED_PERIOD);
    assert!(stub.requests().is_empty());
    assert!(!shared.state.lock().server_ready);

    shared.announce_stop();
    running.join().unwrap();
}
