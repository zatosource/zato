//! The TLS configuration of an outgoing connection - what the certificate of the endpoint is verified
//! against, and the client certificate presented to it.
//!
//! One configuration serves every TLS connection of a transport, so the sessions it establishes
//! are resumed by the new connections that follow them.

use std::sync::Arc;

use rustls::client::danger::{HandshakeSignatureValid, ServerCertVerified, ServerCertVerifier};
use rustls::crypto::{WebPkiSupportedAlgorithms, verify_tls12_signature, verify_tls13_signature};
use rustls::pki_types::pem::PemObject;
use rustls::pki_types::{CertificateDer, PrivateKeyDer, ServerName, UnixTime};
use rustls::{ClientConfig, DigitallySignedStruct, RootCertStore, SignatureScheme};

/// How the TLS connections of a transport are established.
#[derive(Clone, Default, PartialEq, Eq)]
pub struct TlsSettings {
    /// The CA bundle the certificate of the endpoint is verified against, or `None` to not verify it at all.
    pub ca_path: Option<String>,

    /// The client certificate presented to the endpoint, a PEM file that may also hold its key.
    pub client_cert: Option<String>,

    /// The key of the client certificate, if it is kept in a file of its own.
    pub client_key: Option<String>,
}

/// Builds the TLS configuration the settings describe, reading the CA bundle and the client certificate from their files.
pub fn build_config(settings: &TlsSettings) -> Result<Arc<ClientConfig>, String> {
    let provider = Arc::new(rustls::crypto::ring::default_provider());

    let builder = ClientConfig::builder_with_provider(Arc::clone(&provider))
        .with_safe_default_protocol_versions()
        .map_err(|err| format!("TLS protocol versions not available: {err}"))?;

    let builder = match &settings.ca_path {
        Some(ca_path) => builder.with_root_certificates(load_roots(ca_path)?),
        None => builder.dangerous().with_custom_certificate_verifier(Arc::new(NoVerification {
            algorithms: provider.signature_verification_algorithms,
        })),
    };

    let config = match &settings.client_cert {
        Some(cert_path) => {
            let key_path = settings.client_key.as_deref().unwrap_or(cert_path);
            let chain = load_certificates(cert_path)?;
            let key = PrivateKeyDer::from_pem_file(key_path).map_err(|err| format!("Could not read the key from {key_path}: {err}"))?;

            builder
                .with_client_auth_cert(chain, key)
                .map_err(|err| format!("Invalid client certificate {cert_path}: {err}"))?
        }
        None => builder.with_no_client_auth(),
    };

    Ok(Arc::new(config))
}

/// Reads the certificates of a PEM file.
fn load_certificates(path: &str) -> Result<Vec<CertificateDer<'static>>, String> {
    let iterator = CertificateDer::pem_file_iter(path).map_err(|err| format!("Could not read {path}: {err}"))?;

    let mut out = Vec::new();
    for item in iterator {
        out.push(item.map_err(|err| format!("Invalid certificate in {path}: {err}"))?);
    }

    if out.is_empty() {
        return Err(format!("No certificate found in {path}"));
    }

    Ok(out)
}

/// Reads the CA certificates of a PEM bundle into a trust store.
fn load_roots(path: &str) -> Result<RootCertStore, String> {
    let mut roots = RootCertStore::empty();
    let (added, _ignored) = roots.add_parsable_certificates(load_certificates(path)?);

    if added == 0 {
        return Err(format!("No usable CA certificate found in {path}"));
    }

    Ok(roots)
}

/// The name the certificate of the endpoint is issued for, a DNS name or an IP address.
pub fn server_name(host: &str) -> Result<ServerName<'static>, String> {
    ServerName::try_from(host.to_owned()).map_err(|err| format!("Invalid TLS server name {host}: {err}"))
}

/// A verifier that accepts any certificate, for connections that do not validate TLS, while still checking
/// that the handshake is signed with the key of the certificate the endpoint presented.
#[derive(Debug)]
struct NoVerification {
    /// The signature algorithms of the crypto provider.
    algorithms: WebPkiSupportedAlgorithms,
}

impl ServerCertVerifier for NoVerification {
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
        cert: &CertificateDer<'_>,
        dss: &DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        verify_tls12_signature(message, cert, dss, &self.algorithms)
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        verify_tls13_signature(message, cert, dss, &self.algorithms)
    }

    fn supported_verify_schemes(&self) -> Vec<SignatureScheme> {
        self.algorithms.supported_schemes()
    }
}
