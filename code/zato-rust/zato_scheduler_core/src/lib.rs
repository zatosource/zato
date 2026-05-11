//! Core scheduler crate for Zato - provides the scheduling engine, job management,
//! and Redis/HTTP integration for the standalone `_zato_scheduler` binary.

use std::time::Duration;

/// Calendar holiday support.
pub mod calendar;

/// Execution-history serialization helpers.
pub mod history;

/// Running-job state machine.
pub mod job;

/// Data-transfer objects for job and calendar definitions.
pub mod model;

/// Core scheduler loop and helpers.
pub mod scheduler;

/// Shared type definitions (job-id wrappers, outcome constants, etc.).
pub mod types;

/// Watchdog thread for detecting hung threads.
pub mod watchdog;

/// Redis stream integration for command ingestion and fire event publishing.
pub mod redis_streams;

/// HTTP query API served by actix-web for the Zato server to read scheduler state.
pub mod http_api;

/// Prometheus metrics for the scheduler process.
pub mod metrics;

use calendar::CalendarData;
use job::RunningJob;

/// Collects log messages while the state mutex is held so they can be
/// flushed after the lock is released, avoiding blocking calls inside
/// the critical section.
pub struct DeferredLog {
    /// Buffered messages with their log level.
    entries: Vec<(tracing::Level, String)>,
}

impl Default for DeferredLog {
    fn default() -> Self {
        Self::new()
    }
}

impl DeferredLog {
    /// Creates an empty buffer.
    pub const fn new() -> Self {
        Self { entries: Vec::new() }
    }

    /// Flushes all buffered messages through `tracing`.
    ///
    /// Must be called only when no mutex is held.
    pub fn flush(self) {
        for (level, msg) in self.entries {
            match level {
                tracing::Level::ERROR => tracing::error!("{msg}"),
                tracing::Level::WARN => tracing::warn!("{msg}"),
                tracing::Level::INFO => tracing::info!("{msg}"),
                tracing::Level::DEBUG => tracing::debug!("{msg}"),
                tracing::Level::TRACE => tracing::trace!("{msg}"),
            }
        }
    }
}

/// Buffers a formatted log message into a `DeferredLog` instead of emitting directly.
macro_rules! deferred_log {
    ($dl:expr, $level:expr, $($arg:tt)*) => {
        $dl.entries.push(($level, format!($($arg)*)))
    };
}

pub(crate) use deferred_log;

/// Formats a duration in milliseconds into a human-readable string.
pub fn humanize_ms(millis: u64) -> String {
    if millis == 0 {
        return "< 1ms".to_string();
    }
    humantime::format_duration(Duration::from_millis(millis)).to_string()
}

/// Reconciles the running-job map with a freshly loaded list of scheduler jobs.
/// A reload means the server (re)started, so any previously in-flight jobs
/// will never receive completion callbacks - clear their in_flight state.
pub fn reload_jobs(state: &mut scheduler::SchedulerState, new_jobs: &[crate::model::SchedulerJob]) {
    let new_ids: std::collections::HashSet<i64> = new_jobs.iter().map(|job| job.id).collect();
    let old_ids: std::collections::HashSet<i64> = state.jobs.keys().copied().collect();

    for removed_id in old_ids.difference(&new_ids) {
        state.jobs.remove(removed_id);
    }

    // A reload implies the server restarted; all previous in-flight
    // invocations are lost and will never complete.
    for running_job in state.jobs.values_mut() {
        if running_job.in_flight {
            tracing::info!(
                "Clearing stale in_flight for job id={} name={} (server reloaded)",
                running_job.id,
                running_job.name,
            );
            running_job.in_flight = false;
            running_job.in_flight_since = None;
            running_job.in_flight_run = None;
        }
    }

    for scheduler_job in new_jobs {
        let job_id = scheduler_job.id;
        if let Some(existing) = state.jobs.get_mut(&job_id) {
            existing.update_from_job(scheduler_job);
            let interval = humanize_ms(existing.interval_ms);
            let next = existing.next_fire_utc.map_or_else(|| "none".to_string(), |fire| fire.to_rfc3339());
            tracing::info!(
                "Job updated: id={job_id} name={} interval={interval} next={next} active={} service={}",
                scheduler_job.name,
                scheduler_job.is_active,
                scheduler_job.service,
            );
        } else {
            let running_job = RunningJob::from_scheduler_job(scheduler_job);
            let interval = humanize_ms(running_job.interval_ms);
            let next = running_job
                .next_fire_utc
                .map_or_else(|| "none".to_string(), |fire| fire.to_rfc3339());
            tracing::info!(
                "Job loaded: id={job_id} name={} interval={interval} next={next} active={} service={}",
                scheduler_job.name,
                scheduler_job.is_active,
                scheduler_job.service,
            );
            state.jobs.insert(job_id, running_job);
        }
    }
}

/// Replaces the calendar map in scheduler state with newly loaded calendars.
pub fn reload_calendars(state: &mut scheduler::SchedulerState, new_cals: std::collections::HashMap<String, crate::model::HolidayCalendar>) {
    state.calendars.clear();
    for (name, cal) in new_cals {
        let mut calendar_data = CalendarData::new(name.clone());
        for date_str in &cal.dates {
            if let Ok(date) = chrono::NaiveDate::parse_from_str(date_str, "%Y-%m-%d") {
                calendar_data.dates.insert(date);
            }
        }
        calendar_data.weekdays.clone_from(&cal.weekdays);
        calendar_data.description.clone_from(&cal.description);
        state.calendars.insert(name, calendar_data);
    }
}
