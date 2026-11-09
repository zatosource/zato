// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The messages of the replication link and their binary encoding.
//!
//! Each message is a 32-bit big-endian length followed by that many bytes, of which the first is the kind
//! of the message. Integers are big-endian, and byte strings and text are prefixed with a 32-bit length.

use std::io::{Error, ErrorKind};

/// The largest message accepted, which bounds the memory a peer can make the node allocate.
pub const MAX_MESSAGE_SIZE: u32 = 64 * 1024 * 1024;

/// The kind byte of [`Message::Hello`].
const KIND_HELLO: u8 = 1;

/// The kind byte of [`Message::HelloReply`].
const KIND_HELLO_REPLY: u8 = 2;

/// The kind byte of [`Message::Refused`].
const KIND_REFUSED: u8 = 3;

/// The kind byte of [`Message::Heartbeat`].
const KIND_HEARTBEAT: u8 = 4;

/// The kind byte of [`Message::HeartbeatAck`].
const KIND_HEARTBEAT_ACK: u8 = 5;

/// The kind byte of [`Message::Frames`].
const KIND_FRAMES: u8 = 6;

/// The kind byte of [`Message::Confirm`].
const KIND_CONFIRM: u8 = 7;

/// The kind byte of [`Message::SnapshotBegin`].
const KIND_SNAPSHOT_BEGIN: u8 = 8;

/// The kind byte of [`Message::SnapshotChunk`].
const KIND_SNAPSHOT_CHUNK: u8 = 9;

/// The kind byte of [`Message::SnapshotEnd`].
const KIND_SNAPSHOT_END: u8 = 10;

/// The kind byte of [`Message::Admit`].
const KIND_ADMIT: u8 = 11;

/// The file kind byte of the database file.
const FILE_DATABASE: u8 = 1;

/// The file kind byte of the log.
const FILE_WAL: u8 = 2;

/// Which file of a database a snapshot chunk belongs to.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FileKind {
    /// The database file.
    Database,

    /// The write-ahead log.
    Wal,
}

/// How far the standby holds the log of one database.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Position {
    /// The name of the database.
    pub database: String,

    /// The first salt of the log the standby holds.
    pub salt_one: u32,

    /// The second salt of the log the standby holds.
    pub salt_two: u32,

    /// The index after the last frame the standby synced.
    pub end_frame: u32,
}

/// A message of the replication link.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Message {
    /// The active node opens the link.
    Hello {
        /// The generation of the active node.
        generation: u64,

        /// The name of the active node.
        active_node: String,
    },

    /// The standby answers [`Message::Hello`].
    HelloReply {
        /// Whether the standby is in sync at this generation and can resume from its positions.
        in_sync: bool,

        /// The positions of the standby, if it is in sync.
        positions: Vec<Position>,
    },

    /// The peer holds a higher generation, so the sender was replaced.
    Refused {
        /// The generation of the peer.
        generation: u64,
    },

    /// The active node is alive.
    Heartbeat {
        /// The generation of the active node.
        generation: u64,
    },

    /// The standby is alive.
    HeartbeatAck,

    /// Committed frames of one database.
    Frames {
        /// The generation of the active node.
        generation: u64,

        /// The name of the database.
        database: String,

        /// The header of a new log, which precedes its first frames.
        header: Option<Vec<u8>>,

        /// The index of the first frame.
        first_frame: u32,

        /// The index after the last frame.
        end_frame: u32,

        /// The raw frames.
        bytes: Vec<u8>,
    },

    /// The standby synced the frames of a database up to a position.
    Confirm(Position),

    /// The files of a database follow, replacing the copy of the standby.
    SnapshotBegin {
        /// The generation of the active node.
        generation: u64,

        /// The name of the database.
        database: String,
    },

    /// Bytes appended to a file of a database being replaced.
    SnapshotChunk {
        /// The name of the database.
        database: String,

        /// The file.
        kind: FileKind,

        /// The bytes.
        bytes: Vec<u8>,
    },

    /// The files of a database are complete.
    SnapshotEnd {
        /// The name of the database.
        database: String,
    },

    /// The referee accepted the standby as in sync at a new generation.
    Admit {
        /// The new generation.
        generation: u64,
    },
}

/// Builds the body of a message.
#[derive(Default)]
struct Encoder {
    /// The bytes written so far.
    bytes: Vec<u8>,
}

impl Encoder {
    /// Appends a byte.
    fn byte(&mut self, value: u8) {
        self.bytes.push(value);
    }

    /// Appends a 32-bit integer.
    fn u32(&mut self, value: u32) {
        self.bytes.extend_from_slice(&value.to_be_bytes());
    }

    /// Appends a 64-bit integer.
    fn u64(&mut self, value: u64) {
        self.bytes.extend_from_slice(&value.to_be_bytes());
    }

    /// Appends a byte string with its length.
    fn blob(&mut self, value: &[u8]) -> Result<(), Error> {
        let length = u32::try_from(value.len()).map_err(|error| Error::new(ErrorKind::InvalidInput, error))?;
        self.u32(length);
        self.bytes.extend_from_slice(value);
        Ok(())
    }

    /// Appends a text with its length.
    fn text(&mut self, value: &str) -> Result<(), Error> {
        self.blob(value.as_bytes())
    }

    /// Appends a position.
    fn position(&mut self, position: &Position) -> Result<(), Error> {
        self.text(&position.database)?;
        self.u32(position.salt_one);
        self.u32(position.salt_two);
        self.u32(position.end_frame);
        Ok(())
    }
}

/// Reads the body of a message.
struct Decoder<'body> {
    /// The bytes not read yet.
    rest: &'body [u8],
}

/// Returns the error of a message that ends before its fields do.
fn truncated() -> Error {
    Error::new(ErrorKind::InvalidData, "truncated message")
}

impl<'body> Decoder<'body> {
    /// Takes the next `count` bytes.
    fn take(&mut self, count: usize) -> Result<&'body [u8], Error> {
        if self.rest.len() < count {
            return Err(truncated());
        }
        let (head, tail) = self.rest.split_at(count);
        self.rest = tail;
        Ok(head)
    }

    /// Reads a byte.
    fn byte(&mut self) -> Result<u8, Error> {
        self.take(1)?.first().copied().ok_or_else(truncated)
    }

    /// Reads a 32-bit integer.
    fn u32(&mut self) -> Result<u32, Error> {
        let array: [u8; 4] = self
            .take(4)?
            .try_into()
            .map_err(|error| Error::new(ErrorKind::InvalidData, error))?;
        Ok(u32::from_be_bytes(array))
    }

    /// Reads a 64-bit integer.
    fn u64(&mut self) -> Result<u64, Error> {
        let array: [u8; 8] = self
            .take(8)?
            .try_into()
            .map_err(|error| Error::new(ErrorKind::InvalidData, error))?;
        Ok(u64::from_be_bytes(array))
    }

    /// Reads a byte string.
    fn blob(&mut self) -> Result<Vec<u8>, Error> {
        let length = usize::try_from(self.u32()?).map_err(|error| Error::new(ErrorKind::InvalidData, error))?;
        Ok(self.take(length)?.to_vec())
    }

    /// Reads a text.
    fn text(&mut self) -> Result<String, Error> {
        String::from_utf8(self.blob()?).map_err(|error| Error::new(ErrorKind::InvalidData, error))
    }

    /// Reads a position.
    fn position(&mut self) -> Result<Position, Error> {
        Ok(Position {
            database: self.text()?,
            salt_one: self.u32()?,
            salt_two: self.u32()?,
            end_frame: self.u32()?,
        })
    }
}

/// Encodes the body of a message.
fn encode(message: &Message) -> Result<Vec<u8>, Error> {
    let mut out = Encoder::default();
    match message {
        Message::Hello { generation, active_node } => {
            out.byte(KIND_HELLO);
            out.u64(*generation);
            out.text(active_node)?;
        }
        Message::HelloReply { in_sync, positions } => {
            out.byte(KIND_HELLO_REPLY);
            out.byte(u8::from(*in_sync));
            let count = u32::try_from(positions.len()).map_err(|error| Error::new(ErrorKind::InvalidInput, error))?;
            out.u32(count);
            for position in positions {
                out.position(position)?;
            }
        }
        Message::Refused { generation } => {
            out.byte(KIND_REFUSED);
            out.u64(*generation);
        }
        Message::Heartbeat { generation } => {
            out.byte(KIND_HEARTBEAT);
            out.u64(*generation);
        }
        Message::HeartbeatAck => out.byte(KIND_HEARTBEAT_ACK),
        Message::Frames {
            generation,
            database,
            header,
            first_frame,
            end_frame,
            bytes,
        } => {
            out.byte(KIND_FRAMES);
            out.u64(*generation);
            out.text(database)?;
            out.blob(header.as_deref().unwrap_or_default())?;
            out.u32(*first_frame);
            out.u32(*end_frame);
            out.blob(bytes)?;
        }
        Message::Confirm(position) => {
            out.byte(KIND_CONFIRM);
            out.position(position)?;
        }
        Message::SnapshotBegin { generation, database } => {
            out.byte(KIND_SNAPSHOT_BEGIN);
            out.u64(*generation);
            out.text(database)?;
        }
        Message::SnapshotChunk { database, kind, bytes } => {
            out.byte(KIND_SNAPSHOT_CHUNK);
            out.text(database)?;
            out.byte(match kind {
                FileKind::Database => FILE_DATABASE,
                FileKind::Wal => FILE_WAL,
            });
            out.blob(bytes)?;
        }
        Message::SnapshotEnd { database } => {
            out.byte(KIND_SNAPSHOT_END);
            out.text(database)?;
        }
        Message::Admit { generation } => {
            out.byte(KIND_ADMIT);
            out.u64(*generation);
        }
    }
    Ok(out.bytes)
}

/// Decodes the body of a message.
fn decode(body: &[u8]) -> Result<Message, Error> {
    let mut input = Decoder { rest: body };
    let out = match input.byte()? {
        KIND_HELLO => Message::Hello {
            generation: input.u64()?,
            active_node: input.text()?,
        },
        KIND_HELLO_REPLY => {
            let in_sync = input.byte()? != 0;
            let count = input.u32()?;
            let mut positions = Vec::new();
            for _ in 0..count {
                positions.push(input.position()?);
            }
            Message::HelloReply { in_sync, positions }
        }
        KIND_REFUSED => Message::Refused { generation: input.u64()? },
        KIND_HEARTBEAT => Message::Heartbeat { generation: input.u64()? },
        KIND_HEARTBEAT_ACK => Message::HeartbeatAck,
        KIND_FRAMES => {
            let generation = input.u64()?;
            let database = input.text()?;
            let header = Some(input.blob()?).filter(|header| !header.is_empty());
            Message::Frames {
                generation,
                database,
                header,
                first_frame: input.u32()?,
                end_frame: input.u32()?,
                bytes: input.blob()?,
            }
        }
        KIND_CONFIRM => Message::Confirm(input.position()?),
        KIND_SNAPSHOT_BEGIN => Message::SnapshotBegin {
            generation: input.u64()?,
            database: input.text()?,
        },
        KIND_SNAPSHOT_CHUNK => {
            let database = input.text()?;
            let kind = match input.byte()? {
                FILE_DATABASE => FileKind::Database,
                FILE_WAL => FileKind::Wal,
                other => return Err(Error::new(ErrorKind::InvalidData, format!("unknown file kind {other}"))),
            };
            Message::SnapshotChunk {
                database,
                kind,
                bytes: input.blob()?,
            }
        }
        KIND_SNAPSHOT_END => Message::SnapshotEnd { database: input.text()? },
        KIND_ADMIT => Message::Admit { generation: input.u64()? },
        other => return Err(Error::new(ErrorKind::InvalidData, format!("unknown message kind {other}"))),
    };
    Ok(out)
}

/// Returns a message encoded with its length prefix.
pub fn frame(message: &Message) -> Result<Vec<u8>, Error> {
    let body = encode(message)?;
    let length = u32::try_from(body.len()).map_err(|error| Error::new(ErrorKind::InvalidInput, error))?;
    let mut out = Vec::with_capacity(body.len() + 4);
    out.extend_from_slice(&length.to_be_bytes());
    out.extend_from_slice(&body);
    Ok(out)
}

/// Removes the first complete message from the front of a buffer, if the buffer holds one.
pub fn take_message(buffer: &mut Vec<u8>) -> Result<Option<Message>, Error> {
    let Some(length_bytes) = buffer.get(..4) else {
        return Ok(None);
    };
    let array: [u8; 4] = length_bytes.try_into().map_err(|error| Error::new(ErrorKind::InvalidData, error))?;
    let length = u32::from_be_bytes(array);
    if length > MAX_MESSAGE_SIZE {
        return Err(Error::new(
            ErrorKind::InvalidData,
            format!("message of {length} bytes exceeds the limit"),
        ));
    }
    let size = usize::try_from(length).map_err(|error| Error::new(ErrorKind::InvalidData, error))?;
    let end = size + 4;
    let Some(body) = buffer.get(4..end) else {
        return Ok(None);
    };
    let out = decode(body)?;
    let _ = buffer.drain(..end);
    Ok(Some(out))
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    /// Returns a strategy of arbitrary messages.
    fn message_strategy() -> impl Strategy<Value = Message> {
        let text = "[a-z]{0,12}";
        let position = (text, any::<u32>(), any::<u32>(), any::<u32>()).prop_map(|(database, salt_one, salt_two, end_frame)| Position {
            database,
            salt_one,
            salt_two,
            end_frame,
        });
        prop_oneof![
            (any::<u64>(), text).prop_map(|(generation, active_node)| Message::Hello { generation, active_node }),
            (any::<bool>(), prop::collection::vec(position.clone(), 0..4))
                .prop_map(|(in_sync, positions)| Message::HelloReply { in_sync, positions }),
            any::<u64>().prop_map(|generation| Message::Refused { generation }),
            any::<u64>().prop_map(|generation| Message::Heartbeat { generation }),
            Just(Message::HeartbeatAck),
            (
                any::<u64>(),
                text,
                prop::option::of(prop::collection::vec(any::<u8>(), 1..40)),
                any::<u32>(),
                any::<u32>(),
                prop::collection::vec(any::<u8>(), 0..100)
            )
                .prop_map(|(generation, database, header, first_frame, end_frame, bytes)| Message::Frames {
                    generation,
                    database,
                    header,
                    first_frame,
                    end_frame,
                    bytes
                }),
            position.prop_map(Message::Confirm),
            (any::<u64>(), text).prop_map(|(generation, database)| Message::SnapshotBegin { generation, database }),
            (text, any::<bool>(), prop::collection::vec(any::<u8>(), 0..100)).prop_map(|(database, is_wal, bytes)| {
                Message::SnapshotChunk {
                    database,
                    kind: if is_wal { FileKind::Wal } else { FileKind::Database },
                    bytes,
                }
            }),
            text.prop_map(|database| Message::SnapshotEnd { database }),
            any::<u64>().prop_map(|generation| Message::Admit { generation }),
        ]
    }

    proptest! {
        #[test]
        fn every_message_survives_a_round_trip(message in message_strategy()) {
            let mut buffer = frame(&message).unwrap();
            let decoded = take_message(&mut buffer).unwrap();
            prop_assert_eq!(decoded, Some(message));
            prop_assert!(buffer.is_empty());
        }

        #[test]
        fn arbitrary_bytes_never_panic(bytes in prop::collection::vec(any::<u8>(), 0..200)) {
            let mut buffer = bytes;
            let _ = take_message(&mut buffer);
        }
    }
}
