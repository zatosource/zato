//! Conversion of the JSON text carried in Redis stream fields into typed Rust structs.
//!
//! Redis stream fields hold text, so the Zato server and the queue bridge exchange their
//! commands as JSON, and something has to parse it. The project-wide ban on the `serde_json`
//! entry points exists to stop JSON being used as an intermediate format between Rust and
//! Python, where PyO3 `extract()` does the job directly. That does not apply here: this crate
//! is a standalone binary with no Python objects in reach, and JSON is the wire format itself
//! rather than a detour on the way to one.
//!
//! The exception is therefore granted once, in this module, so that command handlers stay free
//! of per-call-site suppressions and every payload is still deserialized into a named struct.

use serde::Deserialize;

// ################################################################################################################################

/// Parses one Redis stream payload into the struct the caller names.
///
/// # Errors
///
/// Returns an error when the payload is not valid JSON, or when it does not match the
/// shape of the target struct.
#[expect(clippy::disallowed_methods, reason = "JSON is the Redis stream wire format, see the module docs")]
pub fn parse_payload<'payload, T: Deserialize<'payload>>(payload: &'payload str) -> Result<T, serde_json::Error> {
    serde_json::from_str(payload)
}

// ################################################################################################################################
