// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

use std::time::{Duration, Instant};

use super::{ServerFailure, ServerHealth, Verdict};
use crate::config::ServerHealthConfig;

/// The liveness timeout of the tests.
const LIVENESS_TIMEOUT: Duration = Duration::from_secs(10);

/// The start timeout of the tests.
const START_TIMEOUT: Duration = Duration::from_mins(5);

/// The exit limit of the tests.
const EXIT_LIMIT: u32 = 3;

/// The exit window of the tests.
const EXIT_WINDOW: Duration = Duration::from_mins(1);

/// A moment just short of a threshold.
const JUST_SHORT: Duration = Duration::from_millis(1);

/// Returns a policy with the thresholds of the tests.
fn health() -> ServerHealth {
    let config = ServerHealthConfig {
        liveness_timeout: LIVENESS_TIMEOUT,
        start_timeout: START_TIMEOUT,
        exit_limit: EXIT_LIMIT,
        exit_window: EXIT_WINDOW,
        ..ServerHealthConfig::from_defaults()
    };
    ServerHealth::new(config)
}

#[test]
fn a_server_that_never_ran_is_healthy() {
    let mut health = health();
    assert_eq!(health.verdict(Instant::now()), Verdict::Healthy);
}

#[test]
fn a_server_that_stops_answering_fails_at_the_liveness_timeout() {
    let mut health = health();
    let started_at = Instant::now();
    health.on_start(started_at);
    health.on_answer(started_at);

    let answered_at = started_at + Duration::from_secs(5);
    health.on_answer(answered_at);

    // The measure begins at the last answer, not at the first one ..
    let before = answered_at + LIVENESS_TIMEOUT.saturating_sub(JUST_SHORT);
    assert_eq!(health.verdict(before), Verdict::Healthy);

    // .. and the threshold itself is a failure.
    let at_threshold = answered_at + LIVENESS_TIMEOUT;
    assert_eq!(health.verdict(at_threshold), Verdict::Failed(ServerFailure::Unanswered));
}

#[test]
fn an_answer_ends_a_run_of_unanswered_pings() {
    let mut health = health();
    let started_at = Instant::now();
    health.on_start(started_at);
    health.on_answer(started_at);

    // The pings go unanswered for almost the whole liveness timeout, and one answer then starts the measure again ..
    let answered_at = started_at + LIVENESS_TIMEOUT.saturating_sub(JUST_SHORT);
    health.on_answer(answered_at);

    // .. so the server is healthy where the first silence alone would have failed it.
    let past_first_silence = started_at + LIVENESS_TIMEOUT + LIVENESS_TIMEOUT / 2;
    assert_eq!(health.verdict(past_first_silence), Verdict::Healthy);
}

#[test]
fn a_server_that_never_answers_fails_at_the_start_timeout() {
    let mut health = health();
    let started_at = Instant::now();
    health.on_start(started_at);

    // A start is measured by the start timeout, not by the shorter liveness timeout ..
    let past_liveness = started_at + LIVENESS_TIMEOUT;
    assert_eq!(health.verdict(past_liveness), Verdict::Healthy);
    let before = started_at + START_TIMEOUT.saturating_sub(JUST_SHORT);
    assert_eq!(health.verdict(before), Verdict::Healthy);

    // .. up to the threshold itself.
    let at_threshold = started_at + START_TIMEOUT;
    assert_eq!(health.verdict(at_threshold), Verdict::Failed(ServerFailure::NotStarted));
}

#[test]
fn a_start_after_an_answer_is_measured_from_the_start() {
    let mut health = health();
    let started_at = Instant::now();
    health.on_start(started_at);
    health.on_answer(started_at);

    // A new server has not answered, whatever its predecessor did, so the liveness timeout does not apply to it.
    let restarted_at = started_at + Duration::from_secs(1);
    health.on_start(restarted_at);
    let past_liveness = restarted_at + LIVENESS_TIMEOUT;
    assert_eq!(health.verdict(past_liveness), Verdict::Healthy);
}

#[test]
fn exits_fail_the_server_at_the_exit_limit() {
    let mut health = health();
    let first = Instant::now();

    // Fewer exits than the limit are restarted without a failure ..
    health.on_exit(first);
    health.on_exit(first + Duration::from_secs(1));
    assert_eq!(health.verdict(first + Duration::from_secs(2)), Verdict::Healthy);

    // .. and the exit that reaches the limit is a failure.
    health.on_exit(first + Duration::from_secs(2));
    assert_eq!(
        health.verdict(first + Duration::from_secs(2)),
        Verdict::Failed(ServerFailure::Exits)
    );
}

#[test]
fn exits_outside_the_window_do_not_count() {
    let mut health = health();
    let first = Instant::now();
    health.on_exit(first);
    health.on_exit(first + Duration::from_secs(1));

    // The first exit leaves the window at the moment the window elapses ..
    let third_at = first + EXIT_WINDOW;
    health.on_exit(third_at);
    assert_eq!(health.verdict(third_at), Verdict::Healthy);

    // .. so three exits fail the server only once they fall into one window.
    health.on_exit(third_at);
    assert_eq!(health.verdict(third_at), Verdict::Failed(ServerFailure::Exits));
}

#[test]
fn a_stop_by_the_node_is_not_a_failure() {
    let mut health = health();
    let started_at = Instant::now();
    health.on_start(started_at);
    health.on_answer(started_at);
    health.on_stop();

    let long_after = started_at + START_TIMEOUT;
    assert_eq!(health.verdict(long_after), Verdict::Healthy);
}

#[test]
fn a_reset_forgets_the_exits() {
    let mut health = health();
    let first = Instant::now();
    for _ in 0..EXIT_LIMIT {
        health.on_exit(first);
    }
    assert_eq!(health.verdict(first), Verdict::Failed(ServerFailure::Exits));

    health.reset();
    assert_eq!(health.verdict(first), Verdict::Healthy);
}
