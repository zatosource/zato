#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_scheduler_core::types::JobType;

fuzz_target!(|data: &[u8]| {
    let s = String::from_utf8_lossy(data);
    let jt = JobType::from(s.as_ref());
    let out = jt.as_str();
    assert!(out == "one_time" || out == "interval_based");
});
