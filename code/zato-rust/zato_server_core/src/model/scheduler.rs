use std::collections::HashMap;
use std::sync::LazyLock;

use serde::{Deserialize, Serialize};
use super::defaults::*;

static TZ_ALIASES: LazyLock<HashMap<&'static str, &'static str>> = LazyLock::new(|| {
    HashMap::from([
        ("Europe/Reykjavik", "Atlantic/Reykjavik"),
    ])
});

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedulerJob {
    #[serde(default)]
    pub id: i64,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub service: String,
    #[serde(default = "default_job_type")]
    pub job_type: String,
    #[serde(default)]
    pub start_date: String,
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
    #[serde(default)]
    pub repeats: Option<u32>,
    #[serde(default)]
    pub jitter_ms: Option<u32>,
    #[serde(default)]
    pub timezone: Option<String>,
    #[serde(default)]
    pub calendar: Option<String>,
    #[serde(default)]
    pub on_missed: Option<String>,
    #[serde(default)]
    pub max_execution_time_ms: Option<u64>,
}

impl SchedulerJob {
    pub fn iana_timezone(&self) -> Option<&str> {
        self.timezone.as_deref().map(|tz| TZ_ALIASES.get(tz).copied().unwrap_or(tz))
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HolidayCalendar {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub dates: Vec<String>,
    #[serde(default)]
    pub weekdays: Vec<u8>,
    #[serde(default)]
    pub description: Option<String>,
}
