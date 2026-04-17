#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::logging::format_rest_line;

fuzz_target!(|data: &[u8]| {
    if data.len() < 16 { return; }
    let pid = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    let delta_sec = (i64::from_le_bytes(data[4..12].try_into().unwrap()) & 0x7FFF_FFFF_FFFF_FFFF) % 86400;
    let delta_usec = (i32::from_le_bytes(data[12..16].try_into().unwrap()) & 0x7FFF_FFFF) % 1_000_000;
    let rest = &data[16..];
    let s = String::from_utf8_lossy(rest);
    let parts: Vec<&str> = s.splitn(3, '\0').collect();
    let cid = parts.first().map_or("cid", |s| s);
    let status = parts.get(1).map_or("200", |s| s);
    let size = parts.get(2).and_then(|s| s.parse().ok()).unwrap_or(0usize);

    let line = format_rest_line(pid, cid, status, delta_sec, delta_usec, size);
    assert!(line.ends_with('\n'));
    assert!(line.contains("REST cha"));
});
