//! Serde default-value functions for the enmasse YAML configuration system.
//! Each function provides a fallback value used when the corresponding field is omitted from input.

/// Default number of connections in a pool, shared by u16 and u32 variants.
const POOL_SIZE: u16 = 20;

/// Serde default for `is_active` fields - connections are active by default.
pub const fn default_true() -> bool { true }

/// Serde default for connection timeout in seconds.
pub const fn default_timeout() -> u32 { 10 }

/// Serde default for connection pool size (u16).
pub const fn default_pool_size() -> u16 { POOL_SIZE }

/// Serde default for connection pool size (u32).
#[expect(clippy::as_conversions, reason = "POOL_SIZE is a small constant that fits in u32")]
pub const fn default_pool_size_u32() -> u32 { POOL_SIZE as u32 }

/// Serde default for AMQP delivery mode - persistent delivery survives broker restarts.
pub fn default_delivery_mode() -> String { "persistent".to_string() }

/// Serde default for AMQP message priority (mid-range on the 0-9 scale).
pub const fn default_amqp_priority() -> u16 { 5 }

/// Serde default for FTP control port.
pub const fn default_ftp_port() -> u16 { 21 }

/// Serde default for Odoo XML-RPC port.
pub const fn default_odoo_port() -> u16 { 8069 }

/// Serde default for maximum cache entries.
pub const fn default_cache_max_size() -> u32 { 10000 }

/// Serde default for maximum single cache entry size in bytes.
pub const fn default_cache_max_item_size() -> u32 { 10000 }

/// Serde default for cache backend type.
pub fn default_cache_type() -> String { "builtin".to_string() }

/// Serde default for scheduler job type.
pub fn default_job_type() -> String { "interval_based".to_string() }

/// Serde default for slow-response threshold in milliseconds (effectively disabled at ~100 seconds).
pub const fn default_slow_threshold() -> u32 { 99999 }

/// Generates a unique ID by combining the current UTC timestamp with a random hex suffix.
pub fn next_id() -> String {
    let timestamp = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%S%.6f");
    let suffix: u32 = rand::random();
    format!("{timestamp}-{suffix:08x}")
}
