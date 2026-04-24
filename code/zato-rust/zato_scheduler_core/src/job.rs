use std::collections::VecDeque;
use std::time::Instant;

use chrono::{DateTime, LocalResult, TimeZone, Utc};
use chrono_tz::Tz;
use rand::rngs::SmallRng;
use rand::{RngExt, SeedableRng};

use zato_server_core::model::SchedulerJob;

use crate::types::{JobId, JobType, OnMissedPolicy, ServiceName};

pub const DEFAULT_MAX_EXECUTION_TIME_MS: u64 = 3_600_000;
pub const DEFAULT_MAX_HISTORY: usize = 10_000;
pub const DEFAULT_ON_MISSED: &str = "run_once";

pub const MIN_MAX_EXECUTION_TIME_MS: u64 = 1_000;
pub const MAX_MAX_EXECUTION_TIME_MS: u64 = 86_400_000;

#[derive(Debug, Clone)]
pub struct ExecutionRecord {
    pub planned_fire_time_iso: String,
    pub actual_fire_time_iso: String,
    pub delay_ms: u64,
    pub outcome: String,
    pub current_run: u32,
    pub duration_ms: Option<u64>,
    pub error: Option<String>,
    pub outcome_ctx: Option<String>,
}

impl ExecutionRecord {
    pub fn new(planned: &str, actual: &str, outcome: &str, current_run: u32) -> Self {
        ExecutionRecord {
            planned_fire_time_iso: planned.to_string(),
            actual_fire_time_iso: actual.to_string(),
            delay_ms: 0,
            outcome: outcome.to_string(),
            current_run,
            duration_ms: None,
            error: None,
            outcome_ctx: None,
        }
    }

    pub fn with_delay(mut self, delay_ms: u64) -> Self {
        self.delay_ms = delay_ms;
        self
    }

    pub fn with_outcome_ctx(mut self, ctx: String) -> Self {
        self.outcome_ctx = Some(ctx);
        self
    }

    pub fn with_duration(mut self, duration_ms: u64) -> Self {
        self.duration_ms = Some(duration_ms);
        self
    }

    pub fn with_error(mut self, error: String) -> Self {
        self.error = Some(error);
        self
    }

}

#[derive(Debug)]
pub struct RunningJob {
    pub id: JobId,
    pub name: String,
    pub is_active: bool,
    pub service: ServiceName,
    pub extra: Option<String>,
    pub job_type: JobType,
    pub start_date: Option<DateTime<Utc>>,
    pub interval_ms: u64,
    pub repeats: Option<u32>,
    pub jitter_ms: Option<u32>,
    pub timezone: Option<Tz>,
    pub timezone_str: Option<String>,
    pub calendar: Option<String>,
    pub on_missed: OnMissedPolicy,
    pub max_execution_time_ms: u64,

    pub next_fire_utc: Option<DateTime<Utc>>,
    pub next_fire_instant: Option<Instant>,
    pub in_flight: bool,
    pub in_flight_since: Option<Instant>,
    pub in_flight_run: Option<u32>,
    pub current_run: u32,

    pub history: VecDeque<ExecutionRecord>,
    pub max_history: usize,

    jitter_rng: SmallRng,
}

pub fn clamp_max_execution_time(raw: u64, job_name: &str) -> u64 {
    if raw < MIN_MAX_EXECUTION_TIME_MS {
        log::warn!(
            "Job `{}`: max_execution_time_ms={} below minimum, clamped to {}",
            job_name, raw, MIN_MAX_EXECUTION_TIME_MS
        );
        return MIN_MAX_EXECUTION_TIME_MS;
    }
    if raw > MAX_MAX_EXECUTION_TIME_MS {
        log::warn!(
            "Job `{}`: max_execution_time_ms={} above maximum, clamped to {}",
            job_name, raw, MAX_MAX_EXECUTION_TIME_MS
        );
        return MAX_MAX_EXECUTION_TIME_MS;
    }
    raw
}

impl RunningJob {

    pub fn from_scheduler_job(job: &SchedulerJob) -> Self {
        let interval_ms = Self::compute_interval_ms(job);
        let tz: Option<Tz> = match job.timezone.as_deref() {
            Some(s) => match s.parse::<Tz>() {
                Ok(tz) => Some(tz),
                Err(_) => {
                    log::error!("Job `{}`: invalid timezone `{}`", job.name, s);
                    None
                }
            },
            None => None,
        };
        let tz_str = job.timezone.clone();
        let start_date = match Self::parse_start_date(&job.start_date, tz.as_ref()) {
            Some(dt) => Some(dt),
            None => {
                log::error!("Job `{}`: failed to parse start_date `{}`", job.name, job.start_date);
                Some(Utc::now())
            }
        };
        let seed = job.id as u64;
        let jitter_rng = SmallRng::seed_from_u64(seed);
        let on_missed = OnMissedPolicy::from(
            job.on_missed.as_deref().unwrap_or(DEFAULT_ON_MISSED)
        );
        let max_exec = clamp_max_execution_time(
            job.max_execution_time_ms.unwrap_or(DEFAULT_MAX_EXECUTION_TIME_MS),
            &job.name,
        );

        let mut running_job = RunningJob {
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
            timezone: tz,
            timezone_str: tz_str,
            calendar: job.calendar.clone(),
            on_missed,
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

    pub fn update_from_job(&mut self, job: &SchedulerJob) {
        self.name = job.name.clone();
        self.is_active = job.is_active;
        self.service = ServiceName(job.service.clone());
        self.extra = job.extra.clone();
        self.job_type = JobType::from(job.job_type.as_str());
        self.calendar = job.calendar.clone();
        self.on_missed = OnMissedPolicy::from(
            job.on_missed.as_deref().unwrap_or(DEFAULT_ON_MISSED)
        );
        self.max_execution_time_ms = clamp_max_execution_time(
            job.max_execution_time_ms.unwrap_or(DEFAULT_MAX_EXECUTION_TIME_MS),
            &job.name,
        );
        self.repeats = job.repeats;

        let new_interval = Self::compute_interval_ms(job);
        let new_tz: Option<Tz> = match job.timezone.as_deref() {
            Some(s) => match s.parse::<Tz>() {
                Ok(tz) => Some(tz),
                Err(_) => {
                    log::error!("Job `{}`: invalid timezone `{}`", self.name, s);
                    None
                }
            },
            None => None,
        };
        let new_start = match Self::parse_start_date(&job.start_date, new_tz.as_ref()) {
            Some(dt) => Some(dt),
            None => {
                log::error!("Job `{}`: failed to parse start_date `{}`", self.name, job.start_date);
                Some(Utc::now())
            }
        };

        let schedule_changed = new_interval != self.interval_ms
            || new_start != self.start_date
            || new_tz != self.timezone
            || job.jitter_ms != self.jitter_ms;

        self.interval_ms = new_interval;
        self.timezone = new_tz;
        self.timezone_str = job.timezone.clone();
        self.start_date = new_start;

        if job.jitter_ms != self.jitter_ms {
            self.jitter_ms = job.jitter_ms;
            self.jitter_rng = SmallRng::seed_from_u64(self.id.0 as u64);
        }

        if schedule_changed && self.is_active {
            self.compute_next_fire(Utc::now());
        } else if !self.is_active {
            self.next_fire_utc = None;
            self.next_fire_instant = None;
        }
    }

    pub fn compute_next_fire(&mut self, now: DateTime<Utc>) {
        match self.job_type {
            JobType::OneTime => {
                if let Some(sd) = self.start_date {
                    if sd > now {
                        self.next_fire_utc = Some(sd);
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
                    if let Some(sd) = self.start_date {
                        let n = self.find_next_n(sd, now);
                        let base_ms = n * self.interval_ms;
                        let jitter = self.compute_jitter();
                        self.next_fire_utc = Some(sd + chrono::Duration::milliseconds((base_ms + jitter) as i64));
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

    pub fn advance_to_next(&mut self, now: DateTime<Utc>) {
        if self.job_type == JobType::OneTime {
            self.next_fire_utc = None;
            self.next_fire_instant = None;
            return;
        }
        if let Some(max) = self.repeats {
            if self.current_run >= max {
                self.next_fire_utc = None;
                self.next_fire_instant = None;
                return;
            }
        }
        self.compute_next_fire(now);
    }

    pub fn record_execution(&mut self, record: ExecutionRecord) {
        if self.history.len() >= self.max_history {
            self.history.pop_front();
        }
        self.history.push_back(record);
    }

    pub fn is_holiday_today(&self, calendars: &std::collections::HashMap<String, super::calendar::CalendarData>) -> bool {
        let Some(ref cal_name) = self.calendar else { return false };
        let Some(cal) = calendars.get(cal_name) else { return false };
        let today: chrono::NaiveDate = if let Some(ref tz) = self.timezone {
            Utc::now().with_timezone(tz).date_naive()
        } else {
            Utc::now().date_naive()
        };
        cal.is_excluded(today)
    }

    pub fn sync_instant_from_utc_pub(&mut self, now: DateTime<Utc>) {
        self.sync_instant_from_utc(now);
    }

    fn find_next_n(&self, start: DateTime<Utc>, now: DateTime<Utc>) -> u64 {
        if now <= start {
            return 0;
        }
        let elapsed_ms = (now - start).num_milliseconds().max(0) as u64;
        let n = elapsed_ms / self.interval_ms;
        let candidate = start + chrono::Duration::milliseconds((n * self.interval_ms) as i64);
        if candidate <= now { n + 1 } else { n }
    }

    fn compute_jitter(&mut self) -> u64 {
        match self.jitter_ms {
            Some(j) if j > 0 => self.jitter_rng.random_range(0..j as u64),
            _ => 0,
        }
    }

    fn sync_instant_from_utc(&mut self, now: DateTime<Utc>) {
        self.next_fire_instant = self.next_fire_utc.map(|fire_utc| {
            let diff_ms = (fire_utc - now).num_milliseconds().max(0) as u64;
            Instant::now() + std::time::Duration::from_millis(diff_ms)
        });
    }

    pub fn compute_interval_ms(job: &SchedulerJob) -> u64 {
        let w = job.weeks.unwrap_or(0) as u64 * 7 * 86_400_000;
        let d = job.days.unwrap_or(0) as u64 * 86_400_000;
        let h = job.hours.unwrap_or(0) as u64 * 3_600_000;
        let m = job.minutes.unwrap_or(0) as u64 * 60_000;
        let s = job.seconds.unwrap_or(0) as u64 * 1_000;
        w + d + h + m + s
    }

    fn parse_start_date(s: &str, tz: Option<&Tz>) -> Option<DateTime<Utc>> {
        if s.is_empty() {
            return None;
        }
        let clean = s.split('+').next().unwrap().trim_end_matches('Z');
        let formats = [
            "%Y-%m-%dT%H:%M:%S%.f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S%.f",
            "%Y-%m-%d %H:%M:%S",
        ];
        for fmt in &formats {
            if let Ok(naive) = chrono::NaiveDateTime::parse_from_str(clean, fmt) {
                if let Some(tz_ref) = tz {
                    return Self::naive_to_utc_in_tz(naive, tz_ref);
                }
                return Some(DateTime::<Utc>::from_naive_utc_and_offset(naive, Utc));
            }
        }
        None
    }

    fn local_result_to_utc(lr: LocalResult<DateTime<Tz>>) -> Option<DateTime<Utc>> {
        match lr {
            LocalResult::Single(dt) | LocalResult::Ambiguous(dt, _) => Some(dt.with_timezone(&Utc)),
            LocalResult::None => None,
        }
    }

    fn naive_to_utc_in_tz(naive: chrono::NaiveDateTime, tz: &Tz) -> Option<DateTime<Utc>> {
        if let Some(utc) = Self::local_result_to_utc(tz.from_local_datetime(&naive)) {
            return Some(utc);
        }
        let advanced = naive + chrono::Duration::hours(1);
        if let Some(utc) = Self::local_result_to_utc(tz.from_local_datetime(&advanced)) {
            return Some(utc);
        }
        Some(DateTime::<Utc>::from_naive_utc_and_offset(naive, Utc))
    }

}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_interval_ms() {
        let job = SchedulerJob {
            id: 1, name: "t".into(), is_active: true,
            service: "s".into(), job_type: "interval_based".into(),
            start_date: "2026-01-01T00:00:00".into(),
            extra: None, weeks: Some(1), days: Some(2), hours: Some(3),
            minutes: Some(4), seconds: Some(5), repeats: None,
            jitter_ms: None, timezone: None, calendar: None,
            on_missed: None, max_execution_time_ms: None,
        };
        let ms = RunningJob::compute_interval_ms(&job);
        let expected = 1u64 * 7 * 86_400_000
            + 2 * 86_400_000
            + 3 * 3_600_000
            + 4 * 60_000
            + 5 * 1_000;
        assert_eq!(ms, expected);
    }

    #[test]
    fn test_parse_start_date_iso() {
        let dt = RunningJob::parse_start_date("2026-04-10T12:00:00", None);
        assert!(dt.is_some());
    }

}
