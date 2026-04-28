//! Utility functions shared across the crate.

/// Generates a unique correlation ID.
///
/// Combines a UTC timestamp with a random hex suffix.
pub fn next_id() -> String {
    let timestamp = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%S%.6f");
    let suffix: u32 = rand::random();
    format!("{timestamp}-{suffix:08x}")
}
