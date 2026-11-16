// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! A Redis connection of the standalone scheduler binary that survives a restart of Redis.
//!
//! The command listener and the fire publisher each hold one connection for the lifetime of the process.
//! A connection that Redis closed is replaced by a new one at the next command, so the scheduler
//! reads commands and publishes fire events again as soon as Redis accepts connections.

use std::time::Duration;

use redis::{Client, Cmd, Connection, ConnectionLike, FromRedisValue, RedisResult, Value};

/// How long a link waits before it sends a command again to a Redis that it could not reach.
const UNREACHABLE_RETRY_INTERVAL: Duration = Duration::from_secs(1);

/// A Redis connection that is opened again after Redis closed it.
pub struct RedisLink {

    /// The client that opens each connection, with the address and the credentials of Redis.
    client: Client,

    /// The connection in use, absent from the moment Redis closed it until the next command opens a new one.
    connection: Option<Connection>,
}

impl RedisLink {

    /// Opens the first connection of a link to the Redis of a client.
    ///
    /// # Errors
    ///
    /// Returns the error of the connection attempt when Redis does not accept the connection.
    pub fn open(client: Client) -> RedisResult<Self> {
        let connection = client.get_connection()?;
        Ok(Self {
            client,
            connection: Some(connection),
        })
    }

    /// Returns the connection in use, opening a new one if Redis closed the previous one.
    fn get_connection(&mut self) -> RedisResult<&mut Connection> {
        let connection = if let Some(connection) = self.connection.take() {
            connection
        } else {
            // A link whose connection was lost opens a new one, and an attempt that fails leaves it to the next command
            let connection = self.client.get_connection()?;
            tracing::info!("Reconnected to Redis");
            connection
        };

        Ok(self.connection.insert(connection))
    }

    /// Runs a command until Redis is reachable and returns its result, so that an event is not lost during an outage.
    ///
    /// # Errors
    ///
    /// Returns the error of a command that Redis received and rejected.
    pub fn query_until_reachable<T: FromRedisValue>(&mut self, command: &Cmd) -> RedisResult<T> {
        let mut is_unreachable = false;

        loop {
            let result: RedisResult<T> = command.query(self);

            // Only an error of the connection is retried, a rejection by Redis would recur on every attempt
            let Err(err) = &result else {
                if is_unreachable {
                    tracing::info!("Command sent after Redis became reachable again");
                }
                return result;
            };
            if !err.is_io_error() {
                return result;
            }

            // An outage is reported once, not on each attempt
            if !is_unreachable {
                tracing::warn!("Redis is unreachable, the command is retried every {UNREACHABLE_RETRY_INTERVAL:?}: {err}");
                is_unreachable = true;
            }
            std::thread::sleep(UNREACHABLE_RETRY_INTERVAL);
        }
    }

    /// Releases the connection after an error that leaves it unusable, so that the next command opens another one.
    fn check_result<T>(&mut self, result: RedisResult<T>) -> RedisResult<T> {
        if let Err(err) = &result {
            // An error that a new connection resolves, such as a connection that Redis closed, releases this one
            if err.is_unrecoverable_error() {
                tracing::warn!("Lost the connection to Redis: {err}");
                self.connection = None;
            }
        }
        result
    }
}

impl ConnectionLike for RedisLink {

    fn req_packed_command(&mut self, cmd: &[u8]) -> RedisResult<Value> {
        let result = self.get_connection()?.req_packed_command(cmd);
        self.check_result(result)
    }

    fn req_packed_commands(&mut self, cmd: &[u8], offset: usize, count: usize) -> RedisResult<Vec<Value>> {
        let result = self.get_connection()?.req_packed_commands(cmd, offset, count);
        self.check_result(result)
    }

    fn get_db(&self) -> i64 {
        self.client.get_connection_info().redis_settings().db()
    }

    fn check_connection(&mut self) -> bool {
        // A link that cannot open a connection is not usable
        self.get_connection().is_ok_and(ConnectionLike::check_connection)
    }

    fn is_open(&self) -> bool {
        self.connection.as_ref().is_some_and(ConnectionLike::is_open)
    }
}
