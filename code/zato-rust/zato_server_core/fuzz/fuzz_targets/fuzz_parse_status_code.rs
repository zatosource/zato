#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::http::response::parse_status_code;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        let status = parse_status_code(s);
        assert!(status.as_u16() >= 100 && status.as_u16() < 1000);
    }
});
