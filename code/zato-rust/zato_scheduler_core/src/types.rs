// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

use std::fmt;

use serde::Serialize;

/// Unique identifier for a scheduler job, wrapping an `i64`.
#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq, Serialize)]
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
#[derive(Debug, Clone, Serialize)]
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
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
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

/// String constants for job execution outcome labels.
pub mod outcome {
    /// The job timed out.
    pub const TIMEOUT: &str = "timeout";
}

/// A batch of fire information for a single job invocation.
#[derive(Serialize)]
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
    /// ISO timestamp of the planned fire time, so the server can record the run's delay.
    pub planned_fire_time_iso: String,
    /// Service to invoke on success.
    pub on_success_service: Option<String>,
    /// Scheduler job to execute on success.
    pub on_success_job: Option<String>,
    /// Service to invoke on error.
    pub on_error_service: Option<String>,
    /// Scheduler job to execute on error.
    pub on_error_job: Option<String>,
}

/// A run that overran its `max_execution_time_ms` and was given up on.
pub struct TimeoutEvent {
    /// Identifier of the job whose run timed out.
    pub job_id: i64,

    /// Run counter of the attempt that timed out.
    pub current_run: u32,

    /// How long the run had been in flight when it was abandoned.
    pub elapsed_ms: u64,

    /// Message describing the timeout, as shown to the user.
    pub error_msg: String,
}

/// One event on its way from the scheduler loop to the Redis publisher thread.
pub enum OutgoingEvent {
    /// A job is due and the server is to execute it.
    Fire(FireBatch),

    /// An in-flight run exceeded its execution-time limit.
    Timeout(TimeoutEvent),
}
