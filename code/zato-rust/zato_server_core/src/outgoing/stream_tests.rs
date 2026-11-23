//! The vectored writes of the head and the body parts of a request.
//!
//! The tests cover partial writes that end inside a slice and between slices, writes that would block,
//! empty parts anywhere in a request, and a non-blocking loopback connection whose buffers hold
//! far less than one request.

use std::io::{ErrorKind, IoSlice, Read};
use std::net::{Shutdown, TcpListener, TcpStream};
use std::thread;
use std::time::Duration;

use socket2::SockRef;

use super::{IoError, write_all_slices};

/// The size of each of the large body parts.
const LARGE_PART_LEN: usize = 2 * 1024 * 1024;

/// The most bytes the writer of the deterministic tests accepts per write, a size that does not divide any part evenly.
const TRICKLE_WRITE_LEN: usize = 7;

/// Every how many writes the writer of the deterministic tests reports that it would block.
const WOULD_BLOCK_EVERY: usize = 3;

/// The size requested for the send and receive buffers of the loopback connection, which the kernel raises to its minimum.
const SMALL_BUFFER_LEN: usize = 4096;

/// The size of each read of the receiving side of the loopback connection.
const READ_CHUNK_LEN: usize = 1024;

/// How long the receiving side waits before its first read, so that the send buffer fills up.
const READER_START_DELAY: Duration = Duration::from_millis(50);

/// How long the writing side waits after a write that would block.
const WAIT_INTERVAL: Duration = Duration::from_millis(1);

/// The period of the byte pattern of the large parts, a prime, so that the pattern is out of step with every buffer size.
const PATTERN_PERIOD: usize = 251;

/// Returns a part of the given length with bytes that differ from one position to the next.
fn patterned_part(len: usize, seed: u8) -> Vec<u8> {
    (0..len)
        .map(|position| {
            let offset = u8::try_from(position % PATTERN_PERIOD).unwrap_or(0);
            seed.wrapping_add(offset)
        })
        .collect()
}

/// Joins the head and the parts as the endpoint receives them.
fn joined(head: &[u8], parts: &[&[u8]]) -> Vec<u8> {
    let mut out = head.to_vec();
    for part in parts {
        out.extend_from_slice(part);
    }
    out
}

/// A writer that accepts a few bytes per write and regularly reports that it would block.
struct TrickleWriter {
    /// Everything accepted so far.
    received: Vec<u8>,

    /// How many writes were requested so far.
    write_count: usize,

    /// How many writes were requested with nothing to write.
    empty_write_count: usize,
}

impl TrickleWriter {
    /// Returns a writer that accepted nothing yet.
    const fn new() -> Self {
        Self {
            received: Vec::new(),
            write_count: 0,
            empty_write_count: 0,
        }
    }

    /// Accepts up to `TRICKLE_WRITE_LEN` bytes from the slices, in order, or reports that it would block.
    fn write(&mut self, slices: &[IoSlice<'_>]) -> std::io::Result<usize> {
        self.write_count += 1;

        if self.write_count.is_multiple_of(WOULD_BLOCK_EVERY) {
            return Err(ErrorKind::WouldBlock.into());
        }

        let total: usize = slices.iter().map(|slice| slice.len()).sum();
        if total == 0 {
            self.empty_write_count += 1;
            return Ok(0);
        }

        let mut accepted = 0;
        for slice in slices {
            let room = TRICKLE_WRITE_LEN - accepted;
            let taken = slice.get(..room.min(slice.len())).unwrap_or_default();
            self.received.extend_from_slice(taken);
            accepted += taken.len();

            if accepted == TRICKLE_WRITE_LEN {
                break;
            }
        }

        Ok(accepted)
    }
}

/// Writes the head and the parts through the trickle writer and returns it.
fn write_through_trickle(head: &[u8], parts: &[&[u8]]) -> (Result<(), IoError>, TrickleWriter, usize) {
    let mut writer = TrickleWriter::new();
    let mut wait_count = 0;

    let mut slices = vec![IoSlice::new(head)];
    slices.extend(parts.iter().map(|part| IoSlice::new(part)));

    let result = write_all_slices(
        &mut slices,
        |current| writer.write(current),
        || {
            wait_count += 1;
            Ok(())
        },
    );

    (result, writer, wait_count)
}

#[test]
fn partial_writes_inside_and_between_slices() {
    let head = b"POST /orders HTTP/1.1\r\n\r\n";
    let parts: [&[u8]; 3] = [b"{\"data\":", b"\"Order 12345 for John Smith\"", b"}"];

    let (result, writer, wait_count) = write_through_trickle(head, &parts);

    assert!(result.is_ok());
    assert_eq!(writer.received, joined(head, &parts));
    assert_eq!(writer.empty_write_count, 0);
    assert!(wait_count > 0);
}

#[test]
fn empty_parts_anywhere() {
    let empty: &[u8] = b"";
    let parts: [&[u8]; 5] = [empty, b"{\"data\":", empty, b"\"Invoice 2024-001\"}", empty];

    // An empty head is followed by the parts, and a request of empty parts alone writes nothing
    for head in [empty, b"POST /invoices HTTP/1.1\r\n\r\n".as_slice()] {
        let (result, writer, _) = write_through_trickle(head, &parts);

        assert!(result.is_ok());
        assert_eq!(writer.received, joined(head, &parts));
        assert_eq!(writer.empty_write_count, 0);
    }

    let (result, writer, _) = write_through_trickle(empty, &[empty, empty]);
    assert!(result.is_ok());
    assert!(writer.received.is_empty());
    assert_eq!(writer.write_count, 0);
}

#[test]
fn write_of_zero_bytes_is_an_error() {
    let head = b"POST /orders HTTP/1.1\r\n\r\n";
    let mut slices = [IoSlice::new(head)];

    let result = write_all_slices(&mut slices, |_| Ok(0), || Ok(()));

    assert!(matches!(result, Err(IoError::System(err)) if err.kind() == ErrorKind::WriteZero));
}

#[test]
fn loopback_connection_smaller_than_the_request() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    SockRef::from(&listener).set_recv_buffer_size(SMALL_BUFFER_LEN).unwrap();
    let address = listener.local_addr().unwrap();

    // The receiving side starts reading only once the send buffer is full, and then reads until the writer shuts down
    let reader = thread::spawn(move || {
        let (mut connection, _) = listener.accept().unwrap();
        thread::sleep(READER_START_DELAY);

        let mut received = Vec::new();
        let mut chunk = [0_u8; READ_CHUNK_LEN];
        loop {
            let count = connection.read(&mut chunk).unwrap();
            if count == 0 {
                break;
            }
            received.extend_from_slice(chunk.get(..count).unwrap());
        }
        received
    });

    let mut tcp = TcpStream::connect(address).unwrap();
    SockRef::from(&tcp).set_send_buffer_size(SMALL_BUFFER_LEN).unwrap();
    tcp.set_nonblocking(true).unwrap();

    let head = b"POST /orders HTTP/1.1\r\nContent-Type: application/json\r\n\r\n";
    let first = patterned_part(LARGE_PART_LEN, 1);
    let second = patterned_part(LARGE_PART_LEN + 1, 2);
    let third = patterned_part(LARGE_PART_LEN - 1, 3);
    let parts: [&[u8]; 3] = [&first, &second, &third];

    let mut slices = vec![IoSlice::new(head)];
    slices.extend(parts.iter().map(|part| IoSlice::new(part)));

    let mut wait_count = 0;
    let result = write_all_slices(
        &mut slices,
        |current| std::io::Write::write_vectored(&mut tcp, current),
        || {
            wait_count += 1;
            thread::sleep(WAIT_INTERVAL);
            Ok(())
        },
    );

    assert!(result.is_ok());
    tcp.shutdown(Shutdown::Write).unwrap();

    let received = reader.join().unwrap();
    assert_eq!(received, joined(head, &parts));
    assert!(wait_count > 0);
}
