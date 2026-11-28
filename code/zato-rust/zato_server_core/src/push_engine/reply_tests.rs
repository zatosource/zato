//! The response to a push of several messages.
//!
//! The tests cover lists of the IDs of the request, empty lists, escapes and whitespace,
//! bodies that are not JSON lists of strings, and IDs that are not in the request.

use super::parse_accepted_ids;

/// The IDs of the messages of the request of the tests.
fn request_ids() -> Vec<String> {
    vec![
        String::from("zpsm.20261128-a1"),
        String::from("zpsm.20261128-b2"),
        String::from("zpsm.20261128-c3"),
    ]
}

#[test]
fn lists_of_request_ids() {
    let ids = request_ids();

    let all = parse_accepted_ids(br#"["zpsm.20261128-a1","zpsm.20261128-b2","zpsm.20261128-c3"]"#, &ids).unwrap();
    assert_eq!(all, ids);

    let partial = parse_accepted_ids(b" [ \"zpsm.20261128-c3\" ,\n\t\"zpsm.20261128-a1\" ] \r\n", &ids).unwrap();
    assert_eq!(partial, vec![String::from("zpsm.20261128-c3"), String::from("zpsm.20261128-a1")]);

    let empty = parse_accepted_ids(b"[]", &ids).unwrap();
    assert!(empty.is_empty());

    let empty_spaced = parse_accepted_ids(b" [ \n ] ", &ids).unwrap();
    assert!(empty_spaced.is_empty());
}

#[test]
fn escapes() {
    let ids = vec![String::from("zpsm/\"quoted\"\\caf\u{e9}\u{1f600}")];

    let body = br#"["zpsm\/\"quoted\"\\caf\u00e9\ud83d\ude00"]"#;
    assert_eq!(parse_accepted_ids(body, &ids).unwrap(), ids);
}

#[test]
fn not_a_list_of_strings() {
    let ids = request_ids();

    let bodies: [&[u8]; 16] = [
        b"",
        b"OK",
        b"{\"accepted\": [\"zpsm.20261128-a1\"]}",
        b"\"zpsm.20261128-a1\"",
        b"[\"zpsm.20261128-a1\", 1]",
        b"[null]",
        b"[[\"zpsm.20261128-a1\"]]",
        b"[\"zpsm.20261128-a1\",]",
        b"[\"zpsm.20261128-a1\"",
        b"[\"zpsm.20261128-a1\"] x",
        b"[\"zpsm.20261128-a1\"][]",
        b"[\"zpsm\n\"]",
        b"[\"zpsm\\x\"]",
        b"[\"\\ud83d\"]",
        b"[\"\\udc00\"]",
        b"[\"\xff\"]",
    ];

    for body in bodies {
        let error = parse_accepted_ids(body, &ids).unwrap_err();
        assert!(error.contains("not a JSON list of strings"), "{body:?}: {error}");
    }
}

#[test]
fn ids_not_in_the_request() {
    let ids = request_ids();

    let error = parse_accepted_ids(br#"["zpsm.20261128-a1","zpsm.20261128-zz"]"#, &ids).unwrap_err();
    assert!(error.contains("`zpsm.20261128-zz`, not in the request"), "{error}");
}
