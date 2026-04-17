#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::logging::format_access_line;

fuzz_target!(|data: &[u8]| {
    if data.len() < 4 { return; }
    let pid = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    let rest = &data[4..];
    let s = String::from_utf8_lossy(rest);
    let parts: Vec<&str> = s.splitn(10, '\0').collect();
    if parts.len() < 9 { return; }
    let size = parts.get(9).and_then(|s| s.parse().ok()).unwrap_or(0usize);

    let line = format_access_line(
        pid, parts[0], parts[1], parts[2], parts[3], parts[4],
        parts[5], parts[6], parts[7], parts[8], size, parts.get(9).unwrap_or(&""),
    );
    assert!(line.ends_with('\n'));
    assert!(line.contains("zato_access_log:0"));
});
