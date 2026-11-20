// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Configurations, shared states and probes of the two nodes of a pair for the unit tests.

use std::path::Path;
use std::sync::Arc;

use parking_lot::Mutex;

use crate::config::{
    DEFAULT_LEASE_NAME, DEFAULT_LOG_LEVEL, DEFAULT_POSTGRESQL_PORT, KubernetesConfig, NodeConfig, PostgreSqlConfig, PostgreSqlPassword,
    RefereeConfig, Timers,
};
use crate::postgresql::{DatabaseProbe, ProbeError};
use crate::referee::Referee;
use crate::state::Shared;

/// The name of the first node of the pair.
pub const NODE_A: &str = "zato-a";

/// The name of the second node of the pair.
pub const NODE_B: &str = "zato-b";

/// The address on which the nodes of the tests listen.
pub const LOOPBACK: &str = "127.0.0.1";

/// The name of the Zato database and of its user in the configuration of the tests, which no test connects to.
const DATABASE_NAME: &str = "zato";

/// Returns the configuration of a node whose files are in `dir`.
pub fn node_config(node: &str, dir: &Path, timers: Timers) -> NodeConfig {
    NodeConfig {
        referee: RefereeConfig::Kubernetes(KubernetesConfig {
            lease_name: DEFAULT_LEASE_NAME.to_owned(),
        }),
        node_name: node.to_owned(),
        role_port: 0,
        data_dir: dir.to_path_buf(),
        database: PostgreSqlConfig {
            host: LOOPBACK.to_owned(),
            port: DEFAULT_POSTGRESQL_PORT,
            username: DATABASE_NAME.to_owned(),
            password: PostgreSqlPassword::Value(String::new()),
            database: DATABASE_NAME.to_owned(),
            tls: None,
        },
        timers,
        log_level: DEFAULT_LOG_LEVEL.to_owned(),
    }
}

/// Returns the shared state of a node that has not read the referee record yet.
pub fn shared(config: NodeConfig, referee: Box<dyn Referee>) -> Arc<Shared> {
    Arc::new(Shared::new(config, referee))
}

/// A probe kept in memory, which a test makes fail or succeed.
#[derive(Default)]
pub struct MemoryProbe {
    /// Whether every probe fails.
    pub unreachable: Mutex<bool>,

    /// Whether every probe finds the database not durable.
    pub not_durable: Mutex<bool>,

    /// The generation that the generation guard in the database names, if a Zato server took it over.
    pub generation: Mutex<Option<u64>>,
}

impl DatabaseProbe for Arc<MemoryProbe> {
    fn probe(&self) -> Result<Option<u64>, ProbeError> {
        if *self.unreachable.lock() {
            return Err(ProbeError::Unreachable("unreachable".to_owned()));
        }
        if *self.not_durable.lock() {
            return Err(ProbeError::NotDurable("synchronous_standby_names is empty".to_owned()));
        }
        Ok(*self.generation.lock())
    }
}
