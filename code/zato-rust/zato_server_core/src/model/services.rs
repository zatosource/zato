//! Service metadata and Elasticsearch connection definitions.

use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true, default_slow_threshold, default_timeout};

/// Metadata for a deployed Zato service.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceInfo {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    /// Fully qualified Python class path (e.g. `zato.server.service.internal.ping.Ping`).
    #[serde(default)]
    pub impl_name: String,
    #[serde(default)]
    pub is_internal: bool,
    /// Invocation time in milliseconds above which the service is flagged as slow.
    #[serde(default = "default_slow_threshold")]
    pub slow_threshold: u32,
}

/// Outgoing Elasticsearch connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ElasticSearchDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    /// Space-separated list of Elasticsearch node URLs.
    #[serde(default)]
    pub hosts: String,
    #[serde(default = "default_timeout")]
    pub timeout: u32,
    /// How the request/response body is handled (e.g. `json`).
    #[serde(default)]
    pub body_as: String,
}
