//! Data model for Zato's enmasse YAML configuration system.
//!
//! Each submodule defines the Rust-side schema for a category of Zato objects (channels, security,
//! outgoing connections, etc.) that users declare in YAML and deploy as a single unit.

/// Serde default-value functions used across all enmasse structs.
pub mod defaults;

/// Security definitions - basic auth, API keys, NTLM, bearer tokens and security groups.
pub mod security;

/// Inbound channel definitions - REST, SOAP, AMQP and OpenAPI.
pub mod channels;

/// Outgoing connection definitions - REST, SOAP, AMQP, FTP, SQL, Odoo and SAP.
pub mod outgoing;

/// Scheduler job definitions with timezone handling and holiday calendars.
pub mod scheduler;

/// Publish/subscribe messaging - topics, permissions and subscriptions.
pub mod pubsub;

/// Service metadata and Elasticsearch connection definitions.
pub mod services;

/// Built-in cache configuration.
pub mod cache;

/// Email connection definitions - SMTP for sending, IMAP for receiving.
pub mod email;

/// Generic connection type for connectors without a dedicated struct (Confluence, JIRA, Microsoft 365, LDAP, etc.).
pub mod generic;

/// Top-level enmasse configuration that aggregates all object types into a single deployable unit.
pub mod enmasse;

pub use defaults::next_id;
pub use security::{BasicAuthDef, ApiKeyDef, NtlmDef, BearerTokenDef, SecurityDef, SecurityGroup};
pub use channels::{ChannelRest, ChannelSoap, ChannelAmqp, ChannelOpenApi};
pub use outgoing::{OutgoingRest, OutgoingSoap, OutgoingAmqp, OutgoingFtp, OutgoingSql, OutgoingOdoo, OutgoingSap};
pub use scheduler::{SchedulerJob, HolidayCalendar};
pub use pubsub::{PubSubTopic, PubSubPermission, PubSubSubscription};
pub use services::{ServiceInfo, ElasticSearchDef};
pub use cache::CacheBuiltinDef;
pub use email::{EmailSmtp, EmailImap};
pub use generic::GenericConnection;
pub use enmasse::EnmasseConfig;
