// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The replication link, a TCP connection with mutual TLS whose two directions are used by different threads.
//!
//! One thread reads the TCP stream without holding any lock and feeds the bytes to the TLS connection under
//! a mutex, and any thread sends a message under the same mutex. This keeps confirmations flowing while
//! frames are being sent.

use std::io::{Error, ErrorKind, Read, Write};
use std::net::{Shutdown, SocketAddr, TcpStream, ToSocketAddrs};
use std::sync::Arc;
use std::time::Duration;

use parking_lot::Mutex;
use rustls::crypto::CryptoProvider;
use rustls::pki_types::pem::PemObject;
use rustls::pki_types::{CertificateDer, PrivateKeyDer, ServerName};
use rustls::server::WebPkiClientVerifier;
use rustls::{ClientConfig, ClientConnection, Connection, RootCertStore, ServerConfig, ServerConnection};

use crate::config::TlsFiles;
use crate::protocol::{self, Message};

/// How long a TCP connection and a TLS handshake may take.
pub const CONNECT_TIMEOUT: Duration = Duration::from_secs(2);

/// The size of the buffer the reader fills from the TCP stream.
const READ_BUFFER_SIZE: usize = 256 * 1024;

/// The TLS configurations of both ends of the link.
pub struct TlsContext {
    /// The configuration of the standby, which accepts the link.
    server: Arc<ServerConfig>,

    /// The configuration of the active node, which opens the link.
    client: Arc<ClientConfig>,
}

/// Returns an error of invalid TLS material.
fn tls_error(context: &str, error: impl std::fmt::Display) -> Error {
    Error::new(ErrorKind::InvalidData, format!("{context}: {error}"))
}

impl TlsContext {
    /// Loads the CA, the certificate and the key of this node.
    pub fn load(files: &TlsFiles) -> Result<Self, Error> {
        let provider = Arc::new(rustls::crypto::ring::default_provider());

        let mut roots = RootCertStore::empty();
        for certificate in CertificateDer::pem_file_iter(&files.authority).map_err(|error| tls_error("CA file", error))? {
            let certificate = certificate.map_err(|error| tls_error("CA file", error))?;
            roots.add(certificate).map_err(|error| tls_error("CA file", error))?;
        }
        let roots = Arc::new(roots);

        let chain = CertificateDer::pem_file_iter(&files.certificate)
            .map_err(|error| tls_error("certificate file", error))?
            .collect::<Result<Vec<_>, _>>()
            .map_err(|error| tls_error("certificate file", error))?;
        let key = PrivateKeyDer::from_pem_file(&files.private_key).map_err(|error| tls_error("key file", error))?;

        let server = Self::server_config(&provider, &roots, chain.clone(), key.clone_key())?;
        let client = Self::client_config(&provider, &roots, chain, key)?;
        Ok(Self {
            server: Arc::new(server),
            client: Arc::new(client),
        })
    }

    /// Builds the configuration of the accepting end, which requires a client certificate issued by the CA.
    fn server_config(
        provider: &Arc<CryptoProvider>,
        roots: &Arc<RootCertStore>,
        chain: Vec<CertificateDer<'static>>,
        key: PrivateKeyDer<'static>,
    ) -> Result<ServerConfig, Error> {
        let verifier = WebPkiClientVerifier::builder_with_provider(Arc::clone(roots), Arc::clone(provider))
            .build()
            .map_err(|error| tls_error("client verifier", error))?;
        let mut out = ServerConfig::builder_with_provider(Arc::clone(provider))
            .with_safe_default_protocol_versions()
            .map_err(|error| tls_error("protocol versions", error))?
            .with_client_cert_verifier(verifier)
            .with_single_cert(chain, key)
            .map_err(|error| tls_error("certificate", error))?;

        // The link is never resumed, so no ticket is sent.
        out.send_tls13_tickets = 0;
        Ok(out)
    }

    /// Builds the configuration of the opening end, which presents its own certificate.
    fn client_config(
        provider: &Arc<CryptoProvider>,
        roots: &Arc<RootCertStore>,
        chain: Vec<CertificateDer<'static>>,
        key: PrivateKeyDer<'static>,
    ) -> Result<ClientConfig, Error> {
        ClientConfig::builder_with_provider(Arc::clone(provider))
            .with_safe_default_protocol_versions()
            .map_err(|error| tls_error("protocol versions", error))?
            .with_root_certificates(Arc::clone(roots))
            .with_client_auth_cert(chain, key)
            .map_err(|error| tls_error("certificate", error))
    }

    /// Opens the link to the node named `peer_name` at `host:port`, verifying that its certificate names it.
    pub fn connect(&self, peer_name: &str, host: &str, port: u16) -> Result<(LinkSender, LinkReceiver), Error> {
        let address = resolve(host, port)?;
        let mut tcp = TcpStream::connect_timeout(&address, CONNECT_TIMEOUT)?;
        let server_name = ServerName::try_from(peer_name.to_owned()).map_err(|error| tls_error("peer name", error))?;
        let mut connection = ClientConnection::new(Arc::clone(&self.client), server_name).map_err(|error| tls_error("TLS", error))?;
        handshake(&mut tcp, &mut connection)?;
        split(tcp, Connection::Client(connection))
    }

    /// Completes the accepting end of a link and verifies that the peer's certificate names `expected_peer`.
    pub fn accept(&self, mut tcp: TcpStream) -> Result<AcceptedLink, Error> {
        let mut connection = ServerConnection::new(Arc::clone(&self.server)).map_err(|error| tls_error("TLS", error))?;
        handshake(&mut tcp, &mut connection)?;
        let peer_certificate = connection
            .peer_certificates()
            .and_then(|chain| chain.first())
            .cloned()
            .ok_or_else(|| tls_error("TLS", "the peer presented no certificate"))?;
        let (sender, receiver) = split(tcp, Connection::Server(connection))?;
        Ok(AcceptedLink {
            sender,
            receiver,
            peer_certificate,
        })
    }
}

/// A link accepted by the standby, whose peer is verified once it states its name.
pub struct AcceptedLink {
    /// The sending half.
    pub sender: LinkSender,

    /// The receiving half.
    pub receiver: LinkReceiver,

    /// The certificate of the peer.
    pub peer_certificate: CertificateDer<'static>,
}

/// Verifies that the certificate of a peer is valid for the DNS name `peer_name`.
pub fn verify_peer_name(peer_certificate: &CertificateDer<'static>, peer_name: &str) -> Result<(), Error> {
    let certificate = webpki::EndEntityCert::try_from(peer_certificate).map_err(|error| tls_error("peer certificate", error))?;
    let server_name = ServerName::try_from(peer_name).map_err(|error| tls_error("peer name", error))?;
    certificate
        .verify_is_valid_for_subject_name(&server_name)
        .map_err(|error| tls_error(&format!("the peer certificate does not name {peer_name}"), error))
}

/// Resolves a host and port to the first address.
fn resolve(host: &str, port: u16) -> Result<SocketAddr, Error> {
    (host, port)
        .to_socket_addrs()?
        .next()
        .ok_or_else(|| Error::new(ErrorKind::NotFound, format!("no address for {host}")))
}

/// Completes a TLS handshake within [`CONNECT_TIMEOUT`].
fn handshake<Data>(tcp: &mut TcpStream, connection: &mut rustls::ConnectionCommon<Data>) -> Result<(), Error> {
    tcp.set_read_timeout(Some(CONNECT_TIMEOUT))?;
    tcp.set_write_timeout(Some(CONNECT_TIMEOUT))?;
    while connection.is_handshaking() {
        let _ = connection.complete_io(tcp)?;
    }
    Ok(())
}

/// Splits a connection into its sending and its receiving half.
fn split(tcp: TcpStream, mut connection: Connection) -> Result<(LinkSender, LinkReceiver), Error> {
    tcp.set_nodelay(true)?;

    // A message is encrypted whole before it is written, so its size is bounded only by the protocol.
    connection.set_buffer_limit(None);

    // A message that arrived together with the last record of the handshake was decrypted by the handshake,
    // and no later read of the TCP stream returns it.
    let mut plaintext = Vec::new();
    take_plaintext(&mut connection, &mut plaintext)?;

    // The receiver blocks until the peer sends something or the link is shut down.
    tcp.set_read_timeout(None)?;
    let reader = tcp.try_clone()?;
    let shared = Arc::new(Mutex::new(SharedEnd { connection, tcp }));
    let sender = LinkSender {
        shared: Arc::clone(&shared),
    };
    let receiver = LinkReceiver {
        shared,
        tcp: reader,
        plaintext,
        buffer: vec![0_u8; READ_BUFFER_SIZE],
    };
    Ok((sender, receiver))
}

/// The TLS state and the TCP stream that both halves use.
struct SharedEnd {
    /// The TLS connection.
    connection: Connection,

    /// The TCP stream to which encrypted records are written.
    tcp: TcpStream,
}

impl SharedEnd {
    /// Writes every pending encrypted record to the TCP stream.
    fn flush_records(&mut self) -> Result<(), Error> {
        while self.connection.wants_write() {
            let _ = self.connection.write_tls(&mut self.tcp)?;
        }
        Ok(())
    }
}

/// The sending half of a link, shared by every thread that sends.
#[derive(Clone)]
pub struct LinkSender {
    /// The shared TLS state.
    shared: Arc<Mutex<SharedEnd>>,
}

impl LinkSender {
    /// Sends a message, waiting at most `timeout` for the peer to take it.
    pub fn send(&self, message: &Message, timeout: Duration) -> Result<(), Error> {
        let framed = protocol::frame(message)?;
        let mut shared = self.shared.lock();

        // A peer that stops reading would otherwise block this thread for good.
        shared.tcp.set_write_timeout(Some(timeout))?;
        shared.connection.writer().write_all(&framed)?;
        shared.flush_records()
    }

    /// Shuts the link down, which ends the receiver's wait as well.
    pub fn close(&self) {
        let shared = self.shared.lock();

        // A link already closed by the peer reports an error that changes nothing.
        let _ = shared.tcp.shutdown(Shutdown::Both);
    }
}

/// The receiving half of a link, owned by one thread.
pub struct LinkReceiver {
    /// The shared TLS state.
    shared: Arc<Mutex<SharedEnd>>,

    /// A clone of the TCP stream, read without the lock.
    tcp: TcpStream,

    /// Decrypted bytes not yet parsed into a message.
    plaintext: Vec<u8>,

    /// The buffer the TCP stream is read into.
    buffer: Vec<u8>,
}

impl LinkReceiver {
    /// Returns the next message with the receiver for the messages after it, blocking until
    /// a message arrives or the link ends. A link that fails is over, so an error consumes the receiver.
    pub fn receive(mut self) -> Result<(Message, Self), Error> {
        loop {
            if let Some(message) = protocol::take_message(&mut self.plaintext)? {
                return Ok((message, self));
            }

            let count = self.tcp.read(&mut self.buffer)?;
            if count == 0 {
                return Err(Error::new(ErrorKind::UnexpectedEof, "the peer closed the link"));
            }
            let received = self.buffer.get(..count).ok_or_else(|| Error::other("read past the buffer"))?;
            decrypt(&self.shared, &mut self.plaintext, received)?;
        }
    }
}

/// Feeds encrypted bytes to the TLS connection and collects the plaintext they contain.
fn decrypt(shared: &Mutex<SharedEnd>, plaintext: &mut Vec<u8>, mut received: &[u8]) -> Result<(), Error> {
    let mut shared = shared.lock();

    while !received.is_empty() {
        let _ = shared.connection.read_tls(&mut received)?;
        let _ = shared.connection.process_new_packets().map_err(|error| tls_error("TLS", error))?;
        take_plaintext(&mut shared.connection, plaintext)?;
    }

    // Key updates and alerts produced by the bytes just read are answered at once.
    shared.flush_records()
}

/// Appends the plaintext that the TLS connection has decrypted so far.
fn take_plaintext(connection: &mut Connection, plaintext: &mut Vec<u8>) -> Result<(), Error> {
    let mut chunk = [0_u8; 16 * 1024];
    loop {
        match connection.reader().read(&mut chunk) {
            Ok(0) => return Ok(()),
            Ok(count) => {
                let bytes = chunk.get(..count).ok_or_else(|| Error::other("read past the buffer"))?;
                plaintext.extend_from_slice(bytes);
            }
            Err(error) if error.kind() == ErrorKind::WouldBlock => return Ok(()),
            Err(error) => return Err(error),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_support::{Certificates, LOOPBACK, NODE_A, NODE_B};
    use std::net::TcpListener;
    use std::sync::mpsc;
    use std::thread;

    /// How many links are opened, since a message reaches the other end together with the last record
    /// of the handshake on only some of them.
    const LINK_COUNT: usize = 50;

    /// How long a message may take to reach the other end.
    const RECEIVE_TIMEOUT: Duration = Duration::from_secs(5);

    #[test]
    fn a_message_sent_right_after_the_handshake_is_received() {
        let certificates = Certificates::issue();
        let standby_tls = Arc::new(TlsContext::load(&certificates.files(NODE_B)).unwrap());
        let active_tls = TlsContext::load(&certificates.files(NODE_A)).unwrap();
        let hello = Message::Hello {
            generation: 1,
            active_node: NODE_A.to_owned(),
        };

        for _ in 0..LINK_COUNT {
            let listener = TcpListener::bind((LOOPBACK, 0)).unwrap();
            let port = listener.local_addr().unwrap().port();
            let (received_sender, received) = mpsc::channel();
            let tls = Arc::clone(&standby_tls);
            let standby = thread::spawn(move || {
                let (tcp, _) = listener.accept().unwrap();
                let accepted = tls.accept(tcp).unwrap();
                let (message, _) = accepted.receiver.receive().unwrap();
                received_sender.send(message).unwrap();
            });

            let (sender, _receiver) = active_tls.connect(NODE_B, LOOPBACK, port).unwrap();
            sender.send(&hello, RECEIVE_TIMEOUT).unwrap();
            let message = received.recv_timeout(RECEIVE_TIMEOUT).expect("the standby received no message");
            assert_eq!(message, hello);
            standby.join().unwrap();
            sender.close();
        }
    }
}
