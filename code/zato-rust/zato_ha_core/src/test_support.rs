// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Certificates, configurations and shared states of the two nodes of a pair for the unit tests.

use std::path::Path;
use std::process::Command;
use std::sync::Arc;

use tempfile::TempDir;

use crate::config::{
    DB_NAME_AUDIT, DB_NAME_COMMON, DB_NAME_PUBSUB, DatabaseConfig, NodeConfig, RefereeType, ShippingMode, Timers, TlsFiles,
};
use crate::link::TlsContext;
use crate::referee::Referee;
use crate::state::Shared;

/// The name of the first node of the pair.
pub const NODE_A: &str = "zato-a";

/// The name of the second node of the pair.
pub const NODE_B: &str = "zato-b";

/// How long the issued certificates are valid, in days.
const VALIDITY_DAYS: &str = "2";

/// The address on which the nodes of the tests listen.
pub const LOOPBACK: &str = "127.0.0.1";

/// A CA and a certificate for each node, issued by the `openssl` command into a directory removed on drop.
pub struct Certificates {
    /// The directory of the CA, the certificates and the keys.
    dir: TempDir,
}

impl Certificates {
    /// Issues the CA and the certificate of each node, each naming its node as a DNS name.
    pub fn issue() -> Self {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path();
        run_openssl(
            path,
            &[
                "req",
                "-x509",
                "-newkey",
                "ec",
                "-pkeyopt",
                "ec_paramgen_curve:prime256v1",
                "-nodes",
                "-keyout",
                "ca.key",
                "-out",
                "ca.pem",
                "-days",
                VALIDITY_DAYS,
                "-subj",
                "/CN=zato-ha-test-ca",
            ],
        );
        for node in [NODE_A, NODE_B] {
            let key = format!("{node}.key");
            let request = format!("{node}.csr");
            let certificate = format!("{node}.pem");
            let extensions = format!("{node}.ext");
            let subject = format!("/CN={node}");
            std::fs::write(
                path.join(&extensions),
                format!("subjectAltName=DNS:{node}\nextendedKeyUsage=serverAuth,clientAuth\n"),
            )
            .unwrap();
            run_openssl(
                path,
                &[
                    "req",
                    "-newkey",
                    "ec",
                    "-pkeyopt",
                    "ec_paramgen_curve:prime256v1",
                    "-nodes",
                    "-keyout",
                    &key,
                    "-out",
                    &request,
                    "-subj",
                    &subject,
                ],
            );
            run_openssl(
                path,
                &[
                    "x509",
                    "-req",
                    "-in",
                    &request,
                    "-CA",
                    "ca.pem",
                    "-CAkey",
                    "ca.key",
                    "-CAcreateserial",
                    "-out",
                    &certificate,
                    "-days",
                    VALIDITY_DAYS,
                    "-extfile",
                    &extensions,
                ],
            );
        }
        Self { dir }
    }

    /// Returns the TLS files of a node.
    pub fn files(&self, node: &str) -> TlsFiles {
        let path = self.dir.path();
        TlsFiles {
            authority: path.join("ca.pem"),
            certificate: path.join(format!("{node}.pem")),
            private_key: path.join(format!("{node}.key")),
        }
    }
}

/// Runs the `openssl` command in `dir` and fails the test if it fails.
fn run_openssl(dir: &Path, args: &[&str]) {
    let output = Command::new("openssl").args(args).current_dir(dir).output().unwrap();
    assert!(
        output.status.success(),
        "openssl {}: {}",
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
}

/// Returns the configuration of a node whose files are in `dir`.
pub fn node_config(node: &str, dir: &Path, certificates: &Certificates, timers: Timers) -> NodeConfig {
    NodeConfig {
        referee_type: RefereeType::Consul,
        consul_address: format!("http://{LOOPBACK}:8500"),
        consul_token: String::new(),
        consul_ca_file: None,
        consul_key: "zato/ha/test".to_owned(),
        node_name: node.to_owned(),
        advertised_address: LOOPBACK.to_owned(),
        replication_port: 0,
        role_port: 0,
        data_dir: dir.to_path_buf(),
        tls: certificates.files(node),
        timers,
        databases: vec![
            DatabaseConfig {
                name: DB_NAME_PUBSUB,
                path: dir.join("pubsub.db"),
                shipping: ShippingMode::Synchronous,
            },
            DatabaseConfig {
                name: DB_NAME_COMMON,
                path: dir.join("common.db"),
                shipping: ShippingMode::Synchronous,
            },
            DatabaseConfig {
                name: DB_NAME_AUDIT,
                path: dir.join("audit.db"),
                shipping: ShippingMode::Asynchronous,
            },
        ],
        barrier_socket: dir.join("ha-barrier.sock"),
        log_level: "info".to_owned(),
    }
}

/// Returns the shared state of a node that has not read the referee record yet.
pub fn shared(config: NodeConfig, referee: Box<dyn Referee>) -> Arc<Shared> {
    let tls = TlsContext::load(&config.tls).unwrap();
    Arc::new(Shared::new(config, referee, tls))
}
