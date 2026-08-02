// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Numeric conversions that the standard library cannot express without loss.
//!
//! Everywhere else in this crate, timing is integer milliseconds and conversions go through
//! `TryFrom`. Prometheus is the exception: it records every observation as `f64` seconds, so
//! the step out of integer milliseconds has to happen somewhere. It happens here, once, with
//! the reasoning written down, rather than at each metric call.

/// Milliseconds in one second, as the float the conversion below divides by.
const MILLISECONDS_PER_SECOND: f64 = 1000.0;

// ################################################################################################################################

/// Converts a duration in whole milliseconds into the seconds a Prometheus histogram takes.
///
/// An `f64` represents whole milliseconds exactly up to roughly 285,000 years, so no job
/// duration this crate measures can reach the point where precision is actually lost. The
/// lint fires on the pair of types involved, not on the values that arrive here.
#[must_use]
#[expect(
    clippy::cast_precision_loss,
    clippy::as_conversions,
    reason = "Prometheus observes f64 seconds, and no measured duration comes near the precision limit"
)]
pub fn ms_to_seconds(milliseconds: u64) -> f64 {
    milliseconds as f64 / MILLISECONDS_PER_SECOND
}

// ################################################################################################################################
