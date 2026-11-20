// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the warm server, of the readiness and of the health of the Zato server against a stub of its ping endpoint.
//!
//! Every server of the tests is a shell that waits on the activation FIFO as the Zato server does, by reading one line
//! from the path in `Zato_HA_Activation_Path`, and runs its script only once it received the generation.

use std::os::unix::fs::MetadataExt;

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
const SERVER_SCRIPT: &str = r#"read generation < "$Zato_HA_Activation_Path"; while [ ! -e "$0" ]; do sleep 0.05; done"#;

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

/// The start timeout of the tests of a server that reaches its wait on the activation FIFO late.
const LATE_WAIT_START_TIMEOUT: Duration = Duration::from_secs(5);

/// The exit limit of the tests of the health of the server.
const EXIT_LIMIT: u32 = 3;

/// The file to which the server of the exit tests appends a line at each start.
const STARTS_FILE_NAME: &str = "starts";

/// The server of the exit tests, which records its start and exits at once with a non-zero code.
const EXITING_SCRIPT: &str = r#"read generation < "$Zato_HA_Activation_Path"; echo start >> "$0"; exit 1"#;

/// The server of the exit tests that exits after its first start alone, and runs after every later start.
const EXITING_ONCE_SCRIPT: &str = r#"read generation < "$Zato_HA_Activation_Path"; echo start >> "$0"; if [ "$(wc -l < "$0")" -eq 1 ]; then exit 1; fi; while true; do sleep 0.05; done"#;

/// The file to which the server of the warm tests appends its PID at each spawn.
const SPAWNS_FILE_NAME: &str = "spawns";

/// The suffix of the file into which the server of the warm tests writes what it received at its activation.
const ACTIVATED_SUFFIX: &str = ".activated";

/// The server of the warm tests, which records its PID at the spawn, and the generation that it received
/// together with its own `Zato_HA_Generation` at the activation, and then runs.
const WARM_SCRIPT: &str = r#"echo $$ >> "$0"; read generation < "$Zato_HA_Activation_Path"; echo "$generation ${Zato_HA_Generation-unset}" > "$0.activated"; while true; do sleep 0.05; done"#;

/// What the server of the warm tests records at an activation at `GENERATION` without a generation in its environment.
const ACTIVATED_RECORD: &str = "1 unset";

/// How long the server of the late wait test runs before it opens the activation FIFO.
const LATE_WAIT_DELAY: Duration = Duration::from_secs(2);

/// The server of the late wait test, which opens the activation FIFO only after `LATE_WAIT_DELAY`.
const LATE_WAIT_SCRIPT: &str = r#"sleep 2; read generation < "$Zato_HA_Activation_Path"; echo "$generation ${Zato_HA_Generation-unset}" > "$0.activated"; while true; do sleep 0.05; done"#;

/// How many pings show that the supervisor loop keeps running while the generation waits for its reader.
const PINGS_DURING_DELIVERY: usize = 2;

/// The server of the warm restart test, which records the moment of each spawn in nanoseconds.
///
/// It exits before its wait at each of its first `EXIT_LIMIT` spawns and waits for the activation at every later one.
const EXITING_WARM_SCRIPT: &str = r#"date +%s%N >> "$0"; if [ "$(wc -l < "$0")" -le 3 ]; then exit 1; fi; read generation < "$Zato_HA_Activation_Path"; echo "$generation ${Zato_HA_Generation-unset}" > "$0.activated"; while true; do sleep 0.05; done"#;

/// A node whose supervisor runs a server, with the files and the stub of the server for as long as it exists.
struct SupervisedNode {
    /// The shared state of the node.
    shared: Arc<Shared>,

    /// The thread of the supervisor.
    running: thread::JoinHandle<()>,

    /// The directory of the node's files.
    dir: tempfile::TempDir,
}

impl SupervisedNode {
    /// Starts the supervisor of an active node whose server runs `script` with the file `argument` of its directory
    /// as its first argument, and whose ping endpoint is the port of `stub_port`.
    fn start(stub_port: u16, script: &str, argument: &str) -> Self {
        Self::start_with(Role::Active, START_TIMEOUT, stub_port, script, argument)
    }

    /// Starts the supervisor of a node in `role`, as `start` does, with the start timeout of `start_timeout`.
    fn start_with(role: Role, start_timeout: Duration, stub_port: u16, script: &str, argument: &str) -> Self {
        let dir = tempfile::tempdir().unwrap();
        let mut config = node_config(NODE_A, dir.path(), TIMERS);
        config.server_port = stub_port;
        config.server_health.liveness_timeout = LIVENESS_TIMEOUT;
        config.server_health.start_timeout = start_timeout;
        config.server_health.exit_limit = EXIT_LIMIT;
        let shared = shared(config, Box::new(MemoryReferee::default()));
        {
            let mut state = shared.state.lock();
            state.role = role;
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

    /// Gives the node `role` and notifies the supervisor.
    fn set_role(&self, role: Role) {
        self.shared.state.lock().role = role;
        self.shared.changed.notify_all();
    }

    /// Returns the failure that the supervisor recorded, if any.
    fn failure(&self) -> Option<ServerFailure> {
        self.shared.state.lock().server_failure
    }

    /// Returns the lines of the file `name` of the node's directory, none if the file does not exist yet.
    fn lines(&self, name: &str) -> Vec<String> {
        let path = self.dir.path().join(name);
        std::fs::read_to_string(path).map_or_else(|_| Vec::new(), |text| text.lines().map(str::to_owned).collect())
    }

    /// Returns how many times the server of the exit tests started.
    fn starts(&self) -> usize {
        self.lines(STARTS_FILE_NAME).len()
    }

    /// Returns the PIDs of the servers of the warm tests in the order of their spawns.
    fn spawned_pids(&self) -> Vec<Pid> {
        self.lines(SPAWNS_FILE_NAME)
            .iter()
            .map(|line| Pid::from_raw(line.parse().unwrap()))
            .collect()
    }

    /// Returns what the server of the warm tests received at its activation, none before it.
    fn activated_record(&self, argument: &str) -> Option<String> {
        let name = format!("{argument}{ACTIVATED_SUFFIX}");
        self.lines(&name).into_iter().next()
    }

    /// Returns the activation FIFO of the node.
    fn activation_path(&self) -> PathBuf {
        self.dir.path().join(ACTIVATION_FIFO_NAME)
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
    let node = SupervisedNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
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
    let node = SupervisedNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_ready));

    // A ping endpoint that refuses every connection answers no liveness ping.
    drop(stub);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::Unanswered)));
    node.stop();
}

#[test]
fn a_server_that_never_answers_fails_at_the_start_timeout() {
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let node = SupervisedNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::NotStarted)));
    assert!(!node.shared.state.lock().server_ready);
    node.stop();
}

#[test]
fn a_server_that_exits_at_once_fails_at_the_exit_limit_and_is_not_started_again() {
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let node = SupervisedNode::start(stub.port, EXITING_SCRIPT, STARTS_FILE_NAME);
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
    let node = SupervisedNode::start(stub.port, EXITING_ONCE_SCRIPT, STARTS_FILE_NAME);

    // The server started again after its exit answers, and the one exit stays below the limit.
    assert!(wait_until(|| node.starts() == 2 && node.shared.state.lock().server_ready));
    thread::sleep(UNANSWERED_PERIOD);
    assert_eq!(node.failure(), None);
    node.stop();
}

/// The file that the draining server of the stop test writes on SIGTERM before it exits.
const STOPPED_FILE_NAME: &str = "stopped";

/// The server of the stop test, which records its activation once it handles SIGTERM, drains for a while on SIGTERM,
/// records that it stopped and exits.
const DRAINING_SCRIPT: &str = r#"read generation < "$Zato_HA_Activation_Path"; trap 'sleep 0.3; echo stopped > "$0"; exit 0' TERM; echo activated > "$0.activated"; while true; do sleep 0.05; done"#;

#[test]
fn the_running_mark_is_set_at_the_spawn_and_cleared_when_the_server_exits() {
    // A spawned server is marked as running ..
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start(stub.port, SERVER_SCRIPT, EXIT_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_running));
    node.stop();

    // .. and the exit of a server that is not started again clears the mark.
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let node = SupervisedNode::start(stub.port, EXITING_SCRIPT, STARTS_FILE_NAME);
    assert!(wait_until(|| node.failure() == Some(ServerFailure::Exits)));
    assert!(wait_until(|| !node.shared.state.lock().server_running));
    thread::sleep(UNANSWERED_PERIOD);
    assert!(!node.shared.state.lock().server_running);
    node.stop();
}

#[test]
fn on_a_stop_the_running_mark_is_cleared_only_after_the_server_has_exited() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start(stub.port, DRAINING_SCRIPT, STOPPED_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_ready));
    assert!(wait_until(|| node.activated_record(STOPPED_FILE_NAME).is_some()));

    // The stop of the node sends SIGTERM to a server that drains before it exits, and the mark stays set
    // until the server has recorded its stop and exited.
    node.shared.announce_stop();
    assert!(node.shared.state.lock().server_running);
    assert!(wait_until(|| !node.shared.state.lock().server_running));
    assert!(node.dir.path().join(STOPPED_FILE_NAME).exists());
    node.stop();
}

/// The server of the test of a launcher, which exits at once on SIGTERM while the process it started drains.
///
/// The launcher is a shell that starts the draining server in the background and waits for it, as `zato start --fg`
/// waits for its arbiter.
const LAUNCHER_SCRIPT: &str = r#"read generation < "$Zato_HA_Activation_Path"; sh -c 'trap "sleep 0.3; echo stopped > \"$0\"; exit 0" TERM; echo activated > "$0.activated"; while true; do sleep 0.05; done' "$0" & wait"#;

#[test]
fn on_a_stop_the_running_mark_is_cleared_only_after_every_process_of_the_server_has_exited() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start(stub.port, LAUNCHER_SCRIPT, STOPPED_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_ready));
    assert!(wait_until(|| node.activated_record(STOPPED_FILE_NAME).is_some()));

    // The launcher exits at once on SIGTERM, and the mark stays set until the process that it started
    // has drained, recorded its stop and exited.
    node.shared.announce_stop();
    assert!(wait_until(|| !node.shared.state.lock().server_running));
    assert!(node.dir.path().join(STOPPED_FILE_NAME).exists());
    node.stop();
}

#[test]
fn a_stopping_node_starts_no_server() {
    let dir = tempfile::tempdir().unwrap();
    let stub = HttpStub::start(STATUS_OK);
    let mut config = node_config(NODE_A, dir.path(), TIMERS);
    config.server_port = stub.port;
    let shared = shared(config, Box::new(MemoryReferee::default()));
    {
        let mut state = shared.state.lock();
        state.role = Role::Active;
        state.generation = GENERATION;
        state.stopping = true;
    }

    // The supervisor does not commit to a start once the node is stopping, so no server is ever marked as running.
    let supervisor = Supervisor::new(
        Arc::clone(&shared),
        vec!["sh".to_owned(), "-c".to_owned(), SERVER_SCRIPT.to_owned()],
    );
    assert!(!supervisor.commit_to_start());
    assert!(!shared.state.lock().server_running);
}

#[test]
fn a_standby_keeps_one_warm_server() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start_with(Role::Standby, START_TIMEOUT, stub.port, WARM_SCRIPT, SPAWNS_FILE_NAME);

    // A standby spawns one warm server, which keeps waiting on the activation FIFO ..
    assert!(wait_until(|| node.spawned_pids().len() == 1));
    thread::sleep(UNANSWERED_PERIOD);
    let pids = node.spawned_pids();
    assert_eq!(pids.len(), 1);
    assert!(group_exists(*pids.first().unwrap()));
    assert_eq!(node.activated_record(SPAWNS_FILE_NAME), None);

    // .. is neither marked as running nor as ready, and receives no ping.
    let state = node.shared.state.lock();
    assert!(!state.server_running);
    assert!(!state.server_ready);
    drop(state);
    assert!(stub.requests().is_empty());

    node.stop();
}

#[test]
fn the_activation_delivers_the_generation_to_the_warm_server() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start_with(Role::Standby, START_TIMEOUT, stub.port, WARM_SCRIPT, SPAWNS_FILE_NAME);
    assert!(wait_until(|| node.spawned_pids().len() == 1));

    // The active role activates the warm server that waits, which receives the generation of the node
    // without any generation in its environment ..
    node.set_role(Role::Active);
    assert!(wait_until(|| node.activated_record(SPAWNS_FILE_NAME).is_some()));
    assert_eq!(node.activated_record(SPAWNS_FILE_NAME).as_deref(), Some(ACTIVATED_RECORD));

    // .. and is already marked as running once it has the generation, with no other server spawned.
    assert!(node.shared.state.lock().server_running);
    assert_eq!(node.spawned_pids().len(), 1);
    assert!(wait_until(|| node.shared.state.lock().server_ready));

    node.stop();
}

#[test]
fn a_generation_offered_before_the_wait_is_delivered_once_the_server_waits() {
    let stub = HttpStub::start(STATUS_UNAVAILABLE);
    let started_at = Instant::now();
    let node = SupervisedNode::start_with(Role::Active, LATE_WAIT_START_TIMEOUT, stub.port, LATE_WAIT_SCRIPT, STARTS_FILE_NAME);

    // The supervisor keeps sending pings while the server has not opened the activation FIFO yet ..
    assert!(wait_until(|| stub.requests().len() >= PINGS_DURING_DELIVERY));
    assert!(started_at.elapsed() < LATE_WAIT_DELAY);
    assert_eq!(node.activated_record(STARTS_FILE_NAME), None);
    assert!(node.shared.state.lock().server_running);

    // .. and the server receives the generation once it opens it.
    assert!(wait_until(|| node.activated_record(STARTS_FILE_NAME).is_some()));
    assert_eq!(node.activated_record(STARTS_FILE_NAME).as_deref(), Some(ACTIVATED_RECORD));
    assert_eq!(node.failure(), None);

    node.stop();
}

#[test]
fn a_warm_server_that_exits_is_spawned_again_after_the_restart_delay() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start_with(Role::Standby, START_TIMEOUT, stub.port, EXITING_WARM_SCRIPT, SPAWNS_FILE_NAME);

    // A warm server that exits is spawned again, each time only after the restart delay ..
    let exits = usize::try_from(EXIT_LIMIT).unwrap_or(usize::MAX);
    assert!(wait_until(|| node.lines(SPAWNS_FILE_NAME).len() > exits));
    let spawned_at: Vec<u128> = node.lines(SPAWNS_FILE_NAME).iter().map(|line| line.parse().unwrap()).collect();
    for (earlier, later) in spawned_at.iter().zip(spawned_at.iter().skip(1)) {
        let gap = later - earlier;
        assert!(gap >= WARM_RESTART_DELAY.as_nanos(), "warm server spawned again after {gap} ns");
    }

    // .. and its exits, as many as the exit limit, are not recorded by the policy of the health,
    // so the active role still activates the next warm server.
    node.set_role(Role::Active);
    assert!(wait_until(|| node.activated_record(SPAWNS_FILE_NAME).is_some()));
    assert!(wait_until(|| node.shared.state.lock().server_ready));
    assert_eq!(node.failure(), None);

    node.stop();
}

#[test]
fn the_stop_of_a_standby_ends_its_warm_server() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start_with(Role::Standby, START_TIMEOUT, stub.port, WARM_SCRIPT, SPAWNS_FILE_NAME);
    assert!(wait_until(|| node.spawned_pids().len() == 1));
    let pid = *node.spawned_pids().first().unwrap();
    assert!(group_exists(pid));

    // The supervisor ends only after no process of the group of the warm server exists.
    let shared = Arc::clone(&node.shared);
    node.stop();
    assert!(!group_exists(pid));
    assert!(!shared.state.lock().server_running);
}

#[test]
fn an_activated_server_that_loses_the_role_is_replaced_by_a_new_warm_server() {
    let stub = HttpStub::start(STATUS_OK);
    let node = SupervisedNode::start(stub.port, WARM_SCRIPT, SPAWNS_FILE_NAME);
    assert!(wait_until(|| node.shared.state.lock().server_ready));
    let activated = *node.spawned_pids().first().unwrap();

    // The first FIFO is held open, so that its inode is not reused by the next one.
    let first_fifo = OpenOptions::new()
        .read(true)
        .custom_flags(OFlag::O_NONBLOCK.bits())
        .open(node.activation_path())
        .unwrap();
    let first_inode = first_fifo.metadata().unwrap().ino();

    // A loss of the role stops the activated server ..
    node.set_role(Role::Standby);
    assert!(wait_until(|| !node.shared.state.lock().server_running));
    assert!(!group_exists(activated));

    // .. and a new warm server waits on a new activation FIFO, with neither mark set.
    assert!(wait_until(|| node.spawned_pids().len() == 2));
    let warm = *node.spawned_pids().get(1).unwrap();
    assert_ne!(warm, activated);
    assert!(group_exists(warm));
    let second_inode = std::fs::metadata(node.activation_path()).unwrap().ino();
    assert_ne!(second_inode, first_inode);
    drop(first_fifo);
    assert!(!node.shared.state.lock().server_ready);

    node.stop();
}
