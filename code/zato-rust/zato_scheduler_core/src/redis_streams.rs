// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Redis Streams integration for the standalone scheduler binary.
//!
//! Provides command ingestion from `zato:scheduler:stream:command` and
//! fire event publishing to `zato:scheduler:stream:fire`.

use std::sync::Arc;

use chrono::Utc;
use serde::Deserialize;

use crate::job::{ExecutionRecord, LogEntry, RunningJob};
use crate::model::SchedulerJob;
use crate::scheduler::SchedulerShared;
use crate::types::{FireBatch, outcome};
use crate::{humanize_ms, reload_jobs};

/// Redis stream key where the server publishes commands for the scheduler.
pub const COMMAND_STREAM: &str = "zato:scheduler:stream:command";

/// Redis stream key where the scheduler publishes fire events.
pub const FIRE_STREAM: &str = "zato:scheduler:stream:fire";

/// Redis stream key where the scheduler publishes timeout events.
pub const TIMEOUT_STREAM: &str = "zato:scheduler:stream:timeout";

/// Redis stream key where the scheduler publishes synchronous replies.
pub const REPLY_STREAM: &str = "zato:scheduler:stream:reply";

/// Redis stream key where the scheduler publishes requests for the server.
pub const REQUEST_STREAM: &str = "zato:scheduler:stream:request";

/// Consumer group name used by the scheduler for the command stream.
pub const CONSUMER_GROUP_NAME: &str = "scheduler";

/// Consumer name within the group.
pub const CONSUMER_INSTANCE_NAME: &str = "scheduler-0";

/// Maximum number of entries in each stream before trimming.
const STREAM_MAXLEN: usize = 100_000;

/// Ensures the consumer group exists on the command stream.
///
/// Creates the stream and group if they do not exist.
pub fn ensure_consumer_group(conn: &mut redis::Connection) {
    let result: Result<(), redis::RedisError> = redis::cmd("XGROUP")
        .arg("CREATE")
        .arg(COMMAND_STREAM)
        .arg(CONSUMER_GROUP_NAME)
        .arg("$")
        .arg("MKSTREAM")
        .query(conn);

    match result {
        Ok(()) => tracing::info!("Created consumer group '{CONSUMER_GROUP_NAME}' on '{COMMAND_STREAM}'"),
        Err(err) => {
            let msg = err.to_string();
            if msg.contains("BUSYGROUP") {
                tracing::debug!("Consumer group '{CONSUMER_GROUP_NAME}' already exists on '{COMMAND_STREAM}'");
            } else {
                tracing::error!("Failed to create consumer group: {err}");
            }
        }
    }
}

/// Publishes a `request_jobs` message to the request stream, asking the server
/// to send a reload command with jobs from ODB.
pub fn request_jobs(conn: &mut redis::Connection) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(REQUEST_STREAM)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("command")
        .arg("request_jobs")
        .query(conn);

    match result {
        Ok(_) => tracing::info!("Published request_jobs to '{REQUEST_STREAM}'"),
        Err(err) => tracing::error!("Failed to publish request_jobs: {err}"),
    }
}

/// Processes a reload command received during the startup wait phase.
pub fn process_startup_reload(
    conn: &mut redis::Connection,
    shared: &crate::scheduler::SchedulerShared,
    correlation_id: &str,
    payload: &str,
) {
    handle_reload(shared, payload);
    publish_reply(conn, correlation_id, "ok");
}

/// Publishes a fire event to the fire stream via XADD.
pub fn publish_fire_event(conn: &mut redis::Connection, batch: &FireBatch) {
    let payload = serde_json::to_string(batch).unwrap_or_default();
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(FIRE_STREAM)
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
pub fn publish_timeout_event(conn: &mut redis::Connection, job_id: i64, current_run: u32, elapsed_ms: u64, error_msg: &str) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(TIMEOUT_STREAM)
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
fn publish_reply(conn: &mut redis::Connection, correlation_id: &str, status: &str) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(REPLY_STREAM)
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
pub fn command_listener_loop(conn: &mut redis::Connection, shared: Arc<SchedulerShared>) {
    tracing::info!("Command listener started on '{COMMAND_STREAM}'");

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
            .arg(COMMAND_STREAM)
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

                process_command(conn, &shared, &command, &correlation_id, &payload);

                let ack_result: Result<u32, redis::RedisError> = redis::cmd("XACK")
                    .arg(COMMAND_STREAM)
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
fn process_command(conn: &mut redis::Connection, shared: &SchedulerShared, command: &str, correlation_id: &str, payload: &str) {
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
            publish_reply(conn, correlation_id, "ok");
        }
        "stop" => {
            tracing::info!("Received stop command");
            shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
            shared.condvar.notify_all();
            publish_reply(conn, correlation_id, "ok");
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

/// Payload for delete_job and execute_job commands.
#[derive(Deserialize)]
struct JobIdPayload {
    /// The ODB job identifier.
    job_id: i64,
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
        let running_job = RunningJob::from_scheduler_job(&parsed.job_data);
        state.jobs.insert(parsed.job_id, running_job);
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

fn handle_execute_job(shared: &SchedulerShared, payload: &str) {
    let parsed: JobIdPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse execute_job payload: {err}");
            return;
        }
    };
    let mut state = shared.state.lock();
    if let Some(running_job) = state.jobs.get_mut(&parsed.job_id) {
        let now = Utc::now();
        running_job.next_fire_utc = Some(now);
        running_job.sync_instant_from_utc_pub(now);
    }
    state.dirty = true;
    drop(state);
    shared.condvar.notify_one();
    tracing::info!("Forced execution of job: id={}", parsed.job_id);
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
        running_job.in_flight = false;
        running_job.in_flight_since = None;
        running_job.in_flight_run = None;

        let mut found_rec = false;
        for rec in running_job.history.iter_mut().rev() {
            if rec.current_run == parsed.current_run {
                rec.duration_ms = Some(parsed.duration_ms);
                rec.outcome.clone_from(&parsed.outcome);
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
                running_job.current_run += 1;
                let skipped_run = running_job.current_run;
                running_job.record_execution(
                    ExecutionRecord::new(
                        &fire.to_rfc3339(),
                        &now.to_rfc3339(),
                        outcome::SKIPPED_ALREADY_IN_FLIGHT,
                        skipped_run,
                    )
                    .with_outcome_ctx(parsed.current_run.to_string()),
                );
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
    if count == 1 {
        tracing::info!("Reloaded 1 job");
    } else {
        tracing::info!("Reloaded {count} jobs");
    }
}
