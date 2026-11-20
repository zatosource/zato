//! The active-standby node of a Zato server on a `PostgreSQL` Zato database.
//!
//! The `_zato_ha_node` binary runs the Zato server only while its node is active, renews the lease of the active node
//! on a referee, takes over once the lease of the other node lapses, and moves the active role between two nodes
//! through compare-and-set writes to the referee.

pub mod config;
pub mod control;
pub mod generation;
pub mod kubernetes;
pub mod postgresql;
pub mod record;
pub mod referee;
pub mod role_endpoint;
pub mod server_health;
pub mod state;
pub mod supervisor;
#[cfg(test)]
pub mod test_support;
pub mod wire;
