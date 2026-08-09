# zato_scheduler_core

Job scheduling engine, runtime state, metrics, and query API for the Zato scheduler.

Execution history is not stored here - each run's historical record lives in the
Zato server's SQL audit log. This crate keeps only what is genuinely scheduling:
next-fire computation, in-flight tracking, timeout detection, and Prometheus metrics.

## 1. Runtime state

1. Each job is a RunningJob held in a HashMap keyed by job id.
2. Per-job runtime fields: next_fire_utc, in_flight, in_flight_since,
   in_flight_run, current_run.
3. No execution records are retained - the server writes one audit log
   event per run and updates it in place on completion or timeout.

## 2. Outcome labels

The scheduler itself only labels timeouts (for its Prometheus metrics):

1. timeout - exceeded max_execution_time_ms

All other outcome labels (ok, error, running, skipped_already_in_flight)
are assigned by the server when it records runs in the audit log.

## 3. Per-job summary (JobSummary)

Scheduling-state snapshot returned by the HTTP query API:

1. id, name, is_active, service, job_type
2. in_flight, current_run, interval_ms, next_fire_utc

History aggregates (outcome counts, last outcome, recent outcomes) come
from the audit log on the server side, not from this crate.

## 4. Prometheus metrics

```
+----------------------------------------------+--------+--------------------------+
| Metric name                                  | Type   | Labels                   |
+----------------------------------------------+--------+--------------------------+
| zato_scheduler_jobs_total                    | gauge  | (none)                   |
| zato_scheduler_jobs_active                   | gauge  | (none)                   |
| zato_scheduler_jobs_in_flight                | gauge  | (none)                   |
| zato_scheduler_ticks_total                   | counter| (none)                   |
| zato_scheduler_clock_jumps_total             | counter| (none)                   |
| zato_scheduler_executions_total              | counter| job_name, outcome        |
| zato_scheduler_execution_duration_seconds    | hist   | job_name                 |
| zato_scheduler_uptime_seconds                | gauge  | (none)                   |
+----------------------------------------------+--------+--------------------------+
```

Histogram buckets: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0 seconds.
These match the Python server's zato_histogram_buckets.

## 5. Core functions

1. RunningJob::summary() -> JobSummary
   - Module: job.rs
   - Snapshots the job's scheduling state under the state mutex.

2. collect_due_jobs(state, now, coalesce_window_ms, deferred) -> Vec<FireBatch>
   - Module: scheduler.rs
   - Fires due jobs, marks them in flight, increments current_run,
     carries planned_fire_time_iso for the server's delay computation.

3. check_in_flight_timeouts(state, deferred) -> Vec<TimeoutEvent>
   - Module: scheduler.rs
   - Detects timed-out runs, clears their in-flight state, updates
     EXECUTIONS_TOTAL and EXECUTION_DURATION_SECONDS, and returns the
     events the loop publishes to the timeout stream.

4. handle_mark_complete(shared, payload)
   - Module: redis_streams.rs
   - Clears in-flight state, increments EXECUTIONS_TOTAL, observes
     EXECUTION_DURATION_SECONDS, and catches up on fires the run outlasted.

5. encode_metrics() -> String
   - Module: metrics.rs
   - Encodes all registered Prometheus metrics into text exposition format.

6. compute_sleep_duration(state) -> Duration
   - Module: scheduler.rs
   - Finds the soonest event (next fire or in-flight timeout) to determine
     how long the loop sleeps.

## 6. How a run flows

```
                              Redis command stream
                                     |
                                     v
+--------+  fire event   +----------+     mark_complete     +----------+
| sched  | ------------> | server   | --------------------> | sched    |
| loop   |  (Redis)      | (Python) |     (Redis)           | clears   |
|        |               | writes   |                       | in-flight|
+--------+               | audit log|                       +----------+
     |                   +----------+
     |  timeout detected        ^
     |  internally              |
     v                          |
  timeout event ----------------+
  (Redis)          server marks the run timed out in the audit log
```

1. Job fires -> the fire event carries planned_fire_time_iso, the server
   inserts a running audit log event.
2. Server completes invocation -> it updates the audit log event in place
   and sends mark_complete, which clears the in-flight state here.
3. Timeouts are detected by the scheduler loop comparing elapsed time
   against max_execution_time_ms (default 1 hour, range 1s-24h) - the
   timeout event goes to the server, which marks the run in the audit log.

## 7. Retention

1. Redis streams: trimmed at ~100,000 entries each (STREAM_MAXLEN).
2. Prometheus counters: monotonic, never reset except on process restart.
3. Execution history retention is the audit log's concern, on the server side.
