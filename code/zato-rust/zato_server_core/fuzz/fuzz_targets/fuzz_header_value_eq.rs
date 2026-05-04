#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::http::io::{header_value_eq, trim_ows};

fuzz_target!(|data: &[u8]| {
    if data.len() < 2 { return; }
    let split = data[0] as usize % data.len().max(1);
    let (raw, target) = data[1..].split_at(split.min(data.len() - 1));

    let result = header_value_eq(raw, target);

    let trimmed = trim_ows(raw);
    if trimmed.len() == target.len()
        && trimmed.iter().zip(target).all(|(a, b)| a.to_ascii_lowercase() == *b)
    {
        assert!(result);
    }
});
