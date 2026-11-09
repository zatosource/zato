//! Active-standby replication of the `SQLite` databases of Zato.
//!
//! The `_zato_ha_node` binary reads the write-ahead logs of the databases of a Zato server, ships their
//! frames to a standby node, answers the replication barrier of the server, and moves the active role
//! between two nodes through compare-and-set writes to a referee.

pub mod active;
pub mod barrier;
pub mod config;
pub mod consul;
pub mod control;
pub mod copy;
pub mod generation;
pub mod kubernetes;
pub mod link;
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
