//! Inbound channel definitions - how external clients connect to Zato services.

use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true, default_pool_size_u32};

/// REST HTTP channel - maps a URL path + method to a Zato service.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelRest {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    /// Zato service invoked when a request hits this channel.
    #[serde(default)]
    pub service: String,
    #[serde(default)]
    pub url_path: String,
    #[serde(default, rename = "security_name", alias = "security")]
    pub security_name: Option<String>,
    #[serde(default)]
    pub security_id: Option<String>,
    #[serde(default)]
    pub sec_type: Option<String>,
    #[serde(default)]
    pub data_format: Option<String>,
    #[serde(default)]
    pub method: Option<String>,
    #[serde(default)]
    pub content_type: Option<String>,
    #[serde(default)]
    pub content_encoding: Option<String>,
    /// Carried on the channel record, not used in REST dispatch.
    #[serde(default)]
    pub host: Option<String>,
    /// Whether to merge URL path parameters into the request payload.
    #[serde(default)]
    pub merge_url_params_req: Option<bool>,
    /// Priority of URL parameters vs query string when merging.
    #[serde(default)]
    pub url_params_pri: Option<String>,
    /// Priority when merging different parameter sources for the service payload.
    #[serde(default)]
    pub params_pri: Option<String>,
    #[serde(default)]
    pub cache_id: Option<String>,
    #[serde(default)]
    pub cache_name: Option<String>,
    #[serde(default)]
    pub cache_type: Option<String>,
    /// Cache TTL in seconds for response caching.
    #[serde(default)]
    pub cache_expiry: Option<u32>,
    /// Security groups assigned to this channel.
    #[serde(default)]
    pub groups: Vec<String>,
    /// Whitelist of service names callable through this channel when used as an API gateway.
    #[serde(default)]
    pub gateway_service_list: Vec<String>,
    #[serde(default)]
    pub is_internal: bool,
    /// Whether trailing slashes matter for URL pattern matching.
    #[serde(default)]
    pub match_slash: Option<bool>,
    /// Binds this channel to a specific `Accept` header value for content negotiation.
    #[serde(default)]
    pub http_accept: Option<String>,
}

/// SOAP channel - maps a URL path + SOAP action to a Zato service.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelSoap {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub service: String,
    #[serde(default)]
    pub url_path: String,
    #[serde(default, rename = "security_name", alias = "security")]
    pub security_name: Option<String>,
    #[serde(default)]
    pub soap_action: String,
    #[serde(default)]
    pub soap_version: Option<String>,
    #[serde(default)]
    pub data_format: Option<String>,
    #[serde(default)]
    pub is_internal: bool,
}

/// AMQP consumer channel - binds a queue to a Zato service.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelAmqp {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    /// AMQP broker address (host:port or amqp:// URL).
    #[serde(default)]
    pub address: String,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    /// Queue name to consume from.
    #[serde(default)]
    pub queue: String,
    /// Prefix for the AMQP consumer tag.
    #[serde(default)]
    pub consumer_tag_prefix: Option<String>,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    /// Acknowledgement mode for consumed messages.
    #[serde(default)]
    pub ack_mode: String,
    /// AMQP `QoS` prefetch count.
    #[serde(default)]
    pub prefetch_count: u32,
    #[serde(default)]
    pub data_format: Option<String>,
    #[serde(default)]
    pub service: String,
    /// Maximum AMQP frame size in bytes.
    #[serde(default)]
    pub frame_max: Option<u32>,
    /// AMQP heartbeat interval in seconds.
    #[serde(default)]
    pub heartbeat: Option<u32>,
}

/// `OpenAPI` channel - groups multiple REST channels under a single spec.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelOpenApi {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub url_path: String,
    /// Names of REST channels that this `OpenAPI` spec covers.
    #[serde(default)]
    pub rest_channel_list: Vec<String>,
}
