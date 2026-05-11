// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Prometheus metrics for the Zato scheduler process.

use std::sync::LazyLock;

use prometheus::{Encoder, GaugeVec, HistogramOpts, HistogramVec, IntCounter, IntCounterVec, IntGauge, Opts, Registry, TextEncoder};

/// Duration histogram buckets matching the Python server's `zato_histogram_buckets`.
const ZATO_HISTOGRAM_BUCKETS: &[f64] = &[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0];

/// Dedicated registry so we never expose default process metrics.
static REGISTRY: LazyLock<Registry> = LazyLock::new(Registry::new);

// ############################################################################
// Gauges
// ############################################################################

/// Total number of jobs known to the scheduler (active + paused).
pub static JOBS_TOTAL: LazyLock<IntGauge> = LazyLock::new(|| {
    let gauge = IntGauge::new("zato_scheduler_jobs_total", "Total number of jobs known to the scheduler").unwrap();
    REGISTRY.register(Box::new(gauge.clone())).unwrap();
    gauge
});

/// Number of active (enabled) jobs.
pub static JOBS_ACTIVE: LazyLock<IntGauge> = LazyLock::new(|| {
    let gauge = IntGauge::new("zato_scheduler_jobs_active", "Number of active (enabled) scheduler jobs").unwrap();
    REGISTRY.register(Box::new(gauge.clone())).unwrap();
    gauge
});

/// Number of jobs currently in flight (dispatched, awaiting completion).
pub static JOBS_IN_FLIGHT: LazyLock<IntGauge> = LazyLock::new(|| {
    let gauge = IntGauge::new("zato_scheduler_jobs_in_flight", "Number of jobs currently in flight").unwrap();
    REGISTRY.register(Box::new(gauge.clone())).unwrap();
    gauge
});

// ############################################################################
// Counters
// ############################################################################

/// Total scheduler ticks (iterations of the main loop).
pub static TICKS_TOTAL: LazyLock<IntCounter> = LazyLock::new(|| {
    let counter = IntCounter::new("zato_scheduler_ticks_total", "Total iterations of the scheduler main loop").unwrap();
    REGISTRY.register(Box::new(counter.clone())).unwrap();
    counter
});

/// Total clock-jump events detected.
pub static CLOCK_JUMPS_TOTAL: LazyLock<IntCounter> = LazyLock::new(|| {
    let counter = IntCounter::new("zato_scheduler_clock_jumps_total", "Total wall-clock jump events detected").unwrap();
    REGISTRY.register(Box::new(counter.clone())).unwrap();
    counter
});

/// Total job executions, labelled by `job_name` and `outcome`.
pub static EXECUTIONS_TOTAL: LazyLock<IntCounterVec> = LazyLock::new(|| {
    let counter = IntCounterVec::new(
        Opts::new(
            "zato_scheduler_executions_total",
            "Total scheduler job executions, by job name and outcome",
        ),
        &["job_name", "outcome"],
    )
    .unwrap();
    REGISTRY.register(Box::new(counter.clone())).unwrap();
    counter
});

// ############################################################################
// Histograms
// ############################################################################

/// Execution duration histogram, labelled by `job_name`.
pub static EXECUTION_DURATION_SECONDS: LazyLock<HistogramVec> = LazyLock::new(|| {
    let hist = HistogramVec::new(
        HistogramOpts::new(
            "zato_scheduler_execution_duration_seconds",
            "Duration of scheduler job executions in seconds",
        )
        .buckets(ZATO_HISTOGRAM_BUCKETS.to_vec()),
        &["job_name"],
    )
    .unwrap();
    REGISTRY.register(Box::new(hist.clone())).unwrap();
    hist
});

// ############################################################################
// Uptime gauge
// ############################################################################

/// Scheduler uptime in seconds (set by the binary's main loop).
pub static UPTIME_SECONDS: LazyLock<GaugeVec> = LazyLock::new(|| {
    let gauge = GaugeVec::new(
        Opts::new(
            "zato_scheduler_uptime_seconds",
            "Time in seconds since the scheduler process started",
        ),
        &[],
    )
    .unwrap();
    REGISTRY.register(Box::new(gauge.clone())).unwrap();
    gauge
});

// ############################################################################
// Text encoding
// ############################################################################

/// Encodes all registered metrics into Prometheus text exposition format.
pub fn encode_metrics() -> String {
    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();
    let mut buffer = Vec::new();
    encoder.encode(&metric_families, &mut buffer).unwrap();
    String::from_utf8(buffer).unwrap()
}

/// Returns the shared histogram buckets for tests.
#[cfg(test)]
pub fn histogram_buckets() -> &'static [f64] {
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
