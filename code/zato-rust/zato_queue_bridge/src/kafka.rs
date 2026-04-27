//! Kafka-specific consumer and producer wrappers for the Zato queue bridge.
//!
//! Wraps `rdkafka` types and handles SSL/TLS configuration using the same
//! property names as the standard Kafka client (`ssl.ca.location`,
//! `ssl.certificate.location`, `ssl.key.location`).

#![cfg(feature = "kafka")]

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use rdkafka::ClientConfig;
use rdkafka::Message;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::producer::{FutureProducer, FutureRecord};

/// SSL configuration shared between consumer and producer paths.
pub struct SslConfig<'ssl> {
    /// Whether SSL/TLS is enabled for this connection.
    pub ssl: bool,
    /// Path to the CA certificate file.
    pub ssl_ca_file: Option<&'ssl str>,
    /// Path to the client certificate file.
    pub ssl_cert_file: Option<&'ssl str>,
    /// Path to the client private key file.
    pub ssl_key_file: Option<&'ssl str>,
}

/// Parameters for running a Kafka consumer loop.
pub struct ConsumeParams<'params> {
    /// Connection name as registered in Zato.
    pub connection_name: &'params str,
    /// Broker address (e.g. "host:9092").
    pub address: &'params str,
    /// Topic to consume from.
    pub topic: &'params str,
    /// Consumer group identifier.
    pub group_id: &'params str,
    /// Zato service name to invoke for each received message.
    pub service_name: &'params str,
    /// SSL/TLS configuration.
    pub ssl_config: SslConfig<'params>,
}

/// Parameters for publishing a single message to a Kafka topic.
pub struct PublishParams<'params> {
    /// Broker address (e.g. "host:9092").
    pub address: &'params str,
    /// Topic to publish to.
    pub topic: &'params str,
    /// Whether SSL/TLS is enabled.
    pub ssl: bool,
    /// Path to the CA certificate file.
    pub ssl_ca_file: Option<&'params str>,
    /// Path to the client certificate file.
    pub ssl_cert_file: Option<&'params str>,
    /// Path to the client private key file.
    pub ssl_key_file: Option<&'params str>,
    /// Raw message payload bytes.
    pub payload: &'params [u8],
}

/// Applies SSL/TLS properties to an rdkafka `ClientConfig`.
fn apply_ssl_config(client_config: &mut ClientConfig, ssl_config: &SslConfig<'_>) {
    if !ssl_config.ssl {
        return;
    }
    client_config.set("security.protocol", "ssl");
    if let Some(ca_path) = ssl_config.ssl_ca_file {
        client_config.set("ssl.ca.location", ca_path);
    }
    if let Some(cert_path) = ssl_config.ssl_cert_file {
        client_config.set("ssl.certificate.location", cert_path);
    }
    if let Some(key_path) = ssl_config.ssl_key_file {
        client_config.set("ssl.key.location", key_path);
    }
}

/// A message consumed from Kafka, ready to be forwarded to the Python callback
/// on the main bridge OS thread.
pub struct ConsumedMessage {
    /// Raw message payload.
    pub payload: Vec<u8>,
    /// Topic the message was received from.
    pub topic: String,
    /// Zato service name to invoke.
    pub service_name: String,
}

/// Runs a consume loop for a single Kafka topic, sending received messages through
/// the provided channel. The Python callback is NOT invoked here - that happens on
/// the main bridge OS thread to avoid GIL contention from tokio worker threads.
pub async fn consume_loop(
    params: &ConsumeParams<'_>,
    message_sender: crossbeam_channel::Sender<ConsumedMessage>,
    stop_flag: Arc<AtomicBool>,
) {
    loop {
        if stop_flag.load(Ordering::Relaxed) {
            return;
        }

        let mut client_config = ClientConfig::new();
        client_config
            .set("bootstrap.servers", params.address)
            .set("group.id", params.group_id)
            .set("auto.offset.reset", "earliest")
            .set("session.timeout.ms", "6000")
            .set("heartbeat.interval.ms", "2000")
            .set("max.poll.interval.ms", "300000")
            .set("fetch.wait.max.ms", "500")
            .set("reconnect.backoff.ms", "100")
            .set("reconnect.backoff.max.ms", "10000")
            .set("enable.partition.eof", "false")
;

        apply_ssl_config(&mut client_config, &params.ssl_config);

        let consumer: StreamConsumer = match client_config.create() {
            Ok(consumer) => consumer,
            Err(err) => {
                eprintln!("Kafka consumer `{}`: waiting for broker: {err}", params.connection_name);
                tokio::time::sleep(std::time::Duration::from_secs(5)).await;
                continue;
            }
        };

        if let Err(err) = consumer.subscribe(&[params.topic]) {
            eprintln!("Kafka consumer `{}`: cannot subscribe to `{}`: {err}", params.connection_name, params.topic);
            tokio::time::sleep(std::time::Duration::from_secs(5)).await;
            continue;
        }

        eprintln!("Kafka consumer `{}` subscribed to topic `{}`", params.connection_name, params.topic);

        let mut consecutive_errors: u32 = 0;

        loop {
            if stop_flag.load(Ordering::Relaxed) {
                return;
            }

            match consumer.recv().await {
                Ok(borrowed_message) => {
                    consecutive_errors = 0;
                    let payload = match borrowed_message.payload() {
                        Some(bytes) => bytes.to_vec(),
                        None => continue,
                    };
                    let msg = ConsumedMessage {
                        payload,
                        topic: borrowed_message.topic().to_string(),
                        service_name: params.service_name.to_string(),
                    };
                    if message_sender.send(msg).is_err() {
                        return;
                    }
                }
                Err(err) => {
                    consecutive_errors += 1;
                    eprintln!("Kafka consumer `{}`: receive warning: {err}", params.connection_name);
                    if consecutive_errors >= 5 {
                        eprintln!("Kafka consumer `{}`: reconnecting after repeated failures", params.connection_name);
                        break;
                    }
                    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
                }
            }
        }
    }
}

/// Publishes a single message to a Kafka topic via a one-shot `FutureProducer`.
///
/// Returns an error string if the producer cannot be created or the send fails.
pub async fn publish_message(params: &PublishParams<'_>) -> Result<(), String> {
    let mut client_config = ClientConfig::new();
    client_config.set("bootstrap.servers", params.address);

    let ssl_config = SslConfig {
        ssl: params.ssl,
        ssl_ca_file: params.ssl_ca_file,
        ssl_cert_file: params.ssl_cert_file,
        ssl_key_file: params.ssl_key_file,
    };
    apply_ssl_config(&mut client_config, &ssl_config);

    let producer: FutureProducer = client_config
        .create()
        .map_err(|err| format!("Failed to create Kafka producer: {err}"))?;

    let record: FutureRecord<'_, str, [u8]> = FutureRecord::to(params.topic).payload(params.payload);

    producer
        .send(record, rdkafka::util::Timeout::After(std::time::Duration::from_secs(5)))
        .await
        .map_err(|(err, _)| format!("Kafka send failed: {err}"))?;

    Ok(())
}
