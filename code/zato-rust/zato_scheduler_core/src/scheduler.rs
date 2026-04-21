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
        eprintln!("[zato-scheduler] Loaded {} jobs", state.jobs.len());
        for (id, rj) in &state.jobs {
            eprintln!("[zato-scheduler] job id={} name={} active={} next_fire={:?}",
                id, rj.name, rj.is_active, rj.next_fire_utc);
        }
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
            eprintln!("[zato-scheduler] Dispatching {} jobs", fire_batch.len());
            dispatch_jobs(&fire_batch, &run_cb, &spawn_fn, &on_job_executed_cb);
        }
    }
}

pub fn load_from_config_store_py(
    cs: &Bound<'_, PyAny>,
) -> PyResult<(
    HashMap<String, zato_server_core::model::SchedulerJob>,
    HashMap<String, zato_server_core::model::HolidayCalendar>,
)> {
    let jobs_json: String = cs.call_method0("get_scheduler_jobs_json")?.extract()?;
    let cals_json: String = cs.call_method0("get_holiday_calendars_json")?.extract()?;

    eprintln!("[zato-scheduler] load_from_config_store_py: jobs_json length={}, preview={}",
        jobs_json.len(), &jobs_json[..jobs_json.len().min(500)]);

    let jobs: HashMap<String, zato_server_core::model::SchedulerJob> =
        serde_json::from_str(&jobs_json).map_err(|e| {
            eprintln!("[zato-scheduler] JSON parse error: {}, json={}", e, &jobs_json[..jobs_json.len().min(1000)]);
            pyo3::exceptions::PyValueError::new_err(format!("bad scheduler jobs JSON: {}", e))
        })?;
    let cals: HashMap<String, zato_server_core::model::HolidayCalendar> =
        serde_json::from_str(&cals_json).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("bad holiday calendars JSON: {}", e))
        })?;

    Ok((jobs, cals))
}

fn load_jobs_from_config_store(shared: &SchedulerShared, config_store: &PyObject) {
    Python::try_attach(|py| {
        let cs = config_store.bind(py);
        match load_from_config_store_py(cs) {
            Ok((jobs, cals)) => {
                let mut state = shared.state.lock().unwrap();
                for (_name, job) in &jobs {
                    let running_job = RunningJob::from_scheduler_job(job);
                    state.jobs.insert(job.id.clone(), running_job);
                }
                for (name, cal) in cals {
                    let mut calendar_data = CalendarData::new(name.clone());
                    for date_str in &cal.dates {
                        if let Ok(date) = chrono::NaiveDate::parse_from_str(date_str, "%Y-%m-%d") {
                            calendar_data.dates.insert(date);
                        }
                    }
                    calendar_data.weekdays = cal.weekdays.clone();
                    calendar_data.description = cal.description.clone();
                    state.calendars.insert(name, calendar_data);
                }
            }
            Err(e) => {
                eprintln!("[zato-scheduler] Failed to load jobs from config store: {}", e);
            }
        }
    });
}

pub fn compute_sleep_duration(state: &SchedulerState) -> Duration {
    let now = Utc::now();
    let mut min_ms: i64 = 60_000;

    for running_job in state.jobs.values() {
        if !running_job.is_active {
            continue;
        }
        if let Some(fire_utc) = running_job.next_fire_utc {
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
        let running_job = match state.jobs.get_mut(&id) {
            Some(running_job) => running_job,
            None => continue,
        };

        if !running_job.is_active {
            continue;
        }

        let Some(fire_utc) = running_job.next_fire_utc else { continue };

        if fire_utc > threshold {
            continue;
        }

        let planned = fire_utc.to_rfc3339();
        let actual = now.to_rfc3339();

        if running_job.in_flight {
            running_job.record_execution(
                ExecutionRecord::new(&planned, &actual, outcome::SKIPPED_ALREADY_IN_FLIGHT, running_job.current_run)
            );
            running_job.advance_to_next(now);
            continue;
        }

        if running_job.is_holiday_today(calendars_ref) {
            running_job.record_execution(
                ExecutionRecord::new(&planned, &actual, outcome::SKIPPED_HOLIDAY, running_job.current_run)
            );
            running_job.advance_to_next(now);
            continue;
        }

        running_job.in_flight = true;
        running_job.in_flight_since = Some(Instant::now());
        running_job.current_run += 1;

        let latency = (now - fire_utc).num_milliseconds().max(0) as u64;

        batch.push(FireBatch {
            job_id: running_job.id.clone(),
            name: running_job.name.clone(),
            service: running_job.service.clone(),
            extra: running_job.extra.clone(),
            job_type: running_job.job_type.clone(),
            current_run: running_job.current_run,
        });

        running_job.record_execution(
            ExecutionRecord::new(&planned, &actual, outcome::EXECUTED, running_job.current_run)
                .with_latency(latency)
        );

        running_job.advance_to_next(now);
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

    for running_job in state.jobs.values_mut() {
        if !running_job.in_flight {
            continue;
        }
        let Some(since) = running_job.in_flight_since else { continue };
        let elapsed_ms = now_instant.duration_since(since).as_millis() as u64;
        if elapsed_ms > running_job.max_execution_time_ms {
            running_job.in_flight = false;
            running_job.in_flight_since = None;
            running_job.record_execution(
                ExecutionRecord::new("", &Utc::now().to_rfc3339(), outcome::TIMEOUT, running_job.current_run)
                    .with_duration(elapsed_ms)
                    .with_error(format!("exceeded max_execution_time_ms={}", running_job.max_execution_time_ms))
            );
        }
    }
}

pub fn reanchor_all_jobs(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    for running_job in state.jobs.values_mut() {
        if running_job.is_active {
            running_job.compute_next_fire(now);
        }
    }
    apply_missed_catchup(state, now);
}

pub fn apply_missed_catchup(state: &mut SchedulerState, now: chrono::DateTime<Utc>) {
    let job_ids: Vec<String> = state.jobs.keys().cloned().collect();

    for id in job_ids {
        let running_job = match state.jobs.get_mut(&id) {
            Some(running_job) => running_job,
            None => continue,
        };

        if !running_job.is_active || running_job.job_type == JobType::OneTime {
            continue;
        }

        let Some(start_date) = running_job.start_date else { continue };
        if start_date > now {
            continue;
        }

        match running_job.on_missed {
            OnMissedPolicy::Skip => {
                running_job.compute_next_fire(now);
            }
            OnMissedPolicy::RunOnce => {
                if let Some(fire) = running_job.next_fire_utc {
                    if fire < now {
                        running_job.record_execution(
                            ExecutionRecord::new(
                                &fire.to_rfc3339(),
                                &now.to_rfc3339(),
                                outcome::MISSED_CATCHUP,
                                running_job.current_run,
                            )
                        );
                        running_job.next_fire_utc = Some(now);
                        running_job.sync_instant_from_utc_pub(now);
                    }
                }
            }
        }
    }
}
