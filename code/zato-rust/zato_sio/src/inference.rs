/// Name prefixes that indicate a boolean SIO element (e.g. `is_active`, `has_data`).
const BOOL_PREFIXES: &[&str] = &["by_", "has_", "is_", "may_", "needs_", "should_"];

/// Name suffixes that indicate an integer SIO element (e.g. `retry_count`, `read_timeout`).
const INT_SUFFIXES: &[&str] = &["_count", "_timeout"];

/// Exact element names that are always treated as secrets.
const SECRET_EXACT: &[&str] = &[
    "auth_data",
    "auth_token",
    "password",
    "secret_key",
    "tls_pem_passphrase",
    "token",
    "api_key",
    "apiKey",
    "xApiKey",
];

/// The type of a SimpleIO element, inferred from its name or declared explicitly.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ElemType {
    /// Boolean value (Python `bool`).
    Bool,
    /// Integer value (Python `int`).
    Int,
    /// Secret value - masked in logs and responses.
    Secret,
    /// Free-form text (Python `str`), the default.
    Text,
    /// Pass-through with no conversion applied.
    AsIs,
}

/// Infers the SIO element type from its name using prefix, suffix, and exact-match rules.
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
