// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Execution-history serialization helpers for the HTTP query API.
//!
//! Converts execution records and related data into JSON-serializable
//! structures for the actix-web endpoints.

use serde::Serialize;

use crate::job::ExecutionRecord;

/// Per-level log entry count summary for a single execution record.
#[derive(Serialize)]
pub struct LogSummary {
    /// Count of SYSTEM-level entries.
    pub system: usize,
    /// Count of INFO-level entries.
    pub info: usize,
    /// Count of WARNING-level entries.
    pub warn: usize,
    /// Count of ERROR/CRITICAL-level entries.
    pub error: usize,
}

/// A single execution record enriched with job metadata for JSON responses.
#[derive(Serialize)]
pub struct RecordResponse {
    /// Unique job identifier.
    pub job_id: i64,
    /// Human-readable job name.
    pub job_name: String,
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
    /// Per-level log entry count summary.
    pub log_summary: LogSummary,
}

/// Converts a single execution record into a JSON-serializable response struct.
pub fn record_to_response(rec: &ExecutionRecord, job_id: i64, job_name: &str) -> RecordResponse {
    let mut log_counts = [0usize; 4];
    for entry in &rec.log_entries {
        let bucket = match entry.level.as_str() {
            "SYSTEM" => 0,
            "WARNING" | "WARN" => 2,
            "ERROR" | "CRITICAL" => 3,
            _ => 1,
        };
        if let Some(slot) = log_counts.get_mut(bucket) {
            *slot += 1;
        }
    }

    RecordResponse {
        job_id,
        job_name: job_name.to_string(),
        planned_fire_time_iso: rec.planned_fire_time_iso.clone(),
        actual_fire_time_iso: rec.actual_fire_time_iso.clone(),
        delay_ms: rec.delay_ms,
        outcome: rec.outcome.clone(),
        current_run: rec.current_run,
        duration_ms: rec.duration_ms,
        error: rec.error.clone(),
        outcome_ctx: rec.outcome_ctx.clone(),
        log_summary: LogSummary {
            system: log_counts[0],
            info: log_counts[1],
            warn: log_counts[2],
            error: log_counts[3],
        },
    }
}

/// Converts a slice of execution records into a vector of response structs.
pub fn records_to_responses(records: &[ExecutionRecord], job_id: i64, job_name: &str) -> Vec<RecordResponse> {
    records.iter().map(|rec| record_to_response(rec, job_id, job_name)).collect()
}
