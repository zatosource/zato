//! `PushEngine`, the OS threads that send the REST pushes of pub/sub subscribers without the GIL.
//!
//! The Python side submits a job with an ID and waits. A thread of the engine runs the job and puts its outcome
//! on the completed list, then writes to an eventfd. One greenlet per worker process waits for the eventfd
//! to become readable, takes the completed outcomes and hands each to the greenlet that waits for it.

use std::collections::VecDeque;
use std::os::fd::{AsRawFd, OwnedFd};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use std::thread::JoinHandle;
use std::time::{Duration, Instant};

use parking_lot::{Condvar, Mutex};
use pyo3::exceptions::{PyOSError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList, PyString, PyTuple};
use rustix::event::{EventfdFlags, eventfd};
use rustix::io::{Errno, read, write};

use super::job::{JobOutcome, PushJob, PushRequest, RequestOutcome};
use super::redirect::next_redirect;
use super::run::{EnginePools, run_job};
use crate::outgoing::headers::{encode_text_value, is_valid_name};
use crate::outgoing::scope::NetworkScope;
use crate::outgoing::tls::TlsSettings;

/// Value written to the eventfd for each completed job.
const WAKE_INCREMENT: u64 = 1;

/// Initial counter of the eventfd.
const INITIAL_COUNT: u32 = 0;

/// The header whose framing of the body the engine does not reproduce.
const TRANSFER_ENCODING_HEADER: &str = "Transfer-Encoding";

/// The prefix of the names of the threads of the engine.
const THREAD_NAME_PREFIX: &str = "zato-push-";

/// The description of an internal error of a job whose payload is neither a string nor a string slice.
const UNKNOWN_INTERNAL_ERROR: &str = "Push job ended by an internal error";

/// The TLS settings of a job as Python passes them - the CA bundle, the client certificate, its key
/// and the generation of the material in those files.
type TlsTuple = (Option<String>, Option<String>, Option<String>, u64);

/// One request as Python passes it - the address, the headers, the parts of the body, the IDs of its messages
/// and whether the body is a list of envelopes.
type RequestTuple<'py> = (String, Bound<'py, PyDict>, Bound<'py, PyTuple>, Vec<String>, bool);

/// The jobs waiting for a thread, and whether the engine is stopping.
struct JobQueue {

    /// The jobs in the order they were submitted.
    jobs: VecDeque<PushJob>,

    /// Whether the engine was asked to stop, after which no job is taken.
    is_stopping: bool,
}

/// What the threads of the engine and the Python side share.
struct Shared {

    /// The jobs waiting for a thread.
    queue: Mutex<JobQueue>,

    /// Signaled when a job is submitted or the engine is stopping.
    has_work: Condvar,

    /// The outcomes of the jobs completed since the Python side last took them.
    completed: Mutex<Vec<JobOutcome>>,

    /// Written to for each completed job, so the greenlet that waits on it wakes up.
    wake: OwnedFd,

    /// How many threads are still running.
    running: Mutex<usize>,

    /// Signaled when a thread exits.
    thread_exited: Condvar,

    /// The idle connections of the engine.
    pools: EnginePools,
}

impl Shared {

    /// Waits for the next job, returning `None` once the engine is stopping.
    fn next_job(&self) -> Option<PushJob> {
        let mut queue = self.queue.lock();

        loop {
            // A stopping engine takes no job, including those still waiting
            if queue.is_stopping {
                return None;
            }

            if let Some(job) = queue.jobs.pop_front() {
                return Some(job);
            }

            // The lock is released while the thread waits for a job to be submitted
            self.has_work.wait(&mut queue);
        }
    }

    /// Adds the outcome of a job to the completed list and wakes the greenlet that takes it.
    fn complete(&self, outcome: JobOutcome) {
        self.completed.lock().push(outcome);

        // A counter at its maximum already wakes the greenlet, so a refused increment changes nothing,
        // and no other error of an eventfd write is possible for a valid descriptor
        write(&self.wake, &WAKE_INCREMENT.to_ne_bytes()).ok();
    }

    /// Records that a thread exited and wakes the caller of `stop`.
    fn on_thread_exit(&self) {
        let mut running = self.running.lock();
        *running = running.saturating_sub(1);
        self.thread_exited.notify_all();
    }

    /// Clears the wake-ups of the eventfd that arrived since the previous call.
    fn drain_wake(&self) -> Result<(), Errno> {
        let mut bytes = [0_u8; 8];

        match read(&self.wake, &mut bytes) {
            // Nothing arrived since the previous read
            Ok(_) | Err(Errno::AGAIN) => Ok(()),
            Err(errno) => Err(errno),
        }
    }
}

/// The OS threads that send the REST pushes of the pub/sub subscribers of one worker process.
#[pyclass(module = "zato_server_core", frozen)]
pub struct PushEngine {

    /// What the threads and the Python side share.
    shared: Arc<Shared>,

    /// The threads, joined when the engine stops.
    threads: Mutex<Vec<JoinHandle<()>>>,
}

#[pymethods]
impl PushEngine {

    /// Starts `thread_count` threads, which keep up to `pool_size` idle connections per endpoint.
    #[new]
    fn new(thread_count: usize, pool_size: usize) -> PyResult<Self> {
        if thread_count == 0 {
            return Err(PyValueError::new_err("A push engine needs at least one thread"));
        }

        let wake = eventfd(INITIAL_COUNT, EventfdFlags::NONBLOCK | EventfdFlags::CLOEXEC)
            .map_err(|errno| PyOSError::new_err(format!("Could not create the eventfd of the push engine: {errno}")))?;

        let shared = Arc::new(Shared {
            queue: Mutex::new(JobQueue {
                jobs: VecDeque::new(),
                is_stopping: false,
            }),
            has_work: Condvar::new(),
            completed: Mutex::new(Vec::new()),
            wake,
            running: Mutex::new(thread_count),
            thread_exited: Condvar::new(),
            pools: EnginePools::new(pool_size),
        });

        let mut threads = Vec::with_capacity(thread_count);

        for idx in 0..thread_count {
            let thread_shared = Arc::clone(&shared);
            let spawned = std::thread::Builder::new()
                .name(format!("{THREAD_NAME_PREFIX}{idx}"))
                .spawn(move || worker_loop(&thread_shared));

            match spawned {
                Ok(handle) => threads.push(handle),
                Err(err) => {
                    // The threads started so far stop, and the threads never started are not counted as running
                    stop_threads(&shared, idx);
                    return Err(PyOSError::new_err(format!("Could not start a thread of the push engine: {err}")));
                }
            }
        }

        Ok(Self {
            shared,
            threads: Mutex::new(threads),
        })
    }

    /// The descriptor that becomes readable when a job completes.
    fn fileno(&self) -> i32 {
        self.shared.wake.as_raw_fd()
    }

    /// Submits a job of one subscriber, its requests sent in order on one thread of the engine.
    ///
    /// Each request is a tuple of the address, the headers, the parts of the body, the IDs of its messages
    /// and whether the body is a JSON list of envelopes.
    #[pyo3(signature = (job_id, requests, timeout, tls))]
    fn submit(&self, job_id: u64, requests: &Bound<'_, PyList>, timeout: Option<f64>, tls: TlsTuple) -> PyResult<()> {
        let mut job_requests = Vec::with_capacity(requests.len());

        for item in requests.iter() {
            job_requests.push(extract_request(&item)?);
        }

        let (ca_path, client_cert, client_key, tls_generation) = tls;

        let job = PushJob {
            id: job_id,
            requests: job_requests,
            timeout,
            tls: TlsSettings {
                ca_path,
                client_cert,
                client_key,
            },
            tls_generation,
        };

        {
            let mut queue = self.shared.queue.lock();

            // A stopped engine sends nothing, and the caller's messages are delivered again after a restart
            if queue.is_stopping {
                return Err(PyRuntimeError::new_err("The push engine is stopped"));
            }

            queue.jobs.push_back(job);
        }

        self.shared.has_work.notify_one();
        Ok(())
    }

    /// Takes the outcomes of the jobs completed since the previous call, each a tuple of the job ID,
    /// the description of the internal error that ended the job or `None`, and the outcome of each request sent.
    fn take_completed<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        self.shared
            .drain_wake()
            .map_err(|errno| PyOSError::new_err(format!("Could not read the eventfd of the push engine: {errno}")))?;

        let completed = std::mem::take(&mut *self.shared.completed.lock());
        let out = PyList::empty(py);

        for job in completed {
            let requests = PyList::empty(py);

            for outcome in job.requests {
                requests.append(build_outcome_tuple(py, outcome)?)?;
            }

            let items: [Bound<'_, PyAny>; 3] = [
                job.id.into_pyobject(py)?.into_any(),
                job.internal_error.into_pyobject(py)?.into_any(),
                requests.into_any(),
            ];

            out.append(PyTuple::new(py, items)?)?;
        }

        Ok(out)
    }

    /// Stops the engine - no job is taken anymore, the jobs not yet taken are discarded, and the threads
    /// finish their current jobs. Returns whether all the threads exited within the timeout, in seconds.
    fn stop(&self, py: Python<'_>, timeout: f64) -> bool {
        let thread_count = self.threads.lock().len();
        let shared = Arc::clone(&self.shared);

        let wait = Duration::try_from_secs_f64(timeout).unwrap_or(Duration::ZERO);

        // The GIL is released while the threads finish, so the other interpreter threads proceed
        let is_stopped = py.detach(move || {
            request_stop(&shared);
            wait_for_threads(&shared, wait)
        });

        // Threads that exited are joined, while one still in a job past the timeout is left to end on its own
        if is_stopped {
            let threads = std::mem::take(&mut *self.threads.lock());
            for handle in threads {
                handle.join().ok();
            }
        }

        self.shared.pools.clear();

        is_stopped || thread_count == 0
    }
}

/// The loop of one thread of the engine, which runs jobs until the engine stops.
fn worker_loop(shared: &Shared) {
    while let Some(job) = shared.next_job() {
        let outcome = run_guarded(job.id, || run_job(&shared.pools, &job));
        shared.complete(outcome);
    }

    shared.on_thread_exit();
}

/// Runs a job, turning an internal error that unwinds it into the outcome of the job,
/// so the thread keeps serving the jobs after it.
fn run_guarded(id: u64, runner: impl FnOnce() -> Vec<RequestOutcome>) -> JobOutcome {
    match catch_unwind(AssertUnwindSafe(runner)) {
        Ok(requests) => JobOutcome { id, requests, internal_error: None },
        Err(payload) => {
            let message = payload
                .downcast_ref::<&str>()
                .map(|text| (*text).to_owned())
                .or_else(|| payload.downcast_ref::<String>().cloned())
                .unwrap_or_else(|| String::from(UNKNOWN_INTERNAL_ERROR));

            JobOutcome {
                id,
                requests: Vec::new(),
                internal_error: Some(message),
            }
        }
    }
}

/// Marks the engine as stopping, discards the jobs not yet taken and wakes every waiting thread.
fn request_stop(shared: &Shared) {
    {
        let mut queue = shared.queue.lock();
        queue.is_stopping = true;
        queue.jobs.clear();
    }

    shared.has_work.notify_all();
}

/// Waits until all the threads exited or the wait elapsed, returning whether they all exited.
fn wait_for_threads(shared: &Shared, wait: Duration) -> bool {
    let deadline = Instant::now().checked_add(wait).unwrap_or_else(Instant::now);
    let mut running = shared.running.lock();

    while *running > 0 {
        // A wait that reached the deadline reports whether the last thread exited just before it
        if shared.thread_exited.wait_until(&mut running, deadline).timed_out() {
            return *running == 0;
        }
    }

    true
}

/// Stops the threads that started before a thread could not be started.
fn stop_threads(shared: &Shared, started: usize) {
    *shared.running.lock() = started;
    request_stop(shared);
}

/// Extracts one request of a job from its Python tuple, validating its headers.
fn extract_request(item: &Bound<'_, PyAny>) -> PyResult<PushRequest> {
    let (url, headers, parts, msg_ids, is_list): RequestTuple<'_> = item.extract()?;

    let mut header_list = Vec::with_capacity(headers.len());

    for (key, value) in headers.iter() {
        let name = key.cast::<PyString>()?.to_str()?.to_owned();

        if !is_valid_name(&name) {
            return Err(PyValueError::new_err(format!("Invalid header name {name:?} of a push request")));
        }

        // A body framed by the caller's own transfer encoding is not what the engine sends
        if name.eq_ignore_ascii_case(TRANSFER_ENCODING_HEADER) {
            return Err(PyValueError::new_err("A push request may not set Transfer-Encoding"));
        }

        let text = value.cast::<PyString>()?.to_str()?;
        let encoded = encode_text_value(text)
            .ok_or_else(|| PyValueError::new_err(format!("Invalid value of header {name:?} of a push request")))?;

        header_list.push((name, encoded));
    }

    let mut part_list = Vec::with_capacity(parts.len());

    for part in parts.iter() {
        part_list.push(part.cast::<PyBytes>()?.as_bytes().to_vec());
    }

    Ok(PushRequest {
        url,
        headers: header_list,
        parts: part_list,
        msg_ids,
        is_list,
    })
}

/// Builds the tuple the outcome of one request is returned to Python as - the last address, the status, the reason,
/// the concluded IDs, the elapsed microseconds, the scope of the first push, the error kind, the error message
/// and the redirects followed.
fn build_outcome_tuple(py: Python<'_>, outcome: RequestOutcome) -> PyResult<Bound<'_, PyTuple>> {
    let redirects = PyList::empty(py);

    for redirect in outcome.redirects {
        redirects.append((redirect.status, redirect.from_url, redirect.to_url))?;
    }

    let (error_kind, error_message) = match outcome.error {
        Some(error) => (Some(error.kind.name()), error.message),
        None => (None, String::new()),
    };

    let items: [Bound<'_, PyAny>; 9] = [
        PyString::new(py, &outcome.url).into_any(),
        outcome.status.into_pyobject(py)?.into_any(),
        PyString::new(py, &outcome.reason).into_any(),
        PyList::new(py, outcome.concluded)?.into_any(),
        outcome.elapsed_us.into_pyobject(py)?.into_any(),
        outcome.peer_scope.map(NetworkScope::name).into_pyobject(py)?.into_any(),
        error_kind.into_pyobject(py)?.into_any(),
        PyString::new(py, &error_message).into_any(),
        redirects.into_any(),
    ];

    PyTuple::new(py, items)
}

/// Returns the address that a response to a push redirects to under the rules of the engine, or `None`
/// for a response that is not a redirect to be followed, raising `ValueError` for a redirect not followed.
#[pyfunction]
#[pyo3(signature = (url, status, location, hop_count, first_scope))]
pub fn get_push_redirect(url: &str, status: u16, location: Option<&str>, hop_count: usize, first_scope: Option<&str>) -> PyResult<Option<String>> {
    let scope = first_scope.and_then(parse_scope_name);
    next_redirect(url, status, location, hop_count, scope).map_err(PyValueError::new_err)
}

/// Parses the name of a network scope, including the link-local one.
fn parse_scope_name(name: &str) -> Option<NetworkScope> {
    let link_local = NetworkScope::LinkLocal;

    if name == link_local.name() {
        return Some(link_local);
    }

    NetworkScope::parse_required(name)
}

#[cfg(test)]
#[path = "engine_tests.rs"]
mod tests;
