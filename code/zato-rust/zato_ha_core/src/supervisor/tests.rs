// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the readiness and the health of the Zato server against a stub of its ping endpoint.

use super::*;
use crate::config::Timers;
use crate::referee::tests::MemoryReferee;
use crate::server_health::ServerFailure;
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

/// The liveness timeout of the tests of the health of the server, which spans one liveness ping.
const LIVENESS_TIMEOUT: Duration = Duration::from_millis(1500);

/// The start timeout of the tests of the health of the server.
const START_TIMEOUT: Duration = Duration::from_secs(1);

/// The exit limit of the tests of the health of the server.
const EXIT_LIMIT: u32 = 3;

/// The file to which the server of the exit tests appends a line at each start.
const STARTS_FILE_NAME: &str = "starts";

/// The server of the exit tests, which records its start and exits at once with a non-zero code.
const EXITING_SCRIPT: &str = r#"echo start >> "$0"; exit 1"#;

/// The server of the exit tests that exits after its first start alone, and runs after every later start.
const EXITING_ONCE_SCRIPT: &str = r#"echo start >> "$0"; if [ "$(wc -l < "$0")" -eq 1 ]; then exit 1; fi; while true; do sleep 0.05; done"#;

/// An active node whose supervisor runs a server, with the files and the stub of the server for as long as it exists.
struct ActiveNode {
    /// The shared state of the node.
    shared: Arc<Shared>,

    /// The thread of the supervisor.
    running: thread::JoinHandle<()>,

    /// The directory of the node's files.
    dir: tempfile::TempDir,
}

impl ActiveNode {
    /// Starts the supervisor of an active node whose server runs `script` with the file `argument` of its directory
    /// as its first argument, and whose ping endpoint is the port of `stub_port`.
    fn start(stub_port: u16, script: &str, argument: &str) -> Self {
        let dir = tempfile::tempdir().unwrap();
        let mut config = node_config(NODE_A, dir.path(), TIMERS);
        config.server_port = stub_port;
        config.server_health.liveness_timeout = LIVENESS_TIMEOUT;
        config.server_health.start_timeout = START_TIMEOUT;
        config.server_health.exit_limit = EXIT_LIMIT;
        let shared = shared(config, Box::new(MemoryReferee::default()));
        {
            let mut state = shared.state.lock();
            state.role = Role::Active;
            state.generation = GENERATION;
        }

        let command = vec![
            "sh".to_owned(),
            "-c".to_owned(),
            script.to_owned(),
            dir.path().join(argument).display().to_string(),
        ];
        let supervisor = Supervisor::new(Arc::clone(&shared), command);
        let running = thread::spawn(move || supervisor.run());
        Self { shared, running, dir }
    }

    /// Returns the failure that the supervisor recorded, if any.
    fn failure(&self) -> Option<ServerFailure> {
        self.shared.state.lock().server_failure
    }

    /// Returns how many times the server of the exit tests started.
    fn starts(&self) -> usize {
        let path = self.dir.path().join(STARTS_FILE_NAME);
        std::fs::read_to_string(path).map_or(0, |text| text.lines().count())
    }

    /// Stops the node and waits for its supervisor to end.
    fn stop(self) {
        self.shared.announce_stop();
        self.running.join().unwrap();
    }
}

#[test]
fn a_server_that_stops_answering_fails_and_is_stopped() {
    let stub = HttpStub::start(STATUS_OK);
    let node = ActiveNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_ready));

    // A server that answers 503 to every liveness ping fails once the liveness timeout elapses ..
    stub.set_status(STATUS_UNAVAILABLE);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::Unanswered)));
    assert!(!node.shared.state.lock().server_ready);

    // .. and is stopped, so it receives no ping after its stop.
    thread::sleep(SERVER_PING_INTERVAL);
    let count = stub.requests().len();
    thread::sleep(UNANSWERED_PERIOD);
    assert_eq!(stub.requests().len(), count);

    node.stop();
}

#[test]
fn a_server_whose_endpoint_is_gone_fails() {
    let stub = HttpStub::start(STATUS_OK);
    let node = ActiveNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_ready));

    // A ping endpoint that refuses every connection answers no liveness ping.
    drop(stub);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::Unanswered)));
    node.stop();
}

#[test]
fn a_server_that_never_answers_fails_at_the_start_timeout() {
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let node = ActiveNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::NotStarted)));
    assert!(!node.shared.state.lock().server_ready);
    node.stop();
}

#[test]
fn a_server_that_exits_at_once_fails_at_the_exit_limit_and_is_not_started_again() {
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let node = ActiveNode::start(stub.port, EXITING_SCRIPT, STARTS_FILE_NAME);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::Exits)));

    // The failure keeps the server stopped while the role is still active, until the control loop resigns.
    thread::sleep(UNANSWERED_PERIOD);
    let limit = usize::try_from(EXIT_LIMIT).unwrap_or(usize::MAX);
    assert_eq!(node.starts(), limit);
    node.stop();
}

#[test]
fn a_single_exit_is_not_a_failure() {
    let stub = HttpStub::start(STATUS_OK);
    let node = ActiveNode::start(stub.port, EXITING_ONCE_SCRIPT, STARTS_FILE_NAME);

    // The server started again after its exit answers, and the one exit stays below the limit.
    assert!(wait_until(|| node.starts() == 2 && node.shared.state.lock().server_ready));
    thread::sleep(UNANSWERED_PERIOD);
    assert_eq!(node.failure(), None);
    node.stop();
}
