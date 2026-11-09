// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Configuration of the node, read from `Zato_HA_*` environment variables.
//!
//! A deployment sets the mode, the referee type, the Consul address and the Consul token,
//! and every other variable overrides a default defined in this module.

use std::path::{Path, PathBuf};
use std::time::Duration;

/// The environment variable that selects the high-availability mode.
pub const ENV_MODE: &str = "Zato_HA_Mode";

/// The only mode the node runs in.
pub const MODE_ACTIVE_STANDBY: &str = "active-standby";

/// The environment variable that selects the referee.
pub const ENV_REFEREE_TYPE: &str = "Zato_HA_Referee_Type";

/// The environment variable with the address of the Consul agent, e.g. `https://consul:8501`.
pub const ENV_CONSUL_ADDRESS: &str = "Zato_HA_Consul_Address";

/// The environment variable with the Consul ACL token.
pub const ENV_CONSUL_TOKEN: &str = "Zato_HA_Consul_Token";

/// The environment variable with the CA file that the certificate of Consul is verified against.
pub const ENV_CONSUL_CA_FILE: &str = "Zato_HA_Consul_CA_File";

/// The environment variable with the Consul key of the referee record.
pub const ENV_CONSUL_KEY: &str = "Zato_HA_Consul_Key";

/// The environment variable with the name of this node.
pub const ENV_NODE_NAME: &str = "Zato_HA_Node_Name";

/// The environment variable with the address under which the other node reaches this one.
pub const ENV_ADVERTISED_ADDRESS: &str = "Zato_HA_Advertised_Address";

/// The environment variable with the port of the replication link.
pub const ENV_REPLICATION_PORT: &str = "Zato_HA_Replication_Port";

/// The environment variable with the port of the role endpoint.
pub const ENV_ROLE_PORT: &str = "Zato_HA_Role_Port";

/// The environment variable with the directory of the databases and of the node's own files.
pub const ENV_DATA_DIR: &str = "Zato_HA_Data_Dir";

/// The environment variable with the CA file of the replication link.
pub const ENV_TLS_CA_FILE: &str = "Zato_HA_TLS_CA_File";

/// The environment variable with the certificate file of this node on the replication link.
pub const ENV_TLS_CERT_FILE: &str = "Zato_HA_TLS_Cert_File";

/// The environment variable with the private key file of this node on the replication link.
pub const ENV_TLS_KEY_FILE: &str = "Zato_HA_TLS_Key_File";

/// The environment variable with the interval of heartbeats, in seconds.
pub const ENV_HEARTBEAT_TIME: &str = "Zato_HA_Heartbeat_Time";

/// The environment variable with the time after which the active node marks the standby out, in seconds.
pub const ENV_MARK_OUT_TIME: &str = "Zato_HA_Mark_Out_Time";

/// The environment variable with the time after which the standby attempts a takeover, in seconds.
pub const ENV_TAKEOVER_TIME: &str = "Zato_HA_Takeover_Time";

/// The environment variable with the path of the Unix socket of the replication barrier.
pub const ENV_BARRIER_SOCKET: &str = "Zato_HA_Barrier_Socket";

/// The environment variable through which the node passes its generation to the Zato server.
pub const ENV_GENERATION: &str = "Zato_HA_Generation";

/// The environment variable with the path of the pub/sub database, shared with the Zato server.
pub const ENV_PUBSUB_DB_PATH: &str = "Zato_PubSub_DB_Path";

/// The environment variable with the path of the common database, shared with the Zato server.
pub const ENV_COMMON_DB_PATH: &str = "Zato_Common_DB_Path";

/// The environment variable with the path of the audit log database, shared with the Zato server.
pub const ENV_AUDIT_DB_PATH: &str = "Zato_Audit_Log_DB_Name";

/// The environment variable with the log level filter of the node.
pub const ENV_LOG_LEVEL: &str = "Zato_HA_Log_Level";

/// The referee type backed by Consul.
pub const REFEREE_TYPE_CONSUL: &str = "consul";

/// The default port of the replication link.
pub const DEFAULT_REPLICATION_PORT: u16 = 35_200;

/// The default port of the role endpoint.
pub const DEFAULT_ROLE_PORT: u16 = 35_201;

/// The default Consul key of the referee record.
pub const DEFAULT_CONSUL_KEY: &str = "zato/ha/default";

/// The default directory of the databases, relative to the home directory, as in `zato.common.defaults`.
pub const DEFAULT_DATA_DIR_UNDER_HOME: &str = "env/qs-1";

/// The default heartbeat interval, in seconds.
pub const DEFAULT_HEARTBEAT_TIME: f64 = 0.5;

/// The default mark-out time, in seconds.
pub const DEFAULT_MARK_OUT_TIME: f64 = 3.0;

/// The default takeover time, in seconds.
pub const DEFAULT_TAKEOVER_TIME: f64 = 6.0;

/// The default log level filter.
pub const DEFAULT_LOG_LEVEL: &str = "info";

/// The file name of the pub/sub database.
pub const PUBSUB_DB_FILE_NAME: &str = "pubsub.db";

/// The file name of the common database.
pub const COMMON_DB_FILE_NAME: &str = "common.db";

/// The file name of the audit log database.
pub const AUDIT_DB_FILE_NAME: &str = "audit.db";

/// The file name of the barrier socket in the data directory.
pub const BARRIER_SOCKET_FILE_NAME: &str = "ha-barrier.sock";

/// The file name of the highest generation this node has seen, in the data directory.
pub const GENERATION_FILE_NAME: &str = "ha-generation";

/// The name under which the barrier refers to the pub/sub database.
pub const DB_NAME_PUBSUB: &str = "pubsub";

/// The name under which the barrier refers to the common database.
pub const DB_NAME_COMMON: &str = "common";

/// The name under which the replication link refers to the audit log database.
pub const DB_NAME_AUDIT: &str = "audit";

/// Errors that stop the node at startup.
#[derive(Debug)]
pub enum ConfigError {
    /// A required variable is not set.
    Missing(&'static str),

    /// A variable has a value that cannot be used.
    Invalid {
        /// The name of the variable.
        name: &'static str,

        /// What is wrong with the value.
        reason: String,
    },
}

impl std::fmt::Display for ConfigError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Missing(name) => write!(formatter, "Environment variable {name} is required"),
            Self::Invalid { name, reason } => write!(formatter, "Environment variable {name} is invalid: {reason}"),
        }
    }
}

impl std::error::Error for ConfigError {}

/// The referee selected by the configuration.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RefereeType {
    /// Consul KV with check-and-set writes.
    Consul,
}

/// How the frames of a database reach the standby.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ShippingMode {
    /// Success is reported to a caller only after the standby synced the frames.
    Synchronous,

    /// The frames are shipped without a barrier, and the standby keeps them in a copy named after the active node.
    Asynchronous,
}

/// One replicated database.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DatabaseConfig {
    /// The name of the database on the replication link and in the barrier.
    pub name: &'static str,

    /// The path of the database file.
    pub path: PathBuf,

    /// How its frames reach the standby.
    pub shipping: ShippingMode,
}

impl DatabaseConfig {
    /// Returns the path under which the standby keeps the copy of this database written by `active_node`.
    pub fn copy_path(&self, active_node: &str) -> PathBuf {
        match self.shipping {
            ShippingMode::Synchronous => self.path.clone(),
            ShippingMode::Asynchronous => {
                let stem = file_stem(&self.path);
                let file_name = format!("{stem}-{active_node}.db");
                self.path.with_file_name(file_name)
            }
        }
    }
}

/// Returns the file name of a path without its extension.
fn file_stem(path: &Path) -> String {
    let stem = path.file_stem().unwrap_or_default();
    stem.to_string_lossy().into_owned()
}

/// The files of mutual TLS on the replication link.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TlsFiles {
    /// The CA file that both certificates are issued by.
    pub authority: PathBuf,

    /// The certificate file of this node, whose DNS name is the node name.
    pub certificate: PathBuf,

    /// The private key file of this node.
    pub private_key: PathBuf,
}

/// The timers of the node.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Timers {
    /// How often the active node sends a heartbeat.
    pub heartbeat: Duration,

    /// How long the active node waits for a confirmation before it marks the standby out.
    pub mark_out: Duration,

    /// How long the standby waits for a frame or a heartbeat before it attempts a takeover.
    pub takeover: Duration,
}

/// The complete configuration of the node.
#[derive(Debug, Clone)]
pub struct NodeConfig {
    /// The selected referee.
    pub referee_type: RefereeType,

    /// The address of the Consul agent.
    pub consul_address: String,

    /// The Consul ACL token.
    pub consul_token: String,

    /// The CA file for the certificate of Consul, if Consul is reached over TLS with a private CA.
    pub consul_ca_file: Option<PathBuf>,

    /// The Consul key of the referee record.
    pub consul_key: String,

    /// The name of this node.
    pub node_name: String,

    /// The host name or address under which the other node reaches this one.
    pub advertised_address: String,

    /// The port of the replication link.
    pub replication_port: u16,

    /// The port of the role endpoint.
    pub role_port: u16,

    /// The directory of the node's own files.
    pub data_dir: PathBuf,

    /// The files of mutual TLS on the replication link.
    pub tls: TlsFiles,

    /// The timers.
    pub timers: Timers,

    /// The replicated databases.
    pub databases: Vec<DatabaseConfig>,

    /// The path of the barrier socket.
    pub barrier_socket: PathBuf,

    /// The log level filter.
    pub log_level: String,
}

/// A source of variables, which is the process environment in production and a map in tests.
pub trait VariableSource {
    /// Returns the value of a variable, if it is set and not empty.
    fn variable(&self, name: &str) -> Option<String>;
}

/// The process environment.
pub struct ProcessEnvironment;

impl VariableSource for ProcessEnvironment {
    fn variable(&self, name: &str) -> Option<String> {
        std::env::var(name).ok().filter(|value| !value.is_empty())
    }
}

/// Returns a required variable.
fn required(source: &dyn VariableSource, name: &'static str) -> Result<String, ConfigError> {
    source.variable(name).ok_or(ConfigError::Missing(name))
}

/// Returns a port from a variable or its default.
fn port(source: &dyn VariableSource, name: &'static str, default: u16) -> Result<u16, ConfigError> {
    let Some(value) = source.variable(name) else {
        return Ok(default);
    };
    value.parse::<u16>().map_err(|error| ConfigError::Invalid {
        name,
        reason: error.to_string(),
    })
}

/// Returns a time in seconds, fractions allowed, from a variable or its default.
fn seconds(source: &dyn VariableSource, name: &'static str, default: f64) -> Result<Duration, ConfigError> {
    let value = match source.variable(name) {
        Some(text) => text.parse::<f64>().map_err(|error| ConfigError::Invalid {
            name,
            reason: error.to_string(),
        })?,
        None => default,
    };

    // A zero or negative timer would make the node act on every tick.
    Duration::try_from_secs_f64(value)
        .ok()
        .filter(|duration| !duration.is_zero())
        .ok_or_else(|| ConfigError::Invalid {
            name,
            reason: format!("{value} is not a positive number of seconds"),
        })
}

/// Returns the referee type.
fn referee_type(source: &dyn VariableSource) -> Result<RefereeType, ConfigError> {
    let value = required(source, ENV_REFEREE_TYPE)?;
    match value.as_str() {
        REFEREE_TYPE_CONSUL => Ok(RefereeType::Consul),
        _ => Err(ConfigError::Invalid {
            name: ENV_REFEREE_TYPE,
            reason: format!("unsupported referee type `{value}`"),
        }),
    }
}

/// Returns the timers, refusing a takeover time that does not exceed the mark-out time.
fn timers(source: &dyn VariableSource) -> Result<Timers, ConfigError> {
    let out = Timers {
        heartbeat: seconds(source, ENV_HEARTBEAT_TIME, DEFAULT_HEARTBEAT_TIME)?,
        mark_out: seconds(source, ENV_MARK_OUT_TIME, DEFAULT_MARK_OUT_TIME)?,
        takeover: seconds(source, ENV_TAKEOVER_TIME, DEFAULT_TAKEOVER_TIME)?,
    };

    // The active node must stop acknowledging before the standby may take over.
    if out.takeover <= out.mark_out {
        return Err(ConfigError::Invalid {
            name: ENV_TAKEOVER_TIME,
            reason: format!(
                "{} seconds does not exceed {ENV_MARK_OUT_TIME} of {} seconds",
                out.takeover.as_secs_f64(),
                out.mark_out.as_secs_f64()
            ),
        });
    }

    Ok(out)
}

/// Returns the default data directory under the home directory.
fn default_data_dir(source: &dyn VariableSource) -> Result<PathBuf, ConfigError> {
    let home = source.variable("HOME").ok_or(ConfigError::Missing("HOME"))?;
    Ok(Path::new(&home).join(DEFAULT_DATA_DIR_UNDER_HOME))
}

/// Returns the node name, which defaults to the host name.
fn node_name(source: &dyn VariableSource) -> Result<String, ConfigError> {
    if let Some(name) = source.variable(ENV_NODE_NAME) {
        return Ok(name);
    }
    let host_name = std::fs::read_to_string("/proc/sys/kernel/hostname").map_err(|error| ConfigError::Invalid {
        name: ENV_NODE_NAME,
        reason: error.to_string(),
    })?;
    Ok(host_name.trim().to_owned())
}

/// Returns the replicated databases, with the paths that the Zato server uses.
fn databases(source: &dyn VariableSource, data_dir: &Path) -> Vec<DatabaseConfig> {
    let path_of = |name: &str, file_name: &str| source.variable(name).map_or_else(|| data_dir.join(file_name), PathBuf::from);
    vec![
        DatabaseConfig {
            name: DB_NAME_PUBSUB,
            path: path_of(ENV_PUBSUB_DB_PATH, PUBSUB_DB_FILE_NAME),
            shipping: ShippingMode::Synchronous,
        },
        DatabaseConfig {
            name: DB_NAME_COMMON,
            path: path_of(ENV_COMMON_DB_PATH, COMMON_DB_FILE_NAME),
            shipping: ShippingMode::Synchronous,
        },
        DatabaseConfig {
            name: DB_NAME_AUDIT,
            path: path_of(ENV_AUDIT_DB_PATH, AUDIT_DB_FILE_NAME),
            shipping: ShippingMode::Asynchronous,
        },
    ]
}

impl NodeConfig {
    /// Reads the configuration from a source of variables.
    pub fn from_source(source: &dyn VariableSource) -> Result<Self, ConfigError> {
        let mode = required(source, ENV_MODE)?;
        if mode != MODE_ACTIVE_STANDBY {
            return Err(ConfigError::Invalid {
                name: ENV_MODE,
                reason: format!("`{mode}` is not {MODE_ACTIVE_STANDBY}"),
            });
        }

        let referee_type = referee_type(source)?;
        let consul_address = required(source, ENV_CONSUL_ADDRESS)?;
        let consul_token = required(source, ENV_CONSUL_TOKEN)?;

        let data_dir = match source.variable(ENV_DATA_DIR) {
            Some(dir) => PathBuf::from(dir),
            None => default_data_dir(source)?,
        };

        let node_name = node_name(source)?;
        let advertised_address = source.variable(ENV_ADVERTISED_ADDRESS).unwrap_or_else(|| node_name.clone());

        let tls = TlsFiles {
            authority: PathBuf::from(required(source, ENV_TLS_CA_FILE)?),
            certificate: PathBuf::from(required(source, ENV_TLS_CERT_FILE)?),
            private_key: PathBuf::from(required(source, ENV_TLS_KEY_FILE)?),
        };

        let barrier_socket = source
            .variable(ENV_BARRIER_SOCKET)
            .map_or_else(|| data_dir.join(BARRIER_SOCKET_FILE_NAME), PathBuf::from);

        Ok(Self {
            referee_type,
            consul_address,
            consul_token,
            consul_ca_file: source.variable(ENV_CONSUL_CA_FILE).map(PathBuf::from),
            consul_key: source.variable(ENV_CONSUL_KEY).unwrap_or_else(|| DEFAULT_CONSUL_KEY.to_owned()),
            databases: databases(source, &data_dir),
            node_name,
            advertised_address,
            replication_port: port(source, ENV_REPLICATION_PORT, DEFAULT_REPLICATION_PORT)?,
            role_port: port(source, ENV_ROLE_PORT, DEFAULT_ROLE_PORT)?,
            tls,
            timers: timers(source)?,
            barrier_socket,
            log_level: source.variable(ENV_LOG_LEVEL).unwrap_or_else(|| DEFAULT_LOG_LEVEL.to_owned()),
            data_dir,
        })
    }

    /// Returns the path of the file with the highest generation this node has seen.
    pub fn generation_file(&self) -> PathBuf {
        self.data_dir.join(GENERATION_FILE_NAME)
    }

    /// Returns the replicated database with the given name.
    pub fn database(&self, name: &str) -> Option<&DatabaseConfig> {
        self.databases.iter().find(|database| database.name == name)
    }
}

#[cfg(test)]
mod tests {
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

    #[test]
    fn audit_copy_is_named_after_the_writer() {
        let config = NodeConfig::from_source(&minimal()).unwrap();
        let audit = config.database(DB_NAME_AUDIT).unwrap();
        assert_eq!(audit.copy_path("zato-b"), PathBuf::from("/home/zato/env/qs-1/audit-zato-b.db"));
    }
}
