//! IBM MQ consumer and producer wrappers for the standalone Zato queue bridge.
//!
//! The IBM MQ client library `libmqm_r.so` is loaded at runtime with dlopen2,
//! so deployments that use only Kafka keep working without the client installed.
//! TLS connections build a PKCS#12 key repository on the fly from the PEM files
//! given in the connection config.

#![cfg(feature = "ibm-mq")]

use std::fmt::Write;
use std::str::FromStr;
use std::sync::Arc;
use std::sync::atomic::Ordering;

use libmqm_sys::dlopen2::MqmContainer;
use mqi::connection::{Credentials, ThreadNone, Tls};
use mqi::get::{GetConvert, GetWait};
use mqi::prelude::*;
use mqi::types::{ApplName, CertificateLabel, CipherSpec, KeyRepo, MQMT, QueueManagerName, QueueName};
use mqi::{Connection, MqStr, Object, connection::MqServer, constants, structs, types};
use tokio_util::sync::CancellationToken;

use crate::bridge::{BridgeShared, ChannelConfig, OutgoingConfig, RecvEvent};
use crate::rfh2;

/// Application name reported to the queue manager for all bridge connections.
const APP_NAME: ApplName = ApplName(mqi::mqstr!("zato_queue_bridge"));

/// How long a single MQGET waits for a message before the loop re-checks cancellation.
const GET_WAIT_INTERVAL_MS: types::MQLONG = 5_000;

/// Buffer size for MQGET calls - matches the default IBM MQ maximum message length.
const GET_BUFFER_SIZE: usize = 4 * 1024 * 1024;

/// Delay before reconnecting after a connection-level failure.
const RECONNECT_DELAY: std::time::Duration = std::time::Duration::from_secs(5);

/// Cipher used when a TLS connection does not specify one explicitly.
const DEFAULT_CIPHER_SPEC: &str = "ANY_TLS12_OR_HIGHER";

/// Format name of messages that carry an MQRFH2 header.
const FORMAT_RF_HEADER_2: &str = "MQHRF2";

/// Environment variable that overrides the IBM MQ client library path.
const CLIENT_LIB_ENV: &str = "Zato_MQ_Client_Lib";

/// Default IBM MQ client library name, resolved through the standard loader search rules.
const CLIENT_LIB_DEFAULT: &str = "libmqm_r.so";

/// Type alias for the runtime-loaded MQ library shared by a connection.
type MqLibrary = Arc<MqmContainer>;

/// Type alias for a bridge connection to a queue manager.
type MqConnection = Connection<MqLibrary, ThreadNone>;

/// Sequence number that keeps concurrently built key repository files apart.
static KEY_REPOSITORY_SEQUENCE: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

// ################################################################################################################################

/// Loads the IBM MQ client library `libmqm_r.so` at runtime.
///
/// The `Zato_MQ_Client_Lib` environment variable may hold a full path to the library,
/// otherwise the standard dynamic loader search rules apply.
fn load_client_library() -> Result<MqLibrary, String> {
    let lib_path = std::env::var(CLIENT_LIB_ENV).unwrap_or_else(|_| CLIENT_LIB_DEFAULT.to_string());

    // Loading a dynamic library is the one place in this crate where unsafe code is required.
    #[expect(unsafe_code, reason = "dlopen of the IBM MQ client library is inherently unsafe")]
    let container = unsafe { MqmContainer::load(&lib_path) };

    let container = container.map_err(|err| format!("Cannot load IBM MQ client library `{lib_path}`: {err}"))?;

    Ok(Arc::new(container))
}

// ################################################################################################################################

/// Connection details shared by channels and outgoing connections.
pub struct ConnDetails {

    /// Broker address as `host:port`.
    pub address: String,

    /// Queue manager name.
    pub queue_manager: String,

    /// Server-connection channel name, e.g. `DEV.APP.SVRCONN`.
    pub mq_channel_name: String,

    /// Username, empty when the queue manager does not require credentials.
    pub username: String,

    /// Password matching the username.
    pub password: String,

    /// Whether TLS is enabled.
    pub ssl: bool,

    /// TLS cipher specification, e.g. `ANY_TLS12_OR_HIGHER`.
    pub cipher_spec: String,

    /// Path to the CA certificate PEM file.
    pub ssl_ca_file: Option<String>,

    /// Path to the client certificate PEM file for mutual TLS.
    pub ssl_cert_file: Option<String>,

    /// Path to the client private key PEM file for mutual TLS.
    pub ssl_key_file: Option<String>,
}

impl ChannelConfig {
    /// Returns the MQ connection details of this channel config.
    pub fn mq_details(&self) -> ConnDetails {
        ConnDetails {
            address: self.address.clone(),
            queue_manager: self.queue_manager.clone(),
            mq_channel_name: self.mq_channel_name.clone(),
            username: self.username.clone(),
            password: self.password.clone(),
            ssl: self.ssl,
            cipher_spec: self.cipher_spec.clone(),
            ssl_ca_file: self.ssl_ca_file.clone(),
            ssl_cert_file: self.ssl_cert_file.clone(),
            ssl_key_file: self.ssl_key_file.clone(),
        }
    }
}

impl OutgoingConfig {
    /// Returns the MQ connection details of this outgoing config.
    pub fn mq_details(&self) -> ConnDetails {
        ConnDetails {
            address: self.address.clone(),
            queue_manager: self.queue_manager.clone(),
            mq_channel_name: self.mq_channel_name.clone(),
            username: self.username.clone(),
            password: self.password.clone(),
            ssl: self.ssl,
            cipher_spec: self.cipher_spec.clone(),
            ssl_ca_file: self.ssl_ca_file.clone(),
            ssl_cert_file: self.ssl_cert_file.clone(),
            ssl_key_file: self.ssl_key_file.clone(),
        }
    }
}

// ################################################################################################################################

/// A PKCS#12 key repository built from PEM files, with the password MQ needs to open it.
struct KeyRepository {

    /// Full path to the `.p12` file.
    path: std::path::PathBuf,

    /// Password protecting the file.
    password: String,
}

impl Drop for KeyRepository {
    fn drop(&mut self) {
        // GSKit reads the keystore during MQCONNX, so the file is not needed once
        // the connect attempt is over and it never outlives the connection.
        let _ = std::fs::remove_file(&self.path);
    }
}

/// Builds a PKCS#12 key repository file from the PEM files in the connection details.
///
/// IBM MQ clients cannot use PEM files directly - they need a CMS or PKCS#12 key
/// repository, so one is assembled in a per-connection file under the temp directory.
fn build_key_repository(details: &ConnDetails, conn_name: &str) -> Result<KeyRepository, String> {
    use openssl::pkcs12::Pkcs12;
    use openssl::pkey::PKey;
    use openssl::stack::Stack;
    use openssl::x509::X509;

    let mut builder = Pkcs12::builder();

    // The CA certificates form the trust store used to verify the queue manager ..
    if let Some(ca_path) = &details.ssl_ca_file {
        let ca_pem = std::fs::read(ca_path).map_err(|err| format!("Cannot read CA file `{ca_path}`: {err}"))?;
        let ca_certs = X509::stack_from_pem(&ca_pem).map_err(|err| format!("Cannot parse CA file `{ca_path}`: {err}"))?;

        let mut ca_stack = Stack::new().map_err(|err| format!("Cannot build CA stack: {err}"))?;
        for ca_cert in ca_certs {
            ca_stack.push(ca_cert).map_err(|err| format!("Cannot add CA certificate: {err}"))?;
        }
        let _ = builder.ca(ca_stack);
    }

    // .. the client certificate and key are only needed for mutual TLS.
    if let Some(cert_path) = &details.ssl_cert_file {
        let cert_pem = std::fs::read(cert_path).map_err(|err| format!("Cannot read cert file `{cert_path}`: {err}"))?;
        let cert = X509::from_pem(&cert_pem).map_err(|err| format!("Cannot parse cert file `{cert_path}`: {err}"))?;
        let _ = builder.cert(&cert);
    }

    if let Some(key_path) = &details.ssl_key_file {
        let key_pem = std::fs::read(key_path).map_err(|err| format!("Cannot read key file `{key_path}`: {err}"))?;
        let key = PKey::private_key_from_pem(&key_pem).map_err(|err| format!("Cannot parse key file `{key_path}`: {err}"))?;
        let _ = builder.pkey(&key);
    }

    // A random password protects the repository for the lifetime of the connection.
    let mut password_bytes = [0_u8; 24];
    openssl::rand::rand_bytes(&mut password_bytes).map_err(|err| format!("Cannot generate keystore password: {err}"))?;
    let mut password = String::with_capacity(password_bytes.len() * 2);
    for byte in password_bytes {
        let _ = write!(password, "{byte:02x}");
    }

    let pkcs12 = builder
        .build2(&password)
        .map_err(|err| format!("Cannot build PKCS#12 keystore: {err}"))?;
    let der = pkcs12.to_der().map_err(|err| format!("Cannot serialize PKCS#12 keystore: {err}"))?;

    // The file lives in a bridge-specific directory under the system temp directory ..
    let repo_dir = std::env::temp_dir().join("zato-queue-bridge");
    std::fs::create_dir_all(&repo_dir).map_err(|err| format!("Cannot create key repository directory: {err}"))?;

    // .. named after the connection plus a process-wide sequence number, because parallel
    // connects to the same queue manager each generate their own keystore password and
    // sharing one file would make one connection read a file another one just rewrote.
    let sequence = KEY_REPOSITORY_SEQUENCE.fetch_add(1, Ordering::Relaxed);

    let mut file_name = String::with_capacity(conn_name.len() + 24);
    for character in conn_name.chars() {
        if character.is_ascii_alphanumeric() {
            file_name.push(character);
        } else {
            file_name.push('_');
        }
    }
    let _ = write!(file_name, ".{}.{sequence}.p12", std::process::id());

    let path = repo_dir.join(file_name);
    std::fs::write(&path, &der).map_err(|err| format!("Cannot write key repository `{}`: {err}", path.display()))?;

    let out = KeyRepository { path, password };

    Ok(out)
}

// ################################################################################################################################

/// Connects to the queue manager described by the given connection details.
fn connect(details: &ConnDetails) -> Result<MqConnection, String> {
    let lib = load_client_library()?;

    // MQ expects the connection name as `host(port)` while Zato stores `host:port`.
    let connection_name = match details.address.rsplit_once(':') {
        Some((host, port)) => format!("{host}({port})"),
        None => details.address.clone(),
    };

    let server_definition = format!("{}/TCP/{}", details.mq_channel_name, connection_name);
    let server =
        MqServer::try_from(server_definition.as_str()).map_err(|err| format!("Invalid MQ server `{server_definition}`: {err:?}"))?;

    let queue_manager = QueueManagerName::from_str(&details.queue_manager)
        .map_err(|err| format!("Invalid queue manager name `{}`: {err}", details.queue_manager))?;

    // Credentials are optional - developer queue managers often accept anonymous connections.
    let credentials = if details.username.is_empty() {
        None
    } else {
        Some(Credentials::User(details.username.as_str(), details.password.as_str().into()))
    };

    // TLS needs a PKCS#12 key repository built from the configured PEM files.
    let key_repository = if details.ssl {
        let repository = build_key_repository(details, &details.queue_manager)?;
        Some(repository)
    } else {
        None
    };

    let tls = match &key_repository {
        Some(repository) => {
            let cipher_name = if details.cipher_spec.is_empty() {
                DEFAULT_CIPHER_SPEC
            } else {
                details.cipher_spec.as_str()
            };
            let cipher_mqstr =
                MqStr::from_str(cipher_name).map_err(|err| format!("Invalid cipher spec `{cipher_name}`: {err}"))?;
            let cipher = CipherSpec(cipher_mqstr);

            let repo_path = repository.path.display().to_string();
            let repo_mqstr =
                MqStr::from_str(&repo_path).map_err(|err| format!("Key repository path too long `{repo_path}`: {err}"))?;
            let key_repo = KeyRepo(repo_mqstr);

            let mut tls = Tls::new(&key_repo, None::<&CertificateLabel>, &cipher);
            let repo_password: types::ProtectedSecret<&str> = repository.password.as_str().into();
            let _ = tls.key_repo_password(Some(repo_password));

            Some(tls)
        }
        None => None,
    };

    let connection = mqi::connect_lib::<ThreadNone, _>(lib, &(APP_NAME, tls, queue_manager, credentials, server))
        .warn_as_error()
        .map_err(|err| format!("Cannot connect to queue manager `{}`: {err}", details.queue_manager))?;

    Ok(connection)
}

// ################################################################################################################################

/// Converts an MQ character field (space-padded, possibly NUL-padded) to a trimmed string.
fn mq_field_to_string(field: &[types::MQCHAR]) -> String {
    let mut bytes = Vec::with_capacity(field.len());
    for &character in field {
        bytes.push(character as u8);
    }

    String::from_utf8_lossy(&bytes).trim_end_matches(['\0', ' ']).to_string()
}

/// Converts a binary MQ identifier (MsgId, CorrelId) to a lowercase hex string.
fn identifier_to_hex(identifier: &[u8]) -> String {
    let mut out = String::with_capacity(identifier.len() * 2);
    for byte in identifier {
        let _ = write!(out, "{byte:02x}");
    }

    out
}

/// Parses a lowercase hex string back into a 24-byte MQ identifier.
fn hex_to_identifier(hex: &str) -> Result<[u8; 24], String> {
    let mut out = [0_u8; 24];

    if hex.len() != 48 {
        return Err(format!("Invalid MQ identifier length: {}", hex.len()));
    }

    for (index, chunk) in hex.as_bytes().chunks(2).enumerate() {
        let pair = std::str::from_utf8(chunk).map_err(|err| format!("Invalid MQ identifier: {err}"))?;
        out[index] = u8::from_str_radix(pair, 16).map_err(|err| format!("Invalid MQ identifier: {err}"))?;
    }

    Ok(out)
}

/// Builds the MQMD-derived headers exposed to services.
fn build_mqmd_headers(md: &structs::MQMD, headers: &mut Vec<(String, String)>) {
    headers.push(("mqmd.message_id".to_string(), identifier_to_hex(&md.MsgId)));
    headers.push(("mqmd.correlation_id".to_string(), identifier_to_hex(&md.CorrelId)));
    headers.push(("mqmd.reply_to_queue".to_string(), mq_field_to_string(&md.ReplyToQ)));
    headers.push(("mqmd.reply_to_queue_manager".to_string(), mq_field_to_string(&md.ReplyToQMgr)));
    headers.push(("mqmd.format".to_string(), mq_field_to_string(&md.Format)));
    headers.push(("mqmd.priority".to_string(), md.Priority.to_string()));
    headers.push(("mqmd.persistence".to_string(), md.Persistence.to_string()));
    headers.push(("mqmd.expiry".to_string(), md.Expiry.to_string()));

    // PutDate is YYYYMMDD and PutTime is HHMMSSTH, combined into one readable value.
    let put_date = mq_field_to_string(&md.PutDate);
    let put_time = mq_field_to_string(&md.PutTime);
    let put_date_time = if put_date.len() == 8 && put_time.len() == 8 {
        format!(
            "{}-{}-{}T{}:{}:{}.{}",
            &put_date[0..4],
            &put_date[4..6],
            &put_date[6..8],
            &put_time[0..2],
            &put_time[2..4],
            &put_time[4..6],
            &put_time[6..8],
        )
    } else {
        format!("{put_date} {put_time}")
    };
    headers.push(("mqmd.put_date_time".to_string(), put_date_time));
}

/// Serializes header pairs into the JSON object string carried in recv events.
fn headers_to_json(headers: &[(String, String)]) -> String {
    let mut map = serde_json::Map::with_capacity(headers.len());
    for (key, value) in headers {
        let _ = map.insert(key.clone(), serde_json::Value::String(value.clone()));
    }

    serde_json::Value::Object(map).to_string()
}

// ################################################################################################################################

/// Builds a recv event from one consumed message, parsing MQRFH2 headers when present.
fn build_recv_event(config: &ChannelConfig, data: Vec<u8>, md: &structs::MQMD) -> RecvEvent {
    let mut headers = Vec::new();
    build_mqmd_headers(md, &mut headers);

    let md_format = mq_field_to_string(&md.Format);
    let mut payload = data;

    // Messages in MQHRF2 format start with an MQRFH2 header holding JMS and user folders ..
    if md_format == FORMAT_RF_HEADER_2 && rfh2::has_rfh2(&payload) {
        match rfh2::parse_rfh2(&payload) {
            Ok(parsed) => {
                for header in parsed.headers {
                    headers.push(header);
                }

                // .. which is stripped from the payload when the channel says so.
                if config.remove_jms_headers {
                    payload = payload.split_off(parsed.header_length);
                }
            }
            Err(err) => {
                tracing::warn!("IBM MQ consumer `{}`: cannot parse MQRFH2 header: {err}", config.name);
            }
        }
    }

    RecvEvent {
        channel_name: config.name.clone(),
        topic: config.queue.clone(),
        service: config.service.clone(),
        payload,
        headers: headers_to_json(&headers),
        reply_to_queue: mq_field_to_string(&md.ReplyToQ),
        reply_to_queue_manager: mq_field_to_string(&md.ReplyToQMgr),
        message_id: identifier_to_hex(&md.MsgId),
    }
}

// ################################################################################################################################

/// Runs the blocking consume loop body for one IBM MQ channel.
///
/// Returns when the cancellation token or the global stop flag is set.
fn consume_loop_blocking(
    config: &ChannelConfig,
    message_sender: &tokio::sync::mpsc::UnboundedSender<RecvEvent>,
    shared: &BridgeShared,
    cancel: &CancellationToken,
) {
    let details = config.mq_details();

    loop {
        if shared.stop_flag.load(Ordering::Relaxed) || cancel.is_cancelled() {
            tracing::info!("IBM MQ consumer `{}` stopping", config.name);
            return;
        }

        // Establish the connection, backing off when the queue manager is not reachable ..
        let connection = match connect(&details) {
            Ok(connection) => connection,
            Err(err) => {
                tracing::warn!("IBM MQ consumer `{}`: waiting for queue manager: {err}", config.name);
                std::thread::sleep(RECONNECT_DELAY);
                continue;
            }
        };

        // .. and open the queue for input.
        let queue_name = match QueueName::from_str(&config.queue) {
            Ok(queue_name) => queue_name,
            Err(err) => {
                tracing::error!("IBM MQ consumer `{}`: invalid queue name `{}`: {err}", config.name, config.queue);
                return;
            }
        };

        let open_options = constants::MQOO_INPUT_AS_Q_DEF | constants::MQOO_FAIL_IF_QUIESCING;
        let object = match Object::open(&connection, &(queue_name, open_options)).warn_as_error() {
            Ok(object) => object,
            Err(err) => {
                tracing::warn!("IBM MQ consumer `{}`: cannot open queue `{}`: {err}", config.name, config.queue);
                std::thread::sleep(RECONNECT_DELAY);
                continue;
            }
        };

        tracing::info!("IBM MQ consumer `{}` connected to queue `{}`", config.name, config.queue);

        // Keep getting messages until cancellation or a connection-level failure.
        loop {
            if shared.stop_flag.load(Ordering::Relaxed) || cancel.is_cancelled() {
                tracing::info!("IBM MQ consumer `{}` stopping", config.name);
                return;
            }

            let get_options = (
                GetWait::Wait(GET_WAIT_INTERVAL_MS),
                GetConvert::NoConvert,
                constants::MQGMO_NO_SYNCPOINT | constants::MQGMO_FAIL_IF_QUIESCING,
            );

            let buffer = vec![0_u8; GET_BUFFER_SIZE];
            let result: Result<_, mqi::result::Error> =
                object.get_as::<(Vec<u8>, structs::MQMD), _, _>(&get_options, buffer).warn_as_error();

            match result {
                // A message arrived - forward it to the recv publisher.
                Ok(Some((data, md))) => {
                    let event = build_recv_event(config, data, &md);
                    if message_sender.send(event).is_err() {
                        return;
                    }
                }

                // The wait interval elapsed without a message - loop around for cancellation checks.
                Ok(None) => {}

                // Anything else means the connection is gone - reconnect with backoff.
                Err(err) => {
                    tracing::warn!("IBM MQ consumer `{}`: receive error, reconnecting: {err}", config.name);
                    std::thread::sleep(RECONNECT_DELAY);
                    break;
                }
            }
        }
    }
}

/// Runs a consume loop for a single IBM MQ channel on a blocking thread.
///
/// Exits when the `cancel` token is cancelled or the global stop flag is set.
pub async fn consume_loop(
    config: ChannelConfig,
    message_sender: tokio::sync::mpsc::UnboundedSender<RecvEvent>,
    shared: Arc<BridgeShared>,
    cancel: CancellationToken,
) {
    // MQGET blocks the thread, so the whole loop runs on the blocking thread pool.
    let join_result = tokio::task::spawn_blocking(move || {
        consume_loop_blocking(&config, &message_sender, &shared, &cancel);
    })
    .await;

    if let Err(err) = join_result {
        tracing::error!("IBM MQ consumer task panicked: {err}");
    }
}

// ################################################################################################################################

/// Message format used for outgoing text payloads.
fn text_message_format() -> types::MessageFormat {
    types::MessageFormat {
        ccsid: mqi::string::CCSID(1208),
        encoding: constants::MQENC_NATIVE,
        fmt: mqi::header::TextEnc::Ascii(mqi::header::fmt::MQFMT_STRING),
    }
}

/// Publishes a single message to the queue of an outgoing IBM MQ connection.
///
/// Uses MQPUT1 through a one-shot connection, mirroring the Kafka one-shot producer.
pub fn publish_message(config: &OutgoingConfig, payload: &[u8]) -> Result<(), String> {
    let details = config.mq_details();
    let connection = connect(&details)?;

    let queue_name =
        QueueName::from_str(&config.queue).map_err(|err| format!("Invalid queue name `{}`: {err}", config.queue))?;

    let put_options = constants::MQPMO_NO_SYNCPOINT | constants::MQPMO_FAIL_IF_QUIESCING;
    let format = text_message_format();

    connection
        .put_message(&(queue_name, put_options), &(), &(payload, format))
        .warn_as_error()
        .map_err(|err| format!("IBM MQ send to `{}` failed: {err}", config.queue))?;

    let _ = connection.disconnect();

    Ok(())
}

// ################################################################################################################################

/// Open option that addresses a queue at a specific queue manager.
///
/// The crate's own `QueueManagerName` option cannot be used for this - it sets the
/// object type to `MQOT_Q_MGR`, which MQPUT1 rejects when the target is a queue.
/// This option only fills in `ObjectQMgrName`, leaving the object type as a queue.
struct ReplyToQueueManager(QueueManagerName);

// Implementing the option trait is unsafe because it manipulates the MQOD structure directly.
#[expect(unsafe_code, reason = "the open option trait is unsafe by design, only ObjectQMgrName is set here")]
unsafe impl<T> mqi::open::OpenOption<'_, T> for ReplyToQueueManager {
    fn apply_param(&self, param: &mut mqi::open::OpenParamOption<'_, T>) {
        param.mqod.ObjectQMgrName = self.0.0.into();
    }
}

// ################################################################################################################################

/// Sends a reply to the ReplyToQ and ReplyToQMgr of a previously received message.
///
/// The reply's correlation ID is set to the original message ID so the requester
/// can match the reply, and the message type is MQMT_REPLY.
pub fn send_reply(
    config: &ChannelConfig,
    reply_to_queue: &str,
    reply_to_queue_manager: &str,
    message_id: &str,
    payload: &[u8],
) -> Result<(), String> {
    let details = config.mq_details();
    let connection = connect(&details)?;

    let queue_name =
        QueueName::from_str(reply_to_queue).map_err(|err| format!("Invalid reply queue `{reply_to_queue}`: {err}"))?;

    // An empty reply queue manager means the reply goes to the local queue manager.
    let queue_manager = if reply_to_queue_manager.is_empty() {
        None
    } else {
        let name = QueueManagerName::from_str(reply_to_queue_manager)
            .map_err(|err| format!("Invalid reply queue manager `{reply_to_queue_manager}`: {err}"))?;
        Some(ReplyToQueueManager(name))
    };

    let identifier = hex_to_identifier(message_id)?;
    let correlation_id = types::CorrelationId(identifier);
    let message_type: MQMT = constants::MQMT_REPLY;

    let put_options = constants::MQPMO_NO_SYNCPOINT | constants::MQPMO_FAIL_IF_QUIESCING;
    let format = text_message_format();

    connection
        .put_message(
            &(queue_manager, queue_name, put_options),
            &(correlation_id, message_type),
            &(payload, format),
        )
        .warn_as_error()
        .map_err(|err| format!("IBM MQ reply to `{reply_to_queue}` failed: {err}"))?;

    let _ = connection.disconnect();

    Ok(())
}

// ################################################################################################################################

/// Pings an outgoing IBM MQ connection by connecting and opening its queue for inquiry.
pub fn ping(config: &OutgoingConfig) -> Result<(), String> {
    let details = config.mq_details();
    let connection = connect(&details)?;

    let queue_name =
        QueueName::from_str(&config.queue).map_err(|err| format!("Invalid queue name `{}`: {err}", config.queue))?;

    let open_options = constants::MQOO_INQUIRE | constants::MQOO_FAIL_IF_QUIESCING;
    let object = Object::open(&connection, &(queue_name, open_options))
        .warn_as_error()
        .map_err(|err| format!("Cannot open queue `{}` for inquiry: {err}", config.queue))?;

    let _ = object.close();
    let _ = connection.disconnect();

    Ok(())
}
