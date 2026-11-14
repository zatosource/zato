// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The probe of the pub/sub database on `PostgreSQL` in the shared storage mode.
//!
//! A probe reads the row of `pubsub_active` that the generation guard of the Zato server keeps, which establishes
//! that the database is reachable from the pod, including before the Zato server first created the table.
//! Each probe runs within [`REQUEST_TIMEOUT`] on a runtime of the probe,
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
use tokio_postgres::{Client, Config, NoTls};
use tokio_postgres_rustls::MakeRustlsConnect;

use crate::config::{PostgreSqlConfig, PostgreSqlPassword, PostgreSqlTls};

/// How long one probe may take, a new connection included.
pub const REQUEST_TIMEOUT: Duration = Duration::from_secs(2);

/// The name under which the node appears among the sessions of `PostgreSQL`.
const APPLICATION_NAME: &str = "zato-ha-node";

/// Reads the row of the generation guard, which fails if the database is not reachable.
const PROBE_STATEMENT: &str = "SELECT 1 FROM pubsub_active WHERE id = 1";

/// The error of a probe that did not succeed.
#[derive(Debug)]
pub struct ProbeError(pub String);

impl std::fmt::Display for ProbeError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "Database probe error: {}", self.0)
    }
}

impl std::error::Error for ProbeError {}

/// A check that the database of the shared storage mode is reachable from this node.
pub trait DatabaseProbe: Send + Sync {
    /// Returns `Ok` if the database answered the probe.
    fn probe(&self) -> Result<(), ProbeError>;
}

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
fn tls_error(context: &str, error: impl std::fmt::Display) -> ProbeError {
    ProbeError(format!("PostgreSQL TLS, {context}: {error}"))
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

/// The probe of the pub/sub database on `PostgreSQL`.
pub struct PostgreSqlProbe {
    /// The connection settings, which are those of the pub/sub database.
    settings: PostgreSqlConfig,

    /// The TLS connector, if TLS is on.
    connector: Option<MakeRustlsConnect>,

    /// The runtime that the requests run on.
    runtime: Runtime,

    /// The current session, if one is connected.
    session: Mutex<Option<Session>>,
}

impl PostgreSqlProbe {
    /// Builds the probe of the database that `settings` describe, without connecting yet.
    pub fn new(settings: &PostgreSqlConfig) -> Result<Self, ProbeError> {
        let connector = settings.tls.as_ref().map(tls_connector).transpose()?;
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .map_err(|error| ProbeError(format!("PostgreSQL runtime: {error}")))?;
        Ok(Self {
            settings: settings.clone(),
            connector,
            runtime,
            session: Mutex::new(None),
        })
    }

    /// Returns the connection settings, with the password read again if it is kept in a file.
    fn connection_config(&self) -> Result<Config, ProbeError> {
        let password = match &self.settings.password {
            PostgreSqlPassword::Value(value) => value.clone(),
            PostgreSqlPassword::File(path) => std::fs::read_to_string(path)
                .map_err(|error| ProbeError(format!("{}: {error}", path.display())))?
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

    /// Connects to the database.
    async fn connect(&self) -> Result<Session, ProbeError> {
        let config = self.connection_config()?;
        let connect_error = |error: tokio_postgres::Error| ProbeError(format!("PostgreSQL connection: {error}"));

        // The connection exchanges the messages of the client in a task of its own, and an error that ends it
        // is reported by the next request on the client.
        let (client, connection) = if let Some(connector) = &self.connector {
            let (client, connection) = config.connect(connector.clone()).await.map_err(connect_error)?;
            (client, spawn_connection(connection))
        } else {
            let (client, connection) = config.connect(NoTls).await.map_err(connect_error)?;
            (client, spawn_connection(connection))
        };
        Ok(Session { client, connection })
    }

    /// Runs `operation` on the session within [`REQUEST_TIMEOUT`], connecting first if there is no session,
    /// and ends the session if the operation fails or does not complete in time.
    fn call<T>(
        &self,
        description: &str,
        operation: impl AsyncFnOnce(&Client) -> Result<T, tokio_postgres::Error>,
    ) -> Result<T, ProbeError> {
        // The probes use the session one at a time.
        let mut guard = self.session.lock();
        let existing = guard.take();

        let attempt = async {
            let session = match existing {
                Some(session) => session,
                None => self.connect().await?,
            };
            let value = operation(&session.client)
                .await
                .map_err(|error| ProbeError(format!("PostgreSQL {description}: {error}")))?;
            Ok::<_, ProbeError>((value, session))
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
            Err(_) => Err(ProbeError(format!(
                "PostgreSQL {description}: no answer within {REQUEST_TIMEOUT:?}"
            ))),
        }
    }
}

impl DatabaseProbe for PostgreSqlProbe {
    fn probe(&self) -> Result<(), ProbeError> {
        let _ = self.call("probe", async |client| match client.query_opt(PROBE_STATEMENT, &[]).await {
            // The Zato server creates the generation guard when it first starts, after the node already probes,
            // and a database that reports the table as missing answered the probe.
            Err(error) if error.code() == Some(&SqlState::UNDEFINED_TABLE) => Ok(None),
            outcome => outcome,
        })?;
        Ok(())
    }
}

#[cfg(test)]
mod tests;
