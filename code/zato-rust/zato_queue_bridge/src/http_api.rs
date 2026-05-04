//! HTTP query API served by actix-web for the Zato server to read queue bridge state.
//!
//! All endpoints are GET-only, served on 127.0.0.1:35111, no authentication.

use std::sync::Arc;

use actix_web::{App, HttpResponse, HttpServer, web};
use serde::{Deserialize, Serialize};

use crate::bridge::BridgeShared;

/// Shared application state passed to all actix-web handlers.
struct AppState {
    /// Reference to the queue bridge's shared state.
    shared: Arc<BridgeShared>,
}

/// Starts the actix-web HTTP server on 127.0.0.1:35111.
///
/// This function blocks until the server shuts down.
pub async fn start_http_server(shared: Arc<BridgeShared>) -> std::io::Result<()> {
    let state = web::Data::new(AppState { shared });

    tracing::info!("Starting HTTP query API on 127.0.0.1:35111");

    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .route("/api/get_connections", web::get().to(get_connections))
            .route("/api/get_connection_status", web::get().to(get_connection_status))
    })
    .bind("127.0.0.1:35111")?
    .run()
    .await
}

/// Response structure for a single connection summary.
#[derive(Serialize)]
struct ConnectionInfo {
    /// Connection name as registered in Zato.
    name: String,
    /// Whether this is a channel (consumer) or outgoing (producer) connection.
    conn_type: String,
    /// Broker address.
    address: String,
    /// Topic name.
    topic: String,
    /// Whether SSL/TLS is enabled.
    ssl: bool,
}

/// Returns a list of all registered channel and outgoing connections.
async fn get_connections(state: web::Data<AppState>) -> HttpResponse {
    let connections: Vec<ConnectionInfo> = {
        let bridge_state = state.shared.state.lock();
        let mut result = Vec::with_capacity(bridge_state.channels.len() + bridge_state.outgoing.len());
        for config in bridge_state.channels.values() {
            result.push(ConnectionInfo {
                name: config.name.clone(),
                conn_type: "channel".into(),
                address: config.address.clone(),
                topic: config.topic.clone(),
                ssl: config.ssl,
            });
        }
        for config in bridge_state.outgoing.values() {
            result.push(ConnectionInfo {
                name: config.name.clone(),
                conn_type: "outgoing".into(),
                address: config.address.clone(),
                topic: config.topic.clone(),
                ssl: config.ssl,
            });
        }
        result
    };

    HttpResponse::Ok().json(connections)
}

/// Query parameters for get_connection_status.
#[derive(Deserialize)]
struct ConnectionStatusParams {
    /// Connection name to query.
    name: String,
}

/// Response structure for a single connection's detailed status.
#[derive(Serialize)]
struct ConnectionStatus {
    /// Whether the connection was found.
    found: bool,
    /// Connection name.
    name: String,
    /// Connection type (channel or outgoing).
    conn_type: String,
    /// Broker address.
    address: String,
    /// Topic name.
    topic: String,
    /// Whether SSL/TLS is enabled.
    ssl: bool,
    /// Consumer group (channels only).
    group_id: Option<String>,
    /// Zato service name (channels only).
    service: Option<String>,
}

/// Returns detailed status for a single connection by name.
async fn get_connection_status(state: web::Data<AppState>, params: web::Query<ConnectionStatusParams>) -> HttpResponse {
    let bridge_state = state.shared.state.lock();

    if let Some(config) = bridge_state.channels.get(&params.name) {
        return HttpResponse::Ok().json(ConnectionStatus {
            found: true,
            name: config.name.clone(),
            conn_type: "channel".into(),
            address: config.address.clone(),
            topic: config.topic.clone(),
            ssl: config.ssl,
            group_id: Some(config.group_id.clone()),
            service: Some(config.service.clone()),
        });
    }

    if let Some(config) = bridge_state.outgoing.get(&params.name) {
        return HttpResponse::Ok().json(ConnectionStatus {
            found: true,
            name: config.name.clone(),
            conn_type: "outgoing".into(),
            address: config.address.clone(),
            topic: config.topic.clone(),
            ssl: config.ssl,
            group_id: None,
            service: None,
        });
    }

    drop(bridge_state);

    HttpResponse::Ok().json(ConnectionStatus {
        found: false,
        name: params.name.clone(),
        conn_type: String::new(),
        address: String::new(),
        topic: String::new(),
        ssl: false,
        group_id: None,
        service: None,
    })
}
