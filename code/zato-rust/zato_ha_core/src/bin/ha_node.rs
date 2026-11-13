// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The active-standby node of a Zato server on `SQLite` or on `PostgreSQL`.
//!
//! Usage: `_zato_ha_node -- <command that starts the Zato server>`. The node runs the command only while
//! it is active, and reads its configuration from the `Zato_HA_*` environment variables.

use std::process::ExitCode;
use std::sync::Arc;
use std::sync::atomic::AtomicBool;

use tracing_subscriber::EnvFilter;

use zato_ha_core::active::Shipper;
use zato_ha_core::config::{NodeConfig, ProcessEnvironment, RefereeConfig, StorageMode};
use zato_ha_core::control::Control;
use zato_ha_core::kubernetes::client::ApiClient;
use zato_ha_core::kubernetes::label;
use zato_ha_core::kubernetes::lease::LeaseReferee;
use zato_ha_core::link::TlsContext;
use zato_ha_core::postgresql::{DatabaseProbe, PostgreSqlProbe};
use zato_ha_core::referee::Referee;
use zato_ha_core::state::Shared;
use zato_ha_core::supervisor::Supervisor;
use zato_ha_core::{barrier, role_endpoint, standby};

/// The argument that separates the node's own arguments from the server command.
const COMMAND_SEPARATOR: &str = "--";

/// Builds the referee selected by the configuration.
fn build_referee(config: &NodeConfig, client: &ApiClient) -> Box<dyn Referee> {
    match &config.referee {
        RefereeConfig::Kubernetes(kubernetes) => Box::new(LeaseReferee::new(client.clone(), &kubernetes.lease_name)),
    }
}

/// Builds the probe of the database of the shared storage mode, which the replicated storage mode does not have.
fn build_probe(config: &NodeConfig) -> Result<Option<Box<dyn DatabaseProbe>>, String> {
    let Some(database) = &config.shared_database else {
        return Ok(None);
    };
    let probe = PostgreSqlProbe::new(database).map_err(|error| error.to_string())?;
    Ok(Some(Box::new(probe)))
}

/// Starts every thread and runs the control loop until the node stops.
fn run(config: NodeConfig, command: Vec<String>) -> Result<(), String> {
    // The label thread patches the pods of the pair, so the node runs only where the API server is reachable.
    let client = ApiClient::from_service_account().map_err(|error| format!("Kubernetes: {error}"))?;
    let referee = build_referee(&config, &client);
    let probe = build_probe(&config)?;
    let tls = match &config.tls {
        Some(files) => Some(TlsContext::load(files).map_err(|error| error.to_string())?),
        None => None,
    };
    let storage = config.storage;
    std::fs::create_dir_all(&config.data_dir).map_err(|error| format!("{}: {error}", config.data_dir.display()))?;
    let shared = Arc::new(Shared::new(config, referee, tls));

    let stop_requested = Arc::new(AtomicBool::new(false));
    for signal in [signal_hook::consts::SIGTERM, signal_hook::consts::SIGINT] {
        let _ = signal_hook::flag::register(signal, Arc::clone(&stop_requested)).map_err(|error| error.to_string())?;
    }

    // The control loop loads the persisted generation, which the replication link compares with every Hello.
    let control = Control::new(Arc::clone(&shared), probe, stop_requested).map_err(|error| error.to_string())?;

    // In the shared storage mode, both hosts use one database, so nothing is shipped and no commit waits for a barrier.
    if storage == StorageMode::Replicated {
        barrier::serve(&shared).map_err(|error| format!("barrier socket: {error}"))?;
        standby::serve(&shared).map_err(|error| format!("replication link: {error}"))?;
    }
    role_endpoint::serve(&shared).map_err(|error| format!("role endpoint: {error}"))?;
    label::start(&shared, client).map_err(|error| format!("Kubernetes: {error}"))?;

    let shipper_thread = match storage {
        StorageMode::Replicated => {
            let shipper = Shipper::new(Arc::clone(&shared));
            let thread = std::thread::Builder::new()
                .name("shipper".to_owned())
                .spawn(move || shipper.run())
                .map_err(|error| error.to_string())?;
            Some(thread)
        }
        StorageMode::Shared => None,
    };

    let supervisor = Supervisor::new(Arc::clone(&shared), command);
    let supervisor_thread = std::thread::Builder::new()
        .name("supervisor".to_owned())
        .spawn(move || supervisor.run())
        .map_err(|error| error.to_string())?;

    let outcome = control.run().map_err(|error| error.to_string());

    // The server is stopped before the node exits, whatever ended the control loop.
    let _ = supervisor_thread.join();
    if let Some(thread) = shipper_thread {
        let _ = thread.join();
    }
    outcome
}

fn main() -> ExitCode {
    let mut arguments: Vec<String> = std::env::args().skip(1).collect();
    if arguments.first().map(String::as_str) == Some(COMMAND_SEPARATOR) {
        let _ = arguments.remove(0);
    }

    let config = match NodeConfig::from_source(&ProcessEnvironment) {
        Ok(config) => config,
        Err(error) => {
            tracing_subscriber::fmt().init();
            tracing::error!("{error}");
            return ExitCode::FAILURE;
        }
    };

    let filter = EnvFilter::try_new(&config.log_level).unwrap_or_else(|_| EnvFilter::new("info"));
    tracing_subscriber::fmt().with_env_filter(filter).with_thread_names(true).init();
    tracing::info!("Node {} starting", config.node_name);

    match run(config, arguments) {
        Ok(()) => {
            tracing::info!("Node stopped");
            ExitCode::SUCCESS
        }
        Err(error) => {
            tracing::error!("Node stopped: {error}");
            ExitCode::FAILURE
        }
    }
}
