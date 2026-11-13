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
        (ENV_REFEREE_TYPE, REFEREE_TYPE_CONSUL),
        (ENV_CONSUL_ADDRESS, "https://consul:8501"),
        (ENV_CONSUL_TOKEN, "token"),
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
    assert_eq!(config.data_dir, PathBuf::from("/home/zato/env/qs-1"));
    assert_eq!(config.advertised_address, "zato-a");
    assert_eq!(config.databases.len(), 3);
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

/// Returns the variables of a deployment whose pub/sub database is `PostgreSQL`.
fn shared_storage() -> Variables {
    let pairs = [
        (ENV_MODE, MODE_ACTIVE_STANDBY),
        (ENV_REFEREE_TYPE, REFEREE_TYPE_POSTGRESQL),
        (ENV_PUBSUB_DB_TYPE, PUBSUB_DB_TYPE_POSTGRESQL),
        (ENV_PUBSUB_DB_HOST, "postgresql"),
        (ENV_PUBSUB_DB_USERNAME, "zato"),
        (ENV_PUBSUB_DB_PASSWORD, "Test password"),
        (ENV_PUBSUB_DB_NAME, "zato_pubsub"),
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

/// Returns the settings of the `PostgreSQL` referee read from `variables`.
fn postgresql_config(variables: &Variables) -> PostgreSqlConfig {
    let config = NodeConfig::from_source(variables).unwrap();
    let RefereeConfig::PostgreSql(out) = config.referee else {
        panic!("not the PostgreSQL referee: {:?}", config.referee);
    };
    out
}

#[test]
fn a_postgresql_database_selects_the_shared_storage_mode() {
    let config = NodeConfig::from_source(&shared_storage()).unwrap();
    assert_eq!(config.storage, StorageMode::Shared);
    assert_eq!(config.tls, None);
    assert_eq!(
        config.referee,
        RefereeConfig::PostgreSql(PostgreSqlConfig {
            host: "postgresql".to_owned(),
            port: DEFAULT_POSTGRESQL_PORT,
            username: "zato".to_owned(),
            password: PostgreSqlPassword::Value("Test password".to_owned()),
            database: "zato_pubsub".to_owned(),
            tls: None,
        })
    );
}

#[test]
fn a_sqlite_database_selects_the_replicated_storage_mode() {
    let mut variables = minimal();
    variables.0.insert(ENV_PUBSUB_DB_TYPE.to_owned(), PUBSUB_DB_TYPE_SQLITE.to_owned());
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(config.storage, StorageMode::Replicated);
    assert!(config.tls.is_some());
}

#[test]
fn an_unknown_pubsub_database_type_is_refused() {
    let mut variables = shared_storage();
    variables.0.insert(ENV_PUBSUB_DB_TYPE.to_owned(), "mysql".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_PUBSUB_DB_TYPE,
            ..
        }
    ));
}

#[test]
fn the_password_file_is_preferred_to_the_password() {
    let mut variables = shared_storage();
    variables.0.insert(
        ENV_PUBSUB_DB_PASSWORD_FILE.to_owned(),
        "/run/secrets/zato-pubsub-db-password".to_owned(),
    );
    let config = postgresql_config(&variables);
    assert_eq!(
        config.password,
        PostgreSqlPassword::File(PathBuf::from("/run/secrets/zato-pubsub-db-password"))
    );
}

#[test]
fn mutual_tls_reads_every_file_and_the_verification() {
    let mut variables = shared_storage();
    for (name, value) in [
        (ENV_PUBSUB_DB_SSL, "true"),
        (ENV_PUBSUB_DB_SSL_CA_FILE, "/tls/postgresql-ca.pem"),
        (ENV_PUBSUB_DB_SSL_CERT_FILE, "/tls/zato-a.pem"),
        (ENV_PUBSUB_DB_SSL_KEY_FILE, "/tls/zato-a.key"),
        (ENV_PUBSUB_DB_SSL_VERIFY, "false"),
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
    variables.0.insert(ENV_PUBSUB_DB_SSL.to_owned(), "true".to_owned());
    variables
        .0
        .insert(ENV_PUBSUB_DB_SSL_CERT_FILE.to_owned(), "/tls/zato-a.pem".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(error, ConfigError::Missing(ENV_PUBSUB_DB_SSL_KEY_FILE)));
}
