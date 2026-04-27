//! Queue type definitions and endpoint trait for the Zato queue bridge.

/// Supported external queue systems that the bridge can connect to.
pub enum QueueType {
    /// Apache Kafka broker.
    Kafka,
}
