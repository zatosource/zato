// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the `Lease` referee against a kind API server and against a local TCP stub.

use super::*;
use crate::test_support::{LOOPBACK, NODE_A, NODE_B};
use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpListener;
use std::process::{Child, Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

/// The namespace of the leases of the tests.
const NAMESPACE: &str = "default";

/// The prefix of the line in which `kubectl proxy` reports its address.
const PROXY_STARTED: &str = "Starting to serve on ";

/// How long the API server may take to answer requests for leases consistently.
const STARTUP_TIMEOUT: Duration = Duration::from_mins(2);

/// How long to wait between two checks of the API server.
const STARTUP_POLL: Duration = Duration::from_millis(250);

/// How many consecutive answers establish that the API server serves leases.
const STARTUP_ANSWERS: u32 = 5;

/// The port on which nothing listens.
const CLOSED_PORT: u16 = 1;

/// A kind cluster of one control-plane node reached through `kubectl proxy`, deleted on drop.
struct KindCluster {
    /// The name of the cluster.
    name: String,

    /// The `kubectl proxy` process.
    proxy: Child,

    /// The address of the proxy.
    address: String,
}

impl KindCluster {
    /// Creates the cluster and waits until its API server serves leases.
    fn create() -> Self {
        let name = format!("zato-ha-lease-test-{}", std::process::id());
        run("kind", &["create", "cluster", "--name", &name]);
        let context = format!("kind-{name}");
        let mut proxy = Command::new("kubectl")
            .args(["--context", &context, "proxy", "--port=0"])
            .stdout(Stdio::piped())
            .spawn()
            .unwrap();
        let mut line = String::new();
        BufReader::new(proxy.stdout.take().unwrap()).read_line(&mut line).unwrap();
        let address = line.trim().strip_prefix(PROXY_STARTED).unwrap().to_owned();
        let cluster = Self {
            name,
            proxy,
            address: format!("http://{address}"),
        };
        cluster.wait_until_serving();
        cluster
    }

    /// Waits for consecutive answers to a list of leases, since the API server answers before every controller runs.
    fn wait_until_serving(&self) {
        let client = self.client();
        let url = client.collection_url(LEASES_GROUP_VERSION, LEASES_RESOURCE);
        let deadline = Instant::now() + STARTUP_TIMEOUT;
        let mut answers = 0;
        while Instant::now() < deadline {
            let serving = client.get(&url).is_ok_and(|response| response.status == STATUS_OK);
            answers = if serving { answers + 1 } else { 0 };
            if answers == STARTUP_ANSWERS {
                return;
            }
            thread::sleep(STARTUP_POLL);
        }
        panic!("The API server of {} did not serve leases within {STARTUP_TIMEOUT:?}", self.name);
    }

    /// Returns a client of the namespace of the tests.
    fn client(&self) -> ApiClient {
        ApiClient::new(&self.address, NAMESPACE, None, None).unwrap()
    }

    /// Returns a referee over the lease `name`.
    fn referee(&self, name: &str) -> LeaseReferee {
        LeaseReferee::new(self.client(), name)
    }

    /// Deletes the lease `name`.
    fn delete(&self, name: &str) {
        let context = format!("kind-{}", self.name);
        run("kubectl", &["--context", &context, "--namespace", NAMESPACE, "delete", "lease", name]);
    }
}

impl Drop for KindCluster {
    fn drop(&mut self) {
        let _ = self.proxy.kill();
        let _ = self.proxy.wait();
        let _ = Command::new("kind").args(["delete", "cluster", "--name", &self.name]).output();
    }
}

/// Runs a command and fails the test if it fails.
fn run(program: &str, args: &[&str]) {
    let output = Command::new(program).args(args).output().unwrap();
    assert!(
        output.status.success(),
        "{program} {}: {}",
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
}

/// Returns the version of the record, which must exist.
fn version(referee: &LeaseReferee) -> String {
    referee.read().unwrap().unwrap().version
}

/// An absent record is created by exactly one of two writers.
fn check_creation(cluster: &KindCluster) {
    let referee = cluster.referee("zato-ha-creation");
    assert!(referee.read().unwrap().is_none());
    assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), None).unwrap());
    assert!(!referee.compare_and_set(&RefereeRecord::solo(1, NODE_B), None).unwrap());
    assert_eq!(referee.read().unwrap().unwrap().value, RefereeRecord::solo(1, NODE_A));
}

/// A write that names a version older than the current one is refused.
fn check_stale_version(cluster: &KindCluster) {
    let referee = cluster.referee("zato-ha-stale");
    assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), None).unwrap());
    let first = version(&referee);
    let replicated = RefereeRecord::replicated(1, NODE_A, NODE_B);
    assert!(referee.compare_and_set(&replicated, Some(&first)).unwrap());
    assert!(!referee.compare_and_set(&RefereeRecord::solo(2, NODE_B), Some(&first)).unwrap());
    assert_eq!(referee.read().unwrap().unwrap().value, replicated);
}

/// Every renewal raises the version, and a renewal at an older version or of another record is refused.
fn check_renewal(cluster: &KindCluster) {
    let referee = cluster.referee("zato-ha-renewal");
    let record = RefereeRecord::solo(1, NODE_A);
    assert!(referee.compare_and_set(&record, None).unwrap());
    let first = version(&referee);

    let second = referee.renew(&record, &first).unwrap().unwrap();
    let third = referee.renew(&record, &second).unwrap().unwrap();
    assert_ne!(first, second);
    assert_ne!(second, third);
    assert_eq!(version(&referee), third);

    assert!(referee.renew(&record, &first).unwrap().is_none());
    assert!(referee.renew(&RefereeRecord::solo(1, NODE_B), &third).unwrap().is_none());
    assert_eq!(referee.read().unwrap().unwrap().value, record);
}

/// A deleted record is neither written nor renewed, and neither operation creates it again.
fn check_deletion(cluster: &KindCluster) {
    let name = "zato-ha-deletion";
    let referee = cluster.referee(name);
    let record = RefereeRecord::solo(1, NODE_A);
    assert!(referee.compare_and_set(&record, None).unwrap());
    let first = version(&referee);
    cluster.delete(name);

    assert!(!referee.compare_and_set(&RefereeRecord::solo(2, NODE_A), Some(&first)).unwrap());
    assert!(referee.renew(&record, &first).unwrap().is_none());
    assert!(referee.read().unwrap().is_none());
}

/// The addresses of both nodes are read back, an address published again replaces the earlier one,
/// and neither the record nor the addresses of another lease are among them.
fn check_addresses(cluster: &KindCluster) {
    let referee = cluster.referee("zato-ha-addresses");
    let other = cluster.referee("zato-ha-other");
    assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), None).unwrap());
    let address = |node_name: &str, port| NodeAddress {
        node_name: node_name.to_owned(),
        host: LOOPBACK.to_owned(),
        port,
    };
    referee.publish_address(&address(NODE_A, 17010)).unwrap();
    referee.publish_address(&address(NODE_B, 17011)).unwrap();
    referee.publish_address(&address(NODE_B, 17012)).unwrap();
    other.publish_address(&address(NODE_A, 17020)).unwrap();

    let mut addresses = referee.read_addresses().unwrap();
    addresses.sort_by(|left, right| left.node_name.cmp(&right.node_name));
    assert_eq!(addresses, [address(NODE_A, 17010), address(NODE_B, 17012)]);
    assert_eq!(referee.read().unwrap().unwrap().value, RefereeRecord::solo(1, NODE_A));
}

#[test]
fn the_record_follows_compare_and_set_in_a_lease() {
    let cluster = KindCluster::create();
    check_creation(&cluster);
    check_stale_version(&cluster);
    check_renewal(&cluster);
    check_deletion(&cluster);
    check_addresses(&cluster);
}

/// A request that the stub received.
struct Received {
    /// The request line.
    request_line: String,

    /// The value of the `Content-Type` header, if there is one.
    content_type: Option<String>,

    /// The body.
    body: String,
}

/// Starts a stub of the API server that answers one request with `status` and returns what it received.
fn stub(status: u16) -> (ApiClient, thread::JoinHandle<Received>) {
    let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
    let address = format!("http://{}", listener.local_addr().unwrap());
    let server = thread::spawn(move || {
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut request_line = String::new();
        reader.read_line(&mut request_line).unwrap();

        // The body is read in full before the answer, so that the client is never reset while it sends it.
        let mut content_type = None;
        let mut content_length = 0;
        loop {
            let mut header = String::new();
            reader.read_line(&mut header).unwrap();
            let header = header.trim_end();
            if header.is_empty() {
                break;
            }
            let (name, value) = header.split_once(": ").unwrap();
            match name.to_ascii_lowercase().as_str() {
                "content-type" => content_type = Some(value.to_owned()),
                "content-length" => content_length = value.parse().unwrap(),
                _ => {}
            }
        }
        let mut body = vec![0; content_length];
        reader.read_exact(&mut body).unwrap();

        let answer = format!("HTTP/1.1 {status} Status\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{{}}");
        stream.write_all(answer.as_bytes()).unwrap();
        Received {
            request_line: request_line.trim_end().to_owned(),
            content_type,
            body: String::from_utf8(body).unwrap(),
        }
    });
    (ApiClient::new(&address, NAMESPACE, None, None).unwrap(), server)
}

#[test]
fn an_absent_lease_is_an_absent_record() {
    let (client, server) = stub(STATUS_NOT_FOUND);
    assert!(LeaseReferee::new(client, "zato-ha").read().unwrap().is_none());
    let received = server.join().unwrap();
    assert_eq!(
        received.request_line,
        "GET /apis/coordination.k8s.io/v1/namespaces/default/leases/zato-ha HTTP/1.1"
    );
}

#[test]
fn an_existing_lease_refuses_the_creation() {
    let (client, server) = stub(STATUS_CONFLICT);
    let referee = LeaseReferee::new(client, "zato-ha");
    assert!(!referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), None).unwrap());
    let received = server.join().unwrap();
    assert_eq!(
        received.request_line,
        "POST /apis/coordination.k8s.io/v1/namespaces/default/leases HTTP/1.1"
    );
}

#[test]
fn a_failed_test_or_a_deleted_lease_refuses_the_write() {
    for status in [STATUS_UNPROCESSABLE, STATUS_NOT_FOUND] {
        let (client, server) = stub(status);
        let referee = LeaseReferee::new(client, "zato-ha");
        assert!(!referee.compare_and_set(&RefereeRecord::solo(2, NODE_A), Some("7")).unwrap());
        let received = server.join().unwrap();
        assert_eq!(received.content_type.as_deref(), Some(CONTENT_TYPE_JSON_PATCH));
        assert!(
            received
                .body
                .starts_with(r#"[{"op":"test","path":"/metadata/resourceVersion","value":"7"}"#)
        );
    }
}

#[test]
fn a_failed_test_or_a_deleted_lease_refuses_the_renewal() {
    for status in [STATUS_UNPROCESSABLE, STATUS_NOT_FOUND] {
        let (client, server) = stub(status);
        let referee = LeaseReferee::new(client, "zato-ha");
        assert!(referee.renew(&RefereeRecord::solo(2, NODE_A), "7").unwrap().is_none());
        let received = server.join().unwrap();
        assert!(received.body.contains(r#"{"op":"test","path":"/metadata/annotations/zato.io~1ha-record""#));
        assert!(
            received
                .body
                .contains(r#"{"op":"add","path":"/metadata/annotations/zato.io~1ha-renewed-from","value":"7"}"#)
        );
    }
}

#[test]
fn an_unexpected_status_is_an_error() {
    let (client, server) = stub(STATUS_CONFLICT);
    let referee = LeaseReferee::new(client, "zato-ha");
    assert!(referee.renew(&RefereeRecord::solo(2, NODE_A), "7").is_err());
    let _ = server.join().unwrap();
}

#[test]
fn an_api_server_that_does_not_answer_is_an_error() {
    let address = format!("http://{LOOPBACK}:{CLOSED_PORT}");
    let referee = LeaseReferee::new(ApiClient::new(&address, NAMESPACE, None, None).unwrap(), "zato-ha");
    assert!(referee.read().is_err());
    assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), None).is_err());
}
