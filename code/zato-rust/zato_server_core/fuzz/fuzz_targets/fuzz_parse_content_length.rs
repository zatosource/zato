#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::http::io::parse_content_length;

const DEFAULT_MAX_MSG_SIZE: usize = 8 * 1024 * 1024;

fuzz_target!(|data: &[u8]| {
    let result = parse_content_length(data, DEFAULT_MAX_MSG_SIZE);
    assert!(result <= DEFAULT_MAX_MSG_SIZE);
});
