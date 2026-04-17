use proptest::prelude::*;
use zato_server_core::logging::{LogWriter, format_rest_line, format_access_line, transform_header_key};

proptest! {

    #[test]
    fn rest_line_contains_cid(cid in "[a-zA-Z0-9-]{1,40}") {
        let line = format_rest_line(1234, &cid, "200", 0, 500, 42);
        prop_assert!(line.contains(&cid));
    }

    #[test]
    fn rest_line_contains_status(code in "(200|201|400|404|500)") {
        let line = format_rest_line(1234, "test-cid", &code, 0, 0, 0);
        prop_assert!(line.contains(&code));
    }

    #[test]
    fn rest_line_ends_with_newline(cid in "[a-z]{1,10}", size in 0usize..100000) {
        let line = format_rest_line(1, &cid, "200", 0, 0, size);
        prop_assert!(line.ends_with('\n'));
    }

    #[test]
    fn rest_line_contains_rest_marker(sec in 0i64..3600, usec in 0i32..999999) {
        let line = format_rest_line(1, "cid", "200", sec, usec, 0);
        prop_assert!(line.contains("REST cha"));
        prop_assert!(line.contains("zato_rest:0"));
    }

    #[test]
    fn access_line_contains_all_fields(
        ip in "[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}",
        cid in "[a-z0-9]{5,15}",
        method in "(GET|POST|PUT|DELETE)",
        path in "/[a-z/]{1,20}",
        status in "(200|404|500)",
        size in 0usize..10000,
        ua in "[a-zA-Z0-9/. ]{1,30}",
    ) {
        let line = format_access_line(1, &ip, &cid, "0.001", "test-chan",
            "14/Apr/2026:00:00:00 +0200", &method, &path, "HTTP/1.1",
            &status, size, &ua);
        prop_assert!(line.contains(&ip));
        prop_assert!(line.contains(&cid));
        prop_assert!(line.contains(&method));
        prop_assert!(line.contains(&path));
        prop_assert!(line.contains(&status));
        prop_assert!(line.contains("zato_access_log:0"));
        prop_assert!(line.ends_with('\n'));
    }

    #[test]
    fn transform_header_key_http_prefix(suffix in "[A-Z_]{1,20}") {
        let key = format!("HTTP_{}", suffix);
        let result = transform_header_key(&key);
        prop_assert!(result.is_some());
        let header = result.unwrap();
        prop_assert!(!header.contains('_'));
        let lower = header.to_ascii_lowercase();
        prop_assert_eq!(header, lower);
    }

    #[test]
    fn transform_header_key_non_http_returns_none(key in "[A-Z]{1,10}") {
        if !key.starts_with("HTTP_") {
            prop_assert!(transform_header_key(&key).is_none());
        }
    }

    #[test]
    fn transform_header_key_preserves_length(suffix in "[A-Z_]{1,30}") {
        let key = format!("HTTP_{}", suffix);
        let header = transform_header_key(&key).unwrap();
        prop_assert_eq!(header.len(), suffix.len());
    }

    #[test]
    fn log_writer_tracks_bytes(lines in proptest::collection::vec("[a-z]{1,80}\n", 1..50)) {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("test.log");
        let mut writer = LogWriter::new(path, 1_000_000).unwrap();
        let mut expected: u64 = 0;
        for line in &lines {
            writer.write_line(line.as_bytes()).unwrap();
            expected += line.len() as u64;
        }
        prop_assert_eq!(writer.written, expected);
    }

    #[test]
    fn log_writer_rotates_at_max(chunk_count in 2usize..10) {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("test.log");
        let mut writer = LogWriter::new(path.clone(), 100).unwrap();
        let line = "x".repeat(60) + "\n";
        for _ in 0..chunk_count {
            writer.write_line(line.as_bytes()).unwrap();
        }
        let backup = path.with_extension("log.1");
        prop_assert!(backup.exists());
    }
}
