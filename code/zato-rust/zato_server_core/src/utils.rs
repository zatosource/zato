//! Utility functions shared across the crate.

use jiff::Timestamp;

/// UTC time part of a correlation ID, with microseconds.
const ID_TIMESTAMP_FORMAT: &str = "%Y-%m-%dT%H:%M:%S%.6f";

/// Generates a unique correlation ID.
///
/// Combines a UTC timestamp with a random hex suffix.
pub fn next_id() -> String {
    let timestamp = Timestamp::now().strftime(ID_TIMESTAMP_FORMAT);
    let suffix: u32 = rand::random();
    format!("{timestamp}-{suffix:08x}")
}
