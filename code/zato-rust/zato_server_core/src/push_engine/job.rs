//! The jobs of the push engine and the outcomes of their requests.

use crate::outgoing::scope::NetworkScope;
use crate::outgoing::tls::TlsSettings;

/// One push request of a job - one message, or a JSON list of several messages, posted to one endpoint.
pub struct PushRequest {

    /// The address the request is posted to.
    pub url: String,

    /// The headers of the request, their names valid and their values encoded as sent.
    pub headers: Vec<(String, Vec<u8>)>,

    /// The parts of the body, in order, copied from Python when the job was submitted.
    pub parts: Vec<Vec<u8>>,

    /// The IDs of the messages the request carries, in their order.
    pub msg_ids: Vec<String>,

    /// Whether the body is a JSON list of envelopes, whose response names the messages it accepted.
    pub is_list: bool,
}

/// The ordered requests of one push subscriber, run on one thread of the engine one after another.
pub struct PushJob {

    /// The ID the Python side gave the job, by which it receives the outcome.
    pub id: u64,

    /// The requests, in the order they are sent.
    pub requests: Vec<PushRequest>,

    /// How long each connect and each read may take, in seconds, or `None` for no limit.
    pub timeout: Option<f64>,

    /// How the TLS connections of the job are established.
    pub tls: TlsSettings,

    /// The generation of the TLS material of the connection, increased each time its files are read anew,
    /// so that a configuration built from the previous contents of the same files is not used again.
    pub tls_generation: u64,
}

/// Why a request was not fully concluded.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ErrorKind {

    /// The address is not one the engine sends to.
    Address,

    /// The TLS configuration could not be built from the TLS settings of the job.
    TlsConfig,

    /// The connection could not be established within the timeout.
    ConnectTimeout,

    /// The endpoint did not send the next part of its response within the timeout.
    ReadTimeout,

    /// The connection could not be established, or it was closed or reset before the response arrived.
    Connection,

    /// The TLS handshake failed or the endpoint ended the TLS session with an alert.
    Tls,

    /// The connection was closed or reset while the body of the response was being read.
    Chunked,

    /// No resolved address of the host is within the network scope of the first push.
    ScopeRefused,

    /// A redirect was not followed.
    Redirect,

    /// The final response had a status other than 2xx.
    Status,

    /// The response ended before the length its head declared.
    Incomplete,

    /// The response to a list of messages was not a JSON list of the IDs of the request.
    Reply,
}

impl ErrorKind {

    /// The name of the kind, as Python receives it.
    pub const fn name(self) -> &'static str {
        match self {
            Self::Address => "address",
            Self::TlsConfig => "tls_config",
            Self::ConnectTimeout => "connect_timeout",
            Self::ReadTimeout => "read_timeout",
            Self::Connection => "connection",
            Self::Tls => "tls",
            Self::Chunked => "chunked",
            Self::ScopeRefused => "scope_refused",
            Self::Redirect => "redirect",
            Self::Status => "status",
            Self::Incomplete => "incomplete",
            Self::Reply => "reply",
        }
    }
}

/// An error of a request, with the message the Python side logs or raises.
pub struct PushError {

    /// What failed.
    pub kind: ErrorKind,

    /// The description of the failure.
    pub message: String,
}

/// A redirect that a request followed.
pub struct FollowedRedirect {

    /// The status of the redirect, 307 or 308.
    pub status: u16,

    /// The address that answered with the redirect.
    pub from_url: String,

    /// The address the redirect led to.
    pub to_url: String,
}

/// What one request of a job concluded.
pub struct RequestOutcome {

    /// The last address the request was sent to, after any redirects.
    pub url: String,

    /// The status of the final response, or `None` if no response arrived.
    pub status: Option<u16>,

    /// The reason phrase of the final response, empty if no response arrived.
    pub reason: String,

    /// The IDs of the messages the request concluded as delivered.
    pub concluded: Vec<String>,

    /// How long the request took until the head of its final response was read, in microseconds.
    pub elapsed_us: u64,

    /// The network scope of the address of the first push, or `None` if it had none or no connection was made.
    pub peer_scope: Option<NetworkScope>,

    /// Why the request was not fully concluded, if it was not.
    pub error: Option<PushError>,

    /// The redirects the request followed, in order.
    pub redirects: Vec<FollowedRedirect>,
}

impl RequestOutcome {

    /// An outcome of a request to the given address before any response arrived.
    pub fn new(url: &str) -> Self {
        Self {
            url: url.to_owned(),
            status: None,
            reason: String::new(),
            concluded: Vec::new(),
            elapsed_us: 0,
            peer_scope: None,
            error: None,
            redirects: Vec::new(),
        }
    }

    /// Records why the request was not concluded.
    pub fn fail(&mut self, kind: ErrorKind, message: String) {
        self.error = Some(PushError { kind, message });
    }

    /// Whether every message of the request was concluded, which lets the job continue with its next request.
    pub fn is_fully_concluded(&self, request: &PushRequest) -> bool {
        self.error.is_none() && self.concluded.len() == request.msg_ids.len()
    }
}

/// What one job concluded, or the panic that ended it.
pub struct JobOutcome {

    /// The ID of the job.
    pub id: u64,

    /// The outcome of each request that was sent, in order, which stops at the first request not fully concluded.
    pub requests: Vec<RequestOutcome>,

    /// The message of a panic that ended the job, if one did.
    pub panic: Option<String>,
}
