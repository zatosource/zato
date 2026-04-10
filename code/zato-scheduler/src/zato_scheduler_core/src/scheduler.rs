use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::time::{Duration, Instant};

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::PyString;

type PyObject = Py<PyAny>;

use crate::calendar::CalendarData;
use crate::job::{ExecutionRecord, RunningJob};

const CLOCK_JUMP_THRESHOLD_MS: i64 = 5_000;
const COALESCE_WINDOW_MS: i64 = 50;

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
}

impl SchedulerShared {
    pub fn new() -> Self {
        SchedulerShared {
            state: Mutex::new(SchedulerState::new()),
            condvar: Condvar::new(),
            stop_flag: AtomicBool::new(false),
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

        if (wall_delta_ms - mono_delta_ms).abs() > CLOCK_JUMP_THRESHOLD_MS {
            let mut state = shared.state.lock().unwrap();
            reanchor_all_jobs(&mut state, now_wall);
        }

        last_wall = now_wall;
        last_mono = now_mono;

        let fire_batch = {
            let mut state = shared.state.lock().unwrap();
            check_in_flight_timeouts(&mut state);
            collect_due_jobs(&mut state, now_wall)
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
        // TODO: load calendars here too, same as scheduler_reload does in lib.rs
        if let Ok((jobs, _cals)) = load_from_config_store_py(cs) {
            let mut state = shared.state.lock().unwrap();
            for (id, job) in &jobs {
                let rj = RunningJob::from_scheduler_job(job);
                state.jobs.insert(id.clone(), rj);
            }
        }
    });
}

pub(crate) fn compute_sleep_duration(state: &SchedulerState) -> Duration {
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

pub(crate) fn collect_due_jobs(
    state: &mut SchedulerState,
    now: chrono::DateTime<Utc>,
) -> Vec<(String, String, String, Option<String>, String, u32)> {
    let threshold = now + chrono::Duration::milliseconds(COALESCE_WINDOW_MS);
    let mut batch = Vec::new();

    let job_ids: Vec<String> = state.jobs.keys().cloned().collect();

    for id in job_ids {
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

        if rj.in_flight {
            rj.record_execution(ExecutionRecord {
                planned_fire_time_iso: fire_utc.to_rfc3339(),
                actual_fire_time_iso: now.to_rfc3339(),
                dispatch_latency_ms: 0,
                outcome: "skipped_concurrent".into(),
                current_run: rj.current_run,
                duration_ms: None,
                error: None,
            });
            rj.advance_to_next(now);
            continue;
        }

        if rj.is_holiday_today(&state.calendars) {
            rj.record_execution(ExecutionRecord {
                planned_fire_time_iso: fire_utc.to_rfc3339(),
                actual_fire_time_iso: now.to_rfc3339(),
                dispatch_latency_ms: 0,
                outcome: "skipped_holiday".into(),
                current_run: rj.current_run,
                duration_ms: None,
                error: None,
            });
            rj.advance_to_next(now);
            continue;
        }

        rj.in_flight = true;
        rj.in_flight_since = Some(Instant::now());
        rj.current_run += 1;

        let latency = (now - fire_utc).num_milliseconds().max(0) as u64;

        batch.push((
            rj.id.clone(),
            rj.name.clone(),
            rj.service.clone(),
            rj.extra.clone(),
            rj.job_type.clone(),
            rj.current_run,
        ));

        rj.record_execution(ExecutionRecord {
            planned_fire_time_iso: fire_utc.to_rfc3339(),
            actual_fire_time_iso: now.to_rfc3339(),
            dispatch_latency_ms: latency,
            outcome: "executed".into(),
            current_run: rj.current_run,
            duration_ms: None,
            error: None,
        });

        rj.advance_to_next(now);
    }

    batch
}

fn dispatch_jobs(
    batch: &[(String, String, String, Option<String>, String, u32)],
    run_cb: &PyObject,
    spawn_fn: &PyObject,
    on_job_executed_cb: &PyObject,
) {
    Python::try_attach(|py| {
        for (id, name, service, extra, job_type, current_run) in batch {
            let ctx = serde_json::json!({
                "id": id,
                "name": name,
                "service": service,
                "extra": extra,
                "job_type": job_type,
                "current_run": current_run,
            });
            let ctx_str = ctx.to_string();
            let py_ctx = PyString::new(py, &ctx_str).into_any().unbind();
            if let Err(e) = run_cb.call1(py, (spawn_fn, on_job_executed_cb, py_ctx)) {
                eprintln!("zato_scheduler_core: failed to dispatch job `{}`: {}", name, e);
            }
        }
    });
}

pub(crate) fn check_in_flight_timeouts(state: &mut SchedulerState) {
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
            rj.record_execution(ExecutionRecord {
                planned_fire_time_iso: String::new(),
                actual_fire_time_iso: Utc::now().to_rfc3339(),
                dispatch_latency_ms: 0,
                outcome: "timeout".into(),
                current_run: rj.current_run,
                duration_ms: Some(elapsed_ms),
                error: Some(format!("exceeded max_execution_time_ms={}", rj.max_execution_time_ms)),
            });
        }
    }
}

pub(crate) fn reanchor_all_jobs(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    for rj in state.jobs.values_mut() {
        if rj.is_active {
            rj.compute_next_fire(now);
        }
    }
    apply_missed_catchup(state, now);
}

pub(crate) fn apply_missed_catchup(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    let job_ids: Vec<String> = state.jobs.keys().cloned().collect();

    for id in job_ids {
        let rj = match state.jobs.get_mut(&id) {
            Some(rj) => rj,
            None => continue,
        };

        if !rj.is_active || rj.job_type == "one_time" {
            continue;
        }

        let Some(sd) = rj.start_date else { continue };
        if sd > now {
            continue;
        }

        let policy = rj.on_missed.clone();
        match policy.as_str() {
            "skip" => {
                rj.compute_next_fire(now);
            }
            "run_once" => {
                if let Some(fire) = rj.next_fire_utc {
                    if fire < now {
                        rj.record_execution(ExecutionRecord {
                            planned_fire_time_iso: fire.to_rfc3339(),
                            actual_fire_time_iso: now.to_rfc3339(),
                            dispatch_latency_ms: 0,
                            outcome: "missed_catchup".into(),
                            current_run: rj.current_run,
                            duration_ms: None,
                            error: None,
                        });
                        rj.next_fire_utc = Some(now);
                        rj.sync_instant_from_utc_pub(now);
                    }
                }
            }
            _ => {
                rj.compute_next_fire(now);
            }
        }
    }
}
