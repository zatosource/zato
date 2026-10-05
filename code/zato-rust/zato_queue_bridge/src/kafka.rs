//! Kafka-specific consumer and producer wrappers for the standalone Zato queue bridge.
//!
//! Wraps `rdkafka` types and applies TLS and SASL properties to the client configuration.
//! Consumers never store offsets on their own - the server marks each message as resolved
//! through a `commit_offset` command once the service invocation, a DLQ move or a skip is done.

#![cfg(feature = "kafka")]

use std::sync::Arc;
use std::sync::atomic::Ordering;

use rdkafka::Message;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::message::{BorrowedMessage, Header, Headers, OwnedHeaders};
use rdkafka::producer::{FutureProducer, FutureRecord, Producer};
use rdkafka::{ClientConfig, TopicPartitionList};
use tokio_util::sync::CancellationToken;

use crate::bridge::{BridgeShared, ChannelConfig, CommitReceiver, OutgoingConfig, RecvEvent, SendOutcome, SendRequest};
use crate::wire;

/// The sasl.mechanism value for PLAIN.
const MECHANISM_PLAIN: &str = "PLAIN";

/// The sasl.mechanism value for SCRAM-SHA-256.
const MECHANISM_SCRAM_SHA_256: &str = "SCRAM-SHA-256";

/// The sasl.mechanism value for SCRAM-SHA-512.
const MECHANISM_SCRAM_SHA_512: &str = "SCRAM-SHA-512";

/// The sasl.mechanism value for OAUTHBEARER.
const MECHANISM_OAUTHBEARER: &str = "OAUTHBEARER";

/// The acks value under which librdkafka allows idempotent writes.
const ACKS_ALL: &str = "all";

/// Header carrying the message key when it is valid UTF-8.
const HEADER_KEY: &str = "kafka.key";

/// Header carrying the topic the message came from.
const HEADER_TOPIC: &str = "kafka.topic";

/// Header carrying the partition the message came from.
const HEADER_PARTITION: &str = "kafka.partition";

/// Header carrying the offset of the message in its partition.
const HEADER_OFFSET: &str = "kafka.offset";

/// Header carrying the message timestamp in milliseconds since the Unix epoch, empty when Kafka has none.
const HEADER_TIMESTAMP: &str = "kafka.timestamp";

/// Header telling whether the message is a tombstone, i.e. a key with no value.
const HEADER_IS_TOMBSTONE: &str = "kafka.is_tombstone";

/// Suffix under which a header value that is not valid UTF-8 travels base64-encoded.
const B64_SUFFIX: &str = ".b64";

/// Milliseconds in one second, for the send timeout configured in seconds.
const MS_PER_SECOND: u64 = 1_000;

/// Bytes librdkafka needs in `receive.message.max.bytes` on top of the largest fetch.
const RECEIVE_OVERHEAD: u64 = 512;

/// The librdkafka default of `receive.message.max.bytes`, left alone for messages that fit in it.
const DEFAULT_RECEIVE_MESSAGE_MAX_BYTES: u64 = 100_000_000;

/// How long a consumer waits before trying the broker again after a failure.
const RECONNECT_WAIT: std::time::Duration = std::time::Duration::from_secs(5);

/// How long a consumer waits after one receive error before polling again.
const RECEIVE_ERROR_WAIT: std::time::Duration = std::time::Duration::from_secs(1);

/// How many receive errors in a row make a consumer rebuild its connection.
const MAX_CONSECUTIVE_ERRORS: u32 = 5;

/// How long a ping waits for cluster metadata.
const PING_TIMEOUT: std::time::Duration = std::time::Duration::from_secs(5);

// ################################################################################################################################

/// Connection security settings shared by Kafka channels and outgoing connections.
struct SecurityConfig<'config> {
    /// Whether the broker connection is wrapped in TLS.
    ssl: bool,

    /// Path to the CA certificate the broker's certificate is verified against.
    ssl_ca_file: Option<&'config str>,

    /// Path to the client certificate for mutual TLS.
    ssl_cert_file: Option<&'config str>,

    /// Path to the client private key for mutual TLS.
    ssl_key_file: Option<&'config str>,

    /// Password of the client private key, empty when the key is not encrypted.
    ssl_key_password: &'config str,

    /// SASL mechanism name, empty when the broker does not use SASL.
    sasl_mechanism: &'config str,

    /// SASL username for the PLAIN and SCRAM mechanisms.
    username: &'config str,

    /// SASL password for the PLAIN and SCRAM mechanisms.
    password: &'config str,

    /// Token endpoint for the OAUTHBEARER mechanism.
    oauth_token_url: &'config str,

    /// OAuth client ID for the OAUTHBEARER mechanism.
    oauth_client_id: &'config str,

    /// OAuth client secret for the OAUTHBEARER mechanism.
    oauth_client_secret: &'config str,

    /// OAuth scopes for the OAUTHBEARER mechanism.
    oauth_scope: &'config str,
}

impl<'config> From<&'config ChannelConfig> for SecurityConfig<'config> {
    fn from(config: &'config ChannelConfig) -> Self {
        Self {
            ssl: config.ssl,
            ssl_ca_file: config.ssl_ca_file.as_deref(),
            ssl_cert_file: config.ssl_cert_file.as_deref(),
            ssl_key_file: config.ssl_key_file.as_deref(),
            ssl_key_password: &config.ssl_key_password,
            sasl_mechanism: &config.sasl_mechanism,
            username: &config.username,
            password: &config.password,
            oauth_token_url: &config.oauth_token_url,
            oauth_client_id: &config.oauth_client_id,
            oauth_client_secret: &config.oauth_client_secret,
            oauth_scope: &config.oauth_scope,
        }
    }
}

impl<'config> From<&'config OutgoingConfig> for SecurityConfig<'config> {
    fn from(config: &'config OutgoingConfig) -> Self {
        Self {
            ssl: config.ssl,
            ssl_ca_file: config.ssl_ca_file.as_deref(),
            ssl_cert_file: config.ssl_cert_file.as_deref(),
            ssl_key_file: config.ssl_key_file.as_deref(),
            ssl_key_password: &config.ssl_key_password,
            sasl_mechanism: &config.sasl_mechanism,
            username: &config.username,
            password: &config.password,
            oauth_token_url: &config.oauth_token_url,
            oauth_client_id: &config.oauth_client_id,
            oauth_client_secret: &config.oauth_client_secret,
            oauth_scope: &config.oauth_scope,
        }
    }
}

/// Applies TLS and SASL properties to an rdkafka `ClientConfig`.
fn apply_security_config(client_config: &mut ClientConfig, security: &SecurityConfig<'_>) {
    let has_sasl = !security.sasl_mechanism.is_empty();

    // Plaintext without SASL is the librdkafka default.
    let protocol = match (security.ssl, has_sasl) {
        (false, false) => None,
        (true, false) => Some("ssl"),
        (false, true) => Some("sasl_plaintext"),
        (true, true) => Some("sasl_ssl"),
    };

    if let Some(protocol) = protocol {
        client_config.set("security.protocol", protocol);
    }

    if security.ssl {
        if let Some(ca_path) = security.ssl_ca_file {
            client_config.set("ssl.ca.location", ca_path);
        }
        if let Some(cert_path) = security.ssl_cert_file {
            client_config.set("ssl.certificate.location", cert_path);
        }
        if let Some(key_path) = security.ssl_key_file {
            client_config.set("ssl.key.location", key_path);
        }
        // An empty password means the key is not encrypted, and librdkafka would treat an
        // empty string as a real password.
        if !security.ssl_key_password.is_empty() {
            client_config.set("ssl.key.password", security.ssl_key_password);
        }
    }

    if !has_sasl {
        return;
    }

    client_config.set("sasl.mechanism", security.sasl_mechanism);

    match security.sasl_mechanism {
        MECHANISM_PLAIN | MECHANISM_SCRAM_SHA_256 | MECHANISM_SCRAM_SHA_512 => {
            client_config.set("sasl.username", security.username);
            client_config.set("sasl.password", security.password);
        }
        MECHANISM_OAUTHBEARER => {
            // The oidc method has librdkafka fetch the token itself.
            client_config.set("sasl.oauthbearer.method", "oidc");
            client_config.set("sasl.oauthbearer.token.endpoint.url", security.oauth_token_url);
            client_config.set("sasl.oauthbearer.client.id", security.oauth_client_id);
            client_config.set("sasl.oauthbearer.client.secret", security.oauth_client_secret);

            // An empty scope is not sent.
            if !security.oauth_scope.is_empty() {
                client_config.set("sasl.oauthbearer.scope", security.oauth_scope);
            }
        }
        other => {
            // Any other mechanism is rejected by librdkafka when the client is created.
            tracing::warn!("Kafka SASL mechanism `{other}` is not one the bridge configures credentials for");
        }
    }
}

// ################################################################################################################################

/// Builds the rdkafka client configuration of a channel's consumer.
fn build_consumer_config(config: &ChannelConfig) -> ClientConfig {
    let max_message_size = config.max_message_size();

    let mut client_config = ClientConfig::new();
    client_config
        .set("bootstrap.servers", &config.address)
        .set("group.id", &config.group_id)
        .set("auto.offset.reset", config.auto_offset_reset())
        // Auto-commit stays on, but it only ever commits offsets the server resolved,
        // because the consume loop stores them on commit_offset and nowhere else.
        .set("enable.auto.offset.store", "false")
        .set("max.partition.fetch.bytes", max_message_size.to_string())
        .set("fetch.max.bytes", max_message_size.to_string())
        .set("session.timeout.ms", "6000")
        .set("heartbeat.interval.ms", "2000")
        .set("max.poll.interval.ms", "300000")
        .set("fetch.wait.max.ms", "500")
        .set("reconnect.backoff.ms", "100")
        .set("reconnect.backoff.max.ms", "10000")
        .set("enable.partition.eof", "false");

    // librdkafka requires the receive buffer to be larger than the largest fetch.
    let receive_max = max_message_size.saturating_add(RECEIVE_OVERHEAD);
    if receive_max > DEFAULT_RECEIVE_MESSAGE_MAX_BYTES {
        client_config.set("receive.message.max.bytes", receive_max.to_string());
    }

    apply_security_config(&mut client_config, &SecurityConfig::from(config));

    client_config
}

/// Appends one header to the list, base64-encoding a value that is not valid UTF-8.
fn push_header(headers: &mut Vec<(String, String)>, name: &str, value: Option<&[u8]>) {
    let Some(bytes) = value else {
        headers.push((name.to_string(), String::new()));
        return;
    };

    match std::str::from_utf8(bytes) {
        Ok(text) => headers.push((name.to_string(), text.to_string())),
        Err(_) => {
            // The suffix tells the service the value had to be encoded.
            headers.push((format!("{name}{B64_SUFFIX}"), wire::base64_encode(bytes)));
        }
    }
}

/// Builds a recv event from one consumed message, carrying its headers and metadata.
///
/// A tombstone is forwarded with an empty payload rather than skipped, because storing
/// its offset here would commit past earlier messages still in flight in the server.
fn build_recv_event(config: &ChannelConfig, message: &BorrowedMessage<'_>) -> RecvEvent {
    let mut headers = Vec::new();

    if let Some(message_headers) = message.headers() {
        for index in 0..message_headers.count() {
            if let Some(header) = message_headers.try_get(index) {
                push_header(&mut headers, header.key, header.value);
            }
        }
    }

    if let Some(key) = message.key() {
        push_header(&mut headers, HEADER_KEY, Some(key));
    }

    let timestamp = message.timestamp().to_millis().map(|millis| millis.to_string()).unwrap_or_default();
    let is_tombstone = message.payload().is_none();

    headers.push((HEADER_TOPIC.to_string(), message.topic().to_string()));
    headers.push((HEADER_PARTITION.to_string(), message.partition().to_string()));
    headers.push((HEADER_OFFSET.to_string(), message.offset().to_string()));
    headers.push((HEADER_TIMESTAMP.to_string(), timestamp));
    headers.push((HEADER_IS_TOMBSTONE.to_string(), is_tombstone.to_string()));

    RecvEvent {
        channel_id: config.id(),
        channel_name: config.name.clone(),
        topic: message.topic().to_string(),
        service: config.service.clone(),
        payload: message.payload().map(<[u8]>::to_vec).unwrap_or_default(),
        headers: wire::headers_to_json(&headers),
        reply_to_queue: String::new(),
        reply_to_queue_manager: String::new(),
        message_id: String::new(),
    }
}

// ################################################################################################################################

/// Tracks how many messages a consumer handed to the server and whether its partitions are paused.
struct InFlight {
    /// Messages handed to Redis and not yet marked as resolved by a commit.
    count: u64,
    /// Whether the assigned partitions are paused because the count hit the limit.
    is_paused: bool,
    /// The count at which partitions pause.
    limit: u64,
}

impl InFlight {
    /// Starts tracking with nothing in flight.
    const fn new(limit: u64) -> Self {
        Self {
            count: 0,
            is_paused: false,
            limit,
        }
    }

    /// Records one more message in flight and says whether the partitions are to be paused now.
    ///
    /// Partitions assigned since the last pause arrive unpaused, so this says yes for every
    /// message at or above the limit rather than only for the first one.
    const fn record_forwarded(&mut self) -> bool {
        self.count = self.count.saturating_add(1);
        self.count >= self.limit
    }

    /// Records one message as resolved and says whether the partitions are to be resumed now -
    /// only once they were paused and the count has dropped below the limit again.
    const fn record_committed(&mut self) -> bool {
        self.count = self.count.saturating_sub(1);
        self.is_paused && self.count < self.limit
    }

    /// Records one more message in flight and pauses the partitions once the limit is reached.
    fn on_forwarded(&mut self, consumer: &StreamConsumer, channel_name: &str) {
        if !self.record_forwarded() {
            return;
        }

        match consumer.assignment() {
            Ok(assignment) => {
                if let Err(err) = consumer.pause(&assignment) {
                    tracing::warn!("Kafka consumer `{channel_name}`: cannot pause partitions: {err}");
                } else if !self.is_paused {
                    tracing::info!("Kafka consumer `{channel_name}`: {} messages in flight, pausing", self.count);
                }
                self.is_paused = true;
            }
            Err(err) => tracing::warn!("Kafka consumer `{channel_name}`: cannot read assignment: {err}"),
        }
    }

    /// Records one message as resolved and resumes the partitions once below the limit.
    fn on_committed(&mut self, consumer: &StreamConsumer, channel_name: &str) {
        if !self.record_committed() {
            return;
        }

        match consumer.assignment() {
            Ok(assignment) => {
                if let Err(err) = consumer.resume(&assignment) {
                    tracing::warn!("Kafka consumer `{channel_name}`: cannot resume partitions: {err}");
                } else {
                    tracing::info!("Kafka consumer `{channel_name}`: {} messages in flight, resuming", self.count);
                    self.is_paused = false;
                }
            }
            Err(err) => tracing::warn!("Kafka consumer `{channel_name}`: cannot read assignment: {err}"),
        }
    }
}

/// Whether a resolved message's partition is still among the ones this consumer holds.
///
/// After a rebalance it may not be, and then the consumer that holds the partition now is
/// the one to commit for it - storing the offset here would be storing it for nobody.
fn is_still_assigned(assignment: &TopicPartitionList, request: &crate::bridge::CommitRequest) -> bool {
    assignment.find_partition(&request.topic, request.partition).is_some()
}

/// Stores the offset after a resolved message so the next auto-commit carries it.
///
/// An offset for a partition no longer assigned after a rebalance is dropped, because the
/// consumer that owns the partition now is the one that commits for it.
fn store_resolved_offset(consumer: &StreamConsumer, channel_name: &str, request: &crate::bridge::CommitRequest) {
    let assignment = match consumer.assignment() {
        Ok(assignment) => assignment,
        Err(err) => {
            tracing::warn!("Kafka consumer `{channel_name}`: cannot read assignment: {err}");
            return;
        }
    };

    if !is_still_assigned(&assignment, request) {
        tracing::debug!(
            "Kafka consumer `{channel_name}`: partition {}/{} no longer assigned, dropping offset {}",
            request.topic,
            request.partition,
            request.offset
        );
        return;
    }

    // librdkafka itself stores offset + 1, the position to resume from, so the resolved message's own offset goes in.
    if let Err(err) = consumer.store_offset(&request.topic, request.partition, request.offset) {
        tracing::warn!(
            "Kafka consumer `{channel_name}`: cannot store offset {} for {}/{}: {err}",
            request.offset,
            request.topic,
            request.partition
        );
    }
}

/// Waits before the consumer tries the broker again, unless it is cancelled meanwhile.
///
/// Returns `true` when the loop should go on, `false` when it was cancelled.
async fn wait_before_retry(cancel: &CancellationToken) -> bool {
    tokio::select! {
        () = cancel.cancelled() => false,
        () = tokio::time::sleep(RECONNECT_WAIT) => true,
    }
}

/// Runs a consume loop for a single Kafka channel, sending received messages through
/// the provided tokio mpsc sender to the bridge loop.
///
/// Offsets are stored only when the server sends a commit for the message through
/// `commit_receiver`. Exits when the `cancel` token is cancelled or the global stop flag is set.
pub async fn consume_loop(
    config: &ChannelConfig,
    message_sender: tokio::sync::mpsc::UnboundedSender<RecvEvent>,
    shared: Arc<BridgeShared>,
    cancel: CancellationToken,
    mut commit_receiver: CommitReceiver,
) {
    let topics = config.topics();

    if topics.is_empty() {
        tracing::warn!("Kafka consumer `{}` has no topics to consume from, stopping", config.name);
        return;
    }

    loop {
        if shared.stop_flag.load(Ordering::Relaxed) || cancel.is_cancelled() {
            tracing::info!("Kafka consumer `{}` stopping", config.name);
            return;
        }

        let client_config = build_consumer_config(config);

        let consumer: StreamConsumer = match client_config.create() {
            Ok(consumer) => consumer,
            Err(err) => {
                tracing::warn!("Kafka consumer `{}`: waiting for broker: {err}", config.name);
                if wait_before_retry(&cancel).await {
                    continue;
                }
                return;
            }
        };

        if let Err(err) = consumer.subscribe(&topics) {
            tracing::warn!(
                "Kafka consumer `{}`: cannot subscribe to `{}`: {err}",
                config.name,
                config.topics_text()
            );
            if wait_before_retry(&cancel).await {
                continue;
            }
            return;
        }

        tracing::info!("Kafka consumer `{}` subscribed to `{}`", config.name, config.topics_text());

        let mut consecutive_errors: u32 = 0;

        // Every rebuilt consumer starts with nothing in flight - commits for messages the previous
        // one handed over still arrive and are stored, since they are valid positions for the group.
        let mut in_flight = InFlight::new(config.max_in_flight());

        loop {
            if shared.stop_flag.load(Ordering::Relaxed) || cancel.is_cancelled() {
                tracing::info!("Kafka consumer `{}` stopping", config.name);
                return;
            }

            tokio::select! {
                () = cancel.cancelled() => {
                    tracing::info!("Kafka consumer `{}` cancelled", config.name);
                    return;
                }
                commit = commit_receiver.recv() => {
                    if let Some(request) = commit {
                        store_resolved_offset(&consumer, &config.name, &request);
                        in_flight.on_committed(&consumer, &config.name);
                    } else {
                        // The sender lives in BridgeShared and goes away with the channel.
                        tracing::info!("Kafka consumer `{}` lost its commit queue, stopping", config.name);
                        return;
                    }
                }
                result = consumer.recv() => {
                    match result {
                        Ok(borrowed_message) => {
                            consecutive_errors = 0;
                            let event = build_recv_event(config, &borrowed_message);
                            if message_sender.send(event).is_err() {
                                return;
                            }
                            in_flight.on_forwarded(&consumer, &config.name);
                        }
                        Err(err) => {
                            consecutive_errors += 1;
                            tracing::warn!("Kafka consumer `{}`: receive warning: {err}", config.name);
                            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS {
                                tracing::warn!("Kafka consumer `{}`: reconnecting after repeated failures", config.name);
                                break;
                            }
                            tokio::time::sleep(RECEIVE_ERROR_WAIT).await;
                        }
                    }
                }
            }
        }
    }
}

// ################################################################################################################################

/// Builds the producer of an outgoing connection from its producer options.
///
/// # Errors
///
/// Returns the error text when librdkafka rejects the configuration.
pub fn create_producer(config: &OutgoingConfig) -> Result<FutureProducer, String> {
    let is_idempotent = config.is_idempotent();
    let acks = config.acks();
    let send_timeout_ms = config.send_timeout().saturating_mul(MS_PER_SECOND);

    let mut client_config = ClientConfig::new();
    client_config
        .set("bootstrap.servers", &config.address)
        .set("compression.type", config.compression())
        .set("enable.idempotence", is_idempotent.to_string())
        .set("message.max.bytes", config.max_message_size().to_string())
        .set("linger.ms", config.linger_ms().to_string())
        .set("message.timeout.ms", send_timeout_ms.to_string());

    // librdkafka refuses to create an idempotent producer with anything but acks=all,
    // so exactly-once wins over the configured acks rather than failing the connection.
    if is_idempotent && acks != ACKS_ALL {
        tracing::info!(
            "Kafka producer `{}`: exactly once requires acks=all, ignoring acks={acks}",
            config.name
        );
        client_config.set("acks", ACKS_ALL);
    } else {
        client_config.set("acks", acks);
    }

    apply_security_config(&mut client_config, &SecurityConfig::from(config));

    client_config
        .create()
        .map_err(|err| format!("Failed to create Kafka producer: {err}"))
}

/// Builds and caches the producer of an outgoing Kafka connection, replacing any previous one.
///
/// A connection whose producer cannot be built has no cache entry, and the next send
/// tries to build it again so a corrected broker address or certificate takes effect.
pub fn refresh_producer(shared: &BridgeShared, config: &OutgoingConfig) {
    if config.type_ != crate::bridge::TYPE_OUTCONN_KAFKA {
        return;
    }

    match create_producer(config) {
        Ok(producer) => {
            let _ = shared.kafka_producers.lock().insert(config.name.clone(), Arc::new(producer));
        }
        Err(err) => {
            tracing::warn!("Kafka producer `{}` not created: {err}", config.name);
            let _ = shared.kafka_producers.lock().remove(&config.name);
        }
    }
}

/// Drops the cached producer of an outgoing connection, if there is one.
pub fn drop_producer(shared: &BridgeShared, name: &str) {
    let _ = shared.kafka_producers.lock().remove(name);
}

/// Drops every cached producer, as a reload does before rebuilding them.
pub fn clear_producers(shared: &BridgeShared) {
    shared.kafka_producers.lock().clear();
}

/// Returns the cached producer of an outgoing connection, building it when missing.
fn get_producer(shared: &BridgeShared, config: &OutgoingConfig) -> Result<Arc<FutureProducer>, String> {
    let cached = shared.kafka_producers.lock().get(&config.name).cloned();

    if let Some(producer) = cached {
        return Ok(producer);
    }

    let producer = Arc::new(create_producer(config)?);
    let _ = shared.kafka_producers.lock().insert(config.name.clone(), Arc::clone(&producer));

    Ok(producer)
}

/// Publishes a single message through the cached producer of an outgoing connection.
///
/// # Errors
///
/// Returns the error text when the producer cannot be built or the delivery report says the send failed.
pub async fn publish_message(shared: &BridgeShared, config: &OutgoingConfig, request: SendRequest) -> Result<SendOutcome, String> {
    let producer = get_producer(shared, config)?;

    let mut headers = OwnedHeaders::new_with_capacity(request.headers.len());
    for (name, value) in &request.headers {
        headers = headers.insert(Header {
            key: name,
            value: Some(value.as_slice()),
        });
    }

    let mut record: FutureRecord<'_, [u8], [u8]> = FutureRecord::to(&config.topic).headers(headers);

    if let Some(key) = request.key.as_deref() {
        record = record.key(key);
    }

    if let Some(partition) = request.partition {
        record = record.partition(partition);
    }

    // A tombstone has no payload at all, which is what tells Kafka to compact the key away.
    if !request.is_tombstone {
        record = record.payload(&request.payload);
    }

    // The timeout here only covers waiting for room in the local queue, the delivery
    // itself is bounded by message.timeout.ms set on the producer.
    let send_timeout = std::time::Duration::from_secs(config.send_timeout());

    let delivery = producer
        .send(record, rdkafka::util::Timeout::After(send_timeout))
        .await
        .map_err(|(err, _)| format!("Kafka send failed: {err}"))?;

    Ok(SendOutcome {
        partition: Some(delivery.partition),
        offset: Some(delivery.offset),
    })
}

/// Pings a Kafka broker by fetching cluster metadata through the cached producer.
///
/// # Errors
///
/// Returns the error text when the producer cannot be built or the metadata fetch fails.
pub async fn ping(shared: &BridgeShared, config: &OutgoingConfig) -> Result<(), String> {
    let producer = get_producer(shared, config)?;

    // The metadata fetch blocks the thread, so it runs on the blocking pool.
    let join_result = tokio::task::spawn_blocking(move || {
        producer
            .client()
            .fetch_metadata(None, PING_TIMEOUT)
            .map_err(|err| format!("Kafka metadata fetch failed: {err}"))
            .map(|_| ())
    })
    .await;

    join_result.map_err(|err| format!("Ping task panicked: {err}"))?
}

// ################################################################################################################################

#[cfg(test)]
mod tests {
    use super::*;
    use crate::bridge::CommitRequest;

    /// A commit request for one position of a topic.
    fn commit_request(topic: &str, partition: i32, offset: i64) -> CommitRequest {
        CommitRequest {
            topic: topic.to_string(),
            partition,
            offset,
        }
    }

    /// Looks a header up by name in the list `push_header` builds.
    fn header_value<'headers>(headers: &'headers [(String, String)], name: &str) -> Option<&'headers str> {
        headers.iter().find(|(key, _)| key == name).map(|(_, value)| value.as_str())
    }

    // Header encoding

    #[test]
    fn a_text_header_is_forwarded_as_it_is() {
        let mut headers = Vec::new();
        push_header(&mut headers, "tenant", Some(b"acme"));

        assert_eq!(header_value(&headers, "tenant"), Some("acme"));
        assert_eq!(headers.len(), 1);
    }

    #[test]
    fn a_header_that_is_not_text_is_encoded_and_renamed() {
        let mut headers = Vec::new();
        push_header(&mut headers, "digest", Some(&[0xff, 0x00, 0xfe]));

        // The service sees the suffix and knows to decode the value
        assert_eq!(header_value(&headers, "digest"), None);
        assert_eq!(
            header_value(&headers, "digest.b64"),
            Some(wire::base64_encode(&[0xff, 0x00, 0xfe]).as_str())
        );
    }

    #[test]
    fn a_header_without_a_value_is_an_empty_string() {
        let mut headers = Vec::new();
        push_header(&mut headers, "empty", None);

        assert_eq!(header_value(&headers, "empty"), Some(""));
    }

    #[test]
    fn an_empty_value_is_text_and_stays_under_its_own_name() {
        let mut headers = Vec::new();
        push_header(&mut headers, "blank", Some(b""));

        assert_eq!(header_value(&headers, "blank"), Some(""));
        assert_eq!(header_value(&headers, "blank.b64"), None);
    }

    #[test]
    fn headers_become_a_json_object_the_server_reads() {
        let mut headers = Vec::new();
        push_header(&mut headers, "tenant", Some(b"acme"));
        push_header(&mut headers, "digest", Some(&[0xff]));

        let json: std::collections::HashMap<String, String> =
            wire::parse_payload(&wire::headers_to_json(&headers)).expect("the headers parse");

        assert_eq!(json.get("tenant").map(String::as_str), Some("acme"));
        assert_eq!(json.get("digest.b64"), Some(&wire::base64_encode(&[0xff])));
    }

    // Offsets across a rebalance

    #[test]
    fn an_offset_for_a_partition_still_held_is_kept() {
        let mut assignment = TopicPartitionList::new();
        assignment.add_partition("orders", 0);
        assignment.add_partition("orders", 2);

        assert!(is_still_assigned(&assignment, &commit_request("orders", 0, 17)));
        assert!(is_still_assigned(&assignment, &commit_request("orders", 2, 3)));
    }

    #[test]
    fn an_offset_for_a_partition_that_moved_away_is_dropped() {
        let mut assignment = TopicPartitionList::new();
        assignment.add_partition("orders", 0);

        // The partition went to another consumer in a rebalance
        assert!(!is_still_assigned(&assignment, &commit_request("orders", 1, 17)));

        // And so did a whole topic
        assert!(!is_still_assigned(&assignment, &commit_request("invoices", 0, 17)));
    }

    #[test]
    fn an_offset_is_dropped_when_nothing_is_held_at_all() {
        let assignment = TopicPartitionList::new();

        assert!(!is_still_assigned(&assignment, &commit_request("orders", 0, 0)));
    }

    // In-flight limit

    #[test]
    fn partitions_pause_once_the_limit_is_reached() {
        let mut in_flight = InFlight::new(3);

        assert!(!in_flight.record_forwarded());
        assert!(!in_flight.record_forwarded());
        assert!(in_flight.record_forwarded());
        assert_eq!(in_flight.count, 3);
    }

    #[test]
    fn the_pause_is_repeated_for_every_message_above_the_limit() {
        let mut in_flight = InFlight::new(2);
        let _ = in_flight.record_forwarded();

        // Partitions assigned after the first pause arrive unpaused, so each message above the limit pauses again
        assert!(in_flight.record_forwarded());
        assert!(in_flight.record_forwarded());
        assert!(in_flight.record_forwarded());
    }

    #[test]
    fn partitions_resume_once_below_the_limit_and_only_if_they_were_paused() {
        let mut in_flight = InFlight::new(2);
        let _ = in_flight.record_forwarded();
        let _ = in_flight.record_forwarded();

        // Nothing was told to pause yet, so there is nothing to resume
        assert!(!in_flight.record_committed());

        in_flight.count = 2;
        in_flight.is_paused = true;

        assert!(in_flight.record_committed());
        assert_eq!(in_flight.count, 1);
    }

    #[test]
    fn a_commit_at_the_limit_does_not_resume() {
        let mut in_flight = InFlight::new(2);
        in_flight.count = 3;
        in_flight.is_paused = true;

        // Three down to two is still at the limit
        assert!(!in_flight.record_committed());
        assert!(in_flight.record_committed());
    }

    #[test]
    fn a_commit_with_nothing_in_flight_does_not_go_below_zero() {
        let mut in_flight = InFlight::new(2);

        assert!(!in_flight.record_committed());
        assert_eq!(in_flight.count, 0);
    }
}
