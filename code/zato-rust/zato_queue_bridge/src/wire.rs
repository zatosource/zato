//! Conversion between the text carried in Redis stream fields and typed Rust values.
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
//!
//! Binary payloads travel through the same text fields as base64, encoded and decoded here too.

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

/// Serializes header pairs into the JSON object string carried in recv events.
pub fn headers_to_json(headers: &[(String, String)]) -> String {
    let mut map = serde_json::Map::with_capacity(headers.len());
    for (key, value) in headers {
        let _ = map.insert(key.clone(), serde_json::Value::String(value.clone()));
    }

    serde_json::Value::Object(map).to_string()
}

// ################################################################################################################################

/// The base64 alphabet, indexed by the value of one six-bit group.
const BASE64_ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

/// Keeps only the six bits one base64 character encodes.
const SIX_BIT_MASK: u32 = 0x3F;

/// Keeps only the eight bits one decoded byte holds.
const BYTE_MASK: u32 = 0xFF;

/// Number of input bytes encoded by one group of four base64 characters.
const BYTES_PER_GROUP: usize = 3;

/// Number of base64 characters produced per group of input bytes.
const CHARS_PER_GROUP: usize = 4;

/// Maps one six-bit group onto its base64 character.
fn base64_char(group: u32) -> char {
    // The mask keeps the index inside the 64-entry alphabet, so the lookup always hits.
    let index = usize::try_from(group & SIX_BIT_MASK).unwrap_or(0);
    BASE64_ALPHABET.get(index).copied().map_or('=', char::from)
}

/// Takes the low eight bits of a decoded group as one output byte.
fn base64_byte(group: u32) -> u8 {
    // The mask leaves a value that always fits in a byte.
    u8::try_from(group & BYTE_MASK).unwrap_or(0)
}

/// Simple base64 encoder for binary payloads in Redis stream fields.
pub fn base64_encode(data: &[u8]) -> String {
    let mut result = String::with_capacity(data.len().div_ceil(BYTES_PER_GROUP) * CHARS_PER_GROUP);

    for chunk in data.chunks(BYTES_PER_GROUP) {
        // Bytes missing from a trailing partial chunk count as zero, which is what
        // the padding characters below stand for.
        let first = u32::from(chunk.first().copied().unwrap_or(0));
        let second = u32::from(chunk.get(1).copied().unwrap_or(0));
        let third = u32::from(chunk.get(2).copied().unwrap_or(0));

        let triple = (first << 16) | (second << 8) | third;

        result.push(base64_char(triple >> 18));
        result.push(base64_char(triple >> 12));

        if chunk.len() > 1 {
            result.push(base64_char(triple >> 6));
        } else {
            result.push('=');
        }

        if chunk.len() > 2 {
            result.push(base64_char(triple));
        } else {
            result.push('=');
        }
    }

    result
}

/// Simple base64 decoder for binary payloads from Redis stream fields.
pub fn base64_decode(encoded: &str) -> Vec<u8> {
    const fn decode_char(chr: u8) -> Option<u8> {
        match chr {
            b'A'..=b'Z' => Some(chr - b'A'),
            b'a'..=b'z' => Some(chr - b'a' + 26),
            b'0'..=b'9' => Some(chr - b'0' + 52),
            b'+' => Some(62),
            b'/' => Some(63),
            _ => None,
        }
    }

    let bytes: Vec<u8> = encoded.bytes().filter(|&byte| byte != b'=').collect();
    let mut result = Vec::with_capacity(bytes.len() * BYTES_PER_GROUP / CHARS_PER_GROUP);

    for chunk in bytes.chunks(CHARS_PER_GROUP) {
        let mut buf: u32 = 0;
        let mut count: u32 = 0;

        for &byte in chunk {
            if let Some(val) = decode_char(byte) {
                buf = (buf << 6) | u32::from(val);
                count += 1;
            }
        }

        // A single character carries too few bits to yield a byte, so such a group is dropped.
        if count >= 2 {
            // A partial group is left-aligned first, so its bits sit where a full group's would.
            let shift = (4 - count) * 6;
            buf <<= shift;

            result.push(base64_byte(buf >> 16));

            if count >= 3 {
                result.push(base64_byte(buf >> 8));
            }

            if count >= 4 {
                result.push(base64_byte(buf));
            }
        }
    }

    result
}

// ################################################################################################################################
