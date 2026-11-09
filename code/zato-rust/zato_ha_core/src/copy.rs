// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The copy of one database on the standby, built from the frames and the snapshots the active node sends.
//!
//! No `SQLite` connection is open on a copy while frames arrive, so the frames are written at their offsets
//! in its log as they are. `SQLite` opens the copy only to checkpoint it before a new cycle of the log
//! begins, and when the node takes over.

use std::fs::{File, OpenOptions};
use std::io::{Error, ErrorKind, Write};
use std::os::unix::fs::FileExt;
use std::path::{Path, PathBuf};

use rusqlite::Connection;

use crate::protocol::{FileKind, Position};
use crate::wal::{self, HEADER_SIZE, ScanOutcome, WalCursor, WalHeader};

/// The suffix of a file being received by a snapshot.
const SNAPSHOT_SUFFIX: &str = ".snapshot";

/// Returns a path with a suffix appended to its file name.
fn with_suffix(path: &Path, suffix: &str) -> PathBuf {
    let mut out = path.as_os_str().to_owned();
    out.push(suffix);
    PathBuf::from(out)
}

/// Removes a file, treating a file that does not exist as removed.
fn remove_if_exists(path: &Path) -> Result<(), Error> {
    match std::fs::remove_file(path) {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error),
    }
}

/// Syncs the directory of a path, which makes a rename or a removal in it durable.
fn sync_parent(path: &Path) -> Result<(), Error> {
    if let Some(parent) = path.parent() {
        File::open(parent)?.sync_all()?;
    }
    Ok(())
}

/// Checkpoints the log of a database into its file with `SQLite` and removes the log.
pub fn checkpoint_into_database(db_path: &Path) -> Result<(), Error> {
    // A stale index would describe frames of an earlier log, so SQLite rebuilds it from the log.
    remove_if_exists(&wal::shm_path(db_path))?;
    let connection = Connection::open(db_path).map_err(Error::other)?;
    connection.pragma_update(None, "journal_mode", "wal").map_err(Error::other)?;
    connection.pragma_update(None, "wal_checkpoint", "truncate").map_err(Error::other)?;
    connection.close().map_err(|(_, error)| Error::other(error))?;
    remove_if_exists(&wal::wal_path(db_path))?;
    remove_if_exists(&wal::shm_path(db_path))?;
    File::open(db_path)?.sync_all()?;
    sync_parent(db_path)
}

/// Checkpoints the current log of a copy, if it has one, and starts a new log with the header of the active node.
fn start_new_log(db_path: &Path, raw: &[u8], has_log: bool) -> Result<(WalHeader, File), Error> {
    let array: [u8; HEADER_SIZE] = raw.try_into().map_err(|error| Error::new(ErrorKind::InvalidData, error))?;
    let header = WalHeader::parse(array).map_err(Error::other)?;

    // The frames of the previous cycle become part of the database file before the log is replaced.
    if has_log {
        checkpoint_into_database(db_path)?;
    }

    let wal_path = wal::wal_path(db_path);
    let mut file = OpenOptions::new().create(true).write(true).truncate(true).open(&wal_path)?;
    file.write_all(raw)?;
    file.sync_all()?;
    sync_parent(&wal_path)?;
    Ok((header, file))
}

/// The copy of one database.
pub struct DatabaseCopy {
    /// The name of the database.
    pub name: String,

    /// The path of the copy.
    db_path: PathBuf,

    /// The header of the log of the copy, if it has one.
    header: Option<WalHeader>,

    /// The index after the last frame written and synced.
    end_frame: u32,

    /// The open log of the copy.
    wal_file: Option<File>,
}

impl DatabaseCopy {
    /// Opens the copy at `db_path` and finds how far its log reaches.
    pub fn open(name: &str, db_path: &Path) -> Result<Self, Error> {
        let mut out = Self {
            name: name.to_owned(),
            db_path: db_path.to_owned(),
            header: None,
            end_frame: 0,
            wal_file: None,
        };
        out.read_position()?;
        Ok(out)
    }

    /// Reads the header of the log of the copy and the end of its committed frames.
    fn read_position(&mut self) -> Result<(), Error> {
        self.header = None;
        self.end_frame = 0;
        self.wal_file = None;

        let mut cursor = WalCursor::new(wal::wal_path(&self.db_path));
        loop {
            match cursor.scan().map_err(Error::other)? {
                ScanOutcome::Unchanged => break,
                ScanOutcome::Frames(_) | ScanOutcome::Restarted { .. } => {}
            }
        }
        if let Some(header) = cursor.header() {
            self.header = Some(header.clone());
            self.end_frame = cursor.end_frame();
            self.wal_file = Some(OpenOptions::new().write(true).open(wal::wal_path(&self.db_path))?);
        }
        Ok(())
    }

    /// Returns how far the copy reaches.
    pub fn position(&self) -> Position {
        let (salt_one, salt_two) = self.header.as_ref().map_or((0, 0), |header| (header.salt_one, header.salt_two));
        Position {
            database: self.name.clone(),
            salt_one,
            salt_two,
            end_frame: self.end_frame,
        }
    }

    /// Writes committed frames at their offsets, after starting a new log if a header precedes them,
    /// and syncs them before it returns the new position.
    pub fn apply_frames(&mut self, header: Option<&[u8]>, first_frame: u32, end_frame: u32, bytes: &[u8]) -> Result<Position, Error> {
        // A new log is created on disk first, and the copy records it only once its frames are synced.
        let fresh_log = match header {
            Some(raw) => Some(start_new_log(&self.db_path, raw, self.header.is_some())?),
            None => None,
        };
        let (current_header, file, current_end) = match (&fresh_log, self.header.as_ref(), self.wal_file.as_ref()) {
            (Some((fresh_header, fresh_file)), _, _) => (fresh_header, fresh_file, 0),
            (None, Some(current_header), Some(file)) => (current_header, file, self.end_frame),
            (None, _, _) => {
                return Err(Error::new(
                    ErrorKind::InvalidData,
                    format!("frames of {} arrived before a log header", self.name),
                ));
            }
        };

        // Frames are applied strictly in order, so a gap means a batch was lost.
        if first_frame != current_end {
            return Err(Error::new(
                ErrorKind::InvalidData,
                format!(
                    "frames of {} start at {first_frame} while the copy ends at {current_end}",
                    self.name
                ),
            ));
        }

        let frame_count = u64::from(end_frame.saturating_sub(first_frame));
        let expected_length = frame_count * current_header.frame_size();
        if u64::try_from(bytes.len()).ok() != Some(expected_length) {
            return Err(Error::new(
                ErrorKind::InvalidData,
                format!("frames of {} have an unexpected length", self.name),
            ));
        }

        file.write_all_at(bytes, current_header.frame_offset(first_frame))?;
        file.sync_data()?;

        if let Some((fresh_header, fresh_file)) = fresh_log {
            self.header = Some(fresh_header);
            self.wal_file = Some(fresh_file);
        }
        self.end_frame = end_frame;
        Ok(self.position())
    }

    /// Discards the copy before the files of a snapshot arrive.
    pub fn begin_snapshot(&mut self) -> Result<(), Error> {
        for path in [self.snapshot_path(FileKind::Database), self.snapshot_path(FileKind::Wal)] {
            let _ = File::create(path)?;
        }
        self.header = None;
        self.end_frame = 0;
        self.wal_file = None;
        Ok(())
    }

    /// Returns the path under which a file of a snapshot is received.
    fn snapshot_path(&self, kind: FileKind) -> PathBuf {
        let target = match kind {
            FileKind::Database => self.db_path.clone(),
            FileKind::Wal => wal::wal_path(&self.db_path),
        };
        with_suffix(&target, SNAPSHOT_SUFFIX)
    }

    /// Appends bytes to a file of a snapshot.
    pub fn append_snapshot(&self, kind: FileKind, bytes: &[u8]) -> Result<(), Error> {
        let mut file = OpenOptions::new().append(true).open(self.snapshot_path(kind))?;
        file.write_all(bytes)
    }

    /// Syncs the received files, moves them in place of the copy and returns the new position.
    pub fn end_snapshot(&mut self) -> Result<Position, Error> {
        let pairs = [
            (self.snapshot_path(FileKind::Database), self.db_path.clone()),
            (self.snapshot_path(FileKind::Wal), wal::wal_path(&self.db_path)),
        ];
        remove_if_exists(&wal::shm_path(&self.db_path))?;
        for (received, target) in &pairs {
            File::open(received)?.sync_all()?;
            std::fs::rename(received, target)?;
        }
        sync_parent(&self.db_path)?;
        self.read_position()?;
        Ok(self.position())
    }

    /// Returns the path of the copy.
    pub fn db_path(&self) -> &Path {
        &self.db_path
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Opens a database in WAL mode with checkpoints left to the caller.
    fn open(path: &Path) -> Connection {
        let connection = Connection::open(path).unwrap();
        connection.pragma_update(None, "journal_mode", "wal").unwrap();
        connection.pragma_update(None, "wal_autocheckpoint", 0).unwrap();
        connection
    }

    /// Ships every new frame of `cursor` to `copy`.
    fn ship(cursor: &mut WalCursor, copy: &mut DatabaseCopy) {
        loop {
            match cursor.scan().unwrap() {
                ScanOutcome::Unchanged => break,
                ScanOutcome::Frames(frames) => {
                    let _ = copy
                        .apply_frames(None, frames.first_frame, frames.end_frame, &frames.bytes)
                        .unwrap();
                }
                ScanOutcome::Restarted { header, frames } => {
                    let _ = copy
                        .apply_frames(Some(&header), frames.first_frame, frames.end_frame, &frames.bytes)
                        .unwrap();
                }
            }
        }
    }

    /// Returns the values of the `item` table of a database.
    fn values(path: &Path) -> Vec<String> {
        let connection = Connection::open(path).unwrap();
        let mut statement = connection.prepare("select value from item order by rowid").unwrap();
        statement.query_map([], |row| row.get(0)).unwrap().map(Result::unwrap).collect()
    }

    #[test]
    fn the_copy_holds_every_shipped_commit_across_restarts() {
        let source_dir = tempfile::tempdir().unwrap();
        let copy_dir = tempfile::tempdir().unwrap();
        let source_path = source_dir.path().join("pubsub.db");
        let copy_path = copy_dir.path().join("pubsub.db");

        // A copy begins with the database file, as a snapshot delivers it.
        let source = open(&source_path);
        let _ = std::fs::copy(&source_path, &copy_path).unwrap();
        let mut cursor = WalCursor::new(wal::wal_path(&source_path));
        let mut copy = DatabaseCopy::open("pubsub", &copy_path).unwrap();

        source
            .execute_batch("create table item (value text); insert into item values ('one');")
            .unwrap();
        ship(&mut cursor, &mut copy);

        source.pragma_update(None, "wal_checkpoint", "passive").unwrap();
        source.execute_batch("insert into item values ('two');").unwrap();
        ship(&mut cursor, &mut copy);

        source.execute_batch("insert into item values ('three');").unwrap();
        ship(&mut cursor, &mut copy);

        // SQLite reads the copy as the active node would after a takeover.
        assert_eq!(values(&copy_path), vec!["one", "two", "three"]);
    }

    #[test]
    fn a_gap_is_refused() {
        let source_dir = tempfile::tempdir().unwrap();
        let copy_dir = tempfile::tempdir().unwrap();
        let source_path = source_dir.path().join("pubsub.db");
        let source = open(&source_path);
        source
            .execute_batch("create table item (value text); insert into item values ('one');")
            .unwrap();
        source.execute_batch("insert into item values ('two');").unwrap();

        let mut cursor = WalCursor::new(wal::wal_path(&source_path));
        let ScanOutcome::Restarted { header, frames } = cursor.scan().unwrap() else {
            panic!("expected a new log")
        };
        let mut copy = DatabaseCopy::open("pubsub", &copy_dir.path().join("pubsub.db")).unwrap();
        let _ = copy.apply_frames(Some(&header), 0, 0, &[]).unwrap();
        let error = copy
            .apply_frames(None, 1, frames.end_frame, frames.bytes.get(4120..).unwrap_or_default())
            .unwrap_err();
        assert_eq!(error.kind(), ErrorKind::InvalidData);
    }
}
