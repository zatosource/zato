//! Rate limiting engine for Zato REST channels.
//!
//! Contains a token bucket (pace limiter) and a fixed-window counter
//! (quota limiter), both exposed to Python via `PyO3`.

pub mod common;
pub mod fixed_window;
pub mod token_bucket;

use pyo3::prelude::*;

/// `PyO3` module initializer - registers all Python-visible functions and classes.
#[pymodule]
fn zato_rate_limiting_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<token_bucket::TokenBucketConfig>()?;
    module.add_class::<token_bucket::CheckResult>()?;
    module.add_class::<token_bucket::TokenBucketRegistry>()?;
    Ok(())
}
