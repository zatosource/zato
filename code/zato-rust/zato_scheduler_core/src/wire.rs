// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Conversion between the JSON text carried in Redis stream fields and typed Rust structs.
//!
//! Redis stream fields hold text, so the Zato server and the scheduler exchange their commands
//! and events as JSON, and something has to encode and parse it. The project-wide ban on the
//! `serde_json` entry points exists to stop JSON being used as an intermediate format between
//! Rust and Python, where PyO3 `extract()` does the job directly. That does not apply here: the
//! scheduler is a standalone process with no Python objects in reach, and JSON is the wire
//! format itself rather than a detour on the way to one.
//!
//! The exception is therefore granted twice, in this module, so that command handlers stay free
//! of per-call-site suppressions and every payload still travels as a named struct.

use serde::{Deserialize, Serialize};

// ################################################################################################################################

/// Parses one Redis stream payload into the struct the caller names.
///
/// # Errors
///
/// Returns an error when the payload is not valid JSON, or when it does not match the shape
/// of the target struct.
#[expect(clippy::disallowed_methods, reason = "JSON is the Redis stream wire format, see the module docs")]
pub fn parse_payload<'payload, T: Deserialize<'payload>>(payload: &'payload str) -> Result<T, serde_json::Error> {
    serde_json::from_str(payload)
}

// ################################################################################################################################

/// Parses a JSON response body into the struct the caller names.
///
/// # Errors
///
/// Returns an error when the body is not valid JSON, or when it does not match the shape
/// of the target struct.
#[expect(clippy::disallowed_methods, reason = "JSON is the HTTP API wire format, see the module docs")]
pub fn parse_body<'body, T: Deserialize<'body>>(body: &'body [u8]) -> Result<T, serde_json::Error> {
    serde_json::from_slice(body)
}

// ################################################################################################################################

/// Renders a value as the JSON text that goes into a Redis stream field.
///
/// # Errors
///
/// Returns an error when the value cannot be represented as JSON, which for the structs in
/// this crate means a map with non-string keys or a float that is not a number.
#[expect(clippy::disallowed_methods, reason = "JSON is the Redis stream wire format, see the module docs")]
pub fn render_payload<T: Serialize>(value: &T) -> Result<String, serde_json::Error> {
    serde_json::to_string(value)
}

// ################################################################################################################################
