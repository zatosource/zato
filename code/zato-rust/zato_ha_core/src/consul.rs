// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee kept in the Consul KV store, written with check-and-set.

use std::sync::Arc;
use std::time::Duration;

use base64::Engine;
use base64::engine::general_purpose::STANDARD as BASE64;
use serde::Deserialize;
use ureq::tls::{Certificate, RootCerts, TlsConfig};

use crate::record::{NodeAddress, RefereeRecord, Versioned};
use crate::referee::{Referee, RefereeError};
use crate::wire;

/// How long one request to Consul may take, which is shorter than the gap between the mark-out and the takeover timers.
pub const REQUEST_TIMEOUT: Duration = Duration::from_secs(1);

/// The header that carries the ACL token.
const TOKEN_HEADER: &str = "X-Consul-Token";

/// The HTTP status of a key that does not exist.
const STATUS_NOT_FOUND: u16 = 404;

/// The HTTP status of a successful request.
const STATUS_OK: u16 = 200;

/// The suffix of the keys under which the nodes publish their addresses.
const NODES_SUFFIX: &str = "nodes";

/// One entry of a Consul KV read.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
struct KvEntry {
    /// The index of the last write of the key, which `?cas=` names.
    modify_index: u64,

    /// The value, encoded as Base64, or `None` for an empty value.
    value: Option<String>,
}

/// The Consul referee.
pub struct ConsulReferee {
    /// The HTTP client.
    agent: ureq::Agent,

    /// The address of the Consul agent, without a trailing slash.
    address: String,

    /// The ACL token.
    token: String,

    /// The key of the record.
    key: String,
}

impl ConsulReferee {
    /// Builds a client of the Consul agent at `address`, verifying its certificate against `ca_pem` if given.
    pub fn new(address: &str, token: &str, key: &str, ca_pem: Option<&[u8]>) -> Result<Self, RefereeError> {
        let mut config = ureq::Agent::config_builder()
            .timeout_global(Some(REQUEST_TIMEOUT))
            .http_status_as_error(false);

        if let Some(pem) = ca_pem {
            let certificate = Certificate::from_pem(pem).map_err(|error| RefereeError(format!("Consul CA file: {error}")))?;
            let roots = RootCerts::new_with_certs(&[certificate]);
            let provider = Arc::new(rustls::crypto::ring::default_provider());
            config = config.tls_config(
                TlsConfig::builder()
                    .root_certs(roots)
                    .unversioned_rustls_crypto_provider(provider)
                    .build(),
            );
        }

        Ok(Self {
            agent: config.build().into(),
            address: address.trim_end_matches('/').to_owned(),
            token: token.to_owned(),
            key: key.trim_matches('/').to_owned(),
        })
    }

    /// Returns the URL of a key.
    fn url(&self, key: &str) -> String {
        format!("{}/v1/kv/{key}", self.address)
    }

    /// Returns the key under which `node_name` publishes its address.
    fn address_key(&self, node_name: &str) -> String {
        format!("{}/{NODES_SUFFIX}/{node_name}", self.key)
    }

    /// Reads the entries of a key, or of every key under a prefix with `recurse`.
    fn read_entries(&self, key: &str, recurse: bool) -> Result<Vec<KvEntry>, RefereeError> {
        let mut url = self.url(key);
        if recurse {
            url.push_str("?recurse=true");
        }
        let mut response = self
            .agent
            .get(&url)
            .header(TOKEN_HEADER, &self.token)
            .call()
            .map_err(|error| RefereeError(format!("GET {url}: {error}")))?;

        let status = response.status().as_u16();
        if status == STATUS_NOT_FOUND {
            return Ok(Vec::new());
        }
        let body = response
            .body_mut()
            .read_to_vec()
            .map_err(|error| RefereeError(format!("GET {url}: {error}")))?;
        if status != STATUS_OK {
            return Err(RefereeError(format!(
                "GET {url}: status {status}: {}",
                String::from_utf8_lossy(&body)
            )));
        }
        wire::decode(&body).map_err(|error| RefereeError(format!("GET {url}: {error}")))
    }

    /// Writes a value to a key, with `?cas=` if `expected_version` is given, returning whether the write took place.
    fn write(&self, key: &str, body: &[u8], expected_version: Option<u64>) -> Result<bool, RefereeError> {
        let mut url = self.url(key);
        if let Some(version) = expected_version {
            url = format!("{url}?cas={version}");
        }
        let mut response = self
            .agent
            .put(&url)
            .header(TOKEN_HEADER, &self.token)
            .send(body)
            .map_err(|error| RefereeError(format!("PUT {url}: {error}")))?;

        let status = response.status().as_u16();
        let answer = response
            .body_mut()
            .read_to_string()
            .map_err(|error| RefereeError(format!("PUT {url}: {error}")))?;
        if status != STATUS_OK {
            return Err(RefereeError(format!("PUT {url}: status {status}: {answer}")));
        }
        Ok(answer.trim() == "true")
    }
}

/// Decodes the Base64 value of an entry into a typed value.
fn decode_value<T: serde::de::DeserializeOwned>(entry: &KvEntry) -> Result<T, RefereeError> {
    let encoded = entry.value.as_deref().unwrap_or_default();
    let bytes = BASE64
        .decode(encoded)
        .map_err(|error| RefereeError(format!("Base64 value: {error}")))?;
    wire::decode(&bytes).map_err(|error| RefereeError(format!("JSON value: {error}")))
}

impl Referee for ConsulReferee {
    fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError> {
        let entries = self.read_entries(&self.key, false)?;
        let Some(entry) = entries.first() else {
            return Ok(None);
        };
        let value = decode_value(entry)?;
        Ok(Some(Versioned {
            value,
            version: entry.modify_index,
        }))
    }

    fn compare_and_set(&self, record: &RefereeRecord, expected_version: u64) -> Result<bool, RefereeError> {
        let body = wire::encode(record).map_err(|error| RefereeError(format!("JSON value: {error}")))?;
        self.write(&self.key, &body, Some(expected_version))
    }

    fn publish_address(&self, address: &NodeAddress) -> Result<(), RefereeError> {
        let body = wire::encode(address).map_err(|error| RefereeError(format!("JSON value: {error}")))?;
        let key = self.address_key(&address.node_name);
        if self.write(&key, &body, None)? {
            Ok(())
        } else {
            Err(RefereeError(format!("PUT {key} was not applied")))
        }
    }

    fn read_addresses(&self) -> Result<Vec<NodeAddress>, RefereeError> {
        let prefix = format!("{}/{NODES_SUFFIX}/", self.key);
        let entries = self.read_entries(&prefix, true)?;
        entries.iter().map(decode_value).collect()
    }
}
