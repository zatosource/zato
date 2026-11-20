// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The supervision of the Zato server process, which runs only while the node is active and not isolated.
//!
//! After every start, the supervisor sends `GET /zato/ping` to the server on the loopback address until the server
//! answers 200, and only then marks the server as ready. The label of the pod and the role endpoint follow that mark,
//! so clients reach the node only once its server answers. The mark is cleared whenever the server is started again,
//! exits or is stopped.

use std::os::unix::process::CommandExt;
use std::process::{Child, Command};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use nix::sys::prctl;
use nix::sys::signal::{Signal, killpg};
use nix::sys::wait::{WaitPidFlag, WaitStatus, waitpid};
use nix::unistd::Pid;

use crate::config::ENV_GENERATION;
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

    /// The HTTP client of the pings of the server.
    agent: ureq::Agent,

    /// The URL of the ping endpoint of the server.
    ping_url: String,
}

impl Supervisor {
    /// Returns a supervisor of the server started with `command`.
    pub fn new(shared: Arc<Shared>, command: Vec<String>) -> Self {
        let ping_url = format!("http://{SERVER_HOST}:{}{PING_PATH}", shared.config.server_port);
        let agent = ureq::Agent::config_builder()
            .timeout_global(Some(READINESS_TIMEOUT))
            .http_status_as_error(false)
            .build()
            .into();
        Self {
            shared,
            command,
            child: None,
            agent,
            ping_url,
        }
    }

    /// Runs until the node stops, then stops the server.
    pub fn run(mut self) {
        loop {
            let (should_run, role, stopping, generation, server_ready) = {
                let mut state = self.shared.state.lock();

                // A started server that has not answered yet is checked more often, since clients wait for its answer.
                let awaiting_answer = self.child.is_some() && !state.server_ready;
                let interval = if awaiting_answer { READINESS_INTERVAL } else { CHECK_INTERVAL };
                let _ = self.shared.changed.wait_for(&mut state, interval);
                (
                    state.serves() && !state.stopping,
                    state.role,
                    state.stopping,
                    state.generation,
                    state.server_ready,
                )
            };

            self.reap();

            if should_run && self.child.is_none() {
                self.start(generation);
            } else if !should_run && self.child.is_some() {
                self.stop();
            }

            if !server_ready && self.child.is_some() {
                self.check_readiness(generation);
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
                self.set_server_ready(false);
            }
            Ok(None) => {}
            Err(error) => tracing::error!("Cannot check the Zato server: {error}"),
        }
    }

    /// Records whether the server answers, notifying the label thread and the role endpoint of a change.
    fn set_server_ready(&self, ready: bool) {
        let mut state = self.shared.state.lock();
        let changed = state.server_ready != ready;
        state.server_ready = ready;
        drop(state);

        // Only a change moves the label and the answer of the role endpoint.
        if changed {
            self.shared.changed.notify_all();
        }
    }

    /// Sends one ping to the started server and marks it as ready once it answers 200.
    fn check_readiness(&self, generation: u64) {
        // A server that does not listen yet refuses the connection, and one whose worker has not started
        // lets the ping time out, so neither is marked as ready.
        let answered = self
            .agent
            .get(&self.ping_url)
            .call()
            .is_ok_and(|response| response.status().as_u16() == STATUS_OK);
        if answered {
            tracing::info!("Zato server answers at generation {generation}");
            self.set_server_ready(true);
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
            }
            Err(error) => tracing::error!("Cannot start the Zato server: {error}"),
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

        // Clients stop being sent to a server that is stopping.
        self.set_server_ready(false);

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
