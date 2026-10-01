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

/// Where a Kafka consumer starts when its group has no committed offset yet.
pub const DEFAULT_AUTO_OFFSET_RESET: &str = "earliest";

/// Largest message, in bytes, a Kafka channel fetches or an outgoing connection sends.
pub const DEFAULT_MAX_MESSAGE_SIZE: u64 = 1_000_000;

/// How many messages a Kafka channel may hand to the server before it pauses its partitions.
pub const DEFAULT_MAX_IN_FLIGHT: u64 = 100;

/// Compression an outgoing Kafka connection applies when none is configured.
pub const DEFAULT_COMPRESSION: &str = "none";

/// Acknowledgments an outgoing Kafka connection waits for when none are configured.
///
/// The librdkafka default of `1` loses an acknowledged message when the partition
/// leader fails over before the followers catch up.
pub const DEFAULT_ACKS: &str = "all";

/// Whether an outgoing Kafka connection writes each message exactly once by default.
pub const DEFAULT_IS_IDEMPOTENT: bool = true;

/// How long, in milliseconds, an outgoing Kafka connection gathers messages into a batch.
pub const DEFAULT_LINGER_MS: u64 = 0;

/// How long, in seconds, an outgoing Kafka connection waits for a send to be confirmed.
pub const DEFAULT_SEND_TIMEOUT: u64 = 5;

// ################################################################################################################################

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

impl FlagValue {
    /// Reads the flag as a boolean, treating any text other than "true" as `false`.
    fn as_bool(&self) -> bool {
        match self {
            Self::Bool(value) => *value,
            Self::Text(text) => text == "true",
        }
    }
}

/// Deserializes a JSON value that may be `null`, a boolean or a string into a `bool`,
/// treating `null` and the empty string as `false`.
fn deserialize_nullable_bool<'de, D: Deserializer<'de>>(deserializer: D) -> Result<bool, D::Error> {
    let parsed = Option::<FlagValue>::deserialize(deserializer)?;
    let out = parsed.as_ref().is_some_and(FlagValue::as_bool);
    Ok(out)
}

/// Deserializes a JSON value that may be `null`, a boolean or a string into an optional `bool`.
///
/// Unlike `deserialize_nullable_bool`, a `null` or an empty string stays `None` so the
/// caller can apply a default that is `true`.
fn deserialize_optional_bool<'de, D: Deserializer<'de>>(deserializer: D) -> Result<Option<bool>, D::Error> {
    let parsed = Option::<FlagValue>::deserialize(deserializer)?;

    let out = match parsed {
        Some(FlagValue::Bool(value)) => Some(value),
        Some(FlagValue::Text(text)) => {
            // An unchecked dashboard toggle arrives as an empty string and means "not set".
            if text.is_empty() { None } else { Some(text == "true") }
        }
        None => None,
    };

    Ok(out)
}

/// Deserializes a JSON value that may be `null` or a string into a `String`.
///
/// A `null` becomes an empty string, which is needed because ODB columns such as
/// `username` are `NULL` for connections that do not use them.
fn deserialize_nullable_string<'de, D: Deserializer<'de>>(deserializer: D) -> Result<String, D::Error> {
    Option::<String>::deserialize(deserializer).map(std::option::Option::unwrap_or_default)
}

/// A count or size as serialized by the various config sources.
///
/// Enmasse and the ODB carry real numbers, while dashboard forms may carry
/// the same value as text, and an untouched field arrives as `null` or an empty string.
#[derive(Deserialize)]
#[serde(untagged)]
enum NumberValue {
    /// A real number.
    Number(u64),
    /// The number as text, or an empty string for a field left untouched.
    Text(String),
}

/// Deserializes a JSON value that may be `null`, a number or a numeric string into an optional `u64`.
///
/// A `null`, an empty string or text that is not a number stays `None`, which lets the
/// accessor methods on the config structs apply the documented default.
fn deserialize_optional_u64<'de, D: Deserializer<'de>>(deserializer: D) -> Result<Option<u64>, D::Error> {
    let parsed = Option::<NumberValue>::deserialize(deserializer)?;

    let out = match parsed {
        Some(NumberValue::Number(value)) => Some(value),
        Some(NumberValue::Text(text)) => text.trim().parse::<u64>().ok(),
        None => None,
    };

    Ok(out)
}

/// A list of topics as serialized by the various config sources.
///
/// Enmasse carries a real list, while the dashboard textarea carries one topic per line
/// and configs predating the list carry a single `topic` string.
#[derive(Deserialize)]
#[serde(untagged)]
enum TopicsValue {
    /// A real list of topic names.
    List(Vec<String>),
    /// Topic names separated by newlines or commas.
    Text(String),
}

/// Splits a text of topic names separated by newlines or commas, dropping blanks.
fn split_topics(text: &str) -> Vec<String> {
    let mut out = Vec::new();

    for part in text.split(['\n', ',']) {
        let trimmed = part.trim();
        if !trimmed.is_empty() {
            out.push(trimmed.to_string());
        }
    }

    out
}

/// Deserializes a JSON value that may be `null`, a list of strings or a delimited string
/// into a list of topic names, with blanks dropped.
fn deserialize_topics<'de, D: Deserializer<'de>>(deserializer: D) -> Result<Vec<String>, D::Error> {
    let parsed = Option::<TopicsValue>::deserialize(deserializer)?;

    let out = match parsed {
        Some(TopicsValue::List(items)) => {
            // A list may still carry blank entries, e.g. from a trailing newline in a form.
            let joined = items.join("\n");
            split_topics(&joined)
        }
        Some(TopicsValue::Text(text)) => split_topics(&text),
        None => Vec::new(),
    };

    Ok(out)
}

/// Default connection type for configs that predate the `type_` field.
fn default_channel_type() -> String {
    TYPE_CHANNEL_KAFKA.to_string()
}

/// Default connection type for outgoing configs that predate the `type_` field.
fn default_outgoing_type() -> String {
    TYPE_OUTCONN_KAFKA.to_string()
}

// ################################################################################################################################

/// Configuration for a channel (consumer) connection to an external queue.
///
/// Field names match the ODB `GenericConnection` model so the server can
/// forward the dict from the database without renaming anything. Kafka channels
/// use `topics` and `group_id`, IBM MQ channels use `queue_manager`, `mq_channel_name`
/// and `queue` - the remaining fields are shared.
#[derive(Clone, Deserialize, Serialize)]
pub struct ChannelConfig {
    /// Connection ID as stored in the ODB, which names the channel's recv stream.
    #[serde(default, deserialize_with = "deserialize_optional_u64")]
    pub id: Option<u64>,
    /// Connection name as registered in Zato.
    pub name: String,
    /// Connection type, e.g. `channel-kafka` or `channel-ibm-mq`.
    #[serde(default = "default_channel_type")]
    pub type_: String,
    /// Broker address (e.g. "host:9092" for Kafka, "host:1414" for IBM MQ).
    pub address: String,
    /// Single topic to consume from, kept for configs that predate `topics` (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub topic: String,
    /// Topics to consume from (Kafka only).
    #[serde(default, deserialize_with = "deserialize_topics")]
    pub topics: Vec<String>,
    /// Consumer group identifier (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub group_id: String,
    /// Where the consumer starts when its group has no committed offset, `earliest` or `latest` (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub auto_offset_reset: String,
    /// Largest message, in bytes, the consumer fetches (Kafka only).
    #[serde(default, deserialize_with = "deserialize_optional_u64")]
    pub max_message_size: Option<u64>,
    /// How many messages may be handed to the server and not yet committed before partitions pause (Kafka only).
    #[serde(default, deserialize_with = "deserialize_optional_u64")]
    pub max_in_flight: Option<u64>,
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
    /// Username for IBM MQ, or for the PLAIN and SCRAM mechanisms of Kafka.
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub username: String,
    /// Password matching the username.
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub password: String,
    /// SASL mechanism name, empty when the broker does not use SASL (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub sasl_mechanism: String,
    /// Token endpoint the OAUTHBEARER mechanism fetches its tokens from (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_token_url: String,
    /// OAuth client ID sent to the token endpoint (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_client_id: String,
    /// OAuth client secret sent to the token endpoint (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_client_secret: String,
    /// Space-separated OAuth scopes requested from the token endpoint (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_scope: String,
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
    /// Password of the client private key, empty when the key is not encrypted.
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub ssl_key_password: String,
}

impl ChannelConfig {
    /// Returns the connection ID, or zero for a config that never carried one.
    pub fn id(&self) -> u64 {
        self.id.unwrap_or(0)
    }

    /// Returns the topics to consume from, falling back on the single `topic` of older configs.
    pub fn topics(&self) -> Vec<&str> {
        if !self.topics.is_empty() {
            return self.topics.iter().map(String::as_str).collect();
        }

        // A config predating the list carries one topic, and an empty one carries none.
        if self.topic.is_empty() {
            Vec::new()
        } else {
            vec![self.topic.as_str()]
        }
    }

    /// Returns the topics as one comma-separated text for logs and the HTTP API.
    pub fn topics_text(&self) -> String {
        self.topics().join(", ")
    }

    /// Returns where the consumer starts when its group has no committed offset.
    pub fn auto_offset_reset(&self) -> &str {
        if self.auto_offset_reset.is_empty() {
            DEFAULT_AUTO_OFFSET_RESET
        } else {
            &self.auto_offset_reset
        }
    }

    /// Returns the largest message, in bytes, the consumer fetches.
    pub fn max_message_size(&self) -> u64 {
        self.max_message_size.unwrap_or(DEFAULT_MAX_MESSAGE_SIZE)
    }

    /// Returns how many messages may be in flight before the consumer pauses its partitions.
    pub const fn max_in_flight(&self) -> u64 {
        // A limit of zero would pause the consumer forever, so it means the default.
        match self.max_in_flight {
            Some(0) | None => DEFAULT_MAX_IN_FLIGHT,
            Some(value) => value,
        }
    }
}

// ################################################################################################################################

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
    /// Compression applied to messages, one of none, gzip, snappy, lz4 or zstd (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub compression: String,
    /// Acknowledgments a send waits for, one of all, 1 or 0 (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub acks: String,
    /// Whether a message that had to be sent again is written exactly once (Kafka only).
    #[serde(default, deserialize_with = "deserialize_optional_bool")]
    pub is_idempotent: Option<bool>,
    /// Largest message, in bytes, the producer accepts (Kafka only).
    #[serde(default, deserialize_with = "deserialize_optional_u64")]
    pub max_message_size: Option<u64>,
    /// How long, in milliseconds, messages are gathered into a batch before being sent (Kafka only).
    #[serde(default, deserialize_with = "deserialize_optional_u64")]
    pub linger_ms: Option<u64>,
    /// How long, in seconds, a send waits for its confirmation (Kafka only).
    #[serde(default, deserialize_with = "deserialize_optional_u64")]
    pub send_timeout: Option<u64>,
    /// Queue manager name (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub queue_manager: String,
    /// Server-connection channel name, e.g. `DEV.APP.SVRCONN` (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub mq_channel_name: String,
    /// Queue to publish to (IBM MQ only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub queue: String,
    /// Username for IBM MQ, or for the PLAIN and SCRAM mechanisms of Kafka.
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub username: String,
    /// Password matching the username.
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub password: String,
    /// SASL mechanism name, empty when the broker does not use SASL (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub sasl_mechanism: String,
    /// Token endpoint the OAUTHBEARER mechanism fetches its tokens from (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_token_url: String,
    /// OAuth client ID sent to the token endpoint (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_client_id: String,
    /// OAuth client secret sent to the token endpoint (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_client_secret: String,
    /// Space-separated OAuth scopes requested from the token endpoint (Kafka only).
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub oauth_scope: String,
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
    /// Password of the client private key, empty when the key is not encrypted.
    #[serde(default, deserialize_with = "deserialize_nullable_string")]
    pub ssl_key_password: String,
}

impl OutgoingConfig {
    /// Returns the compression applied to messages.
    pub fn compression(&self) -> &str {
        if self.compression.is_empty() {
            DEFAULT_COMPRESSION
        } else {
            &self.compression
        }
    }

    /// Returns the acknowledgments a send waits for.
    pub fn acks(&self) -> &str {
        if self.acks.is_empty() { DEFAULT_ACKS } else { &self.acks }
    }

    /// Returns whether messages are written exactly once.
    pub fn is_idempotent(&self) -> bool {
        self.is_idempotent.unwrap_or(DEFAULT_IS_IDEMPOTENT)
    }

    /// Returns the largest message, in bytes, the producer accepts.
    pub fn max_message_size(&self) -> u64 {
        self.max_message_size.unwrap_or(DEFAULT_MAX_MESSAGE_SIZE)
    }

    /// Returns how long, in milliseconds, messages are gathered into a batch.
    pub fn linger_ms(&self) -> u64 {
        self.linger_ms.unwrap_or(DEFAULT_LINGER_MS)
    }

    /// Returns how long, in seconds, a send waits for its confirmation.
    pub const fn send_timeout(&self) -> u64 {
        // A timeout of zero would fail every send at once, so it means the default.
        match self.send_timeout {
            Some(0) | None => DEFAULT_SEND_TIMEOUT,
            Some(value) => value,
        }
    }
}

// ################################################################################################################################

/// A message consumed from an external queue, ready to be published to Redis.
pub struct RecvEvent {
    /// ID of the channel connection that produced this message, which names its recv stream.
    pub channel_id: u64,
    /// Channel connection name that produced this message.
    pub channel_name: String,
    /// Topic (Kafka) or queue (IBM MQ) the message was received from.
    pub topic: String,
    /// Zato service name to invoke.
    pub service: String,
    /// Raw message payload bytes.
    pub payload: Vec<u8>,
    /// JSON object string with message headers (Kafka headers and metadata, or MQMD fields and MQRFH2 folders for IBM MQ).
    pub headers: String,
    /// Reply-to queue from the incoming message, empty when there is none.
    pub reply_to_queue: String,
    /// Reply-to queue manager from the incoming message, empty when there is none.
    pub reply_to_queue_manager: String,
    /// Hex-encoded message ID of the incoming message, empty for Kafka.
    pub message_id: String,
}

/// A reply to a command, published to the reply stream by the reply publisher thread.
pub struct ReplyEvent {
    /// Correlation ID of the command being answered.
    pub correlation_id: String,
    /// Outcome of the command, `ok` or `error`.
    pub status: String,
    /// Result data for `ok`, or the error text for `error`.
    pub data: String,
}

/// A request from the server to mark one message of a Kafka channel as resolved.
pub struct CommitRequest {
    /// Topic the message came from.
    pub topic: String,
    /// Partition the message came from.
    pub partition: i32,
    /// Offset of the message itself, the consumer stores the one after it.
    pub offset: i64,
}

/// What one `send_message` command asks an outgoing connection to publish.
pub struct SendRequest {
    /// Message payload, empty for a tombstone.
    pub payload: Vec<u8>,
    /// Message key, which decides the partition when none is given (Kafka only).
    pub key: Option<Vec<u8>>,
    /// Message headers as name and value pairs (Kafka only).
    pub headers: Vec<(String, Vec<u8>)>,
    /// Partition to publish to, letting Kafka choose when `None` (Kafka only).
    pub partition: Option<i32>,
    /// Whether the message is a tombstone, i.e. a key with no value (Kafka only).
    pub is_tombstone: bool,
}

/// Where a published message landed, as far as the backend reports it.
#[derive(Default)]
pub struct SendOutcome {
    /// Partition the message was written to (Kafka only).
    pub partition: Option<i32>,
    /// Offset the message was written at (Kafka only).
    pub offset: Option<i64>,
}

impl SendOutcome {
    /// Formats the outcome as the JSON data field of a reply, empty when the backend reports nothing.
    pub fn to_reply_data(&self) -> String {
        match (self.partition, self.offset) {
            (Some(partition), Some(offset)) => format!("{{\"partition\":{partition},\"offset\":{offset}}}"),
            _ => String::new(),
        }
    }
}

// ################################################################################################################################

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

/// Sender half of the per-channel commit queue a Kafka consume loop reads from.
pub type CommitSender = tokio::sync::mpsc::UnboundedSender<CommitRequest>;

/// Receiver half of the per-channel commit queue a Kafka consume loop reads from.
pub type CommitReceiver = tokio::sync::mpsc::UnboundedReceiver<CommitRequest>;

/// Shared state accessible from multiple threads in the standalone binary.
pub struct BridgeShared {
    /// Mutex-protected bridge connection state.
    pub state: Mutex<BridgeState>,
    /// Flag to signal all threads to stop.
    pub stop_flag: AtomicBool,
    /// Per-channel cancellation tokens so individual consumer tasks can be stopped.
    pub channel_tokens: Mutex<HashMap<String, CancellationToken>>,
    /// Per-channel commit queues keyed by channel ID, through which `commit_offset` commands reach the consume loops.
    pub commit_senders: Mutex<HashMap<u64, CommitSender>>,
    /// Sender to notify the bridge loop that channels changed and need re-syncing.
    pub config_notify: tokio::sync::Notify,
    /// Replies to commands handled on the bridge runtime, drained by the reply publisher thread.
    pub reply_sender: std::sync::mpsc::Sender<ReplyEvent>,
    /// Handle of the bridge runtime, on which sends and pings run so the command thread never blocks.
    pub runtime_handle: tokio::runtime::Handle,
    /// One producer per outgoing Kafka connection, built when the connection is added or edited.
    #[cfg(feature = "kafka")]
    pub kafka_producers: Mutex<HashMap<String, Arc<rdkafka::producer::FutureProducer>>>,
}

impl BridgeShared {
    /// Creates a new shared state with an empty bridge and stop flag unset.
    pub fn new(reply_sender: std::sync::mpsc::Sender<ReplyEvent>, runtime_handle: tokio::runtime::Handle) -> Self {
        Self {
            state: Mutex::new(BridgeState::new()),
            stop_flag: AtomicBool::new(false),
            channel_tokens: Mutex::new(HashMap::new()),
            commit_senders: Mutex::new(HashMap::new()),
            config_notify: tokio::sync::Notify::new(),
            reply_sender,
            runtime_handle,
            #[cfg(feature = "kafka")]
            kafka_producers: Mutex::new(HashMap::new()),
        }
    }

    /// Cancels and removes the token for the given channel name.
    pub fn cancel_channel(&self, name: &str) {
        // The guard is released here rather than inside the branch below, so the lock is not
        // held while the token is cancelled.
        let mut tokens = self.channel_tokens.lock();
        let token = tokens.remove(name);
        drop(tokens);

        // The commit queue goes with the consume loop it fed.
        let channel_id = self.state.lock().channels.get(name).map(ChannelConfig::id);
        if let Some(channel_id) = channel_id {
            let _ = self.commit_senders.lock().remove(&channel_id);
        }

        if let Some(token) = token {
            tracing::info!("Cancelling consumer task for channel `{name}`");
            token.cancel();
        }
    }

    /// Cancels all running channel consumer tasks.
    pub fn cancel_all_channels(&self) {
        // No consume loop survives this, so no commit queue has a reader left either.
        self.commit_senders.lock().clear();

        let mut tokens = self.channel_tokens.lock();
        for (name, token) in tokens.drain() {
            tracing::info!("Cancelling consumer task for channel `{name}`");
            token.cancel();
        }
    }

    /// Hands a reply to the reply publisher thread.
    pub fn publish_reply(&self, correlation_id: &str, result: Result<String, String>) {
        let (status, data) = match result {
            Ok(data) => ("ok", data),
            Err(err) => ("error", err),
        };

        let event = ReplyEvent {
            correlation_id: correlation_id.to_string(),
            status: status.to_string(),
            data,
        };

        // The publisher thread is gone only at shutdown, when nobody waits for the reply anyway.
        if self.reply_sender.send(event).is_err() {
            tracing::warn!("Reply publisher is gone, dropping reply for correlation_id={correlation_id}");
        }
    }

    /// Routes a commit request to the consume loop of the channel it names.
    pub fn commit_offset(&self, channel_id: u64, request: CommitRequest) {
        // The sender is cloned out so the map is not locked while the request is queued.
        let senders = self.commit_senders.lock();
        let sender = senders.get(&channel_id).cloned();
        drop(senders);

        match sender {
            Some(sender) => {
                // A closed queue means the loop is restarting, and the refetch after the restart
                // redelivers the message, so the lost commit costs nothing.
                if sender.send(request).is_err() {
                    tracing::debug!("Consume loop for channel {channel_id} is not reading commits");
                }
            }
            None => {
                tracing::debug!("No consume loop for channel {channel_id}, dropping commit");
            }
        }
    }
}

// ################################################################################################################################

/// Builds the Tokio multi-threaded runtime the bridge loop, sends and pings run on.
///
/// # Errors
///
/// Returns an error when the runtime's worker threads cannot be started.
pub fn build_runtime() -> std::io::Result<tokio::runtime::Runtime> {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .thread_name("zato-queue-bridge-rt")
        .build()
}

/// Runs the bridge loop, consuming messages from all registered channels
/// and forwarding them through the provided sender to the recv event publisher thread.
///
/// This function blocks on the given runtime until the stop flag is set.
/// It should be called from a dedicated OS thread.
pub fn bridge_loop(runtime: &tokio::runtime::Runtime, shared: &Arc<BridgeShared>, recv_sender: &std::sync::mpsc::Sender<RecvEvent>) {
    runtime.block_on(async {
        let (consume_sender, mut consume_receiver) = tokio::sync::mpsc::unbounded_channel::<RecvEvent>();

        spawn_consumers_for_current_config(shared, &consume_sender);

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
                    spawn_consumers_for_current_config(shared, &consume_sender);
                }
                () = tokio::time::sleep(std::time::Duration::from_secs(1)) => {}
            }
        }
    });

    tracing::info!("Bridge loop exiting");
}

/// Spawns a consumer task for every channel in the current config that does
/// not already have a running task (i.e. no token in `channel_tokens`).
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
                // The commit queue is registered before the loop starts, so a commit arriving
                // right after the channel is added always finds its reader.
                let (commit_sender, commit_receiver) = tokio::sync::mpsc::unbounded_channel::<CommitRequest>();
                let _ = shared.commit_senders.lock().insert(config.id(), commit_sender);

                tokio::spawn(async move {
                    crate::kafka::consume_loop(&config, sender, shared_clone, token, commit_receiver).await;
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

    // Nothing below needs the map, so the lock is released before returning.
    drop(tokens);
}

// ################################################################################################################################

/// Looks up the config of a named outgoing connection.
fn outgoing_config(shared: &BridgeShared, conn_name: &str) -> Result<OutgoingConfig, String> {
    let outgoing_config = {
        let bridge_state = shared.state.lock();
        bridge_state.outgoing.get(conn_name).cloned()
    };

    outgoing_config.ok_or_else(|| format!("Unknown outgoing connection: {conn_name}"))
}

/// Publishes a message to a named outgoing connection on the bridge runtime.
///
/// # Errors
///
/// Returns the error text when the connection is unknown, has no backend compiled in,
/// or the backend reports a failure.
pub async fn publish_message(shared: &Arc<BridgeShared>, conn_name: &str, request: SendRequest) -> Result<SendOutcome, String> {
    let config = outgoing_config(shared, conn_name)?;

    match config.type_.as_str() {
        #[cfg(feature = "kafka")]
        TYPE_OUTCONN_KAFKA => crate::kafka::publish_message(shared, &config, request).await,
        #[cfg(feature = "ibm-mq")]
        TYPE_OUTCONN_IBM_MQ => {
            // MQPUT1 blocks the thread, so it runs on the blocking pool rather than a worker.
            let join_result = tokio::task::spawn_blocking(move || crate::ibm_mq::publish_message(&config, &request.payload)).await;

            join_result
                .map_err(|err| format!("Send task panicked: {err}"))?
                .map(|()| SendOutcome::default())
        }
        other => Err(format!("No queue backend compiled for connection `{conn_name}` of type `{other}`")),
    }
}

/// Pings a named outgoing connection on the bridge runtime.
///
/// # Errors
///
/// Returns the error text when the connection is unknown, has no backend compiled in,
/// or the backend cannot be reached.
pub async fn ping(shared: &Arc<BridgeShared>, conn_name: &str) -> Result<(), String> {
    let config = outgoing_config(shared, conn_name)?;

    match config.type_.as_str() {
        #[cfg(feature = "kafka")]
        TYPE_OUTCONN_KAFKA => crate::kafka::ping(shared, &config).await,
        #[cfg(feature = "ibm-mq")]
        TYPE_OUTCONN_IBM_MQ => {
            // MQCONN blocks the thread, so it runs on the blocking pool rather than a worker.
            let join_result = tokio::task::spawn_blocking(move || crate::ibm_mq::ping(&config)).await;

            join_result.map_err(|err| format!("Ping task panicked: {err}"))?
        }
        other => Err(format!("No queue backend compiled for connection `{conn_name}` of type `{other}`")),
    }
}

// ################################################################################################################################

/// Where a reply is to be delivered, as carried in the descriptor of the incoming message.
pub struct ReplyTarget<'msg> {
    /// Name of the channel that received the message being replied to.
    pub channel_name: &'msg str,

    /// Queue the reply goes to, taken from the original message's `ReplyToQ`.
    pub reply_to_queue: &'msg str,

    /// Queue manager owning that queue, taken from the original message's `ReplyToQMgr`.
    pub reply_to_queue_manager: &'msg str,

    /// Identifier of the original message, used as the reply's correlation ID.
    pub message_id: &'msg str,
}

/// Sends a reply through the channel that received the original message.
///
/// Used by IBM MQ channels to deliver `self.response.payload` to the `ReplyToQ`
/// and `ReplyToQMgr` carried in the incoming message descriptor.
pub fn send_reply_sync(shared: &BridgeShared, target: &ReplyTarget<'_>, payload: &[u8]) -> Result<(), String> {
    let channel_name = target.channel_name;

    let channel_config = {
        let bridge_state = shared.state.lock();
        bridge_state.channels.get(channel_name).cloned()
    };

    let config = channel_config.ok_or_else(|| format!("Unknown channel: {channel_name}"))?;

    match config.type_.as_str() {
        #[cfg(feature = "ibm-mq")]
        TYPE_CHANNEL_IBM_MQ => crate::ibm_mq::send_reply(
            &config,
            target.reply_to_queue,
            target.reply_to_queue_manager,
            target.message_id,
            payload,
        ),
        other => Err(format!("Channel `{channel_name}` of type `{other}` does not support replies")),
    }
}

// ################################################################################################################################

#[cfg(test)]
mod tests {
    use super::*;

    /// Parses a channel out of JSON the way the server sends it.
    fn channel(json: &str) -> ChannelConfig {
        crate::wire::parse_payload::<ChannelConfig>(json).expect("channel config parses")
    }

    /// Parses an outgoing connection out of JSON the way the server sends it.
    fn outgoing(json: &str) -> Result<OutgoingConfig, String> {
        crate::wire::parse_payload::<OutgoingConfig>(json).map_err(|err| err.to_string())
    }

    // Channels

    #[test]
    fn a_channel_predating_the_topic_list_reads_its_one_topic() {
        let config = channel(r#"{"name": "orders", "address": "localhost:9092", "topic": "orders", "service": "my.service"}"#);

        assert_eq!(config.topics(), vec!["orders"]);
        assert_eq!(config.topics_text(), "orders");
        assert_eq!(config.type_, TYPE_CHANNEL_KAFKA);
    }

    #[test]
    fn a_channel_with_a_topic_list_reads_the_list_and_not_the_old_topic() {
        let config = channel(
            r#"{"name": "orders", "address": "localhost:9092", "topic": "old", "topics": ["orders", "invoices"],
            "service": "my.service"}"#,
        );

        assert_eq!(config.topics(), vec!["orders", "invoices"]);
        assert_eq!(config.topics_text(), "orders, invoices");
    }

    #[test]
    fn a_channel_reads_topics_typed_one_per_line_or_separated_by_commas() {
        let config =
            channel(r#"{"name": "orders", "address": "localhost:9092", "topics": "orders\n invoices ,\n\n shipments", "service": "s"}"#);

        assert_eq!(config.topics(), vec!["orders", "invoices", "shipments"]);
    }

    #[test]
    fn a_channel_drops_blank_entries_of_a_topic_list() {
        let config = channel(r#"{"name": "orders", "address": "localhost:9092", "topics": ["orders", "", "  "], "service": "s"}"#);

        assert_eq!(config.topics(), vec!["orders"]);
    }

    #[test]
    fn a_channel_with_no_topic_at_all_reads_none() {
        let config = channel(r#"{"name": "orders", "address": "localhost:9092", "topics": null, "topic": null, "service": "s"}"#);

        assert!(config.topics().is_empty());
        assert_eq!(config.topics_text(), "");
    }

    #[test]
    fn a_channel_reads_its_consumer_options_and_falls_back_on_the_defaults() {
        let config = channel(
            r#"{"id": "17", "name": "orders", "address": "localhost:9092", "topics": ["orders"], "service": "s",
            "auto_offset_reset": "latest", "max_message_size": "2000000", "max_in_flight": 5}"#,
        );

        assert_eq!(config.id(), 17);
        assert_eq!(config.auto_offset_reset(), "latest");
        assert_eq!(config.max_message_size(), 2_000_000);
        assert_eq!(config.max_in_flight(), 5);

        let config = channel(
            r#"{"name": "orders", "address": "localhost:9092", "topics": ["orders"], "service": "s",
            "auto_offset_reset": null, "max_message_size": "", "max_in_flight": 0, "id": null}"#,
        );

        assert_eq!(config.id(), 0);
        assert_eq!(config.auto_offset_reset(), DEFAULT_AUTO_OFFSET_RESET);
        assert_eq!(config.max_message_size(), DEFAULT_MAX_MESSAGE_SIZE);

        // A limit of zero would pause the consumer forever, so it means the default
        assert_eq!(config.max_in_flight(), DEFAULT_MAX_IN_FLIGHT);
    }

    #[test]
    fn a_channel_reads_nulls_and_toggles_the_way_the_database_and_the_dashboard_send_them() {
        let config = channel(
            r#"{"name": "orders", "address": "localhost:9092", "topics": ["orders"], "service": "s",
            "username": null, "password": null, "sasl_mechanism": null, "ssl": "", "ssl_key_password": null}"#,
        );

        assert_eq!(config.username, "");
        assert_eq!(config.sasl_mechanism, "");
        assert!(!config.ssl);
        assert_eq!(config.ssl_key_password, "");

        let config = channel(
            r#"{"name": "orders", "address": "localhost:9092", "topics": ["orders"], "service": "s",
            "ssl": "true", "ssl_ca_file": "/tmp/ca.pem", "ssl_key_password": "secret"}"#,
        );

        assert!(config.ssl);
        assert_eq!(config.ssl_ca_file.as_deref(), Some("/tmp/ca.pem"));
        assert_eq!(config.ssl_key_password, "secret");
    }

    // Outgoing connections

    #[test]
    fn an_outgoing_connection_reads_its_producer_options() {
        let config = outgoing(
            r#"{"name": "orders", "address": "localhost:9092", "topic": "orders", "compression": "zstd", "acks": "1",
            "is_idempotent": false, "max_message_size": 500000, "linger_ms": "20", "send_timeout": 12}"#,
        );

        let config = config.expect("outgoing config parses");

        assert_eq!(config.compression(), "zstd");
        assert_eq!(config.acks(), "1");
        assert!(!config.is_idempotent());
        assert_eq!(config.max_message_size(), 500_000);
        assert_eq!(config.linger_ms(), 20);
        assert_eq!(config.send_timeout(), 12);
        assert_eq!(config.type_, TYPE_OUTCONN_KAFKA);
    }

    #[test]
    fn an_outgoing_connection_without_producer_options_reads_the_defaults() {
        let config = outgoing(
            r#"{"name": "orders", "address": "localhost:9092", "topic": "orders", "compression": null, "acks": "",
            "is_idempotent": "", "max_message_size": null, "linger_ms": "", "send_timeout": 0}"#,
        );

        let config = config.expect("outgoing config parses");

        assert_eq!(config.compression(), DEFAULT_COMPRESSION);
        assert_eq!(config.acks(), DEFAULT_ACKS);
        assert_eq!(config.is_idempotent(), DEFAULT_IS_IDEMPOTENT);
        assert_eq!(config.max_message_size(), DEFAULT_MAX_MESSAGE_SIZE);
        assert_eq!(config.linger_ms(), DEFAULT_LINGER_MS);

        // A timeout of zero would fail every send at once, so it means the default
        assert_eq!(config.send_timeout(), DEFAULT_SEND_TIMEOUT);
    }

    #[test]
    fn an_outgoing_connection_reads_exactly_once_as_text_too() {
        let turned_on = outgoing(r#"{"name": "o", "address": "a", "topic": "t", "is_idempotent": "true"}"#);
        let turned_off = outgoing(r#"{"name": "o", "address": "a", "topic": "t", "is_idempotent": "false"}"#);

        assert_eq!(turned_on.map(|config| config.is_idempotent()), Ok(true));
        assert_eq!(turned_off.map(|config| config.is_idempotent()), Ok(false));
    }

    #[test]
    fn an_outgoing_connection_needs_a_name_and_an_address() {
        assert!(outgoing(r#"{"topic": "orders"}"#).is_err());
        assert!(outgoing(r#"{"name": "orders"}"#).is_err());
    }
}
