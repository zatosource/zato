pub fn default_true() -> bool { true }
pub fn default_timeout() -> u32 { 10 }
pub fn default_pool_size() -> u16 { 20 }
pub fn default_pool_size_u32() -> u32 { 20 }
pub fn default_delivery_mode() -> String { "persistent".to_string() }
pub fn default_amqp_priority() -> u16 { 5 }
pub fn default_ftp_port() -> u16 { 21 }
pub fn default_odoo_port() -> u16 { 8069 }
pub fn default_cache_max_size() -> u32 { 10000 }
pub fn default_cache_max_item_size() -> u32 { 10000 }
pub fn default_cache_type() -> String { "builtin".to_string() }
pub fn default_job_type() -> String { "interval_based".to_string() }
pub fn default_slow_threshold() -> u32 { 99999 }

pub fn next_id() -> String {
    let ts = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%S%.6f");
    let suffix: u32 = rand::random();
    format!("{}-{:08x}", ts, suffix)
}
