//! Routing of requests of REST channels, from the request context of the HTTP server to the service invocation.

/// Base64 decoding with the rules of `base64.b64decode` of Python.
pub mod base64;

/// Per-request checks of a matched channel and of its security definition.
pub mod checks;

/// Cross-origin resource sharing rules of REST channels.
pub mod cors;

/// JSON text parser with the grammar of `json.loads` of Python.
pub mod json_parse;

/// JSON text of scalar values as `json.dumps` of Python writes it.
pub mod json_text;

/// Bounded map that evicts the least recently used entry.
pub mod lru;

/// Match targets of REST channels and their compiled form.
pub mod matcher;

/// Canonical forms of request paths and Accept headers.
pub mod path;

/// Conversion between JSON text and Python objects.
pub mod py_json;

/// Router of REST channel requests.
pub mod router;

/// Checks of Basic Auth, API key and static bearer token credentials.
pub mod security;

/// Ordered table of REST channels.
pub mod table;
