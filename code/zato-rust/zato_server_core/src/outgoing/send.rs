//! One request sent on a pooled connection or a new one, shared by the transport and the push engine.

use std::sync::Arc;

use rustls::ClientConfig;

use super::error::TransportError;
use super::exchange::{OutgoingRequest, Peer, RawResponse, connect, exchange};
use super::pool::{OriginKey, Pool};
use super::scope::{NetworkScope, classify};
use super::stream::{IoContext, Stream};

/// A response and the network scope of the address of the connection it arrived on.
pub struct ScopedResponse {

    /// The response.
    pub response: RawResponse,

    /// The scope of the address of the endpoint, or `None` if the address has no scope.
    pub peer_scope: Option<NetworkScope>,
}

/// What a request is sent to and through.
pub struct PooledSend<'call> {

    /// The endpoint, as the messages of the errors describe it, with the scope the call requires, if any.
    pub peer: &'call Peer<'call>,

    /// The key of the idle connections to the endpoint in the pool.
    pub key: OriginKey,

    /// The TLS configuration, if the request uses TLS.
    pub tls_config: Option<&'call Arc<ClientConfig>>,

    /// The request as written to the connection.
    pub request: &'call OutgoingRequest<'call>,
}

/// Sends the request on a pooled connection or a new one and reads its response, repeating it once
/// on a new connection if a pooled connection turns out to have been closed by the endpoint.
pub fn send_pooled(ctx: &IoContext<'_, '_>, pool: &Pool, send: PooledSend<'_>) -> Result<ScopedResponse, TransportError> {
    let PooledSend {
        peer,
        key,
        tls_config,
        request,
    } = send;

    let (mut stream, mut is_reused) = match checkout_within(pool, &key, peer.required_scope) {
        Some(stream) => (stream, true),
        None => (connect(ctx, peer, tls_config)?, false),
    };

    loop {
        // The scope is read before the exchange, while the connection certainly still has its peer
        let peer_scope = stream_scope(&stream);

        match exchange(ctx, peer, &mut stream, request) {
            Ok(response) => {
                // A connection is kept only if the endpoint keeps it open and nothing else is left on it
                if response.is_keep_alive {
                    pool.checkin(key, stream);
                }
                return Ok(ScopedResponse { response, peer_scope });
            }

            // An idle connection the endpoint closed in the meantime fails before any byte of the response,
            // and the request is sent again on a new connection, once
            Err(failure) if is_reused && failure.is_before_response => {
                stream = connect(ctx, peer, tls_config)?;
                is_reused = false;
            }

            Err(failure) => return Err(failure.error),
        }
    }
}

/// Takes an idle connection to the endpoint, provided that the address it is established to has
/// the required scope if the call requires one.
fn checkout_within(pool: &Pool, key: &OriginKey, required_scope: Option<NetworkScope>) -> Option<Stream> {
    let stream = pool.checkout(key)?;

    let Some(required) = required_scope else {
        return Some(stream);
    };

    if stream_scope(&stream) == Some(required) {
        return Some(stream);
    }

    // A connection to an address of another scope stays in the pool for the calls that do not require this one
    pool.checkin(key.clone(), stream);
    None
}

/// The network scope of the address a connection is established to, or `None` if the address has no scope
/// or the connection no longer has a peer.
fn stream_scope(stream: &Stream) -> Option<NetworkScope> {
    let address = stream.peer_address().ok()?;
    classify(address.ip())
}
