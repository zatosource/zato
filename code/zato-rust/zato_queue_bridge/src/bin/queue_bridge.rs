// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Standalone Zato queue bridge binary.
//!
//! Communicates with the Zato server via Redis Streams for commands and
//! recv events, and serves an HTTP query API on 127.0.0.1:35111 for the
//! server to read connection state.

use std::sync::Arc;

use tracing_subscriber::EnvFilter;

use zato_queue_bridge::bridge;
use zato_queue_bridge::http_api;
use zato_queue_bridge::redis_streams;

/// Configuration read from `Zato_Queue_Bridge_*` environment variables.
struct QueueBridgeConfig {
    /// Redis server hostname.
    redis_host: String,
    /// Redis server port.
    redis_port: u16,
    /// Redis password (empty string if not set).
    redis_password: String,
    /// Tracing log level filter.
    log_level: String,
}

impl QueueBridgeConfig {
    /// Reads configuration from environment variables.
    fn from_env() -> Self {
        Self {
            redis_host: std::env::var("Zato_Queue_Bridge_Redis_Host").unwrap_or_else(|_| "localhost".to_string()),
            redis_port: std::env::var("Zato_Queue_Bridge_Redis_Port")
                .ok()
                .and_then(|val| val.parse::<u16>().ok())
                .unwrap_or(6379),
            redis_password: std::env::var("Zato_Queue_Bridge_Redis_Password").unwrap_or_default(),
            log_level: std::env::var("Zato_Queue_Bridge_Log_Level").unwrap_or_else(|_| "info".to_string()),
        }
    }

    /// Builds a Redis connection URL from the config.
    fn redis_url(&self) -> String {
        if self.redis_password.is_empty() {
            format!("redis://{}:{}", self.redis_host, self.redis_port)
        } else {
            format!("redis://:{}@{}:{}", self.redis_password, self.redis_host, self.redis_port)
        }
    }
}

/// Waits for the server to send a `reload` command with initial connection configs.
///
/// Retries indefinitely, requesting config every 10 seconds until the server responds.
fn wait_for_initial_reload(conn: &mut redis::Connection, shared: &bridge::BridgeShared) {
    let mut attempt: u64 = 0;
    loop {
        attempt += 1;
        tracing::info!("Requesting config from server (attempt {attempt})");
        redis_streams::request_config(conn);

        type StreamReadResult = Vec<(String, Vec<(String, Vec<(String, String)>)>)>;

        let result: Result<StreamReadResult, redis::RedisError> = redis::cmd("XREADGROUP")
            .arg("GROUP")
            .arg(redis_streams::CONSUMER_GROUP_NAME)
            .arg(redis_streams::CONSUMER_INSTANCE_NAME)
            .arg("BLOCK")
            .arg(10_000_u64)
            .arg("COUNT")
            .arg(10_u64)
            .arg("STREAMS")
            .arg(redis_streams::COMMAND_STREAM)
            .arg(">")
            .query(conn);

        let streams = match result {
            Ok(streams) => streams,
            Err(err) => {
                tracing::warn!("XREADGROUP error on attempt {attempt}: {err}");
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

                tracing::info!("Startup command received: {command} correlation_id={correlation_id}");

                if command == "reload" {
                    redis_streams::process_startup_reload(conn, shared, &correlation_id, &payload);

                    let ack_result: Result<u32, redis::RedisError> = redis::cmd("XACK")
                        .arg(redis_streams::COMMAND_STREAM)
                        .arg(redis_streams::CONSUMER_GROUP_NAME)
                        .arg(msg_id.as_str())
                        .query(conn);
                    if let Err(err) = ack_result {
                        tracing::error!("Failed to XACK startup reload {msg_id}: {err}");
                    }

                    return;
                }

                let ack_result: Result<u32, redis::RedisError> = redis::cmd("XACK")
                    .arg(redis_streams::COMMAND_STREAM)
                    .arg(redis_streams::CONSUMER_GROUP_NAME)
                    .arg(msg_id.as_str())
                    .query(conn);
                if let Err(err) = ack_result {
                    tracing::error!("Failed to XACK startup message {msg_id}: {err}");
                }
            }
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let config = QueueBridgeConfig::from_env();

    tracing_subscriber::fmt().with_env_filter(EnvFilter::new(&config.log_level)).init();

    tracing::info!("Zato queue bridge starting");
    tracing::info!("Redis: {}:{}", config.redis_host, config.redis_port);

    let redis_client = redis::Client::open(config.redis_url()).map_err(|err| {
        std::io::Error::new(
            std::io::ErrorKind::ConnectionRefused,
            format!("Failed to create Redis client: {err}"),
        )
    })?;

    let mut command_conn = redis_client.get_connection().map_err(|err| {
        std::io::Error::new(
            std::io::ErrorKind::ConnectionRefused,
            format!("Failed to connect to Redis (command): {err}"),
        )
    })?;

    let mut recv_conn = redis_client.get_connection().map_err(|err| {
        std::io::Error::new(
            std::io::ErrorKind::ConnectionRefused,
            format!("Failed to connect to Redis (recv): {err}"),
        )
    })?;

    redis_streams::ensure_consumer_group(&mut command_conn);

    let shared = Arc::new(bridge::BridgeShared::new());

    tracing::info!("Waiting for initial config reload from server");
    wait_for_initial_reload(&mut command_conn, &shared);

    let (recv_sender, recv_receiver) = std::sync::mpsc::channel();

    let shared_for_loop = Arc::clone(&shared);
    let bridge_thread = std::thread::Builder::new()
        .name("zato-bridge-loop".into())
        .spawn(move || {
            bridge::bridge_loop(shared_for_loop, recv_sender);
        })
        .map_err(|err| std::io::Error::other(format!("Failed to spawn bridge loop thread: {err}")))?;

    let shared_for_commands = Arc::clone(&shared);
    let command_thread = std::thread::Builder::new()
        .name("zato-cmd-listener".into())
        .spawn(move || {
            redis_streams::command_listener_loop(&mut command_conn, shared_for_commands);
        })
        .map_err(|err| std::io::Error::other(format!("Failed to spawn command listener: {err}")))?;

    let recv_pub_thread = std::thread::Builder::new()
        .name("zato-recv-pub".into())
        .spawn(move || {
            for event in recv_receiver {
                redis_streams::publish_recv_event(&mut recv_conn, &event);
            }
            tracing::info!("Recv publisher thread exiting");
        })
        .map_err(|err| std::io::Error::other(format!("Failed to spawn recv publisher: {err}")))?;

    let shared_for_http = Arc::clone(&shared);
    let http_result = http_api::start_http_server(shared_for_http).await;

    shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);

    bridge_thread.join().ok();
    command_thread.join().ok();
    recv_pub_thread.join().ok();

    tracing::info!("Zato queue bridge stopped");

    http_result
}
