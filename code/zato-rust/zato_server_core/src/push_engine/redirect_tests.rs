//! The rules of the redirects a push follows.
//!
//! The tests cover each status, each network scope of the first push, the limit of redirects,
//! the validation of the Location value, the resolution of relative references and dot segments,
//! the schemes, user information, hosts and ports of the next address, and the ban on HTTP after HTTPS.

use super::{MAX_PUSH_REDIRECTS, PERMANENT_REDIRECT, TEMPORARY_REDIRECT, next_redirect};
use crate::outgoing::scope::NetworkScope;

/// The address of the first push of the tests.
const SOURCE: &str = "http://orders.example.com/api/v1/push?client=crm";

/// The address of the first push of the tests that use TLS.
const SOURCE_TLS: &str = "https://orders.example.com/api/v1/push";

/// Follows one redirect with the given status and location from the first push, in the private scope.
fn follow(url: &str, status: u16, location: &str) -> Result<Option<String>, String> {
    next_redirect(url, status, Some(location), 0, Some(NetworkScope::Private))
}

#[test]
fn only_307_and_308_are_followed() {
    let location = "http://orders.example.com/api/v2/push";

    for status in [TEMPORARY_REDIRECT, PERMANENT_REDIRECT] {
        assert_eq!(follow(SOURCE, status, location).unwrap(), Some(String::from(location)));
    }

    // Statuses that change the method, or that are not redirects at all, end the attempt with their own outcome
    for status in [200, 201, 204, 301, 302, 303, 304, 400, 404, 500, 503] {
        assert_eq!(follow(SOURCE, status, location).unwrap(), None);
    }
}

#[test]
fn scope_of_the_first_push() {
    let location = "/api/v2/push";

    for scope in [NetworkScope::Public, NetworkScope::Private, NetworkScope::Loopback] {
        assert!(next_redirect(SOURCE, TEMPORARY_REDIRECT, Some(location), 0, Some(scope)).unwrap().is_some());
    }

    for scope in [Some(NetworkScope::LinkLocal), None] {
        let error = next_redirect(SOURCE, TEMPORARY_REDIRECT, Some(location), 0, scope).unwrap_err();
        assert!(error.contains("is not followed"), "{error}");
    }
}

#[test]
fn limit_of_redirects() {
    let location = "/api/v2/push";
    let last_allowed = MAX_PUSH_REDIRECTS - 1;

    assert!(next_redirect(SOURCE, TEMPORARY_REDIRECT, Some(location), last_allowed, Some(NetworkScope::Public)).unwrap().is_some());

    let error = next_redirect(SOURCE, TEMPORARY_REDIRECT, Some(location), MAX_PUSH_REDIRECTS, Some(NetworkScope::Public)).unwrap_err();
    assert!(error.contains("beyond the limit of 5 redirects"), "{error}");
}

#[test]
fn location_is_required_and_valid() {
    for location in [None, Some("")] {
        let error = next_redirect(SOURCE, TEMPORARY_REDIRECT, location, 0, Some(NetworkScope::Private)).unwrap_err();
        assert!(error.contains("without a Location header"), "{error}");
    }

    // Whitespace, control characters and characters outside ASCII are rejected, as are repeated headers joined by a comma
    for location in ["/api/v2/ push", "/api/v2/\tpush", "/api/v2/\u{7f}push", "/api/v2/caf\u{e9}", "/a, /b"] {
        let error = follow(SOURCE, TEMPORARY_REDIRECT, location).unwrap_err();
        assert!(error.contains("outside of the range of a Location"), "{error}");
    }
}

#[test]
fn relative_references() {
    let cases = [
        ("/api/v2/push", "http://orders.example.com/api/v2/push"),
        ("push-v2", "http://orders.example.com/api/v1/push-v2"),
        ("../v2/push", "http://orders.example.com/api/v2/push"),
        ("./other", "http://orders.example.com/api/v1/other"),
        ("../../../../top", "http://orders.example.com/top"),
        ("?client=erp", "http://orders.example.com/api/v1/push?client=erp"),
        ("#section", "http://orders.example.com/api/v1/push?client=crm"),
        ("/api/v2/push#section", "http://orders.example.com/api/v2/push"),
        ("//billing.example.com/push", "http://billing.example.com/push"),
        ("http:/api/v3/push", "http://orders.example.com/api/v3/push"),
        ("/api/./v2/../v3/.", "http://orders.example.com/api/v3/"),
        ("/api/v2/push?", "http://orders.example.com/api/v2/push"),
    ];

    for (location, expected) in cases {
        assert_eq!(follow(SOURCE, TEMPORARY_REDIRECT, location).unwrap().as_deref(), Some(expected), "{location}");
    }
}

#[test]
fn absolute_references() {
    let cases = [
        ("HTTPS://billing.example.com/push", "https://billing.example.com/push"),
        ("http://billing.example.com", "http://billing.example.com"),
        ("http://billing.example.com:8080/push", "http://billing.example.com:8080/push"),
        ("http://[2001:db8::10]:8443/push", "http://[2001:db8::10]:8443/push"),
        ("http://billing.example.com:/push", "http://billing.example.com:/push"),
    ];

    for (location, expected) in cases {
        assert_eq!(follow(SOURCE, TEMPORARY_REDIRECT, location).unwrap().as_deref(), Some(expected), "{location}");
    }
}

#[test]
fn invalid_next_addresses() {
    let cases = [
        ("ftp://files.example.com/push", "with a scheme other than http and https"),
        ("mailto:ops@example.com", "with a scheme other than http and https"),
        ("http://user:secret@billing.example.com/push", "with user information"),
        ("http:///push", "without a host"),
        ("http://:8080/push", "without a host"),
        ("http://billing.example.com:0/push", "with an invalid port"),
        ("http://billing.example.com:65536/push", "with an invalid port"),
        ("http://billing.example.com:80a/push", "with an invalid port"),
        ("http://billing.example.com:+80/push", "with an invalid port"),
        ("http://[2001:db8::10/push", "with an invalid IPv6 address"),
    ];

    for (location, expected) in cases {
        let error = follow(SOURCE, TEMPORARY_REDIRECT, location).unwrap_err();
        assert!(error.contains(expected), "{location}: {error}");
    }
}

#[test]
fn no_http_after_https() {
    let error = follow(SOURCE_TLS, PERMANENT_REDIRECT, "http://orders.example.com/api/v1/push").unwrap_err();
    assert!(error.contains("uses HTTP after HTTPS"), "{error}");

    // A relative reference keeps the scheme of the current address, and HTTPS after HTTP is followed
    assert_eq!(
        follow(SOURCE_TLS, PERMANENT_REDIRECT, "/api/v2/push").unwrap().as_deref(),
        Some("https://orders.example.com/api/v2/push")
    );
    assert_eq!(
        follow(SOURCE, PERMANENT_REDIRECT, "https://orders.example.com/push").unwrap().as_deref(),
        Some("https://orders.example.com/push")
    );
}
