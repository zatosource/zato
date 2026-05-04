//! Kafka-specific consumer and producer wrappers for the standalone Zato queue bridge.
//!
//! Wraps `rdkafka` types and handles SSL/TLS configuration using the same
//! property names as the standard Kafka client (`ssl.ca.location`,
//! `ssl.certificate.location`, `ssl.key.location`).

#![cfg(feature = "kafka")]

use std::sync::Arc;
use std::sync::atomic::Ordering;

use rdkafka::ClientConfig;
use rdkafka::Message;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::producer::{FutureProducer, FutureRecord, Producer};
use tokio_util::sync::CancellationToken;

use crate::bridge::{BridgeShared, ChannelConfig, OutgoingConfig, RecvEvent};

/// Applies SSL/TLS properties to an rdkafka `ClientConfig`.
fn apply_ssl_config(
    client_config: &mut ClientConfig,
    ssl: bool,
    ssl_ca_file: Option<&str>,
    ssl_cert_file: Option<&str>,
    ssl_key_file: Option<&str>,
) {
    if !ssl {
        return;
    }
    client_config.set("security.protocol", "ssl");
    if let Some(ca_path) = ssl_ca_file {
        client_config.set("ssl.ca.location", ca_path);
    }
    if let Some(cert_path) = ssl_cert_file {
        client_config.set("ssl.certificate.location", cert_path);
    }
    if let Some(key_path) = ssl_key_file {
        client_config.set("ssl.key.location", key_path);
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

        apply_ssl_config(
            &mut client_config,
            config.ssl,
            config.ssl_ca_file.as_deref(),
            config.ssl_cert_file.as_deref(),
            config.ssl_key_file.as_deref(),
        );

        let consumer: StreamConsumer = match client_config.create() {
            Ok(consumer) => consumer,
            Err(err) => {
                tracing::warn!("Kafka consumer `{}`: waiting for broker: {err}", config.name);
                tokio::select! {
                    () = cancel.cancelled() => return,
                    _ = tokio::time::sleep(std::time::Duration::from_secs(5)) => continue,
                }
            }
        };

        if let Err(err) = consumer.subscribe(&[&config.topic]) {
            tracing::warn!("Kafka consumer `{}`: cannot subscribe to `{}`: {err}", config.name, config.topic);
            tokio::select! {
                () = cancel.cancelled() => return,
                _ = tokio::time::sleep(std::time::Duration::from_secs(5)) => continue,
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
                            let event = RecvEvent {
                                channel_name: config.name.clone(),
                                topic: borrowed_message.topic().to_string(),
                                service: config.service.clone(),
                                payload,
                            };
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

    apply_ssl_config(
        &mut client_config,
        config.ssl,
        config.ssl_ca_file.as_deref(),
        config.ssl_cert_file.as_deref(),
        config.ssl_key_file.as_deref(),
    );

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

    apply_ssl_config(
        &mut client_config,
        config.ssl,
        config.ssl_ca_file.as_deref(),
        config.ssl_cert_file.as_deref(),
        config.ssl_key_file.as_deref(),
    );

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
