// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The supervision of the Zato server process, which runs only while the node is active and not isolated.
//!
//! After every start, the supervisor sends `GET /zato/ping` to the server on the loopback address until the server
//! answers 200, and only then marks the server as ready. The label of the pod and the role endpoint follow that mark,
//! so clients reach the node only once its server answers. The mark is cleared whenever the server is started again,
//! exits or is stopped.
//!
//! A server that answered is sent a ping at every ping interval with the timeout of a liveness ping, and every start,
//! answer and exit of the server is passed to the policy of its health. Once the policy finds the server failed,
//! because it stopped answering, never answered after its start or exited repeatedly, the supervisor records
//! the failure in the shared state and clears the mark under one lock, so the label of the pod is removed first.
//! The supervisor then stops the server and keeps it stopped, the control loop resigns the active role, the lease
//! lapses and the node holds off its own takeovers. An exit below the exit limit starts the server again.

use std::os::unix::process::CommandExt;
use std::process::{Child, Command};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use nix::sys::prctl;
use nix::sys::signal::{Signal, killpg};
use nix::sys::wait::{WaitPidFlag, WaitStatus, waitpid};
use nix::unistd::Pid;

use crate::config::{ENV_GENERATION, SERVER_PING_INTERVAL, SERVER_PING_TIMEOUT};
use crate::server_health::{ServerHealth, Verdict};
use crate::state::{Role, Shared};

/// How often the supervisor compares the process with the role when nothing notifies it.
const CHECK_INTERVAL: Duration = Duration::from_millis(500);

/// How long the server may take to stop after SIGTERM before it receives SIGKILL.
const STOP_GRACE: Duration = Duration::from_secs(10);

/// How often a stopping server is checked.
const STOP_POLL_INTERVAL: Duration = Duration::from_millis(50);

/// The process group ID that stands for the process group of the child itself.
const OWN_PROCESS_GROUP: i32 = 0;

/// The PID of the first process of a PID namespace.
const INIT_PID: u32 = 1;

/// How often a started server that has not answered yet is sent a ping.
const READINESS_INTERVAL: Duration = Duration::from_millis(100);

/// How long one ping of a starting server may take before the next pass of the supervisor sends another.
const READINESS_TIMEOUT: Duration = Duration::from_millis(250);

/// The address on which the supervisor reaches the server.
const SERVER_HOST: &str = "127.0.0.1";

/// The path of the ping endpoint of the Zato server.
const PING_PATH: &str = "/zato/ping";

/// The HTTP status of a ping that the server answered.
const STATUS_OK: u16 = 200;

/// The Zato server process and the command that starts it.
pub struct Supervisor {
    /// The shared state.
    shared: Arc<Shared>,

    /// The command line of the server.
    command: Vec<String>,

    /// The running server, if any.
    child: Option<Child>,

    /// The HTTP client of the pings of a starting server.
    agent: ureq::Agent,

    /// The HTTP client of the liveness pings of a server that answered.
    liveness_agent: ureq::Agent,

    /// The URL of the ping endpoint of the server.
    ping_url: String,

    /// The policy that decides from the starts, answers and exits of the server whether it failed.
    health: ServerHealth,

    /// When the last liveness ping was sent.
    last_ping_at: Instant,
}

impl Supervisor {
    /// Returns a supervisor of the server started with `command`.
    pub fn new(shared: Arc<Shared>, command: Vec<String>) -> Self {
        let ping_url = format!("http://{SERVER_HOST}:{}{PING_PATH}", shared.config.server_port);
        let agent = new_agent(READINESS_TIMEOUT);
        let liveness_agent = new_agent(SERVER_PING_TIMEOUT);
        let health = ServerHealth::new(shared.config.server_health);
        Self {
            shared,
            command,
            child: None,
            agent,
            liveness_agent,
            ping_url,
            health,
            last_ping_at: Instant::now(),
        }
    }

    /// Runs until the node stops, then stops the server.
    pub fn run(mut self) {
        loop {
            let (mut should_run, role, stopping, generation, server_ready) = {
                let mut state = self.shared.state.lock();

                // A started server that has not answered yet is checked more often, since clients wait for its answer.
                let awaiting_answer = self.child.is_some() && !state.server_ready;
                let interval = if awaiting_answer { READINESS_INTERVAL } else { CHECK_INTERVAL };
                let _ = self.shared.changed.wait_for(&mut state, interval);

                // A failure on which the control loop has not acted yet keeps the server stopped.
                let has_failed = state.server_failure.is_some();
                (
                    state.serves() && !state.stopping && !has_failed,
                    state.role,
                    state.stopping,
                    state.generation,
                    state.server_ready,
                )
            };

            self.reap();

            // A server found failed is not started again, whatever the role, until the control loop resigns.
            if should_run && self.check_health() {
                should_run = false;
            }

            if should_run && self.child.is_none() {
                self.start(generation);
            } else if !should_run && self.child.is_some() {
                self.stop();
            }

            if self.child.is_some() {
                if server_ready {
                    self.check_liveness();
                } else {
                    self.check_readiness(generation);
                }
            }

            // A fenced node joins again as the standby only once its server no longer runs.
            if role == Role::Fenced && self.child.is_none() {
                let mut state = self.shared.state.lock();
                let is_fenced = state.role == Role::Fenced;
                if is_fenced {
                    state.role = Role::Standby;
                }
                drop(state);
                if is_fenced {
                    self.shared.changed.notify_all();
                }
            }

            if stopping && self.child.is_none() {
                return;
            }
        }
    }

    /// Forgets a server that exited by itself, so that it is started again if the role still requires it.
    fn reap(&mut self) {
        let Some(child) = self.child.as_mut() else {
            return;
        };
        match child.try_wait() {
            Ok(Some(status)) => {
                tracing::warn!("Zato server exited with {status}");
                self.child = None;
                self.health.on_exit(Instant::now());
                self.set_server_ready(false);
            }
            Ok(None) => {}
            Err(error) => tracing::error!("Cannot check the Zato server: {error}"),
        }
    }

    /// Records a failure of the server that the policy of its health finds, for the control loop to act on,
    /// and returns whether there was one.
    fn check_health(&mut self) -> bool {
        let Verdict::Failed(failure) = self.health.verdict(Instant::now()) else {
            return false;
        };

        // The failure and the end of readiness are set under one lock, so that the label thread and the role endpoint
        // never see a failed server that is still ready.
        let mut state = self.shared.state.lock();
        state.server_failure = Some(failure);
        state.server_ready = false;
        state.server_ready_since = None;
        drop(state);
        self.shared.changed.notify_all();

        tracing::error!("The node resigns because {failure}");

        // The node acts on this failure once, and a server that it runs again later is judged afresh.
        self.health.reset();
        true
    }

    /// Records whether the server answers, notifying the label thread and the role endpoint of a change.
    fn set_server_ready(&self, ready: bool) {
        let mut state = self.shared.state.lock();
        let changed = state.server_ready != ready;
        state.server_ready = ready;

        // The moment of readiness is kept only from the change to ready, so a ready server keeps its first moment.
        if changed {
            state.server_ready_since = ready.then(Instant::now);
        }
        drop(state);

        // Only a change moves the label and the answer of the role endpoint.
        if changed {
            self.shared.changed.notify_all();
        }
    }

    /// Sends one ping to the server and returns whether it answered 200.
    fn ping(&self, agent: &ureq::Agent) -> bool {
        agent
            .get(&self.ping_url)
            .call()
            .is_ok_and(|response| response.status().as_u16() == STATUS_OK)
    }

    /// Sends one ping to the started server and marks it as ready once it answers 200.
    fn check_readiness(&mut self, generation: u64) {
        // A server that does not listen yet refuses the connection, and one whose worker has not started
        // lets the ping time out, so neither is marked as ready.
        if self.ping(&self.agent) {
            tracing::info!("Zato server answers at generation {generation}");
            self.health.on_answer(Instant::now());
            self.last_ping_at = Instant::now();
            self.set_server_ready(true);
        }
    }

    /// Sends a liveness ping to a server that answered, once per ping interval, and records its answer.
    fn check_liveness(&mut self) {
        if self.last_ping_at.elapsed() < SERVER_PING_INTERVAL {
            return;
        }
        self.last_ping_at = Instant::now();

        // A ping that is refused, times out or is not answered 200 is not recorded,
        // and the policy measures the silence from the last answer.
        if self.ping(&self.liveness_agent) {
            self.health.on_answer(Instant::now());
        }
    }

    /// Starts the server in a process group of its own.
    fn start(&mut self, generation: u64) {
        let Some((program, arguments)) = self.command.split_first() else {
            tracing::error!("No Zato server command was given");
            return;
        };

        // A new server has not answered yet, whatever its predecessor did.
        self.set_server_ready(false);
        reap_reparented_processes();
        let spawned = Command::new(program)
            .args(arguments)
            .env(ENV_GENERATION, generation.to_string())
            .process_group(OWN_PROCESS_GROUP)
            .spawn();
        match spawned {
            Ok(child) => {
                tracing::info!("Zato server started with PID {} at generation {generation}", child.id());
                self.child = Some(child);
                self.health.on_start(Instant::now());

                // A new server receives readiness pings, never a liveness ping before its first ping interval.
                self.last_ping_at = Instant::now();
            }

            // A server that cannot be spawned fails as one that exits at once does.
            Err(error) => {
                tracing::error!("Cannot start the Zato server: {error}");
                self.health.on_exit(Instant::now());
            }
        }
    }

    /// Stops the server and every process it started, with SIGTERM and then SIGKILL.
    fn stop(&mut self) {
        let Some(mut child) = self.child.take() else {
            return;
        };
        let Ok(pid) = i32::try_from(child.id()) else {
            return;
        };
        let group = Pid::from_raw(pid);
        tracing::info!("Stopping the Zato server with PID {pid}");

        // Clients stop being sent to a server that is stopping, and its stop is not a failure of the server.
        self.set_server_ready(false);
        self.health.on_stop();

        // A group that already exited reports an error that changes nothing.
        let _ = killpg(group, Signal::SIGTERM);
        let deadline = Instant::now() + STOP_GRACE;
        while Instant::now() < deadline {
            if matches!(child.try_wait(), Ok(Some(_))) {
                let _ = killpg(group, Signal::SIGKILL);
                return;
            }
            thread::sleep(STOP_POLL_INTERVAL);
        }
        let _ = killpg(group, Signal::SIGKILL);
        let _ = child.wait();
    }
}

/// Returns an HTTP client of the pings of the server with the given timeout, which reads every status as an answer.
fn new_agent(timeout: Duration) -> ureq::Agent {
    ureq::Agent::config_builder()
        .timeout_global(Some(timeout))
        .http_status_as_error(false)
        .build()
        .into()
}

/// Whether the kernel reparents to this node the processes whose parent exited.
fn receives_reparented_processes() -> bool {
    // Such a process goes to the nearest child subreaper among its ancestors, or else to the first process of the namespace.
    std::process::id() == INIT_PID || prctl::get_child_subreaper().is_ok_and(|subreaper| subreaper)
}

/// Reaps the processes of earlier servers that were reparented to this node.
///
/// This happens when the node is the first process of a container. An unreaped process keeps its PID,
/// and the server does not start while its pidfile names a PID that it cannot inspect. A node to which
/// no process is reparented has no child other than its own server, so it reaps nothing here.
fn reap_reparented_processes() {
    if !receives_reparented_processes() {
        return;
    }
    loop {
        // No server runs at this point, so every child that exited belongs to an earlier server.
        match waitpid(None, Some(WaitPidFlag::WNOHANG)) {
            // A child that still runs or no child at all leaves nothing more to reap.
            Ok(WaitStatus::StillAlive) | Err(_) => return,
            Ok(status) => tracing::info!("Reaped a process of an earlier Zato server, {status:?}"),
        }
    }
}

#[cfg(test)]
mod tests;
