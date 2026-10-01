//! Redis Streams integration for the standalone queue bridge binary.
//!
//! Provides command ingestion from `zato:queue_bridge:stream:command`, recv event publishing
//! to one `zato:queue_bridge:stream:recv:<channel_id>` stream per channel, and reply publishing
//! to `zato:queue_bridge:stream:reply`.

use std::collections::HashMap;
use std::sync::Arc;

use serde::Deserialize;

use crate::bridge::{BridgeShared, ChannelConfig, OutgoingConfig, RecvEvent, ReplyEvent, SendRequest};
use crate::wire;

/// Redis stream key where the server publishes commands for the queue bridge.
pub const COMMAND_STREAM: &str = "zato:queue_bridge:stream:command";

/// Prefix of the per-channel Redis stream keys where the queue bridge publishes received messages.
///
/// The channel ID follows the prefix, so one slow channel never holds back another.
pub const RECV_STREAM_PREFIX: &str = "zato:queue_bridge:stream:recv:";

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

/// What XREADGROUP returns - per stream, a list of entries, each a list of field-value pairs.
type StreamReadResult = Vec<(String, Vec<(String, Vec<(String, String)>)>)>;

/// Returns the recv stream key of one channel.
pub fn recv_stream_key(channel_id: u64) -> String {
    format!("{RECV_STREAM_PREFIX}{channel_id}")
}

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

/// Publishes a recv event to the recv stream of its channel via XADD.
pub fn publish_recv_event(conn: &mut redis::Connection, event: &RecvEvent) {
    tracing::info!(
        "Publishing recv event: channel={} topic={} service={} payload_len={}",
        event.channel_name,
        event.topic,
        event.service,
        event.payload.len()
    );
    let payload_b64 = wire::base64_encode(&event.payload);
    let stream_key = recv_stream_key(event.channel_id);
    let result: Result<String, redis::RedisError> = redis::cmd("XADD")
        .arg(&stream_key)
        .arg("MAXLEN")
        .arg("~")
        .arg(STREAM_MAXLEN)
        .arg("*")
        .arg("channel_id")
        .arg(event.channel_id)
        .arg("channel_name")
        .arg(&event.channel_name)
        .arg("topic")
        .arg(&event.topic)
        .arg("service")
        .arg(&event.service)
        .arg("payload")
        .arg(&payload_b64)
        .arg("headers")
        .arg(&event.headers)
        .arg("reply_to_queue")
        .arg(&event.reply_to_queue)
        .arg("reply_to_queue_manager")
        .arg(&event.reply_to_queue_manager)
        .arg("message_id")
        .arg(&event.message_id)
        .query(conn);

    if let Err(err) = result {
        tracing::error!(
            "Failed to XADD recv event for channel '{}' to '{stream_key}': {err}",
            event.channel_name
        );
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

/// Publishes a reply produced on the bridge runtime, as drained by the reply publisher thread.
pub fn publish_reply_event(conn: &mut redis::Connection, event: &ReplyEvent) {
    publish_reply_with_data(conn, &event.correlation_id, &event.status, &event.data);
}

/// Reads and processes commands from the command stream in a blocking loop.
///
/// This function blocks on XREADGROUP and should be run on its own thread.
pub fn command_listener_loop(conn: &mut redis::Connection, shared: &Arc<BridgeShared>) {
    tracing::info!("Command listener started on '{COMMAND_STREAM}'");

    loop {
        if shared.stop_flag.load(std::sync::atomic::Ordering::Relaxed) {
            tracing::info!("Command listener exiting (stop flag set)");
            break;
        }

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

                process_command(conn, shared, &command, &correlation_id, &payload);

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
fn process_command(conn: &mut redis::Connection, shared: &Arc<BridgeShared>, command: &str, correlation_id: &str, payload: &str) {
    // Commits arrive once per message and would drown the log at info level.
    if command == "commit_offset" {
        tracing::debug!("Command received: {command} payload={payload}");
    } else {
        tracing::info!("Command received: {command} correlation_id={correlation_id} payload={payload}");
    }

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
        "commit_offset" => handle_commit_offset(shared, payload),
        "ping" => handle_ping(shared, correlation_id, payload),
        "send_message" => handle_send_message(shared, correlation_id, payload),
        "send_reply" => handle_send_reply(conn, shared, correlation_id, payload),
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

/// Payload for the `ping` command.
#[derive(Deserialize)]
struct PingPayload {
    /// Outgoing connection name to target.
    conn_name: String,
}

/// Payload for the `send_message` command.
#[derive(Deserialize)]
struct SendMessagePayload {
    /// Outgoing connection name to target.
    conn_name: String,
    /// Base64-encoded payload, empty for a tombstone.
    #[serde(default)]
    data: String,
    /// Message key as text, which decides the partition when none is given (Kafka only).
    #[serde(default)]
    key: Option<String>,
    /// Message headers as text names and values (Kafka only).
    #[serde(default)]
    headers: HashMap<String, String>,
    /// Partition to publish to, letting Kafka choose when absent (Kafka only).
    #[serde(default)]
    partition: Option<i32>,
    /// Whether the message is a tombstone, i.e. a key with no value (Kafka only).
    #[serde(default)]
    is_tombstone: bool,
}

/// Payload for the `commit_offset` command.
#[derive(Deserialize)]
struct CommitOffsetPayload {
    /// ID of the channel whose message is resolved.
    channel_id: u64,
    /// Topic the message came from.
    topic: String,
    /// Partition the message came from.
    partition: i32,
    /// Offset of the resolved message.
    offset: i64,
}

/// Payload for the `delete_channel` and `delete_outgoing` commands.
#[derive(Deserialize)]
struct DeletePayload {
    /// Connection name to remove.
    name: String,
}

/// Payload for the `send_reply` command.
#[derive(Deserialize)]
struct SendReplyPayload {
    /// Channel that received the original message.
    channel_name: String,
    /// Reply-to queue from the original message descriptor.
    reply_to_queue: String,
    /// Reply-to queue manager from the original message descriptor.
    #[serde(default)]
    reply_to_queue_manager: String,
    /// Hex-encoded message ID of the original message, used as the reply's correlation ID.
    message_id: String,
    /// Base64-encoded reply payload.
    data: String,
}

/// Replaces the whole connection configuration with the one carried by the payload.
fn handle_reload(shared: &BridgeShared, payload: &str) {
    tracing::info!("Reload payload: {payload}");
    let parsed: ReloadPayload = match wire::parse_payload(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse reload payload: {err}, payload: {payload}");
            return;
        }
    };

    shared.cancel_all_channels();

    #[cfg(feature = "kafka")]
    crate::kafka::clear_producers(shared);

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

    // Producers are built outside the state lock, since building one may take a moment.
    #[cfg(feature = "kafka")]
    for outgoing_config in &parsed.outgoing {
        crate::kafka::refresh_producer(shared, outgoing_config);
    }

    let channel_count = parsed.channels.len();
    let outgoing_count = parsed.outgoing.len();

    let ch_noun = if channel_count == 1 { "channel" } else { "channels" };
    let out_noun = if outgoing_count == 1 {
        "outgoing connection"
    } else {
        "outgoing connections"
    };
    tracing::info!("Reloaded {channel_count} {ch_noun} and {outgoing_count} {out_noun}");

    shared.config_notify.notify_one();
}

/// Adds one channel (consumer) connection from the payload.
fn handle_add_channel(shared: &BridgeShared, payload: &str) {
    let config: ChannelConfig = match wire::parse_payload(payload) {
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

/// Adds one outgoing (producer) connection from the payload.
fn handle_add_outgoing(shared: &BridgeShared, payload: &str) {
    let config: OutgoingConfig = match wire::parse_payload(payload) {
        Ok(config) => config,
        Err(err) => {
            tracing::error!("Failed to parse add_outgoing payload: {err}");
            return;
        }
    };
    let name = config.name.clone();

    #[cfg(feature = "kafka")]
    crate::kafka::refresh_producer(shared, &config);

    shared.state.lock().outgoing.insert(name.clone(), config);
    tracing::info!("Added outgoing: {name}");
}

/// Cancels and removes the channel named in the payload.
fn handle_delete_channel(shared: &BridgeShared, payload: &str) {
    let parsed: DeletePayload = match wire::parse_payload(payload) {
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

/// Removes the outgoing connection named in the payload.
fn handle_delete_outgoing(shared: &BridgeShared, payload: &str) {
    let parsed: DeletePayload = match wire::parse_payload(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse delete_outgoing payload: {err}");
            return;
        }
    };

    #[cfg(feature = "kafka")]
    crate::kafka::drop_producer(shared, &parsed.name);

    shared.state.lock().outgoing.remove(&parsed.name);
    tracing::info!("Deleted outgoing: {}", parsed.name);
}

/// Replaces one channel's configuration, cancelling its current consumer first.
fn handle_edit_channel(shared: &BridgeShared, payload: &str) {
    let config: ChannelConfig = match wire::parse_payload(payload) {
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

/// Replaces one outgoing connection's configuration and rebuilds its producer.
fn handle_edit_outgoing(shared: &BridgeShared, payload: &str) {
    let config: OutgoingConfig = match wire::parse_payload(payload) {
        Ok(config) => config,
        Err(err) => {
            tracing::error!("Failed to parse edit_outgoing payload: {err}");
            return;
        }
    };
    let name = config.name.clone();

    #[cfg(feature = "kafka")]
    crate::kafka::refresh_producer(shared, &config);

    shared.state.lock().outgoing.insert(name.clone(), config);
    tracing::info!("Edited outgoing: {name}");
}

/// Routes a resolved message's offset to the consume loop of its channel.
fn handle_commit_offset(shared: &BridgeShared, payload: &str) {
    let parsed: CommitOffsetPayload = match wire::parse_payload(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse commit_offset payload: {err}");
            return;
        }
    };

    let request = crate::bridge::CommitRequest {
        topic: parsed.topic,
        partition: parsed.partition,
        offset: parsed.offset,
    };

    shared.commit_offset(parsed.channel_id, request);
}

/// Pings the outgoing connection named in the payload on the bridge runtime and replies with the outcome.
fn handle_ping(shared: &Arc<BridgeShared>, correlation_id: &str, payload: &str) {
    let parsed: PingPayload = match wire::parse_payload(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse ping payload: {err}");
            shared.publish_reply(correlation_id, Err(format!("bad payload: {err}")));
            return;
        }
    };

    let shared_for_task = Arc::clone(shared);
    let correlation_id = correlation_id.to_string();

    // The ping may wait for a broker that is down, which must not stall the command thread.
    shared.runtime_handle.spawn(async move {
        let result = crate::bridge::ping(&shared_for_task, &parsed.conn_name).await;
        shared_for_task.publish_reply(&correlation_id, result.map(|()| String::new()));
    });
}

/// Sends one message through the outgoing connection named in the payload on the bridge runtime.
fn handle_send_message(shared: &Arc<BridgeShared>, correlation_id: &str, payload: &str) {
    let parsed: SendMessagePayload = match wire::parse_payload(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse send_message payload: {err}");
            shared.publish_reply(correlation_id, Err(format!("bad payload: {err}")));
            return;
        }
    };

    let mut headers = Vec::with_capacity(parsed.headers.len());
    for (name, value) in parsed.headers {
        headers.push((name, value.into_bytes()));
    }

    let request = SendRequest {
        payload: wire::base64_decode(&parsed.data),
        key: parsed.key.map(String::into_bytes),
        headers,
        partition: parsed.partition,
        is_tombstone: parsed.is_tombstone,
    };

    let shared_for_task = Arc::clone(shared);
    let correlation_id = correlation_id.to_string();

    // The send waits for the delivery report, which must not stall the command thread.
    shared.runtime_handle.spawn(async move {
        let result = crate::bridge::publish_message(&shared_for_task, &parsed.conn_name, request).await;
        shared_for_task.publish_reply(&correlation_id, result.map(|outcome| outcome.to_reply_data()));
    });
}

/// Sends a reply to the queue the original message nominated.
fn handle_send_reply(conn: &mut redis::Connection, shared: &BridgeShared, correlation_id: &str, payload: &str) {
    let parsed: SendReplyPayload = match wire::parse_payload(payload) {
        Ok(parsed) => parsed,
        Err(err) => {
            tracing::error!("Failed to parse send_reply payload: {err}");
            publish_reply_with_data(conn, correlation_id, "error", &format!("bad payload: {err}"));
            return;
        }
    };
    let data = wire::base64_decode(&parsed.data);

    let target = crate::bridge::ReplyTarget {
        channel_name: &parsed.channel_name,
        reply_to_queue: &parsed.reply_to_queue,
        reply_to_queue_manager: &parsed.reply_to_queue_manager,
        message_id: &parsed.message_id,
    };

    let result = crate::bridge::send_reply_sync(shared, &target, &data);
    match result {
        Ok(()) => publish_reply_with_data(conn, correlation_id, "ok", ""),
        Err(err) => publish_reply_with_data(conn, correlation_id, "error", &err),
    }
}
