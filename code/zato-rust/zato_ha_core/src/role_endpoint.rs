// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The HTTP endpoints that a load balancer and Kubernetes probe.
//!
//! `GET /zato/ha/role` answers 200 only on an active node that is not isolated and whose Zato server has answered
//! its ping endpoint since it was started, so a load balancer sends no client to a server that cannot answer yet.
//! `GET /zato/ha/health` answers 200 in every role, which is what a liveness probe needs.
//! `GET /zato/ha/ready` answers 200 only while the node is not stopping and is either the standby, which can take
//! over, or active with a server that answers, so the `StatefulSet` controller replaces the next pod only once
//! the replaced one has read the referee record. A node in `Down` or `Fenced` answers 503.

use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::time::Duration;

use serde::Serialize;

use crate::state::{Role, Shared};
use crate::wire;

/// The path of the role endpoint.
pub const ROLE_PATH: &str = "/zato/ha/role";

/// The path of the health endpoint.
pub const HEALTH_PATH: &str = "/zato/ha/health";

/// The path of the readiness endpoint.
pub const READY_PATH: &str = "/zato/ha/ready";

/// How long a client may take to send its request.
const REQUEST_TIMEOUT: Duration = Duration::from_secs(2);

/// The body of the endpoints.
#[derive(Serialize)]
struct RoleReport {
    /// The name of the node.
    node: String,

    /// The role of the node.
    role: Role,

    /// The generation of the node.
    generation: u64,

    /// Whether the node lost the referee or the database.
    isolated: bool,

    /// Whether the Zato server of the node has answered its ping endpoint since it was started.
    server_ready: bool,
}

/// Builds the report and tells whether the node serves traffic and whether it is ready for a probe.
fn report(shared: &Shared) -> (bool, bool, RoleReport) {
    let state = shared.state.lock();
    let answers = state.answers();
    let is_ready = !state.stopping
        && match state.role {
            Role::Standby => true,
            Role::Active => answers,
            Role::Down | Role::Fenced => false,
        };
    let out = RoleReport {
        node: shared.config.node_name.clone(),
        role: state.role,
        generation: state.generation,
        isolated: state.isolated,
        server_ready: state.server_ready,
    };
    drop(state);
    (answers, is_ready, out)
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

    let (answers, is_ready, report) = report(shared);
    let status = match (method, path) {
        ("GET", ROLE_PATH) if answers => "200 OK",
        ("GET", HEALTH_PATH) => "200 OK",
        ("GET", READY_PATH) if is_ready => "200 OK",
        ("GET", ROLE_PATH | READY_PATH) => "503 Service Unavailable",
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

#[cfg(test)]
mod tests;
