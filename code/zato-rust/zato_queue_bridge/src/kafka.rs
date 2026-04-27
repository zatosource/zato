//! Kafka-specific consumer and producer wrappers for the Zato queue bridge.
//!
//! Wraps `rdkafka` types and handles SSL/TLS configuration using the same
//! property names as the standard Kafka client (`ssl.ca.location`,
//! `ssl.certificate.location`, `ssl.key.location`).

#![cfg(feature = "kafka")]

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use pyo3::prelude::*;
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

/// Runs a consume loop for a single Kafka topic, invoking the Python callback for each message.
///
/// This function is meant to be spawned as a tokio task. It blocks until the stop flag
/// is set or an unrecoverable error occurs.
pub async fn consume_loop(params: &ConsumeParams<'_>, on_message_cb: Py<PyAny>, stop_flag: Arc<AtomicBool>) {
    let mut client_config = ClientConfig::new();
    client_config
        .set("bootstrap.servers", params.address)
        .set("group.id", params.group_id)
        .set("auto.offset.reset", "earliest");

    apply_ssl_config(&mut client_config, &params.ssl_config);

    let consumer: StreamConsumer = match client_config.create() {
        Ok(consumer) => consumer,
        Err(err) => {
            log::error!("Failed to create Kafka consumer for `{}`: {err}", params.connection_name);
            return;
        }
    };

    if let Err(err) = consumer.subscribe(&[params.topic]) {
        log::error!(
            "Failed to subscribe to topic `{}` on `{}`: {err}",
            params.topic,
            params.connection_name
        );
        return;
    }

    log::info!("Kafka consumer `{}` subscribed to topic `{}`", params.connection_name, params.topic);

    loop {
        if stop_flag.load(Ordering::Relaxed) {
            break;
        }

        match consumer.recv().await {
            Ok(borrowed_message) => {
                let payload = match borrowed_message.payload() {
                    Some(bytes) => bytes.to_vec(),
                    None => continue,
                };
                let message_topic = borrowed_message.topic().to_string();
                let svc_name = params.service_name.to_string();

                if let Some(result) = Python::try_attach(|py| -> PyResult<()> {
                    let args = (payload.as_slice(), message_topic.as_str(), svc_name.as_str());
                    on_message_cb.call1(py, args)?;
                    Ok(())
                }) {
                    result.ok();
                }
            }
            Err(err) => {
                log::error!("Kafka consumer `{}` receive error: {err}", params.connection_name);
                tokio::time::sleep(std::time::Duration::from_secs(1)).await;
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
