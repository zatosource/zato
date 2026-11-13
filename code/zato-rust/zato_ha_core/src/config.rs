// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Configuration of the node, read from `Zato_HA_*` environment variables.
//!
//! A deployment sets the mode, and every other variable overrides a default defined in this module. A pub/sub
//! database on `PostgreSQL` puts the node in the shared storage mode, in which both hosts use the one database,
//! nothing is replicated between them, and the node probes the database with the `Zato_PubSub_DB_*` variables
//! of the Zato server.

use std::path::{Path, PathBuf};
use std::time::Duration;

/// The environment variable that selects the high-availability mode.
pub const ENV_MODE: &str = "Zato_HA_Mode";

/// The only mode the node runs in.
pub const MODE_ACTIVE_STANDBY: &str = "active-standby";

/// The environment variable that selects the referee.
pub const ENV_REFEREE_TYPE: &str = "Zato_HA_Referee_Type";

/// The environment variable with the name of the `Lease` that holds the referee record.
pub const ENV_LEASE_NAME: &str = "Zato_HA_Lease_Name";

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

/// The environment variable with the type of the pub/sub database, shared with the Zato server.
pub const ENV_PUBSUB_DB_TYPE: &str = "Zato_PubSub_DB_Type";

/// The environment variable with the host of the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_HOST: &str = "Zato_PubSub_DB_Host";

/// The environment variable with the port of the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_PORT: &str = "Zato_PubSub_DB_Port";

/// The environment variable with the user name of the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_USERNAME: &str = "Zato_PubSub_DB_Username";

/// The environment variable with the password of the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_PASSWORD: &str = "Zato_PubSub_DB_Password";

/// The environment variable with the file whose content is the password of the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_PASSWORD_FILE: &str = "Zato_PubSub_DB_Password_File";

/// The environment variable with the name of the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_NAME: &str = "Zato_PubSub_DB_Name";

/// The environment variable that turns on TLS to the pub/sub database on `PostgreSQL`.
pub const ENV_PUBSUB_DB_SSL: &str = "Zato_PubSub_DB_SSL";

/// The environment variable with the CA file that the certificate of `PostgreSQL` is verified against.
pub const ENV_PUBSUB_DB_SSL_CA_FILE: &str = "Zato_PubSub_DB_SSL_CA_File";

/// The environment variable with the client certificate file of mutual TLS to `PostgreSQL`.
pub const ENV_PUBSUB_DB_SSL_CERT_FILE: &str = "Zato_PubSub_DB_SSL_Cert_File";

/// The environment variable with the client key file of mutual TLS to `PostgreSQL`.
pub const ENV_PUBSUB_DB_SSL_KEY_FILE: &str = "Zato_PubSub_DB_SSL_Key_File";

/// The environment variable that turns off the verification of the certificate of `PostgreSQL`.
pub const ENV_PUBSUB_DB_SSL_VERIFY: &str = "Zato_PubSub_DB_SSL_Verify";

/// The environment variable with the path of the common database, shared with the Zato server.
pub const ENV_COMMON_DB_PATH: &str = "Zato_Common_DB_Path";

/// The environment variable with the path of the audit log database, shared with the Zato server.
pub const ENV_AUDIT_DB_PATH: &str = "Zato_Audit_Log_DB_Name";

/// The environment variable with the log level filter of the node.
pub const ENV_LOG_LEVEL: &str = "Zato_HA_Log_Level";

/// The referee type backed by a `Lease` of the Kubernetes API server.
pub const REFEREE_TYPE_KUBERNETES: &str = "kubernetes";

/// The referee type when the variable is not set.
pub const DEFAULT_REFEREE_TYPE: &str = REFEREE_TYPE_KUBERNETES;

/// The name of the `Lease` of the referee record when the variable is not set.
pub const DEFAULT_LEASE_NAME: &str = "zato-ha";

/// The pub/sub database type of the Zato server that is a `SQLite` file on each host.
pub const PUBSUB_DB_TYPE_SQLITE: &str = "sqlite";

/// The pub/sub database type of the Zato server that both hosts share.
pub const PUBSUB_DB_TYPE_POSTGRESQL: &str = "postgresql";

/// The default port of `PostgreSQL`.
pub const DEFAULT_POSTGRESQL_PORT: u16 = 5432;

/// Whether TLS to `PostgreSQL` is on when the variable is not set, as in `zato.common.db_env.common`.
pub const DEFAULT_POSTGRESQL_SSL: bool = false;

/// Whether the certificate of `PostgreSQL` is verified when the variable is not set, as in `zato.common.db_env.common`.
pub const DEFAULT_POSTGRESQL_SSL_VERIFY: bool = true;

/// The values that a boolean variable reads as true, as in `zato.common.util.eval_`.
const TRUE_VALUES: [&str; 6] = ["true", "yes", "on", "y", "t", "1"];

/// The values that a boolean variable reads as false, as in `zato.common.util.eval_`.
const FALSE_VALUES: [&str; 6] = ["false", "no", "off", "n", "f", "0"];

/// The default port of the replication link.
pub const DEFAULT_REPLICATION_PORT: u16 = 35_200;

/// The default port of the role endpoint.
pub const DEFAULT_ROLE_PORT: u16 = 35_201;

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

/// The settings of the `Lease` referee.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct KubernetesConfig {
    /// The name of the `Lease` that holds the referee record, which also prefixes the leases of the addresses.
    pub lease_name: String,
}

/// The TLS settings of the connections to `PostgreSQL`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PostgreSqlTls {
    /// The CA file that the certificate of `PostgreSQL` is verified against, or the system store if not given.
    pub ca_file: Option<PathBuf>,

    /// The client certificate and key files of mutual TLS, if `PostgreSQL` requires a client certificate.
    pub client_files: Option<(PathBuf, PathBuf)>,

    /// Whether the certificate of `PostgreSQL` is verified.
    pub verify: bool,
}

/// The settings of the pub/sub database on `PostgreSQL`, which are those of the Zato server.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PostgreSqlConfig {
    /// The host of `PostgreSQL`.
    pub host: String,

    /// The port of `PostgreSQL`.
    pub port: u16,

    /// The user name.
    pub username: String,

    /// The password, read from a file on every connection if the file is given.
    pub password: PostgreSqlPassword,

    /// The name of the database.
    pub database: String,

    /// TLS, if it is on.
    pub tls: Option<PostgreSqlTls>,
}

/// Where the password of `PostgreSQL` comes from.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PostgreSqlPassword {
    /// The value of the password variable, empty if it is not set.
    Value(String),

    /// A file read again on every connection, so that a rotated password takes effect without a restart.
    File(PathBuf),
}

/// The referee selected by the configuration.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RefereeConfig {
    /// A `Lease` of the Kubernetes API server, written by JSON Patches that test its `resourceVersion`.
    Kubernetes(KubernetesConfig),
}

/// Where the databases of the Zato server are kept.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StorageMode {
    /// Each host keeps `SQLite` files, which the active node replicates to the standby.
    Replicated,

    /// Both hosts use one database on `PostgreSQL`, and the active node renews its lease on the referee record.
    Shared,
}

/// How the frames of a database reach the standby.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ShippingMode {
    /// Success is reported to a caller only after the standby synced the frames.
    Synchronous,

    /// The frames are shipped without a barrier, so the standby may lag behind the commits of the active node.
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
    /// The selected referee and its settings.
    pub referee: RefereeConfig,

    /// Where the databases of the Zato server are kept.
    pub storage: StorageMode,

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

    /// The files of mutual TLS on the replication link, which the shared storage mode does not open.
    pub tls: Option<TlsFiles>,

    /// The pub/sub database that the node probes, which only the shared storage mode has.
    pub shared_database: Option<PostgreSqlConfig>,

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

/// Returns a boolean from a variable or its default, reading the values that the Zato server reads.
fn boolean(source: &dyn VariableSource, name: &'static str, default: bool) -> Result<bool, ConfigError> {
    let Some(value) = source.variable(name) else {
        return Ok(default);
    };
    let normalized = value.trim().to_lowercase();
    if TRUE_VALUES.contains(&normalized.as_str()) {
        return Ok(true);
    }
    if FALSE_VALUES.contains(&normalized.as_str()) {
        return Ok(false);
    }
    Err(ConfigError::Invalid {
        name,
        reason: format!("`{value}` is neither true nor false"),
    })
}

/// Returns the TLS settings of `PostgreSQL`, or `None` if TLS is off.
fn postgresql_tls(source: &dyn VariableSource) -> Result<Option<PostgreSqlTls>, ConfigError> {
    if !boolean(source, ENV_PUBSUB_DB_SSL, DEFAULT_POSTGRESQL_SSL)? {
        return Ok(None);
    }

    // A client certificate is used only together with its key.
    let client_files = match (
        source.variable(ENV_PUBSUB_DB_SSL_CERT_FILE),
        source.variable(ENV_PUBSUB_DB_SSL_KEY_FILE),
    ) {
        (Some(certificate), Some(key)) => Some((PathBuf::from(certificate), PathBuf::from(key))),
        (None, None) => None,
        (Some(_), None) => return Err(ConfigError::Missing(ENV_PUBSUB_DB_SSL_KEY_FILE)),
        (None, Some(_)) => return Err(ConfigError::Missing(ENV_PUBSUB_DB_SSL_CERT_FILE)),
    };

    Ok(Some(PostgreSqlTls {
        ca_file: source.variable(ENV_PUBSUB_DB_SSL_CA_FILE).map(PathBuf::from),
        client_files,
        verify: boolean(source, ENV_PUBSUB_DB_SSL_VERIFY, DEFAULT_POSTGRESQL_SSL_VERIFY)?,
    }))
}

/// Returns the settings of the pub/sub database on `PostgreSQL`.
fn postgresql(source: &dyn VariableSource) -> Result<PostgreSqlConfig, ConfigError> {
    // A database that authenticates without a password is given an empty one.
    let password = source.variable(ENV_PUBSUB_DB_PASSWORD_FILE).map_or_else(
        || PostgreSqlPassword::Value(source.variable(ENV_PUBSUB_DB_PASSWORD).unwrap_or_default()),
        |path| PostgreSqlPassword::File(PathBuf::from(path)),
    );
    Ok(PostgreSqlConfig {
        host: required(source, ENV_PUBSUB_DB_HOST)?,
        port: port(source, ENV_PUBSUB_DB_PORT, DEFAULT_POSTGRESQL_PORT)?,
        username: required(source, ENV_PUBSUB_DB_USERNAME)?,
        password,
        database: required(source, ENV_PUBSUB_DB_NAME)?,
        tls: postgresql_tls(source)?,
    })
}

/// Returns the referee and its settings.
fn referee(source: &dyn VariableSource) -> Result<RefereeConfig, ConfigError> {
    let value = source.variable(ENV_REFEREE_TYPE).unwrap_or_else(|| DEFAULT_REFEREE_TYPE.to_owned());
    match value.as_str() {
        REFEREE_TYPE_KUBERNETES => Ok(RefereeConfig::Kubernetes(KubernetesConfig {
            lease_name: source.variable(ENV_LEASE_NAME).unwrap_or_else(|| DEFAULT_LEASE_NAME.to_owned()),
        })),
        _ => Err(ConfigError::Invalid {
            name: ENV_REFEREE_TYPE,
            reason: format!("unsupported referee type `{value}`"),
        }),
    }
}

/// Returns the storage mode, which the type of the pub/sub database of the Zato server decides.
fn storage_mode(source: &dyn VariableSource) -> Result<StorageMode, ConfigError> {
    let Some(value) = source.variable(ENV_PUBSUB_DB_TYPE) else {
        return Ok(StorageMode::Replicated);
    };
    match value.as_str() {
        PUBSUB_DB_TYPE_SQLITE => Ok(StorageMode::Replicated),
        PUBSUB_DB_TYPE_POSTGRESQL => Ok(StorageMode::Shared),
        _ => Err(ConfigError::Invalid {
            name: ENV_PUBSUB_DB_TYPE,
            reason: format!("unsupported pub/sub database type `{value}`"),
        }),
    }
}

/// Returns the files of mutual TLS on the replication link, which only the replicated storage mode opens.
fn link_tls(source: &dyn VariableSource, storage: StorageMode) -> Result<Option<TlsFiles>, ConfigError> {
    if storage == StorageMode::Shared {
        return Ok(None);
    }
    Ok(Some(TlsFiles {
        authority: PathBuf::from(required(source, ENV_TLS_CA_FILE)?),
        certificate: PathBuf::from(required(source, ENV_TLS_CERT_FILE)?),
        private_key: PathBuf::from(required(source, ENV_TLS_KEY_FILE)?),
    }))
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

        let referee = referee(source)?;
        let storage = storage_mode(source)?;

        let data_dir = match source.variable(ENV_DATA_DIR) {
            Some(dir) => PathBuf::from(dir),
            None => default_data_dir(source)?,
        };

        let node_name = node_name(source)?;
        let advertised_address = source.variable(ENV_ADVERTISED_ADDRESS).unwrap_or_else(|| node_name.clone());

        let tls = link_tls(source, storage)?;
        let shared_database = match storage {
            StorageMode::Shared => Some(postgresql(source)?),
            StorageMode::Replicated => None,
        };

        let barrier_socket = source
            .variable(ENV_BARRIER_SOCKET)
            .map_or_else(|| data_dir.join(BARRIER_SOCKET_FILE_NAME), PathBuf::from);

        Ok(Self {
            referee,
            storage,
            databases: databases(source, &data_dir),
            node_name,
            advertised_address,
            replication_port: port(source, ENV_REPLICATION_PORT, DEFAULT_REPLICATION_PORT)?,
            role_port: port(source, ENV_ROLE_PORT, DEFAULT_ROLE_PORT)?,
            tls,
            shared_database,
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
mod tests;
