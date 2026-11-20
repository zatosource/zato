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

#[test]
fn defaults_apply() {
    let config = NodeConfig::from_source(&minimal()).unwrap();
    assert_eq!(config.role_port, DEFAULT_ROLE_PORT);
    assert_eq!(config.server_port, DEFAULT_SERVER_PORT);
    assert_eq!(config.timers.takeover, Duration::from_secs(6));
    assert_eq!(config.data_dir, PathBuf::from("/home/zato/env/qs-1"));
    assert_eq!(
        config.referee,
        RefereeConfig::Kubernetes(KubernetesConfig {
            lease_name: DEFAULT_LEASE_NAME.to_owned()
        })
    );
}

#[test]
fn the_request_timeout_is_half_the_takeover_time() {
    // The default timers allow three seconds per request ..
    let config = NodeConfig::from_source(&minimal()).unwrap();
    assert_eq!(config.timers.request_timeout(), Duration::from_secs(3));

    // .. and a custom takeover time changes the request timeout with it.
    let mut variables = minimal();
    variables.0.insert(ENV_TAKEOVER_TIME.to_owned(), "10".to_owned());
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(config.timers.request_timeout(), Duration::from_secs(5));
}

#[test]
fn the_server_port_is_read() {
    let mut variables = minimal();
    variables.0.insert(ENV_SERVER_PORT.to_owned(), "17020".to_owned());
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(config.server_port, 17_020);
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

/// Returns the settings of the Zato database read from `variables`.
fn postgresql_config(variables: &Variables) -> PostgreSqlConfig {
    NodeConfig::from_source(variables).unwrap().database
}

#[test]
fn the_database_is_read() {
    assert_eq!(
        postgresql_config(&minimal()),
        PostgreSqlConfig {
            host: "postgresql".to_owned(),
            port: DEFAULT_POSTGRESQL_PORT,
            username: "zato".to_owned(),
            password: PostgreSqlPassword::Value("Test password".to_owned()),
            database: "zato".to_owned(),
            tls: None,
        }
    );
}

#[test]
fn the_password_file_is_preferred_to_the_password() {
    let mut variables = minimal();
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
    let mut variables = minimal();
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
    let mut variables = minimal();
    variables.0.insert(ENV_DATABASE_SSL.to_owned(), "true".to_owned());
    variables
        .0
        .insert(ENV_DATABASE_SSL_CERT_FILE.to_owned(), "/tls/zato-a.pem".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(error, ConfigError::Missing(ENV_DATABASE_SSL_KEY_FILE)));
}

#[test]
fn the_health_of_the_server_has_defaults() {
    let config = NodeConfig::from_source(&minimal()).unwrap();
    assert_eq!(config.server_health, ServerHealthConfig::from_defaults());
    assert!(config.server_health.hold_off > config.timers.takeover);
}

#[test]
fn the_health_of_the_server_is_read() {
    let mut variables = minimal();
    let pairs = [
        (ENV_SERVER_LIVENESS_TIMEOUT, "15"),
        (ENV_SERVER_START_TIMEOUT, "120"),
        (ENV_SERVER_EXIT_LIMIT, "5"),
        (ENV_SERVER_EXIT_WINDOW, "90"),
        (ENV_RESIGN_HOLD_OFF, "30"),
        (ENV_RESIGN_HOLD_OFF_MAX, "600"),
    ];
    for (name, value) in pairs {
        variables.0.insert(name.to_owned(), value.to_owned());
    }
    let config = NodeConfig::from_source(&variables).unwrap();
    assert_eq!(
        config.server_health,
        ServerHealthConfig {
            liveness_timeout: Duration::from_secs(15),
            start_timeout: Duration::from_mins(2),
            exit_limit: 5,
            exit_window: Duration::from_secs(90),
            hold_off: Duration::from_secs(30),
            hold_off_max: Duration::from_mins(10),
        }
    );
}

#[test]
fn an_exit_limit_of_zero_is_refused() {
    let mut variables = minimal();
    variables.0.insert(ENV_SERVER_EXIT_LIMIT.to_owned(), "0".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_SERVER_EXIT_LIMIT,
            ..
        }
    ));
}

#[test]
fn a_hold_off_not_longer_than_the_takeover_time_is_refused() {
    let mut variables = minimal();
    variables.0.insert(ENV_TAKEOVER_TIME.to_owned(), "6".to_owned());
    variables.0.insert(ENV_RESIGN_HOLD_OFF.to_owned(), "6".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_RESIGN_HOLD_OFF,
            ..
        }
    ));
}

#[test]
fn a_longest_hold_off_below_the_hold_off_is_refused() {
    let mut variables = minimal();
    variables.0.insert(ENV_RESIGN_HOLD_OFF.to_owned(), "30".to_owned());
    variables.0.insert(ENV_RESIGN_HOLD_OFF_MAX.to_owned(), "20".to_owned());
    let error = NodeConfig::from_source(&variables).unwrap_err();
    assert!(matches!(
        error,
        ConfigError::Invalid {
            name: ENV_RESIGN_HOLD_OFF_MAX,
            ..
        }
    ));
}
