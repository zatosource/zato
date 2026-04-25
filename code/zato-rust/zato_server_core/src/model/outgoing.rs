//! Outgoing connection definitions - how Zato connects to external systems.

use serde::{Deserialize, Serialize};
use super::defaults::{
    next_id, default_true, default_timeout, default_delivery_mode,
    default_amqp_priority, default_pool_size, default_ftp_port,
    default_pool_size_u32, default_odoo_port,
};

/// Outgoing REST connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingRest {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub url_path: String,
    #[serde(default, rename = "security_name", alias = "security")]
    pub security_name: Option<String>,
    #[serde(default)]
    pub data_format: Option<String>,
    #[serde(default = "default_timeout")]
    pub timeout: u32,
    #[serde(default)]
    pub method: Option<String>,
    #[serde(default)]
    pub content_type: Option<String>,
    #[serde(default)]
    pub content_encoding: Option<String>,
    #[serde(default)]
    pub pool_size: Option<u32>,
    /// HTTP method used for health/ping checks.
    #[serde(default)]
    pub ping_method: Option<String>,
    /// Controls response body handling (e.g. string vs bytes).
    #[serde(default)]
    pub serialization_type: Option<String>,
    #[serde(default)]
    pub merge_url_params_req: Option<bool>,
    #[serde(default)]
    pub url_params_pri: Option<String>,
    #[serde(default)]
    pub params_pri: Option<String>,
    #[serde(default)]
    pub tls_verify: Option<bool>,
    #[serde(default)]
    pub is_internal: bool,
    /// Whether this is a virtual wrapper grouping of outgoing REST connections.
    #[serde(default)]
    pub is_wrapper: bool,
    /// Discriminator for wrapper-grouped definitions.
    #[serde(default)]
    pub wrapper_type: Option<String>,
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
}

/// Outgoing SOAP connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingSoap {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub url_path: String,
    #[serde(default, rename = "security_name", alias = "security")]
    pub security_name: Option<String>,
    #[serde(default)]
    pub soap_action: String,
    #[serde(default)]
    pub soap_version: Option<String>,
    #[serde(default = "default_timeout")]
    pub timeout: u32,
    #[serde(default)]
    pub tls_verify: Option<bool>,
    #[serde(default)]
    pub is_internal: bool,
}

/// Outgoing AMQP producer connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingAmqp {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub address: String,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    /// `persistent` or `non-persistent` - mapped to AMQP delivery mode integers at runtime.
    #[serde(default = "default_delivery_mode")]
    pub delivery_mode: String,
    /// AMQP message priority (0-9).
    #[serde(default = "default_amqp_priority")]
    pub priority: u16,
    #[serde(default)]
    pub content_type: Option<String>,
    #[serde(default)]
    pub content_encoding: Option<String>,
    /// Message TTL in milliseconds.
    #[serde(default)]
    pub expiration: Option<u32>,
    /// AMQP `user-id` message property.
    #[serde(default)]
    pub user_id: Option<String>,
    /// AMQP `app-id` message property.
    #[serde(default)]
    pub app_id: Option<String>,
    #[serde(default = "default_pool_size")]
    pub pool_size: u16,
    #[serde(default)]
    pub frame_max: Option<u32>,
    #[serde(default)]
    pub heartbeat: Option<u32>,
}

/// Outgoing FTP connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingFtp {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub user: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
    /// FTP ACCT command value.
    #[serde(default)]
    pub acct: Option<String>,
    #[serde(default)]
    pub timeout: Option<u32>,
    #[serde(default = "default_ftp_port")]
    pub port: u16,
    /// Whether to enable directory listing caching.
    #[serde(default)]
    pub dircache: bool,
}

/// Outgoing SQL connection pool.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingSql {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub port: u16,
    #[serde(default)]
    pub db_name: String,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    /// Full `SQLAlchemy` engine string (e.g. `postgresql+pg8000`).
    #[serde(default)]
    pub engine: String,
    /// Logical DB family name from YAML (e.g. `postgresql`) - mapped to `engine` at import time.
    #[serde(rename = "type", default)]
    pub engine_type: Option<String>,
    #[serde(default)]
    pub extra: Option<String>,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
}

/// Outgoing Odoo XML-RPC connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingOdoo {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default = "default_odoo_port")]
    pub port: u16,
    #[serde(default)]
    pub user: String,
    #[serde(default)]
    pub database: String,
    /// XML-RPC or JSON-RPC.
    #[serde(default)]
    pub protocol: String,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub client_type: Option<String>,
}

/// Outgoing SAP RFC connection.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingSap {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    /// SAP system number - part of the RFC connection URL.
    #[serde(default)]
    pub sysnr: Option<String>,
    #[serde(default)]
    pub user: String,
    /// SAP client number.
    #[serde(default)]
    pub client: String,
    /// SAP system ID.
    #[serde(default)]
    pub sysid: String,
    #[serde(default)]
    pub password: String,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    /// SAP router string for connections through a `SAProuter`.
    #[serde(default)]
    pub router: Option<String>,
}
