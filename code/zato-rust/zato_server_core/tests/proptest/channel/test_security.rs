use proptest::prelude::*;
use zato_server_core::channel::cors::is_allowed_origin;
use zato_server_core::channel::security::{check_basic_auth, constant_time_eq, extract_basic_auth, extract_bearer_token, python_strip};

#[test]
fn basic_auth_credentials_are_extracted() {
    let credentials = extract_basic_auth("Basic dXNlcjpwYXNz").unwrap();
    assert_eq!(credentials, ("user".to_owned(), "pass".to_owned()));

    let credentials = extract_basic_auth("Basic  dXNlcjpwYTpzcw==\t").unwrap();
    assert_eq!(credentials, ("user".to_owned(), "pa:ss".to_owned()));
}

#[test]
fn basic_auth_errors_are_detected() {
    assert_eq!(extract_basic_auth("basic dXNlcjpwYXNz"), None);
    assert_eq!(extract_basic_auth("Basic dXNlcnBhc3M="), None);
    assert_eq!(extract_basic_auth("Basic /w=="), None);
    assert_eq!(extract_basic_auth("Basic Y"), None);
}

#[test]
fn basic_auth_check_rejects_an_empty_username() {
    assert!(check_basic_auth(Some("Basic dXNlcjpwYXNz"), "user", "pass"));
    assert!(!check_basic_auth(Some("Basic dXNlcjpwYXNz"), "user", "other"));
    assert!(!check_basic_auth(Some("Basic OnBhc3M="), "", "pass"));
    assert!(!check_basic_auth(None, "user", "pass"));
}

#[test]
fn bearer_prefix_is_case_insensitive() {
    assert_eq!(extract_bearer_token("Bearer abc"), "abc");
    assert_eq!(extract_bearer_token("BEARER  abc \n"), "abc");
    assert_eq!(extract_bearer_token("Bearerabc"), "");
    assert_eq!(extract_bearer_token("Basic abc"), "");
    assert_eq!(extract_bearer_token("Bear"), "");
    assert_eq!(extract_bearer_token("B\u{e9}arer abc"), "");
}

#[test]
fn python_whitespace_includes_information_separators() {
    assert_eq!(python_strip("\u{1c}\u{1f} abc\u{85}\u{3000}"), "abc");
    assert_eq!(python_strip("\u{200b}abc"), "\u{200b}abc");
}

#[test]
fn cors_origins() {
    assert!(is_allowed_origin("https://zato.io"));
    assert!(is_allowed_origin("http://localhost"));
    assert!(is_allowed_origin("http://127.0.0.1:8080"));
    assert!(!is_allowed_origin("http://localhost.example.com"));
    assert!(!is_allowed_origin("https://localhost:8080"));
}

proptest! {

    #[test]
    fn constant_time_comparison_is_equality(left in prop::collection::vec(any::<u8>(), 0..16), right in prop::collection::vec(any::<u8>(), 0..16)) {
        prop_assert_eq!(constant_time_eq(&left, &right), left == right);
    }
}
