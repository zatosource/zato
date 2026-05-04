#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::logging::transform_header_key;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        if let Some(header) = transform_header_key(s) {
            assert!(s.starts_with("HTTP_"));
            assert!(!header.contains('_'));
            assert_eq!(header, header.to_ascii_lowercase());
        }
    }
});
