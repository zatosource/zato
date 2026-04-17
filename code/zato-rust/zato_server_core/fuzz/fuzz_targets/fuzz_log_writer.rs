#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::logging::LogWriter;

fuzz_target!(|data: &[u8]| {
    if data.len() < 3 { return; }
    let max_bytes = u16::from_le_bytes([data[0], data[1]]) as u64;
    let payload = &data[2..];

    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("fuzz.log");
    let mut writer = match LogWriter::new(path, max_bytes) {
        Ok(w) => w,
        Err(_) => return,
    };

    for chunk in payload.chunks(64.max(1)) {
        let _ = writer.write_line(chunk);
    }
});
