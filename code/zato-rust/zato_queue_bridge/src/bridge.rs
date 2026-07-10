//! Bridge state management and Tokio-based bridge loop for the standalone queue bridge binary.
//!
//! Manages channel (consumer) and outgoing (producer) connections to external message
//! queues. The bridge loop runs inside a Tokio multi-threaded runtime on its own OS thread,
//! forwarding consumed messages through an `mpsc` channel to be published to Redis.

use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use parking_lot::Mutex;
use serde::{Deserialize, Deserializer, Serialize};
use tokio_util::sync::CancellationToken;

/// Connection type marker for Kafka channels.
pub const TYPE_CHANNEL_KAFKA: &str = "channel-kafka";

/// Connection type marker for Kafka outgoing connections.
pub const TYPE_OUTCONN_KAFKA: &str = "outconn-kafka";

/// Connection type marker for IBM MQ channels.
pub const TYPE_CHANNEL_IBM_MQ: &str = "channel-ibm-mq";

/// Connection type marker for IBM MQ outgoing connections.
pub const TYPE_OUTCONN_IBM_MQ: &str = "outconn-ibm-mq";

/// A boolean flag as serialized by the various config sources.
///
/// The ODB stores flags like `ssl` as `null` for connections that have never
/// touched the toggle, while dashboard broker messages carry an empty string
/// for an unchecked toggle and a real boolean for a checked one.
#[derive(Deserialize)]
#[serde(untagged)]
enum FlagValue {
    /// A real boolean, as stored by enmasse and checked dashboard toggles.
    Bool(bool),
    /// An empty string from an unchecked dashboard toggle, or a "true"/"false" text.
    Text(String),
}

/// Deserializes a JSON value that may be `null`, a boolean or a string into a `bool`,
/// treating `null` and the empty string as `false`.
fn deserialize_nullable_bool<'de, D: Deserializer<'de>>(deserializer: D) -> Result<bool, D::Error> {
    let parsed = Option::<FlagValue>::deserialize(deserializer)?;

    let out = match parsed {
        Some(FlagValue::Bool(value)) => value,
        Some(FlagValue::Text(text)) => text == "true",
        None => false,
    };

    Ok(out)
}

/// Deserializes a JSON value that may be `null` or a string into a `String`,
/// treating `null` as an empty string. Needed because ODB columns like `username`
/// are `NULL` for connections that do not use them.
fn deserialize_nullable_string<'de, D: Deserializer<'de>>(deserializer: D) -> Result<String, D::Error> {
    Option::<String>::deserialize(deserializer).map(|opt| opt.unwrap_or_default())
}

/// Default connection type for configs that predate the `type_` field.
fn default_channel_type() -> String {
    TYPE_CHANNEL_KAFKA.to_string()
}

/// Default connection type for outgoing configs that predate the `type_` field.
fn default_outgoing_type() -> String {
    TYPE_OUTCONN_KAFKA.to_string()
}

/// Configuration for a channel (consumer) connection to an external queue.
///
/// Field names match the ODB `GenericConnection` model so the server can
/// forward the dict from the database without renaming anything. Kafka channels
/// use `topic` and `group_id`, IBM MQ channels use `queue_manager`, `mq_channel_name`
/// and `queue` - the remaining fields are shared.
#[derive(Clone, Deserialize, Serialize)]
pub struct ChannelConfig {
    /// Connection name as registered in Zato.
    pub name: String,
    /// Connection type, e.g. `channel-kafka` or `channel-ibm-mq`.
    #[serde(default = "default_channel_type")]
    pub type_: String,
    /// Broker address (e.g. "host:9092" for Kafka, "host:1414" for IBM MQ).
    pub address: String,
    /// Topic to consume from (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub topic: String,
    /// Consumer group identifier (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub group_id: String,
    /// Zato service name to invoke for each received message.
    pub service: String,
    /// Queue manager name (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub queue_manager: String,
    /// Server-connection channel name, e.g. `DEV.APP.SVRCONN` (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub mq_channel_name: String,
    /// Queue to consume from (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub queue: String,
    /// Username for authenticated connections (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub username: String,
    /// Password matching the username (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub password: String,
    /// Whether to strip the MQRFH2 header from message payloads (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_bool")]
    pub remove_jms_headers: bool,
    /// TLS cipher specification, e.g. `ANY_TLS12_OR_HIGHER` (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub cipher_spec: String,
    /// Whether SSL/TLS is enabled for this connection.
    #[serde(default, deserialize_with = "deserialize_nullable_bool")]
    pub ssl: bool,
    /// Path to the CA certificate file for SSL verification.
    pub ssl_ca_file: Option<String>,
    /// Path to the client certificate file for mutual TLS.
    pub ssl_cert_file: Option<String>,
    /// Path to the client private key file for mutual TLS.
    pub ssl_key_file: Option<String>,
}

/// Configuration for an outgoing (producer) connection to an external queue.
#[derive(Clone, Deserialize, Serialize)]
pub struct OutgoingConfig {
    /// Connection name as registered in Zato.
    pub name: String,
    /// Connection type, e.g. `outconn-kafka` or `outconn-ibm-mq`.
    #[serde(default = "default_outgoing_type")]
    pub type_: String,
    /// Broker address (e.g. "host:9092" for Kafka, "host:1414" for IBM MQ).
    pub address: String,
    /// Topic to publish to (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub topic: String,
    /// Queue manager name (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub queue_manager: String,
    /// Server-connection channel name, e.g. `DEV.APP.SVRCONN` (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub mq_channel_name: String,
    /// Queue to publish to (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub queue: String,
    /// Username for authenticated connections (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub username: String,
    /// Password matching the username (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub password: String,
    /// TLS cipher specification, e.g. `ANY_TLS12_OR_HIGHER` (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub cipher_spec: String,
    /// Whether SSL/TLS is enabled for this connection.
    #[serde(default, deserialize_with = "deserialize_nullable_bool")]
    pub ssl: bool,
    /// Path to the CA certificate file for SSL verification.
    pub ssl_ca_file: Option<String>,
    /// Path to the client certificate file for mutual TLS.
    pub ssl_cert_file: Option<String>,
    /// Path to the client private key file for mutual TLS.
    pub ssl_key_file: Option<String>,
}

/// A message consumed from an external queue, ready to be published to Redis.
pub struct RecvEvent {
    /// Channel connection name that produced this message.
    pub channel_name: String,
    /// Topic (Kafka) or queue (IBM MQ) the message was received from.
    pub topic: String,
    /// Zato service name to invoke.
    pub service: String,
    /// Raw message payload bytes.
    pub payload: Vec<u8>,
    /// JSON object string with message headers (MQMD fields and MQRFH2 folders for IBM MQ).
    pub headers: String,
    /// Reply-to queue from the incoming message, empty when there is none.
    pub reply_to_queue: String,
    /// Reply-to queue manager from the incoming message, empty when there is none.
    pub reply_to_queue_manager: String,
    /// Hex-encoded message ID of the incoming message, empty for Kafka.
    pub message_id: String,
}

impl RecvEvent {
    /// Creates a recv event with no headers and no reply metadata, as used by Kafka.
    pub fn without_headers(channel_name: String, topic: String, service: String, payload: Vec<u8>) -> Self {
        Self {
            channel_name,
            topic,
            service,
            payload,
            headers: "{}".to_string(),
            reply_to_queue: String::new(),
            reply_to_queue_manager: String::new(),
            message_id: String::new(),
        }
    }
}

/// Holds all registered channel and outgoing connection configurations.
#[derive(Default)]
pub struct BridgeState {
    /// Consumer connections keyed by connection name.
    pub channels: HashMap<String, ChannelConfig>,
    /// Producer connections keyed by connection name.
    pub outgoing: HashMap<String, OutgoingConfig>,
}

impl BridgeState {
    /// Creates an empty bridge state with no registered connections.
    pub fn new() -> Self {
        Self::default()
    }
}

/// Shared state accessible from multiple threads in the standalone binary.
pub struct BridgeShared {
    /// Mutex-protected bridge connection state.
    pub state: Mutex<BridgeState>,
    /// Flag to signal all threads to stop.
    pub stop_flag: AtomicBool,
    /// Per-channel cancellation tokens so individual consumer tasks can be stopped.
    pub channel_tokens: Mutex<HashMap<String, CancellationToken>>,
    /// Sender to notify the bridge loop that channels changed and need re-syncing.
    pub config_notify: tokio::sync::Notify,
}

impl Default for BridgeShared {
    fn default() -> Self {
        Self::new()
    }
}

impl BridgeShared {
    /// Creates a new shared state with an empty bridge and stop flag unset.
    pub fn new() -> Self {
        Self {
            state: Mutex::new(BridgeState::new()),
            stop_flag: AtomicBool::new(false),
            channel_tokens: Mutex::new(HashMap::new()),
            config_notify: tokio::sync::Notify::new(),
        }
    }

    /// Cancels and removes the token for the given channel name.
    pub fn cancel_channel(&self, name: &str) {
        if let Some(token) = self.channel_tokens.lock().remove(name) {
            tracing::info!("Cancelling consumer task for channel `{name}`");
            token.cancel();
        }
    }

    /// Cancels all running channel consumer tasks.
    pub fn cancel_all_channels(&self) {
        let mut tokens = self.channel_tokens.lock();
        for (name, token) in tokens.drain() {
            tracing::info!("Cancelling consumer task for channel `{name}`");
            token.cancel();
        }
    }
}

/// Runs the bridge loop, consuming messages from all registered channels
/// and forwarding them through the provided sender to the recv event publisher thread.
///
/// This function creates a Tokio multi-threaded runtime internally and blocks
/// until the stop flag is set. It should be called from a dedicated OS thread.
pub fn bridge_loop(shared: Arc<BridgeShared>, recv_sender: std::sync::mpsc::Sender<RecvEvent>) {
    let runtime = tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .thread_name("zato-queue-bridge-rt")
        .build();

    let runtime = match runtime {
        Ok(runtime) => runtime,
        Err(err) => {
            tracing::error!("Failed to create tokio runtime for queue bridge: {err}");
            return;
        }
    };

    runtime.block_on(async {
        let (consume_sender, mut consume_receiver) = tokio::sync::mpsc::unbounded_channel::<RecvEvent>();

        spawn_consumers_for_current_config(&shared, &consume_sender);

        loop {
            if shared.stop_flag.load(Ordering::Relaxed) {
                break;
            }

            tokio::select! {
                msg = consume_receiver.recv() => {
                    match msg {
                        Some(event) => {
                            if recv_sender.send(event).is_err() {
                                break;
                            }
                        }
                        None => break,
                    }
                }
                () = shared.config_notify.notified() => {
                    spawn_consumers_for_current_config(&shared, &consume_sender);
                }
                _ = tokio::time::sleep(std::time::Duration::from_secs(1)) => {}
            }
        }
    });

    tracing::info!("Bridge loop exiting");
}

/// Spawns a consumer task for every channel in the current config that does
/// not already have a running task (i.e. no token in channel_tokens).
fn spawn_consumers_for_current_config(shared: &Arc<BridgeShared>, consume_sender: &tokio::sync::mpsc::UnboundedSender<RecvEvent>) {
    let channel_configs: Vec<ChannelConfig> = {
        let bridge_state = shared.state.lock();
        bridge_state.channels.values().cloned().collect()
    };

    let mut tokens = shared.channel_tokens.lock();

    for config in &channel_configs {
        if tokens.contains_key(&config.name) {
            continue;
        }
        let token = CancellationToken::new();
        tokens.insert(config.name.clone(), token.clone());

        let sender = consume_sender.clone();
        let config = config.clone();
        let shared_clone = Arc::clone(shared);

        tracing::info!("Spawned consumer task for channel `{}` (type {})", config.name, config.type_);

        match config.type_.as_str() {
            #[cfg(feature = "kafka")]
            TYPE_CHANNEL_KAFKA => {
                tokio::spawn(async move {
                    crate::kafka::consume_loop(&config, sender, shared_clone, token).await;
                });
            }
            #[cfg(feature = "ibm-mq")]
            TYPE_CHANNEL_IBM_MQ => {
                tokio::spawn(async move {
                    crate::ibm_mq::consume_loop(config, sender, shared_clone, token).await;
                });
            }
            other => {
                tracing::warn!("No queue backend compiled for channel type `{other}`");
            }
        }
    }
}

/// Publishes a message to a named outgoing connection synchronously.
///
/// Returns `Ok(())` on success or an error message string on failure.
pub fn publish_sync(shared: &BridgeShared, conn_name: &str, payload: &[u8]) -> Result<(), String> {
    let outgoing_config = {
        let bridge_state = shared.state.lock();
        bridge_state.outgoing.get(conn_name).cloned()
    };

    let config = outgoing_config.ok_or_else(|| format!("Unknown outgoing connection: {conn_name}"))?;

    match config.type_.as_str() {
        #[cfg(feature = "kafka")]
        TYPE_OUTCONN_KAFKA => {
            let runtime = tokio::runtime::Builder::new_current_thread()
                .enable_all()
                .build()
                .map_err(|err| format!("Failed to create tokio runtime: {err}"))?;

            runtime.block_on(crate::kafka::publish_message(&config, payload))
        }
        #[cfg(feature = "ibm-mq")]
        TYPE_OUTCONN_IBM_MQ => crate::ibm_mq::publish_message(&config, payload),
        other => Err(format!("No queue backend compiled for connection `{conn_name}` of type `{other}`")),
    }
}

/// Pings a named outgoing connection.
///
/// Returns `Ok(())` on success or an error message string on failure.
pub fn ping_sync(shared: &BridgeShared, conn_name: &str) -> Result<(), String> {
    let outgoing_config = {
        let bridge_state = shared.state.lock();
        bridge_state.outgoing.get(conn_name).cloned()
    };

    let config = outgoing_config.ok_or_else(|| format!("Unknown outgoing connection: {conn_name}"))?;

    match config.type_.as_str() {
        #[cfg(feature = "kafka")]
        TYPE_OUTCONN_KAFKA => {
            let runtime = tokio::runtime::Builder::new_current_thread()
                .enable_all()
                .build()
                .map_err(|err| format!("Failed to create tokio runtime: {err}"))?;

            runtime.block_on(crate::kafka::ping_broker(&config))
        }
        #[cfg(feature = "ibm-mq")]
        TYPE_OUTCONN_IBM_MQ => crate::ibm_mq::ping(&config),
        other => Err(format!("No queue backend compiled for connection `{conn_name}` of type `{other}`")),
    }
}

/// Sends a reply through the channel that received the original message.
///
/// Used by IBM MQ channels to deliver `self.response.payload` to the ReplyToQ
/// and ReplyToQMgr carried in the incoming message descriptor.
pub fn send_reply_sync(
    shared: &BridgeShared,
    channel_name: &str,
    reply_to_queue: &str,
    reply_to_queue_manager: &str,
    message_id: &str,
    payload: &[u8],
) -> Result<(), String> {
    let channel_config = {
        let bridge_state = shared.state.lock();
        bridge_state.channels.get(channel_name).cloned()
    };

    let config = channel_config.ok_or_else(|| format!("Unknown channel: {channel_name}"))?;

    match config.type_.as_str() {
        #[cfg(feature = "ibm-mq")]
        TYPE_CHANNEL_IBM_MQ => crate::ibm_mq::send_reply(&config, reply_to_queue, reply_to_queue_manager, message_id, payload),
        other => Err(format!("Channel `{channel_name}` of type `{other}` does not support replies")),
    }
}
