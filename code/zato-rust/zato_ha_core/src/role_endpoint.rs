// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The HTTP endpoints that a load balancer and Kubernetes probe.
//!
//! `GET /zato/ha/role` answers 200 only on an active node that is not isolated, and `GET /zato/ha/health`
//! answers 200 in every role, which is what a readiness probe needs.

use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::time::Duration;

use serde::Serialize;

use crate::state::{LinkState, LogPosition, Role, Shared};
use crate::wire;

/// The path of the role endpoint.
pub const ROLE_PATH: &str = "/zato/ha/role";

/// The path of the health endpoint.
pub const HEALTH_PATH: &str = "/zato/ha/health";

/// How long a client may take to send its request.
const REQUEST_TIMEOUT: Duration = Duration::from_secs(2);

/// The progress of one database in the report.
#[derive(Serialize)]
struct DatabaseReport {
    /// The name of the database.
    name: &'static str,

    /// The end of the log at the last scan.
    scanned: LogPosition,

    /// The end of what the standby confirmed.
    confirmed: LogPosition,
}

/// The body of both endpoints.
#[derive(Serialize)]
struct RoleReport {
    /// The name of the node.
    node: String,

    /// The role of the node.
    role: Role,

    /// The generation of the node.
    generation: u64,

    /// Whether the node lost both the standby and the referee.
    isolated: bool,

    /// Whether an admission holds the barriers.
    admitting: bool,

    /// The state of the link on the active node.
    link: LinkState,

    /// The progress of each database.
    databases: Vec<DatabaseReport>,
}

/// Builds the report and tells whether the node serves traffic.
fn report(shared: &Shared) -> (bool, RoleReport) {
    let state = shared.state.lock();
    let serving = state.role.is_active() && !state.isolated;
    let databases = state
        .databases
        .iter()
        .map(|progress| DatabaseReport {
            name: progress.name,
            scanned: progress.scanned,
            confirmed: progress.confirmed,
        })
        .collect();
    let out = RoleReport {
        node: shared.config.node_name.clone(),
        role: state.role,
        generation: state.generation,
        isolated: state.isolated,
        admitting: state.admitting,
        link: state.link_state,
        databases,
    };
    drop(state);
    (serving, out)
}

/// Answers one request.
fn answer(shared: &Shared, stream: TcpStream) -> Result<(), std::io::Error> {
    stream.set_read_timeout(Some(REQUEST_TIMEOUT))?;
    let mut reader = BufReader::new(stream.try_clone()?);
    let mut request_line = String::new();
    let _ = reader.read_line(&mut request_line)?;
    let mut parts = request_line.split_whitespace();
    let method = parts.next().unwrap_or_default();
    let path = parts.next().unwrap_or_default();

    let (serving, report) = report(shared);
    let status = match (method, path) {
        ("GET", ROLE_PATH) if serving => "200 OK",
        ("GET", ROLE_PATH) => "503 Service Unavailable",
        ("GET", HEALTH_PATH) => "200 OK",
        _ => "404 Not Found",
    };
    let body = wire::encode(&report).map_err(std::io::Error::other)?;
    let head = format!(
        "HTTP/1.1 {status}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
        body.len()
    );
    let mut writer = stream;
    writer.write_all(head.as_bytes())?;
    writer.write_all(&body)
}

/// Serves the endpoints in a thread of their own.
pub fn serve(shared: &Arc<Shared>) -> Result<(), std::io::Error> {
    let listener = TcpListener::bind(("0.0.0.0", shared.config.role_port))?;
    tracing::info!("Role endpoint listening on port {}", shared.config.role_port);

    let shared = Arc::clone(shared);
    let _ = std::thread::Builder::new().name("role-endpoint".to_owned()).spawn(move || {
        for stream in listener.incoming() {
            let Ok(stream) = stream else {
                continue;
            };

            // A client that disconnects early affects only its own request.
            if let Err(error) = answer(&shared, stream) {
                tracing::debug!("Role endpoint request failed: {error}");
            }
        }
    })?;
    Ok(())
}
