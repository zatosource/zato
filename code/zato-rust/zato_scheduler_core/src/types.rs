// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

use std::fmt;

/// Unique identifier for a scheduler job, wrapping an `i64`.
#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq)]
pub struct JobId(
    /// The underlying numeric identifier.
    pub i64,
);

impl fmt::Display for JobId {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}", self.0)
    }
}

/// Wrapper around a service name string.
#[derive(Debug, Clone)]
pub struct ServiceName(
    /// The underlying service name.
    pub String,
);

impl fmt::Display for ServiceName {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.0)
    }
}

impl AsRef<str> for ServiceName {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

/// Represents the type of a scheduler job.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum JobType {
    /// A job that fires exactly once.
    OneTime,
    /// A job that fires repeatedly at a fixed interval.
    IntervalBased,
}

impl JobType {
    /// Returns the string representation of this job type.
    #[must_use]
    pub const fn as_str(&self) -> &'static str {
        match self {
            Self::OneTime => "one_time",
            Self::IntervalBased => "interval_based",
        }
    }
}

impl From<&str> for JobType {
    fn from(value: &str) -> Self {
        match value {
            "one_time" => Self::OneTime,
            _ => Self::IntervalBased,
        }
    }
}

impl fmt::Display for JobType {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(self.as_str())
    }
}

/// Policy for handling missed job firings.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OnMissedPolicy {
    /// Skip the missed firing entirely.
    Skip,
    /// Run the missed firing once to catch up.
    RunOnce,
}

impl OnMissedPolicy {
    /// Returns the string representation of this policy.
    #[must_use]
    pub const fn as_str(&self) -> &'static str {
        match self {
            Self::Skip => "skip",
            Self::RunOnce => "run_once",
        }
    }
}

impl From<&str> for OnMissedPolicy {
    fn from(value: &str) -> Self {
        match value {
            "skip" => Self::Skip,
            _ => Self::RunOnce,
        }
    }
}

/// String constants for job execution outcome labels.
pub mod outcome {
    /// Matches all outcomes (used in filters).
    pub const ALL: &str = "all";
    /// The job is currently running.
    pub const RUNNING: &str = "running";
    /// The job executed successfully.
    pub const EXECUTED: &str = "ok";
    /// The job was skipped because a previous invocation is still in flight.
    pub const SKIPPED_ALREADY_IN_FLIGHT: &str = "skipped_already_in_flight";
    /// The job was skipped because the date falls on a holiday calendar.
    pub const SKIPPED_HOLIDAY: &str = "skipped_holiday";
    /// The job timed out.
    pub const TIMEOUT: &str = "timeout";
    /// The job was missed and caught up.
    pub const MISSED_CATCHUP: &str = "missed_catchup";
}

/// A batch of fire information for a single job invocation.
pub struct FireBatch {
    /// The job identifier.
    pub job_id: JobId,
    /// The human-readable name of the job.
    pub name: String,
    /// The service to invoke.
    pub service: ServiceName,
    /// Optional extra data to pass to the service.
    pub extra: Option<String>,
    /// The type of job being fired.
    pub job_type: JobType,
    /// The current run number.
    pub current_run: u32,
}
