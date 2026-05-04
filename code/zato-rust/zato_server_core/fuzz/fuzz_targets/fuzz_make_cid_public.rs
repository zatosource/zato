#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::http::make_cid_public;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        let result = make_cid_public(s);
        assert!(result.len() <= s.len());
        let dash_count = result.matches('-').count();
        assert!(dash_count <= 3);
    }
});
