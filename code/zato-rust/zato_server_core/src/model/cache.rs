use serde::{Deserialize, Serialize};
use super::defaults::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheBuiltinDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub is_default: bool,
    #[serde(default = "default_cache_type")]
    pub cache_type: String,
    #[serde(default = "default_cache_max_size")]
    pub max_size: u32,
    #[serde(default = "default_cache_max_item_size")]
    pub max_item_size: u32,
    #[serde(default = "default_true")]
    pub extend_expiry_on_get: bool,
    #[serde(default)]
    pub extend_expiry_on_set: bool,
    #[serde(default)]
    pub sync_method: Option<String>,
    #[serde(default)]
    pub persistent_storage: Option<String>,
}
