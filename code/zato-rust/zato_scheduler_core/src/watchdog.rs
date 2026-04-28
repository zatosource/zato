//! Watchdog thread that detects hung Rust threads and logs diagnostics.
//!
//! Each monitored thread registers a heartbeat handle and bumps it on every
//! iteration. The watchdog sleeps for `CHECK_INTERVAL`, then inspects all
//! registered heartbeats. If any heartbeat has not advanced in longer than
//! expected, the watchdog logs thread states, wchan, mutex contention, and
//! the scheduler stop flag.
//!
//! Threads that legitimately sleep (e.g. `condvar.wait_for`) call
//! `set_expected_sleep` before sleeping so the watchdog does not raise
//! false alarms.

use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

use parking_lot::Mutex;
use tracing;

use crate::scheduler::SchedulerShared;

/// How often the watchdog checks heartbeats.
const CHECK_INTERVAL: Duration = Duration::from_secs(2);

/// Grace period added on top of the expected sleep duration before
/// the watchdog considers a thread stuck.
const GRACE: Duration = Duration::from_secs(2);

/// Handle returned by `WatchdogRegistry::register` for a monitored thread.
///
/// The owning thread calls `beat()` on each iteration to signal liveness,
/// and `set_expected_sleep` / `clear_expected_sleep` around legitimate
/// blocking operations.
pub struct HeartbeatHandle {
    /// Shared atomic state for heartbeat timestamps and expected sleep.
    inner: Arc<HeartbeatInner>,
}

/// Internal heartbeat state shared between the handle and the registry.
struct HeartbeatInner {
    /// Monotonic nanoseconds since the registry epoch at last beat.
    last_beat_nanos: AtomicU64,
    /// Expected sleep duration in nanoseconds, set before condvar waits.
    ///
    /// When non-zero, the watchdog adds this plus `GRACE` to the last beat
    /// before comparing against the current time.
    expected_sleep_nanos: AtomicU64,
    /// Epoch used to compute relative timestamps.
    epoch: Instant,
}

impl HeartbeatHandle {
    /// Records the current monotonic timestamp as the latest heartbeat
    /// and clears any expected sleep.
    pub fn beat(&self) {
        let elapsed = self.inner.epoch.elapsed();
        let nanos = u64::try_from(elapsed.as_nanos()).unwrap_or(u64::MAX);
        self.inner.last_beat_nanos.store(nanos, Ordering::Relaxed);
        self.inner.expected_sleep_nanos.store(0, Ordering::Relaxed);
    }

    /// Tells the watchdog that this thread is about to sleep for up to
    /// `duration`. The watchdog will not flag the thread as stuck until
    /// `duration + GRACE` has elapsed since the last beat.
    pub fn set_expected_sleep(&self, duration: Duration) {
        let nanos = u64::try_from(duration.as_nanos()).unwrap_or(u64::MAX);
        self.inner.expected_sleep_nanos.store(nanos, Ordering::Relaxed);
    }
}

/// Metadata for a single registered thread.
struct Registration {
    /// Human-readable thread name for diagnostics.
    name: String,
    /// Shared atomic state for heartbeat timestamps and expected sleep.
    inner: Arc<HeartbeatInner>,
}

/// Registry shared between the watchdog thread and callers of `register`.
pub struct WatchdogRegistry {
    /// Monotonic reference point for computing heartbeat timestamps.
    epoch: Instant,
    /// Registered threads with their heartbeat handles.
    threads: Mutex<Vec<Registration>>,
    /// Shared scheduler state used for diagnostic checks.
    shared: Arc<SchedulerShared>,
}

impl WatchdogRegistry {
    /// Creates a new registry tied to the given scheduler shared state.
    pub fn new(shared: Arc<SchedulerShared>) -> Self {
        Self {
            epoch: Instant::now(),
            threads: Mutex::new(Vec::new()),
            shared,
        }
    }

    /// Registers a thread for watchdog monitoring.
    ///
    /// Returns a `HeartbeatHandle` that the thread must call `beat()` on
    /// each iteration.
    pub fn register(&self, name: &str) -> HeartbeatHandle {
        let inner = Arc::new(HeartbeatInner {
            last_beat_nanos: AtomicU64::new(self.nanos_since_epoch()),
            expected_sleep_nanos: AtomicU64::new(0),
            epoch: self.epoch,
        });
        self.threads.lock().push(Registration {
            name: name.to_string(),
            inner: Arc::clone(&inner),
        });
        HeartbeatHandle { inner }
    }

    /// Monotonic nanoseconds since the registry was created.
    fn nanos_since_epoch(&self) -> u64 {
        u64::try_from(self.epoch.elapsed().as_nanos()).unwrap_or(u64::MAX)
    }
}

/// Starts the watchdog thread.
///
/// The watchdog runs until the scheduler's stop flag is set.
/// If the thread cannot be spawned, an error is logged.
pub fn start_watchdog(registry: Arc<WatchdogRegistry>) {
    let result = std::thread::Builder::new()
        .name("zato-watchdog".into())
        .spawn(move || watchdog_loop(&registry));
    if let Err(err) = result {
        tracing::error!("watchdog: failed to spawn thread: {err}");
    }
}

/// Main watchdog loop.
fn watchdog_loop(registry: &WatchdogRegistry) {
    tracing::info!("watchdog: started");

    let grace_nanos = u64::try_from(GRACE.as_nanos()).unwrap_or(u64::MAX);

    loop {
        std::thread::sleep(CHECK_INTERVAL);

        if registry.shared.stop_flag.load(Ordering::Relaxed) {
            tracing::info!("watchdog: stop flag set, exiting");
            break;
        }

        let now_nanos = registry.nanos_since_epoch();
        let threads = registry.threads.lock();

        let mut any_stuck = false;
        for reg in threads.iter() {
            let last_beat = reg.inner.last_beat_nanos.load(Ordering::Relaxed);
            let expected_sleep = reg.inner.expected_sleep_nanos.load(Ordering::Relaxed);
            let threshold = expected_sleep.saturating_add(grace_nanos);
            let elapsed = now_nanos.saturating_sub(last_beat);
            if elapsed >= threshold {
                let elapsed_secs = elapsed / 1_000_000_000;
                tracing::error!(
                    "watchdog: thread '{}' appears stuck for ~{}s (last heartbeat {}ns ago, expected_sleep={}ns)",
                    reg.name,
                    elapsed_secs,
                    elapsed,
                    expected_sleep,
                );
                any_stuck = true;
            }
        }
        drop(threads);

        if any_stuck {
            log_diagnostics(registry);
        }
    }
}

/// Logs diagnostic information when a stuck thread is detected.
fn log_diagnostics(registry: &WatchdogRegistry) {
    tracing::error!("watchdog: --- begin diagnostics ---");

    tracing::error!("watchdog: stop_flag={}", registry.shared.stop_flag.load(Ordering::Relaxed));

    let mutex_held = registry.shared.state.try_lock().is_none();
    tracing::error!("watchdog: state mutex currently held={mutex_held}");

    log_proc_thread_info();

    tracing::error!("watchdog: --- end diagnostics ---");
}

/// Reads `/proc/self/task/*/wchan` and `/proc/self/task/*/status` for all threads.
fn log_proc_thread_info() {
    let task_dir = match std::fs::read_dir("/proc/self/task") {
        Ok(dir) => dir,
        Err(err) => {
            tracing::error!("watchdog: cannot read /proc/self/task: {err}");
            return;
        }
    };

    for entry in task_dir {
        let Ok(entry) = entry else { continue };
        let tid = entry.file_name();
        let tid_str = tid.to_string_lossy();

        let wchan_path = format!("/proc/self/task/{tid_str}/wchan");
        let wchan = std::fs::read_to_string(&wchan_path).unwrap_or_else(|_| "?".into());

        let status_path = format!("/proc/self/task/{tid_str}/status");
        let state_line = std::fs::read_to_string(&status_path)
            .ok()
            .and_then(|contents| contents.lines().find(|line| line.starts_with("State:")).map(String::from))
            .unwrap_or_else(|| "State: ?".into());

        tracing::error!("watchdog: tid={tid_str} wchan={wchan} {state_line}");
    }
}
