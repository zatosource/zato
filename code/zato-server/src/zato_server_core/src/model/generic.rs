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
    pub address: Option<String>,
    #[serde(default)]
    pub port: Option<u16>,
    #[serde(default)]
    pub timeout: Option<u32>,
    #[serde(default)]
    pub data_format: Option<String>,
    #[serde(default)]
    pub version: Option<String>,
    #[serde(default)]
    pub extra: Option<String>,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub secret: Option<String>,
    #[serde(default)]
    pub cache_expiry: Option<u32>,
    #[serde(default, rename = "security_name", alias = "security")]
    pub security_name: Option<String>,
    #[serde(default)]
    pub opaque: HashMap<String, serde_yaml::Value>,
}
