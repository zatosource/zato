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
const fn ipv4(first: u8, second: u8, third: u8, fourth: u8) -> IpAddr {
    IpAddr::V4(Ipv4Addr::new(first, second, third, fourth))
}

/// Returns an IPv6 address of the given segments.
const fn ipv6(segments: [u16; 8]) -> IpAddr {
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
        (ipv4(8, 8, 8, 8), Some(NetworkScope::Public)),
        (ipv4(1, 1, 1, 1), Some(NetworkScope::Public)),
        (ipv4(172, 15, 255, 255), Some(NetworkScope::Public)),
        (ipv4(172, 32, 0, 0), Some(NetworkScope::Public)),
        (ipv4(100, 63, 255, 255), Some(NetworkScope::Public)),
        (ipv4(100, 128, 0, 0), Some(NetworkScope::Public)),
        (ipv4(169, 253, 255, 255), Some(NetworkScope::Public)),
        (ipv4(169, 255, 0, 0), Some(NetworkScope::Public)),
        (ipv4(11, 0, 0, 0), Some(NetworkScope::Public)),
        (ipv4(9, 255, 255, 255), Some(NetworkScope::Public)),
    ]);
}

#[test]
fn ipv4_private() {
    assert_scopes(&[
        (ipv4(10, 0, 0, 0), Some(NetworkScope::Private)),
        (ipv4(10, 255, 255, 255), Some(NetworkScope::Private)),
        (ipv4(172, 16, 0, 0), Some(NetworkScope::Private)),
        (ipv4(172, 31, 255, 255), Some(NetworkScope::Private)),
        (ipv4(192, 168, 0, 1), Some(NetworkScope::Private)),
        (ipv4(192, 168, 255, 255), Some(NetworkScope::Private)),
        (ipv4(100, 64, 0, 0), Some(NetworkScope::Private)),
        (ipv4(100, 127, 255, 255), Some(NetworkScope::Private)),
    ]);
}

#[test]
fn ipv4_loopback() {
    assert_scopes(&[
        (ipv4(127, 0, 0, 1), Some(NetworkScope::Loopback)),
        (ipv4(127, 0, 1, 1), Some(NetworkScope::Loopback)),
        (ipv4(127, 255, 255, 254), Some(NetworkScope::Loopback)),
    ]);
}

#[test]
fn ipv4_link_local() {
    assert_scopes(&[
        (ipv4(169, 254, 0, 0), Some(NetworkScope::LinkLocal)),
        (ipv4(169, 254, 169, 254), Some(NetworkScope::LinkLocal)),
        (ipv4(169, 254, 255, 255), Some(NetworkScope::LinkLocal)),
    ]);
}

#[test]
fn ipv4_without_scope() {
    assert_scopes(&[
        (ipv4(0, 0, 0, 0), None),
        (ipv4(0, 1, 2, 3), None),
        (ipv4(0, 255, 255, 255), None),
        (ipv4(224, 0, 0, 1), None),
        (ipv4(239, 255, 255, 250), None),
        (ipv4(255, 255, 255, 255), None),
    ]);
}

#[test]
fn ipv6_scopes() {
    assert_scopes(&[
        (ipv6([0x2001, 0x4860, 0x4860, 0, 0, 0, 0, 0x8888]), Some(NetworkScope::Public)),
        (ipv6([0x2606, 0x4700, 0, 0, 0, 0, 0, 0x1111]), Some(NetworkScope::Public)),
        (ipv6([0xfc00, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Private)),
        (ipv6([0xfd00, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Private)),
        (
            ipv6([0xfdff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff]),
            Some(NetworkScope::Private),
        ),
        (ipv6([0, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Loopback)),
        (ipv6([0xfe80, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::LinkLocal)),
        (ipv6([0xfebf, 0xffff, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::LinkLocal)),
        (ipv6([0xfbff, 0, 0, 0, 0, 0, 0, 1]), Some(NetworkScope::Public)),
    ]);
}

#[test]
fn ipv6_without_scope() {
    assert_scopes(&[
        (ipv6([0, 0, 0, 0, 0, 0, 0, 0]), None),
        (ipv6([0xff02, 0, 0, 0, 0, 0, 0, 1]), None),
        (ipv6([0xff05, 0, 0, 0, 0, 0, 0, 0x0002]), None),
    ]);
}

#[test]
fn ipv4_mapped_by_embedded_address() {
    assert_scopes(&[
        (ipv6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0x7f00, 0x0001]), Some(NetworkScope::Loopback)),
        (ipv6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0x0a00, 0x0001]), Some(NetworkScope::Private)),
        (ipv6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0xa9fe, 0xa9fe]), Some(NetworkScope::LinkLocal)),
        (ipv6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0x0808, 0x0808]), Some(NetworkScope::Public)),
        (ipv6([0, 0, 0, 0, 0, MAPPED_SEGMENT, 0, 0]), None),
    ]);
}

#[test]
fn nat64_by_embedded_address() {
    assert_scopes(&[
        (ipv6([0x0064, 0xff9b, 0, 0, 0, 0, 0x7f00, 0x0001]), Some(NetworkScope::Loopback)),
        (ipv6([0x0064, 0xff9b, 0, 0, 0, 0, 0xc0a8, 0x0001]), Some(NetworkScope::Private)),
        (ipv6([0x0064, 0xff9b, 0, 0, 0, 0, 0xa9fe, 0xa9fe]), Some(NetworkScope::LinkLocal)),
        (ipv6([0x0064, 0xff9b, 0, 0, 0, 0, 0x0808, 0x0808]), Some(NetworkScope::Public)),
        (ipv6([0x0064, 0xff9b, 0, 0, 0, 0, 0, 0]), None),
        // An address under 64:ff9b::/32 outside of the /96 prefix is not a NAT64 address of an IPv4 address
        (ipv6([0x0064, 0xff9b, 1, 0, 0, 0, 0x7f00, 0x0001]), Some(NetworkScope::Public)),
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
        socket(ipv4(127, 0, 0, 1)),
        socket(ipv4(10, 0, 0, 1)),
        socket(ipv4(8, 8, 8, 8)),
        socket(ipv4(169, 254, 169, 254)),
        socket(ipv6([0, 0, 0, 0, 0, 0, 0, 1])),
        socket(ipv4(192, 168, 1, 1)),
        socket(ipv4(0, 0, 0, 0)),
    ];

    let private = retain_scope(addresses.clone(), NetworkScope::Private);
    assert_eq!(private, vec![socket(ipv4(10, 0, 0, 1)), socket(ipv4(192, 168, 1, 1))]);

    let loopback = retain_scope(addresses.clone(), NetworkScope::Loopback);
    assert_eq!(loopback, vec![socket(ipv4(127, 0, 0, 1)), socket(ipv6([0, 0, 0, 0, 0, 0, 0, 1]))]);

    let public = retain_scope(addresses, NetworkScope::Public);
    assert_eq!(public, vec![socket(ipv4(8, 8, 8, 8))]);
}

#[test]
fn retain_without_a_match_is_empty() {
    let addresses = vec![
        socket(ipv4(127, 0, 0, 1)),
        socket(ipv4(169, 254, 169, 254)),
        socket(ipv4(0, 0, 0, 0)),
    ];

    let public = retain_scope(addresses.clone(), NetworkScope::Public);
    assert!(public.is_empty());

    let private = retain_scope(addresses, NetworkScope::Private);
    assert!(private.is_empty());

    let none = retain_scope(Vec::new(), NetworkScope::Loopback);
    assert!(none.is_empty());
}
