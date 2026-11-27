//! The log of an outage of a resource that a component of the bridge retries until it is available again.
//!
//! The resource is e.g. Redis, a Kafka broker or an IBM MQ queue manager. The first failure of an outage is logged
//! as a warning, the failures that follow it as debug entries, and the end of the outage with its duration.

use std::fmt::Display;
use std::time::Instant;

/// The run of failures of one component, from its first failure to its next success.
pub struct OutageLog {
    /// What the log entries name, e.g. the Kafka consumer of a channel.
    component: String,

    /// When the current run of failures began, or `None` while the component succeeds.
    failed_at: Option<Instant>,
}

impl OutageLog {
    /// Creates the log of a component that has not failed yet.
    #[must_use]
    pub const fn new(component: String) -> Self {
        Self {
            component,
            failed_at: None,
        }
    }

    /// Records an operation that failed, the first failure of a run marking the beginning of the outage.
    pub fn on_failure(&mut self, error: &dyn Display) {
        // A failure within a run that is logged already adds nothing that an operator acts on.
        if self.failed_at.is_some() {
            tracing::debug!("{} failed again: {error}", self.component);
        } else {
            self.failed_at = Some(Instant::now());
            tracing::warn!("{} failed, retrying until it completes: {error}", self.component);
        }
    }

    /// Records an operation that succeeded, logging how long the component took to resume if it was failing.
    pub fn on_success(&mut self) {
        // Only the end of a run of failures is logged, a success that follows another one is not.
        if let Some(failed_at) = self.failed_at.take() {
            let elapsed = failed_at.elapsed();
            tracing::info!("{} resumed after {elapsed:?}", self.component);
        }
    }
}
