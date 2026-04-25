//! Security definitions for Zato's enmasse configuration.

use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true};

/// HTTP Basic Authentication credentials.
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
    /// HTTP realm sent in the `WWW-Authenticate` challenge header.
    #[serde(default)]
    pub realm: String,
}

/// API key authentication - `username` is the header/query parameter name, `password` is the key value.
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

/// NTLM authentication credentials.
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

/// OAuth 2.0 Bearer Token configuration - acquires tokens from an authorization server.
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
    /// Token endpoint URL of the OAuth authorization server.
    #[serde(default)]
    pub auth_server_url: String,
    /// Form field name that carries the client ID in the token request.
    #[serde(default)]
    pub client_id_field: String,
    /// Form field name that carries the client secret in the token request.
    #[serde(default)]
    pub client_secret_field: String,
    /// OAuth grant type (e.g. `client_credentials`).
    #[serde(default)]
    pub grant_type: String,
    /// Encoding for the token request body - selects JSON vs form encoding.
    #[serde(default)]
    pub data_format: String,
    /// Space-separated OAuth scopes requested in the token call.
    #[serde(default)]
    pub scopes: String,
    /// Additional key=value fields merged into the token request body.
    #[serde(default)]
    pub extra_fields: String,
}

/// Tagged enum that dispatches across all supported security types.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum SecurityDef {
    #[serde(rename = "basic_auth")]
    BasicAuth(BasicAuthDef),
    #[serde(rename = "apikey")]
    ApiKey(ApiKeyDef),
    #[serde(rename = "ntlm")]
    Ntlm(NtlmDef),
    #[serde(rename = "bearer_token")]
    BearerToken(BearerTokenDef),
}

impl SecurityDef {
    /// Returns the human-readable name regardless of the underlying type.
    pub fn name(&self) -> &str {
        match self {
            Self::BasicAuth(def) => &def.name,
            Self::ApiKey(def) => &def.name,
            Self::Ntlm(def) => &def.name,
            Self::BearerToken(def) => &def.name,
        }
    }

    /// Returns the wire-format type tag (e.g. `"basic_auth"`, `"apikey"`).
    pub const fn sec_type(&self) -> &str {
        match self {
            Self::BasicAuth(_) => "basic_auth",
            Self::ApiKey(_) => "apikey",
            Self::Ntlm(_) => "ntlm",
            Self::BearerToken(_) => "bearer_token",
        }
    }

    /// Returns the login username.
    pub fn username(&self) -> &str {
        match self {
            Self::BasicAuth(def) => &def.username,
            Self::ApiKey(def) => &def.username,
            Self::Ntlm(def) => &def.username,
            Self::BearerToken(def) => &def.username,
        }
    }

    /// Returns the password or key value.
    pub fn password(&self) -> &str {
        match self {
            Self::BasicAuth(def) => &def.password,
            Self::ApiKey(def) => &def.password,
            Self::Ntlm(def) => &def.password,
            Self::BearerToken(def) => &def.password,
        }
    }

    /// Returns the unique identifier.
    pub fn id(&self) -> &str {
        match self {
            Self::BasicAuth(def) => &def.id,
            Self::ApiKey(def) => &def.id,
            Self::Ntlm(def) => &def.id,
            Self::BearerToken(def) => &def.id,
        }
    }
}

/// A named group that bundles multiple security definitions for channel assignment.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityGroup {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    /// Names of the security definitions belonging to this group.
    #[serde(default)]
    pub members: Vec<String>,
}
