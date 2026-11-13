use std::collections::BTreeSet;

use zato_server_core::channel::lru::LruCache;
use zato_server_core::channel::matcher::{ChannelPattern, ChannelSpec, get_match_target};
use zato_server_core::channel::path::to_internal_accept;
use zato_server_core::channel::table::{ChannelTable, TableEntry};

fn methods_allowed() -> Vec<String> {
    vec!["GET".to_owned(), "POST".to_owned(), "DELETE".to_owned()]
}

#[expect(clippy::unwrap_used, reason = "a pattern that does not compile fails the test")]
fn entry(name: &'static str, method: &str, http_accept: Option<&str>, url_path: &str) -> TableEntry<&'static str> {
    let spec = ChannelSpec {
        method,
        http_accept,
        url_path,
        match_slash: true,
    };
    let target = get_match_target(&spec, &methods_allowed());
    TableEntry {
        pattern: ChannelPattern::compile(&spec, &methods_allowed(), &target).unwrap(),
        method: method.to_owned(),
        accept_internal: to_internal_accept(http_accept),
        payload: name,
    }
}

fn table() -> ChannelTable<&'static str> {
    ChannelTable::new(vec![
        entry("customer.get", "GET", None, "/api/customer/{id}"),
        entry("customer.json", "POST", Some("application/json"), "/api/customer/{id}"),
        entry("customer.any", "", None, "/api/any/{id}"),
        entry("zato.ping", "GET", None, "/zato/ping"),
    ])
}

#[test]
fn first_matching_channel_wins() {
    let mut table = table();
    let matched = table.find("/api/customer/123", "GET", "haanyHTTP_SEPhaany").unwrap();
    assert_eq!(matched.index, 0);
    assert_eq!(matched.parameters, vec![("id".to_owned(), "123".to_owned())]);

    let cached = table.find("/api/customer/123", "GET", "haanyHTTP_SEPhaany").unwrap();
    assert_eq!(cached, matched);
}

#[test]
fn accept_value_named_by_a_channel_is_kept() {
    let mut table = table();
    let accept = to_internal_accept(Some("application/json"));
    assert_eq!(table.find("/api/customer/1", "POST", &accept).map(|matched| matched.index), Some(1));
    assert_eq!(table.find("/api/customer/1", "POST", "textHTTP_SEPplain"), None);
}

#[test]
fn internal_channels_are_skipped_for_user_paths() {
    let mut table = table();
    assert_eq!(
        table.find("/zato/ping", "GET", "haanyHTTP_SEPhaany").map(|matched| matched.index),
        Some(3)
    );
    assert_eq!(table.find("/api/zato/ping", "GET", "haanyHTTP_SEPhaany"), None);
}

#[test]
fn methods_of_a_path_are_reported_for_a_miss() {
    let mut table = table();
    assert_eq!(table.find("/api/customer/1", "DELETE", "haanyHTTP_SEPhaany"), None);

    let expected: BTreeSet<String> = std::iter::once("GET".to_owned()).collect();
    assert_eq!(table.allow_methods("/api/customer/1", "DELETE", "haanyHTTP_SEPhaany"), expected);
    assert!(table.allow_methods("/api/order/1", "DELETE", "haanyHTTP_SEPhaany").is_empty());
}

#[test]
fn lru_evicts_least_recently_used() {
    let mut cache = LruCache::new(2);
    cache.insert("first".to_owned(), 1);
    cache.insert("second".to_owned(), 2);
    assert_eq!(cache.get("first"), Some(&1));
    cache.insert("third".to_owned(), 3);
    assert_eq!(cache.len(), 2);
    assert_eq!(cache.peek("second"), None);
    assert_eq!(cache.peek("first"), Some(&1));
    assert_eq!(cache.peek("third"), Some(&3));
}
