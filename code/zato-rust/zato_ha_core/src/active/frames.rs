// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The frames of the log and the files of a snapshot, as the shipper reads and sends them.

use std::fs::File;
use std::io::{Error, ErrorKind, Read};
use std::os::unix::fs::FileExt;
use std::path::Path;
use std::time::Duration;

use rusqlite::Connection;

use super::{Database, SessionDatabase};
use crate::link::LinkSender;
use crate::protocol::{FileKind, Message};
use crate::state::LogPosition;
use crate::wal::{self, MAX_SCAN_BYTES, ScanOutcome, WalCursor};

/// The size of one chunk of a snapshot.
const SNAPSHOT_CHUNK_SIZE: usize = 1024 * 1024;

/// The committed frames one scan returned, in the order they were read.
#[derive(Debug, Clone)]
pub(super) struct FreshFrames {
    /// The cycle the frames belong to.
    cycle: u64,

    /// The index of the first frame.
    first_frame: u32,

    /// The index after the last frame.
    end_frame: u32,

    /// The raw frames.
    bytes: Vec<u8>,
}

/// Reads a log until no new committed frame remains, using `connection` to settle its shared-memory index.
pub(super) fn scan_to_end(cursor: &mut WalCursor, connection: &Connection) -> Result<Vec<FreshFrames>, Error> {
    let mut out = Vec::new();
    loop {
        let outcome = cursor.scan().map_err(Error::other)?;
        let cycle = cursor.cycle();
        match outcome {
            ScanOutcome::Unchanged => return Ok(out),

            // A read of the database waits for the writer that is updating the header of the index, or rebuilds
            // the index that a stopped writer left half-written, and the scan is repeated after it.
            ScanOutcome::Unsettled => {
                let _: i64 = connection
                    .query_row("select count(*) from sqlite_master", [], |row| row.get(0))
                    .map_err(Error::other)?;
            }
            ScanOutcome::Frames(frames) | ScanOutcome::Restarted { frames, .. } => out.push(FreshFrames {
                cycle,
                first_frame: frames.first_frame,
                end_frame: frames.end_frame,
                bytes: frames.bytes,
            }),
        }
    }
}

/// Returns the messages that bring the standby from `sent` towards the end of the log, at most one chunk of it,
/// and advances `sent`.
pub(super) fn frames_to_send(
    database: &Database,
    sent: &mut SessionDatabase,
    fresh: &[FreshFrames],
    generation: u64,
) -> Result<Vec<Message>, Error> {
    let mut out = Vec::new();
    let Some(header) = database.cursor.header() else {
        return Ok(out);
    };
    let end = database.end();

    // The standby holds an earlier cycle, which it holds whole, so the current one is sent from its first frame.
    let is_new_cycle = sent.header.as_deref() != Some(&header.raw[..]);
    let start = if is_new_cycle { 0 } else { sent.sent.frame };
    if !is_new_cycle && start >= end.frame {
        return Ok(out);
    }

    // One call sends at most one chunk of a long backlog, so that each iteration completes its scan for the barrier
    // without waiting for the whole backlog to be sent.
    let send_end = end.frame.min(start.saturating_add(frames_per_chunk(header)?));

    // The frames of the most recent scan are sent as they were read, and anything older is read again from the log.
    let fresh_match = fresh
        .iter()
        .find(|frames| frames.cycle == end.cycle && frames.first_frame == start && frames.end_frame == send_end);
    let chunks = match fresh_match {
        Some(frames) => vec![(frames.first_frame, frames.end_frame, frames.bytes.clone())],
        None => read_frames(&database.path, header, start, send_end)?,
    };

    let mut header_to_send = if is_new_cycle { Some(header.raw.to_vec()) } else { None };
    if chunks.is_empty() && header_to_send.is_some() {
        out.push(Message::Frames {
            generation,
            header: header_to_send.take(),
            first_frame: 0,
            end_frame: 0,
            bytes: Vec::new(),
        });
    }
    for (first_frame, end_frame, bytes) in chunks {
        out.push(Message::Frames {
            generation,
            header: header_to_send.take(),
            first_frame,
            end_frame,
            bytes,
        });
    }

    sent.header = Some(header.raw.to_vec());
    sent.sent = LogPosition {
        cycle: end.cycle,
        frame: send_end,
    };
    Ok(out)
}

/// How many frames of a log one chunk holds at most.
fn frames_per_chunk(header: &wal::WalHeader) -> Result<u32, Error> {
    let max_bytes = u64::try_from(MAX_SCAN_BYTES).map_err(Error::other)?;
    u32::try_from((max_bytes / header.frame_size()).max(1)).map_err(Error::other)
}

/// Reads the frames `start..end` of a log in chunks of a bounded size.
fn read_frames(db_path: &Path, header: &wal::WalHeader, start: u32, end: u32) -> Result<Vec<(u32, u32, Vec<u8>)>, Error> {
    let mut out = Vec::new();
    if start >= end {
        return Ok(out);
    }
    let file = File::open(wal::wal_path(db_path))?;
    let frame_size = header.frame_size();
    let frames_per_chunk = frames_per_chunk(header)?;

    let mut first = start;
    while first < end {
        let last = end.min(first.saturating_add(frames_per_chunk));
        let length = usize::try_from(u64::from(last - first) * frame_size).map_err(Error::other)?;
        let mut bytes = vec![0_u8; length];
        file.read_exact_at(&mut bytes, header.frame_offset(first))?;
        out.push((first, last, bytes));
        first = last;
    }
    Ok(out)
}

/// One file of a snapshot.
pub(super) struct SnapshotFile<'snapshot> {
    /// Which file of the database it is.
    pub(super) kind: FileKind,

    /// The path of the file.
    pub(super) path: &'snapshot Path,

    /// How many bytes from its beginning are sent, or `None` for the whole file.
    pub(super) length: Option<u64>,
}

/// Sends a file of a snapshot in chunks.
pub(super) fn send_file(sender: &LinkSender, snapshot_file: &SnapshotFile<'_>, timeout: Duration) -> Result<(), Error> {
    let file = match File::open(snapshot_file.path) {
        Ok(file) => file,

        // A file that does not exist is sent as an empty one.
        Err(error) if error.kind() == ErrorKind::NotFound => return Ok(()),
        Err(error) => return Err(error),
    };
    let mut reader: Box<dyn Read> = match snapshot_file.length {
        Some(limit) => Box::new(file.take(limit)),
        None => Box::new(file),
    };
    let mut chunk = vec![0_u8; SNAPSHOT_CHUNK_SIZE];
    loop {
        let count = reader.read(&mut chunk)?;
        if count == 0 {
            return Ok(());
        }
        let bytes = chunk.get(..count).ok_or_else(|| Error::other("read past the buffer"))?.to_vec();
        sender.send(
            &Message::SnapshotChunk {
                kind: snapshot_file.kind,
                bytes,
            },
            timeout,
        )?;
    }
}
