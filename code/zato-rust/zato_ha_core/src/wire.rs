// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Typed encoding and parsing of the JSON documents exchanged with Consul and Kubernetes and stored in `PostgreSQL`.

use serde::Serialize;
use serde::de::DeserializeOwned;

/// Parses a JSON document into a typed value.
#[expect(
    clippy::disallowed_methods,
    reason = "JSON is the wire format of the Consul and Kubernetes APIs and of the PostgreSQL referee"
)]
pub fn decode<T: DeserializeOwned>(bytes: &[u8]) -> Result<T, serde_json::Error> {
    serde_json::from_slice(bytes)
}

/// Encodes a typed value as a JSON document.
#[expect(
    clippy::disallowed_methods,
    reason = "JSON is the wire format of the Consul and Kubernetes APIs and of the PostgreSQL referee"
)]
pub fn encode<T: Serialize>(value: &T) -> Result<Vec<u8>, serde_json::Error> {
    serde_json::to_vec(value)
}
