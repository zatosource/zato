//! Bridge state management and background thread loop for the Zato queue bridge.

use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use crossbeam_channel::Receiver;
use pyo3::prelude::*;

#[cfg(feature = "kafka")]
use crate::kafka;

/// Configuration for a channel (consumer) connection to an external queue.
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
    pub service_name: String,
    /// Whether SSL/TLS is enabled for this connection.
    pub ssl: bool,
    /// Path to the CA certificate file for SSL verification.
    pub ssl_ca_file: Option<String>,
    /// Path to the client certificate file for mutual TLS.
    pub ssl_cert_file: Option<String>,
    /// Path to the client private key file for mutual TLS.
    pub ssl_key_file: Option<String>,
}

/// Configuration for an outgoing (producer) connection to an external queue.
pub struct OutgoingConfig {
    /// Connection name as registered in Zato.
    pub name: String,
    /// Broker address (e.g. "host:9092" for Kafka).
    pub address: String,
    /// Topic to publish to.
    pub topic: String,
    /// Whether SSL/TLS is enabled for this connection.
    pub ssl: bool,
    /// Path to the CA certificate file for SSL verification.
    pub ssl_ca_file: Option<String>,
    /// Path to the client certificate file for mutual TLS.
    pub ssl_cert_file: Option<String>,
    /// Path to the client private key file for mutual TLS.
    pub ssl_key_file: Option<String>,
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

/// Runs the bridge background loop, consuming messages from all registered channels
/// and forwarding publish requests to outgoing connections.
///
/// This function is meant to be called from a dedicated background thread. It creates
/// a tokio runtime internally and blocks until the stop flag is set.
pub fn bridge_loop(
    state: Arc<parking_lot::Mutex<BridgeState>>,
    on_message_cb: Py<PyAny>,
    publish_receiver: Receiver<(String, Vec<u8>)>,
    stop_flag: Arc<AtomicBool>,
    watchdog_registry: Option<Arc<crate::watchdog::WatchdogRegistry>>,
) {
    let runtime = tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .thread_name("zato-queue-bridge-rt")
        .build();

    let runtime = match runtime {
        Ok(runtime) => runtime,
        Err(err) => {
            log::error!("Failed to create tokio runtime for queue bridge: {err}");
            return;
        }
    };

    let heartbeat = watchdog_registry.as_ref().map(|reg| reg.register("zato-queue-bridge"));

    runtime.block_on(async {
        let channel_configs: Vec<ChannelConfig> = {
            let bridge_state = state.lock();
            let mut configs = Vec::with_capacity(bridge_state.channels.len());
            for channel_config in bridge_state.channels.values() {
                configs.push(ChannelConfig {
                    name: channel_config.name.clone(),
                    address: channel_config.address.clone(),
                    topic: channel_config.topic.clone(),
                    group_id: channel_config.group_id.clone(),
                    service_name: channel_config.service_name.clone(),
                    ssl: channel_config.ssl,
                    ssl_ca_file: channel_config.ssl_ca_file.clone(),
                    ssl_cert_file: channel_config.ssl_cert_file.clone(),
                    ssl_key_file: channel_config.ssl_key_file.clone(),
                });
            }
            configs
        };

        #[cfg(feature = "kafka")]
        for channel_config in &channel_configs {
            let callback = Python::try_attach(|py| on_message_cb.clone_ref(py));
            let callback = match callback {
                Some(cb_ref) => cb_ref,
                None => {
                    eprintln!("Failed to acquire GIL to clone callback for consumer `{}`", channel_config.name);
                    continue;
                }
            };
            let channel_stop_flag = Arc::clone(&stop_flag);
            let consumer_name = channel_config.name.clone();
            let consumer_address = channel_config.address.clone();
            let consumer_topic = channel_config.topic.clone();
            let consumer_group_id = channel_config.group_id.clone();
            let consumer_service_name = channel_config.service_name.clone();
            let consumer_ssl = channel_config.ssl;
            let consumer_ssl_ca_file = channel_config.ssl_ca_file.clone();
            let consumer_ssl_cert_file = channel_config.ssl_cert_file.clone();
            let consumer_ssl_key_file = channel_config.ssl_key_file.clone();

            tokio::spawn(async move {
                let consume_params = kafka::ConsumeParams {
                    connection_name: &consumer_name,
                    address: &consumer_address,
                    topic: &consumer_topic,
                    group_id: &consumer_group_id,
                    service_name: &consumer_service_name,
                    ssl_config: kafka::SslConfig {
                        ssl: consumer_ssl,
                        ssl_ca_file: consumer_ssl_ca_file.as_deref(),
                        ssl_cert_file: consumer_ssl_cert_file.as_deref(),
                        ssl_key_file: consumer_ssl_key_file.as_deref(),
                    },
                };
                kafka::consume_loop(&consume_params, callback, channel_stop_flag).await;
            });
        }

        #[cfg(not(feature = "kafka"))]
        let _ = &channel_configs;

        loop {
            if stop_flag.load(Ordering::Relaxed) {
                break;
            }

            if let Some(hb) = &heartbeat {
                hb.beat();
            }

            match publish_receiver.try_recv() {
                Ok((conn_name, payload)) => {
                    let outgoing_snapshot = {
                        let bridge_state = state.lock();
                        bridge_state.outgoing.get(&conn_name).map(|cfg| {
                            (
                                cfg.address.clone(),
                                cfg.topic.clone(),
                                cfg.ssl,
                                cfg.ssl_ca_file.clone(),
                                cfg.ssl_cert_file.clone(),
                                cfg.ssl_key_file.clone(),
                            )
                        })
                    };

                    if let Some((address, topic, outgoing_ssl, ssl_ca, ssl_cert, ssl_key)) = outgoing_snapshot {
                        #[cfg(feature = "kafka")]
                        {
                            let publish_params = kafka::PublishParams {
                                address: &address,
                                topic: &topic,
                                ssl: outgoing_ssl,
                                ssl_ca_file: ssl_ca.as_deref(),
                                ssl_cert_file: ssl_cert.as_deref(),
                                ssl_key_file: ssl_key.as_deref(),
                                payload: &payload,
                            };

                            if let Err(err) = kafka::publish_message(&publish_params).await {
                                eprintln!("Failed to publish to connection `{conn_name}`: {err}");
                            }
                        }

                        #[cfg(not(feature = "kafka"))]
                        {
                            let _ = (&payload, &address, &topic, outgoing_ssl, &ssl_ca, &ssl_cert, &ssl_key);
                            eprintln!("No queue backend compiled for connection `{conn_name}`");
                        }
                    } else {
                        eprintln!("Publish requested for unknown outgoing connection `{conn_name}`");
                    }
                }
                Err(crossbeam_channel::TryRecvError::Empty) => {
                    if let Some(hb) = &heartbeat {
                        hb.set_expected_sleep(std::time::Duration::from_millis(10));
                    }
                    tokio::time::sleep(std::time::Duration::from_millis(10)).await;
                }
                Err(crossbeam_channel::TryRecvError::Disconnected) => {
                    break;
                }
            }
        }
    });
}
