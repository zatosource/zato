//! Scheduler job definitions with timezone handling and holiday calendars.

use std::collections::HashMap;
use std::sync::LazyLock;

use serde::{Deserialize, Serialize};
use super::defaults::{default_true, default_job_type, next_id};

/// IANA timezone aliases where the canonical name differs from the commonly used one.
static TZ_ALIASES: LazyLock<HashMap<&'static str, &'static str>> = LazyLock::new(|| {
    HashMap::from([
        ("Europe/Reykjavik", "Atlantic/Reykjavik"),
    ])
});

/// A scheduler job that fires at a configured interval, one-time, or cron-like schedule.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedulerJob {
    #[serde(default)]
    pub id: i64,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    /// Zato service to invoke on each job execution.
    #[serde(default)]
    pub service: String,
    /// `interval_based`, `one_time` or `cron_style`.
    #[serde(default = "default_job_type")]
    pub job_type: String,
    #[serde(default)]
    pub start_date: String,
    /// Opaque payload passed to the service on each invocation.
    #[serde(default)]
    pub extra: Option<String>,
    #[serde(default)]
    pub weeks: Option<u32>,
    #[serde(default)]
    pub days: Option<u32>,
    #[serde(default)]
    pub hours: Option<u32>,
    #[serde(default)]
    pub minutes: Option<u32>,
    #[serde(default)]
    pub seconds: Option<u32>,
    /// Maximum number of times the job fires before being deactivated.
    #[serde(default)]
    pub repeats: Option<u32>,
    /// Random jitter added to each invocation to spread load.
    #[serde(default)]
    pub jitter_ms: Option<u32>,
    /// IANA timezone for schedule evaluation (resolved through `TZ_ALIASES`).
    #[serde(default)]
    pub timezone: Option<String>,
    /// Name of a holiday calendar that suppresses execution on holidays.
    #[serde(default)]
    pub calendar: Option<String>,
    /// What to do when a scheduled run was missed (e.g. `run_once`, `skip`).
    #[serde(default)]
    pub on_missed: Option<String>,
    /// Maximum allowed execution time before the job is forcefully stopped.
    #[serde(default)]
    pub max_execution_time_ms: Option<u64>,
}

impl SchedulerJob {
    /// Returns the IANA timezone, resolving through known aliases.
    pub fn iana_timezone(&self) -> Option<&str> {
        self.timezone.as_deref().map(|zone| TZ_ALIASES.get(zone).copied().unwrap_or(zone))
    }
}

/// A named set of dates and weekdays on which scheduler jobs should not fire.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HolidayCalendar {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    /// Specific dates (ISO 8601) on which jobs are suppressed.
    #[serde(default)]
    pub dates: Vec<String>,
    /// Days of the week (0=Monday through 6=Sunday) on which jobs are suppressed.
    #[serde(default)]
    pub weekdays: Vec<u8>,
    #[serde(default)]
    pub description: Option<String>,
}
