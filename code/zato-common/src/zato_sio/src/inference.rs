const BOOL_PREFIXES: &[&str] = &["by_", "has_", "is_", "may_", "needs_", "should_"];

const INT_SUFFIXES: &[&str] = &["_count", "_timeout"];

const SECRET_EXACT: &[&str] = &[
    "auth_data",
    "auth_token",
    "password",
    "password1",
    "password2",
    "secret_key",
    "tls_pem_passphrase",
    "token",
    "api_key",
    "apiKey",
    "xApiKey",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ElemType {
    Bool,
    Int,
    Secret,
    Text,
    AsIs,
}

pub fn infer_type(name: &str) -> ElemType {
    for prefix in BOOL_PREFIXES {
        if name.starts_with(prefix) {
            return ElemType::Bool;
        }
    }
    for suffix in INT_SUFFIXES {
        if name.ends_with(suffix) {
            return ElemType::Int;
        }
    }
    for exact in SECRET_EXACT {
        if name == *exact {
            return ElemType::Secret;
        }
    }
    ElemType::Text
}
