//! The network scopes of the addresses an outgoing connection is established to.
//!
//! A call with a required scope connects only to the resolved addresses of exactly that scope,
//! and the scope of the address a connection is established to is returned with each response.

use std::net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr};

/// The name of the public scope, as Python passes and receives it.
const PUBLIC_NAME: &str = "public";

/// The name of the private scope, as Python passes and receives it.
const PRIVATE_NAME: &str = "private";

/// The name of the loopback scope, as Python passes and receives it.
const LOOPBACK_NAME: &str = "loopback";

/// The name of the link-local scope, as Python receives it.
const LINK_LOCAL_NAME: &str = "link-local";

/// The first octet of 0.0.0.0/8, the addresses of this network.
const THIS_NETWORK_OCTET: u8 = 0;

/// The first octet of 100.64.0.0/10, the shared address space of carrier-grade NAT.
const SHARED_FIRST_OCTET: u8 = 100;

/// The mask of the second octet that 100.64.0.0/10 covers.
const SHARED_SECOND_MASK: u8 = 0b1100_0000;

/// The second octet of 100.64.0.0/10 under its mask.
const SHARED_SECOND_PREFIX: u8 = 0b0100_0000;

/// The first segment of 64:ff9b::/96, the well-known prefix of NAT64.
const NAT64_FIRST_SEGMENT: u16 = 0x0064;

/// The second segment of 64:ff9b::/96.
const NAT64_SECOND_SEGMENT: u16 = 0xff9b;

/// The mask of the first segment that fe80::/10 covers.
const LINK_LOCAL_V6_MASK: u16 = 0xffc0;

/// The first segment of fe80::/10 under its mask.
const LINK_LOCAL_V6_PREFIX: u16 = 0xfe80;

/// The mask of the first segment that fc00::/7 covers.
const UNIQUE_LOCAL_V6_MASK: u16 = 0xfe00;

/// The first segment of fc00::/7 under its mask.
const UNIQUE_LOCAL_V6_PREFIX: u16 = 0xfc00;

/// How many bits a segment of an IPv6 address is shifted by to form the upper half of an IPv4 address.
const SEGMENT_BITS: u32 = 16;

/// The network scope of an address.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum NetworkScope {
    /// An address reachable through the internet.
    Public,

    /// RFC 1918 addresses, 100.64.0.0/10 and fc00::/7.
    Private,

    /// 127.0.0.0/8 and ::1.
    Loopback,

    /// 169.254.0.0/16 and fe80::/10.
    LinkLocal,
}

impl NetworkScope {
    /// The name of the scope, as Python receives it.
    pub const fn name(self) -> &'static str {
        match self {
            Self::Public => PUBLIC_NAME,
            Self::Private => PRIVATE_NAME,
            Self::Loopback => LOOPBACK_NAME,
            Self::LinkLocal => LINK_LOCAL_NAME,
        }
    }

    /// Parses the name of a scope that a call may require, which is any scope other than link-local.
    pub fn parse_required(name: &str) -> Option<Self> {
        match name {
            PUBLIC_NAME => Some(Self::Public),
            PRIVATE_NAME => Some(Self::Private),
            LOOPBACK_NAME => Some(Self::Loopback),
            _ => None,
        }
    }
}

/// Returns the scope of an address, or `None` for an unspecified, multicast or broadcast address and for 0.0.0.0/8.
pub fn classify(address: IpAddr) -> Option<NetworkScope> {
    match address {
        IpAddr::V4(address) => classify_v4(address),
        IpAddr::V6(address) => classify_v6(address),
    }
}

/// Returns the scope of an IPv4 address.
fn classify_v4(address: Ipv4Addr) -> Option<NetworkScope> {
    let [first, second, _, _] = address.octets();

    // Addresses that do not name one host have no scope
    if first == THIS_NETWORK_OCTET {
        return None;
    }

    if address.is_multicast() {
        return None;
    }

    if address.is_broadcast() {
        return None;
    }

    // The shared address space of carrier-grade NAT is not routed publicly, so it counts as private
    let is_rfc1918 = address.is_private();
    let is_shared_space = is_shared(first, second);
    let is_private = is_rfc1918 || is_shared_space;

    let scope = if address.is_loopback() {
        NetworkScope::Loopback
    } else if address.is_link_local() {
        NetworkScope::LinkLocal
    } else if is_private {
        NetworkScope::Private
    } else {
        NetworkScope::Public
    };

    Some(scope)
}

/// Whether the first two octets of an IPv4 address are within 100.64.0.0/10.
const fn is_shared(first: u8, second: u8) -> bool {
    if first != SHARED_FIRST_OCTET {
        return false;
    }

    let masked = second & SHARED_SECOND_MASK;
    masked == SHARED_SECOND_PREFIX
}

/// Returns the scope of an IPv6 address, classifying an IPv4-mapped or a NAT64 address by its IPv4 address.
fn classify_v6(address: Ipv6Addr) -> Option<NetworkScope> {
    // Addresses that do not name one host have no scope
    if address.is_unspecified() {
        return None;
    }

    if address.is_multicast() {
        return None;
    }

    if let Some(embedded) = address.to_ipv4_mapped() {
        return classify_v4(embedded);
    }

    if let Some(embedded) = nat64_embedded(address) {
        return classify_v4(embedded);
    }

    let [first, ..] = address.segments();

    let scope = if address.is_loopback() {
        NetworkScope::Loopback
    } else if (first & LINK_LOCAL_V6_MASK) == LINK_LOCAL_V6_PREFIX {
        NetworkScope::LinkLocal
    } else if (first & UNIQUE_LOCAL_V6_MASK) == UNIQUE_LOCAL_V6_PREFIX {
        NetworkScope::Private
    } else {
        NetworkScope::Public
    };

    Some(scope)
}

/// Returns the IPv4 address in the last 32 bits of an address in 64:ff9b::/96, or `None` for any other address.
fn nat64_embedded(address: Ipv6Addr) -> Option<Ipv4Addr> {
    // Only the well-known prefix followed by four zero segments embeds an IPv4 address
    let [NAT64_FIRST_SEGMENT, NAT64_SECOND_SEGMENT, 0, 0, 0, 0, high, low] = address.segments() else {
        return None;
    };

    let upper = u32::from(high) << SEGMENT_BITS;
    let embedded = upper | u32::from(low);

    Some(Ipv4Addr::from(embedded))
}

/// Keeps only the addresses of exactly the required scope, in their order.
pub fn retain_scope(addresses: Vec<SocketAddr>, required: NetworkScope) -> Vec<SocketAddr> {
    let mut out = addresses;
    out.retain(|address| {
        let scope = classify(address.ip());
        scope == Some(required)
    });
    out
}

#[cfg(test)]
#[path = "scope_tests.rs"]
mod tests;
