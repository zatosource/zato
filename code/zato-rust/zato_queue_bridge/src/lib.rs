//! Queue bridge crate for Zato - connects external message queues (Kafka, SQS, IBM MQ)
//! to the Zato integration platform as a standalone binary communicating via Redis Streams.

/// Bridge state management, connection configs, and the Tokio-based bridge loop.
pub mod bridge;

/// IBM MQ consumer and producer wrappers.
#[cfg(feature = "ibm-mq")]
pub mod ibm_mq;

/// Kafka-specific consumer and producer wrappers.
#[cfg(feature = "kafka")]
pub mod kafka;

/// Pure-Rust parser for the IBM MQ MQRFH2 header.
pub mod rfh2;

/// Redis Streams integration for command ingestion and recv event publishing.
pub mod redis_streams;

/// HTTP query API served by actix-web for the Zato server to read connection state.
pub mod http_api;
