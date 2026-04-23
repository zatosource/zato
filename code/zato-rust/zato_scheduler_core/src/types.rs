use std::fmt;

#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq)]
pub struct JobId(pub i64);

impl fmt::Display for JobId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone)]
pub struct ServiceName(pub String);

impl fmt::Display for ServiceName {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl AsRef<str> for ServiceName {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum JobType {
    OneTime,
    IntervalBased,
}

impl JobType {
    pub fn as_str(&self) -> &'static str {
        match self {
            JobType::OneTime => "one_time",
            JobType::IntervalBased => "interval_based",
        }
    }
}

impl From<&str> for JobType {
    fn from(s: &str) -> Self {
        match s {
            "one_time" => JobType::OneTime,
            _ => JobType::IntervalBased,
        }
    }
}

impl fmt::Display for JobType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OnMissedPolicy {
    Skip,
    RunOnce,
}

impl OnMissedPolicy {
    pub fn as_str(&self) -> &'static str {
        match self {
            OnMissedPolicy::Skip => "skip",
            OnMissedPolicy::RunOnce => "run_once",
        }
    }
}

impl From<&str> for OnMissedPolicy {
    fn from(s: &str) -> Self {
        match s {
            "skip" => OnMissedPolicy::Skip,
            _ => OnMissedPolicy::RunOnce,
        }
    }
}

pub mod outcome {
    pub const RUNNING: &str = "running";
    pub const EXECUTED: &str = "ok";
    pub const SKIPPED_ALREADY_IN_FLIGHT: &str = "skipped_already_in_flight";
    pub const SKIPPED_HOLIDAY: &str = "skipped_holiday";
    pub const TIMEOUT: &str = "timeout";
    pub const MISSED_CATCHUP: &str = "missed_catchup";
}

pub struct FireBatch {
    pub job_id: JobId,
    pub name: String,
    pub service: ServiceName,
    pub extra: Option<String>,
    pub job_type: JobType,
    pub current_run: u32,
}
