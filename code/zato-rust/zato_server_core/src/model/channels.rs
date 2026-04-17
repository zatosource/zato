use serde::{Deserialize, Serialize};
use super::defaults::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelRest {
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
    #[serde(default)]
    pub host: Option<String>,
    #[serde(default)]
    pub merge_url_params_req: Option<bool>,
    #[serde(default)]
    pub url_params_pri: Option<String>,
    #[serde(default)]
    pub params_pri: Option<String>,
    #[serde(default)]
    pub cache_id: Option<String>,
    #[serde(default)]
    pub cache_name: Option<String>,
    #[serde(default)]
    pub cache_type: Option<String>,
    #[serde(default)]
    pub cache_expiry: Option<u32>,
    #[serde(default)]
    pub groups: Vec<String>,
    #[serde(default)]
    pub gateway_service_list: Vec<String>,
    #[serde(default)]
    pub is_internal: bool,
    #[serde(default)]
    pub match_slash: Option<bool>,
    #[serde(default)]
    pub http_accept: Option<String>,
}

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

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelAmqp {
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
    #[serde(default)]
    pub queue: String,
    #[serde(default)]
    pub consumer_tag_prefix: Option<String>,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    #[serde(default)]
    pub ack_mode: String,
    #[serde(default)]
    pub prefetch_count: u32,
    #[serde(default)]
    pub data_format: Option<String>,
    #[serde(default)]
    pub service: String,
    #[serde(default)]
    pub frame_max: Option<u32>,
    #[serde(default)]
    pub heartbeat: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelOpenApi {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub url_path: String,
    #[serde(default)]
    pub rest_channel_list: Vec<String>,
}
