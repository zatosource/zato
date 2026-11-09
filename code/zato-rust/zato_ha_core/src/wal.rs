// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! Reading of the `SQLite` write-ahead log.
//!
//! The format is described at <https://www.sqlite.org/fileformat2.html#walformat>. The log begins with
//! a 32-byte header, and each frame is a 24-byte header followed by one page. A frame is valid when its
//! salts equal those of the header and its checksum continues the chain of the frames before it, and
//! a frame whose database size field is not zero ends a transaction.

use std::fs::File;
use std::io::{ErrorKind, Read, Seek, SeekFrom};
use std::path::{Path, PathBuf};

/// The size of the header of the log.
pub const HEADER_SIZE: usize = 32;

/// The size of the header of a frame.
pub const FRAME_HEADER_SIZE: usize = 24;

/// The size of the header of the log, as a file length.
const HEADER_LENGTH: u64 = 32;

/// The size of the header of a frame, as a file length.
const FRAME_HEADER_LENGTH: u64 = 24;

/// The magic number of a log whose checksums use little-endian words.
const MAGIC_LITTLE_ENDIAN: u32 = 0x377f_0682;

/// The magic number of a log whose checksums use big-endian words.
const MAGIC_BIG_ENDIAN: u32 = 0x377f_0683;

/// The page size field value that stands for 65536 bytes.
const PAGE_SIZE_65536_MARKER: u32 = 1;

/// The page size that [`PAGE_SIZE_65536_MARKER`] stands for.
const PAGE_SIZE_65536: u32 = 65_536;

/// How many bytes of the header the header checksum covers.
const HEADER_CHECKSUM_COVERS: usize = 24;

/// How many bytes of a frame header the frame checksum covers.
const FRAME_HEADER_CHECKSUM_COVERS: usize = 8;

/// How many bytes of committed frames one scan returns at most.
pub const MAX_SCAN_BYTES: usize = 8 * 1024 * 1024;

/// The suffix `SQLite` appends to the database path to name the log.
const WAL_SUFFIX: &str = "-wal";

/// The suffix `SQLite` appends to the database path to name the shared-memory index.
const SHM_SUFFIX: &str = "-shm";

/// Errors of reading the log.
#[derive(Debug)]
pub enum WalError {
    /// The file could not be read.
    Read(std::io::Error),

    /// The header is not a valid header of a log.
    InvalidHeader(&'static str),
}

impl std::fmt::Display for WalError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Read(error) => write!(formatter, "WAL I/O error: {error}"),
            Self::InvalidHeader(reason) => write!(formatter, "Invalid WAL header: {reason}"),
        }
    }
}

impl std::error::Error for WalError {}

impl From<std::io::Error> for WalError {
    fn from(error: std::io::Error) -> Self {
        Self::Read(error)
    }
}

/// Returns the path of the log of a database.
pub fn wal_path(db_path: &Path) -> PathBuf {
    with_suffix(db_path, WAL_SUFFIX)
}

/// Returns the path of the shared-memory index of a database.
pub fn shm_path(db_path: &Path) -> PathBuf {
    with_suffix(db_path, SHM_SUFFIX)
}

/// Returns a path with a suffix appended to its file name.
fn with_suffix(path: &Path, suffix: &str) -> PathBuf {
    let mut out = path.as_os_str().to_owned();
    out.push(suffix);
    PathBuf::from(out)
}

/// Reads a 32-bit big-endian integer at an offset.
fn read_u32(bytes: &[u8], offset: usize) -> Option<u32> {
    let end = offset.checked_add(4)?;
    let slice = bytes.get(offset..end)?;
    let array: [u8; 4] = slice.try_into().ok()?;
    Some(u32::from_be_bytes(array))
}

/// A running checksum of the log.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Checksum {
    /// The first word.
    pub first: u32,

    /// The second word.
    pub second: u32,
}

impl Checksum {
    /// Continues the checksum over `bytes`, whose length is a multiple of 8, in the byte order of the log.
    #[must_use]
    pub fn update(self, bytes: &[u8], big_endian: bool) -> Self {
        let mut first = self.first;
        let mut second = self.second;
        for pair in bytes.chunks_exact(8) {
            let (Some(word_one), Some(word_two)) = (pair.get(..4), pair.get(4..)) else {
                continue;
            };
            let (Ok(array_one), Ok(array_two)) = (<[u8; 4]>::try_from(word_one), <[u8; 4]>::try_from(word_two)) else {
                continue;
            };
            let (value_one, value_two) = if big_endian {
                (u32::from_be_bytes(array_one), u32::from_be_bytes(array_two))
            } else {
                (u32::from_le_bytes(array_one), u32::from_le_bytes(array_two))
            };

            // The two words feed each other, as in walChecksumBytes of SQLite.
            first = first.wrapping_add(value_one).wrapping_add(second);
            second = second.wrapping_add(value_two).wrapping_add(first);
        }
        Self { first, second }
    }
}

/// The header of a log.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WalHeader {
    /// The raw bytes, shipped as they are.
    pub raw: [u8; HEADER_SIZE],

    /// Whether checksums use big-endian words.
    pub big_endian: bool,

    /// The page size in bytes.
    pub page_size: u32,

    /// The first salt, which changes on every restart of the log.
    pub salt_one: u32,

    /// The second salt.
    pub salt_two: u32,

    /// The checksum of the header, from which the chain of the first frame continues.
    pub checksum: Checksum,
}

impl WalHeader {
    /// Parses and verifies a header.
    pub fn parse(raw: [u8; HEADER_SIZE]) -> Result<Self, WalError> {
        let field = |offset: usize| read_u32(&raw, offset).ok_or(WalError::InvalidHeader("short header"));

        let magic = field(0)?;
        let big_endian = match magic {
            MAGIC_LITTLE_ENDIAN => false,
            MAGIC_BIG_ENDIAN => true,
            _ => return Err(WalError::InvalidHeader("magic number")),
        };

        let page_size = match field(8)? {
            PAGE_SIZE_65536_MARKER => PAGE_SIZE_65536,
            size => size,
        };
        if !page_size.is_power_of_two() || page_size < 512 {
            return Err(WalError::InvalidHeader("page size"));
        }

        let checksum = Checksum {
            first: field(24)?,
            second: field(28)?,
        };
        let covered = raw.get(..HEADER_CHECKSUM_COVERS).ok_or(WalError::InvalidHeader("short header"))?;
        if Checksum::default().update(covered, big_endian) != checksum {
            return Err(WalError::InvalidHeader("checksum"));
        }

        Ok(Self {
            raw,
            big_endian,
            page_size,
            salt_one: field(16)?,
            salt_two: field(20)?,
            checksum,
        })
    }

    /// Returns the size of one frame, header included.
    pub fn frame_size(&self) -> u64 {
        u64::from(self.page_size) + FRAME_HEADER_LENGTH
    }

    /// Returns the offset of the frame with a zero-based index.
    pub fn frame_offset(&self, index: u32) -> u64 {
        HEADER_LENGTH + u64::from(index) * self.frame_size()
    }

    /// Whether a frame belongs to this log, judged by its salts.
    fn has_salts_of(&self, frame: &[u8]) -> bool {
        read_u32(frame, 8) == Some(self.salt_one) && read_u32(frame, 12) == Some(self.salt_two)
    }
}

/// Verifies one frame against the running checksum, returning the new checksum and whether the frame
/// ends a transaction, or `None` if the frame is not valid.
pub fn verify_frame(header: &WalHeader, frame: &[u8], previous: Checksum) -> Option<(Checksum, bool)> {
    if !header.has_salts_of(frame) {
        return None;
    }
    let covered_header = frame.get(..FRAME_HEADER_CHECKSUM_COVERS)?;
    let page = frame.get(FRAME_HEADER_SIZE..)?;
    let checksum = previous.update(covered_header, header.big_endian).update(page, header.big_endian);
    let stored = Checksum {
        first: read_u32(frame, 16)?,
        second: read_u32(frame, 20)?,
    };
    if checksum != stored {
        return None;
    }
    let is_commit = read_u32(frame, 4)? != 0;
    Some((checksum, is_commit))
}

/// The frames read by one scan, up to the last commit frame.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ScannedFrames {
    /// The index of the first frame.
    pub first_frame: u32,

    /// The raw frames, headers included.
    pub bytes: Vec<u8>,

    /// The index after the last commit frame.
    pub end_frame: u32,
}

/// The state of reading one log, kept between scans.
#[derive(Debug, Clone)]
pub struct WalCursor {
    /// The path of the log.
    path: PathBuf,

    /// The header of the current cycle of the log, once one was read.
    header: Option<WalHeader>,

    /// The number of the current cycle, raised on every restart of the log.
    cycle: u64,

    /// The index after the last commit frame read.
    end_frame: u32,

    /// The checksum after the last commit frame read.
    checksum: Checksum,
}

/// What a scan found.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ScanOutcome {
    /// No new committed frame.
    Unchanged,

    /// New committed frames of the current cycle.
    Frames(ScannedFrames),

    /// The log restarted with a new header, and the frames of the new cycle follow.
    Restarted {
        /// The new header.
        header: Vec<u8>,

        /// The committed frames of the new cycle.
        frames: ScannedFrames,
    },
}

impl WalCursor {
    /// Returns a cursor that has read nothing yet.
    pub const fn new(path: PathBuf) -> Self {
        Self {
            path,
            header: None,
            cycle: 0,
            end_frame: 0,
            checksum: Checksum { first: 0, second: 0 },
        }
    }

    /// Returns the current cycle number.
    pub const fn cycle(&self) -> u64 {
        self.cycle
    }

    /// Returns the index after the last commit frame read.
    pub const fn end_frame(&self) -> u32 {
        self.end_frame
    }

    /// Returns the header of the current cycle.
    pub const fn header(&self) -> Option<&WalHeader> {
        self.header.as_ref()
    }

    /// Reads the committed frames appended since the previous scan.
    pub fn scan(&mut self) -> Result<ScanOutcome, WalError> {
        let mut file = match File::open(&self.path) {
            Ok(file) => file,

            // A log that does not exist yet holds no frame.
            Err(error) if error.kind() == ErrorKind::NotFound => return Ok(ScanOutcome::Unchanged),
            Err(error) => return Err(WalError::Read(error)),
        };

        let mut raw = [0_u8; HEADER_SIZE];
        match file.read_exact(&mut raw) {
            Ok(()) => {}

            // A log shorter than its header has not been written to yet.
            Err(error) if error.kind() == ErrorKind::UnexpectedEof => return Ok(ScanOutcome::Unchanged),
            Err(error) => return Err(WalError::Read(error)),
        }

        // A header being rewritten by a restart fails its checksum, and the next scan reads it whole.
        let Ok(on_disk) = WalHeader::parse(raw) else {
            return Ok(ScanOutcome::Unchanged);
        };

        // The cursor is advanced only after every read succeeded, so a failed scan leaves it where it was.
        let is_new_cycle = self.header.as_ref().is_none_or(|current| current.raw != on_disk.raw);
        let (first_frame, first_checksum) = if is_new_cycle {
            (0, on_disk.checksum)
        } else {
            (self.end_frame, self.checksum)
        };
        let (frames, checksum) = read_frames(&mut file, &on_disk, first_frame, first_checksum)?;
        self.end_frame = frames.end_frame;
        self.checksum = checksum;

        if is_new_cycle {
            if self.header.is_some() {
                self.cycle += 1;
            }
            let header = on_disk.raw.to_vec();
            self.header = Some(on_disk);
            return Ok(ScanOutcome::Restarted { header, frames });
        }

        if frames.bytes.is_empty() {
            return Ok(ScanOutcome::Unchanged);
        }
        Ok(ScanOutcome::Frames(frames))
    }
}

/// Reads the valid frames from `first_frame` on and returns the committed ones
/// with the running checksum after the last commit frame among them.
fn read_frames(
    file: &mut File,
    header: &WalHeader,
    first_frame: u32,
    first_checksum: Checksum,
) -> Result<(ScannedFrames, Checksum), WalError> {
    let _ = file.seek(SeekFrom::Start(header.frame_offset(first_frame)))?;

    let frame_size = usize::try_from(header.frame_size()).map_err(|error| WalError::Read(std::io::Error::other(error)))?;
    let mut frame = vec![0_u8; frame_size];
    let mut bytes = Vec::new();
    let mut committed_length = 0_usize;
    let mut committed_end = first_frame;
    let mut committed_checksum = first_checksum;
    let mut checksum = first_checksum;
    let mut index = first_frame;

    loop {
        match file.read_exact(&mut frame) {
            Ok(()) => {}

            // The end of the file, or a frame not fully written yet.
            Err(error) if error.kind() == ErrorKind::UnexpectedEof => break,
            Err(error) => return Err(WalError::Read(error)),
        }

        // An invalid frame is one the writer has not finished, or one left over from an earlier cycle.
        let Some((next_checksum, is_commit)) = verify_frame(header, &frame, checksum) else {
            break;
        };
        checksum = next_checksum;
        index += 1;
        bytes.extend_from_slice(&frame);

        // Only whole transactions are shipped, since frames after the last commit may still be rewritten.
        if is_commit {
            committed_length = bytes.len();
            committed_end = index;
            committed_checksum = checksum;

            // A long log is read over several scans, so that one message stays bounded.
            if committed_length >= MAX_SCAN_BYTES {
                break;
            }
        }
    }

    bytes.truncate(committed_length);
    let frames = ScannedFrames {
        first_frame,
        bytes,
        end_frame: committed_end,
    };
    Ok((frames, committed_checksum))
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    /// Opens a database in WAL mode with checkpoints left to the caller.
    fn open(path: &Path) -> Connection {
        let connection = Connection::open(path).unwrap();
        connection.pragma_update(None, "journal_mode", "wal").unwrap();
        connection.pragma_update(None, "wal_autocheckpoint", 0).unwrap();
        connection
    }

    #[test]
    fn reads_committed_frames_only_once() {
        let dir = tempfile::tempdir().unwrap();
        let db_path = dir.path().join("test.db");
        let connection = open(&db_path);
        connection
            .execute_batch("create table item (value text); insert into item values ('one');")
            .unwrap();

        let mut cursor = WalCursor::new(wal_path(&db_path));
        let ScanOutcome::Restarted { frames, .. } = cursor.scan().unwrap() else {
            panic!("expected a new cycle")
        };
        assert!(frames.end_frame > 0);
        assert_eq!(cursor.scan().unwrap(), ScanOutcome::Unchanged);

        connection.execute_batch("insert into item values ('two');").unwrap();
        let ScanOutcome::Frames(next) = cursor.scan().unwrap() else {
            panic!("expected frames")
        };
        assert_eq!(next.first_frame, frames.end_frame);
        assert!(next.end_frame > next.first_frame);
    }

    #[test]
    fn a_restart_starts_a_new_cycle() {
        let dir = tempfile::tempdir().unwrap();
        let db_path = dir.path().join("test.db");
        let connection = open(&db_path);
        connection
            .execute_batch("create table item (value text); insert into item values ('one');")
            .unwrap();

        let mut cursor = WalCursor::new(wal_path(&db_path));
        let _ = cursor.scan().unwrap();
        connection.pragma_update(None, "wal_checkpoint", "passive").unwrap();
        connection.execute_batch("insert into item values ('two');").unwrap();

        let outcome = cursor.scan().unwrap();
        assert!(matches!(outcome, ScanOutcome::Restarted { .. }));
        assert_eq!(cursor.cycle(), 1);
    }

    #[test]
    fn an_uncommitted_frame_is_not_read() {
        let dir = tempfile::tempdir().unwrap();
        let db_path = dir.path().join("test.db");
        let connection = open(&db_path);
        connection.execute_batch("create table item (value text);").unwrap();

        let mut cursor = WalCursor::new(wal_path(&db_path));
        let _ = cursor.scan().unwrap();
        let end_before = cursor.end_frame();

        // A large transaction that spills pages to the log before it commits.
        connection.pragma_update(None, "cache_size", 1).unwrap();
        connection
            .execute_batch(
                "begin; with recursive series(value) as (select 1 union all select value + 1 from series where value < 50) \
                 insert into item select randomblob(4000) from series;",
            )
            .unwrap();
        assert_eq!(cursor.scan().unwrap(), ScanOutcome::Unchanged);
        assert_eq!(cursor.end_frame(), end_before);

        connection.execute_batch("commit;").unwrap();
        assert!(matches!(cursor.scan().unwrap(), ScanOutcome::Frames(_)));
    }
}
