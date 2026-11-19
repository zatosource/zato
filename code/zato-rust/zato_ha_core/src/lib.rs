//! Active-standby replication of the `SQLite` Zato database.
//!
//! The `_zato_ha_node` binary reads the write-ahead log of the Zato database of a Zato server, ships its
//! frames to a standby node, answers the replication barrier of the server, and moves the active role
//! between two nodes through compare-and-set writes to a referee.

pub mod active;
pub mod barrier;
pub mod clock;
pub mod config;
pub mod control;
pub mod copy;
pub mod generation;
pub mod kubernetes;
pub mod link;
pub mod postgresql;
pub mod protocol;
pub mod record;
pub mod referee;
pub mod role_endpoint;
pub mod standby;
pub mod state;
pub mod supervisor;
#[cfg(test)]
pub mod test_support;
pub mod wal;
pub mod wire;
