use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::time::{Duration, Instant};

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::PyString;

use crate::calendar::CalendarData;
use crate::job::{ExecutionRecord, RunningJob};
use crate::types::{FireBatch, JobType, OnMissedPolicy, outcome};

type PyObject = Py<PyAny>;

const DEFAULT_CLOCK_JUMP_THRESHOLD_MS: i64 = 5_000;
const DEFAULT_COALESCE_WINDOW_MS: i64 = 50;

pub struct SchedulerState {
    pub jobs: HashMap<String, RunningJob>,
    pub calendars: HashMap<String, CalendarData>,
    pub dirty: bool,
}

impl SchedulerState {
    pub fn new() -> Self {
        SchedulerState {
            jobs: HashMap::new(),
            calendars: HashMap::new(),
            dirty: false,
        }
    }
}

pub struct SchedulerShared {
    pub state: Mutex<SchedulerState>,
    pub condvar: Condvar,
    pub stop_flag: AtomicBool,
    pub clock_jump_threshold_ms: i64,
    pub coalesce_window_ms: i64,
}

impl SchedulerShared {
    pub fn new() -> Self {
        SchedulerShared {
            state: Mutex::new(SchedulerState::new()),
            condvar: Condvar::new(),
            stop_flag: AtomicBool::new(false),
            clock_jump_threshold_ms: DEFAULT_CLOCK_JUMP_THRESHOLD_MS,
            coalesce_window_ms: DEFAULT_COALESCE_WINDOW_MS,
        }
    }
}

pub fn scheduler_loop(
    shared: Arc<SchedulerShared>,
    config_store: PyObject,
    run_cb: PyObject,
    spawn_fn: PyObject,
    on_job_executed_cb: PyObject,
    initial_sleep_time: f64,
) {
    if initial_sleep_time > 0.0 {
        std::thread::sleep(Duration::from_secs_f64(initial_sleep_time));
    }

    if shared.stop_flag.load(Ordering::Relaxed) {
        return;
    }

    load_jobs_from_config_store(&shared, &config_store);

    {
        let mut state = shared.state.lock().unwrap();
        let now = Utc::now();
        apply_missed_catchup(&mut state, now);
    }

    let mut last_wall = Utc::now();
    let mut last_mono = Instant::now();

    loop {
        if shared.stop_flag.load(Ordering::Relaxed) {
            break;
        }

        let sleep_duration = {
            let state = shared.state.lock().unwrap();
            compute_sleep_duration(&state)
        };

        {
            let state = shared.state.lock().unwrap();
            let _unused = shared.condvar.wait_timeout(state, sleep_duration).unwrap();
        }

        if shared.stop_flag.load(Ordering::Relaxed) {
            break;
        }

        let now_wall = Utc::now();
        let now_mono = Instant::now();
        let wall_delta_ms = (now_wall - last_wall).num_milliseconds();
        let mono_delta_ms = now_mono.duration_since(last_mono).as_millis() as i64;

        if (wall_delta_ms - mono_delta_ms).abs() > shared.clock_jump_threshold_ms {
            let mut state = shared.state.lock().unwrap();
            reanchor_all_jobs(&mut state, now_wall);
        }

        last_wall = now_wall;
        last_mono = now_mono;

        let fire_batch = {
            let mut state = shared.state.lock().unwrap();
            check_in_flight_timeouts(&mut state);
            collect_due_jobs(&mut state, now_wall, shared.coalesce_window_ms)
        };

        if !fire_batch.is_empty() {
            dispatch_jobs(&fire_batch, &run_cb, &spawn_fn, &on_job_executed_cb);
        }
    }
}

pub fn load_from_config_store_py(
    cs: &Bound<'_, PyAny>,
) -> PyResult<(
    HashMap<String, zato_server_core::models::SchedulerJob>,
    HashMap<String, zato_server_core::models::HolidayCalendar>,
)> {
    let jobs_json: String = cs.call_method0("get_scheduler_jobs_json")?.extract()?;
    let cals_json: String = cs.call_method0("get_holiday_calendars_json")?.extract()?;

    let jobs: HashMap<String, zato_server_core::models::SchedulerJob> =
        serde_json::from_str(&jobs_json).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("bad scheduler jobs JSON: {}", e))
        })?;
    let cals: HashMap<String, zato_server_core::models::HolidayCalendar> =
        serde_json::from_str(&cals_json).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("bad holiday calendars JSON: {}", e))
        })?;

    Ok((jobs, cals))
}

fn load_jobs_from_config_store(shared: &SchedulerShared, config_store: &PyObject) {
    Python::try_attach(|py| {
        let cs = config_store.bind(py);
        match load_from_config_store_py(cs) {
            Ok((jobs, _cals)) => {
                let mut state = shared.state.lock().unwrap();
                for (id, job) in &jobs {
                    let rj = RunningJob::from_scheduler_job(job);
                    state.jobs.insert(id.clone(), rj);
                }
            }
            Err(e) => {
                log::error!("Failed to load jobs from config store: {}", e);
            }
        }
    });
}

pub fn compute_sleep_duration(state: &SchedulerState) -> Duration {
    let now = Utc::now();
    let mut min_ms: i64 = 60_000;

    for rj in state.jobs.values() {
        if !rj.is_active {
            continue;
        }
        if let Some(fire_utc) = rj.next_fire_utc {
            let diff = (fire_utc - now).num_milliseconds();
            if diff < min_ms {
                min_ms = diff;
            }
        }
    }

    Duration::from_millis(min_ms.max(1) as u64)
}

pub fn collect_due_jobs(
    state: &mut SchedulerState,
    now: chrono::DateTime<Utc>,
    coalesce_window_ms: i64,
) -> Vec<FireBatch> {
    let threshold = now + chrono::Duration::milliseconds(coalesce_window_ms);
    let mut batch = Vec::new();

    let job_ids: Vec<String> = state.jobs.keys().cloned().collect();

    for id in job_ids {
        let calendars_ref = &state.calendars;
        let rj = match state.jobs.get_mut(&id) {
            Some(rj) => rj,
            None => continue,
        };

        if !rj.is_active {
            continue;
        }

        let Some(fire_utc) = rj.next_fire_utc else { continue };

        if fire_utc > threshold {
            continue;
        }

        let planned = fire_utc.to_rfc3339();
        let actual = now.to_rfc3339();

        if rj.in_flight {
            rj.record_execution(
                ExecutionRecord::new(&planned, &actual, outcome::SKIPPED_CONCURRENT, rj.current_run)
            );
            rj.advance_to_next(now);
            continue;
        }

        if rj.is_holiday_today(calendars_ref) {
            rj.record_execution(
                ExecutionRecord::new(&planned, &actual, outcome::SKIPPED_HOLIDAY, rj.current_run)
            );
            rj.advance_to_next(now);
            continue;
        }

        rj.in_flight = true;
        rj.in_flight_since = Some(Instant::now());
        rj.current_run += 1;

        let latency = (now - fire_utc).num_milliseconds().max(0) as u64;

        batch.push(FireBatch {
            job_id: rj.id.clone(),
            name: rj.name.clone(),
            service: rj.service.clone(),
            extra: rj.extra.clone(),
            job_type: rj.job_type.clone(),
            current_run: rj.current_run,
        });

        rj.record_execution(
            ExecutionRecord::new(&planned, &actual, outcome::EXECUTED, rj.current_run)
                .with_latency(latency)
        );

        rj.advance_to_next(now);
    }

    batch
}

fn dispatch_jobs(
    batch: &[FireBatch],
    run_cb: &PyObject,
    spawn_fn: &PyObject,
    on_job_executed_cb: &PyObject,
) {
    Python::try_attach(|py| {
        for item in batch {
            let ctx = serde_json::json!({
                "id": item.job_id.as_ref(),
                "name": item.name,
                "service": item.service.as_ref(),
                "extra": item.extra,
                "job_type": item.job_type.as_str(),
                "current_run": item.current_run,
            });
            let ctx_str = ctx.to_string();
            let py_ctx = PyString::new(py, &ctx_str).into_any().unbind();
            if let Err(e) = run_cb.call1(py, (spawn_fn, on_job_executed_cb, py_ctx)) {
                log::error!(
                    "Failed to dispatch job `{}` (service=`{}`, run={}): {}",
                    item.name, item.service, item.current_run, e
                );
            }
        }
    });
}

pub fn check_in_flight_timeouts(state: &mut SchedulerState) {
    let now_instant = Instant::now();

    for rj in state.jobs.values_mut() {
        if !rj.in_flight {
            continue;
        }
        let Some(since) = rj.in_flight_since else { continue };
        let elapsed_ms = now_instant.duration_since(since).as_millis() as u64;
        if elapsed_ms > rj.max_execution_time_ms {
            rj.in_flight = false;
            rj.in_flight_since = None;
            rj.record_execution(
                ExecutionRecord::new("", &Utc::now().to_rfc3339(), outcome::TIMEOUT, rj.current_run)
                    .with_duration(elapsed_ms)
                    .with_error(format!("exceeded max_execution_time_ms={}", rj.max_execution_time_ms))
            );
        }
    }
}

pub fn reanchor_all_jobs(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    for rj in state.jobs.values_mut() {
        if rj.is_active {
            rj.compute_next_fire(now);
        }
    }
    apply_missed_catchup(state, now);
}

pub fn apply_missed_catchup(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    let job_ids: Vec<String> = state.jobs.keys().cloned().collect();

    for id in job_ids {
        let rj = match state.jobs.get_mut(&id) {
            Some(rj) => rj,
            None => continue,
        };

        if !rj.is_active || rj.job_type == JobType::OneTime {
            continue;
        }

        let Some(sd) = rj.start_date else { continue };
        if sd > now {
            continue;
        }

        match rj.on_missed {
            OnMissedPolicy::Skip => {
                rj.compute_next_fire(now);
            }
            OnMissedPolicy::RunOnce => {
                if let Some(fire) = rj.next_fire_utc {
                    if fire < now {
                        rj.record_execution(
                            ExecutionRecord::new(
                                &fire.to_rfc3339(),
                                &now.to_rfc3339(),
                                outcome::MISSED_CATCHUP,
                                rj.current_run,
                            )
                        );
                        rj.next_fire_utc = Some(now);
                        rj.sync_instant_from_utc_pub(now);
                    }
                }
            }
        }
    }
}
