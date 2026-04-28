//! Runtime job representation and schedule computation.

use std::collections::VecDeque;
use std::time::Instant;

use chrono::{DateTime, LocalResult, TimeZone, Utc};
use rand::rngs::SmallRng;
use rand::{RngExt, SeedableRng};
use serde::Serialize;

/// Alias for the chrono timezone type.
type Timezone = chrono_tz::Tz;

use crate::model::SchedulerJob;
use crate::types::{JobId, JobType, ServiceName};

/// Default maximum execution time for a job (1 hour in ms).
pub const DEFAULT_MAX_EXECUTION_TIME_MS: u64 = 3_600_000;

/// Default maximum number of history records kept per job.
pub const DEFAULT_MAX_HISTORY: usize = 10_000;

/// Minimum allowed `max_execution_time_ms` (1 second).
pub const MIN_MAX_EXECUTION_TIME_MS: u64 = 1_000;

/// Maximum allowed `max_execution_time_ms` (24 hours).
pub const MAX_MAX_EXECUTION_TIME_MS: u64 = 86_400_000;

/// Number of distinct outcome labels tracked per job.
pub const OUTCOME_COUNT: usize = crate::types::outcome::COUNTABLE.len();

/// Computed summary of a scheduler job for the dashboard API.
///
/// Contains both static job metadata and derived stats from execution history.
/// Built by `RunningJob::summary()` under the state mutex, then serialized
/// to JSON for the HTTP query API.
#[derive(Serialize)]
pub struct JobSummary {
    /// Unique job identifier.
    pub id: i64,
    /// Human-readable job name.
    pub name: String,
    /// Whether the job is enabled.
    pub is_active: bool,
    /// Zato service to invoke.
    pub service: String,
    /// Job type label (e.g. "`interval_based`").
    pub job_type: String,
    /// Whether the job is currently executing.
    pub in_flight: bool,
    /// Current run counter.
    pub current_run: u32,
    /// Computed interval between firings (ms).
    pub interval_ms: u64,
    /// Next scheduled fire time as an ISO string, if any.
    pub next_fire_utc: Option<String>,
    /// Outcome label of the most recent execution, if any.
    pub last_outcome: Option<String>,
    /// Duration of the most recent completed execution (ms), if any.
    pub last_duration_ms: Option<u64>,
    /// Outcome labels of the last 10 executions (most recent last).
    pub recent_outcomes: Vec<String>,
    /// Per-outcome execution counts, indexed by `COUNTABLE` position.
    pub outcome_counts: [usize; OUTCOME_COUNT],
}

/// A single timeline event combining job metadata with an execution record.
///
/// Built under the state mutex by cloning job fields and the record,
/// then serialized to JSON for the HTTP query API.
#[derive(Serialize)]
pub struct TimelineEvent {
    /// Unique job identifier.
    pub job_id: i64,
    /// Human-readable job name.
    pub job_name: String,
    /// Cloned execution record.
    pub record: ExecutionRecord,
}

/// A single log entry captured from a service during scheduler-initiated execution.
#[derive(Debug, Clone, Serialize)]
pub struct LogEntry {
    /// ISO timestamp of when the log record was created.
    pub timestamp_iso: String,
    /// Log level name (INFO, WARNING, ERROR, etc.).
    pub level: String,
    /// Formatted log message text.
    pub message: String,
}

/// A single execution history record for a job firing.
#[derive(Debug, Clone, Serialize)]
pub struct ExecutionRecord {
    /// ISO timestamp of the planned fire time.
    pub planned_fire_time_iso: String,
    /// ISO timestamp of the actual fire time.
    pub actual_fire_time_iso: String,
    /// Delay between planned and actual fire times (ms).
    pub delay_ms: u64,
    /// Outcome label for this execution.
    pub outcome: String,
    /// Run counter at the time of this execution.
    pub current_run: u32,
    /// Wall-clock duration of the execution (ms), if completed.
    pub duration_ms: Option<u64>,
    /// Error message, if the execution failed.
    pub error: Option<String>,
    /// Additional context for the outcome.
    pub outcome_ctx: Option<String>,
    /// Log entries captured from the service during this execution.
    pub log_entries: Vec<LogEntry>,
}

impl ExecutionRecord {
    /// Creates a new record with the given planned/actual times, outcome and run number.
    #[must_use]
    pub fn new(planned: &str, actual: &str, outcome: &str, current_run: u32) -> Self {
        Self {
            planned_fire_time_iso: planned.to_string(),
            actual_fire_time_iso: actual.to_string(),
            delay_ms: 0,
            outcome: outcome.to_string(),
            current_run,
            duration_ms: None,
            error: None,
            outcome_ctx: None,
            log_entries: Vec::new(),
        }
    }

    /// Sets the delay and returns `self` for chaining.
    #[must_use]
    pub const fn with_delay(mut self, delay_ms: u64) -> Self {
        self.delay_ms = delay_ms;
        self
    }

    /// Sets the outcome context and returns `self` for chaining.
    #[must_use]
    pub fn with_outcome_ctx(mut self, ctx: String) -> Self {
        self.outcome_ctx = Some(ctx);
        self
    }

    /// Sets the duration and returns `self` for chaining.
    #[must_use]
    pub const fn with_duration(mut self, duration_ms: u64) -> Self {
        self.duration_ms = Some(duration_ms);
        self
    }

    /// Sets the error message and returns `self` for chaining.
    #[must_use]
    pub fn with_error(mut self, error: String) -> Self {
        self.error = Some(error);
        self
    }
}

/// A job that is actively managed by the scheduler runtime.
#[derive(Debug)]
pub struct RunningJob {
    /// Unique job identifier.
    pub id: JobId,
    /// Human-readable job name.
    pub name: String,
    /// Whether the job is enabled.
    pub is_active: bool,
    /// Zato service to invoke.
    pub service: ServiceName,
    /// Opaque payload passed to the service.
    pub extra: Option<String>,
    /// Whether this is a one-time or interval-based job.
    pub job_type: JobType,
    /// UTC datetime of the first firing.
    pub start_date: Option<DateTime<Utc>>,
    /// Computed interval between firings (ms).
    pub interval_ms: u64,
    /// Maximum number of firings allowed.
    pub repeats: Option<u32>,
    /// Random jitter added to each firing (ms).
    pub jitter_ms: Option<u32>,
    /// IANA timezone for schedule evaluation.
    pub timezone: Option<Timezone>,
    /// String representation of the timezone.
    pub timezone_str: Option<String>,
    /// Name of the holiday calendar to honour.
    pub calendar: Option<String>,
    /// Kill threshold for long-running invocations (ms).
    pub max_execution_time_ms: u64,

    /// Next scheduled fire time in UTC.
    pub next_fire_utc: Option<DateTime<Utc>>,
    /// Monotonic instant corresponding to `next_fire_utc`.
    pub next_fire_instant: Option<Instant>,
    /// Whether the job is currently executing.
    pub in_flight: bool,
    /// Monotonic instant when in-flight execution started.
    pub in_flight_since: Option<Instant>,
    /// Run number of the in-flight execution.
    pub in_flight_run: Option<u32>,
    /// Number of times this job has fired.
    pub current_run: u32,

    /// Circular buffer of execution history records.
    pub history: VecDeque<ExecutionRecord>,
    /// Maximum number of history records to retain.
    pub max_history: usize,

    /// PRNG used to compute per-firing jitter.
    jitter_rng: SmallRng,
}

/// Clamps `raw` to the allowed `[MIN, MAX]` execution-time range, logging if clamped.
#[must_use]
pub fn clamp_max_execution_time(raw: u64, job_name: &str) -> u64 {
    if raw < MIN_MAX_EXECUTION_TIME_MS {
        tracing::warn!("Job `{job_name}`: max_execution_time_ms={raw} below minimum, clamped to {MIN_MAX_EXECUTION_TIME_MS}");
        return MIN_MAX_EXECUTION_TIME_MS;
    }
    if raw > MAX_MAX_EXECUTION_TIME_MS {
        tracing::warn!("Job `{job_name}`: max_execution_time_ms={raw} above maximum, clamped to {MAX_MAX_EXECUTION_TIME_MS}");
        return MAX_MAX_EXECUTION_TIME_MS;
    }
    raw
}

/// Parses a timezone string and start-date string into their resolved forms.
///
/// Falls back to `Utc::now()` if the start date cannot be parsed, logging the error.
fn resolve_tz_and_start(
    tz_str: Option<&str>,
    start_date_str: &str,
    job_name: &str,
) -> (Option<Timezone>, Option<String>, Option<DateTime<Utc>>) {
    let timezone: Option<Timezone> = tz_str.and_then(|val| {
        val.parse::<Timezone>().map_or_else(
            |_| {
                tracing::error!("Job `{job_name}`: invalid timezone `{val}`");
                None
            },
            Some,
        )
    });
    let start_date = RunningJob::parse_start_date(start_date_str, timezone.as_ref()).map_or_else(
        || {
            tracing::error!("Job `{job_name}`: failed to parse start_date `{start_date_str}`");
            Some(Utc::now())
        },
        Some,
    );
    (timezone, tz_str.map(String::from), start_date)
}

impl RunningJob {
    /// Constructs a `RunningJob` from a `SchedulerJob` definition.
    #[must_use]
    pub fn from_scheduler_job(job: &SchedulerJob) -> Self {
        let interval_ms = Self::compute_interval_ms(job);
        let (timezone, tz_str, start_date) = resolve_tz_and_start(job.timezone.as_deref(), &job.start_date, &job.name);
        let seed = job.id.unsigned_abs();
        let jitter_rng = SmallRng::seed_from_u64(seed);
        let max_exec = clamp_max_execution_time(job.max_execution_time_ms.unwrap_or(DEFAULT_MAX_EXECUTION_TIME_MS), &job.name);

        let mut running_job = Self {
            id: JobId(job.id),
            name: job.name.clone(),
            is_active: job.is_active,
            service: ServiceName(job.service.clone()),
            extra: job.extra.clone(),
            job_type: JobType::from(job.job_type.as_str()),
            start_date,
            interval_ms,
            repeats: job.repeats,
            jitter_ms: job.jitter_ms,
            timezone,
            timezone_str: tz_str,
            calendar: job.calendar.clone(),
            max_execution_time_ms: max_exec,
            next_fire_utc: None,
            next_fire_instant: None,
            in_flight: false,
            in_flight_since: None,
            in_flight_run: None,
            current_run: 0,
            history: VecDeque::with_capacity(DEFAULT_MAX_HISTORY),
            max_history: DEFAULT_MAX_HISTORY,
            jitter_rng,
        };
        if running_job.is_active {
            running_job.compute_next_fire(Utc::now());
        }
        running_job
    }

    /// Applies changes from an updated `SchedulerJob` definition, recomputing the schedule if needed.
    pub fn update_from_job(&mut self, job: &SchedulerJob) {
        self.name.clone_from(&job.name);
        self.is_active = job.is_active;
        self.service = ServiceName(job.service.clone());
        self.extra.clone_from(&job.extra);
        self.job_type = JobType::from(job.job_type.as_str());
        self.calendar.clone_from(&job.calendar);
        self.max_execution_time_ms =
            clamp_max_execution_time(job.max_execution_time_ms.unwrap_or(DEFAULT_MAX_EXECUTION_TIME_MS), &job.name);
        self.repeats = job.repeats;

        let new_interval = Self::compute_interval_ms(job);
        let (new_timezone, _new_tz_str, new_start) = resolve_tz_and_start(job.timezone.as_deref(), &job.start_date, &self.name);

        let schedule_changed = new_interval != self.interval_ms
            || new_start != self.start_date
            || new_timezone != self.timezone
            || job.jitter_ms != self.jitter_ms;

        self.interval_ms = new_interval;
        self.timezone = new_timezone;
        self.timezone_str.clone_from(&job.timezone);
        self.start_date = new_start;

        if job.jitter_ms != self.jitter_ms {
            self.jitter_ms = job.jitter_ms;
            self.jitter_rng = SmallRng::seed_from_u64(self.id.0.unsigned_abs());
        }

        if schedule_changed && self.is_active {
            self.compute_next_fire(Utc::now());
        } else if !self.is_active {
            self.next_fire_utc = None;
            self.next_fire_instant = None;
        }
    }

    /// Computes the next fire time from `now` based on job type and interval.
    pub fn compute_next_fire(&mut self, now: DateTime<Utc>) {
        match self.job_type {
            JobType::OneTime => {
                if let Some(start) = self.start_date {
                    if start > now {
                        self.next_fire_utc = Some(start);
                    } else if self.current_run == 0 {
                        self.next_fire_utc = Some(now);
                    } else {
                        self.next_fire_utc = None;
                    }
                } else {
                    self.next_fire_utc = None;
                }
            }
            JobType::IntervalBased => {
                if self.interval_ms > 0 {
                    if let Some(start) = self.start_date {
                        let nth = self.find_next_n(start, now);
                        let base_ms = nth * self.interval_ms;
                        let jitter = self.compute_jitter();
                        let total_ms = i64::try_from(base_ms + jitter).unwrap_or(i64::MAX);
                        let new_fire = start + chrono::Duration::milliseconds(total_ms);
                        self.next_fire_utc = Some(new_fire);
                    } else {
                        self.next_fire_utc = None;
                    }
                } else {
                    self.next_fire_utc = None;
                }
            }
        }
        self.sync_instant_from_utc(now);
    }

    /// Advances to the next fire time after the current run completes.
    pub fn advance_to_next(&mut self, now: DateTime<Utc>) {
        if self.job_type == JobType::OneTime {
            self.next_fire_utc = None;
            self.next_fire_instant = None;
            return;
        }
        if let Some(max) = self.repeats
            && self.current_run >= max
        {
            self.next_fire_utc = None;
            self.next_fire_instant = None;
            return;
        }
        let reference = match self.next_fire_utc {
            Some(fire) if fire > now => fire,
            _ => now,
        };
        self.compute_next_fire(reference);
    }

    /// Computes a `JobSummary` snapshot from the current job state and history.
    ///
    /// Intended to be called under the state mutex. The returned value is fully
    /// owned and can be used after the mutex is released.
    #[must_use]
    pub fn summary(&self) -> JobSummary {
        let countable = crate::types::outcome::COUNTABLE;
        let mut outcome_counts = [0usize; OUTCOME_COUNT];

        for rec in &self.history {
            if let Some(pos) = countable.iter().position(|label| *label == rec.outcome)
                && let Some(slot) = outcome_counts.get_mut(pos)
            {
                *slot += 1;
            }
        }

        let last_outcome = self.history.back().map(|rec| rec.outcome.clone());
        let last_duration_ms = self.history.iter().rev().find_map(|rec| rec.duration_ms);

        let recent_start = self.history.len().saturating_sub(10);
        let recent_outcomes: Vec<String> = self.history.range(recent_start..).map(|rec| rec.outcome.clone()).collect();

        JobSummary {
            id: self.id.0,
            name: self.name.clone(),
            is_active: self.is_active,
            service: self.service.0.clone(),
            job_type: self.job_type.as_str().to_owned(),
            in_flight: self.in_flight,
            current_run: self.current_run,
            interval_ms: self.interval_ms,
            next_fire_utc: self.next_fire_utc.map(|fire_dt| fire_dt.to_rfc3339()),
            last_outcome,
            last_duration_ms,
            recent_outcomes,
            outcome_counts,
        }
    }

    /// Appends a record to the execution history, evicting the oldest if at capacity.
    pub fn record_execution(&mut self, record: ExecutionRecord) {
        if self.history.len() >= self.max_history {
            self.history.pop_front();
        }
        self.history.push_back(record);
    }

    /// Returns `true` if today is a holiday according to the job's calendar.
    #[must_use]
    pub fn is_holiday_today(&self, calendars: &std::collections::HashMap<String, super::calendar::CalendarData>) -> bool {
        let Some(ref cal_name) = self.calendar else { return false };
        let Some(cal) = calendars.get(cal_name) else { return false };
        let today: chrono::NaiveDate = self
            .timezone
            .as_ref()
            .map_or_else(|| Utc::now().date_naive(), |zone| Utc::now().with_timezone(zone).date_naive());
        cal.is_excluded(today)
    }

    /// Public wrapper around `sync_instant_from_utc`.
    pub fn sync_instant_from_utc_pub(&mut self, now: DateTime<Utc>) {
        self.sync_instant_from_utc(now);
    }

    /// Finds the next interval multiple `n` such that `start + n * interval > now`.
    fn find_next_n(&self, start: DateTime<Utc>, now: DateTime<Utc>) -> u64 {
        if now <= start {
            return 0;
        }
        let elapsed_ms = (now - start).num_milliseconds().unsigned_abs();
        let nth = elapsed_ms / self.interval_ms;
        let offset_ms = i64::try_from(nth * self.interval_ms).unwrap_or(i64::MAX);
        let candidate = start + chrono::Duration::milliseconds(offset_ms);
        if candidate <= now { nth + 1 } else { nth }
    }

    /// Computes a random jitter value in `[0, jitter_ms)`, or 0 if jitter is not configured.
    fn compute_jitter(&mut self) -> u64 {
        match self.jitter_ms {
            Some(jitter) if jitter > 0 => self.jitter_rng.random_range(0..u64::from(jitter)),
            _ => 0,
        }
    }

    /// Converts `next_fire_utc` to a monotonic `Instant` relative to `now`.
    fn sync_instant_from_utc(&mut self, now: DateTime<Utc>) {
        self.next_fire_instant = self.next_fire_utc.map(|fire_utc| {
            let diff_ms = (fire_utc - now).num_milliseconds().unsigned_abs();
            Instant::now() + std::time::Duration::from_millis(diff_ms)
        });
    }

    /// Computes the total interval in milliseconds from the individual time components.
    #[must_use]
    pub fn compute_interval_ms(job: &SchedulerJob) -> u64 {
        let weeks_ms = u64::from(job.weeks.unwrap_or(0)) * 7 * 86_400_000;
        let days_ms = u64::from(job.days.unwrap_or(0)) * 86_400_000;
        let hours_ms = u64::from(job.hours.unwrap_or(0)) * 3_600_000;
        let mins_ms = u64::from(job.minutes.unwrap_or(0)) * 60_000;
        let secs_ms = u64::from(job.seconds.unwrap_or(0)) * 1_000;
        weeks_ms + days_ms + hours_ms + mins_ms + secs_ms
    }

    /// Parses a start-date string into a UTC `DateTime`, optionally interpreting it in a timezone.
    fn parse_start_date(raw: &str, zone: Option<&Timezone>) -> Option<DateTime<Utc>> {
        if raw.is_empty() {
            return None;
        }
        let clean = raw.split('+').next().unwrap_or(raw).trim_end_matches('Z');
        let formats = [
            "%Y-%m-%dT%H:%M:%S%.f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S%.f",
            "%Y-%m-%d %H:%M:%S",
        ];
        for fmt in &formats {
            if let Ok(naive) = chrono::NaiveDateTime::parse_from_str(clean, fmt) {
                if let Some(tz_ref) = zone {
                    return Some(Self::naive_to_utc_in_tz(naive, *tz_ref));
                }
                return Some(DateTime::<Utc>::from_naive_utc_and_offset(naive, Utc));
            }
        }
        None
    }

    /// Converts a `LocalResult` to a UTC `DateTime`, picking the earliest for ambiguous results.
    fn local_result_to_utc(local_result: LocalResult<DateTime<Timezone>>) -> Option<DateTime<Utc>> {
        match local_result {
            LocalResult::Single(dt) | LocalResult::Ambiguous(dt, _) => Some(dt.with_timezone(&Utc)),
            LocalResult::None => None,
        }
    }

    /// Converts a naive datetime to UTC by interpreting it in a timezone, with a DST-gap fallback.
    fn naive_to_utc_in_tz(naive: chrono::NaiveDateTime, zone: Timezone) -> DateTime<Utc> {
        if let Some(utc) = Self::local_result_to_utc(zone.from_local_datetime(&naive)) {
            return utc;
        }
        let advanced = naive + chrono::Duration::hours(1);
        if let Some(utc) = Self::local_result_to_utc(zone.from_local_datetime(&advanced)) {
            return utc;
        }
        DateTime::<Utc>::from_naive_utc_and_offset(naive, Utc)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_interval_ms() {
        let job = SchedulerJob {
            id: 1,
            name: "t".into(),
            is_active: true,
            service: "s".into(),
            job_type: "interval_based".into(),
            start_date: "2026-01-01T00:00:00".into(),
            extra: None,
            weeks: Some(1),
            days: Some(2),
            hours: Some(3),
            minutes: Some(4),
            seconds: Some(5),
            repeats: None,
            jitter_ms: None,
            timezone: None,
            calendar: None,
            max_execution_time_ms: None,
        };
        let interval = RunningJob::compute_interval_ms(&job);
        let expected = 7u64 * 86_400_000 + 2 * 86_400_000 + 3 * 3_600_000 + 4 * 60_000 + 5 * 1_000;
        assert_eq!(interval, expected);
    }

    #[test]
    fn test_parse_start_date_iso() {
        let dt = RunningJob::parse_start_date("2026-04-10T12:00:00", None);
        assert!(dt.is_some());
    }
}
