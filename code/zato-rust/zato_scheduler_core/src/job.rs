//! Runtime job representation and schedule computation.

use std::collections::BTreeMap;
use std::time::Instant;

use jiff::civil::DateTime;
use jiff::tz::{AmbiguousOffset, TimeZone};
use jiff::{SignedDuration, Timestamp};
use rand::rngs::SmallRng;
use rand::{RngExt, SeedableRng};
use serde::Serialize;

/// Alias for the IANA timezone type.
type Timezone = TimeZone;

/// Formats of the start date of a job, each read as a civil datetime without an offset.
const START_DATE_FORMATS: [&str; 4] = [
    "%Y-%m-%dT%H:%M:%S%.f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S%.f",
    "%Y-%m-%d %H:%M:%S",
];

/// RFC 3339 form of a UTC instant, with the offset written as `+00:00`.
const RFC3339_UTC_FORMAT: &str = "%Y-%m-%dT%H:%M:%S%.f+00:00";

/// Shift applied to a start date that falls into a gap of its timezone, such as the hour skipped by daylight saving time.
const DST_GAP_SHIFT: SignedDuration = SignedDuration::from_hours(1);

/// Formats a UTC instant as RFC 3339, the form in which slots and fire times travel to the server.
#[must_use]
pub fn to_rfc3339(instant: Timestamp) -> String {
    instant.strftime(RFC3339_UTC_FORMAT).to_string()
}

/// Returns the whole milliseconds from `earlier` to `later`, negative when `later` precedes `earlier`.
#[must_use]
pub fn signed_millis(later: Timestamp, earlier: Timestamp) -> i64 {
    let millis = later.duration_since(earlier).as_millis();
    i64::try_from(millis).unwrap_or(if millis < 0 { i64::MIN } else { i64::MAX })
}

/// Returns the whole milliseconds between two instants, regardless of their order.
#[must_use]
pub fn millis_between(first: Timestamp, second: Timestamp) -> u64 {
    let millis = first.duration_since(second).as_millis().unsigned_abs();
    u64::try_from(millis).unwrap_or(u64::MAX)
}

use crate::model::SchedulerJob;
use crate::types::{JobId, JobType, ServiceName};

/// Default maximum execution time for a job (1 hour in ms).
pub const DEFAULT_MAX_EXECUTION_TIME_MS: u64 = 3_600_000;

/// Minimum allowed `max_execution_time_ms` (1 second).
pub const MIN_MAX_EXECUTION_TIME_MS: u64 = 1_000;

/// Maximum allowed `max_execution_time_ms` (24 hours).
pub const MAX_MAX_EXECUTION_TIME_MS: u64 = 86_400_000;

/// Scheduling-state summary of a scheduler job for the dashboard API.
///
/// Execution history lives in the server's audit log - this summary carries
/// only what the scheduler itself owns: the schedule and the in-flight state.
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
    pub start_date: Option<Timestamp>,
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
    /// Kill threshold for long-running invocations (ms).
    pub max_execution_time_ms: u64,
    /// Service to invoke when the job completes successfully.
    pub on_success_service: Option<String>,
    /// Scheduler job to execute when the job completes successfully.
    pub on_success_job: Option<String>,
    /// Service to invoke when the job raises an exception.
    pub on_error_service: Option<String>,
    /// Scheduler job to execute when the job raises an exception.
    pub on_error_job: Option<String>,

    /// Next scheduled fire time in UTC.
    pub next_fire_utc: Option<Timestamp>,
    /// Slot of the schedule that the next firing belongs to, which is its fire time without jitter.
    pub next_nominal_utc: Option<Timestamp>,
    /// Monotonic instant corresponding to `next_fire_utc`.
    pub next_fire_instant: Option<Instant>,
    /// Runs of the job that were fired and whose completion was not reported yet, each by its run number,
    /// with the monotonic instant at which it was fired.
    pub in_flight_runs: BTreeMap<u32, Instant>,
    /// Number of times this job has fired.
    pub current_run: u32,

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
/// Falls back to `Timestamp::now()` if the start date cannot be parsed, logging the error.
fn resolve_tz_and_start(
    tz_str: Option<&str>,
    start_date_str: &str,
    job_name: &str,
) -> (Option<Timezone>, Option<String>, Option<Timestamp>) {
    let timezone: Option<Timezone> = tz_str.and_then(|val| {
        Timezone::get(val).map_or_else(
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
            Some(Timestamp::now())
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
            max_execution_time_ms: max_exec,
            on_success_service: job.on_success_service.clone(),
            on_success_job: job.on_success_job.clone(),
            on_error_service: job.on_error_service.clone(),
            on_error_job: job.on_error_job.clone(),
            next_fire_utc: None,
            next_nominal_utc: None,
            next_fire_instant: None,
            in_flight_runs: BTreeMap::new(),
            current_run: 0,
            jitter_rng,
        };
        if running_job.is_active {
            running_job.compute_next_fire(Timestamp::now());
        }
        running_job
    }

    /// Applies changes from an updated `SchedulerJob` definition, recomputing the schedule if needed.
    pub fn update_from_job(&mut self, job: &SchedulerJob) {
        // Remembered so a flip from inactive to active can be detected below.
        let was_active = self.is_active;

        self.name.clone_from(&job.name);
        self.is_active = job.is_active;
        self.service = ServiceName(job.service.clone());
        self.extra.clone_from(&job.extra);
        self.job_type = JobType::from(job.job_type.as_str());
        self.max_execution_time_ms =
            clamp_max_execution_time(job.max_execution_time_ms.unwrap_or(DEFAULT_MAX_EXECUTION_TIME_MS), &job.name);
        self.repeats = job.repeats;
        self.on_success_service.clone_from(&job.on_success_service);
        self.on_success_job.clone_from(&job.on_success_job);
        self.on_error_service.clone_from(&job.on_error_service);
        self.on_error_job.clone_from(&job.on_error_job);

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

        // A job that has just been re-activated has no next fire time - deactivation cleared it -
        // so the schedule must be recomputed even when none of the interval fields changed.
        let just_activated = self.is_active && !was_active;

        if self.is_active && (schedule_changed || just_activated) {
            self.compute_next_fire(Timestamp::now());
        } else if !self.is_active {
            self.clear_next_fire();
        }
    }

    /// Restores the run state that the server loaded from the Zato database for this job.
    ///
    /// The run counter takes the count of the Zato database only when that count is higher,
    /// because a run fired and not yet claimed is counted here and not there.
    /// A job whose repeats are used up, or a one-time job that already ran, does not fire again.
    /// An interval-based job whose latest due slot lies after the last claimed slot fires
    /// once for that slot at `now`, and every older missed slot is skipped.
    pub fn restore_run_state(&mut self, current_run: u32, last_slot: Option<Timestamp>, now: Timestamp) {
        self.raise_run_count(current_run);

        // An inactive job has no schedule to restore - activating it later computes one.
        if !self.is_active {
            return;
        }

        if self.is_repeats_exhausted() {
            self.clear_next_fire();
            return;
        }

        // A one-time job that already ran gets no fire time here, because its counter is above zero.
        self.compute_next_fire(now);

        if self.job_type != JobType::IntervalBased {
            return;
        }

        // Without a claimed slot the job never ran anywhere, so there is nothing it missed.
        let Some(last_slot) = last_slot else { return };
        let Some(latest_due) = self.latest_due_slot(now) else { return };

        if latest_due > last_slot {
            self.next_fire_utc = Some(now);
            self.next_nominal_utc = Some(latest_due);
            self.sync_instant_from_utc(now);
        }
    }

    /// Restores the run count that the server loaded from the Zato database for a job whose schedule this
    /// scheduler kept running, which therefore missed no slot.
    ///
    /// The next fire time is kept, because a slot that fired and that no worker claimed yet lies after
    /// the last claimed slot and would otherwise be fired once more, and skipped by the worker as claimed.
    pub const fn restore_run_count(&mut self, current_run: u32) {
        self.raise_run_count(current_run);

        // Runs claimed through other servers may have used up the repeats of the job
        if self.is_repeats_exhausted() {
            self.clear_next_fire();
        }
    }

    /// Takes the run count of the Zato database only when it is higher than the counter of this job.
    const fn raise_run_count(&mut self, current_run: u32) {
        // Runs claimed through other servers raise the counter, and a run fired and not yet claimed keeps it
        if current_run > self.current_run {
            self.current_run = current_run;
        }
    }

    /// Computes the next fire time from `now` based on job type and interval.
    pub fn compute_next_fire(&mut self, now: Timestamp) {
        match self.job_type {
            JobType::OneTime => {
                if let Some(start) = self.start_date {
                    if start > now {
                        self.next_fire_utc = Some(start);
                        self.next_nominal_utc = Some(start);
                    } else if self.current_run == 0 {
                        // The start date has passed without a run, so the slot is due at once.
                        self.next_fire_utc = Some(now);
                        self.next_nominal_utc = Some(start);
                    } else {
                        self.clear_next_fire();
                    }
                } else {
                    self.clear_next_fire();
                }
            }
            JobType::IntervalBased => {
                if self.interval_ms > 0 {
                    if let Some(start) = self.start_date {
                        let nth = self.find_next_n(start, now);
                        let base_ms = nth * self.interval_ms;
                        let jitter = self.compute_jitter();
                        let nominal_offset_ms = i64::try_from(base_ms).unwrap_or(i64::MAX);
                        let total_ms = i64::try_from(base_ms + jitter).unwrap_or(i64::MAX);
                        let new_fire = start + SignedDuration::from_millis(total_ms);
                        self.next_fire_utc = Some(new_fire);
                        self.next_nominal_utc = Some(start + SignedDuration::from_millis(nominal_offset_ms));
                    } else {
                        self.clear_next_fire();
                    }
                } else {
                    self.clear_next_fire();
                }
            }
        }
        self.sync_instant_from_utc(now);
    }

    /// Advances to the next fire time after the current run completes.
    pub fn advance_to_next(&mut self, now: Timestamp) {
        if self.job_type == JobType::OneTime {
            self.clear_next_fire();
            return;
        }
        if self.is_repeats_exhausted() {
            self.clear_next_fire();
            return;
        }
        let reference = match self.next_fire_utc {
            Some(fire) if fire > now => fire,
            _ => now,
        };
        self.compute_next_fire(reference);
    }

    /// Whether any run of the job was fired and its completion was not reported yet.
    #[must_use]
    pub fn is_in_flight(&self) -> bool {
        !self.in_flight_runs.is_empty()
    }

    /// Records the run of the given number as fired at the given instant.
    pub fn start_run(&mut self, run: u32, since: Instant) {
        self.in_flight_runs.insert(run, since);
    }

    /// Records the completion of the run of the given number.
    ///
    /// The other runs of the job remain in flight, so the completion of a forced run, or of a run
    /// the server skipped, never lets the next slot fire while a scheduled run is still executing.
    pub fn complete_run(&mut self, run: u32) {
        self.in_flight_runs.remove(&run);
    }

    /// Returns the instant at which the earliest run still in flight was fired.
    #[must_use]
    pub fn earliest_in_flight_since(&self) -> Option<Instant> {
        self.in_flight_runs.values().min().copied()
    }

    /// Computes a `JobSummary` snapshot from the current job's scheduling state.
    ///
    /// Intended to be called under the state mutex. The returned value is fully
    /// owned and can be used after the mutex is released.
    #[must_use]
    pub fn summary(&self) -> JobSummary {
        JobSummary {
            id: self.id.0,
            name: self.name.clone(),
            is_active: self.is_active,
            service: self.service.0.clone(),
            job_type: self.job_type.as_str().to_owned(),
            in_flight: self.is_in_flight(),
            current_run: self.current_run,
            interval_ms: self.interval_ms,
            next_fire_utc: self.next_fire_utc.map(to_rfc3339),
        }
    }

    /// Public wrapper around `sync_instant_from_utc`.
    pub fn sync_instant_from_utc_pub(&mut self, now: Timestamp) {
        self.sync_instant_from_utc(now);
    }

    /// Tells whether the job has a repeat limit and has fired that many times.
    const fn is_repeats_exhausted(&self) -> bool {
        match self.repeats {
            Some(max) => max > 0 && self.current_run >= max,
            None => false,
        }
    }

    /// Clears the next fire time and its slot, so the job does not fire until a schedule is computed again.
    const fn clear_next_fire(&mut self) {
        self.next_fire_utc = None;
        self.next_nominal_utc = None;
        self.next_fire_instant = None;
    }

    /// Returns the latest slot of an interval-based schedule that is at or before `now`.
    ///
    /// Returns `None` when the job has no interval or no start date, or when `now` is before the start date.
    #[must_use]
    pub fn latest_due_slot(&self, now: Timestamp) -> Option<Timestamp> {
        if self.interval_ms == 0 {
            return None;
        }
        let start = self.start_date?;
        if now < start {
            return None;
        }
        let elapsed_ms = millis_between(now, start);
        let elapsed_slots = elapsed_ms / self.interval_ms;
        let offset_ms = i64::try_from(elapsed_slots * self.interval_ms).unwrap_or(i64::MAX);
        Some(start + SignedDuration::from_millis(offset_ms))
    }

    /// Finds the next interval multiple `n` such that `start + n * interval > now`.
    fn find_next_n(&self, start: Timestamp, now: Timestamp) -> u64 {
        if now <= start {
            return 0;
        }
        let elapsed_ms = millis_between(now, start);
        let nth = elapsed_ms / self.interval_ms;
        let offset_ms = i64::try_from(nth * self.interval_ms).unwrap_or(i64::MAX);
        let candidate = start + SignedDuration::from_millis(offset_ms);
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
    fn sync_instant_from_utc(&mut self, now: Timestamp) {
        self.next_fire_instant = self.next_fire_utc.map(|fire_utc| {
            let diff_ms = millis_between(fire_utc, now);
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

    /// Parses a start-date string into a UTC instant, optionally interpreting it in a timezone.
    fn parse_start_date(raw: &str, zone: Option<&Timezone>) -> Option<Timestamp> {
        if raw.is_empty() {
            return None;
        }
        let clean = raw.split('+').next().unwrap_or(raw).trim_end_matches('Z');
        for fmt in &START_DATE_FORMATS {
            if let Ok(civil) = DateTime::strptime(fmt, clean) {
                if let Some(tz_ref) = zone {
                    return Self::civil_to_utc_in_tz(civil, tz_ref);
                }
                return TimeZone::UTC.to_timestamp(civil).ok();
            }
        }
        None
    }

    /// Returns the instant of a civil datetime in a timezone, picking the earliest for ambiguous results.
    ///
    /// Returns `None` when the civil datetime falls into a gap of the timezone.
    fn earliest_instant_in_tz(civil: DateTime, zone: &Timezone) -> Option<Timestamp> {
        match zone.to_ambiguous_timestamp(civil).offset() {
            AmbiguousOffset::Unambiguous { offset } | AmbiguousOffset::Fold { before: offset, .. } => offset.to_timestamp(civil).ok(),
            AmbiguousOffset::Gap { .. } => None,
        }
    }

    /// Converts a civil datetime to UTC by interpreting it in a timezone, with a DST-gap fallback.
    fn civil_to_utc_in_tz(civil: DateTime, zone: &Timezone) -> Option<Timestamp> {
        if let Some(utc) = Self::earliest_instant_in_tz(civil, zone) {
            return Some(utc);
        }
        // A datetime skipped by the timezone exists one shift later.
        if let Ok(advanced) = civil.checked_add(DST_GAP_SHIFT)
            && let Some(utc) = Self::earliest_instant_in_tz(advanced, zone)
        {
            return Some(utc);
        }
        TimeZone::UTC.to_timestamp(civil).ok()
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
            max_execution_time_ms: None,
            on_success_service: None,
            on_success_job: None,
            on_error_service: None,
            on_error_job: None,
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
