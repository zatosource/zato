// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Configurations, shared states and probes of the two nodes of a pair for the unit tests.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::Path;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU16, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use parking_lot::Mutex;

use crate::config::{
    DEFAULT_LEASE_NAME, DEFAULT_LOG_LEVEL, DEFAULT_POSTGRESQL_PORT, KubernetesConfig, NodeConfig, PostgreSqlConfig, PostgreSqlPassword,
    RefereeConfig, ServerHealthConfig, Timers,
};
use crate::postgresql::{DatabaseProbe, ProbeError};
use crate::referee::Referee;
use crate::state::Shared;

/// The name of the first node of the pair.
pub const NODE_A: &str = "zato-a";

/// The name of the second node of the pair.
pub const NODE_B: &str = "zato-b";

/// The address on which the nodes of the tests listen.
pub const LOOPBACK: &str = "127.0.0.1";

/// The name of the Zato database and of its user in the configuration of the tests, which no test connects to.
const DATABASE_NAME: &str = "zato";

/// How often an HTTP stub checks for a connection and for the request to stop.
const STUB_POLL: Duration = Duration::from_millis(5);

/// How long an HTTP stub waits for a client that connected to send its request.
const STUB_READ_TIMEOUT: Duration = Duration::from_secs(1);

/// How long a test waits for a condition that the threads of a node bring about.
const CONDITION_TIMEOUT: Duration = Duration::from_secs(10);

/// How often a test checks such a condition.
const CONDITION_POLL: Duration = Duration::from_millis(10);

/// A request that an HTTP stub received.
#[derive(Debug, Clone)]
pub struct StubRequest {
    /// The request line, e.g. `GET /zato/ping HTTP/1.1`.
    pub request_line: String,

    /// The body.
    pub body: String,
}

/// An HTTP server on the loopback address that answers every request with a status that a test changes,
/// records every request in the order of arrival and stops on drop.
pub struct HttpStub {
    /// The port of the stub.
    pub port: u16,

    /// The status of every next answer.
    status: Arc<AtomicU16>,

    /// The requests received so far.
    requests: Arc<Mutex<Vec<StubRequest>>>,

    /// Set on drop, which ends the thread of the stub.
    stop: Arc<AtomicBool>,

    /// The thread of the stub.
    thread: Option<JoinHandle<()>>,
}

impl HttpStub {
    /// Starts a stub that answers with `status` until a test changes it.
    pub fn start(status: u16) -> Self {
        let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
        listener.set_nonblocking(true).unwrap();
        let port = listener.local_addr().unwrap().port();
        let status = Arc::new(AtomicU16::new(status));
        let requests = Arc::new(Mutex::new(Vec::new()));
        let stop = Arc::new(AtomicBool::new(false));

        let thread = {
            let status = Arc::clone(&status);
            let requests = Arc::clone(&requests);
            let stop = Arc::clone(&stop);
            thread::spawn(move || {
                while !stop.load(Ordering::SeqCst) {
                    let Ok((stream, _)) = listener.accept() else {
                        thread::sleep(STUB_POLL);
                        continue;
                    };

                    // A client that gave up before it sent its request, e.g. after its own timeout, leaves nothing to record.
                    if let Ok(request) = answer_stub(stream, status.load(Ordering::SeqCst)) {
                        requests.lock().push(request);
                    }
                }
            })
        };

        Self {
            port,
            status,
            requests,
            stop,
            thread: Some(thread),
        }
    }

    /// Changes the status of every next answer.
    pub fn set_status(&self, status: u16) {
        self.status.store(status, Ordering::SeqCst);
    }

    /// Returns the requests received so far.
    pub fn requests(&self) -> Vec<StubRequest> {
        self.requests.lock().clone()
    }
}

impl Drop for HttpStub {
    fn drop(&mut self) {
        self.stop.store(true, Ordering::SeqCst);
        if let Some(thread) = self.thread.take() {
            thread.join().ok();
        }
    }
}

/// Reads one request in full and answers it with `status` and an empty JSON object, closing the connection.
fn answer_stub(stream: TcpStream, status: u16) -> std::io::Result<StubRequest> {
    stream.set_nonblocking(false)?;
    stream.set_read_timeout(Some(STUB_READ_TIMEOUT))?;
    let mut reader = BufReader::new(stream.try_clone()?);
    let mut request_line = String::new();
    let _ = reader.read_line(&mut request_line)?;

    // The body is read in full before the answer, so that the client is never reset while it sends it.
    let mut content_length = 0;
    loop {
        let mut header = String::new();
        let _ = reader.read_line(&mut header)?;
        let header = header.trim_end();
        if header.is_empty() {
            break;
        }
        if let Some((name, value)) = header.split_once(": ")
            && name.eq_ignore_ascii_case("content-length")
        {
            content_length = value.parse().map_err(std::io::Error::other)?;
        }
    }
    let mut body = vec![0; content_length];
    reader.read_exact(&mut body)?;

    let answer = format!("HTTP/1.1 {status} Status\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{{}}");
    let mut writer = stream;

    // The request is recorded even if the client no longer reads the answer.
    writer.write_all(answer.as_bytes()).ok();
    Ok(StubRequest {
        request_line: request_line.trim_end().to_owned(),
        body: String::from_utf8_lossy(&body).into_owned(),
    })
}

/// Waits until `condition` holds and returns whether it did before the timeout of the tests.
pub fn wait_until(condition: impl Fn() -> bool) -> bool {
    let deadline = Instant::now() + CONDITION_TIMEOUT;
    while Instant::now() < deadline {
        if condition() {
            return true;
        }
        thread::sleep(CONDITION_POLL);
    }
    false
}

/// Returns the configuration of a node whose files are in `dir`.
pub fn node_config(node: &str, dir: &Path, timers: Timers) -> NodeConfig {
    NodeConfig {
        referee: RefereeConfig::Kubernetes(KubernetesConfig {
            lease_name: DEFAULT_LEASE_NAME.to_owned(),
        }),
        node_name: node.to_owned(),
        role_port: 0,
        server_port: 0,
        data_dir: dir.to_path_buf(),
        database: PostgreSqlConfig {
            host: LOOPBACK.to_owned(),
            port: DEFAULT_POSTGRESQL_PORT,
            username: DATABASE_NAME.to_owned(),
            password: PostgreSqlPassword::Value(String::new()),
            database: DATABASE_NAME.to_owned(),
            tls: None,
        },
        timers,
        server_health: ServerHealthConfig::from_defaults(),
        log_level: DEFAULT_LOG_LEVEL.to_owned(),
    }
}

/// Returns the shared state of a node that has not read the referee record yet.
pub fn shared(config: NodeConfig, referee: Box<dyn Referee>) -> Arc<Shared> {
    Arc::new(Shared::new(config, referee))
}

/// A probe kept in memory, which a test makes fail or succeed.
#[derive(Default)]
pub struct MemoryProbe {
    /// Whether every probe fails.
    pub unreachable: Mutex<bool>,

    /// Whether every probe finds the database not durable.
    pub not_durable: Mutex<bool>,

    /// The generation that the generation guard in the database names, if a Zato server took it over.
    pub generation: Mutex<Option<u64>>,
}

impl DatabaseProbe for Arc<MemoryProbe> {
    fn probe(&self) -> Result<Option<u64>, ProbeError> {
        if *self.unreachable.lock() {
            return Err(ProbeError::Unreachable("unreachable".to_owned()));
        }
        if *self.not_durable.lock() {
            return Err(ProbeError::NotDurable("synchronous_standby_names is empty".to_owned()));
        }
        Ok(*self.generation.lock())
    }
}
