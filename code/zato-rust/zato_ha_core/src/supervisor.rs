// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The supervision of the Zato server process, which serves only while the node is active and not isolated.
//!
//! Whenever no activated server runs and the node is not stopping, the supervisor keeps one warm server. A warm server
//! is the server command spawned with the path of an activation FIFO in the data directory and without a generation.
//! It imports its code, reads its configuration files and waits on the FIFO, without any startup hook, connection
//! to a database or listening port. The FIFO is created anew before each spawn, so that no generation meant for
//! an earlier process reaches a new one. A warm server that exits is spawned again after a delay, and its exit is not
//! passed to the policy of the health of the server, since it served nothing.
//!
//! When the role requires a running server, the supervisor activates the warm server. It commits to the start, records
//! the start in the policy of the health and writes the generation to the FIFO, retrying at the readiness interval
//! while the warm server has not reached its wait yet. A node without a warm server spawns one and activates it at once.
//! An activated server is never returned to the warm state. A loss of the role, a failure or a stop ends it, after
//! which the supervisor spawns a new warm server unless the node is stopping.
//!
//! After every activation, the supervisor sends `GET /zato/ping` to the server on the loopback address until the server
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
//!
//! The supervisor marks the server as running from the moment it commits to a start until the process exited or its
//! stop completed, and a warm server never sets the mark. On a stop of the node, the label thread removes the label
//! of the own pod while the supervisor stops the server with SIGTERM, which drains its requests, and waits until
//! no process of its group exists. The warm server of a standby is stopped in the same way before the node exits.
//! The control loop of an active node keeps renewing the lease until the mark is cleared and then releases
//! the referee record.

use std::fs::OpenOptions;
use std::io::{self, Write};
use std::os::unix::fs::OpenOptionsExt;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use nix::errno::Errno;
use nix::fcntl::OFlag;
use nix::sys::prctl;
use nix::sys::signal::{Signal, killpg};
use nix::sys::stat::Mode;
use nix::sys::wait::{WaitPidFlag, WaitStatus, waitid, waitpid};
use nix::unistd::{Pid, mkfifo};

use crate::config::{ACTIVATION_FIFO_NAME, ENV_ACTIVATION_PATH, ENV_GENERATION, SERVER_PING_INTERVAL, SERVER_PING_TIMEOUT};
use crate::server_health::{ServerHealth, Verdict};
use crate::state::{Role, Shared};

/// How often the supervisor compares the process with the role when nothing notifies it.
const CHECK_INTERVAL: Duration = Duration::from_millis(500);

/// How long the server may take to stop after SIGTERM before it receives SIGKILL.
pub const STOP_GRACE: Duration = Duration::from_secs(10);

/// How often a stopping server is checked.
const STOP_POLL_INTERVAL: Duration = Duration::from_millis(50);

/// The process group ID that stands for the process group of the child itself.
const OWN_PROCESS_GROUP: i32 = 0;

/// The PID of the first process of a PID namespace.
const INIT_PID: u32 = 1;

/// How often a started server that has not answered yet is sent a ping, and how often the generation is offered
/// to an activated server that has not reached its wait yet.
const READINESS_INTERVAL: Duration = Duration::from_millis(100);

/// How long one ping of a starting server may take before the next pass of the supervisor sends another.
const READINESS_TIMEOUT: Duration = Duration::from_millis(250);

/// How long after a warm server exited the supervisor spawns the next one.
pub const WARM_RESTART_DELAY: Duration = Duration::from_secs(1);

/// The mode of the activation FIFO, readable and writable by the owner of the node alone.
const ACTIVATION_FIFO_MODE: Mode = Mode::S_IRUSR.union(Mode::S_IWUSR);

/// The address on which the supervisor reaches the server.
const SERVER_HOST: &str = "127.0.0.1";

/// The path of the ping endpoint of the Zato server.
const PING_PATH: &str = "/zato/ping";

/// The HTTP status of a ping that the server answered.
const STATUS_OK: u16 = 200;

/// The outcome of one attempt to write the generation to the activation FIFO.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Delivery {
    /// The warm server has the FIFO open and received the generation.
    Delivered,

    /// The warm server has not opened the FIFO for reading yet.
    NotWaiting,
}

/// The Zato server process, the warm server that waits to replace it, and the command that starts both.
pub struct Supervisor {
    /// The shared state.
    shared: Arc<Shared>,

    /// The command line of the server.
    command: Vec<String>,

    /// The activated server, if any.
    child: Option<Child>,

    /// The warm server, which waits on the activation FIFO, if any.
    warm: Option<Child>,

    /// When the last warm server exited, if one exited and no other was spawned since.
    warm_exited_at: Option<Instant>,

    /// The generation that the activated server has not received yet.
    pending_generation: Option<u64>,

    /// The activation FIFO in the data directory of the node.
    activation_path: PathBuf,

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
        let activation_path = shared.config.data_dir.join(ACTIVATION_FIFO_NAME);
        let agent = new_agent(READINESS_TIMEOUT);
        let liveness_agent = new_agent(SERVER_PING_TIMEOUT);
        let health = ServerHealth::new(shared.config.server_health);
        Self {
            shared,
            command,
            child: None,
            warm: None,
            warm_exited_at: None,
            pending_generation: None,
            activation_path,
            agent,
            liveness_agent,
            ping_url,
            health,
            last_ping_at: Instant::now(),
        }
    }

    /// Runs until the node stops, then stops the server and the warm server.
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
            self.reap_warm();

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
                // An activated server that has not received its generation is offered it at every pass.
                self.deliver_pending_generation();
                if server_ready {
                    self.check_liveness();
                } else {
                    self.check_readiness(generation);
                }
            }

            // A node that serves nothing keeps a warm server, unless it is stopping.
            if self.child.is_none() && !stopping {
                self.keep_warm();
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

            // The warm server of a stopping node is stopped before the node exits.
            if stopping && self.child.is_none() {
                self.stop_warm();
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
                self.pending_generation = None;
                self.health.on_exit(Instant::now());
                self.set_server_ready(false);
                self.set_server_running(false);
            }
            Ok(None) => {}
            Err(error) => tracing::error!("Cannot check the Zato server: {error}"),
        }
    }

    /// Forgets a warm server that exited, which served nothing, so its exit is not passed to the policy of the health,
    /// and ends any process that it left in its group.
    fn reap_warm(&mut self) {
        let Some(warm) = self.warm.as_mut() else {
            return;
        };
        match warm.try_wait() {
            Ok(Some(status)) => {
                tracing::warn!("Warm Zato server exited with {status}");

                // A process of the warm server that outlived it would wait on a FIFO that no longer receives anything.
                if let Ok(pid) = i32::try_from(warm.id()) {
                    let _ = killpg(Pid::from_raw(pid), Signal::SIGKILL);
                }
                self.warm = None;
                self.warm_exited_at = Some(Instant::now());
            }
            Ok(None) => {}
            Err(error) => tracing::error!("Cannot check the warm Zato server: {error}"),
        }
    }

    /// Spawns a warm server unless one runs, at once after an activated server ended, and only after
    /// `WARM_RESTART_DELAY` once a warm server exited.
    fn keep_warm(&mut self) {
        if self.warm.is_some() {
            return;
        }

        // A warm server that exits at once is not spawned again in a tight loop.
        if let Some(exited_at) = self.warm_exited_at
            && exited_at.elapsed() < WARM_RESTART_DELAY
        {
            return;
        }

        match self.spawn_warm() {
            Ok(warm) => {
                tracing::info!("Warm Zato server spawned with PID {}", warm.id());
                self.warm = Some(warm);
                self.warm_exited_at = None;
            }

            // A warm server that cannot be spawned is tried again as one that exited.
            Err(error) => {
                tracing::error!("Cannot start a warm Zato server: {error}");
                self.warm_exited_at = Some(Instant::now());
            }
        }
    }

    /// Spawns the server command in a process group of its own as a warm server, with a new activation FIFO
    /// and without a generation.
    fn spawn_warm(&self) -> io::Result<Child> {
        let Some((program, arguments)) = self.command.split_first() else {
            return Err(io::Error::other("no Zato server command was given"));
        };

        // No warm and no activated server runs at this point, so every child that exited belongs to an earlier server.
        reap_reparented_processes(None);
        create_activation_fifo(&self.activation_path)?;

        Command::new(program)
            .args(arguments)
            .env(ENV_ACTIVATION_PATH, &self.activation_path)
            .env_remove(ENV_GENERATION)
            .process_group(OWN_PROCESS_GROUP)
            .spawn()
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

    /// Records whether a process of the server runs, notifying the control loop, which releases the record
    /// of a stopping active node only once no process of its server runs.
    fn set_server_running(&self, running: bool) {
        let mut state = self.shared.state.lock();
        state.server_running = running;
        drop(state);
        self.shared.changed.notify_all();
    }

    /// Commits to a start of the server unless the node is stopping, and returns whether it did.
    ///
    /// The mark of a running server is set under the same lock in which the stop is read, so the control loop of
    /// a stopping node either finds the mark set and waits for the stop of the server, or the server never starts.
    fn commit_to_start(&self) -> bool {
        let mut state = self.shared.state.lock();
        let committed = !state.stopping;
        if committed {
            state.server_running = true;
        }
        drop(state);
        self.shared.changed.notify_all();
        committed
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

    /// Activates the warm server at `generation`, or spawns a warm server and activates it at once if none runs.
    fn start(&mut self, generation: u64) {
        // A node that began to stop since the role was read starts no server.
        if !self.commit_to_start() {
            return;
        }

        // A new server has not answered yet, whatever its predecessor did.
        self.set_server_ready(false);

        let warm = if let Some(warm) = self.warm.take() {
            // The warm server is held while the children of earlier servers are reaped, so its own exit status is kept
            // for the supervisor.
            let held = i32::try_from(warm.id()).ok().map(Pid::from_raw);
            reap_reparented_processes(held);
            warm
        } else {
            match self.spawn_warm() {
                Ok(warm) => warm,

                // A server that cannot be spawned fails as one that exits at once does, and no process of it runs.
                Err(error) => {
                    tracing::error!("Cannot start the Zato server: {error}");
                    self.health.on_exit(Instant::now());
                    self.set_server_running(false);
                    return;
                }
            }
        };

        tracing::info!("Zato server started with PID {} at generation {generation}", warm.id());
        self.child = Some(warm);

        // The start timeout of the policy covers the delivery of the generation as well as the start that follows it.
        self.health.on_start(Instant::now());

        // A new server receives readiness pings, never a liveness ping before its first ping interval.
        self.last_ping_at = Instant::now();

        self.pending_generation = Some(generation);
        self.deliver_pending_generation();
    }

    /// Writes the generation to the activation FIFO of the activated server if the server has not received it yet.
    fn deliver_pending_generation(&mut self) {
        let Some(generation) = self.pending_generation else {
            return;
        };
        match deliver_generation(&self.activation_path, generation) {
            Ok(Delivery::Delivered) => {
                tracing::info!("Generation {generation} delivered to the Zato server");
                self.pending_generation = None;
            }

            // The server has not reached its wait yet, and the next pass offers the generation again.
            Ok(Delivery::NotWaiting) => {}

            // A FIFO that cannot be written makes the server one that exits at once.
            Err(error) => {
                tracing::error!("Cannot deliver generation {generation} to the Zato server: {error}");
                self.pending_generation = None;
                self.health.on_exit(Instant::now());
                if let Some(child) = self.child.take() {
                    terminate(child);
                }
                self.set_server_ready(false);
                self.set_server_running(false);
            }
        }
    }

    /// Stops the server and every process it started, and only then clears the mark of a running server.
    fn stop(&mut self) {
        let Some(child) = self.child.take() else {
            return;
        };
        self.pending_generation = None;

        // Clients stop being sent to a server that is stopping, and its stop is not a failure of the server.
        self.set_server_ready(false);
        self.health.on_stop();

        terminate(child);
        self.set_server_running(false);
    }

    /// Stops the warm server, which leaves the marks of a running and of a ready server as they are.
    fn stop_warm(&mut self) {
        if let Some(warm) = self.warm.take() {
            terminate(warm);
        }
    }
}

/// Stops a server and every process it started, with SIGTERM and then SIGKILL.
///
/// The server is stopped once no process of its group exists. The process that the node started may exit
/// at once on SIGTERM, as `zato start --fg` does, while the arbiter that it started still drains its worker.
fn terminate(mut child: Child) {
    let Ok(pid) = i32::try_from(child.id()) else {
        return;
    };
    let group = Pid::from_raw(pid);
    tracing::info!("Stopping the Zato server with PID {pid}");

    // A group that already exited reports an error that changes nothing.
    let _ = killpg(group, Signal::SIGTERM);
    let deadline = Instant::now() + STOP_GRACE;
    while Instant::now() < deadline {
        // The started process and the processes reparented to this node are reaped as they exit,
        // so that an exited process does not keep the group in existence.
        let _ = child.try_wait();
        reap_group(group);
        if !group_exists(group) {
            return;
        }
        thread::sleep(STOP_POLL_INTERVAL);
    }
    let _ = killpg(group, Signal::SIGKILL);
    let _ = child.wait();
}

/// Returns an HTTP client of the pings of the server with the given timeout, which reads every status as an answer.
fn new_agent(timeout: Duration) -> ureq::Agent {
    ureq::Agent::config_builder()
        .timeout_global(Some(timeout))
        .http_status_as_error(false)
        .build()
        .into()
}

/// Replaces the activation FIFO with a new one, so that no generation meant for an earlier warm server reaches
/// the next one.
fn create_activation_fifo(path: &Path) -> io::Result<()> {
    // The FIFO of an earlier warm server is removed, and a node that has not spawned one yet has none to remove.
    match std::fs::remove_file(path) {
        Ok(()) => {}
        Err(error) if error.kind() == io::ErrorKind::NotFound => {}
        Err(error) => return Err(error),
    }
    mkfifo(path, ACTIVATION_FIFO_MODE)?;
    Ok(())
}

/// Writes the generation, followed by a newline, to the activation FIFO, without waiting for a reader.
fn deliver_generation(path: &Path, generation: u64) -> io::Result<Delivery> {
    // A FIFO opened for writing without blocking reports ENXIO while no process has it open for reading.
    let opened = OpenOptions::new().write(true).custom_flags(OFlag::O_NONBLOCK.bits()).open(path);
    let mut fifo = match opened {
        Ok(fifo) => fifo,
        Err(error) if error.raw_os_error().map(Errno::from_raw) == Some(Errno::ENXIO) => return Ok(Delivery::NotWaiting),
        Err(error) => return Err(error),
    };

    // The line is shorter than the atomic write size of a pipe, so the reader receives all of it or nothing.
    let line = format!("{generation}\n");
    fifo.write_all(line.as_bytes())?;
    Ok(Delivery::Delivered)
}

/// Reaps the processes of the group of a stopping server that exited and whose parent is this node.
fn reap_group(group: Pid) {
    // A negative PID selects every child of this node in the process group of the same number.
    let members = Pid::from_raw(group.as_raw().saturating_neg());
    loop {
        match waitpid(members, Some(WaitPidFlag::WNOHANG)) {
            // A member that still runs or no member at all leaves nothing more to reap.
            Ok(WaitStatus::StillAlive) | Err(_) => return,
            Ok(_) => {}
        }
    }
}

/// Whether any process of a process group exists, one that exited and was not reaped yet included.
fn group_exists(group: Pid) -> bool {
    // No signal is delivered, only the existence of the group is checked.
    !matches!(killpg(group, None), Err(Errno::ESRCH))
}

/// Whether the kernel reparents to this node the processes whose parent exited.
fn receives_reparented_processes() -> bool {
    // Such a process goes to the nearest child subreaper among its ancestors, or else to the first process of the namespace.
    std::process::id() == INIT_PID || prctl::get_child_subreaper().is_ok_and(|subreaper| subreaper)
}

/// Reaps the processes of earlier servers that were reparented to this node, except the process `held`
/// that the supervisor holds.
///
/// This happens when the node is the first process of a container. An unreaped process keeps its PID,
/// and the server does not start while its pidfile names a PID that it cannot inspect. A node to which
/// no process is reparented has no child other than its own servers, so it reaps nothing here.
fn reap_reparented_processes(held: Option<Pid>) {
    if !receives_reparented_processes() {
        return;
    }

    // An exited child is first inspected without being reaped, so that the status of the held process stays
    // with its `Child` for `try_wait`.
    let peek = WaitPidFlag::WEXITED | WaitPidFlag::WNOHANG | WaitPidFlag::WNOWAIT;
    loop {
        // A child that still runs or no child at all leaves nothing more to reap.
        let Ok(status) = waitid(nix::sys::wait::Id::All, peek) else {
            return;
        };
        let Some(pid) = status.pid() else {
            return;
        };

        // The held process is reaped through its `Child`, and the earlier servers behind it at the next start.
        if Some(pid) == held {
            return;
        }
        match waitpid(pid, Some(WaitPidFlag::WNOHANG)) {
            Ok(status) => tracing::info!("Reaped a process of an earlier Zato server, {status:?}"),
            Err(_) => return,
        }
    }
}

#[cfg(test)]
mod tests;
