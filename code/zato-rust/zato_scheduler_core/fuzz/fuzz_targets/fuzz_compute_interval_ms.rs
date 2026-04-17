#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_scheduler_core::job::RunningJob;
use zato_server_core::model::SchedulerJob;

fuzz_target!(|data: &[u8]| {
    if data.len() < 20 {
        return;
    }

    let read_u32 = |offset: usize| -> u32 {
        u32::from_le_bytes([data[offset], data[offset + 1], data[offset + 2], data[offset + 3]])
    };

    let job = SchedulerJob {
        id: "fuzz".into(),
        name: "fuzz".into(),
        is_active: true,
        service: "svc".into(),
        job_type: "interval_based".into(),
        start_date: "2026-01-01T00:00:00".into(),
        extra: None,
        weeks: Some(read_u32(0)),
        days: Some(read_u32(4)),
        hours: Some(read_u32(8)),
        minutes: Some(read_u32(12)),
        seconds: Some(read_u32(16)),
        repeats: None,
        jitter_ms: None,
        timezone: None,
        calendar: None,
        on_missed: None,
        max_execution_time_ms: None,
    };

    let _ = RunningJob::compute_interval_ms(&job);
});
