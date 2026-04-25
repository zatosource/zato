//! Email connection definitions - SMTP for sending, IMAP for receiving.

use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true, default_timeout};

/// Outgoing SMTP connection for sending email.
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
    /// TLS mode (e.g. `starttls`, `ssl`).
    #[serde(default)]
    pub mode: String,
    /// Email address used for SMTP connection health checks.
    #[serde(default)]
    pub ping_address: String,
}

/// IMAP connection for receiving email.
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
    /// IMAP protocol debug verbosity level.
    #[serde(default)]
    pub debug_level: u32,
    #[serde(default)]
    pub username: Option<String>,
    #[serde(default)]
    pub password: Option<String>,
    /// TLS mode.
    #[serde(default)]
    pub mode: String,
    /// IMAP SEARCH criteria for message retrieval.
    #[serde(default)]
    pub get_criteria: String,
}
