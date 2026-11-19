// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the configuration read from the environment.

use super::*;
use std::collections::HashMap;

/// Variables kept in a map.
struct Variables(HashMap<String, String>);

impl VariableSource for Variables {
    fn variable(&self, name: &str) -> Option<String> {
        self.0.get(name).cloned()
    }
}

/// Returns the variables of a minimal deployment.
fn minimal() -> Variables {
    let pairs = [
        (ENV_MODE, MODE_ACTIVE_STANDBY),
        (ENV_NODE_NAME, "zato-a"),
        (ENV_TLS_CA_FILE, "/tls/ca.pem"),
        (ENV_TLS_CERT_FILE, "/tls/zato-a.pem"),
        (ENV_TLS_KEY_FILE, "/tls/zato-a.key"),
        ("HOME", "/home/zato"),
    ];
    Variables(
        pairs
            .iter()
            .map(|(name, value)| ((*name).to_owned(), (*value).to_owned()))
            .collect(),
    )
}

#[test]
fn defaults_apply() {
    let config = NodeConfig::from_source(&minimal()).unwrap();
    assert_eq!(config.replication_port, DEFAULT_REPLICATION_PORT);
    assert_eq!(config.timers.mark_out, Duration::from_secs(3));
    assert_eq!(config.max_clock_skew_ms, DEFAULT_MAX_CLOCK_SKEW_MS);
    assert_eq!(config.data_dir, PathBuf::from("/home/zato/env/qs-1"));
    assert_eq!(config.advertised_address, "zato-a");
    assert_eq!(config.database_path, PathBuf::from("/home/zato/env/qs-1/zato.db"));
    assert_eq!(config.shared_database, None);
    assert_eq!(
        config.referee,
        RefereeConfig::Kubernetes(KubernetesConfig {
            lease_name: DEFAULT_LEASE_NAME.to_owned()
        })
    );
}

#[test]
fn the_lease_name_is_read() {
    let mut variables = minimal();
    variables.0.insert(ENV_REFEREE_TYPE.to_owned(), REFEREE_TYPE_KUBERNETES.to_owned());
    variables.0.insert(ENV_LEASE_NAME.to_owned(), "zato-ha-billing".to_owned());
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(
        config.referee,
        RefereeConfig::Kubernetes(KubernetesConfig {
            lease_name: "zato-ha-billing".to_owned()
        })
    );
}

#[test]
fn unknown_referee_is_refused() {
    let mut variables = minimal();
    variables.0.insert(ENV_REFEREE_TYPE.to_owned(), "etcd".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_REFEREE_TYPE,
            ..
        }
    ));
}

/// Modes that name an asynchronous, relaxed or unknown way of running a pair, each of which the node refuses.
const REFUSED_MODES: [&str; 9] = [
    "",
    "async",
    "asynchronous",
    "active-standby-async",
    "active-active",
    "relaxed",
    "solo",
    "ACTIVE-STANDBY",
    " active-standby",
];

#[test]
fn every_mode_other_than_active_standby_is_refused() {
    for mode in REFUSED_MODES {
        let mut variables = minimal();
        variables.0.insert(ENV_MODE.to_owned(), mode.to_owned());
        let result = NodeConfig::from_source(&variables);
        assert!(
            matches!(result, Err(ConfigError::Invalid { name: ENV_MODE, .. })),
            "mode `{mode}` was not refused"
        );
    }
}

#[test]
fn a_missing_mode_is_refused() {
    let mut variables = minimal();
    variables.0.remove(ENV_MODE);
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(error, ConfigError::Missing(ENV_MODE)));
}

#[test]
fn takeover_must_exceed_mark_out() {
    let mut variables = minimal();
    variables.0.insert(ENV_TAKEOVER_TIME.to_owned(), "3".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_TAKEOVER_TIME,
            ..
        }
    ));
}

#[test]
fn the_bound_of_the_clock_skew_is_read() {
    let mut variables = minimal();
    variables.0.insert(ENV_MAX_CLOCK_SKEW_MS.to_owned(), "250".to_owned());
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(config.max_clock_skew_ms, 250);
}

#[test]
fn a_bound_of_the_clock_skew_of_zero_is_refused() {
    let mut variables = minimal();
    variables.0.insert(ENV_MAX_CLOCK_SKEW_MS.to_owned(), "0".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_MAX_CLOCK_SKEW_MS,
            ..
        }
    ));
}

/// Returns the variables of a deployment whose Zato database is `PostgreSQL`.
fn shared_storage() -> Variables {
    let pairs = [
        (ENV_MODE, MODE_ACTIVE_STANDBY),
        (ENV_DATABASE_TYPE, DATABASE_TYPE_POSTGRESQL),
        (ENV_DATABASE_HOST, "postgresql"),
        (ENV_DATABASE_USERNAME, "zato"),
        (ENV_DATABASE_PASSWORD, "Test password"),
        (ENV_DATABASE_NAME, "zato"),
        (ENV_NODE_NAME, "zato-a"),
        ("HOME", "/home/zato"),
    ];
    Variables(
        pairs
            .iter()
            .map(|(name, value)| ((*name).to_owned(), (*value).to_owned()))
            .collect(),
    )
}

/// Returns the settings of the Zato database read from `variables`.
fn postgresql_config(variables: &Variables) -> PostgreSqlConfig {
    NodeConfig::from_source(variables).unwrap().shared_database.unwrap()
}

#[test]
fn a_postgresql_database_selects_the_shared_storage_mode() {
    let config = NodeConfig::from_source(&shared_storage()).unwrap();
    assert_eq!(config.storage, StorageMode::Shared);
    assert_eq!(config.tls, None);
    assert_eq!(
        config.shared_database,
        Some(PostgreSqlConfig {
            host: "postgresql".to_owned(),
            port: DEFAULT_POSTGRESQL_PORT,
            username: "zato".to_owned(),
            password: PostgreSqlPassword::Value("Test password".to_owned()),
            database: "zato".to_owned(),
            tls: None,
        })
    );
}

#[test]
fn a_sqlite_database_selects_the_replicated_storage_mode() {
    let mut variables = minimal();
    variables.0.insert(ENV_DATABASE_TYPE.to_owned(), DATABASE_TYPE_SQLITE.to_owned());
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(config.storage, StorageMode::Replicated);
    assert!(config.tls.is_some());
}

#[test]
fn an_unknown_database_type_is_refused() {
    let mut variables = shared_storage();
    variables.0.insert(ENV_DATABASE_TYPE.to_owned(), "mysql".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_DATABASE_TYPE,
            ..
        }
    ));
}

#[test]
fn the_password_file_is_preferred_to_the_password() {
    let mut variables = shared_storage();
    variables.0.insert(
        ENV_DATABASE_PASSWORD_FILE.to_owned(),
        "/run/secrets/zato-database-password".to_owned(),
    );
    let config = postgresql_config(&variables);
    assert_eq!(
        config.password,
        PostgreSqlPassword::File(PathBuf::from("/run/secrets/zato-database-password"))
    );
}

#[test]
fn mutual_tls_reads_every_file_and_the_verification() {
    let mut variables = shared_storage();
    for (name, value) in [
        (ENV_DATABASE_SSL, "true"),
        (ENV_DATABASE_SSL_CA_FILE, "/tls/postgresql-ca.pem"),
        (ENV_DATABASE_SSL_CERT_FILE, "/tls/zato-a.pem"),
        (ENV_DATABASE_SSL_KEY_FILE, "/tls/zato-a.key"),
        (ENV_DATABASE_SSL_VERIFY, "false"),
    ] {
        variables.0.insert(name.to_owned(), value.to_owned());
    }
    let config = postgresql_config(&variables);
    assert_eq!(
        config.tls,
        Some(PostgreSqlTls {
            ca_file: Some(PathBuf::from("/tls/postgresql-ca.pem")),
            client_files: Some((PathBuf::from("/tls/zato-a.pem"), PathBuf::from("/tls/zato-a.key"))),
            verify: false,
        })
    );
}

#[test]
fn a_client_certificate_without_its_key_is_refused() {
    let mut variables = shared_storage();
    variables.0.insert(ENV_DATABASE_SSL.to_owned(), "true".to_owned());
    variables
        .0
        .insert(ENV_DATABASE_SSL_CERT_FILE.to_owned(), "/tls/zato-a.pem".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(error, ConfigError::Missing(ENV_DATABASE_SSL_KEY_FILE)));
}
