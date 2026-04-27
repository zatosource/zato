//! Queue bridge crate for Zato - connects external message queues (Kafka, SQS, IBM MQ)
//! to the Zato integration platform, exposing a Python-visible `QueueBridge` class via PyO3.

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use crossbeam_channel::{Receiver, Sender};
use parking_lot::Mutex;
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Bridge state management and background thread loop.
pub mod bridge;

/// Queue type definitions and endpoint trait.
pub mod endpoint;

/// Kafka-specific consumer and producer wrappers.
#[cfg(feature = "kafka")]
pub mod kafka;

/// Inbound and outbound message types.
pub mod message;

/// Watchdog thread for detecting hung bridge threads.
pub mod watchdog;

/// Convenience alias so the rest of the module can say `PyObject`.
type PyObject = Py<PyAny>;

/// Collects log messages while a mutex is held so they can be flushed after the
/// lock is released, avoiding `pyo3_log`'s blocking `Python::attach` call that
/// would otherwise deadlock with the GIL.
pub struct DeferredLog {
    /// Buffered messages with their log level.
    entries: Vec<(log::Level, String)>,
}

impl Default for DeferredLog {
    fn default() -> Self {
        Self::new()
    }
}

impl DeferredLog {
    /// Creates an empty buffer.
    pub const fn new() -> Self {
        Self { entries: Vec::new() }
    }

    /// Flushes all buffered messages through `log::log!`.
    ///
    /// Must be called only when no mutex is held.
    pub fn flush(self) {
        for (level, msg) in self.entries {
            log::log!(level, "{msg}");
        }
    }
}

/// Buffers a formatted log message into a `DeferredLog` instead of calling `log::` directly.
macro_rules! deferred_log {
    ($deferred:expr, $level:expr, $($arg:tt)*) => {
        $deferred.entries.push(($level, format!($($arg)*)))
    };
}

pub(crate) use deferred_log;

/// Extracts a required string value from a Python dict.
fn extract_required_str(dict: &Bound<'_, PyDict>, key: &str) -> PyResult<String> {
    dict.get_item(key)?
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_string()))?
        .extract::<String>()
}

/// Extracts an optional string value from a Python dict.
fn extract_optional_str(dict: &Bound<'_, PyDict>, key: &str) -> PyResult<Option<String>> {
    match dict.get_item(key)? {
        Some(val) => {
            let text: String = val.extract()?;
            if text.is_empty() { Ok(None) } else { Ok(Some(text)) }
        }
        None => Ok(None),
    }
}

/// Extracts a required bool value from a Python dict, defaulting to `false` if absent.
fn extract_bool_or_false(dict: &Bound<'_, PyDict>, key: &str) -> PyResult<bool> {
    match dict.get_item(key)? {
        Some(val) => val.extract::<bool>(),
        None => Ok(false),
    }
}

/// The queue bridge runtime, exposed to Python as a `#[pyclass]`.
///
/// Owns the background thread, tokio runtime, connection registry, and the
/// crossbeam channel used for the publish path. Each instance connects Zato
/// to one or more external message queue brokers.
#[pyclass]
pub struct QueueBridge {
    /// Shared bridge state holding channel and outgoing connection configs.
    state: Arc<Mutex<bridge::BridgeState>>,
    /// Sender side of the publish channel - pymethods enqueue messages here.
    publish_sender: Sender<(String, Vec<u8>)>,
    /// Receiver side of the publish channel - consumed by the background thread.
    publish_receiver: Receiver<(String, Vec<u8>)>,
    /// Flag to signal the background thread to stop.
    stop_flag: Arc<AtomicBool>,
    /// Handle for the background bridge thread.
    thread_handle: Mutex<Option<std::thread::JoinHandle<()>>>,
    /// Python callback invoked for each inbound message from a channel.
    on_message_cb: PyObject,
}

#[pymethods]
impl QueueBridge {
    /// Creates a new queue bridge instance with no active connections.
    #[new]
    fn new(py: Python<'_>) -> Self {
        let (publish_sender, publish_receiver) = crossbeam_channel::unbounded();
        Self {
            state: Arc::new(Mutex::new(bridge::BridgeState::new())),
            publish_sender,
            publish_receiver,
            stop_flag: Arc::new(AtomicBool::new(false)),
            thread_handle: Mutex::new(None),
            on_message_cb: py.None(),
        }
    }

    /// Starts the bridge background thread, extracting the `on_message_cb` callback from config.
    ///
    /// The config dict must contain an `on_message_cb` key with a callable that receives
    /// `(payload_bytes, topic, service_name)` for each consumed message.
    fn start(&mut self, py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<()> {
        let on_message_cb: PyObject = config
            .get_item("on_message_cb")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("missing on_message_cb"))?
            .unbind();

        self.on_message_cb = on_message_cb.clone_ref(py);
        self.stop_flag.store(false, Ordering::Relaxed);

        let bridge_state = Arc::clone(&self.state);
        let callback = on_message_cb;
        let receiver = self.publish_receiver.clone();
        let bridge_stop_flag = Arc::clone(&self.stop_flag);

        let registry = Arc::new(watchdog::WatchdogRegistry::new(
            Arc::clone(&bridge_stop_flag),
            Arc::clone(&bridge_state),
        ));
        let registry_for_thread = Arc::clone(&registry);

        let handle = py.detach(|| {
            watchdog::start_watchdog(Arc::clone(&registry));
            std::thread::Builder::new()
                .name("zato-queue-bridge".into())
                .spawn(move || {
                    bridge::bridge_loop(bridge_state, callback, receiver, bridge_stop_flag, Some(registry_for_thread));
                })
                .map_err(|err| pyo3::exceptions::PyException::new_err(format!("spawn failed: {err}")))
        })?;

        *self.thread_handle.lock() = Some(handle);

        Ok(())
    }

    /// Signals the background thread to stop and waits for it to finish.
    fn stop(&self, py: Python<'_>) -> PyResult<()> {
        self.stop_flag.store(true, Ordering::Relaxed);

        let handle = py.detach(|| self.thread_handle.lock().take());

        if let Some(thread_handle) = handle {
            py.detach(|| {
                thread_handle.join().ok();
            });
        }

        Ok(())
    }

    /// Enqueues a message to be published to the named outgoing connection.
    fn publish(&self, py: Python<'_>, conn_name: String, data: Vec<u8>) -> PyResult<()> {
        let sender = self.publish_sender.clone();
        py.detach(|| {
            sender
                .send((conn_name, data))
                .map_err(|err| pyo3::exceptions::PyException::new_err(format!("publish send failed: {err}")))
        })
    }

    /// Registers a new channel (consumer) connection from a Python config dict.
    ///
    /// Required keys: `name`, `address`, `topic`, `group_id`, `service`.
    /// Optional keys: `ssl`, `ssl_ca_file`, `ssl_cert_file`, `ssl_key_file`.
    fn add_channel(&self, py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<()> {
        let channel_name = extract_required_str(config, "name")?;
        let address = extract_required_str(config, "address")?;
        let topic = extract_required_str(config, "topic")?;
        let group_id = extract_required_str(config, "group_id")?;
        let service_name = extract_required_str(config, "service")?;
        let ssl = extract_bool_or_false(config, "ssl")?;
        let ssl_ca_file = extract_optional_str(config, "ssl_ca_file")?;
        let ssl_cert_file = extract_optional_str(config, "ssl_cert_file")?;
        let ssl_key_file = extract_optional_str(config, "ssl_key_file")?;

        let channel_config = bridge::ChannelConfig {
            name: channel_name.clone(),
            address,
            topic,
            group_id,
            service_name,
            ssl,
            ssl_ca_file,
            ssl_cert_file,
            ssl_key_file,
        };

        py.detach(|| {
            let mut bridge_state = self.state.lock();
            bridge_state.channels.insert(channel_name, channel_config);
        });

        Ok(())
    }

    /// Registers a new outgoing (producer) connection from a Python config dict.
    ///
    /// Required keys: `name`, `address`, `topic`.
    /// Optional keys: `ssl`, `ssl_ca_file`, `ssl_cert_file`, `ssl_key_file`.
    fn add_outgoing(&self, py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<()> {
        let outgoing_name = extract_required_str(config, "name")?;
        let address = extract_required_str(config, "address")?;
        let topic = extract_required_str(config, "topic")?;
        let ssl = extract_bool_or_false(config, "ssl")?;
        let ssl_ca_file = extract_optional_str(config, "ssl_ca_file")?;
        let ssl_cert_file = extract_optional_str(config, "ssl_cert_file")?;
        let ssl_key_file = extract_optional_str(config, "ssl_key_file")?;

        let outgoing_config = bridge::OutgoingConfig {
            name: outgoing_name.clone(),
            address,
            topic,
            ssl,
            ssl_ca_file,
            ssl_cert_file,
            ssl_key_file,
        };

        py.detach(|| {
            let mut bridge_state = self.state.lock();
            bridge_state.outgoing.insert(outgoing_name, outgoing_config);
        });

        Ok(())
    }

    /// Removes a channel (consumer) connection by name.
    fn delete_channel(&self, py: Python<'_>, name: String) -> PyResult<()> {
        py.detach(|| {
            let mut bridge_state = self.state.lock();
            bridge_state.channels.remove(&name);
        });
        Ok(())
    }

    /// Removes an outgoing (producer) connection by name.
    fn delete_outgoing(&self, py: Python<'_>, name: String) -> PyResult<()> {
        py.detach(|| {
            let mut bridge_state = self.state.lock();
            bridge_state.outgoing.remove(&name);
        });
        Ok(())
    }
}

/// PyO3 module entry point - registers the `QueueBridge` class.
#[pymodule]
fn zato_queue_bridge(module: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();
    module.add_class::<QueueBridge>()?;
    Ok(())
}
