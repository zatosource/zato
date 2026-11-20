// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Configuration of the node, read from `Zato_HA_*` environment variables.
//!
//! A deployment sets the mode and the Zato database, and every other variable overrides a default defined in this
//! module. Both hosts use one Zato database on `PostgreSQL`, which the node probes with the `Zato_Database_*`
//! variables of the Zato server.

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

/// The environment variable with the port of the role endpoint.
pub const ENV_ROLE_PORT: &str = "Zato_HA_Role_Port";

/// The environment variable with the directory of the node's own files.
pub const ENV_DATA_DIR: &str = "Zato_HA_Data_Dir";

/// The environment variable with the interval of heartbeats, in seconds.
pub const ENV_HEARTBEAT_TIME: &str = "Zato_HA_Heartbeat_Time";

/// The environment variable with the time after which the standby attempts a takeover, in seconds.
pub const ENV_TAKEOVER_TIME: &str = "Zato_HA_Takeover_Time";

/// The environment variable with the port of the Zato server, which the server itself reads.
pub const ENV_SERVER_PORT: &str = "Zato_Config_Bind_Port";

/// The environment variable through which the node passes its generation to the Zato server.
pub const ENV_GENERATION: &str = "Zato_HA_Generation";

/// The environment variable with the FIFO through which the node delivers its generation to a warm Zato server,
/// which waits for it before it runs any startup hook or opens the Zato database.
pub const ENV_ACTIVATION_PATH: &str = "Zato_HA_Activation_Path";

/// The environment variable with the host of the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_HOST: &str = "Zato_Database_Host";

/// The environment variable with the port of the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_PORT: &str = "Zato_Database_Port";

/// The environment variable with the user name of the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_USERNAME: &str = "Zato_Database_Username";

/// The environment variable with the password of the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_PASSWORD: &str = "Zato_Database_Password";

/// The environment variable with the file whose content is the password of the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_PASSWORD_FILE: &str = "Zato_Database_Password_File";

/// The environment variable with the name of the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_NAME: &str = "Zato_Database_Name";

/// The environment variable that turns on TLS to the Zato database on `PostgreSQL`.
pub const ENV_DATABASE_SSL: &str = "Zato_Database_SSL";

/// The environment variable with the CA file that the certificate of `PostgreSQL` is verified against.
pub const ENV_DATABASE_SSL_CA_FILE: &str = "Zato_Database_SSL_CA_File";

/// The environment variable with the client certificate file of mutual TLS to `PostgreSQL`.
pub const ENV_DATABASE_SSL_CERT_FILE: &str = "Zato_Database_SSL_Cert_File";

/// The environment variable with the client key file of mutual TLS to `PostgreSQL`.
pub const ENV_DATABASE_SSL_KEY_FILE: &str = "Zato_Database_SSL_Key_File";

/// The environment variable that turns off the verification of the certificate of `PostgreSQL`.
pub const ENV_DATABASE_SSL_VERIFY: &str = "Zato_Database_SSL_Verify";

/// The environment variable with the log level filter of the node.
pub const ENV_LOG_LEVEL: &str = "Zato_HA_Log_Level";

/// The environment variable with how long a Zato server that has answered may remain without an answer before the node
/// resigns, in seconds.
pub const ENV_SERVER_LIVENESS_TIMEOUT: &str = "Zato_HA_Server_Liveness_Timeout";

/// The environment variable with how long a started Zato server may take to answer for the first time before the node
/// resigns, in seconds.
pub const ENV_SERVER_START_TIMEOUT: &str = "Zato_HA_Server_Start_Timeout";

/// The environment variable with how many exits of the Zato server within the exit window make the node resign.
pub const ENV_SERVER_EXIT_LIMIT: &str = "Zato_HA_Server_Exit_Limit";

/// The environment variable with the window in which the exits of the Zato server are counted, in seconds.
pub const ENV_SERVER_EXIT_WINDOW: &str = "Zato_HA_Server_Exit_Window";

/// The environment variable with how long a node that resigned waits before it may take over again, in seconds.
pub const ENV_RESIGN_HOLD_OFF: &str = "Zato_HA_Resign_Hold_Off";

/// The environment variable with the longest hold-off that consecutive resignations reach, in seconds.
pub const ENV_RESIGN_HOLD_OFF_MAX: &str = "Zato_HA_Resign_Hold_Off_Max";

/// The referee type backed by a `Lease` of the Kubernetes API server.
pub const REFEREE_TYPE_KUBERNETES: &str = "kubernetes";

/// The referee type when the variable is not set.
pub const DEFAULT_REFEREE_TYPE: &str = REFEREE_TYPE_KUBERNETES;

/// The name of the `Lease` of the referee record when the variable is not set.
pub const DEFAULT_LEASE_NAME: &str = "zato-ha";

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

/// The default port of the role endpoint.
pub const DEFAULT_ROLE_PORT: u16 = 35_201;

/// The default port of the Zato server, as in the configuration of a new server.
pub const DEFAULT_SERVER_PORT: u16 = 17_010;

/// The default directory of the node's own files, relative to the home directory, as in `zato.common.defaults`.
pub const DEFAULT_DATA_DIR_UNDER_HOME: &str = "env/qs-1";

/// The default heartbeat interval, in seconds.
pub const DEFAULT_HEARTBEAT_TIME: f64 = 0.5;

/// The default takeover time, in seconds.
pub const DEFAULT_TAKEOVER_TIME: f64 = 6.0;

/// The default log level filter.
pub const DEFAULT_LOG_LEVEL: &str = "info";

/// How often the node sends `GET /zato/ping` to a Zato server that has answered.
pub const SERVER_PING_INTERVAL: Duration = Duration::from_secs(1);

/// How long one ping of a Zato server that has answered may take before it counts as unanswered.
///
/// The slowest ping of a server under 16 publishers and 16 subscribers of pub/sub measures 55 ms on `PostgreSQL` 19,
/// so the timeout exceeds it more than 30 times.
pub const SERVER_PING_TIMEOUT: Duration = Duration::from_secs(2);

/// The default liveness timeout of the Zato server, in seconds.
///
/// The timeout spans several unanswered pings, so that one slow answer does not fail a server that answers the pings
/// after it. It is below the 30 s after which the arbiter of the server replaces a worker without a heartbeat,
/// so that the node resigns before a hung worker is replaced.
pub const DEFAULT_SERVER_LIVENESS_TIMEOUT: f64 = 10.0;

/// The default start timeout of the Zato server, in seconds.
///
/// The timeout equals the time that the arbiter of the server gives a starting worker, so that the node never cuts
/// short a start that the server itself permits.
pub const DEFAULT_SERVER_START_TIMEOUT: f64 = 300.0;

/// The default number of exits of the Zato server within the exit window after which the node resigns.
pub const DEFAULT_SERVER_EXIT_LIMIT: u32 = 3;

/// The default window in which the exits of the Zato server are counted, in seconds.
pub const DEFAULT_SERVER_EXIT_WINDOW: f64 = 60.0;

/// The default hold-off of a node that resigned, in seconds, which exceeds the default takeover time,
/// so that the standby takes over before the node that resigned may.
pub const DEFAULT_RESIGN_HOLD_OFF: f64 = 20.0;

/// The default longest hold-off of consecutive resignations, in seconds.
pub const DEFAULT_RESIGN_HOLD_OFF_MAX: f64 = 300.0;

/// The file name of the highest generation this node has seen, in the data directory.
pub const GENERATION_FILE_NAME: &str = "ha-generation";

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
    /// The name of the `Lease` that holds the referee record, which also prefixes the leases of the nodes.
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

/// The settings of the Zato database on `PostgreSQL`, which are those of the Zato server.
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

/// The timers of the node.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Timers {
    /// How often the active node renews its lease and the standby reads it.
    pub heartbeat: Duration,

    /// How long the standby waits for a renewal of the lease before it attempts a takeover.
    pub takeover: Duration,
}

/// How the node decides that its Zato server failed and how long it holds off after it resigned.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ServerHealthConfig {
    /// How long a server that has answered may remain without an answer.
    pub liveness_timeout: Duration,

    /// How long a started server may take to answer for the first time.
    pub start_timeout: Duration,

    /// How many exits of the server within the exit window count as a failure.
    pub exit_limit: u32,

    /// The window in which the exits of the server are counted, and the time for which a server that answers
    /// without a failure resets the hold-off.
    pub exit_window: Duration,

    /// How long a node that resigned waits before it may take over again.
    pub hold_off: Duration,

    /// The longest hold-off that consecutive resignations reach.
    pub hold_off_max: Duration,
}

impl ServerHealthConfig {
    /// Returns the defaults of every setting.
    pub fn from_defaults() -> Self {
        Self {
            liveness_timeout: Duration::from_secs_f64(DEFAULT_SERVER_LIVENESS_TIMEOUT),
            start_timeout: Duration::from_secs_f64(DEFAULT_SERVER_START_TIMEOUT),
            exit_limit: DEFAULT_SERVER_EXIT_LIMIT,
            exit_window: Duration::from_secs_f64(DEFAULT_SERVER_EXIT_WINDOW),
            hold_off: Duration::from_secs_f64(DEFAULT_RESIGN_HOLD_OFF),
            hold_off_max: Duration::from_secs_f64(DEFAULT_RESIGN_HOLD_OFF_MAX),
        }
    }
}

/// The complete configuration of the node.
#[derive(Debug, Clone)]
pub struct NodeConfig {
    /// The selected referee and its settings.
    pub referee: RefereeConfig,

    /// The name of this node.
    pub node_name: String,

    /// The port of the role endpoint.
    pub role_port: u16,

    /// The port on which the Zato server answers its ping endpoint on the loopback address.
    pub server_port: u16,

    /// The directory of the node's own files.
    pub data_dir: PathBuf,

    /// The Zato database that the node probes.
    pub database: PostgreSqlConfig,

    /// The timers.
    pub timers: Timers,

    /// The thresholds of the health of the Zato server and the hold-off after a resignation.
    pub server_health: ServerHealthConfig,

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
    if !boolean(source, ENV_DATABASE_SSL, DEFAULT_POSTGRESQL_SSL)? {
        return Ok(None);
    }

    // A client certificate is used only together with its key.
    let client_files = match (
        source.variable(ENV_DATABASE_SSL_CERT_FILE),
        source.variable(ENV_DATABASE_SSL_KEY_FILE),
    ) {
        (Some(certificate), Some(key)) => Some((PathBuf::from(certificate), PathBuf::from(key))),
        (None, None) => None,
        (Some(_), None) => return Err(ConfigError::Missing(ENV_DATABASE_SSL_KEY_FILE)),
        (None, Some(_)) => return Err(ConfigError::Missing(ENV_DATABASE_SSL_CERT_FILE)),
    };

    Ok(Some(PostgreSqlTls {
        ca_file: source.variable(ENV_DATABASE_SSL_CA_FILE).map(PathBuf::from),
        client_files,
        verify: boolean(source, ENV_DATABASE_SSL_VERIFY, DEFAULT_POSTGRESQL_SSL_VERIFY)?,
    }))
}

/// Returns the settings of the Zato database on `PostgreSQL`.
fn postgresql(source: &dyn VariableSource) -> Result<PostgreSqlConfig, ConfigError> {
    // A database that authenticates without a password is given an empty one.
    let password = source.variable(ENV_DATABASE_PASSWORD_FILE).map_or_else(
        || PostgreSqlPassword::Value(source.variable(ENV_DATABASE_PASSWORD).unwrap_or_default()),
        |path| PostgreSqlPassword::File(PathBuf::from(path)),
    );
    Ok(PostgreSqlConfig {
        host: required(source, ENV_DATABASE_HOST)?,
        port: port(source, ENV_DATABASE_PORT, DEFAULT_POSTGRESQL_PORT)?,
        username: required(source, ENV_DATABASE_USERNAME)?,
        password,
        database: required(source, ENV_DATABASE_NAME)?,
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

/// Returns the timers.
fn timers(source: &dyn VariableSource) -> Result<Timers, ConfigError> {
    Ok(Timers {
        heartbeat: seconds(source, ENV_HEARTBEAT_TIME, DEFAULT_HEARTBEAT_TIME)?,
        takeover: seconds(source, ENV_TAKEOVER_TIME, DEFAULT_TAKEOVER_TIME)?,
    })
}

/// Returns a positive count from a variable or its default.
fn count(source: &dyn VariableSource, name: &'static str, default: u32) -> Result<u32, ConfigError> {
    let Some(value) = source.variable(name) else {
        return Ok(default);
    };
    let parsed = value.parse::<u32>().map_err(|error| ConfigError::Invalid {
        name,
        reason: error.to_string(),
    })?;

    // A limit of zero would count every server as failed before it ever exited.
    if parsed == 0 {
        return Err(ConfigError::Invalid {
            name,
            reason: "0 is not a positive count".to_owned(),
        });
    }
    Ok(parsed)
}

/// Returns the thresholds of the health of the Zato server, refusing a hold-off that the takeover of the standby
/// would not precede.
fn server_health(source: &dyn VariableSource, takeover: Duration) -> Result<ServerHealthConfig, ConfigError> {
    let out = ServerHealthConfig {
        liveness_timeout: seconds(source, ENV_SERVER_LIVENESS_TIMEOUT, DEFAULT_SERVER_LIVENESS_TIMEOUT)?,
        start_timeout: seconds(source, ENV_SERVER_START_TIMEOUT, DEFAULT_SERVER_START_TIMEOUT)?,
        exit_limit: count(source, ENV_SERVER_EXIT_LIMIT, DEFAULT_SERVER_EXIT_LIMIT)?,
        exit_window: seconds(source, ENV_SERVER_EXIT_WINDOW, DEFAULT_SERVER_EXIT_WINDOW)?,
        hold_off: seconds(source, ENV_RESIGN_HOLD_OFF, DEFAULT_RESIGN_HOLD_OFF)?,
        hold_off_max: seconds(source, ENV_RESIGN_HOLD_OFF_MAX, DEFAULT_RESIGN_HOLD_OFF_MAX)?,
    };

    // A node that resigned would otherwise take its own lease over again before the standby does.
    if out.hold_off <= takeover {
        return Err(ConfigError::Invalid {
            name: ENV_RESIGN_HOLD_OFF,
            reason: format!(
                "{} s is not longer than the takeover time of {} s",
                out.hold_off.as_secs_f64(),
                takeover.as_secs_f64()
            ),
        });
    }

    // Doubling never shortens the hold-off, so the longest one is at least the first one.
    if out.hold_off_max < out.hold_off {
        return Err(ConfigError::Invalid {
            name: ENV_RESIGN_HOLD_OFF_MAX,
            reason: format!(
                "{} s is shorter than the hold-off of {} s",
                out.hold_off_max.as_secs_f64(),
                out.hold_off.as_secs_f64()
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

        let data_dir = match source.variable(ENV_DATA_DIR) {
            Some(dir) => PathBuf::from(dir),
            None => default_data_dir(source)?,
        };

        let timers = timers(source)?;

        Ok(Self {
            referee: referee(source)?,
            node_name: node_name(source)?,
            role_port: port(source, ENV_ROLE_PORT, DEFAULT_ROLE_PORT)?,
            server_port: port(source, ENV_SERVER_PORT, DEFAULT_SERVER_PORT)?,
            database: postgresql(source)?,
            server_health: server_health(source, timers.takeover)?,
            timers,
            log_level: source.variable(ENV_LOG_LEVEL).unwrap_or_else(|| DEFAULT_LOG_LEVEL.to_owned()),
            data_dir,
        })
    }

    /// Returns the path of the file with the highest generation this node has seen.
    pub fn generation_file(&self) -> PathBuf {
        self.data_dir.join(GENERATION_FILE_NAME)
    }
}

#[cfg(test)]
mod tests;
