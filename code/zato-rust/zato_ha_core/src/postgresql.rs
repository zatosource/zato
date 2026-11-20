// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The probe of the Zato database on `PostgreSQL`.
//!
//! A probe reads the generation from the row of `zato_active` that the generation guard of the Zato server keeps,
//! which establishes that the database is reachable from the pod, including before the Zato server first created
//! the table, and tells which generation the server that took the database over last runs at.
//! It then verifies that a commit on the database is durable once acknowledged - the server flushes its write-ahead
//! log, writes full pages after a checkpoint, and as a primary with streaming standbys waits for at least one of them,
//! unless the provider of a managed service performs the failover.
//!
//! The generation and the durability settings are read by one statement prepared once per session, so that
//! once the Zato server created the generation guard, each probe is one exchange with the database.
//! Each probe runs within the request timeout of the node on a runtime of the probe,
//! and a probe that fails or does not complete in time ends the session, so that the next probe connects again.

use std::sync::Arc;
use std::time::Duration;

use parking_lot::Mutex;
use rustls::client::danger::{HandshakeSignatureValid, ServerCertVerified, ServerCertVerifier};
use rustls::crypto::{CryptoProvider, verify_tls12_signature, verify_tls13_signature};
use rustls::pki_types::pem::PemObject;
use rustls::pki_types::{CertificateDer, PrivateKeyDer, ServerName, UnixTime};
use rustls::{ClientConfig, DigitallySignedStruct, RootCertStore, SignatureScheme};
use tokio::runtime::Runtime;
use tokio::task::JoinHandle;
use tokio_postgres::config::SslMode;
use tokio_postgres::error::SqlState;
use tokio_postgres::{Client, Config, NoTls, Row, Statement};
use tokio_postgres_rustls::MakeRustlsConnect;

use crate::config::{PostgreSqlConfig, PostgreSqlPassword, PostgreSqlTls};

/// The name under which the node appears among the sessions of `PostgreSQL`.
const APPLICATION_NAME: &str = "zato-ha-node";

/// How `PostgreSQL` shows a setting that is turned on.
const SETTING_ON: &str = "on";

/// The columns that tell whether a commit on the database is durable once acknowledged.
///
/// These are whether the server flushes its write-ahead log to disk, whether it writes full pages after
/// a checkpoint, without which a torn page cannot be recovered, and the standbys that a commit waits for.
/// They are followed by the number of standbys that stream the write-ahead log of the server, without the logical
/// replication connections, which receive changes that are already durable. The last column tells whether
/// the server has a role that Amazon RDS, Aurora or Azure Database for `PostgreSQL` creates on it.
///
/// On these services the provider performs every automatic failover, and only to a standby that it replicates
/// synchronously, at the storage layer or through `synchronous_standby_names` that it manages, while
/// the read replicas that stream asynchronously are never a target of an automatic failover.
macro_rules! durability_columns {
    () => {
        "current_setting('fsync'), current_setting('full_page_writes'), current_setting('synchronous_standby_names'), \
        (SELECT count(*) FROM pg_stat_replication AS replication \
            WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots AS slot \
            WHERE slot.active_pid = replication.pid AND slot.slot_type = 'logical')), \
        EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('rds_superuser', 'azure_pg_admin'))"
    };
}

/// Reads the durability settings, before the Zato server created the generation guard.
const DURABILITY_STATEMENT: &str = concat!("SELECT ", durability_columns!());

/// Reads the durability settings and the generation of the generation guard, which is null without its row.
const GUARDED_STATEMENT: &str = concat!(
    "SELECT ",
    durability_columns!(),
    ", (SELECT generation FROM zato_active WHERE id = 1)"
);

/// The column of `fsync`.
const FSYNC_COLUMN: usize = 0;

/// The column of `full_page_writes`.
const FULL_PAGE_WRITES_COLUMN: usize = 1;

/// The column of `synchronous_standby_names`.
const SYNCHRONOUS_STANDBY_NAMES_COLUMN: usize = 2;

/// The column of the number of streaming standbys.
const STANDBY_COUNT_COLUMN: usize = 3;

/// The column of whether the provider performs the failover.
const PROVIDER_FAILOVER_COLUMN: usize = 4;

/// The column of the generation, which only the guarded statement has.
const GENERATION_COLUMN: usize = 5;

/// The error of a probe that did not succeed.
#[derive(Debug)]
pub enum ProbeError {
    /// The database did not answer.
    Unreachable(String),

    /// The database answered, and a commit on it could be acknowledged before it is durable.
    NotDurable(String),
}

impl std::fmt::Display for ProbeError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Unreachable(reason) => write!(formatter, "Database probe error: {reason}"),
            Self::NotDurable(reason) => write!(formatter, "Database not durable: {reason}"),
        }
    }
}

impl std::error::Error for ProbeError {}

/// A check that the Zato database is reachable from this node.
pub trait DatabaseProbe: Send + Sync {
    /// Returns the generation that the generation guard in the database names if the database answered the probe,
    /// which is `None` until a Zato server first took the database over.
    fn probe(&self) -> Result<Option<u64>, ProbeError>;
}

/// A connection to `PostgreSQL`, the task that exchanges its messages and the statements prepared on it.
struct Session {
    /// The client that sends the statements.
    client: Client,

    /// The task of the connection, which ends with the session.
    connection: JoinHandle<()>,

    /// The statement that reads the durability settings, prepared when the session connects.
    durability: Statement,

    /// The statement that reads the durability settings and the generation, prepared by the first probe
    /// that finds the generation guard, and dropped once the database reports its table missing.
    guarded: Option<Statement>,
}

/// The generation that the generation guard names and why a commit could be acknowledged before it is durable,
/// as one probe reads them.
type ProbeReading = (Option<i64>, Option<String>);

/// Returns whether the database reports a table missing.
fn is_undefined_table(error: &tokio_postgres::Error) -> bool {
    error.code() == Some(&SqlState::UNDEFINED_TABLE)
}

impl Session {
    /// Returns the guarded statement, preparing it if the session has none, or `None` while the generation guard
    /// does not exist.
    async fn guarded_statement(&mut self) -> Result<Option<Statement>, tokio_postgres::Error> {
        // A statement prepared by an earlier probe is reused ..
        if let Some(statement) = &self.guarded {
            return Ok(Some(statement.clone()));
        }

        // .. otherwise it is prepared, which fails until the Zato server first created the generation guard.
        match self.client.prepare(GUARDED_STATEMENT).await {
            Ok(statement) => {
                self.guarded = Some(statement.clone());
                Ok(Some(statement))
            }
            Err(error) if is_undefined_table(&error) => Ok(None),
            Err(error) => Err(error),
        }
    }

    /// Reads the generation and the durability settings, in one exchange once the guarded statement is prepared.
    async fn read(&mut self) -> Result<ProbeReading, tokio_postgres::Error> {
        if let Some(statement) = self.guarded_statement().await? {
            match self.client.query_one(&statement, &[]).await {
                Ok(row) => {
                    let stored: Option<i64> = row.try_get(GENERATION_COLUMN)?;
                    let shortfall = durability_shortfall(&row)?;
                    return Ok((stored, shortfall));
                }

                // The generation guard was removed after the statement was prepared, so it is prepared again
                // by a probe that finds the table, and this probe reads the durability settings alone.
                Err(error) if is_undefined_table(&error) => self.guarded = None,
                Err(error) => return Err(error),
            }
        }

        // A database without the generation guard answered the probe, and no Zato server took it over yet.
        let row = self.client.query_one(&self.durability, &[]).await?;
        let shortfall = durability_shortfall(&row)?;
        Ok((None, shortfall))
    }
}

impl Drop for Session {
    fn drop(&mut self) {
        self.connection.abort();
    }
}

/// Accepts every certificate of `PostgreSQL`, for a deployment that turned the verification off.
#[derive(Debug)]
struct UnverifiedServer {
    /// The provider whose algorithms verify the signatures of the handshake.
    provider: Arc<CryptoProvider>,
}

impl ServerCertVerifier for UnverifiedServer {
    fn verify_server_cert(
        &self,
        _end_entity: &CertificateDer<'_>,
        _intermediates: &[CertificateDer<'_>],
        _server_name: &ServerName<'_>,
        _ocsp_response: &[u8],
        _now: UnixTime,
    ) -> Result<ServerCertVerified, rustls::Error> {
        Ok(ServerCertVerified::assertion())
    }

    fn verify_tls12_signature(
        &self,
        message: &[u8],
        certificate: &CertificateDer<'_>,
        signature: &DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        verify_tls12_signature(message, certificate, signature, &self.provider.signature_verification_algorithms)
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        certificate: &CertificateDer<'_>,
        signature: &DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        verify_tls13_signature(message, certificate, signature, &self.provider.signature_verification_algorithms)
    }

    fn supported_verify_schemes(&self) -> Vec<SignatureScheme> {
        self.provider.signature_verification_algorithms.supported_schemes()
    }
}

/// Runs a connection in a task of its own, which ends with the connection, and whose error the next request
/// on the client reports.
fn spawn_connection<F>(connection: F) -> JoinHandle<()>
where
    F: Future<Output = Result<(), tokio_postgres::Error>> + Send + 'static,
{
    tokio::spawn(async move {
        connection.await.ok();
    })
}

/// Returns an error of a TLS setting.
fn tls_error(context: &str, error: impl std::fmt::Display) -> ProbeError {
    ProbeError::Unreachable(format!("PostgreSQL TLS, {context}: {error}"))
}

/// Returns the certificates that the certificate of `PostgreSQL` is verified against.
fn root_store(settings: &PostgreSqlTls) -> Result<RootCertStore, ProbeError> {
    let mut out = RootCertStore::empty();
    let Some(ca_file) = &settings.ca_file else {
        // Without a CA file, the store of the system is used, as in the Zato server.
        let native = rustls_native_certs::load_native_certs();
        for certificate in native.certs {
            out.add(certificate).map_err(|error| tls_error("system CA store", error))?;
        }
        return Ok(out);
    };
    for certificate in CertificateDer::pem_file_iter(ca_file).map_err(|error| tls_error("CA file", error))? {
        let certificate = certificate.map_err(|error| tls_error("CA file", error))?;
        out.add(certificate).map_err(|error| tls_error("CA file", error))?;
    }
    Ok(out)
}

/// Builds the TLS connector of the connections to `PostgreSQL`.
fn tls_connector(settings: &PostgreSqlTls) -> Result<MakeRustlsConnect, ProbeError> {
    let provider = Arc::new(rustls::crypto::ring::default_provider());
    let builder = ClientConfig::builder_with_provider(Arc::clone(&provider))
        .with_safe_default_protocol_versions()
        .map_err(|error| tls_error("protocol versions", error))?;

    let builder = if settings.verify {
        builder.with_root_certificates(root_store(settings)?)
    } else {
        builder
            .dangerous()
            .with_custom_certificate_verifier(Arc::new(UnverifiedServer { provider }))
    };

    let config = match &settings.client_files {
        Some((certificate_file, key_file)) => {
            let chain = CertificateDer::pem_file_iter(certificate_file)
                .map_err(|error| tls_error("client certificate file", error))?
                .collect::<Result<Vec<_>, _>>()
                .map_err(|error| tls_error("client certificate file", error))?;
            let key = PrivateKeyDer::from_pem_file(key_file).map_err(|error| tls_error("client key file", error))?;
            builder
                .with_client_auth_cert(chain, key)
                .map_err(|error| tls_error("client certificate", error))?
        }
        None => builder.with_no_client_auth(),
    };
    Ok(MakeRustlsConnect::new(config))
}

/// The probe of the Zato database on `PostgreSQL`.
pub struct PostgreSqlProbe {
    /// The connection settings, which are those of the Zato database.
    settings: PostgreSqlConfig,

    /// The TLS connector, if TLS is on.
    connector: Option<MakeRustlsConnect>,

    /// The runtime that the requests run on.
    runtime: Runtime,

    /// The current session, if one is connected.
    session: Mutex<Option<Session>>,

    /// How long one probe may take, a new connection included.
    request_timeout: Duration,
}

impl PostgreSqlProbe {
    /// Builds the probe of the database that `settings` describe, each of whose probes may take `request_timeout`,
    /// without connecting yet.
    pub fn new(settings: &PostgreSqlConfig, request_timeout: Duration) -> Result<Self, ProbeError> {
        let connector = settings.tls.as_ref().map(tls_connector).transpose()?;
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .map_err(|error| ProbeError::Unreachable(format!("PostgreSQL runtime: {error}")))?;
        Ok(Self {
            settings: settings.clone(),
            connector,
            runtime,
            session: Mutex::new(None),
            request_timeout,
        })
    }

    /// Returns the connection settings, with the password read again if it is kept in a file.
    fn connection_config(&self) -> Result<Config, ProbeError> {
        let password = match &self.settings.password {
            PostgreSqlPassword::Value(value) => value.clone(),
            PostgreSqlPassword::File(path) => std::fs::read_to_string(path)
                .map_err(|error| ProbeError::Unreachable(format!("{}: {error}", path.display())))?
                .trim()
                .to_owned(),
        };
        let ssl_mode = if self.connector.is_some() {
            SslMode::Require
        } else {
            SslMode::Disable
        };

        let mut out = Config::new();
        let _ = out
            .host(&self.settings.host)
            .port(self.settings.port)
            .user(&self.settings.username)
            .password(password)
            .dbname(&self.settings.database)
            .application_name(APPLICATION_NAME)
            .connect_timeout(self.request_timeout)
            .ssl_mode(ssl_mode);
        Ok(out)
    }

    /// Connects to the database.
    async fn connect(&self) -> Result<Session, ProbeError> {
        let config = self.connection_config()?;
        let connect_error = |error: tokio_postgres::Error| ProbeError::Unreachable(format!("PostgreSQL connection: {error}"));

        // The connection exchanges the messages of the client in a task of its own, and an error that ends it
        // is reported by the next request on the client.
        let (client, connection) = if let Some(connector) = &self.connector {
            let (client, connection) = config.connect(connector.clone()).await.map_err(connect_error)?;
            (client, spawn_connection(connection))
        } else {
            let (client, connection) = config.connect(NoTls).await.map_err(connect_error)?;
            (client, spawn_connection(connection))
        };

        // The durability settings are read by every probe, so their statement is prepared once per session.
        let durability = client
            .prepare(DURABILITY_STATEMENT)
            .await
            .map_err(|error| ProbeError::Unreachable(format!("PostgreSQL prepare: {error}")))?;
        Ok(Session {
            client,
            connection,
            durability,
            guarded: None,
        })
    }

    /// Runs `operation` on the session within the request timeout, connecting first if there is no session,
    /// and ends the session if the operation fails or does not complete in time.
    fn call<T>(
        &self,
        description: &str,
        operation: impl AsyncFnOnce(&mut Session) -> Result<T, tokio_postgres::Error>,
    ) -> Result<T, ProbeError> {
        // The probes use the session one at a time.
        let mut guard = self.session.lock();
        let existing = guard.take();

        let attempt = async {
            let mut session = match existing {
                Some(session) => session,
                None => self.connect().await?,
            };
            let value = operation(&mut session)
                .await
                .map_err(|error| ProbeError::Unreachable(format!("PostgreSQL {description}: {error}")))?;
            Ok::<_, ProbeError>((value, session))
        };

        // The timer of the deadline registers with the runtime when it is created, so it is created within it.
        // A session that failed or did not answer in time is dropped with the attempt, which ends its connection.
        let request_timeout = self.request_timeout;
        let outcome = self
            .runtime
            .block_on(async { tokio::time::timeout(request_timeout, attempt).await });
        match outcome {
            Ok(Ok((value, session))) => {
                *guard = Some(session);
                drop(guard);
                Ok(value)
            }
            Ok(Err(error)) => Err(error),
            Err(_) => Err(ProbeError::Unreachable(format!(
                "PostgreSQL {description}: no answer within {request_timeout:?}"
            ))),
        }
    }
}

/// Returns why a commit on the database could be acknowledged before it is durable, or `None` if it could not,
/// from a row with the durability columns.
fn durability_shortfall(row: &Row) -> Result<Option<String>, tokio_postgres::Error> {
    let fsync: String = row.try_get(FSYNC_COLUMN)?;
    if fsync != SETTING_ON {
        return Ok(Some(format!("fsync is `{fsync}`, it must be `{SETTING_ON}`")));
    }

    let full_page_writes: String = row.try_get(FULL_PAGE_WRITES_COLUMN)?;
    if full_page_writes != SETTING_ON {
        return Ok(Some(format!("full_page_writes is `{full_page_writes}`, it must be `{SETTING_ON}`")));
    }

    let synchronous_standby_names: String = row.try_get(SYNCHRONOUS_STANDBY_NAMES_COLUMN)?;
    let standby_count: i64 = row.try_get(STANDBY_COUNT_COLUMN)?;
    let has_provider_failover: bool = row.try_get(PROVIDER_FAILOVER_COLUMN)?;

    // A primary whose standbys all stream asynchronously acknowledges commits that a failover to any of them loses,
    // unless the provider performs the failover, and only to a standby that it replicates synchronously.
    if standby_count > 0 && !has_provider_failover && synchronous_standby_names.is_empty() {
        return Ok(Some(format!(
            "the primary has {standby_count} streaming standby(s) and an empty synchronous_standby_names, \
            at least one standby must be synchronous"
        )));
    }

    Ok(None)
}

impl DatabaseProbe for PostgreSqlProbe {
    fn probe(&self) -> Result<Option<u64>, ProbeError> {
        // The Zato server creates the generation guard when it first starts, after the node already probes,
        // and a database that reports the table as missing answered the probe.
        let (stored, shortfall) = self.call("probe", async |session| session.read().await)?;

        // A database that answered and is not durable is reported apart from one that did not answer.
        if let Some(reason) = shortfall {
            return Err(ProbeError::NotDurable(reason));
        }

        // The column is signed, and the generation guard only ever stores generations of zero or more.
        stored
            .map(u64::try_from)
            .transpose()
            .map_err(|error| ProbeError::Unreachable(format!("PostgreSQL generation: {error}")))
    }
}

#[cfg(test)]
mod tests;
