use serde::{Deserialize, Serialize};
use super::defaults::*;

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
    #[serde(default)]
    pub ping_method: Option<String>,
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
    #[serde(default)]
    pub is_wrapper: bool,
    #[serde(default)]
    pub wrapper_type: Option<String>,
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
}

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
    #[serde(default = "default_delivery_mode")]
    pub delivery_mode: String,
    #[serde(default = "default_amqp_priority")]
    pub priority: u16,
    #[serde(default)]
    pub content_type: Option<String>,
    #[serde(default)]
    pub content_encoding: Option<String>,
    #[serde(default)]
    pub expiration: Option<u32>,
    #[serde(default)]
    pub user_id: Option<String>,
    #[serde(default)]
    pub app_id: Option<String>,
    #[serde(default = "default_pool_size")]
    pub pool_size: u16,
    #[serde(default)]
    pub frame_max: Option<u32>,
    #[serde(default)]
    pub heartbeat: Option<u32>,
}

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
    #[serde(default)]
    pub acct: Option<String>,
    #[serde(default)]
    pub timeout: Option<u32>,
    #[serde(default = "default_ftp_port")]
    pub port: u16,
    #[serde(default)]
    pub dircache: bool,
}

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
    #[serde(default)]
    pub engine: String,
    #[serde(rename = "type", default)]
    pub engine_type: Option<String>,
    #[serde(default)]
    pub extra: Option<String>,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
}

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
    #[serde(default)]
    pub protocol: String,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub client_type: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutgoingSap {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub sysnr: Option<String>,
    #[serde(default)]
    pub user: String,
    #[serde(default)]
    pub client: String,
    #[serde(default)]
    pub sysid: String,
    #[serde(default)]
    pub password: String,
    #[serde(default = "default_pool_size_u32")]
    pub pool_size: u32,
    #[serde(default)]
    pub router: Option<String>,
}
