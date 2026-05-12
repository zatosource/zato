//! Data types for scheduler job and calendar definitions.

use serde::{Deserialize, Deserializer, Serialize};

/// Deserializes a value that may arrive as a number or a string representation of a number.
///
/// Empty strings and null are treated as `None`.
fn deserialize_optional_number_or_string<'de, D, T>(deserializer: D) -> Result<Option<T>, D::Error>
where
    D: Deserializer<'de>,
    T: std::str::FromStr + Deserialize<'de>,
    T::Err: std::fmt::Display,
{
    use serde::de;

    #[derive(Deserialize)]
    #[serde(untagged)]
    enum NumberOrString<T> {
        Number(T),
        Str(String),
        Null,
    }

    match NumberOrString::<T>::deserialize(deserializer)? {
        NumberOrString::Number(val) => Ok(Some(val)),
        NumberOrString::Str(text) => {
            let trimmed = text.trim();
            if trimmed.is_empty() {
                Ok(None)
            } else {
                trimmed.parse::<T>().map(Some).map_err(de::Error::custom)
            }
        }
        NumberOrString::Null => Ok(None),
    }
}

/// Deserializes a string field where empty strings should become `None`.
fn deserialize_optional_empty_string<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: Deserializer<'de>,
{
    let val: Option<String> = Option::deserialize(deserializer)?;
    match val {
        Some(text) if text.trim().is_empty() => Ok(None),
        other => Ok(other),
    }
}

/// A scheduler job loaded from the ODB.
#[derive(Debug, Clone, Serialize, Deserialize)]
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
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub weeks: Option<u32>,
    /// Interval days component.
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub days: Option<u32>,
    /// Interval hours component.
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub hours: Option<u32>,
    /// Interval minutes component.
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub minutes: Option<u32>,
    /// Interval seconds component.
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub seconds: Option<u32>,
    /// Maximum number of times the job fires.
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub repeats: Option<u32>,
    /// Random jitter added to each firing (ms).
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub jitter_ms: Option<u32>,
    /// IANA timezone for schedule evaluation.
    #[serde(default, deserialize_with = "deserialize_optional_empty_string")]
    pub timezone: Option<String>,
    /// Name of the holiday calendar to skip.
    #[serde(default, deserialize_with = "deserialize_optional_empty_string")]
    pub calendar: Option<String>,
    /// Kill threshold for long-running invocations (ms).
    #[serde(default, deserialize_with = "deserialize_optional_number_or_string")]
    pub max_execution_time_ms: Option<u64>,
    /// Service to invoke when the job completes successfully.
    #[serde(default, deserialize_with = "deserialize_optional_empty_string")]
    pub on_success_service: Option<String>,
    /// Scheduler job to execute when the job completes successfully.
    #[serde(default, deserialize_with = "deserialize_optional_empty_string")]
    pub on_success_job: Option<String>,
    /// Service to invoke when the job raises an exception.
    #[serde(default, deserialize_with = "deserialize_optional_empty_string")]
    pub on_error_service: Option<String>,
    /// Scheduler job to execute when the job raises an exception.
    #[serde(default, deserialize_with = "deserialize_optional_empty_string")]
    pub on_error_job: Option<String>,
}

/// A named set of holidays and weekday rules.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HolidayCalendar {
    /// Human-readable calendar description.
    pub description: Option<String>,
    /// Specific dates to skip (ISO format strings parsed into `NaiveDate`).
    pub dates: Vec<String>,
    /// Weekday numbers (0=Mon .. 6=Sun) on which jobs should not fire.
    pub weekdays: Vec<u8>,
}
