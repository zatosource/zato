//! Kafka-specific consumer and producer wrappers for the standalone Zato queue bridge.
//!
//! Wraps `rdkafka` types and applies TLS and SASL properties to the client configuration.

#![cfg(feature = "kafka")]

use std::sync::Arc;
use std::sync::atomic::Ordering;

use rdkafka::ClientConfig;
use rdkafka::Message;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::producer::{FutureProducer, FutureRecord, Producer};
use tokio_util::sync::CancellationToken;

use crate::bridge::{BridgeShared, ChannelConfig, OutgoingConfig, RecvEvent};

/// The sasl.mechanism value for PLAIN.
const MECHANISM_PLAIN: &str = "PLAIN";

/// The sasl.mechanism value for SCRAM-SHA-256.
const MECHANISM_SCRAM_SHA_256: &str = "SCRAM-SHA-256";

/// The sasl.mechanism value for SCRAM-SHA-512.
const MECHANISM_SCRAM_SHA_512: &str = "SCRAM-SHA-512";

/// The sasl.mechanism value for OAUTHBEARER.
const MECHANISM_OAUTHBEARER: &str = "OAUTHBEARER";

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

/// Runs a consume loop for a single Kafka channel, sending received messages through
/// the provided tokio mpsc sender to the bridge loop.
///
/// Exits when the `cancel` token is cancelled or the global stop flag is set.
pub async fn consume_loop(
    config: &ChannelConfig,
    message_sender: tokio::sync::mpsc::UnboundedSender<RecvEvent>,
    shared: Arc<BridgeShared>,
    cancel: CancellationToken,
) {
    loop {
        if shared.stop_flag.load(Ordering::Relaxed) || cancel.is_cancelled() {
            tracing::info!("Kafka consumer `{}` stopping", config.name);
            return;
        }

        let mut client_config = ClientConfig::new();
        client_config
            .set("bootstrap.servers", &config.address)
            .set("group.id", &config.group_id)
            .set("auto.offset.reset", "earliest")
            .set("session.timeout.ms", "6000")
            .set("heartbeat.interval.ms", "2000")
            .set("max.poll.interval.ms", "300000")
            .set("fetch.wait.max.ms", "500")
            .set("reconnect.backoff.ms", "100")
            .set("reconnect.backoff.max.ms", "10000")
            .set("enable.partition.eof", "false");

        apply_security_config(&mut client_config, &SecurityConfig::from(config));

        let consumer: StreamConsumer = match client_config.create() {
            Ok(consumer) => consumer,
            Err(err) => {
                tracing::warn!("Kafka consumer `{}`: waiting for broker: {err}", config.name);
                tokio::select! {
                    () = cancel.cancelled() => return,
                    () = tokio::time::sleep(std::time::Duration::from_secs(5)) => continue,
                }
            }
        };

        if let Err(err) = consumer.subscribe(&[&config.topic]) {
            tracing::warn!("Kafka consumer `{}`: cannot subscribe to `{}`: {err}", config.name, config.topic);
            tokio::select! {
                () = cancel.cancelled() => return,
                () = tokio::time::sleep(std::time::Duration::from_secs(5)) => continue,
            }
        }

        tracing::info!("Kafka consumer `{}` subscribed to topic `{}`", config.name, config.topic);

        let mut consecutive_errors: u32 = 0;

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
                result = consumer.recv() => {
                    match result {
                        Ok(borrowed_message) => {
                            consecutive_errors = 0;
                            let payload = match borrowed_message.payload() {
                                Some(bytes) => bytes.to_vec(),
                                None => continue,
                            };
                            let event = RecvEvent::without_headers(
                                config.name.clone(),
                                borrowed_message.topic().to_string(),
                                config.service.clone(),
                                payload,
                            );
                            if message_sender.send(event).is_err() {
                                return;
                            }
                        }
                        Err(err) => {
                            consecutive_errors += 1;
                            tracing::warn!("Kafka consumer `{}`: receive warning: {err}", config.name);
                            if consecutive_errors >= 5 {
                                tracing::warn!("Kafka consumer `{}`: reconnecting after repeated failures", config.name);
                                break;
                            }
                            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
                        }
                    }
                }
            }
        }
    }
}

/// Publishes a single message to a Kafka topic via a one-shot `FutureProducer`.
///
/// Returns an error string if the producer cannot be created or the send fails.
pub async fn publish_message(config: &OutgoingConfig, payload: &[u8]) -> Result<(), String> {
    let mut client_config = ClientConfig::new();
    client_config.set("bootstrap.servers", &config.address);

    apply_security_config(&mut client_config, &SecurityConfig::from(config));

    let producer: FutureProducer = client_config
        .create()
        .map_err(|err| format!("Failed to create Kafka producer: {err}"))?;

    let record: FutureRecord<'_, str, [u8]> = FutureRecord::to(&config.topic).payload(payload);

    producer
        .send(record, rdkafka::util::Timeout::After(std::time::Duration::from_secs(5)))
        .await
        .map_err(|(err, _)| format!("Kafka send failed: {err}"))?;

    Ok(())
}

/// Pings a Kafka broker by fetching cluster metadata without producing a message.
///
/// Returns `Ok(())` if metadata is fetched successfully.
pub async fn ping_broker(config: &OutgoingConfig) -> Result<(), String> {
    let mut client_config = ClientConfig::new();
    client_config.set("bootstrap.servers", &config.address);

    apply_security_config(&mut client_config, &SecurityConfig::from(config));

    let producer: FutureProducer = client_config
        .create()
        .map_err(|err| format!("Failed to create Kafka client for ping: {err}"))?;

    tokio::task::spawn_blocking(move || {
        producer
            .client()
            .fetch_metadata(None, std::time::Duration::from_secs(5))
            .map_err(|err| format!("Kafka metadata fetch failed: {err}"))
            .map(|_| ())
    })
    .await
    .map_err(|err| format!("Ping task panicked: {err}"))?
}
