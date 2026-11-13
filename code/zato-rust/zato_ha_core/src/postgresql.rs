// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee kept in a table of the pub/sub database on `PostgreSQL`, written with conditional updates.
//!
//! The table `zato_ha_referee` holds the record and the published addresses under text keys, each as JSON
//! with a version that every write raises. Each request runs within [`REQUEST_TIMEOUT`] on a runtime of
//! the referee, and a request that fails or does not complete in time ends the session, so that the next
//! request connects again.

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
use tokio_postgres::{Client, Config, NoTls, Row};
use tokio_postgres_rustls::MakeRustlsConnect;

use crate::config::{PostgreSqlConfig, PostgreSqlPassword, PostgreSqlTls};
use crate::record::{NodeAddress, RefereeRecord, Versioned};
use crate::referee::{Referee, RefereeError, VERSION_ABSENT};
use crate::wire;

/// How long one request may take, a new connection included.
///
/// It is shorter than the gap between the mark-out and the takeover timers, and longer than a commit that waits
/// for a synchronous standby under load.
pub const REQUEST_TIMEOUT: Duration = Duration::from_secs(2);

/// The name under which the node appears among the sessions of `PostgreSQL`.
const APPLICATION_NAME: &str = "zato-ha-node";

/// The suffix of the keys under which the nodes publish their addresses.
const NODES_SUFFIX: &str = "nodes";

/// Creates the table under an advisory lock, so that two nodes that start at the same time create it in turn.
///
/// The lock is held by the implicit transaction of the statements, and it is the lock that the Zato schemas
/// are created under in `zato.common.db_env.engine`.
const CREATE_TABLE: &str = "SELECT pg_advisory_xact_lock(7401852117309);
    CREATE TABLE IF NOT EXISTS zato_ha_referee (key TEXT PRIMARY KEY, record JSONB NOT NULL, version BIGINT NOT NULL)";

/// Reads one record and its version.
const SELECT_RECORD: &str = "SELECT record::text, version FROM zato_ha_referee WHERE key = $1";

/// Creates a record that does not exist yet.
const INSERT_RECORD: &str = "INSERT INTO zato_ha_referee (key, record, version) VALUES ($1, $2::text::jsonb, 1)
    ON CONFLICT (key) DO NOTHING";

/// Replaces a record whose version is still the expected one.
const UPDATE_RECORD: &str = "UPDATE zato_ha_referee SET record = $2::text::jsonb, version = version + 1
    WHERE key = $1 AND version = $3";

/// Raises the version of a record whose version and value are still the expected ones.
const RENEW_RECORD: &str = "UPDATE zato_ha_referee SET version = version + 1
    WHERE key = $1 AND version = $2 AND record = $3::text::jsonb RETURNING version";

/// Writes the address of a node whatever was there before.
const UPSERT_ADDRESS: &str = "INSERT INTO zato_ha_referee (key, record, version) VALUES ($1, $2::text::jsonb, 1)
    ON CONFLICT (key) DO UPDATE SET record = EXCLUDED.record, version = zato_ha_referee.version + 1";

/// Reads every record under a prefix of keys.
const SELECT_ADDRESSES: &str = "SELECT record::text FROM zato_ha_referee WHERE starts_with(key, $1)";

/// A connection to `PostgreSQL` and the task that exchanges its messages.
struct Session {
    /// The client that sends the statements.
    client: Client,

    /// The task of the connection, which ends with the session.
    connection: JoinHandle<()>,
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
fn tls_error(context: &str, error: impl std::fmt::Display) -> RefereeError {
    RefereeError(format!("PostgreSQL TLS, {context}: {error}"))
}

/// Returns the certificates that the certificate of `PostgreSQL` is verified against.
fn root_store(settings: &PostgreSqlTls) -> Result<RootCertStore, RefereeError> {
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
fn tls_connector(settings: &PostgreSqlTls) -> Result<MakeRustlsConnect, RefereeError> {
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

/// Returns a version as `PostgreSQL` stores it.
fn stored_version(version: u64) -> Result<i64, RefereeError> {
    i64::try_from(version).map_err(|error| RefereeError(format!("version {version}: {error}")))
}

/// Returns a version as `PostgreSQL` returned it.
fn returned_version(version: i64) -> Result<u64, RefereeError> {
    u64::try_from(version).map_err(|error| RefereeError(format!("version {version}: {error}")))
}

/// Encodes a value as the text of a JSON document.
fn encode_text<T: serde::Serialize>(value: &T) -> Result<String, RefereeError> {
    let bytes = wire::encode(value).map_err(|error| RefereeError(format!("JSON value: {error}")))?;
    String::from_utf8(bytes).map_err(|error| RefereeError(format!("JSON value: {error}")))
}

/// Decodes the JSON document in the first column of a row.
fn decode_column<T: serde::de::DeserializeOwned>(row: &Row) -> Result<T, RefereeError> {
    let text: String = row.try_get(0).map_err(|error| RefereeError(format!("record column: {error}")))?;
    wire::decode(text.as_bytes()).map_err(|error| RefereeError(format!("JSON value: {error}")))
}

/// The `PostgreSQL` referee.
pub struct PostgreSqlReferee {
    /// The connection settings, which are those of the pub/sub database.
    settings: PostgreSqlConfig,

    /// The TLS connector, if TLS is on.
    connector: Option<MakeRustlsConnect>,

    /// The key of the record.
    key: String,

    /// The runtime that the requests run on.
    runtime: Runtime,

    /// The current session, if one is connected.
    session: Mutex<Option<Session>>,
}

impl PostgreSqlReferee {
    /// Builds a client of the record under `key` in the database that `settings` describe, without connecting yet.
    pub fn new(settings: &PostgreSqlConfig, key: &str) -> Result<Self, RefereeError> {
        let connector = settings.tls.as_ref().map(tls_connector).transpose()?;
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .map_err(|error| RefereeError(format!("PostgreSQL runtime: {error}")))?;
        Ok(Self {
            settings: settings.clone(),
            connector,
            key: key.to_owned(),
            runtime,
            session: Mutex::new(None),
        })
    }

    /// Returns the connection settings, with the password read again if it is kept in a file.
    fn connection_config(&self) -> Result<Config, RefereeError> {
        let password = match &self.settings.password {
            PostgreSqlPassword::Value(value) => value.clone(),
            PostgreSqlPassword::File(path) => std::fs::read_to_string(path)
                .map_err(|error| RefereeError(format!("{}: {error}", path.display())))?
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
            .connect_timeout(REQUEST_TIMEOUT)
            .ssl_mode(ssl_mode);
        Ok(out)
    }

    /// Connects and creates the table if it does not exist.
    async fn connect(&self) -> Result<Session, RefereeError> {
        let config = self.connection_config()?;
        let connect_error = |error: tokio_postgres::Error| RefereeError(format!("PostgreSQL connection: {error}"));

        // The connection exchanges the messages of the client in a task of its own, and an error that ends it
        // is reported by the next request on the client.
        let (client, connection) = if let Some(connector) = &self.connector {
            let (client, connection) = config.connect(connector.clone()).await.map_err(connect_error)?;
            (client, spawn_connection(connection))
        } else {
            let (client, connection) = config.connect(NoTls).await.map_err(connect_error)?;
            (client, spawn_connection(connection))
        };
        let out = Session { client, connection };

        out.client
            .batch_execute(CREATE_TABLE)
            .await
            .map_err(|error| RefereeError(format!("PostgreSQL table: {error}")))?;
        Ok(out)
    }

    /// Runs `operation` on the session within [`REQUEST_TIMEOUT`], connecting first if there is no session,
    /// and ends the session if the operation fails or does not complete in time.
    fn call<T>(
        &self,
        description: &str,
        operation: impl AsyncFnOnce(&Client) -> Result<T, tokio_postgres::Error>,
    ) -> Result<T, RefereeError> {
        // The requests of the threads of the node use the session one at a time.
        let mut guard = self.session.lock();
        let existing = guard.take();

        let attempt = async {
            let session = match existing {
                Some(session) => session,
                None => self.connect().await?,
            };
            let value = operation(&session.client)
                .await
                .map_err(|error| RefereeError(format!("PostgreSQL {description}: {error}")))?;
            Ok::<_, RefereeError>((value, session))
        };

        // The timer of the deadline registers with the runtime when it is created, so it is created within it.
        // A session that failed or did not answer in time is dropped with the attempt, which ends its connection.
        let outcome = self
            .runtime
            .block_on(async { tokio::time::timeout(REQUEST_TIMEOUT, attempt).await });
        match outcome {
            Ok(Ok((value, session))) => {
                *guard = Some(session);
                drop(guard);
                Ok(value)
            }
            Ok(Err(error)) => Err(error),
            Err(_) => Err(RefereeError(format!(
                "PostgreSQL {description}: no answer within {REQUEST_TIMEOUT:?}"
            ))),
        }
    }

    /// Returns the key under which `node_name` publishes its address.
    fn address_key(&self, node_name: &str) -> String {
        format!("{}/{NODES_SUFFIX}/{node_name}", self.key)
    }
}

impl Referee for PostgreSqlReferee {
    fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError> {
        let row = self.call("read", async |client| client.query_opt(SELECT_RECORD, &[&self.key]).await)?;
        let Some(row) = row else {
            return Ok(None);
        };
        let value = decode_column(&row)?;
        let version: i64 = row.try_get(1).map_err(|error| RefereeError(format!("version column: {error}")))?;
        Ok(Some(Versioned {
            value,
            version: returned_version(version)?,
        }))
    }

    fn compare_and_set(&self, record: &RefereeRecord, expected_version: u64) -> Result<bool, RefereeError> {
        let body = encode_text(record)?;
        let changed = if expected_version == VERSION_ABSENT {
            self.call("insert", async |client| client.execute(INSERT_RECORD, &[&self.key, &body]).await)?
        } else {
            let expected = stored_version(expected_version)?;
            self.call("update", async |client| {
                client.execute(UPDATE_RECORD, &[&self.key, &body, &expected]).await
            })?
        };
        Ok(changed == 1)
    }

    fn renew(&self, record: &RefereeRecord, expected_version: u64) -> Result<Option<u64>, RefereeError> {
        let body = encode_text(record)?;
        let expected = stored_version(expected_version)?;
        let row = self.call("renewal", async |client| {
            client.query_opt(RENEW_RECORD, &[&self.key, &expected, &body]).await
        })?;
        let Some(row) = row else {
            return Ok(None);
        };
        let version: i64 = row.try_get(0).map_err(|error| RefereeError(format!("version column: {error}")))?;
        Ok(Some(returned_version(version)?))
    }

    fn publish_address(&self, address: &NodeAddress) -> Result<(), RefereeError> {
        let body = encode_text(address)?;
        let key = self.address_key(&address.node_name);
        let _ = self.call("address", async |client| client.execute(UPSERT_ADDRESS, &[&key, &body]).await)?;
        Ok(())
    }

    fn read_addresses(&self) -> Result<Vec<NodeAddress>, RefereeError> {
        let prefix = format!("{}/{NODES_SUFFIX}/", self.key);
        let rows = self.call("addresses", async |client| client.query(SELECT_ADDRESSES, &[&prefix]).await)?;
        rows.iter().map(decode_column).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_support::{LOOPBACK, NODE_A};

    /// A port on the loopback that nothing listens on.
    const CLOSED_PORT: u16 = 1;

    #[test]
    fn a_database_that_does_not_answer_is_an_error() {
        let settings = PostgreSqlConfig {
            host: LOOPBACK.to_owned(),
            port: CLOSED_PORT,
            username: "zato".to_owned(),
            password: PostgreSqlPassword::Value("Test password".to_owned()),
            database: "zato".to_owned(),
            tls: None,
        };
        let referee = PostgreSqlReferee::new(&settings, "zato/ha/test").unwrap();
        assert!(referee.read().is_err());
        assert!(referee.compare_and_set(&RefereeRecord::solo(1, NODE_A), VERSION_ABSENT).is_err());
    }
}
