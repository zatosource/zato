// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Prometheus metrics for the Zato scheduler process.

use std::sync::LazyLock;

use prometheus::core::Collector;
use prometheus::{Encoder, GaugeVec, HistogramOpts, HistogramVec, IntCounter, IntCounterVec, IntGauge, Opts, Registry, TextEncoder};

/// Duration histogram buckets matching the Python server's `zato_histogram_buckets`.
const ZATO_HISTOGRAM_BUCKETS: &[f64] = &[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0];

/// Dedicated registry so we never expose default process metrics.
static REGISTRY: LazyLock<Registry> = LazyLock::new(Registry::new);

/// Adds a freshly built metric to the scheduler's registry and hands it back.
///
/// Every metric in this module is built from a name and a help string that are literals
/// written a few lines above the call, so the only ways this can fail are a malformed name
/// or the same metric being registered twice. Both are mistakes in this file rather than
/// conditions a running scheduler can encounter or recover from, which is why the error is
/// turned into a panic here instead of being propagated to every metric access.
///
/// # Panics
///
/// Panics when the metric cannot be built or is already registered.
#[expect(clippy::expect_used, reason = "an invalid or duplicate metric name is a bug in this file")]
fn register<M: Collector + Clone + 'static>(built: prometheus::Result<M>) -> M {
    let metric = built.expect("Scheduler metric could not be built");
    REGISTRY
        .register(Box::new(metric.clone()))
        .expect("Scheduler metric could not be registered");
    metric
}

// ############################################################################
// Gauges
// ############################################################################

/// Total number of jobs known to the scheduler (active + paused).
pub static JOBS_TOTAL: LazyLock<IntGauge> = LazyLock::new(|| {
    register(IntGauge::new(
        "zato_scheduler_jobs_total",
        "Total number of jobs known to the scheduler",
    ))
});

/// Number of active (enabled) jobs.
pub static JOBS_ACTIVE: LazyLock<IntGauge> = LazyLock::new(|| {
    register(IntGauge::new(
        "zato_scheduler_jobs_active",
        "Number of active (enabled) scheduler jobs",
    ))
});

/// Number of jobs currently in flight (dispatched, awaiting completion).
pub static JOBS_IN_FLIGHT: LazyLock<IntGauge> =
    LazyLock::new(|| register(IntGauge::new("zato_scheduler_jobs_in_flight", "Number of jobs currently in flight")));

// ############################################################################
// Counters
// ############################################################################

/// Total scheduler ticks (iterations of the main loop).
pub static TICKS_TOTAL: LazyLock<IntCounter> = LazyLock::new(|| {
    register(IntCounter::new(
        "zato_scheduler_ticks_total",
        "Total iterations of the scheduler main loop",
    ))
});

/// Total clock-jump events detected.
pub static CLOCK_JUMPS_TOTAL: LazyLock<IntCounter> = LazyLock::new(|| {
    register(IntCounter::new(
        "zato_scheduler_clock_jumps_total",
        "Total wall-clock jump events detected",
    ))
});

/// Total job executions, labelled by `job_name` and `outcome`.
pub static EXECUTIONS_TOTAL: LazyLock<IntCounterVec> = LazyLock::new(|| {
    register(IntCounterVec::new(
        Opts::new(
            "zato_scheduler_executions_total",
            "Total scheduler job executions, by job name and outcome",
        ),
        &["job_name", "outcome"],
    ))
});

// ############################################################################
// Histograms
// ############################################################################

/// Execution duration histogram, labelled by `job_name`.
pub static EXECUTION_DURATION_SECONDS: LazyLock<HistogramVec> = LazyLock::new(|| {
    register(HistogramVec::new(
        HistogramOpts::new(
            "zato_scheduler_execution_duration_seconds",
            "Duration of scheduler job executions in seconds",
        )
        .buckets(ZATO_HISTOGRAM_BUCKETS.to_vec()),
        &["job_name"],
    ))
});

// ############################################################################
// Uptime gauge
// ############################################################################

/// Scheduler uptime in seconds (set by the binary's main loop).
pub static UPTIME_SECONDS: LazyLock<GaugeVec> = LazyLock::new(|| {
    register(GaugeVec::new(
        Opts::new(
            "zato_scheduler_uptime_seconds",
            "Time in seconds since the scheduler process started",
        ),
        &[],
    ))
});

// ############################################################################
// Text encoding
// ############################################################################

/// Encodes all registered metrics into Prometheus text exposition format.
///
/// An encoding failure yields an empty body rather than an error, because the caller is a
/// scrape endpoint for which a missing sample is a far better outcome than a failed request.
pub fn encode_metrics() -> String {
    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();
    let mut buffer = Vec::new();

    if let Err(err) = encoder.encode(&metric_families, &mut buffer) {
        tracing::error!("Could not encode scheduler metrics: {err}");
        return String::new();
    }

    // The text encoder emits ASCII only, so the conversion below cannot lose anything.
    String::from_utf8_lossy(&buffer).into_owned()
}

/// Returns the shared histogram buckets for tests.
#[cfg(test)]
pub const fn histogram_buckets() -> &'static [f64] {
    ZATO_HISTOGRAM_BUCKETS
}

// ############################################################################
// Unit tests
// ############################################################################

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_jobs_total_starts_at_zero() {
        assert_eq!(JOBS_TOTAL.get(), 0);
    }

    #[test]
    fn test_jobs_active_starts_at_zero() {
        assert_eq!(JOBS_ACTIVE.get(), 0);
    }

    #[test]
    fn test_jobs_in_flight_starts_at_zero() {
        assert_eq!(JOBS_IN_FLIGHT.get(), 0);
    }

    #[test]
    fn test_ticks_total_is_counter() {
        let before = TICKS_TOTAL.get();
        TICKS_TOTAL.inc();
        assert_eq!(TICKS_TOTAL.get(), before + 1);
    }

    #[test]
    fn test_clock_jumps_total_is_counter() {
        let before = CLOCK_JUMPS_TOTAL.get();
        CLOCK_JUMPS_TOTAL.inc();
        assert_eq!(CLOCK_JUMPS_TOTAL.get(), before + 1);
    }

    #[test]
    fn test_executions_total_can_inc() {
        EXECUTIONS_TOTAL.with_label_values(&["test_job", "ok"]).inc();
        let val = EXECUTIONS_TOTAL.with_label_values(&["test_job", "ok"]).get();
        assert!(val >= 1);
    }

    #[test]
    fn test_execution_duration_can_observe() {
        EXECUTION_DURATION_SECONDS.with_label_values(&["test_job_dur"]).observe(0.123);
        let count = EXECUTION_DURATION_SECONDS.with_label_values(&["test_job_dur"]).get_sample_count();
        assert!(count >= 1);
    }

    #[test]
    fn test_histogram_buckets_match_python() {
        let expected = &[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0];
        assert_eq!(histogram_buckets(), expected);
    }

    #[test]
    fn test_encode_metrics_contains_scheduler_prefix() {
        TICKS_TOTAL.inc();
        let text = encode_metrics();
        assert!(text.contains("zato_scheduler_ticks_total"));
    }
}
