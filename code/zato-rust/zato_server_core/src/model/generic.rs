//! Generic connection type for connectors without a dedicated struct
//! (Confluence, JIRA, Microsoft 365, LDAP, etc.).

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true, default_pool_size_u32};

/// A catch-all connection definition whose `type_` field discriminates the connector kind.
///
/// Fields not applicable to a given type are left at their defaults; connector-specific
/// extras go into the `opaque` map and are persisted as JSON in the ODB.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[expect(clippy::struct_excessive_bools, reason = "mirrors the ODB schema which has independent boolean flags per connector type")]
pub struct GenericConnection {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    /// Connector type constant (e.g. `outconn-ldap`, `outconn-confluence`).
    #[serde(default)]
    pub type_: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub is_internal: bool,
    #[serde(default)]
    pub is_channel: bool,
    #[serde(default)]
    pub is_outconn: bool,
    #[serde(default)]
    pub address: String,
    #[serde(default)]
    pub port: u16,
    #[serde(default)]
    pub timeout: u32,
    #[serde(default)]
    pub data_format: String,
    #[serde(default)]
    pub version: String,
    #[serde(default)]
    pub extra: String,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub secret: String,
    #[serde(default)]
    pub cache_expiry: u32,
    #[serde(default, alias = "security")]
    pub security_name: String,

    #[serde(default)]
    pub auth_type: String,
    /// Comma or newline-separated list of server addresses (e.g. for LDAP).
    #[serde(default)]
    pub server_list: String,

    /// OAuth/Microsoft 365 application (client) ID.
    #[serde(default)]
    pub client_id: String,
    /// OAuth/Microsoft 365 directory (tenant) ID.
    #[serde(default)]
    pub tenant_id: String,
    #[serde(default)]
    pub scopes: String,
    #[serde(default)]
    pub secret_value: String,

    #[serde(default)]
    pub api_version: String,
    #[serde(default)]
    pub is_cloud: bool,
    #[serde(default)]
    pub site_url: String,
    #[serde(default)]
    pub recv_timeout: u32,

    /// Connector-specific configuration that varies by connection type, persisted as JSON in the ODB.
    #[serde(default)]
    pub opaque: HashMap<String, String>,
}
