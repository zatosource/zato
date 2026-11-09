// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The supervision of the Zato server process, which runs only while the node is active and not isolated.

use std::os::unix::process::CommandExt;
use std::process::{Child, Command};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use nix::sys::signal::{Signal, killpg};
use nix::unistd::Pid;

use crate::config::{ENV_BARRIER_SOCKET, ENV_GENERATION, ENV_NODE_NAME};
use crate::state::{Role, Shared};

/// How often the supervisor compares the process with the role when nothing notifies it.
const CHECK_INTERVAL: Duration = Duration::from_millis(500);

/// How long the server may take to stop after SIGTERM before it receives SIGKILL.
const STOP_GRACE: Duration = Duration::from_secs(10);

/// How often a stopping server is checked.
const STOP_POLL_INTERVAL: Duration = Duration::from_millis(50);

/// The process group ID that stands for the process group of the child itself.
const OWN_PROCESS_GROUP: i32 = 0;

/// The Zato server process and the command that starts it.
pub struct Supervisor {
    /// The shared state.
    shared: Arc<Shared>,

    /// The command line of the server.
    command: Vec<String>,

    /// The running server, if any.
    child: Option<Child>,
}

impl Supervisor {
    /// Returns a supervisor of the server started with `command`.
    pub const fn new(shared: Arc<Shared>, command: Vec<String>) -> Self {
        Self {
            shared,
            command,
            child: None,
        }
    }

    /// Runs until the node stops, then stops the server.
    pub fn run(mut self) {
        loop {
            let (should_run, role, stopping, generation) = {
                let mut state = self.shared.state.lock();
                let _ = self.shared.changed.wait_for(&mut state, CHECK_INTERVAL);
                (
                    state.role.is_active() && !state.isolated && !state.stopping,
                    state.role,
                    state.stopping,
                    state.generation,
                )
            };

            self.reap();

            if should_run && self.child.is_none() {
                self.start(generation);
            } else if !should_run && self.child.is_some() {
                self.stop();
            }

            // A fenced node joins again only once its server no longer runs.
            if role == Role::Fenced && self.child.is_none() {
                let mut state = self.shared.state.lock();
                let is_fenced = state.role == Role::Fenced;
                if is_fenced {
                    state.role = Role::StandbyOut;
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
            }
            Ok(None) => {}
            Err(error) => tracing::error!("Cannot check the Zato server: {error}"),
        }
    }

    /// Starts the server in a process group of its own.
    fn start(&mut self, generation: u64) {
        let Some((program, arguments)) = self.command.split_first() else {
            tracing::error!("No Zato server command was given");
            return;
        };
        let config = &self.shared.config;
        let spawned = Command::new(program)
            .args(arguments)
            .env(ENV_GENERATION, generation.to_string())
            .env(ENV_BARRIER_SOCKET, &config.barrier_socket)
            .env(ENV_NODE_NAME, &config.node_name)
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
