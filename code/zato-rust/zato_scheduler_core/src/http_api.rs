// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! HTTP query API served by actix-web for the Zato server to read scheduler state.
//!
//! All endpoints are GET-only, served on 127.0.0.1 on the port given by the
//! `Zato_Scheduler_HTTP_Port` environment variable (35100 by default), no authentication.

use std::sync::Arc;

use actix_web::{App, HttpResponse, HttpServer, web};
use chrono::{DateTime, Utc};
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

/// Default port for the HTTP query API when `Zato_Scheduler_HTTP_Port` is not set.
pub const DEFAULT_HTTP_PORT: u16 = 35100;

/// Starts the actix-web HTTP server on 127.0.0.1 on the given port.
///
/// This function blocks until the server shuts down.
pub async fn start_http_server(shared: Arc<SchedulerShared>, http_port: u16) -> std::io::Result<()> {
    let state = web::Data::new(AppState { shared });

    tracing::info!("Starting HTTP query API on 127.0.0.1:{http_port}");

    let server = HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/metrics", web::get().to(get_metrics))
            .route("/api/get_job_summaries", web::get().to(get_job_summaries))
            .route("/api/get_chart_data", web::get().to(get_chart_data))
            .route("/api/get_timeline_events_since", web::get().to(get_timeline_events_since))
            .route("/api/get_history_page", web::get().to(get_history_page))
            .route("/api/get_history_since", web::get().to(get_history_since))
            .route("/api/get_run_detail", web::get().to(get_run_detail))
            .route("/api/get_log_entries", web::get().to(get_log_entries))
    })
    .bind(("127.0.0.1", http_port))
    // A failed bind means another process owns the port - the caller shuts the whole scheduler down.
    .map_err(|err| {
        tracing::error!("Cannot bind HTTP query API to 127.0.0.1:{http_port}: {err}");
        err
    })?;

    server.run().await
}

/// Returns all scheduler metrics in Prometheus text exposition format.
async fn get_metrics() -> HttpResponse {
    let body = crate::metrics::encode_metrics();
    HttpResponse::Ok()
        .content_type("text/plain; version=0.0.4; charset=utf-8")
        .body(body)
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

/// Query parameters for get_chart_data.
#[derive(Deserialize)]
struct ChartDataParams {
    /// ISO timestamp of the window start. If absent (together with `until_iso`), the server
    /// derives bucket boundaries from the actual data extent (used by the "All" range).
    since_iso: Option<String>,
    /// ISO timestamp of the window end. Must be provided together with `since_iso` to enable
    /// fixed-grid bucketing. When both are present, records outside [since_iso, until_iso) are
    /// excluded and the 120 buckets are distributed evenly across this fixed window.
    until_iso: Option<String>,
}

/// A single time bucket with per-outcome counts.
#[derive(Serialize, Deserialize)]
struct ChartBucket {
    /// ISO timestamp of the bucket start.
    start_iso: String,
    /// ISO timestamp of the bucket end.
    end_iso: String,
    /// Count of successful executions in this bucket.
    ok: u64,
    /// Count of failed executions in this bucket.
    error: u64,
    /// Count of timed-out executions in this bucket.
    timeout: u64,
    /// Count of skipped (already in flight) executions in this bucket.
    skipped_already_in_flight: u64,
}

/// Response structure for chart data.
#[derive(Serialize, Deserialize)]
struct ChartDataResponse {
    /// Pre-aggregated time buckets.
    buckets: Vec<ChartBucket>,
    /// ISO timestamp of the earliest event in the window.
    min_time_iso: String,
    /// ISO timestamp of the latest event in the window.
    max_time_iso: String,
}

/// Number of fixed buckets returned by the chart data endpoint.
const CHART_BUCKET_COUNT: usize = 120;


/// Returns pre-aggregated chart data as 120 time buckets with per-outcome counts.
///
/// # Bucket boundary stability
///
/// The client sends `since_iso` and `until_iso` to define a fixed time window for bucketing.
/// This ensures bucket boundaries are deterministic and do not shift when new records arrive.
/// Without fixed boundaries, every new record would shift `max_ms`, redistribute all 120 buckets,
/// and make the chart visually unstable across consecutive polls.
///
/// The client computes these boundaries using one of two strategies depending on the selected
/// time range:
///
/// ## Category A - Sliding windows (5 min, 15 min, 30 min, 1 hour, 6 hours)
///
/// These are relative to "now" and use grid-snapped boundaries:
///
/// ```text
/// bucket_size_ms = range_ms / 120
/// until_ms       = ceil(now_ms / bucket_size_ms) * bucket_size_ms
/// since_ms       = until_ms - range_ms
/// ```
///
/// Grid advance intervals (how often boundaries shift by one bucket):
/// - 5 min range:  bucket = 2,500ms,  grid advances every 2.5 seconds
/// - 15 min range: bucket = 7,500ms,  grid advances every 7.5 seconds
/// - 30 min range: bucket = 15,000ms, grid advances every 15 seconds
/// - 1 hour range: bucket = 30,000ms, grid advances every 30 seconds
/// - 6 hour range: bucket = 180,000ms, grid advances every 3 minutes
///
/// Within each advance interval, the bucket boundaries are identical no matter how many
/// times the client polls.
///
/// ## Category B - Calendar-anchored (Today, Yesterday, This week, This month, This year)
///
/// These use hard calendar boundaries that never shift within their period:
/// - Today:      since = today 00:00:00 local,     until = tomorrow 00:00:00 local
/// - Yesterday:  since = yesterday 00:00:00 local, until = today 00:00:00 local
/// - This week:  since = Monday 00:00:00 local,    until = next Monday 00:00:00 local
/// - This month: since = 1st 00:00:00 local,       until = 1st next month 00:00:00 local
/// - This year:  since = Jan 1 00:00:00 local,     until = Jan 1 next year 00:00:00 local
///
/// These produce completely stable bucket boundaries for their entire period.
///
/// ## "All" range
///
/// When `since_iso` and `until_iso` are both absent, the server derives boundaries from
/// the actual data extent (min/max of all records). This is the only mode where the chart
/// can shift on every poll, which is acceptable because "All" has no fixed span to anchor to.
async fn get_chart_data(state: web::Data<AppState>, params: web::Query<ChartDataParams>) -> HttpResponse {

    let fixed_window = match (params.since_iso.as_deref(), params.until_iso.as_deref()) {
        (Some(since), Some(until)) if !since.is_empty() && !until.is_empty() => {
            let since_ms = DateTime::parse_from_rfc3339(since)
                .map(|dt| dt.timestamp_millis())
                .unwrap_or(0);
            let until_ms = DateTime::parse_from_rfc3339(until)
                .map(|dt| dt.timestamp_millis())
                .unwrap_or(0);
            if since_ms > 0 && until_ms > since_ms {
                Some((since_ms, until_ms))
            } else {
                None
            }
        }
        _ => None,
    };

    // outcome_index: 0=ok, 1=error, 2=timeout, 3=skipped
    let (window_min, window_max, events) = {
        let scheduler_state = state.shared.state.lock();

        let mut collected: Vec<(i64, usize)> = Vec::new();

        for running_job in scheduler_state.jobs.values() {
            for rec in &running_job.history {
                let outcome_index = match rec.outcome.as_str() {
                    outcome::EXECUTED => 0,
                    outcome::ERROR => 1,
                    outcome::TIMEOUT => 2,
                    outcome::SKIPPED_ALREADY_IN_FLIGHT => 3,
                    _ => continue,
                };

                if let Ok(parsed) = DateTime::parse_from_rfc3339(&rec.actual_fire_time_iso) {
                    let ms = parsed.timestamp_millis();

                    if let Some((since_ms, until_ms)) = fixed_window {
                        if ms < since_ms || ms >= until_ms {
                            continue;
                        }
                    }

                    collected.push((ms, outcome_index));
                }
            }
        }

        if let Some((since_ms, until_ms)) = fixed_window {
            (since_ms, until_ms, collected)
        } else if collected.is_empty() {
            let now_ms = Utc::now().timestamp_millis();
            (now_ms, now_ms, collected)
        } else {
            let mut min_ms: i64 = i64::MAX;
            let mut max_ms: i64 = i64::MIN;
            for (ms, _) in &collected {
                if *ms < min_ms { min_ms = *ms; }
                if *ms > max_ms { max_ms = *ms; }
            }
            if max_ms == min_ms {
                (min_ms - 3_600_000, max_ms, collected)
            } else {
                (min_ms, max_ms, collected)
            }
        }
    };

    let time_range = window_max - window_min;
    let effective_range = if time_range == 0 { 3_600_000 } else { time_range };
    let bucket_size_ms = effective_range as f64 / CHART_BUCKET_COUNT as f64;

    let mut bucket_counts = vec![[0u64; 4]; CHART_BUCKET_COUNT];

    for (ms, outcome_index) in &events {
        let bucket_index = ((*ms - window_min) as f64 / bucket_size_ms) as i64;
        let bucket_index = bucket_index.clamp(0, (CHART_BUCKET_COUNT - 1) as i64) as usize;
        bucket_counts[bucket_index][*outcome_index] += 1;
    }

    let mut buckets: Vec<ChartBucket> = Vec::with_capacity(CHART_BUCKET_COUNT);
    for bucket_index in 0..CHART_BUCKET_COUNT {
        let start_ms = window_min + (bucket_index as f64 * bucket_size_ms) as i64;
        let end_ms = window_min + ((bucket_index + 1) as f64 * bucket_size_ms) as i64;

        let start_iso = DateTime::from_timestamp_millis(start_ms)
            .unwrap_or_else(|| Utc::now())
            .to_rfc3339();
        let end_iso = DateTime::from_timestamp_millis(end_ms)
            .unwrap_or_else(|| Utc::now())
            .to_rfc3339();

        let counts = &bucket_counts[bucket_index];
        buckets.push(ChartBucket {
            start_iso,
            end_iso,
            ok: counts[0],
            error: counts[1],
            timeout: counts[2],
            skipped_already_in_flight: counts[3],
        });
    }

    let min_time_iso = DateTime::from_timestamp_millis(window_min)
        .unwrap_or_else(|| Utc::now())
        .to_rfc3339();
    let max_time_iso = DateTime::from_timestamp_millis(window_max)
        .unwrap_or_else(|| Utc::now())
        .to_rfc3339();

    let response = ChartDataResponse {
        buckets,
        min_time_iso,
        max_time_iso,
    };

    HttpResponse::Ok().json(response)
}

/// Query parameters for get_timeline_events_since.
#[derive(Deserialize)]
struct TimelineEventsSinceParams {
    /// ISO timestamp cutoff - only return events strictly after this time.
    since_iso: Option<String>,
    /// Maximum number of events to return (for initial load of the recent table).
    limit: Option<usize>,
}

/// Response structure for timeline events.
#[derive(Serialize, Deserialize)]
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

/// Returns timeline events, optionally filtered by since_iso and capped by limit.
async fn get_timeline_events_since(state: web::Data<AppState>, params: web::Query<TimelineEventsSinceParams>) -> HttpResponse {
    let since_cutoff = params.since_iso.as_deref().unwrap_or("");

    let events: Vec<job::TimelineEvent> = {
        let scheduler_state = state.shared.state.lock();
        let mut events: Vec<job::TimelineEvent> = Vec::new();

        for (job_id, running_job) in &scheduler_state.jobs {
            for rec in &running_job.history {
                if !since_cutoff.is_empty() {
                    if rec.actual_fire_time_iso.as_str() <= since_cutoff {
                        continue;
                    }
                }
                events.push(job::TimelineEvent {
                    job_id: *job_id,
                    job_name: running_job.name.clone(),
                    record: rec.clone(),
                });
            }
        }

        drop(scheduler_state);
        events.sort_unstable_by(|lhs, rhs| rhs.record.actual_fire_time_iso.cmp(&lhs.record.actual_fire_time_iso));

        if let Some(limit) = params.limit {
            events.truncate(limit);
        }

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
    /// ISO timestamp cutoff - only records at or after this time are included.
    since_iso: Option<String>,
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
    let since_cutoff = params.since_iso.as_deref().unwrap_or("");

    let (records, total, job_name) = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.get(&params.job_id).map_or_else(
            || (Vec::new(), 0, String::new()),
            |running_job| {
                let name = running_job.name.clone();
                let mut total: usize = 0;
                let mut page: Vec<job::ExecutionRecord> = Vec::with_capacity(params.limit);
                let mut skipped: usize = 0;

                for rec in running_job.history.iter().rev() {
                    if !since_cutoff.is_empty() && rec.actual_fire_time_iso.as_str() < since_cutoff {
                        continue;
                    }

                    if let Some(allowed) = &filter {
                        if !allowed.iter().any(|allowed_val| allowed_val == &rec.outcome) {
                            continue;
                        }
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
    /// Range cutoff - only count records at or after this time toward `total`.
    range_since_iso: Option<String>,
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
    let range_cutoff = params.range_since_iso.as_deref().unwrap_or("");

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
                        if range_cutoff.is_empty() || rec.actual_fire_time_iso.as_str() >= range_cutoff {
                            total += 1;
                        }
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    use actix_web::web;

    use crate::job::{ExecutionRecord, RunningJob};
    use crate::model::SchedulerJob;
    use crate::scheduler::SchedulerShared;

    fn make_shared(jobs: HashMap<i64, RunningJob>) -> Arc<SchedulerShared> {
        let shared = Arc::new(SchedulerShared::new());
        {
            let mut state = shared.state.lock();
            state.jobs = jobs;
        }
        shared
    }

    fn make_scheduler_job(id: i64, name: &str) -> SchedulerJob {
        SchedulerJob {
            id,
            name: name.to_string(),
            is_active: true,
            service: "test_service".into(),
            job_type: "interval_based".into(),
            start_date: "2025-01-01T00:00:00".into(),
            extra: None,
            weeks: None,
            days: None,
            hours: None,
            minutes: Some(5),
            seconds: None,
            repeats: None,
            jitter_ms: None,
            timezone: None,
            calendar: None,
            max_execution_time_ms: None,
            on_success_service: None,
            on_success_job: None,
            on_error_service: None,
            on_error_job: None,
        }
    }

    fn make_record(actual_iso: &str, outcome_label: &str, run: u32) -> ExecutionRecord {
        ExecutionRecord::new("2026-01-01T00:00:00+00:00", actual_iso, outcome_label, run)
    }

    fn make_job_with_records(id: i64, name: &str, records: Vec<ExecutionRecord>) -> RunningJob {
        let scheduler_job = make_scheduler_job(id, name);
        let mut job = RunningJob::from_scheduler_job(&scheduler_job);
        for rec in records {
            job.history.push_back(rec);
        }
        job
    }

    #[actix_web::test]
    async fn test_get_chart_data_empty() {
        let shared = make_shared(HashMap::new());
        let state = web::Data::new(AppState { shared });
        let params = web::Query(ChartDataParams { since_iso: None });

        let response = get_chart_data(state, params).await;
        assert_eq!(response.status(), 200);
    }

    #[actix_web::test]
    async fn test_get_chart_data_bucketing() {
        let mut jobs = HashMap::new();
        let records = vec![
            make_record("2026-01-01T10:00:00+00:00", outcome::EXECUTED, 1),
            make_record("2026-01-01T10:30:00+00:00", outcome::EXECUTED, 2),
            make_record("2026-01-01T10:30:01+00:00", outcome::ERROR, 3),
            make_record("2026-01-01T11:00:00+00:00", outcome::TIMEOUT, 4),
        ];
        jobs.insert(1, make_job_with_records(1, "test_job", records));

        let shared = make_shared(jobs);
        let state = web::Data::new(AppState { shared });
        let params = web::Query(ChartDataParams { since_iso: None });

        let response = get_chart_data(state, params).await;
        assert_eq!(response.status(), 200);

        let body = response.into_body();
        let bytes = actix_web::body::to_bytes(body).await.unwrap();
        let data: ChartDataResponse = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(data.buckets.len(), CHART_BUCKET_COUNT);

        let mut total_ok: u64 = 0;
        let mut total_error: u64 = 0;
        let mut total_timeout: u64 = 0;
        for bucket in &data.buckets {
            total_ok += bucket.ok;
            total_error += bucket.error;
            total_timeout += bucket.timeout;
        }
        assert_eq!(total_ok, 2);
        assert_eq!(total_error, 1);
        assert_eq!(total_timeout, 1);
    }

    #[actix_web::test]
    async fn test_get_chart_data_since_iso_filters() {
        let mut jobs = HashMap::new();
        let records = vec![
            make_record("2026-01-01T08:00:00+00:00", outcome::EXECUTED, 1),
            make_record("2026-01-01T12:00:00+00:00", outcome::EXECUTED, 2),
        ];
        jobs.insert(1, make_job_with_records(1, "test_job", records));

        let shared = make_shared(jobs);
        let state = web::Data::new(AppState { shared });
        let params = web::Query(ChartDataParams {
            since_iso: Some("2026-01-01T10:00:00+00:00".to_string()),
        });

        let response = get_chart_data(state, params).await;
        let body = response.into_body();
        let bytes = actix_web::body::to_bytes(body).await.unwrap();
        let data: ChartDataResponse = serde_json::from_slice(&bytes).unwrap();

        let mut total_ok: u64 = 0;
        for bucket in &data.buckets {
            total_ok += bucket.ok;
        }
        assert_eq!(total_ok, 1);
    }

    #[actix_web::test]
    async fn test_get_timeline_events_since_no_filter() {
        let mut jobs = HashMap::new();
        let records = vec![
            make_record("2026-01-01T10:00:00+00:00", outcome::EXECUTED, 1),
            make_record("2026-01-01T10:01:00+00:00", outcome::ERROR, 2),
            make_record("2026-01-01T10:02:00+00:00", outcome::EXECUTED, 3),
        ];
        jobs.insert(1, make_job_with_records(1, "test_job", records));

        let shared = make_shared(jobs);
        let state = web::Data::new(AppState { shared });
        let params = web::Query(TimelineEventsSinceParams { since_iso: None, limit: None });

        let response = get_timeline_events_since(state, params).await;
        let body = response.into_body();
        let bytes = actix_web::body::to_bytes(body).await.unwrap();
        let events: Vec<TimelineEventResponse> = serde_json::from_slice(&bytes).unwrap();

        assert_eq!(events.len(), 3);
        assert_eq!(events[0].actual_fire_time_iso, "2026-01-01T10:02:00+00:00");
    }

    #[actix_web::test]
    async fn test_get_timeline_events_since_with_cutoff() {
        let mut jobs = HashMap::new();
        let records = vec![
            make_record("2026-01-01T10:00:00+00:00", outcome::EXECUTED, 1),
            make_record("2026-01-01T10:01:00+00:00", outcome::ERROR, 2),
            make_record("2026-01-01T10:02:00+00:00", outcome::EXECUTED, 3),
        ];
        jobs.insert(1, make_job_with_records(1, "test_job", records));

        let shared = make_shared(jobs);
        let state = web::Data::new(AppState { shared });
        let params = web::Query(TimelineEventsSinceParams {
            since_iso: Some("2026-01-01T10:01:00+00:00".to_string()),
            limit: None,
        });

        let response = get_timeline_events_since(state, params).await;
        let body = response.into_body();
        let bytes = actix_web::body::to_bytes(body).await.unwrap();
        let events: Vec<TimelineEventResponse> = serde_json::from_slice(&bytes).unwrap();

        assert_eq!(events.len(), 1);
        assert_eq!(events[0].actual_fire_time_iso, "2026-01-01T10:02:00+00:00");
    }

    #[actix_web::test]
    async fn test_get_timeline_events_since_with_limit() {
        let mut jobs = HashMap::new();
        let records = vec![
            make_record("2026-01-01T10:00:00+00:00", outcome::EXECUTED, 1),
            make_record("2026-01-01T10:01:00+00:00", outcome::ERROR, 2),
            make_record("2026-01-01T10:02:00+00:00", outcome::EXECUTED, 3),
        ];
        jobs.insert(1, make_job_with_records(1, "test_job", records));

        let shared = make_shared(jobs);
        let state = web::Data::new(AppState { shared });
        let params = web::Query(TimelineEventsSinceParams {
            since_iso: None,
            limit: Some(2),
        });

        let response = get_timeline_events_since(state, params).await;
        let body = response.into_body();
        let bytes = actix_web::body::to_bytes(body).await.unwrap();
        let events: Vec<TimelineEventResponse> = serde_json::from_slice(&bytes).unwrap();

        assert_eq!(events.len(), 2);
    }
}
