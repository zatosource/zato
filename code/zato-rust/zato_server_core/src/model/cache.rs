//! Built-in cache configuration.

use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true, default_cache_type, default_cache_max_size, default_cache_max_item_size};

/// Configuration for a Zato built-in in-process cache.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[expect(clippy::struct_excessive_bools, reason = "mirrors the ODB schema which has four independent boolean flags")]
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
    /// Whether a `get` operation resets the entry's TTL.
    #[serde(default = "default_true")]
    pub extend_expiry_on_get: bool,
    /// Whether a `set` operation resets the entry's TTL.
    #[serde(default)]
    pub extend_expiry_on_set: bool,
    /// Cross-server cache synchronization method.
    #[serde(default)]
    pub sync_method: Option<String>,
    /// Backing store for cache persistence across restarts.
    #[serde(default)]
    pub persistent_storage: Option<String>,
}
