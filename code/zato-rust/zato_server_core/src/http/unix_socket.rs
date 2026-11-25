//! Unix domain socket listener of the HTTP server.
//!
//! Binds the socket file with the owner-only mode, after removing a socket file that a previous process left
//! at the same path, and removes the socket file when the server stops.

use parking_lot::Mutex;
use pyo3::exceptions::PyOSError;
use pyo3::prelude::*;
use socket2::{Domain, SockAddr, Socket, Type};
use std::fs::{Metadata, Permissions};
use std::io::ErrorKind;
use std::os::fd::IntoRawFd;
use std::os::unix::fs::{FileTypeExt, MetadataExt, PermissionsExt};
use std::path::{Path, PathBuf};

use super::{LISTEN_BACKLOG, UNIX_SOCKET_MODE};

/// Identity of the socket file that this process bound.
///
/// A socket file that another process binds later under the same path has a different identity.
#[derive(PartialEq, Eq)]
struct SocketFileIdentity {
    /// Device ID of the filesystem that holds the socket file.
    device: u64,

    /// Inode number of the socket file.
    inode: u64,

    /// Seconds part of the last status change time of the socket file.
    changed_secs: i64,

    /// Nanoseconds part of the last status change time of the socket file.
    changed_nanos: i64,
}

impl SocketFileIdentity {
    /// Reads the identity of a socket file from its metadata.
    fn from_metadata(metadata: &Metadata) -> Self {
        Self {
            device: metadata.dev(),
            inode: metadata.ino(),
            changed_secs: metadata.ctime(),
            changed_nanos: metadata.ctime_nsec(),
        }
    }
}

/// Socket file that the Unix listener of this process bound, together with its identity.
struct BoundSocketFile {
    /// Filesystem path of the socket file.
    path: PathBuf,

    /// Identity of the socket file at the time this process bound it.
    identity: SocketFileIdentity,
}

/// Socket file of the Unix listener of this process, removed when the server stops.
static BOUND_SOCKET_FILE: Mutex<Option<BoundSocketFile>> = Mutex::new(None);

/// Builds the Python error of a filesystem or socket operation on the socket path.
fn path_error(operation: &str, path: &Path, err: &std::io::Error) -> PyErr {
    PyOSError::new_err(format!("{operation} of Unix socket {} failed: {err}", path.display()))
}

/// Removes a socket file that a previous process left at the path.
///
/// Anything other than a socket file stays in place, and the bind that follows reports the path as in use.
fn remove_stale_socket_file(path: &Path) -> PyResult<()> {
    let metadata = match std::fs::symlink_metadata(path) {
        Ok(metadata) => metadata,

        // A path with nothing at it is ready for the bind
        Err(err) if err.kind() == ErrorKind::NotFound => return Ok(()),
        Err(err) => return Err(path_error("stat", path, &err)),
    };

    if metadata.file_type().is_socket() {
        std::fs::remove_file(path).map_err(|err| path_error("removal of stale socket file", path, &err))?;
    }

    Ok(())
}

/// Sets the owner-only mode on the bound socket file, records its identity and starts listening.
fn finish_bound_socket(socket: &Socket, path: &Path) -> PyResult<()> {
    // The mode is in place before listen, so no client connects while the file has the mode of the umask
    let permissions = Permissions::from_mode(UNIX_SOCKET_MODE);
    std::fs::set_permissions(path, permissions).map_err(|err| path_error("chmod", path, &err))?;

    // The identity is read after the chmod, which changes the status change time of the file
    let metadata = std::fs::symlink_metadata(path).map_err(|err| path_error("stat", path, &err))?;
    let bound = BoundSocketFile {
        path: path.to_path_buf(),
        identity: SocketFileIdentity::from_metadata(&metadata),
    };
    *BOUND_SOCKET_FILE.lock() = Some(bound);

    socket.listen(LISTEN_BACKLOG).map_err(|err| path_error("listen", path, &err))
}

/// Creates a non-blocking, `CLOEXEC` Unix domain socket listener bound to `path` and returns its file descriptor.
pub(super) fn create_unix_listen_socket(path: &str) -> PyResult<i32> {
    let socket_path = Path::new(path);
    remove_stale_socket_file(socket_path)?;

    let address = SockAddr::unix(socket_path).map_err(|err| path_error("address", socket_path, &err))?;

    // socket2 sets CLOEXEC on every socket it creates
    let socket = Socket::new(Domain::UNIX, Type::STREAM, None).map_err(|err| path_error("socket", socket_path, &err))?;
    socket
        .set_nonblocking(true)
        .map_err(|err| path_error("O_NONBLOCK", socket_path, &err))?;
    socket.bind(&address).map_err(|err| path_error("bind", socket_path, &err))?;

    // A socket file that was bound but cannot listen is removed, the socket itself closes when it is dropped
    if let Err(err) = finish_bound_socket(&socket, socket_path) {
        remove_bound_socket_file();
        return Err(err);
    }

    Ok(socket.into_raw_fd())
}

/// Removes the socket file that the Unix listener of this process bound, once.
///
/// The file stays in place when the path refers by now to a socket file that another process bound.
pub(super) fn remove_bound_socket_file() {
    // The lock is held only to take the record, so a second stop finds nothing to remove
    let taken_file = BOUND_SOCKET_FILE.lock().take();

    let Some(bound) = taken_file else {
        return;
    };

    match std::fs::symlink_metadata(&bound.path) {
        Ok(metadata) if SocketFileIdentity::from_metadata(&metadata) == bound.identity => {
            if let Err(err) = std::fs::remove_file(&bound.path) {
                log::warn!("Could not remove Unix socket file {}: {err}", bound.path.display());
            }
        }

        // The path refers to a socket file of another process, which stays in place
        Ok(_) => {}

        // Another process removed the file already
        Err(err) if err.kind() == ErrorKind::NotFound => {}
        Err(err) => log::warn!("Could not stat Unix socket file {}: {err}", bound.path.display()),
    }
}
