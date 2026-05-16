# zato_scheduler_core

Statistics computation, storage, and query API for the Zato scheduler.

## 1. Execution history storage

1. All statistics are computed in-memory, per job.
2. Each job holds a ring buffer (VecDeque) of ExecutionRecord entries.
3. Maximum capacity: 10,000 records per job (DEFAULT_MAX_HISTORY).
4. When full, the oldest record is evicted (FIFO).
5. No time-based retention - only the count cap applies.

Each ExecutionRecord contains:

```
+-------------------------+------------------------------------------+
| Field                   | Description                              |
+-------------------------+------------------------------------------+
| planned_fire_time_iso   | ISO timestamp of the scheduled fire time |
| actual_fire_time_iso    | ISO timestamp of the actual fire time    |
| delay_ms                | Difference between planned and actual    |
| outcome                 | One of the outcome labels (see below)    |
| current_run             | Run counter at time of execution         |
| duration_ms             | Wall-clock duration (ms), if completed   |
| error                   | Error message, if failed                 |
| outcome_ctx             | Additional context for the outcome       |
| log_entries             | Vec of (timestamp_iso, level, message)   |
+-------------------------+------------------------------------------+
```


## 2. Outcome labels

1. ok                        - executed successfully
2. error                     - failed with an exception
3. timeout                   - exceeded max_execution_time_ms
4. running                   - currently in flight
5. skipped_already_in_flight - skipped because previous run still going
6. skipped_holiday           - skipped because date is on a holiday calendar

The filter wildcard "all" matches every outcome.


## 3. Per-job summary (JobSummary)

Computed on-the-fly from the ring buffer when queried:

1. outcome_counts   - per-outcome totals across the entire retained history
2. last_outcome     - outcome of the most recent record
3. last_duration_ms - duration of the most recent completed record
4. recent_outcomes  - last 10 outcome labels (most recent last)

Plus static metadata:

5. id, name, is_active, service, job_type
6. in_flight, current_run, interval_ms, next_fire_utc


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


## 5. Stats-related functions

1. RunningJob::summary() -> JobSummary
   - Module: job.rs
   - Iterates the ring buffer to compute outcome_counts, last_outcome,
     last_duration_ms, and recent_outcomes (last 10).

2. RunningJob::record_execution(record: ExecutionRecord)
   - Module: job.rs
   - Appends a record to the ring buffer, evicting oldest if at capacity.

3. collect_due_jobs(state, now, coalesce_window_ms, deferred) -> Vec<FireBatch>
   - Module: scheduler.rs
   - Fires due jobs, creates ExecutionRecord with outcome=running,
     increments current_run, updates Prometheus gauges.

4. check_in_flight_timeouts(state, deferred)
   - Module: scheduler.rs
   - Detects timed-out jobs, records outcome=timeout, updates
     EXECUTIONS_TOTAL and EXECUTION_DURATION_SECONDS.

5. handle_mark_complete(shared, payload)
   - Module: redis_streams.rs
   - Patches existing history record's outcome and duration_ms in-place,
     increments EXECUTIONS_TOTAL and observes EXECUTION_DURATION_SECONDS.

6. handle_append_log_entry(shared, payload)
   - Module: redis_streams.rs
   - Appends a LogEntry to the matching history record by current_run.

7. record_to_response(rec, job_id, job_name) -> RecordResponse
   - Module: history.rs
   - Converts an ExecutionRecord into the API response struct,
     computing LogSummary counts per level.

8. records_to_responses(records, job_id, job_name) -> Vec<RecordResponse>
   - Module: history.rs
   - Batch version of the above.

9. encode_metrics() -> String
   - Module: metrics.rs
   - Encodes all registered Prometheus metrics into text exposition format.

10. compute_sleep_duration(state) -> Duration
    - Module: scheduler.rs
    - Finds the soonest event (next fire or in-flight timeout) to determine
      how long the loop sleeps.


## 6. How stats are updated

```
                              Redis command stream
                                     |
                                     v
+--------+    fire    +----------+     mark_complete     +----------+
| sched  | ---------> | record   | <-------------------- | server   |
| loop   |            | outcome= |                       | (Python) |
|        |            | running  |                       +----------+
+--------+            +----------+
     |                      |
     |  timeout detected    |  outcome + duration_ms patched in-place
     |  internally          |  Prometheus counters incremented
     v                      v
  record with            record with
  outcome=timeout        outcome=ok/error
```

1. Job fires -> ExecutionRecord with outcome=running appended to ring buffer.
2. Server completes invocation -> mark_complete arrives via Redis stream.
3. Existing record's outcome and duration_ms are patched in-place.
4. Prometheus execution counter and duration histogram are updated.
5. Timeouts are detected by the scheduler loop comparing elapsed time
   against max_execution_time_ms (default 1 hour, range 1s-24h).


## 7. Retention

1. In-memory execution history: 10,000 records per job (FIFO eviction).
2. Redis streams: trimmed at ~100,000 entries each (STREAM_MAXLEN).
3. Prometheus counters: monotonic, never reset except on process restart.
4. No disk persistence for any of the above.
