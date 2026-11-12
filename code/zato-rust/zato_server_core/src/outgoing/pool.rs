//! The pool of connections a transport keeps open between requests, per endpoint.
//!
//! A request takes the most recently returned connection, the way urllib3's pool hands them out,
//! and a connection that is returned while the pool already holds as many as its size is closed.

use std::collections::HashMap;

use parking_lot::Mutex;

use super::stream::Stream;

/// The endpoint a pooled connection is open to.
#[derive(Clone, Hash, PartialEq, Eq)]
pub struct OriginKey {
    /// Whether the connection uses TLS.
    pub is_tls: bool,

    /// The host name or IP address.
    pub host: String,

    /// The port.
    pub port: u16,
}

/// The idle connections of a transport, per endpoint.
pub struct Pool {
    /// The idle connections, the most recently returned one last.
    idle: Mutex<HashMap<OriginKey, Vec<Stream>>>,

    /// How many idle connections are kept per endpoint.
    size: usize,
}

impl Pool {
    /// Creates an empty pool that keeps up to the given number of idle connections per endpoint.
    pub fn new(size: usize) -> Self {
        Self {
            idle: Mutex::new(HashMap::new()),
            size,
        }
    }

    /// Takes an idle connection to the endpoint that can serve another request, closing any that cannot.
    pub fn checkout(&self, key: &OriginKey) -> Option<Stream> {
        loop {
            // The lock is held only to take the connection out, never while it is checked
            let mut stream = {
                let mut idle = self.idle.lock();
                idle.get_mut(key)?.pop()?
            };

            if stream.is_reusable() {
                return Some(stream);
            }
        }
    }

    /// Returns a connection to the pool, or closes it if the pool already keeps as many as its size.
    pub fn checkin(&self, key: OriginKey, stream: Stream) {
        let mut idle = self.idle.lock();
        let streams = idle.entry(key).or_default();

        if streams.len() < self.size {
            streams.push(stream);
        }

        // A connection beyond the pool size is closed when the function returns, after the lock is released
        drop(idle);
    }

    /// Closes all the idle connections.
    pub fn clear(&self) {
        // The guard is released at the end of the statement, and the connections are closed when the function returns
        let _drained = std::mem::take(&mut *self.idle.lock());
    }
}
