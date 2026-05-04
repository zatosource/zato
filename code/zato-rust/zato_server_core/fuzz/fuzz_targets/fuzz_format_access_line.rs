#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::logging::{AccessLogEntry, format_access_line};

fuzz_target!(|data: &[u8]| {
    if data.len() < 4 { return; }
    let pid = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    let rest = &data[4..];
    let text = String::from_utf8_lossy(rest);
    let parts: Vec<&str> = text.splitn(10, '\0').collect();
    if parts.len() < 9 { return; }
    let size = parts.get(9).and_then(|val| val.parse().ok()).unwrap_or(0usize);

    let line = format_access_line(&AccessLogEntry {
        pid, remote_ip: parts[0], cid: parts[1], resp_time: parts[2],
        channel_name: parts[3], req_timestamp: parts[4], method: parts[5],
        path: parts[6], http_version: parts[7], status_code: parts[8],
        response_size: size, user_agent: parts.get(9).unwrap_or(&""),
    });
    assert!(line.ends_with('\n'));
    assert!(line.contains("zato_access_log:0"));
});
