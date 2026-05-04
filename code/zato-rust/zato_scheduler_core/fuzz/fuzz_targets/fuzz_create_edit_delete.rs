#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_scheduler_core::job::RunningJob;
use zato_scheduler_core::scheduler::SchedulerState;
use zato_server_core::model::SchedulerJob;

fn make_job_from_bytes(data: &[u8], id: &str) -> SchedulerJob {
    let get_byte = |i: usize| -> u8 { *data.get(i).unwrap_or(&0) };
    let is_active = get_byte(0) % 2 == 0;
    let job_type = if get_byte(1) % 2 == 0 { "interval_based" } else { "one_time" };
    let minutes = u32::from(get_byte(2) % 60) + 1;

    SchedulerJob {
        id: id.into(),
        name: format!("fuzz-{id}"),
        is_active,
        service: "svc".into(),
        job_type: job_type.into(),
        start_date: "2026-01-01T00:00:00".into(),
        extra: None,
        weeks: None,
        days: None,
        hours: None,
        minutes: Some(minutes),
        seconds: None,
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        max_execution_time_ms: None,
    }
}

fuzz_target!(|data: &[u8]| {
    if data.len() < 10 {
        return;
    }

    let mut state = SchedulerState::new();

    let mut offset = 0;
    let mut job_counter = 0u32;

    while offset + 4 <= data.len() {
        let op = data[offset] % 3;
        offset += 1;

        match op {
            0 => {
                let id = format!("j{job_counter}");
                job_counter += 1;
                let chunk = &data[offset..data.len().min(offset + 3)];
                let sj = make_job_from_bytes(chunk, &id);
                let running_job = RunningJob::from_scheduler_job(&sj);
                state.jobs.insert(id, running_job);
                offset += 3;
            }
            1 => {
                if job_counter > 0 {
                    let idx = u32::from(data.get(offset).copied().unwrap_or(0)) % job_counter;
                    let id = format!("j{idx}");
                    offset += 1;
                    let chunk = &data[offset..data.len().min(offset + 3)];
                    let sj = make_job_from_bytes(chunk, &id);
                    if let Some(existing) = state.jobs.get_mut(&id) {
                        existing.update_from_job(&sj);
                    }
                    offset += 3;
                }
            }
            _ => {
                if job_counter > 0 {
                    let idx = u32::from(data.get(offset).copied().unwrap_or(0)) % job_counter;
                    let id = format!("j{idx}");
                    state.jobs.remove(&id);
                    offset += 1;
                }
            }
        }
    }

    for running_job in state.jobs.values() {
        if running_job.is_active && running_job.interval_ms > 0 && running_job.start_date.is_some() {
            assert!(
                running_job.next_fire_utc.is_some(),
                "active job with interval and start_date must have next_fire"
            );
        }
        if !running_job.in_flight {
            assert!(running_job.in_flight_since.is_none());
        }
    }
});
