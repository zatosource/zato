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

/// Deserializes a JSON value that may be `null` or `true`/`false` into a `bool`,
/// treating `null` as `false`. Needed because the ODB stores `ssl` as `None`
/// for connections that have never touched the SSL toggle.
fn deserialize_nullable_bool<'de, D: Deserializer<'de>>(deserializer: D) -> Result<bool, D::Error> {
    Option::<bool>::deserialize(deserializer).map(|opt| opt.unwrap_or(false))
}

/// Configuration for a channel (consumer) connection to an external queue.
///
/// Field names match the ODB `GenericConnection` model so the server can
/// forward the dict from the database without renaming anything.
#[derive(Clone, Deserialize, Serialize)]
pub struct ChannelConfig {
    /// Connection name as registered in Zato.
    pub name: String,
    /// Broker address (e.g. "host:9092" for Kafka).
    pub address: String,
    /// Topic to consume from.
    pub topic: String,
    /// Consumer group identifier.
    pub group_id: String,
    /// Zato service name to invoke for each received message.
    pub service: String,
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
    /// Broker address (e.g. "host:9092" for Kafka).
    pub address: String,
    /// Topic to publish to.
    pub topic: String,
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
    /// Topic the message was received from.
    pub topic: String,
    /// Zato service name to invoke.
    pub service: String,
    /// Raw message payload bytes.
    pub payload: Vec<u8>,
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

/// Runs the bridge loop, consuming messages from all registered Kafka channels
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
        #[cfg(feature = "kafka")]
        {
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
        }

        #[cfg(not(feature = "kafka"))]
        {
            let _ = &recv_sender;
            while !shared.stop_flag.load(Ordering::Relaxed) {
                tokio::time::sleep(std::time::Duration::from_secs(1)).await;
            }
        }
    });

    tracing::info!("Bridge loop exiting");
}

/// Spawns a consumer task for every channel in the current config that does
/// not already have a running task (i.e. no token in channel_tokens).
#[cfg(feature = "kafka")]
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

        tracing::info!("Spawned consumer task for channel `{}`", config.name);

        tokio::spawn(async move {
            crate::kafka::consume_loop(&config, sender, shared_clone, token).await;
        });
    }
}

/// Publishes a message to a named outgoing connection synchronously using a temporary Tokio runtime.
///
/// Returns `Ok(())` on success or an error message string on failure.
pub fn publish_sync(shared: &BridgeShared, conn_name: &str, payload: &[u8]) -> Result<(), String> {
    let outgoing_config = {
        let bridge_state = shared.state.lock();
        bridge_state.outgoing.get(conn_name).cloned()
    };

    let config = outgoing_config.ok_or_else(|| format!("Unknown outgoing connection: {conn_name}"))?;

    #[cfg(feature = "kafka")]
    {
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .map_err(|err| format!("Failed to create tokio runtime: {err}"))?;

        runtime.block_on(crate::kafka::publish_message(&config, payload))
    }

    #[cfg(not(feature = "kafka"))]
    {
        let _ = (&config, payload);
        Err(format!("No queue backend compiled for connection `{conn_name}`"))
    }
}

/// Pings a named outgoing connection by fetching Kafka broker metadata.
///
/// Returns `Ok(())` on success or an error message string on failure.
pub fn ping_sync(shared: &BridgeShared, conn_name: &str) -> Result<(), String> {
    let outgoing_config = {
        let bridge_state = shared.state.lock();
        bridge_state.outgoing.get(conn_name).cloned()
    };

    let config = outgoing_config.ok_or_else(|| format!("Unknown outgoing connection: {conn_name}"))?;

    #[cfg(feature = "kafka")]
    {
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .map_err(|err| format!("Failed to create tokio runtime: {err}"))?;

        runtime.block_on(crate::kafka::ping_broker(&config))
    }

    #[cfg(not(feature = "kafka"))]
    {
        let _ = &config;
        Err(format!("No queue backend compiled for connection `{conn_name}`"))
    }
}
