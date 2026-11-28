//! The jobs of the push engine, run against endpoints on the loopback interface.
//!
//! The tests cover single and list requests, keep-alive reuse between jobs, a job that stops
//! at a request not fully concluded, timeouts, a connection reset in the middle of a response,
//! a body larger than the socket buffers, redirects followed and refused, refusal by scope and TLS.

use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::process::Command;
use std::sync::Arc;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use rustls::pki_types::pem::PemObject;
use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use rustls::{ServerConfig, ServerConnection, StreamOwned};
use socket2::SockRef;

use super::super::job::{ErrorKind, PushJob, PushRequest};
use super::{EnginePools, run_job};
use crate::outgoing::tls::TlsSettings;

/// The timeout of the jobs of the tests, in seconds.
const JOB_TIMEOUT: f64 = 2.0;

/// The timeout of the job that waits for an endpoint that never answers, in seconds.
const SHORT_TIMEOUT: f64 = 0.3;

/// How many idle connections the pools of the tests keep per endpoint.
const POOL_SIZE: usize = 4;

/// The size of the body of the request larger than the socket buffers.
const LARGE_BODY_LEN: usize = 4 * 1024 * 1024;

/// The size of the socket buffers of the endpoint that reads slowly.
const SMALL_BUFFER_LEN: usize = 4096;

/// The size of each read of the endpoint that reads slowly.
const SLOW_READ_LEN: usize = 1024;

/// How long the endpoint that never answers keeps its connection open.
const SILENT_HOLD: Duration = Duration::from_secs(2);

/// The period of the byte pattern of the large body, a prime, so it is out of step with every buffer size.
const PATTERN_PERIOD: usize = 251;

/// What an endpoint of the tests received.
struct Received {

    /// How many connections it accepted.
    connections: usize,

    /// Each request as it arrived, the head and the body.
    requests: Vec<Vec<u8>>,
}

/// A response with the given status line, headers and body.
fn response(status_line: &str, headers: &[(&str, &str)], body: &[u8]) -> Vec<u8> {
    let mut out = format!("HTTP/1.1 {status_line}\r\nContent-Length: {}\r\n", body.len()).into_bytes();

    for (name, value) in headers {
        out.extend_from_slice(format!("{name}: {value}\r\n").as_bytes());
    }

    out.extend_from_slice(b"\r\n");
    out.extend_from_slice(body);
    out
}

/// Reads one request from a connection, or returns `None` once the client closed it.
fn read_request(connection: &mut impl Read) -> Option<Vec<u8>> {
    let mut received = Vec::new();
    let mut chunk = [0_u8; 8192];

    loop {
        let head_end = received.windows(4).position(|window| window == b"\r\n\r\n");

        if let Some(end) = head_end {
            let head = String::from_utf8_lossy(received.get(..end).unwrap()).to_ascii_lowercase();
            let length: usize = head
                .lines()
                .find_map(|line| line.strip_prefix("content-length: "))
                .map_or(0, |value| value.trim().parse().unwrap());

            if received.len() >= end + 4 + length {
                return Some(received);
            }
        }

        let count = connection.read(&mut chunk).ok()?;
        if count == 0 {
            return None;
        }
        received.extend_from_slice(chunk.get(..count).unwrap());
    }
}

/// Starts an endpoint that answers each request with the next of the responses, keeping each connection open,
/// and stops once it sent all of them.
fn serve(responses: Vec<Vec<u8>>) -> (SocketAddr, JoinHandle<Received>) {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let address = listener.local_addr().unwrap();

    let handle = thread::spawn(move || {
        let mut received = Received {
            connections: 0,
            requests: Vec::new(),
        };
        let mut pending = responses.into_iter();

        'accept: while let Ok((mut connection, _)) = listener.accept() {
            received.connections += 1;

            while let Some(request) = read_request(&mut connection) {
                received.requests.push(request);

                let Some(next) = pending.next() else {
                    break 'accept;
                };
                connection.write_all(&next).unwrap();

                if pending.len() == 0 {
                    break 'accept;
                }
            }
        }

        received
    });

    (address, handle)
}

/// A request of one message to the given address.
fn single(url: &str, msg_id: &str) -> PushRequest {
    PushRequest {
        url: url.to_owned(),
        headers: vec![(String::from("Content-Type"), b"application/json".to_vec())],
        parts: vec![b"{\"msg_id\":\"".to_vec(), msg_id.as_bytes().to_vec(), b"\"}".to_vec()],
        msg_ids: vec![msg_id.to_owned()],
        is_list: false,
    }
}

/// A request of several messages to the given address.
fn list(url: &str, msg_ids: &[&str]) -> PushRequest {
    let mut body = String::from("[");
    for (idx, msg_id) in msg_ids.iter().enumerate() {
        if idx > 0 {
            body.push(',');
        }
        body.push_str(&format!("{{\"msg_id\":\"{msg_id}\"}}"));
    }
    body.push(']');

    PushRequest {
        url: url.to_owned(),
        headers: vec![(String::from("Content-Type"), b"application/json".to_vec())],
        parts: vec![body.into_bytes()],
        msg_ids: msg_ids.iter().map(|msg_id| (*msg_id).to_owned()).collect(),
        is_list: true,
    }
}

/// A job of the given requests, with no TLS settings.
fn job(requests: Vec<PushRequest>, timeout: f64) -> PushJob {
    PushJob {
        id: 1,
        requests,
        timeout: Some(timeout),
        tls: TlsSettings::default(),
        tls_generation: 0,
    }
}

/// The body of a request, after its head.
fn body_of(request: &[u8]) -> &[u8] {
    let end = request.windows(4).position(|window| window == b"\r\n\r\n").unwrap();
    request.get(end + 4..).unwrap()
}

#[test]
fn single_message_is_concluded_by_a_2xx() {
    let (address, server) = serve(vec![response("200 OK", &[], b"")]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let outcomes = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], JOB_TIMEOUT));
    let received = server.join().unwrap();

    let outcome = outcomes.first().unwrap();
    assert!(outcome.error.is_none());
    assert_eq!(outcome.status, Some(200));
    assert_eq!(outcome.concluded, vec![String::from("zpsm.a1")]);
    assert_eq!(outcome.peer_scope.map(|scope| scope.name()), Some("loopback"));

    let request = received.requests.first().unwrap();
    assert!(request.starts_with(b"POST /orders/push HTTP/1.1\r\n"));
    assert_eq!(body_of(request), b"{\"msg_id\":\"zpsm.a1\"}");
}

#[test]
fn keep_alive_connection_is_reused_between_jobs() {
    let (address, server) = serve(vec![response("200 OK", &[], b""), response("204 No Content", &[], b"")]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let first = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], JOB_TIMEOUT));
    let second = run_job(&pools, &job(vec![single(&url, "zpsm.b2")], JOB_TIMEOUT));
    let received = server.join().unwrap();

    assert!(first.first().unwrap().error.is_none());
    assert!(second.first().unwrap().error.is_none());
    assert_eq!(received.connections, 1);
    assert_eq!(received.requests.len(), 2);
}

#[test]
fn list_response_concludes_what_it_names_and_the_job_stops() {
    let (address, server) = serve(vec![response("200 OK", &[], br#"["zpsm.a1"]"#)]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let requests = vec![list(&url, &["zpsm.a1", "zpsm.b2"]), list(&url, &["zpsm.c3"])];
    let outcomes = run_job(&pools, &job(requests, JOB_TIMEOUT));
    let received = server.join().unwrap();

    // The second request is not sent, because the first was not fully concluded
    assert_eq!(outcomes.len(), 1);
    assert_eq!(received.requests.len(), 1);

    let outcome = outcomes.first().unwrap();
    assert!(outcome.error.is_none());
    assert_eq!(outcome.concluded, vec![String::from("zpsm.a1")]);
}

#[test]
fn list_response_that_is_not_valid_concludes_nothing() {
    let bodies: [&[u8]; 3] = [b"OK", br#"{"accepted": ["zpsm.a1"]}"#, br#"["zpsm.a1", "zpsm.zz"]"#];

    for body in bodies {
        let (address, server) = serve(vec![response("200 OK", &[], body)]);
        let pools = EnginePools::new(POOL_SIZE);
        let url = format!("http://{address}/orders/push");

        let outcomes = run_job(&pools, &job(vec![list(&url, &["zpsm.a1", "zpsm.b2"])], JOB_TIMEOUT));
        server.join().unwrap();

        let outcome = outcomes.first().unwrap();
        assert!(outcome.concluded.is_empty());
        assert_eq!(outcome.error.as_ref().map(|error| error.kind), Some(ErrorKind::Reply));
    }
}

#[test]
fn status_other_than_2xx_concludes_nothing() {
    let (address, server) = serve(vec![response("503 Service Unavailable", &[], b"")]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let outcomes = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], JOB_TIMEOUT));
    server.join().unwrap();

    let outcome = outcomes.first().unwrap();
    let error = outcome.error.as_ref().unwrap();

    assert!(outcome.concluded.is_empty());
    assert_eq!(error.kind, ErrorKind::Status);
    assert!(error.message.starts_with("503 Server Error: Service Unavailable for url: http://"), "{}", error.message);
}

#[test]
fn endpoint_that_never_answers_times_out() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let address = listener.local_addr().unwrap();

    let server = thread::spawn(move || {
        let (mut connection, _) = listener.accept().unwrap();
        read_request(&mut connection);
        thread::sleep(SILENT_HOLD);
    });

    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let start = Instant::now();
    let outcomes = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], SHORT_TIMEOUT));
    let elapsed = start.elapsed();

    let error = outcomes.first().unwrap().error.as_ref().unwrap();
    assert_eq!(error.kind, ErrorKind::ReadTimeout);
    assert!(error.message.contains("Read timed out"), "{}", error.message);
    assert!(elapsed < SILENT_HOLD);

    server.join().unwrap();
}

#[test]
fn connection_reset_in_the_middle_of_a_response() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let address = listener.local_addr().unwrap();

    let server = thread::spawn(move || {
        let (mut connection, _) = listener.accept().unwrap();
        read_request(&mut connection);
        connection.write_all(b"HTTP/1.1 200 OK\r\nContent-Length: 100\r\n\r\npartial").unwrap();

        // A zero linger time makes the close send a reset rather than a regular end of the connection
        SockRef::from(&connection).set_linger(Some(Duration::ZERO)).unwrap();
    });

    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let outcomes = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], JOB_TIMEOUT));
    server.join().unwrap();

    let outcome = outcomes.first().unwrap();
    assert!(outcome.concluded.is_empty());
    assert!(matches!(
        outcome.error.as_ref().map(|error| error.kind),
        Some(ErrorKind::Connection | ErrorKind::Chunked | ErrorKind::Incomplete)
    ));
}

#[test]
fn body_larger_than_the_socket_buffers() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    SockRef::from(&listener).set_recv_buffer_size(SMALL_BUFFER_LEN).unwrap();
    let address = listener.local_addr().unwrap();

    let body: Vec<u8> = (0..LARGE_BODY_LEN).map(|position| u8::try_from(position % PATTERN_PERIOD).unwrap_or(0)).collect();
    let expected = body.clone();

    // The endpoint reads in small chunks, so the writes of the engine are partial and wait for the socket
    let server = thread::spawn(move || {
        let (mut connection, _) = listener.accept().unwrap();
        let mut received = Vec::new();
        let mut chunk = [0_u8; SLOW_READ_LEN];

        while received.windows(4).position(|window| window == b"\r\n\r\n").is_none_or(|end| received.len() < end + 4 + LARGE_BODY_LEN) {
            let count = connection.read(&mut chunk).unwrap();
            received.extend_from_slice(chunk.get(..count).unwrap());
        }

        connection.write_all(&response("200 OK", &[], b"")).unwrap();
        received
    });

    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/files/push");

    let mut request = single(&url, "zpsm.large");
    request.parts = vec![body];

    let outcomes = run_job(&pools, &job(vec![request], JOB_TIMEOUT));
    let received = server.join().unwrap();

    assert!(outcomes.first().unwrap().error.is_none());
    assert_eq!(body_of(&received), expected.as_slice());
}

#[test]
fn redirect_is_followed_with_the_same_body() {
    let (address, server) = serve(vec![
        response("307 Temporary Redirect", &[("Location", "/orders/v2/push")], b""),
        response("200 OK", &[], br#"["zpsm.a1","zpsm.b2"]"#),
    ]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let outcomes = run_job(&pools, &job(vec![list(&url, &["zpsm.a1", "zpsm.b2"])], JOB_TIMEOUT));
    let received = server.join().unwrap();

    let outcome = outcomes.first().unwrap();
    assert!(outcome.error.is_none());
    assert_eq!(outcome.concluded.len(), 2);
    assert_eq!(outcome.url, format!("http://{address}/orders/v2/push"));

    let redirect = outcome.redirects.first().unwrap();
    assert_eq!(redirect.status, 307);

    let first = received.requests.first().unwrap();
    let second = received.requests.get(1).unwrap();
    assert!(second.starts_with(b"POST /orders/v2/push HTTP/1.1\r\n"));
    assert_eq!(body_of(first), body_of(second));
}

#[test]
fn redirect_not_followed_concludes_nothing() {
    let (address, server) = serve(vec![response("307 Temporary Redirect", &[("Location", "ftp://files.example.com/push")], b"")]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let outcomes = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], JOB_TIMEOUT));
    server.join().unwrap();

    let error = outcomes.first().unwrap().error.as_ref().unwrap();
    assert_eq!(error.kind, ErrorKind::Redirect);
    assert!(error.message.contains("with a scheme other than http and https"), "{}", error.message);
}

#[test]
fn redirect_to_another_scope_is_refused() {
    let (address, server) = serve(vec![response("308 Permanent Redirect", &[("Location", "http://10.20.30.40/orders/push")], b"")]);
    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("http://{address}/orders/push");

    let outcomes = run_job(&pools, &job(vec![single(&url, "zpsm.a1")], JOB_TIMEOUT));
    server.join().unwrap();

    let error = outcomes.first().unwrap().error.as_ref().unwrap();
    assert_eq!(error.kind, ErrorKind::ScopeRefused);
    assert!(error.message.contains("within the required network scope `loopback`"), "{}", error.message);
}

#[test]
fn address_not_supported() {
    let pools = EnginePools::new(POOL_SIZE);

    let outcomes = run_job(&pools, &job(vec![single("http://ORDERS.example.com/push", "zpsm.a1")], JOB_TIMEOUT));

    let error = outcomes.first().unwrap().error.as_ref().unwrap();
    assert_eq!(error.kind, ErrorKind::Address);
}

/// The extensions of the certificate of the endpoint.
const LEAF_EXTENSIONS: &str = "basicConstraints=CA:FALSE\nextendedKeyUsage=serverAuth\nsubjectAltName=IP:127.0.0.1\n";

/// The key arguments of the openssl commands.
const KEY_ARGS: [&str; 5] = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1", "-nodes"];

/// The paths of the certificates and the key of the TLS test.
struct TestCertificates {

    /// The CA that issued the certificate of the endpoint.
    ca_path: String,

    /// The certificate of the endpoint.
    cert_path: String,

    /// The key of the endpoint.
    key_path: String,
}

/// Runs openssl with the given arguments, returning whether it succeeded.
fn openssl(args: &[&std::ffi::OsStr]) -> bool {
    Command::new("openssl").args(args).output().is_ok_and(|output| output.status.success())
}

/// Generates a CA and a certificate for 127.0.0.1 that it issued,
/// or returns `None` if the openssl command is not available.
fn issue_certificates(directory: &std::path::Path) -> Option<TestCertificates> {
    let ca_path = directory.join("ca.pem");
    let ca_key_path = directory.join("ca.key");
    let csr_path = directory.join("endpoint.csr");
    let cert_path = directory.join("endpoint.pem");
    let key_path = directory.join("endpoint.key");
    let extensions_path = directory.join("endpoint.ext");

    std::fs::write(&extensions_path, LEAF_EXTENSIONS).ok()?;

    let key_args: Vec<&std::ffi::OsStr> = KEY_ARGS.iter().map(std::ffi::OsStr::new).collect();
    let os = std::ffi::OsStr::new;

    let mut ca_args = vec![os("req"), os("-x509"), os("-days"), os("1"), os("-subj"), os("/CN=Zato Test CA")];
    ca_args.extend_from_slice(&key_args);
    ca_args.extend_from_slice(&[os("-keyout"), ca_key_path.as_os_str(), os("-out"), ca_path.as_os_str()]);

    let mut csr_args = vec![os("req"), os("-new"), os("-subj"), os("/CN=127.0.0.1")];
    csr_args.extend_from_slice(&key_args);
    csr_args.extend_from_slice(&[os("-keyout"), key_path.as_os_str(), os("-out"), csr_path.as_os_str()]);

    let sign_args = [
        os("x509"), os("-req"), os("-days"), os("1"), os("-in"), csr_path.as_os_str(),
        os("-CA"), ca_path.as_os_str(), os("-CAkey"), ca_key_path.as_os_str(), os("-CAcreateserial"),
        os("-extfile"), extensions_path.as_os_str(), os("-out"), cert_path.as_os_str(),
    ];

    let is_issued = openssl(&ca_args) && openssl(&csr_args) && openssl(&sign_args);

    is_issued.then(|| TestCertificates {
        ca_path: ca_path.display().to_string(),
        cert_path: cert_path.display().to_string(),
        key_path: key_path.display().to_string(),
    })
}

#[test]
fn tls_endpoint_verified_against_its_certificate() {
    let directory = tempfile::tempdir().unwrap();

    let Some(certificates) = issue_certificates(directory.path()) else {
        return;
    };

    let chain: Vec<CertificateDer<'static>> = CertificateDer::pem_file_iter(&certificates.cert_path).unwrap().map(Result::unwrap).collect();
    let key = PrivateKeyDer::from_pem_file(&certificates.key_path).unwrap();

    let provider = Arc::new(rustls::crypto::ring::default_provider());
    let config = ServerConfig::builder_with_provider(provider)
        .with_safe_default_protocol_versions()
        .unwrap()
        .with_no_client_auth()
        .with_single_cert(chain, key)
        .unwrap();
    let config = Arc::new(config);

    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let address = listener.local_addr().unwrap();

    let server = thread::spawn(move || {
        let (tcp, _): (TcpStream, _) = listener.accept().unwrap();
        let session = ServerConnection::new(config).unwrap();
        let mut stream = StreamOwned::new(session, tcp);

        let request = read_request(&mut stream);
        if request.is_some() {
            stream.write_all(&response("200 OK", &[], b"")).unwrap();
            stream.flush().unwrap();
        }
        request
    });

    let pools = EnginePools::new(POOL_SIZE);
    let url = format!("https://{address}/orders/push");

    let mut tls_job = job(vec![single(&url, "zpsm.tls")], JOB_TIMEOUT);
    tls_job.tls = TlsSettings {
        ca_path: Some(certificates.ca_path),
        client_cert: None,
        client_key: None,
    };

    let outcomes = run_job(&pools, &tls_job);
    let request = server.join().unwrap();

    let error = outcomes.first().unwrap().error.as_ref().map(|error| error.message.clone());
    assert_eq!(error, None);
    assert_eq!(body_of(&request.unwrap()), b"{\"msg_id\":\"zpsm.tls\"}");
}

#[test]
fn newer_tls_generation_reads_the_files_anew() {
    let directory = tempfile::tempdir().unwrap();

    let Some(certificates) = issue_certificates(directory.path()) else {
        return;
    };

    let pools = EnginePools::new(POOL_SIZE);
    let settings = TlsSettings {
        ca_path: Some(certificates.ca_path.clone()),
        client_cert: None,
        client_key: None,
    };

    assert!(pools.select(true, &settings, 0).is_ok());

    // With the file removed, the configuration of the same generation is still the one built before ..
    std::fs::remove_file(&certificates.ca_path).unwrap();
    assert!(pools.select(true, &settings, 0).is_ok());

    // .. while a newer generation reads the files again.
    assert!(pools.select(true, &settings, 1).is_err());
}
