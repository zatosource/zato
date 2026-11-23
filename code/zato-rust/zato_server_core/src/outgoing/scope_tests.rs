//! The network scopes of addresses.
//!
//! The tests cover the classification of each range at its boundaries for IPv4, IPv6, IPv4-mapped IPv6
//! and NAT64 addresses, the addresses that have no scope, the names of the scopes that a call may require,
//! and the filtering of resolved addresses by a required scope.

use std::net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr};

use super::{NetworkScope, classify, retain_scope};

/// The port of every socket address of the tests.
const PORT: u16 = 8080;

/// The first segment of an IPv4-mapped IPv6 address after its zero segments.
const MAPPED_SEGMENT: u16 = 0xffff;

/// Returns an IPv4 address.
const fn v4(first: u8, second: u8, third: u8, fourth: u8) -> IpAddr {
    IpAddr::V4(Ipv4Addr::new(first, second, third, fourth))
}

/// Returns an IPv6 address of the given segments.
const fn v6(segments: [u16; 8]) -> IpAddr {
    let [first, second, third, fourth, fifth, sixth, seventh, eighth] = segments;
    IpAddr::V6(Ipv6Addr::new(first, second, third, fourth, fifth, sixth, seventh, eighth))
}

/// Returns a socket address of the given IP address.
const fn socket(address: IpAddr) -> SocketAddr {
    SocketAddr::new(address, PORT)
}

/// Asserts the scope of each address.
fn assert_scopes(cases: &[(IpAddr, Option<NetworkScope>)]) {
    for (address, expected) in cases {
        let scope = classify(*address);
        assert_eq!(scope, *expected, "scope of {address}");
    }
}

#[test]
fn ipv4_public() {
    assert_scopes(&[
        (v4(8, 8, 8, 8), Some(NetworkScope::Public)),
        (v4(1, 1, 1, 1), Some(NetworkScope::Public)),
        (v4(172, 15, 255, 255), Some(NetworkScope::Public)),
        (v4(172, 32, 0, 0), Some(NetworkScope::Public)),
        (v4(100, 63, 255, 255), Some(NetworkScope::Public)),
        (v4(100, 128, 0, 0), Some(NetworkScope::Public)),
        (v4(169, 253, 255, 255), Some(NetworkScope::Public)),
        (v4(169, 255, 0, 0), Some(NetworkScope::Public)),
        (v4(11, 0, 0, 0), Some(NetworkScope::Public)),
        (v4(9, 255, 255, 255), Some(NetworkScope::Public)),
    ]);
}

#[test]
fn ipv4_private() {
    assert_scopes(&[
        (v4(10, 0, 0, 0), Some(NetworkScope::Private)),
        (v4(10, 255, 255, 255), Some(NetworkScope::Private)),
        (v4(172, 16, 0, 0), Some(NetworkScope::Private)),
        (v4(172, 31, 255, 255), Some(NetworkScope::Private)),
        (v4(192, 168, 0, 1), Some(NetworkScope::Private)),
        (v4(192, 168, 255, 255), Some(NetworkScope::Private)),
        (v4(100, 64, 0, 0), Some(NetworkScope::Private)),
        (v4(100, 127, 255, 255), Some(NetworkScope::Private)),
    ]);
}

#[test]
fn ipv4_loopback() {
    assert_scopes(&[
        (v4(127, 0, 0, 1), Some(NetworkScope::Loopback)),
        (v4(127, 0, 1, 1), Some(NetworkScope::Loopback)),
        (v4(127, 255, 255, 254), Some(NetworkScope::Loopback)),
    ]);
}

#[test]
fn ipv4_link_local() {
    assert_scopes(&[
        (v4(169, 254, 0, 0), Some(NetworkScope::LinkLocal)),
        (v4(169, 254, 169, 254), Some(NetworkScope::LinkLocal)),
        (v4(169, 254, 255, 255), Some(NetworkScope::LinkLocal)),
    ]);
}

#[test]
fn ipv4_without_scope() {
    assert_scopes(&[
        (v4(0, 0, 0, 0), None),
        (v4(0, 1, 2, 3), None),
        (v4(0, 255, 255, 255), None),
        (v4(224, 0, 0, 1), None),
        (v4(239, 255, 255, 250), None),
        (v4(255, 255, 255, 255), None),
    ]);
}

#[test]
fn ipv6_scopes() {
    assert_scopes(&[
        (v6([0x2001, 0x4860, 0x4860, 0, 0, 0, 0, 0x8888]), Some(NetworkScope::Public)),
        (v6([0x2606, 0x4700, 0, 0, 0, 0, 0, 0x1111]), Some(NetworkScope::Public)),
        (v6([0xfc00, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Private)),
        (v6([0xfd00, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Private)),
        (
            v6([0xfdff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff]),
            Some(NetworkScope::Private),
        ),
        (v6([0, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Loopback)),
        (v6([0xfe80, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::LinkLocal)),
        (v6([0xfebf, 0xffff, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::LinkLocal)),
        (v6([0xfbff, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Public)),
    ]);
}

#[test]
fn ipv6_without_scope() {
    assert_scopes(&[
        (v6([0, 0, 0, 0, 0, 0, 0, 0]), None),
        (v6([0xff02, 0, 0, 0, 0, 0, 0, 1]), None),
        (v6([0xff05, 0, 0, 0, 0, 0, 0, 0x0002]), None),
    ]);
}

#[test]
fn ipv4_mapped_by_embedded_address() {
    assert_scopes(&[
        (v6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0x7f00, 0x0001]), Some(NetworkScope::Loopback)),
        (v6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0x0a00, 0x0001]), Some(NetworkScope::Private)),
        (v6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0xa9fe, 0xa9fe]), Some(NetworkScope::LinkLocal)),
        (v6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0x0808, 0x0808]), Some(NetworkScope::Public)),
        (v6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0, 0]), None),
    ]);
}

#[test]
fn nat64_by_embedded_address() {
    assert_scopes(&[
        (v6([0x0064, 0xff9b, 0, 0, 0, 0, 0x7f00, 0x0001]), Some(NetworkScope::Loopback)),
        (v6([0x0064, 0xff9b, 0, 0, 0, 0, 0xc0a8, 0x0001]), Some(NetworkScope::Private)),
        (v6([0x0064, 0xff9b, 0, 0, 0, 0, 0xa9fe, 0xa9fe]), Some(NetworkScope::LinkLocal)),
        (v6([0x0064, 0xff9b, 0, 0, 0, 0, 0x0808, 0x0808]), Some(NetworkScope::Public)),
        (v6([0x0064, 0xff9b, 0, 0, 0, 0, 0, 0]), None),
        // An address under 64:ff9b::/32 outside of the /96 prefix is not a NAT64 address of an IPv4 address
        (v6([0x0064, 0xff9b, 1, 0, 0, 0, 0x7f00, 0x0001]), Some(NetworkScope::Public)),
    ]);
}

#[test]
fn names() {
    assert_eq!(NetworkScope::Public.name(), "public");
    assert_eq!(NetworkScope::Private.name(), "private");
    assert_eq!(NetworkScope::Loopback.name(), "loopback");
    assert_eq!(NetworkScope::LinkLocal.name(), "link-local");
}

#[test]
fn required_scope_names() {
    assert_eq!(NetworkScope::parse_required("public"), Some(NetworkScope::Public));
    assert_eq!(NetworkScope::parse_required("private"), Some(NetworkScope::Private));
    assert_eq!(NetworkScope::parse_required("loopback"), Some(NetworkScope::Loopback));

    // The link-local scope is never required, and a name of no scope is not parsed
    assert_eq!(NetworkScope::parse_required("link-local"), None);
    assert_eq!(NetworkScope::parse_required("Public"), None);
    assert_eq!(NetworkScope::parse_required("internal"), None);
    assert_eq!(NetworkScope::parse_required(""), None);
}

#[test]
fn retain_keeps_exactly_the_required_scope_in_order() {
    let addresses = vec![
        socket(v4(127, 0, 0, 1)),
        socket(v4(10, 0, 0, 1)),
        socket(v4(8, 8, 8, 8)),
        socket(v4(169, 254, 169, 254)),
        socket(v6([0, 0, 0, 0, 0, 0, 0, 1])),
        socket(v4(192, 168, 1, 1)),
        socket(v4(0, 0, 0, 0)),
    ];

    let private = retain_scope(addresses.clone(), NetworkScope::Private);
    assert_eq!(private, vec![socket(v4(10, 0, 0, 1)), socket(v4(192, 168, 1, 1))]);

    let loopback = retain_scope(addresses.clone(), NetworkScope::Loopback);
    assert_eq!(loopback, vec![socket(v4(127, 0, 0, 1)), socket(v6([0, 0, 0, 0, 0, 0, 0, 1]))]);

    let public = retain_scope(addresses, NetworkScope::Public);
    assert_eq!(public, vec![socket(v4(8, 8, 8, 8))]);
}

#[test]
fn retain_without_a_match_is_empty() {
    let addresses = vec![socket(v4(127, 0, 0, 1)), socket(v4(169, 254, 169, 254)), socket(v4(0, 0, 0, 0))];

    let public = retain_scope(addresses.clone(), NetworkScope::Public);
    assert!(public.is_empty());

    let private = retain_scope(addresses, NetworkScope::Private);
    assert!(private.is_empty());

    let none = retain_scope(Vec::new(), NetworkScope::Loopback);
    assert!(none.is_empty());
}
