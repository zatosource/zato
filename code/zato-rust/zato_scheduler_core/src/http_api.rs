// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! HTTP query API served by actix-web for the Zato server to read scheduler state.
//!
//! Execution history lives in the server's audit log, so the API exposes only what
//! the scheduler itself owns: Prometheus metrics and per-job scheduling summaries.
//! All endpoints are GET-only, served on 127.0.0.1 on the port given by the
//! `Zato_Scheduler_HTTP_Port` environment variable (35100 by default), no authentication.

use std::sync::Arc;

use actix_web::{App, HttpResponse, HttpServer, web};

use crate::job;
use crate::scheduler::SchedulerShared;

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

/// Returns the scheduling-state summary of every job.
async fn get_job_summaries(state: web::Data<AppState>) -> HttpResponse {
    let summaries: Vec<job::JobSummary> = {
        let scheduler_state = state.shared.state.lock();
        scheduler_state.jobs.values().map(job::RunningJob::summary).collect()
    };

    HttpResponse::Ok().json(summaries)
}
