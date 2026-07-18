// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Redis Streams integration for the standalone scheduler binary.
//!
//! Provides command ingestion from the command stream and fire event
//! publishing to the fire stream. All stream keys are namespaced by
//! the `Zato_Scheduler_Stream_Prefix` environment variable so that
//! multiple Zato environments sharing one Redis never consume each
//! other's messages.

use std::sync::Arc;

use chrono::Utc;
use serde::Deserialize;

use crate::job::{ExecutionRecord, LogEntry, RunningJob};
use crate::model::SchedulerJob;
use crate::scheduler::SchedulerShared;
use crate::types::{FireBatch, JobId};
use crate::{humanize_ms, reload_jobs};

/// Environment variable holding the per-environment stream key prefix.
pub const STREAM_PREFIX_ENV_VAR: &str = "Zato_Scheduler_Stream_Prefix";

/// Default stream key prefix used when the environment does not set one.
pub const DEFAULT_STREAM_PREFIX: &str = "zato:scheduler";

/// Consumer group name used by the scheduler for the command stream.
pub const CONSUMER_GROUP_NAME: &str = "scheduler";

/// Consumer name within the group.
pub const CONSUMER_INSTANCE_NAME: &str = "scheduler-0";

/// Maximum number of entries in each stream before trimming.
const STREAM_MAXLEN: usize = 100_000;

/// Redis stream keys, all namespaced by the per-environment prefix.
#[derive(Clone)]
pub struct StreamKeys {

    /// Stream where the server publishes commands for the scheduler.
    pub command: String,

    /// Stream where the scheduler publishes fire events.
    pub fire: String,

    /// Stream where the scheduler publishes timeout events.
    pub timeout: String,

    /// Stream where the scheduler publishes synchronous replies.
    pub reply: String,

    /// Stream where the scheduler publishes requests for the server.
    pub request: String,
}

impl StreamKeys {

    /// Builds stream keys from the `Zato_Scheduler_Stream_Prefix` environment variable.
    pub fn from_env() -> Self {
        // The prefix is genuinely optional - a standalone production environment runs with the default.
        let prefix = std::env::var(STREAM_PREFIX_ENV_VAR).unwrap_or_else(|_| DEFAULT_STREAM_PREFIX.to_string());
        Self {
            command: format!("{prefix}:stream:command"),
            fire: format!("{prefix}:stream:fire"),
            timeout: format!("{prefix}:stream:timeout"),
            reply: format!("{prefix}:stream:reply"),
            request: format!("{prefix}:stream:request"),
        }
    }
}

/// Ensures the consumer group exists on the command stream.
///
/// Creates the stream and group if they do not exist.
pub fn ensure_consumer_group(conn: &mut redis::Connection, keys: &StreamKeys) {
    let result: Result<(), redis::RedisError> = redis::cmd("XGROUP")
        .arg("CREATE")
        .arg(&keys.command)
        .arg(CONSUMER_GROUP_NAME)
        .arg("$")
        .arg("MKSTREAM")
        .query(conn);

    match result {
        Ok(()) => tracing::info!("Created consumer group '{CONSUMER_GROUP_NAME}' on '{}'", keys.command),
        Err(err) => {
            let msg = err.to_string();
            if msg.contains("BUSYGROUP") {
                tracing::debug!("Consumer group '{CONSUMER_GROUP_NAME}' already exists on '{}'", keys.command);
            } else {
                tracing::error!("Failed to create consumer group: {err}");
            }
        }
    }
}

/// Publishes a `request_jobs` message to the request stream, asking the server
/// to send a reload command with jobs from ODB.
pub fn request_jobs(conn: &mut redis::Connection, keys: &StreamKeys) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(&keys.request)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("command")
        .arg("request_jobs")
        .query(conn);

    match result {
        Ok(_) => tracing::info!("Published request_jobs to '{}'", keys.request),
        Err(err) => tracing::error!("Failed to publish request_jobs: {err}"),
    }
}

/// Processes a reload command received during the startup wait phase.
pub fn process_startup_reload(
    conn: &mut redis::Connection,
    keys: &StreamKeys,
    shared: &crate::scheduler::SchedulerShared,
    correlation_id: &str,
    payload: &str,
) {
    handle_reload(shared, payload);
    publish_reply(conn, keys, correlation_id, "ok");
}

/// Publishes a fire event to the fire stream via XADD.
pub fn publish_fire_event(conn: &mut redis::Connection, keys: &StreamKeys, batch: &FireBatch) {
    let payload = serde_json::to_string(batch).unwrap_or_default();
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(&keys.fire)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("job_id")
        .arg(batch.job_id.0)
        .arg("name")
        .arg(&batch.name)
        .arg("service")
        .arg(batch.service.as_ref())
        .arg("current_run")
        .arg(batch.current_run)
        .arg("payload")
        .arg(&payload)
        .query(conn);

    if let Err(err) = result {
        tracing::error!("Failed to XADD fire event for job '{}': {err}", batch.name);
    }
}

/// Publishes a timeout event to the timeout stream via XADD.
pub fn publish_timeout_event(
    conn: &mut redis::Connection,
    keys: &StreamKeys,
    job_id: i64,
    current_run: u32,
    elapsed_ms: u64,
    error_msg: &str,
) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(&keys.timeout)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("job_id")
        .arg(job_id)
        .arg("current_run")
        .arg(current_run)
        .arg("elapsed_ms")
        .arg(elapsed_ms)
        .arg("error")
        .arg(error_msg)
        .query(conn);

    if let Err(err) = result {
        tracing::error!("Failed to XADD timeout event for job_id={job_id}: {err}");
    }
}

/// Publishes a synchronous reply to the reply stream.
fn publish_reply(conn: &mut redis::Connection, keys: &StreamKeys, correlation_id: &str, status: &str) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(&keys.reply)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("correlation_id")
        .arg(correlation_id)
        .arg("status")
        .arg(status)
        .query(conn);

    if let Err(err) = result {
        tracing::error!("Failed to XADD reply for correlation_id={correlation_id}: {err}");
    }
}

/// Reads and processes commands from the command stream in a blocking loop.
///
/// This function blocks on XREADGROUP and should be run on its own thread.
pub fn command_listener_loop(conn: &mut redis::Connection, keys: &StreamKeys, shared: Arc<SchedulerShared>) {
    tracing::info!("Command listener started on '{}'", keys.command);

    loop {
        if shared.stop_flag.load(std::sync::atomic::Ordering::Relaxed) {
            tracing::info!("Command listener exiting (stop flag set)");
            break;
        }

        type StreamReadResult = Vec<(String, Vec<(String, Vec<(String, String)>)>)>;

        let result: Result<StreamReadResult, redis::RedisError> = redis::cmd("XREADGROUP")
            .arg("GROUP")
            .arg(CONSUMER_GROUP_NAME)
            .arg(CONSUMER_INSTANCE_NAME)
            .arg("BLOCK")
            .arg(1000_u64)
            .arg("COUNT")
            .arg(10_u64)
            .arg("STREAMS")
            .arg(&keys.command)
            .arg(">")
            .query(conn);

        let streams = match result {
            Ok(streams) => streams,
            Err(err) => {
                let msg = err.to_string();
                if msg.contains("timeout") || msg.contains("nil") {
                    continue;
                }
                tracing::error!("XREADGROUP error: {err}");
                std::thread::sleep(std::time::Duration::from_secs(1));
                continue;
            }
        };

        for (_stream_name, messages) in &streams {
            for (msg_id, fields) in messages {
                let mut command = String::new();
                let mut correlation_id = String::new();
                let mut payload = String::new();

                for (key, value) in fields {
                    match key.as_str() {
                        "command" => command.clone_from(value),
                        "correlation_id" => correlation_id.clone_from(value),
                        "payload" => payload.clone_from(value),
                        _ => {}
                    }
                }

                process_command(conn, keys, &shared, &command, &correlation_id, &payload);

                let ack_result: Result<u32, redis::RedisError> = redis::cmd("XACK")
                    .arg(&keys.command)
                    .arg(CONSUMER_GROUP_NAME)
                    .arg(msg_id.as_str())
                    .query(conn);
                if let Err(err) = ack_result {
                    tracing::error!("Failed to XACK message {msg_id}: {err}");
                }
            }
        }
    }
}

/// Dispatches a single command to the appropriate handler.
fn process_command(
    conn: &mut redis::Connection,
    keys: &StreamKeys,
    shared: &SchedulerShared,
    command: &str,
    correlation_id: &str,
    payload: &str,
) {
    tracing::info!("Command received: {command} correlation_id={correlation_id} payload={payload}");
    match command {
        "create_job" => handle_create_job(shared, payload),
        "edit_job" => handle_edit_job(shared, payload),
        "delete_job" => handle_delete_job(shared, payload),
        "execute_job" => handle_execute_job(shared, payload),
        "mark_complete" => handle_mark_complete(shared, payload),
        "append_log_entry" => handle_append_log_entry(shared, payload),
        "reload" => {
            handle_reload(shared, payload);
            publish_reply(conn, keys, correlation_id, "ok");
        }
        "stop" => {
            tracing::info!("Received stop command");
            shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
            shared.condvar.notify_all();
            publish_reply(conn, keys, correlation_id, "ok");
        }
        _ => {
            tracing::warn!("Unknown command: {command}");
        }
    }
}

/// Payload for create_job and edit_job commands.
#[derive(Deserialize)]
struct JobCommandPayload {
    /// The ODB job identifier.
    job_id: i64,
    /// Full job definition.
    job_data: SchedulerJob,
}

/// Payload for the delete_job command.
#[derive(Deserialize)]
struct JobIdPayload {
    /// The ODB job identifier.
    job_id: i64,
}

/// Payload for the execute_job command.
#[derive(Deserialize)]
struct ExecuteJobPayload {
    /// The ODB job identifier.
    job_id: i64,
    /// Job name, used when the runtime knows the job under a different ID.
    #[serde(default)]
    name: String,
}

/// Payload for mark_complete command.
#[derive(Deserialize)]
struct MarkCompletePayload {
    /// The ODB job identifier.
    job_id: i64,
    /// Execution outcome label.
    outcome: String,
    /// Execution duration in milliseconds.
    duration_ms: u64,
    /// Run number being completed.
    current_run: u32,
    /// Error details (traceback), empty when the run succeeded.
    error: String,
}

/// Payload for append_log_entry command.
#[derive(Deserialize)]
struct AppendLogPayload {
    /// The ODB job identifier.
    job_id: i64,
    /// Run number to append to.
    current_run: u32,
    /// ISO timestamp of the log entry.
    timestamp_iso: String,
    /// Log level name.
    level: String,
    /// Log message text.
    message: String,
}

/// Payload for reload command.
#[derive(Deserialize)]
struct ReloadPayload {
    /// Full list of jobs from ODB.
    jobs: Vec<SchedulerJob>,
}

fn handle_create_job(shared: &SchedulerShared, payload: &str) {
    let parsed: JobCommandPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse create_job payload: {err}");
            return;
        }
    };
    let running_job = RunningJob::from_scheduler_job(&parsed.job_data);
    let mut state = shared.state.lock();
    state.jobs.insert(parsed.job_id, running_job);
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    tracing::info!("Created job: id={} name={}", parsed.job_id, parsed.job_data.name);
}

fn handle_edit_job(shared: &SchedulerShared, payload: &str) {
    let parsed: JobCommandPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse edit_job payload: {err}");
            return;
        }
    };
    let mut state = shared.state.lock();
    if let Some(existing) = state.jobs.get_mut(&parsed.job_id) {
        existing.update_from_job(&parsed.job_data);
    } else {
        // The incoming ID is unknown - the runtime may still hold this job under an old ID,
        // e.g. after a redeployment recreated the ODB rows with new identifiers.
        let name_match_key = state
            .jobs
            .iter()
            .find_map(|(key, job)| (job.name == parsed.job_data.name).then_some(*key));

        if let Some(old_key) = name_match_key {
            // Move the job under the new ID instead of inserting a duplicate,
            // so its execution history survives and only one entry keeps firing.
            if let Some(mut existing) = state.jobs.remove(&old_key) {
                existing.id = JobId(parsed.job_id);
                existing.update_from_job(&parsed.job_data);
                state.jobs.insert(parsed.job_id, existing);
                tracing::info!(
                    "Moved job under new id: old_id={old_key} new_id={} name={}",
                    parsed.job_id,
                    parsed.job_data.name
                );
            }
        } else {
            let running_job = RunningJob::from_scheduler_job(&parsed.job_data);
            state.jobs.insert(parsed.job_id, running_job);
        }
    }
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    tracing::info!("Edited job: id={} name={}", parsed.job_id, parsed.job_data.name);
}

fn handle_delete_job(shared: &SchedulerShared, payload: &str) {
    let parsed: JobIdPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse delete_job payload: {err}");
            return;
        }
    };
    let mut state = shared.state.lock();
    state.jobs.remove(&parsed.job_id);
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    tracing::info!("Deleted job: id={}", parsed.job_id);
}

pub fn handle_execute_job(shared: &SchedulerShared, payload: &str) {
    let parsed: ExecuteJobPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse execute_job payload: {err}");
            return;
        }
    };

    let sender = shared.fire_sender.lock().clone();
    let Some(sender) = sender else {
        tracing::error!("Fire sender not available for forced execution of job_id={}", parsed.job_id);
        return;
    };

    let mut state = shared.state.lock();

    // Look the job up by its ODB ID first - when the runtime knows it under an older ID,
    // e.g. after a redeployment recreated the ODB rows, fall back to a name match.
    let mut job_key = parsed.job_id;
    if !state.jobs.contains_key(&job_key) {
        let name_match_key = state
            .jobs
            .iter()
            .find_map(|(key, job)| (job.name == parsed.name).then_some(*key));
        if let Some(matched_key) = name_match_key {
            job_key = matched_key;
        }
    }

    let Some(running_job) = state.jobs.get_mut(&job_key) else {
        tracing::warn!("Forced execute: job_id={} name={} not found", parsed.job_id, parsed.name);
        return;
    };

    let now = Utc::now();
    let now_iso = now.to_rfc3339();

    running_job.current_run += 1;

    let batch = FireBatch {
        job_id: running_job.id,
        name: running_job.name.clone(),
        service: running_job.service.clone(),
        extra: running_job.extra.clone(),
        job_type: running_job.job_type.clone(),
        current_run: running_job.current_run,
        on_success_service: running_job.on_success_service.clone(),
        on_success_job: running_job.on_success_job.clone(),
        on_error_service: running_job.on_error_service.clone(),
        on_error_job: running_job.on_error_job.clone(),
    };

    running_job.in_flight = true;
    running_job.in_flight_since = Some(std::time::Instant::now());
    running_job.in_flight_run = Some(running_job.current_run);

    let mut rec = ExecutionRecord::new(&now_iso, &now_iso, crate::types::outcome::RUNNING, running_job.current_run);
    rec.log_entries.push(LogEntry {
        timestamp_iso: now_iso,
        level: "SYSTEM".into(),
        message: "Job started (forced execute)".into(),
    });
    running_job.record_execution(rec);

    let job_name = running_job.name.clone();
    let current_run = running_job.current_run;
    drop(state);

    if let Err(err) = sender.send(batch) {
        tracing::error!("Failed to send forced fire event for job `{job_name}`: {err}");
    } else {
        tracing::info!("Forced execution of job: name={job_name} run={current_run} job_id={}", parsed.job_id);
    }
}

fn handle_mark_complete(shared: &SchedulerShared, payload: &str) {
    let parsed: MarkCompletePayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse mark_complete payload: {err}");
            return;
        }
    };
    let mut state = shared.state.lock();
    if let Some(running_job) = state.jobs.get_mut(&parsed.job_id) {
        tracing::info!(
            "Job completed: name={} run={} outcome={} duration_ms={} job_id={}",
            running_job.name,
            parsed.current_run,
            parsed.outcome,
            parsed.duration_ms,
            parsed.job_id,
        );

        crate::metrics::EXECUTIONS_TOTAL
            .with_label_values(&[&running_job.name, &parsed.outcome])
            .inc();

        let duration_secs = parsed.duration_ms as f64 / 1000.0;
        crate::metrics::EXECUTION_DURATION_SECONDS
            .with_label_values(&[&running_job.name])
            .observe(duration_secs);
        running_job.in_flight = false;
        running_job.in_flight_since = None;
        running_job.in_flight_run = None;

        let mut found_rec = false;
        for rec in running_job.history.iter_mut().rev() {
            if rec.current_run == parsed.current_run {
                rec.duration_ms = Some(parsed.duration_ms);
                rec.outcome.clone_from(&parsed.outcome);
                // The server sends an empty string on success - only a failed run carries a traceback.
                if !parsed.error.is_empty() {
                    rec.error = Some(parsed.error.clone());
                }
                rec.log_entries.push(LogEntry {
                    timestamp_iso: Utc::now().to_rfc3339(),
                    level: "SYSTEM".into(),
                    message: format!(
                        "Job completed, outcome: {}, duration: {}",
                        parsed.outcome,
                        humanize_ms(parsed.duration_ms)
                    ),
                });
                found_rec = true;
                break;
            }
        }
        if !found_rec {
            tracing::warn!(
                "No history for name={} run={} job_id={}",
                running_job.name,
                parsed.current_run,
                parsed.job_id,
            );
        }

        if running_job.interval_ms > 0 && parsed.duration_ms >= running_job.interval_ms {
            let now = Utc::now();
            while let Some(fire) = running_job.next_fire_utc {
                if fire >= now {
                    break;
                }
                running_job.advance_to_next(now);
            }
        }
    }
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
}

fn handle_append_log_entry(shared: &SchedulerShared, payload: &str) {
    let parsed: AppendLogPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse append_log_entry payload: {err}");
            return;
        }
    };
    let entry = LogEntry {
        timestamp_iso: parsed.timestamp_iso,
        level: parsed.level,
        message: parsed.message,
    };
    let mut state = shared.state.lock();
    if let Some(running_job) = state.jobs.get_mut(&parsed.job_id) {
        for rec in running_job.history.iter_mut().rev() {
            if rec.current_run == parsed.current_run {
                rec.log_entries.push(entry);
                break;
            }
        }
    }
    drop(state);
}

fn handle_reload(shared: &SchedulerShared, payload: &str) {
    let parsed: ReloadPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse reload payload: {err}");
            return;
        }
    };
    let mut state = shared.state.lock();
    reload_jobs(&mut state, &parsed.jobs);
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    let count = parsed.jobs.len();
    let label = crate::plural(count, "job", "jobs");
    tracing::info!("Reloaded {count} {label}");
}
