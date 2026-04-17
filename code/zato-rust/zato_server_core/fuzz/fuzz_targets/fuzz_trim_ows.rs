#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::http::io::trim_ows;

fuzz_target!(|data: &[u8]| {
    let trimmed = trim_ows(data);
    assert!(trimmed.len() <= data.len());
    if !trimmed.is_empty() {
        assert!(trimmed[0] != b' ' && trimmed[0] != b'\t');
        assert!(trimmed[trimmed.len() - 1] != b' ' && trimmed[trimmed.len() - 1] != b'\t');
    }
});
