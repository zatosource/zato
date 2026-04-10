use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// ── ID generation ──

pub fn next_id() -> String {
    let ts = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%S%.6f");
    let suffix: u32 = rand::random();
    format!("{}-{:08x}", ts, suffix)
}

// ── Security ──

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BasicAuthDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub realm: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiKeyDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NtlmDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OAuthDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub proto_version: String,
    #[serde(default)]
    pub sig_method: String,
    #[serde(default)]
    pub max_nonce_log: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BearerTokenDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub auth_endpoint: String,
    #[serde(default)]
    pub client_id_field: String,
    #[serde(default)]
    pub client_secret_field: String,
    #[serde(default)]
    pub grant_type: String,
    #[serde(default)]
    pub data_format: String,
}

// ── Groups ──

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityGroup {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub members: Vec<String>,
}

// ── Channels ──

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

// ── Outgoing connections ──

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

// ── Cache ──

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheBuiltinDef {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub is_default: bool,
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

// ── Email ──

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmailSmtp {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub port: u16,
    #[serde(default = "default_timeout")]
    pub timeout: u32,
    #[serde(default)]
    pub is_debug: bool,
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
    #[serde(default)]
    pub mode: String,
    #[serde(default)]
    pub ping_address: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmailImap {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub port: u16,
    #[serde(default = "default_timeout")]
    pub timeout: u32,
    #[serde(default)]
    pub debug_level: u32,
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
    #[serde(default)]
    pub mode: String,
    #[serde(default)]
    pub get_criteria: String,
}

// ── Scheduler ──

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedulerJob {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
    #[serde(default)]
    pub service: String,
    #[serde(default = "default_job_type")]
    pub job_type: String,
    #[serde(default)]
    pub start_date: String,
    #[serde(default)]
    pub extra: Option<String>,
    #[serde(default)]
    pub weeks: Option<u32>,
    #[serde(default)]
    pub days: Option<u32>,
    #[serde(default)]
    pub hours: Option<u32>,
    #[serde(default)]
    pub minutes: Option<u32>,
    #[serde(default)]
    pub seconds: Option<u32>,
    #[serde(default)]
    pub repeats: Option<u32>,
}

// ── Generic connections ──

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

// ── Pub/Sub ──

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubTopic {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub description: Option<String>,
    #[serde(default = "default_true")]
    pub is_active: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubPermission {
    #[serde(default = "next_id")]
    pub id: String,
    pub security: String,
    #[serde(default)]
    pub sec_base_id: String,
    #[serde(default)]
    pub pub_: Vec<String>,
    #[serde(rename = "pub", default)]
    pub pub_topics: Vec<String>,
    #[serde(rename = "sub", default)]
    pub sub_topics: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubSubscription {
    #[serde(default = "next_id")]
    pub id: String,
    pub security: String,
    #[serde(default)]
    pub delivery_type: String,
    #[serde(default)]
    pub topic_list: Vec<String>,
    #[serde(default)]
    pub push_rest_endpoint: Option<String>,
    #[serde(default)]
    pub push_service_name: Option<String>,
    #[serde(default)]
    pub max_retry_time: Option<String>,
}

// ── Search ──

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

// ── Services ──

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

// ── Channel AMQP ──

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

// ── Channel OpenAPI ──

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

// ── YAML top-level ──

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EnmasseConfig {
    #[serde(default)]
    pub security: Vec<SecurityDef>,
    #[serde(default)]
    pub groups: Vec<SecurityGroup>,
    #[serde(default)]
    pub channel_rest: Vec<ChannelRest>,
    #[serde(default)]
    pub outgoing_rest: Vec<OutgoingRest>,
    #[serde(default)]
    pub outgoing_soap: Vec<OutgoingSoap>,
    #[serde(default, alias = "outconn_soap")]
    pub outgoing_soap_alias: Vec<OutgoingSoap>,
    #[serde(default)]
    pub scheduler: Vec<SchedulerJob>,
    #[serde(default, alias = "outconn_sql")]
    pub sql: Vec<OutgoingSql>,
    #[serde(default, alias = "outgoing_ldap")]
    pub ldap: Vec<GenericConnection>,
    #[serde(default)]
    pub cache: Vec<CacheBuiltinDef>,
    #[serde(default)]
    pub email_smtp: Vec<EmailSmtp>,
    #[serde(default)]
    pub email_imap: Vec<EmailImap>,
    #[serde(default)]
    pub confluence: Vec<GenericConnection>,
    #[serde(default)]
    pub jira: Vec<GenericConnection>,
    #[serde(default)]
    pub microsoft_365: Vec<GenericConnection>,
    #[serde(default)]
    pub odoo: Vec<OutgoingOdoo>,
    #[serde(default)]
    pub elastic_search: Vec<ElasticSearchDef>,
    #[serde(default)]
    pub pubsub_topic: Vec<PubSubTopic>,
    #[serde(default)]
    pub pubsub_permission: Vec<PubSubPermission>,
    #[serde(default)]
    pub pubsub_subscription: Vec<PubSubSubscription>,
    #[serde(default)]
    pub channel_openapi: Vec<ChannelOpenApi>,
    #[serde(default)]
    pub zato_generic_connection: Vec<GenericConnection>,
}

// ── Security discriminator ──

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum SecurityDef {
    #[serde(rename = "basic_auth")]
    BasicAuth(BasicAuthDef),
    #[serde(rename = "apikey")]
    ApiKey(ApiKeyDef),
    #[serde(rename = "ntlm")]
    Ntlm(NtlmDef),
    #[serde(rename = "oauth")]
    OAuth(OAuthDef),
    #[serde(rename = "bearer_token")]
    BearerToken(BearerTokenDef),
}

impl SecurityDef {
    pub fn name(&self) -> &str {
        match self {
            SecurityDef::BasicAuth(d) => &d.name,
            SecurityDef::ApiKey(d) => &d.name,
            SecurityDef::Ntlm(d) => &d.name,
            SecurityDef::OAuth(d) => &d.name,
            SecurityDef::BearerToken(d) => &d.name,
        }
    }

    pub fn sec_type(&self) -> &str {
        match self {
            SecurityDef::BasicAuth(_) => "basic_auth",
            SecurityDef::ApiKey(_) => "apikey",
            SecurityDef::Ntlm(_) => "ntlm",
            SecurityDef::OAuth(_) => "oauth",
            SecurityDef::BearerToken(_) => "bearer_token",
        }
    }
}

// ── defaults ──

fn default_true() -> bool { true }
fn default_timeout() -> u32 { 10 }
fn default_pool_size() -> u16 { 20 }
fn default_pool_size_u32() -> u32 { 20 }
fn default_delivery_mode() -> String { "persistent".to_string() }
fn default_amqp_priority() -> u16 { 5 }
fn default_ftp_port() -> u16 { 21 }
fn default_odoo_port() -> u16 { 8069 }
fn default_cache_max_size() -> u32 { 10000 }
fn default_cache_max_item_size() -> u32 { 10000 }
fn default_job_type() -> String { "interval_based".to_string() }
fn default_slow_threshold() -> u32 { 99999 }
