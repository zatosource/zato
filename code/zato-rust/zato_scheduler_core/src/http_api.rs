// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! HTTP query API served by actix-web for the Zato server to read scheduler state.
//!
//! All endpoints are GET-only, served on 127.0.0.1:35100, no authentication.

use std::sync::Arc;

use actix_web::{App, HttpResponse, HttpServer, web};
use serde::{Deserialize, Serialize};

use crate::history;
use crate::job;
use crate::scheduler::SchedulerShared;
use crate::types::outcome;

/// Shared application state passed to all actix-web handlers.
struct AppState {
    /// Reference to the scheduler's shared state.
    shared: Arc<SchedulerShared>,
}

/// Starts the actix-web HTTP server on 127.0.0.1:35100.
///
/// This function blocks until the server shuts down.
pub async fn start_http_server(shared: Arc<SchedulerShared>) -> std::io::Result<()> {
    let state = web::Data::new(AppState { shared });

    tracing::info!("Starting HTTP query API on 127.0.0.1:35100");

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/api/get_job_summaries", web::get().to(get_job_summaries))
            .route("/api/get_timeline_events", web::get().to(get_timeline_events))
            .route("/api/get_history_page", web::get().to(get_history_page))
            .route("/api/get_history_since", web::get().to(get_history_since))
            .route("/api/get_run_detail", web::get().to(get_run_detail))
            .route("/api/get_log_entries", web::get().to(get_log_entries))
    })
    .bind("127.0.0.1:35100")?
    .run()
    .await
}

/// Returns a summary list of all jobs including history-derived fields.
async fn get_job_summaries(state: web::Data<AppState>) -> HttpResponse {
    let summaries: Vec<job::JobSummary> = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.values().map(job::RunningJob::summary).collect()
    };

    let countable = outcome::COUNTABLE;
    let response: Vec<JobSummaryResponse> = summaries
        .iter()
        .map(|summary| {
            let mut outcome_counts = serde_json::Map::new();
            for (label, count) in countable.iter().zip(&summary.outcome_counts) {
                outcome_counts.insert((*label).to_string(), serde_json::Value::from(*count));
            }
            JobSummaryResponse {
                id: summary.id,
                name: summary.name.clone(),
                is_active: summary.is_active,
                service: summary.service.clone(),
                job_type: summary.job_type.clone(),
                in_flight: summary.in_flight,
                current_run: summary.current_run,
                interval_ms: summary.interval_ms,
                next_fire_utc: summary.next_fire_utc.clone(),
                last_outcome: summary.last_outcome.clone(),
                last_duration_ms: summary.last_duration_ms,
                recent_outcomes: summary.recent_outcomes.clone(),
                outcome_counts,
            }
        })
        .collect();

    HttpResponse::Ok().json(response)
}

/// Response structure for job summaries.
#[derive(Serialize)]
struct JobSummaryResponse {
    /// Unique job identifier.
    id: i64,
    /// Human-readable job name.
    name: String,
    /// Whether the job is enabled.
    is_active: bool,
    /// Zato service to invoke.
    service: String,
    /// Job type label.
    job_type: String,
    /// Whether the job is currently executing.
    in_flight: bool,
    /// Current run counter.
    current_run: u32,
    /// Computed interval between firings (ms).
    interval_ms: u64,
    /// Next scheduled fire time as an ISO string.
    next_fire_utc: Option<String>,
    /// Outcome label of the most recent execution.
    last_outcome: Option<String>,
    /// Duration of the most recent completed execution (ms).
    last_duration_ms: Option<u64>,
    /// Outcome labels of the last 10 executions.
    recent_outcomes: Vec<String>,
    /// Per-outcome execution counts.
    outcome_counts: serde_json::Map<String, serde_json::Value>,
}

/// Query parameters for get_timeline_events.
#[derive(Deserialize)]
struct TimelineParams {
    /// Maximum number of events to return (default 1000).
    max_events: Option<usize>,
}

/// Response structure for timeline events.
#[derive(Serialize)]
struct TimelineEventResponse {
    /// Execution outcome label.
    outcome: String,
    /// ISO timestamp of the actual fire time.
    actual_fire_time_iso: String,
    /// Unique job identifier.
    job_id: i64,
    /// Human-readable job name.
    job_name: String,
    /// Execution duration in milliseconds.
    duration_ms: Option<u64>,
    /// Error message, if the execution failed.
    error: Option<String>,
    /// Additional context for the outcome.
    outcome_ctx: Option<String>,
    /// Run counter at the time of this execution.
    current_run: u32,
    /// ISO timestamp of the planned fire time.
    planned_fire_time_iso: String,
}

/// Returns a lightweight timeline of execution events for the dashboard chart.
async fn get_timeline_events(state: web::Data<AppState>, params: web::Query<TimelineParams>) -> HttpResponse {
    let max_events = params.max_events.unwrap_or(1000);

    let events: Vec<job::TimelineEvent> = {
        let scheduler_state = state.shared.state.lock();
        let mut events: Vec<job::TimelineEvent> = Vec::new();
        for (job_id, running_job) in &scheduler_state.jobs {
            for rec in &running_job.history {
                events.push(job::TimelineEvent {
                    job_id: *job_id,
                    job_name: running_job.name.clone(),
                    record: rec.clone(),
                });
            }
        }
        drop(scheduler_state);
        events.sort_unstable_by(|lhs, rhs| rhs.record.actual_fire_time_iso.cmp(&lhs.record.actual_fire_time_iso));
        events.truncate(max_events);
        events
    };

    let response: Vec<TimelineEventResponse> = events
        .iter()
        .map(|event| {
            let rec = &event.record;
            TimelineEventResponse {
                outcome: rec.outcome.clone(),
                actual_fire_time_iso: rec.actual_fire_time_iso.clone(),
                job_id: event.job_id,
                job_name: event.job_name.clone(),
                duration_ms: rec.duration_ms,
                error: rec.error.clone(),
                outcome_ctx: rec.outcome_ctx.clone(),
                current_run: rec.current_run,
                planned_fire_time_iso: rec.planned_fire_time_iso.clone(),
            }
        })
        .collect();

    HttpResponse::Ok().json(response)
}

/// Query parameters for get_history_page.
#[derive(Deserialize)]
struct HistoryPageParams {
    /// Job identifier.
    job_id: i64,
    /// Zero-based offset into the history.
    offset: usize,
    /// Maximum number of records to return.
    limit: usize,
    /// Comma-separated list of outcome filters, or "all".
    outcomes: Option<String>,
}

/// Response structure for paginated history.
#[derive(Serialize)]
struct HistoryPageResponse {
    /// Page of execution records.
    records: Vec<history::RecordResponse>,
    /// Total number of completed (non-running) records matching the filter.
    total: usize,
}

/// Returns a page of execution-history records for a single job.
async fn get_history_page(state: web::Data<AppState>, params: web::Query<HistoryPageParams>) -> HttpResponse {
    let filter = parse_outcome_filter(params.outcomes.as_deref());

    let (records, total, job_name) = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.get(&params.job_id).map_or_else(
            || (Vec::new(), 0, String::new()),
            |running_job| {
                let name = running_job.name.clone();
                let (page, total) = filter.as_ref().map_or_else(
                    || {
                        let total = running_job.history.iter().filter(|rec| rec.outcome != outcome::RUNNING).count();
                        let all_len = running_job.history.len();
                        let start = if params.offset >= all_len {
                            all_len
                        } else {
                            all_len - params.offset
                        };
                        let range_end = start.saturating_sub(params.limit);
                        let page: Vec<job::ExecutionRecord> = running_job.history.range(range_end..start).rev().cloned().collect();
                        (page, total)
                    },
                    |allowed| {
                        let mut total: usize = 0;
                        let mut page: Vec<job::ExecutionRecord> = Vec::with_capacity(params.limit);
                        let mut skipped: usize = 0;

                        for rec in running_job.history.iter().rev() {
                            if !allowed.iter().any(|allowed_val| allowed_val == &rec.outcome) {
                                continue;
                            }
                            if rec.outcome != outcome::RUNNING {
                                total += 1;
                            }
                            if page.len() < params.limit {
                                if skipped < params.offset {
                                    skipped += 1;
                                } else {
                                    page.push(rec.clone());
                                }
                            }
                        }
                        (page, total)
                    },
                );
                (page, total, name)
            },
        )
    };

    let response = HistoryPageResponse {
        records: history::records_to_responses(&records, params.job_id, &job_name),
        total,
    };

    HttpResponse::Ok().json(response)
}

/// Query parameters for get_history_since.
#[derive(Deserialize)]
struct HistorySinceParams {
    /// Job identifier.
    job_id: i64,
    /// ISO timestamp to fetch records after.
    since_iso: String,
    /// Comma-separated list of outcome filters, or "all".
    outcomes: Option<String>,
    /// Comma-separated list of run numbers to always include.
    running_runs: Option<String>,
}

/// Response structure for history-since queries.
#[derive(Serialize)]
struct HistorySinceResponse {
    /// Records added since the given timestamp.
    rows: Vec<history::RecordResponse>,
    /// Total number of completed records matching the filter.
    total: usize,
}

/// Returns records added since a given ISO timestamp.
async fn get_history_since(state: web::Data<AppState>, params: web::Query<HistorySinceParams>) -> HttpResponse {
    let filter = parse_outcome_filter(params.outcomes.as_deref());
    let running_runs: Vec<u32> = params
        .running_runs
        .as_deref()
        .unwrap_or("")
        .split(',')
        .filter_map(|val| val.trim().parse::<u32>().ok())
        .collect();

    let (records, total, job_name) = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.get(&params.job_id).map_or_else(
            || (Vec::new(), 0, String::new()),
            |running_job| {
                let name = running_job.name.clone();
                let mut records: Vec<job::ExecutionRecord> = Vec::new();
                let mut total: usize = 0;

                for rec in &running_job.history {
                    let outcome_allowed = filter
                        .as_ref()
                        .is_none_or(|allowed| allowed.iter().any(|allowed_val| allowed_val == &rec.outcome));

                    if outcome_allowed && rec.outcome != outcome::RUNNING {
                        total += 1;
                    }

                    let run_override = running_runs.contains(&rec.current_run);
                    let is_since = rec.actual_fire_time_iso.as_str() >= params.since_iso.as_str() || run_override;
                    if is_since && (outcome_allowed || run_override) {
                        records.push(rec.clone());
                    }
                }

                records.reverse();
                (records, total, name)
            },
        )
    };

    let response = HistorySinceResponse {
        rows: history::records_to_responses(&records, params.job_id, &job_name),
        total,
    };

    HttpResponse::Ok().json(response)
}

/// Query parameters for get_run_detail.
#[derive(Deserialize)]
struct RunDetailParams {
    /// Job identifier.
    job_id: i64,
    /// Run number to retrieve.
    current_run: u32,
}

/// Response structure for run detail.
#[derive(Serialize)]
struct RunDetailResponse {
    /// The execution record, if found.
    record: Option<history::RecordResponse>,
    /// Previous run number for navigation.
    prev_run: Option<u32>,
    /// Next run number for navigation.
    next_run: Option<u32>,
}

/// Returns a single execution record by run number with prev/next navigation.
async fn get_run_detail(state: web::Data<AppState>, params: web::Query<RunDetailParams>) -> HttpResponse {
    let result = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.get(&params.job_id).and_then(|running_job| {
            let mut prev_run: Option<u32> = None;
            let mut found: Option<job::ExecutionRecord> = None;
            let mut next_run: Option<u32> = None;

            for rec in &running_job.history {
                if found.is_some() {
                    next_run = Some(rec.current_run);
                    break;
                }
                if rec.current_run == params.current_run {
                    found = Some(rec.clone());
                } else {
                    prev_run = Some(rec.current_run);
                }
            }

            found.map(|rec| (rec, running_job.name.clone(), prev_run, next_run))
        })
    };

    let response = if let Some((rec, job_name, prev_run, next_run)) = result {
        RunDetailResponse {
            record: Some(history::record_to_response(&rec, params.job_id, &job_name)),
            prev_run,
            next_run,
        }
    } else {
        RunDetailResponse {
            record: None,
            prev_run: None,
            next_run: None,
        }
    };

    HttpResponse::Ok().json(response)
}

/// Query parameters for get_log_entries.
#[derive(Deserialize)]
struct LogEntriesParams {
    /// Job identifier.
    job_id: i64,
    /// Run number to get logs for.
    current_run: u32,
    /// Index to start from (0 = all entries, >0 = incremental).
    since_idx: usize,
}

/// Returns log entries for a specific execution record.
async fn get_log_entries(state: web::Data<AppState>, params: web::Query<LogEntriesParams>) -> HttpResponse {
    let entries: Vec<job::LogEntry> = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.get(&params.job_id).map_or_else(Vec::new, |running_job| {
            let mut found = Vec::new();
            for rec in running_job.history.iter().rev() {
                if rec.current_run == params.current_run {
                    found = rec.log_entries.iter().skip(params.since_idx).cloned().collect();
                    break;
                }
            }
            found
        })
    };

    HttpResponse::Ok().json(entries)
}

/// Parses a comma-separated outcome filter string into an optional allow-list.
fn parse_outcome_filter(outcomes: Option<&str>) -> Option<Vec<String>> {
    let outcomes = outcomes?;
    if outcomes == outcome::ALL {
        return None;
    }
    let mut items: Vec<String> = outcomes.split(',').map(|val| val.trim().to_string()).collect();
    if !items.iter().any(|val| val == outcome::RUNNING) {
        items.push(outcome::RUNNING.to_string());
    }
    Some(items)
}
