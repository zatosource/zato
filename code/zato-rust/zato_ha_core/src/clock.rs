// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The wall clocks of the two nodes, from which the Zato server on `SQLite` takes the time of its database.
//!
//! The active node sends its wall time in its hello and in every heartbeat, and the standby estimates from them
//! how far its own wall clock is from that of the active node. A standby whose skew exceeds the bound of the
//! configuration is not admitted in sync, and one in sync is marked out, so that a takeover does not move
//! the time of the database by more than that bound.

use std::collections::VecDeque;
use std::time::{SystemTime, UNIX_EPOCH};

/// How many of the most recent wall times of the active node the skew is estimated from.
const SKEW_SAMPLES: usize = 8;

/// Returns the wall time of this host in milliseconds since the Unix epoch.
pub fn wall_ms() -> u64 {
    // A wall clock set before the epoch reads as the epoch itself.
    let since_epoch = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default();
    u64::try_from(since_epoch.as_millis()).unwrap_or(u64::MAX)
}

/// The skew of the wall clock of the standby from that of the active node, estimated on the standby.
#[derive(Debug, Default)]
pub struct SkewEstimate {
    /// The differences between the wall time of the standby when a message arrived and the wall time
    /// of the active node that the message carried, in milliseconds, the most recent last.
    samples: VecDeque<i128>,

    /// The estimate as of the most recent sample, in milliseconds.
    estimate_ms: u64,

    /// Whether the estimate exceeded the bound when it was last recorded.
    exceeds_bound: bool,
}

impl SkewEstimate {
    /// Records the wall time that the active node sent and returns the estimated skew in milliseconds.
    ///
    /// Each message arrives after it was sent, including the time it waited behind the frames sent before it,
    /// so each difference exceeds the skew by that delay, and the smallest of the recent differences is closest to it.
    /// A change of the estimate across `bound_ms` is logged.
    pub fn record(&mut self, sent_wall_ms: u64, bound_ms: u64) -> u64 {
        let received = i128::from(wall_ms());
        let sent = i128::from(sent_wall_ms);
        let difference = received - sent;

        // Only the most recent samples count, so that the estimate follows a clock that was changed.
        if self.samples.len() == SKEW_SAMPLES {
            let _ = self.samples.pop_front();
        }
        self.samples.push_back(difference);

        let smallest = self.samples.iter().copied().fold(difference, i128::min);
        let out = u64::try_from(smallest.unsigned_abs()).unwrap_or(u64::MAX);

        let exceeds_bound = out > bound_ms;
        if exceeds_bound && !self.exceeds_bound {
            tracing::warn!("The wall clock of this node is {out} ms away from that of the active node, above the bound of {bound_ms} ms");
        } else if !exceeds_bound && self.exceeds_bound {
            tracing::info!("The wall clock of this node is {out} ms away from that of the active node, within the bound of {bound_ms} ms");
        }
        self.exceeds_bound = exceeds_bound;
        self.estimate_ms = out;
        out
    }

    /// Returns the estimate as of the most recent sample, in milliseconds.
    pub const fn current(&self) -> u64 {
        self.estimate_ms
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The bound of the skew that the tests record against.
    const BOUND_MS: u64 = 1000;

    /// A skew well beyond the bound.
    const LARGE_SKEW_MS: u64 = 5000;

    /// A delay of one message behind the frames sent before it.
    const QUEUED_DELAY_MS: u64 = 3000;

    #[test]
    fn a_clock_ahead_of_the_active_node_is_estimated_from_its_wall_time() {
        let mut estimate = SkewEstimate::default();
        let sent = wall_ms() - LARGE_SKEW_MS;
        let skew = estimate.record(sent, BOUND_MS);
        assert!(skew >= LARGE_SKEW_MS, "{skew}");
    }

    #[test]
    fn a_clock_behind_the_active_node_is_estimated_from_its_wall_time() {
        let mut estimate = SkewEstimate::default();
        let sent = wall_ms() + LARGE_SKEW_MS;
        let skew = estimate.record(sent, BOUND_MS);
        assert!(skew > BOUND_MS, "{skew}");
    }

    #[test]
    fn a_message_delayed_behind_frames_does_not_raise_the_estimate() {
        let mut estimate = SkewEstimate::default();
        let _ = estimate.record(wall_ms(), BOUND_MS);
        let skew = estimate.record(wall_ms() - QUEUED_DELAY_MS, BOUND_MS);
        assert!(skew < BOUND_MS, "{skew}");
    }

    #[test]
    fn a_skew_older_than_the_recent_samples_no_longer_counts() {
        let mut estimate = SkewEstimate::default();
        let _ = estimate.record(wall_ms() + LARGE_SKEW_MS, BOUND_MS);
        for _ in 0..SKEW_SAMPLES {
            let _ = estimate.record(wall_ms(), BOUND_MS);
        }
        let skew = estimate.record(wall_ms(), BOUND_MS);
        assert!(skew < BOUND_MS, "{skew}");
    }
}
