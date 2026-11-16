//! Core scheduler crate for Zato - provides the scheduling engine, job management,
//! and Redis/HTTP integration for the standalone `_zato_scheduler` binary.

use std::time::Duration;

/// Numeric conversions that have no lossless form, kept in one place.
pub mod convert;

/// Typed encoding and parsing of the JSON payloads carried in Redis stream fields.
pub mod wire;

/// Running-job state machine.
pub mod job;

/// Data-transfer objects for job definitions.
pub mod model;

/// Core scheduler loop and helpers.
pub mod scheduler;

/// Shared type definitions (job-id wrappers, outcome constants, etc.).
pub mod types;

/// Watchdog thread for detecting hung threads.
pub mod watchdog;

/// Redis stream integration for command ingestion and fire event publishing.
pub mod redis_streams;

/// The Redis connection of the scheduler binary that is opened again after a restart of Redis.
pub mod redis_link;

/// HTTP query API served by actix-web for the Zato server to read scheduler state.
pub mod http_api;

/// Prometheus metrics for the scheduler process.
pub mod metrics;

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

/// Returns the singular or plural form of a word based on the count.
#[must_use]
pub const fn plural<'word>(count: usize, singular: &'word str, plural_form: &'word str) -> &'word str {
    if count == 1 { singular } else { plural_form }
}

/// Reconciles the running-job map with a freshly loaded list of scheduler jobs.
///
/// The worker of a server sends a reload each time it starts, so a reload arrives while runs fired
/// for its predecessor are still in progress. The runs in flight of every job are therefore kept, and a run
/// whose worker terminated is removed by `check_in_flight_timeouts` once its execution time is exceeded.
/// The run state of each job is restored from what the server loaded from the common database,
/// which holds the runs claimed by every server, not only by this one.
///
/// The server draws the number of a reload before it reads the ODB and the number of a job command after
/// its ODB commit, so a job whose latest applied command or reload has a higher number than this reload
/// was changed after the ODB read of this reload, and it is left as it is.
pub fn reload_jobs(state: &mut scheduler::SchedulerState, new_jobs: &[crate::model::ReloadedJob], sequence: u64) {
    let new_ids: std::collections::HashSet<i64> = new_jobs.iter().map(|reloaded| reloaded.job.id).collect();
    let old_ids: std::collections::HashSet<i64> = state.jobs.keys().copied().collect();

    for removed_id in old_ids.difference(&new_ids) {
        // A job created after the ODB read of this reload is not in its list and is kept
        if state.is_changed_after(*removed_id, sequence) {
            continue;
        }
        state.jobs.remove(removed_id);
        state.record_change(*removed_id, sequence);
    }

    let now = chrono::Utc::now();

    for reloaded in new_jobs {
        let scheduler_job = &reloaded.job;
        let job_id = scheduler_job.id;

        // A job edited or deleted after the ODB read of this reload keeps that change
        if state.is_changed_after(job_id, sequence) {
            continue;
        }
        state.record_change(job_id, sequence);

        let last_slot = parse_last_slot(reloaded, &scheduler_job.name);
        if let Some(existing) = state.jobs.get_mut(&job_id) {
            existing.update_from_job(scheduler_job);

            // The scheduler kept the schedule of a job it holds running, so only a job it did not hold catches up
            existing.restore_run_count(reloaded.current_run);
            let interval = humanize_ms(existing.interval_ms);
            let next = existing.next_fire_utc.map_or_else(|| "none".to_string(), |fire| fire.to_rfc3339());
            tracing::info!(
                "Job updated: id={job_id} name={} interval={interval} next={next} active={} service={}",
                scheduler_job.name,
                scheduler_job.is_active,
                scheduler_job.service,
            );
        } else {
            let mut running_job = RunningJob::from_scheduler_job(scheduler_job);
            running_job.restore_run_state(reloaded.current_run, last_slot, now);
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

/// Parses the last claimed slot of a reloaded job into a UTC datetime.
///
/// A slot that cannot be parsed is logged and treated as absent, so the job keeps its
/// regular schedule and only the catch-up of a missed slot is given up.
fn parse_last_slot(reloaded: &crate::model::ReloadedJob, job_name: &str) -> Option<chrono::DateTime<chrono::Utc>> {
    let raw = reloaded.last_slot_iso.as_deref()?;
    match chrono::DateTime::parse_from_rfc3339(raw) {
        Ok(slot) => Some(slot.with_timezone(&chrono::Utc)),
        Err(err) => {
            tracing::error!("Job `{job_name}`: could not parse last_slot_iso `{raw}`: {err}");
            None
        }
    }
}
