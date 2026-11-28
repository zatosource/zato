//! The push engine of pub/sub - OS threads that send the REST pushes of subscribers without the GIL.
//!
//! A job is the ordered requests of one subscriber. A thread of the engine sends them one after another
//! on its own keep-alive connections, follows their redirects, parses the list responses and stops
//! at the first request not fully concluded. Acknowledgements, retries and audit events stay in Python.

/// The engine class exported to Python.
mod engine;

/// The jobs and the outcomes of their requests.
mod job;

/// The redirects a push follows.
mod redirect;

/// The response to a push of several messages.
mod reply;

/// One job run on a thread of the engine.
mod run;

pub use engine::{PushEngine, get_push_redirect};
pub use redirect::MAX_PUSH_REDIRECTS;
