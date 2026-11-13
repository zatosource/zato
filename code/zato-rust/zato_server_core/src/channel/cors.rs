//! Cross-origin resource sharing rules of REST channels, as `zato.server.connection.http_soap.cors` defines them.

/// Origins accepted as they are.
const ALLOWED_ORIGINS: [&str; 3] = ["https://zato.io", "http://localhost", "http://127.0.0.1"];

/// Prefixes of origins accepted on any port.
const ALLOWED_ORIGIN_PREFIXES: [&str; 2] = ["http://localhost:", "http://127.0.0.1:"];

/// Header that names the origin a response is shared with.
pub const HEADER_ALLOW_ORIGIN: &str = "Access-Control-Allow-Origin";

/// Header that names the response headers a page may read.
pub const HEADER_EXPOSE_HEADERS: &str = "Access-Control-Expose-Headers";

/// Response headers a page may read.
pub const EXPOSE_HEADERS: &str = "Mcp-Session-Id";

/// Headers of a preflight response other than the origin, in the order they are set.
pub const PREFLIGHT_HEADERS: [(&str, &str); 3] = [
    ("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS"),
    (
        "Access-Control-Allow-Headers",
        "X-API-Key, Authorization, Content-Type, Mcp-Session-Id, MCP-Protocol-Version, Mcp-Method, Mcp-Name, Last-Event-ID",
    ),
    ("Access-Control-Max-Age", "86400"),
];

/// Whether an Origin header value is one that cross-origin requests are accepted from.
pub fn is_allowed_origin(origin: &str) -> bool {
    ALLOWED_ORIGINS.contains(&origin) || ALLOWED_ORIGIN_PREFIXES.iter().any(|prefix| origin.starts_with(prefix))
}
