use serde::{Deserialize, Serialize};
use super::defaults::*;

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
    #[serde(default)]
    pub extra_fields: Vec<String>,
}

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
            Self::BasicAuth(d) => &d.name,
            Self::ApiKey(d) => &d.name,
            Self::Ntlm(d) => &d.name,
            Self::OAuth(d) => &d.name,
            Self::BearerToken(d) => &d.name,
        }
    }

    pub fn sec_type(&self) -> &str {
        match self {
            Self::BasicAuth(_) => "basic_auth",
            Self::ApiKey(_) => "apikey",
            Self::Ntlm(_) => "ntlm",
            Self::OAuth(_) => "oauth",
            Self::BearerToken(_) => "bearer_token",
        }
    }

    pub fn username(&self) -> &str {
        match self {
            Self::BasicAuth(d) => &d.username,
            Self::ApiKey(d) => &d.username,
            Self::Ntlm(d) => &d.username,
            Self::OAuth(d) => &d.username,
            Self::BearerToken(d) => &d.username,
        }
    }

    pub fn password(&self) -> &str {
        match self {
            Self::BasicAuth(d) => &d.password,
            Self::ApiKey(d) => &d.password,
            Self::Ntlm(d) => &d.password,
            Self::OAuth(d) => &d.password,
            Self::BearerToken(d) => &d.password,
        }
    }

    pub fn id(&self) -> &str {
        match self {
            Self::BasicAuth(d) => &d.id,
            Self::ApiKey(d) => &d.id,
            Self::Ntlm(d) => &d.id,
            Self::OAuth(d) => &d.id,
            Self::BearerToken(d) => &d.id,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityGroup {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub members: Vec<String>,
}
