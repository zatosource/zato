//! Redis Streams integration for the standalone queue bridge binary.
//!
//! Provides command ingestion from `zato:queue_bridge:stream:command` and
//! recv event publishing to `zato:queue_bridge:stream:recv`.

use std::sync::Arc;

use serde::Deserialize;

use crate::bridge::{BridgeShared, ChannelConfig, OutgoingConfig, RecvEvent};

/// Redis stream key where the server publishes commands for the queue bridge.
pub const COMMAND_STREAM: &str = "zato:queue_bridge:stream:command";

/// Redis stream key where the queue bridge publishes received messages.
pub const RECV_STREAM: &str = "zato:queue_bridge:stream:recv";

/// Redis stream key where the queue bridge publishes synchronous replies.
pub const REPLY_STREAM: &str = "zato:queue_bridge:stream:reply";

/// Redis stream key where the queue bridge requests config from the server.
pub const REQUEST_STREAM: &str = "zato:queue_bridge:stream:request";

/// Consumer group name used by the queue bridge for the command stream.
pub const CONSUMER_GROUP_NAME: &str = "queue_bridge";

/// Consumer name within the group.
pub const CONSUMER_INSTANCE_NAME: &str = "queue_bridge-0";

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

/// Publishes a `request_config` message to the request stream, asking the server
/// to send a reload command with connection configs from ODB.
pub fn request_config(conn: &mut redis::Connection) {
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(REQUEST_STREAM)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("command")
        .arg("request_config")
        .query(conn);

    match result {
        Ok(_) => tracing::info!("Published request_config to '{REQUEST_STREAM}'"),
        Err(err) => tracing::error!("Failed to publish request_config: {err}"),
    }
}

/// Processes a reload command received during the startup wait phase.
pub fn process_startup_reload(conn: &mut redis::Connection, shared: &BridgeShared, correlation_id: &str, payload: &str) {
    tracing::info!("Startup reload received: correlation_id={correlation_id} payload={payload}");
    handle_reload(shared, payload);
    publish_reply(conn, correlation_id, "ok");
}

/// Publishes a recv event to the recv stream via XADD.
pub fn publish_recv_event(conn: &mut redis::Connection, event: &RecvEvent) {
    tracing::info!(
        "Publishing recv event: channel={} topic={} service={} payload_len={}",
        event.channel_name,
        event.topic,
        event.service,
        event.payload.len()
    );
    let payload_b64 = base64_encode(&event.payload);
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(RECV_STREAM)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("channel_name")
        .arg(&event.channel_name)
        .arg("topic")
        .arg(&event.topic)
        .arg("service")
        .arg(&event.service)
        .arg("payload")
        .arg(&payload_b64)
        .query(conn);

    if let Err(err) = result {
        tracing::error!("Failed to XADD recv event for channel '{}': {err}", event.channel_name);
    }
}

/// Publishes a synchronous reply to the reply stream.
fn publish_reply(conn: &mut redis::Connection, correlation_id: &str, status: &str) {
    publish_reply_with_data(conn, correlation_id, status, "");
}

/// Publishes a synchronous reply with an optional data field to the reply stream.
fn publish_reply_with_data(conn: &mut redis::Connection, correlation_id: &str, status: &str, data: &str) {
    tracing::info!("Publishing reply: correlation_id={correlation_id} status={status} data={data}");
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
        .arg("data")
        .arg(data)
        .query(conn);

    if let Err(err) = result {
        tracing::error!("Failed to XADD reply for correlation_id={correlation_id}: {err}");
    }
}

/// Reads and processes commands from the command stream in a blocking loop.
///
/// This function blocks on XREADGROUP and should be run on its own thread.
pub fn command_listener_loop(conn: &mut redis::Connection, shared: Arc<BridgeShared>) {
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
fn process_command(conn: &mut redis::Connection, shared: &BridgeShared, command: &str, correlation_id: &str, payload: &str) {
    tracing::info!("Command received: {command} correlation_id={correlation_id} payload={payload}");
    match command {
        "reload" => {
            handle_reload(shared, payload);
            publish_reply(conn, correlation_id, "ok");
        }
        "add_channel" => handle_add_channel(shared, payload),
        "add_outgoing" => handle_add_outgoing(shared, payload),
        "delete_channel" => handle_delete_channel(shared, payload),
        "delete_outgoing" => handle_delete_outgoing(shared, payload),
        "edit_channel" => handle_edit_channel(shared, payload),
        "edit_outgoing" => handle_edit_outgoing(shared, payload),
        "ping" => handle_ping(conn, shared, correlation_id, payload),
        "send_message" => handle_send_message(conn, shared, correlation_id, payload),
        "stop" => {
            tracing::info!("Received stop command");
            shared.stop_flag.store(true, std::sync::atomic::Ordering::Relaxed);
            publish_reply(conn, correlation_id, "ok");
        }
        _ => {
            tracing::warn!("Unknown command: {command}");
        }
    }
}

/// Payload for the reload command.
#[derive(Deserialize)]
struct ReloadPayload {
    /// Channel (consumer) connection configs from ODB.
    #[serde(default)]
    channels: Vec<ChannelConfig>,
    /// Outgoing (producer) connection configs from ODB.
    #[serde(default)]
    outgoing: Vec<OutgoingConfig>,
}

/// Payload for ping and send_message commands.
#[derive(Deserialize)]
struct ConnPayload {
    /// Outgoing connection name to target.
    conn_name: String,
    /// Optional base64-encoded payload for send_message.
    #[serde(default)]
    data: String,
}

/// Payload for delete_channel and delete_outgoing commands.
#[derive(Deserialize)]
struct DeletePayload {
    /// Connection name to remove.
    name: String,
}

fn handle_reload(shared: &BridgeShared, payload: &str) {
    tracing::info!("Reload payload: {payload}");
    let parsed: ReloadPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse reload payload: {err}, payload: {payload}");
            return;
        }
    };

    shared.cancel_all_channels();

    let mut state = shared.state.lock();
    state.channels.clear();
    state.outgoing.clear();
    for channel_config in &parsed.channels {
        state.channels.insert(channel_config.name.clone(), channel_config.clone());
    }
    for outgoing_config in &parsed.outgoing {
        state.outgoing.insert(outgoing_config.name.clone(), outgoing_config.clone());
    }
    drop(state);

    let channel_count = parsed.channels.len();
    let outgoing_count = parsed.outgoing.len();

    let ch_noun = if channel_count == 1 { "channel" } else { "channels" };
    let out_noun = if outgoing_count == 1 { "outgoing connection" } else { "outgoing connections" };
    tracing::info!("Reloaded {channel_count} {ch_noun} and {outgoing_count} {out_noun}");

    shared.config_notify.notify_one();
}

fn handle_add_channel(shared: &BridgeShared, payload: &str) {
    let config: ChannelConfig = match serde_json::from_str(payload) {
        Ok(config) => config,
        Err(err) => {
            tracing::error!("Failed to parse add_channel payload: {err}");
            return;
        }
    };
    let name = config.name.clone();
    shared.state.lock().channels.insert(name.clone(), config);
    tracing::info!("Added channel: {name}");
    shared.config_notify.notify_one();
}

fn handle_add_outgoing(shared: &BridgeShared, payload: &str) {
    let config: OutgoingConfig = match serde_json::from_str(payload) {
        Ok(config) => config,
        Err(err) => {
            tracing::error!("Failed to parse add_outgoing payload: {err}");
            return;
        }
    };
    let name = config.name.clone();
    shared.state.lock().outgoing.insert(name.clone(), config);
    tracing::info!("Added outgoing: {name}");
}

fn handle_delete_channel(shared: &BridgeShared, payload: &str) {
    let parsed: DeletePayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse delete_channel payload: {err}");
            return;
        }
    };
    shared.cancel_channel(&parsed.name);
    shared.state.lock().channels.remove(&parsed.name);
    tracing::info!("Deleted channel: {}", parsed.name);
}

fn handle_delete_outgoing(shared: &BridgeShared, payload: &str) {
    let parsed: DeletePayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse delete_outgoing payload: {err}");
            return;
        }
    };
    shared.state.lock().outgoing.remove(&parsed.name);
    tracing::info!("Deleted outgoing: {}", parsed.name);
}

fn handle_edit_channel(shared: &BridgeShared, payload: &str) {
    let config: ChannelConfig = match serde_json::from_str(payload) {
        Ok(config) => config,
        Err(err) => {
            tracing::error!("Failed to parse edit_channel payload: {err}");
            return;
        }
    };
    let name = config.name.clone();
    shared.cancel_channel(&name);
    shared.state.lock().channels.insert(name.clone(), config);
    tracing::info!("Edited channel: {name}");
    shared.config_notify.notify_one();
}

fn handle_edit_outgoing(shared: &BridgeShared, payload: &str) {
    let config: OutgoingConfig = match serde_json::from_str(payload) {
        Ok(config) => config,
        Err(err) => {
            tracing::error!("Failed to parse edit_outgoing payload: {err}");
            return;
        }
    };
    let name = config.name.clone();
    shared.state.lock().outgoing.insert(name.clone(), config);
    tracing::info!("Edited outgoing: {name}");
}

fn handle_ping(conn: &mut redis::Connection, shared: &BridgeShared, correlation_id: &str, payload: &str) {
    let parsed: ConnPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse ping payload: {err}");
            publish_reply_with_data(conn, correlation_id, "error", &format!("bad payload: {err}"));
            return;
        }
    };
    match crate::bridge::ping_sync(shared, &parsed.conn_name) {
        Ok(()) => publish_reply_with_data(conn, correlation_id, "ok", ""),
        Err(err) => publish_reply_with_data(conn, correlation_id, "error", &err),
    }
}

fn handle_send_message(conn: &mut redis::Connection, shared: &BridgeShared, correlation_id: &str, payload: &str) {
    let parsed: ConnPayload = match serde_json::from_str(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse send_message payload: {err}");
            publish_reply_with_data(conn, correlation_id, "error", &format!("bad payload: {err}"));
            return;
        }
    };
    let data = base64_decode(&parsed.data);
    match crate::bridge::publish_sync(shared, &parsed.conn_name, &data) {
        Ok(()) => publish_reply_with_data(conn, correlation_id, "ok", ""),
        Err(err) => publish_reply_with_data(conn, correlation_id, "error", &err),
    }
}

/// Simple base64 encoder for binary payloads in Redis stream fields.
fn base64_encode(data: &[u8]) -> String {
    use std::fmt::Write;
    const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut result = String::with_capacity(data.len().div_ceil(3) * 4);
    for chunk in data.chunks(3) {
        let triple = match chunk.len() {
            3 => (u32::from(chunk[0]) << 16) | (u32::from(chunk[1]) << 8) | u32::from(chunk[2]),
            2 => (u32::from(chunk[0]) << 16) | (u32::from(chunk[1]) << 8),
            1 => u32::from(chunk[0]) << 16,
            _ => continue,
        };
        result.push(char::from(ALPHABET[((triple >> 18) & 0x3F) as usize]));
        result.push(char::from(ALPHABET[((triple >> 12) & 0x3F) as usize]));
        if chunk.len() > 1 {
            result.push(char::from(ALPHABET[((triple >> 6) & 0x3F) as usize]));
        } else {
            result.push('=');
        }
        if chunk.len() > 2 {
            result.push(char::from(ALPHABET[(triple & 0x3F) as usize]));
        } else {
            result.push('=');
        }
    }
    let _ = write!(result, "");
    result
}

/// Simple base64 decoder for binary payloads from Redis stream fields.
fn base64_decode(encoded: &str) -> Vec<u8> {
    fn decode_char(chr: u8) -> Option<u8> {
        match chr {
            b'A'..=b'Z' => Some(chr - b'A'),
            b'a'..=b'z' => Some(chr - b'a' + 26),
            b'0'..=b'9' => Some(chr - b'0' + 52),
            b'+' => Some(62),
            b'/' => Some(63),
            _ => None,
        }
    }

    let bytes: Vec<u8> = encoded.bytes().filter(|&byte| byte != b'=').collect();
    let mut result = Vec::with_capacity(bytes.len() * 3 / 4);

    for chunk in bytes.chunks(4) {
        let mut buf: u32 = 0;
        let mut count: u8 = 0;
        for &byte in chunk {
            if let Some(val) = decode_char(byte) {
                buf = (buf << 6) | u32::from(val);
                count += 1;
            }
        }
        if count >= 2 {
            let shift = (4 - count) * 6;
            buf <<= shift;
            result.push((buf >> 16) as u8);
            if count >= 3 {
                result.push((buf >> 8) as u8);
            }
            if count >= 4 {
                result.push(buf as u8);
            }
        }
    }

    result
}
