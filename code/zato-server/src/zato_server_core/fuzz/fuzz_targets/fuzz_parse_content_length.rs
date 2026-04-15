#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::http::io::parse_content_length;

fuzz_target!(|data: &[u8]| {
    let result = parse_content_length(data);
    assert!(result <= 16 * 1024 * 1024);
});
