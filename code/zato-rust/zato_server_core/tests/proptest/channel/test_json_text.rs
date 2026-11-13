use proptest::prelude::*;
use zato_server_core::channel::json_text::{push_float_repr, push_json_code_points, push_json_float, push_json_string};

fn repr(value: f64) -> String {
    let mut out = String::new();
    push_float_repr(&mut out, value);
    out
}

fn quoted(text: &str) -> String {
    let mut out = String::new();
    push_json_string(&mut out, text);
    out
}

#[test]
fn float_repr_matches_python() {
    assert_eq!(repr(0.0), "0.0");
    assert_eq!(repr(-0.0), "-0.0");
    assert_eq!(repr(0.1), "0.1");
    assert_eq!(repr(100.0), "100.0");
    assert_eq!(repr(1234.5), "1234.5");
    assert_eq!(repr(0.0001), "0.0001");
    assert_eq!(repr(0.00001), "1e-05");
    assert_eq!(repr(1.5e-7), "1.5e-07");
    assert_eq!(repr(9_999_999_999_999_998.0), "9999999999999998.0");
    assert_eq!(repr(1e16), "1e+16");
    assert_eq!(repr(1.5e16), "1.5e+16");
    assert_eq!(repr(123_456_789_012_345_680.0), "1.2345678901234568e+17");
    assert_eq!(repr(1e22), "1e+22");
    assert_eq!(repr(5e-324), "5e-324");
    assert_eq!(repr(f64::MAX), "1.7976931348623157e+308");
}

#[test]
fn special_floats_have_names() {
    let mut out = String::new();
    push_json_float(&mut out, f64::NAN);
    out.push(' ');
    push_json_float(&mut out, f64::INFINITY);
    out.push(' ');
    push_json_float(&mut out, f64::NEG_INFINITY);
    assert_eq!(out, "NaN Infinity -Infinity");
}

#[test]
fn strings_are_escaped_as_ascii() {
    assert_eq!(quoted("John Smith"), "\"John Smith\"");
    assert_eq!(quoted("a\"b\\c\n\r\t\u{8}\u{c}"), "\"a\\\"b\\\\c\\n\\r\\t\\b\\f\"");
    assert_eq!(quoted("\u{1}\u{7f}\u{e9}"), "\"\\u0001\\u007f\\u00e9\"");
    assert_eq!(quoted("\u{1f600}"), "\"\\ud83d\\ude00\"");
    assert_eq!(quoted("/"), "\"/\"");
}

#[test]
fn surrogates_are_escaped() {
    let mut out = String::new();
    push_json_code_points(&mut out, &[0x61, 0xD83D]);
    assert_eq!(out, "\"a\\ud83d\"");
}

proptest! {

    #[test]
    fn repr_reads_back_as_the_same_float(value in any::<f64>().prop_filter("finite", |number| number.is_finite())) {
        let text = repr(value);
        let parsed: f64 = text.parse().unwrap();
        prop_assert_eq!(parsed.to_bits(), value.to_bits());
    }

    #[test]
    fn escaped_strings_are_ascii(text in "\\PC{0,30}") {
        let out = quoted(&text);
        prop_assert!(out.bytes().all(|byte| (0x20..=0x7E).contains(&byte)));
    }
}
