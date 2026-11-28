//! The threads of the push engine.
//!
//! The tests cover an internal error of a job reported as its outcome, the engine serving jobs after one,
//! the eventfd written for each completed job, and a stop with a job in flight.

use std::net::TcpListener;
use std::thread;
use std::time::{Duration, Instant};

use super::{Shared, request_stop, run_guarded, wait_for_threads, worker_loop};
use crate::push_engine::job::{PushJob, PushRequest, RequestOutcome};
use crate::push_engine::run::EnginePools;
use crate::outgoing::tls::TlsSettings;

use std::collections::VecDeque;
use std::sync::Arc;

use parking_lot::{Condvar, Mutex};
use rustix::event::{EventfdFlags, eventfd};

/// How many idle connections the pools of the tests keep per endpoint.
const POOL_SIZE: usize = 2;

/// The timeout of the job that is in flight when the engine stops, in seconds.
const IN_FLIGHT_TIMEOUT: f64 = 0.5;

/// How long a stop waits for the threads.
const STOP_WAIT: Duration = Duration::from_secs(5);

/// How long the endpoint that never answers keeps its connection open.
const SILENT_HOLD: Duration = Duration::from_secs(3);

/// Shared state of an engine with the given number of threads and no jobs.
fn new_shared(thread_count: usize) -> Arc<Shared> {
    Arc::new(Shared {
        queue: Mutex::new(super::JobQueue {
            jobs: VecDeque::new(),
            is_stopping: false,
        }),
        has_work: Condvar::new(),
        completed: Mutex::new(Vec::new()),
        wake: eventfd(0, EventfdFlags::NONBLOCK | EventfdFlags::CLOEXEC).unwrap(),
        running: Mutex::new(thread_count),
        thread_exited: Condvar::new(),
        pools: EnginePools::new(POOL_SIZE),
    })
}

#[test]
fn internal_error_of_a_job_is_its_outcome() {
    let outcome = run_guarded(7, || panic!("Push job of sub_key zpsk.rest.a1 ended by an internal error"));

    assert_eq!(outcome.id, 7);
    assert!(outcome.requests.is_empty());
    assert_eq!(outcome.internal_error.as_deref(), Some("Push job of sub_key zpsk.rest.a1 ended by an internal error"));

    // The thread that caught the internal error runs the next job as usual
    let next = run_guarded(8, || vec![RequestOutcome::new("http://127.0.0.1/orders")]);
    assert_eq!(next.id, 8);
    assert!(next.internal_error.is_none());
    assert_eq!(next.requests.len(), 1);
}

#[test]
fn eventfd_is_written_for_each_completed_job() {
    let shared = new_shared(1);

    shared.complete(run_guarded(1, Vec::new));
    shared.complete(run_guarded(2, Vec::new));

    let mut bytes = [0_u8; 8];
    rustix::io::read(&shared.wake, &mut bytes).unwrap();
    assert_eq!(u64::from_ne_bytes(bytes), 2);

    // The read cleared the counter, and the completed outcomes wait to be taken
    shared.drain_wake().unwrap();
    assert_eq!(shared.completed.lock().len(), 2);
}

#[test]
fn stop_with_a_job_in_flight() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let address = listener.local_addr().unwrap();

    let server = thread::spawn(move || {
        let (_connection, _) = listener.accept().unwrap();
        thread::sleep(SILENT_HOLD);
    });

    let shared = new_shared(1);
    let thread_shared = Arc::clone(&shared);
    let worker = thread::spawn(move || worker_loop(&thread_shared));

    let request = PushRequest {
        url: format!("http://{address}/orders/push"),
        headers: Vec::new(),
        parts: vec![b"{}".to_vec()],
        msg_ids: vec![String::from("zpsm.in-flight")],
        is_list: false,
    };

    shared.queue.lock().jobs.push_back(PushJob {
        id: 1,
        requests: vec![request],
        timeout: Some(IN_FLIGHT_TIMEOUT),
        tls: TlsSettings::default(),
        tls_generation: 0,
    });
    shared.has_work.notify_one();

    // The job is in flight once the endpoint holds its connection
    thread::sleep(Duration::from_millis(100));

    let start = Instant::now();
    request_stop(&shared);
    let is_stopped = wait_for_threads(&shared, STOP_WAIT);

    assert!(is_stopped);
    assert!(start.elapsed() < STOP_WAIT);
    worker.join().unwrap();

    // The job in flight completed with the error of its timeout
    let completed = shared.completed.lock();
    let outcome = completed.first().unwrap();
    assert_eq!(outcome.id, 1);
    assert!(outcome.requests.first().unwrap().error.is_some());

    drop(completed);
    server.join().unwrap();
}
