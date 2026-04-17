use serde::{Deserialize, Serialize};
use super::defaults::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceInfo {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub impl_name: String,
    #[serde(default)]
    pub is_internal: bool,
    #[serde(default = "default_slow_threshold")]
    pub slow_threshold: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ElasticSearchDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub hosts: String,
    #[serde(default = "default_timeout")]
    pub timeout: u32,
    #[serde(default)]
    pub body_as: String,
}
