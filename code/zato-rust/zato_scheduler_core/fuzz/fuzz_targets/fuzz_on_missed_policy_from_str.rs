#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_scheduler_core::types::OnMissedPolicy;

fuzz_target!(|data: &[u8]| {
    let s = String::from_utf8_lossy(data);
    let p = OnMissedPolicy::from(s.as_ref());
    let out = p.as_str();
    assert!(out == "skip" || out == "run_once");
});
