// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The health of the Zato server, which decides from the starts, the answers and the exits of the server
//! whether the node resigns its active role.
//!
//! A server that has answered fails once it has not answered for the liveness timeout, a started server that never
//! answered fails once the start timeout elapses, and a server fails once it has exited as many times as the exit limit
//! within the exit window. The policy reads no clock, every moment is passed to it, so its tests set the moments.

use std::collections::VecDeque;
use std::time::Instant;

use crate::config::ServerHealthConfig;

/// Why the node considers its Zato server failed.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ServerFailure {
    /// The server answered before and has not answered for the liveness timeout.
    Unanswered,

    /// The server was started and has not answered for the start timeout.
    NotStarted,

    /// The server exited as many times as the exit limit within the exit window.
    Exits,
}

impl std::fmt::Display for ServerFailure {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let text = match self {
            Self::Unanswered => "the Zato server stopped answering its ping endpoint",
            Self::NotStarted => "the Zato server did not answer its ping endpoint after its start",
            Self::Exits => "the Zato server exited repeatedly",
        };
        formatter.write_str(text)
    }
}

/// The verdict of the policy at one moment.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Verdict {
    /// The server works or may still start.
    Healthy,

    /// The server failed for the given reason.
    Failed(ServerFailure),
}

/// The record of the starts, the answers and the exits of the Zato server.
pub struct ServerHealth {
    /// The thresholds of the policy.
    config: ServerHealthConfig,

    /// When the running server was started, if one runs.
    started_at: Option<Instant>,

    /// When the running server last answered, if it has answered.
    last_answer_at: Option<Instant>,

    /// The moments of the exits of the server, the oldest first.
    exits: VecDeque<Instant>,
}

impl ServerHealth {
    /// Returns the policy with the given thresholds and nothing recorded.
    pub const fn new(config: ServerHealthConfig) -> Self {
        Self {
            config,
            started_at: None,
            last_answer_at: None,
            exits: VecDeque::new(),
        }
    }

    /// Records a start of the server.
    pub const fn on_start(&mut self, now: Instant) {
        self.started_at = Some(now);
        self.last_answer_at = None;
    }

    /// Records an answer of the running server.
    pub const fn on_answer(&mut self, now: Instant) {
        self.last_answer_at = Some(now);
    }

    /// Records an exit of the server that the node did not request, or a start that could not spawn it.
    pub fn on_exit(&mut self, now: Instant) {
        self.started_at = None;
        self.last_answer_at = None;
        self.exits.push_back(now);
    }

    /// Records a stop of the server that the node requested, which is not a failure of the server.
    pub const fn on_stop(&mut self) {
        self.started_at = None;
        self.last_answer_at = None;
    }

    /// Forgets everything recorded, after the node acted on a failure.
    pub fn reset(&mut self) {
        self.started_at = None;
        self.last_answer_at = None;
        self.exits.clear();
    }

    /// Returns the verdict at `now`, forgetting the exits that fell out of the exit window.
    pub fn verdict(&mut self, now: Instant) -> Verdict {
        // Only the exits within the window count, so the window is moved before they are counted.
        while let Some(oldest) = self.exits.front() {
            let age = now.saturating_duration_since(*oldest);
            if age < self.config.exit_window {
                break;
            }
            self.exits.pop_front();
        }

        let exit_count = self.exits.len();
        let exit_limit = usize::try_from(self.config.exit_limit).unwrap_or(usize::MAX);
        if exit_count >= exit_limit {
            return Verdict::Failed(ServerFailure::Exits);
        }

        // A server that answered once is measured from its last answer ..
        if let Some(last_answer_at) = self.last_answer_at {
            let silent_for = now.saturating_duration_since(last_answer_at);
            if silent_for >= self.config.liveness_timeout {
                return Verdict::Failed(ServerFailure::Unanswered);
            }
            return Verdict::Healthy;
        }

        // .. and one that never answered is measured from its start.
        if let Some(started_at) = self.started_at {
            let starting_for = now.saturating_duration_since(started_at);
            if starting_for >= self.config.start_timeout {
                return Verdict::Failed(ServerFailure::NotStarted);
            }
        }
        Verdict::Healthy
    }
}

#[cfg(test)]
mod tests;
