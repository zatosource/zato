//! Message types exchanged between Zato queue bridge components.

/// A message received from an external queue (e.g. Kafka topic) destined for a Zato service.
pub struct InboundMessage {
    /// Raw message payload bytes.
    pub payload: Vec<u8>,
    /// Source topic name from which the message was consumed.
    pub topic: String,
    /// Zato service name that should process this message.
    pub service_name: String,
}

/// A message to be published to an external queue via a named outgoing connection.
pub struct OutboundMessage {
    /// Name of the outgoing connection to publish through.
    pub conn_name: String,
    /// Raw message payload bytes.
    pub payload: Vec<u8>,
}
