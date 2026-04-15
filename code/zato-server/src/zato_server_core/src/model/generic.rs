use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use super::defaults::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GenericConnection {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
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
    #[serde(default)]
    pub server_list: String,

    #[serde(default)]
    pub client_id: String,
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

    #[serde(default)]
    pub opaque: HashMap<String, serde_yaml::Value>,
}
