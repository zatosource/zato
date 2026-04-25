//! Data types for scheduler job and calendar definitions.

/// A scheduler job loaded from the ODB.
#[derive(Debug, Clone)]
pub struct SchedulerJob {
    /// ODB primary key.
    pub id: i64,
    /// Human-readable job name.
    pub name: String,
    /// Whether the job is enabled.
    pub is_active: bool,
    /// Zato service to invoke on each firing.
    pub service: String,
    /// One of `interval_based`, `cron_style`, or `one_time`.
    pub job_type: String,
    /// ISO datetime string for the first firing.
    pub start_date: String,
    /// Opaque payload passed to the service.
    pub extra: Option<String>,
    /// Interval weeks component.
    pub weeks: Option<u32>,
    /// Interval days component.
    pub days: Option<u32>,
    /// Interval hours component.
    pub hours: Option<u32>,
    /// Interval minutes component.
    pub minutes: Option<u32>,
    /// Interval seconds component.
    pub seconds: Option<u32>,
    /// Maximum number of times the job fires.
    pub repeats: Option<u32>,
    /// Random jitter added to each firing (ms).
    pub jitter_ms: Option<u32>,
    /// IANA timezone for schedule evaluation.
    pub timezone: Option<String>,
    /// Name of the holiday calendar to skip.
    pub calendar: Option<String>,
    /// Policy when a firing is missed (`run_once`, `skip`, `run_all`).
    pub on_missed: Option<String>,
    /// Kill threshold for long-running invocations (ms).
    pub max_execution_time_ms: Option<u64>,
}

/// A named set of holidays and weekday rules.
#[derive(Debug, Clone)]
pub struct HolidayCalendar {
    /// Human-readable calendar description.
    pub description: Option<String>,
    /// Specific dates to skip (ISO format strings parsed into `NaiveDate`).
    pub dates: Vec<String>,
    /// Weekday numbers (0=Mon .. 6=Sun) on which jobs should not fire.
    pub weekdays: Vec<u8>,
}
