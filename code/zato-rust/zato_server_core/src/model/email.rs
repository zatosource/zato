use serde::{Deserialize, Serialize};
use super::defaults::*;

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
