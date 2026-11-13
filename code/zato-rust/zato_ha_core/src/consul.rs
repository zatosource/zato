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

/// The header that contains the ACL token.
const TOKEN_HEADER: &str = "X-Consul-Token";

/// The HTTP status of a key that does not exist.
const STATUS_NOT_FOUND: u16 = 404;

/// The HTTP status of a successful request.
const STATUS_OK: u16 = 200;

/// The suffix of the keys under which the nodes publish their addresses.
const NODES_SUFFIX: &str = "nodes";

/// The query of a read of the record, which only a server whose leadership a quorum confirms answers.
const CONSISTENT_QUERY: &str = "?consistent";

/// The query of a read of every key under a prefix.
const RECURSE_QUERY: &str = "?recurse=true";

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

    /// Reads the entries of a key with `query` appended to its URL.
    fn read_entries(&self, key: &str, query: &str) -> Result<Vec<KvEntry>, RefereeError> {
        let url = format!("{}{query}", self.url(key));
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
        // A former leader that a new one replaced answers a read in the default mode with a superseded record.
        let entries = self.read_entries(&self.key, CONSISTENT_QUERY)?;
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

    fn renew(&self, record: &RefereeRecord, expected_version: u64) -> Result<Option<u64>, RefereeError> {
        // The check-and-set of Consul compares the index alone, so the value is compared on a read first,
        // and the write under the same index fails if anything changed the key after that read.
        let current = self.read()?;
        let unchanged = current.is_some_and(|versioned| versioned.version == expected_version && versioned.value == *record);
        if !unchanged {
            return Ok(None);
        }
        if !self.compare_and_set(record, expected_version)? {
            return Ok(None);
        }

        // Consul answers a write with its outcome only, so the new index is read back.
        let renewed = self.read()?;
        Ok(renewed
            .filter(|versioned| versioned.value == *record)
            .map(|versioned| versioned.version))
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
        let entries = self.read_entries(&prefix, RECURSE_QUERY)?;
        entries.iter().map(decode_value).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::referee::VERSION_ABSENT;
    use crate::test_support::{LOOPBACK, NODE_A, NODE_B};
    use std::io::{BufRead, BufReader, Write};
    use std::net::TcpListener;
    use std::process::Command;
    use std::thread;
    use std::time::Instant;

    /// The answer of a server to a read of a key that does not exist.
    const NOT_FOUND_RESPONSE: &[u8] = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";

    /// The Consul image of the test container.
    const CONSUL_IMAGE: &str = "hashicorp/consul:1.21.4";

    /// The port of the Consul HTTP API inside the container.
    const CONSUL_PORT: &str = "8500/tcp";

    /// How long the container may take to elect itself the leader.
    const STARTUP_TIMEOUT: Duration = Duration::from_mins(1);

    /// How long to wait between two checks of the leader.
    const STARTUP_POLL: Duration = Duration::from_millis(250);

    /// The port on which nothing listens.
    const CLOSED_PORT: u16 = 1;

    /// A Consul agent in development mode in a container removed on drop.
    struct ConsulContainer {
        /// The name of the container.
        name: String,

        /// The address of its HTTP API on the host.
        address: String,
    }

    impl ConsulContainer {
        /// Starts the container and waits until the agent has a leader.
        fn start() -> Self {
            let name = format!("zato-ha-consul-test-{}", std::process::id());
            let publish = format!("{LOOPBACK}::8500");
            docker(&[
                "run",
                "--detach",
                "--rm",
                "--name",
                &name,
                "--publish",
                &publish,
                CONSUL_IMAGE,
                "agent",
                "-dev",
                "-client",
                "0.0.0.0",
            ]);
            let mapping = docker(&["port", &name, CONSUL_PORT]);
            let host_port = mapping.lines().next().unwrap().trim();
            let container = Self {
                name,
                address: format!("http://{host_port}"),
            };
            container.wait_for_leader();
            container
        }

        /// Waits until the agent answers with the address of a leader.
        fn wait_for_leader(&self) {
            let agent: ureq::Agent = ureq::Agent::config_builder().timeout_global(Some(REQUEST_TIMEOUT)).build().into();
            let url = format!("{}/v1/status/leader", self.address);
            let deadline = Instant::now() + STARTUP_TIMEOUT;
            while Instant::now() < deadline {
                if let Ok(mut response) = agent.get(&url).call() {
                    let leader = response.body_mut().read_to_string().unwrap();
                    if leader.trim() != "\"\"" {
                        return;
                    }
                }
                thread::sleep(STARTUP_POLL);
            }
            panic!("Consul at {} elected no leader within {STARTUP_TIMEOUT:?}", self.address);
        }

        /// Returns a client of the record under `key`.
        fn referee(&self, key: &str) -> ConsulReferee {
            ConsulReferee::new(&self.address, "", key, None).unwrap()
        }
    }

    impl Drop for ConsulContainer {
        fn drop(&mut self) {
            let _ = Command::new("docker").args(["rm", "--force", &self.name]).output();
        }
    }

    /// Runs the `docker` command and returns its standard output, failing the test if it fails.
    fn docker(args: &[&str]) -> String {
        let output = Command::new("docker").args(args).output().unwrap();
        assert!(
            output.status.success(),
            "docker {}: {}",
            args.join(" "),
            String::from_utf8_lossy(&output.stderr)
        );
        String::from_utf8(output.stdout).unwrap()
    }

    /// Returns the version of the record, which must exist.
    fn version(referee: &ConsulReferee) -> u64 {
        referee.read().unwrap().unwrap().version
    }

    /// An absent record is created by exactly one of two writers.
    fn check_creation(consul: &ConsulContainer) {
        let referee = consul.referee("zato/ha/creation");
        assert!(referee.read().unwrap().is_none());
        assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), VERSION_ABSENT).unwrap());
        assert!(!referee.compare_and_set(&RefereeRecord::solo(1, NODE_B), VERSION_ABSENT).unwrap());
        assert_eq!(referee.read().unwrap().unwrap().value, RefereeRecord::solo(1, NODE_A));
    }

    /// A write that names a version older than the current one is refused.
    fn check_stale_version(consul: &ConsulContainer) {
        let referee = consul.referee("zato/ha/stale");
        assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), VERSION_ABSENT).unwrap());
        let first = version(&referee);
        assert!(
            referee
                .compare_and_set(&RefereeRecord::replicated(1, NODE_A, NODE_B), first)
                .unwrap()
        );
        assert!(!referee.compare_and_set(&RefereeRecord::solo(2, NODE_B), first).unwrap());
        assert_eq!(referee.read().unwrap().unwrap().value, RefereeRecord::replicated(1, NODE_A, NODE_B));
    }

    /// The addresses of both nodes are read back, and the record is not among them.
    fn check_addresses(consul: &ConsulContainer) {
        let referee = consul.referee("zato/ha/addresses");
        assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), VERSION_ABSENT).unwrap());
        for (node_name, port) in [(NODE_A, 17010), (NODE_B, 17011)] {
            referee
                .publish_address(&NodeAddress {
                    node_name: node_name.to_owned(),
                    host: LOOPBACK.to_owned(),
                    port,
                })
                .unwrap();
        }
        let mut addresses = referee.read_addresses().unwrap();
        addresses.sort_by(|left, right| left.node_name.cmp(&right.node_name));
        let names: Vec<&str> = addresses.iter().map(|address| address.node_name.as_str()).collect();
        assert_eq!(names, [NODE_A, NODE_B]);
        assert_eq!(referee.read().unwrap().unwrap().value, RefereeRecord::solo(1, NODE_A));
    }

    #[test]
    fn the_record_follows_compare_and_set_in_consul_kv() {
        let consul = ConsulContainer::start();
        check_creation(&consul);
        check_stale_version(&consul);
        check_addresses(&consul);
    }

    #[test]
    fn the_record_is_read_in_the_consistent_mode() {
        let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
        let address = format!("http://{}", listener.local_addr().unwrap());
        let server = thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let mut request_line = String::new();
            reader.read_line(&mut request_line).unwrap();
            stream.write_all(NOT_FOUND_RESPONSE).unwrap();
            request_line
        });

        let referee = ConsulReferee::new(&address, "", "zato/ha/test", None).unwrap();
        assert!(referee.read().unwrap().is_none());
        let request_line = server.join().unwrap();
        assert_eq!(request_line.trim_end(), "GET /v1/kv/zato/ha/test?consistent HTTP/1.1");
    }

    #[test]
    fn an_agent_that_does_not_answer_is_an_error() {
        let address = format!("http://{LOOPBACK}:{CLOSED_PORT}");
        let referee = ConsulReferee::new(&address, "", "zato/ha/test", None).unwrap();
        assert!(referee.read().is_err());
        assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), VERSION_ABSENT).is_err());
    }
}
