// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the answers of the role endpoint in each state of the node.

use super::*;
use crate::config::Timers;
use crate::referee::tests::MemoryReferee;
use crate::test_support::{LOOPBACK, NODE_A, node_config, shared};
use std::io::Read;
use std::thread;

/// The timers of the node, which the role endpoint does not read.
const TIMERS: Timers = Timers {
    heartbeat: Duration::from_millis(500),
    takeover: Duration::from_secs(6),
};

/// The generation of the active node of the tests.
const GENERATION: u64 = 3;

/// The status line of an answer of a node that serves and whose server answers.
const STATUS_LINE_OK: &str = "HTTP/1.1 200 OK";

/// The status line of an answer of a node to which no client is sent.
const STATUS_LINE_UNAVAILABLE: &str = "HTTP/1.1 503 Service Unavailable";

/// Sends `GET path` to the role endpoint of `shared` and returns the answer.
fn request(shared: &Shared, path: &str) -> String {
    let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
    let address = listener.local_addr().unwrap();
    let path = path.to_owned();
    let client = thread::spawn(move || {
        let mut stream = TcpStream::connect(address).unwrap();
        stream
            .write_all(format!("GET {path} HTTP/1.1\r\nHost: {LOOPBACK}\r\n\r\n").as_bytes())
            .unwrap();
        let mut out = String::new();
        let _ = stream.read_to_string(&mut out).unwrap();
        out
    });
    let (stream, _) = listener.accept().unwrap();
    answer(shared, stream).unwrap();
    client.join().unwrap()
}

#[test]
fn an_active_node_answers_only_once_its_server_answers() {
    let dir = tempfile::tempdir().unwrap();
    let shared = shared(node_config(NODE_A, dir.path(), TIMERS), Box::new(MemoryReferee::default()));
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.generation = GENERATION;
    }

    // An active node whose server has not answered sends no client to it, and its report says why ..
    let before = request(&shared, ROLE_PATH);
    assert!(before.starts_with(STATUS_LINE_UNAVAILABLE));
    assert!(before.contains(r#""role":"Active""#));
    assert!(before.contains(r#""server_ready":false"#));

    // .. while its health endpoint answers in every state ..
    assert!(request(&shared, HEALTH_PATH).starts_with(STATUS_LINE_OK));

    // .. and the role endpoint answers 200 once the server has answered.
    shared.state.lock().server_ready = true;
    let after = request(&shared, ROLE_PATH);
    assert!(after.starts_with(STATUS_LINE_OK));
    assert!(after.contains(r#""server_ready":true"#));
}

#[test]
fn a_standby_or_isolated_node_does_not_answer() {
    let dir = tempfile::tempdir().unwrap();
    let shared = shared(node_config(NODE_A, dir.path(), TIMERS), Box::new(MemoryReferee::default()));

    // A standby never answers ..
    shared.state.lock().role = Role::Standby;
    assert!(request(&shared, ROLE_PATH).starts_with(STATUS_LINE_UNAVAILABLE));

    // .. and neither does an isolated active node, even with a server that answered.
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.server_ready = true;
        state.isolated = true;
    }
    assert!(request(&shared, ROLE_PATH).starts_with(STATUS_LINE_UNAVAILABLE));
}

#[test]
fn the_ready_endpoint_follows_the_role() {
    let dir = tempfile::tempdir().unwrap();
    let shared = shared(node_config(NODE_A, dir.path(), TIMERS), Box::new(MemoryReferee::default()));

    // A node that has not read the record is not ready ..
    assert!(request(&shared, READY_PATH).starts_with(STATUS_LINE_UNAVAILABLE));

    // .. nor is a fenced node ..
    shared.state.lock().role = Role::Fenced;
    assert!(request(&shared, READY_PATH).starts_with(STATUS_LINE_UNAVAILABLE));

    // .. nor is an active node whose server has not answered ..
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.server_ready = false;
    }
    assert!(request(&shared, READY_PATH).starts_with(STATUS_LINE_UNAVAILABLE));

    // .. while a standby is ready, and so is an active node whose server answers ..
    shared.state.lock().role = Role::Standby;
    assert!(request(&shared, READY_PATH).starts_with(STATUS_LINE_OK));

    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.server_ready = true;
    }
    assert!(request(&shared, READY_PATH).starts_with(STATUS_LINE_OK));

    // .. until the node stops.
    shared.state.lock().stopping = true;
    assert!(request(&shared, READY_PATH).starts_with(STATUS_LINE_UNAVAILABLE));
}
