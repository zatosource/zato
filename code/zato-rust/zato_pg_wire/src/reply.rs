//! Parsing of the replies that `PostgreSQL` sends to the statements of the pg8000 driver of Zato.
//!
//! A reply of the extended query protocol is a run of `ParseComplete`, `BindComplete`, `DataRow`, `CommandComplete`,
//! `NoData` and `ReadyForQuery` messages. This module walks the messages of a buffer received from the socket,
//! decodes each `DataRow` with the decoder of the prepared statement and collects each `CommandComplete` tag,
//! and it stops at any other message, which the driver handles in Python, or where the buffer ends.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList};

use crate::row::RowDecoder;

/// The size of the code of a message.
const CODE_SIZE: usize = 1;

/// The size of the length that follows the code of a message and counts itself and the body.
const LENGTH_SIZE: usize = 4;

/// The size of the header of a message, its code and its length.
const HEADER_SIZE: usize = CODE_SIZE + LENGTH_SIZE;

/// The code of a `ParseComplete` message.
const PARSE_COMPLETE: u8 = b'1';

/// The code of a `BindComplete` message.
const BIND_COMPLETE: u8 = b'2';

/// The code of a `NoData` message.
const NO_DATA: u8 = b'n';

/// The code of a `DataRow` message.
const DATA_ROW: u8 = b'D';

/// The code of a `CommandComplete` message.
const COMMAND_COMPLETE: u8 = b'C';

/// What the parser does with one message of a reply.
enum Step {

    /// The message carries nothing that the driver keeps.
    Skip,

    /// The message is a row of the result.
    Row,

    /// The message reports that a statement completed, with its tag.
    Tag,

    /// The message is handled by the driver in Python.
    Stop,
}

/// Where the parse of a buffer ended.
#[derive(Debug, PartialEq, Eq)]
pub enum ParseEnd<'buffer> {

    /// The next message is not complete in the buffer, and this many unread bytes, counted from the position
    /// where the parse ended, hold it whole.
    Incomplete(usize),

    /// The parse stopped at a message that the driver handles, with its code and its body.
    Stopped(u8, &'buffer [u8]),
}

/// The messages of a buffer that the parser read, up to where it ended.
#[derive(Debug, PartialEq, Eq)]
pub struct ParsedReplies<'buffer> {

    /// The bodies of the `DataRow` messages, in the order of the rows.
    pub rows: Vec<&'buffer [u8]>,

    /// The bodies of the `CommandComplete` messages, each the tag of a statement followed by its NUL byte.
    pub tags: Vec<&'buffer [u8]>,

    /// The position in the buffer after the last message read, where the next parse begins.
    pub position: usize,

    /// Why the parse ended.
    pub end: ParseEnd<'buffer>,
}

/// Returns the error raised for a message whose length is smaller than the length field itself.
fn invalid_length(length: i32) -> PyErr {
    PyValueError::new_err(format!("Message of the server has an invalid length: {length}"))
}

/// Returns what the parser does with a message of the code given, where rows are decoded only if requested.
const fn step_of(code: u8, decodes_rows: bool) -> Step {
    match code {
        PARSE_COMPLETE | BIND_COMPLETE | NO_DATA => Step::Skip,
        DATA_ROW if decodes_rows => Step::Row,
        COMMAND_COMPLETE => Step::Tag,
        _ => Step::Stop,
    }
}

/// Parses the messages of a buffer from the position given, collecting the bodies of rows, if requested,
/// and the tags of statements, until a message that the driver handles or the end of the buffer.
///
/// # Errors
///
/// Returns an error when the length of a message is smaller than its length field.
pub fn parse_replies(buffer: &[u8], position: usize, decodes_rows: bool) -> PyResult<ParsedReplies<'_>> {
    let mut rows = Vec::new();
    let mut tags = Vec::new();
    let mut current = position;

    loop {
        // The header of the next message gives its code and its length ..
        let header_end = current.saturating_add(HEADER_SIZE);

        let Some(header) = buffer.get(current..header_end) else {
            // .. and a header that is not complete yet is read by the driver first.
            let end = ParseEnd::Incomplete(HEADER_SIZE);
            return Ok(ParsedReplies {
                rows,
                tags,
                position: current,
                end,
            });
        };

        let (code_bytes, length_bytes) = header.split_at(CODE_SIZE);
        let code = code_bytes.first().copied().unwrap_or_default();
        let length_array = <[u8; LENGTH_SIZE]>::try_from(length_bytes).map_err(|error| PyValueError::new_err(error.to_string()))?;
        let length = i32::from_be_bytes(length_array);

        // The length counts itself and the body of the message, never less than itself.
        let length_size = usize::try_from(length)
            .ok()
            .filter(|size| *size >= LENGTH_SIZE)
            .ok_or_else(|| invalid_length(length))?;

        let body_size = length_size.saturating_sub(LENGTH_SIZE);
        let message_end = header_end.saturating_add(body_size);

        // A body that is not complete yet is read by the driver together with its header.
        let Some(body) = buffer.get(header_end..message_end) else {
            let needed = CODE_SIZE.saturating_add(length_size);
            let end = ParseEnd::Incomplete(needed);
            return Ok(ParsedReplies {
                rows,
                tags,
                position: current,
                end,
            });
        };

        match step_of(code, decodes_rows) {
            Step::Skip => {}
            Step::Row => rows.push(body),
            Step::Tag => tags.push(body),

            // The message is consumed here and handled by the driver, which continues after it.
            Step::Stop => {
                let end = ParseEnd::Stopped(code, body);
                return Ok(ParsedReplies {
                    rows,
                    tags,
                    position: message_end,
                    end,
                });
            }
        }

        current = message_end;
    }
}

/// The result of `read_replies`.
///
/// It holds the decoded rows, the tags of the statements, the position after the last message read,
/// the number of unread bytes that the next message needs, or 0, and the code and the body of the message
/// at which the parse stopped, if any.
type RepliesResult<'py> = (
    Bound<'py, PyList>,
    Bound<'py, PyList>,
    usize,
    usize,
    Option<Bound<'py, PyBytes>>,
    Option<Bound<'py, PyBytes>>,
);

/// Reads the messages of a buffer received from the socket of a connection, from the position given.
///
/// Each `DataRow` is decoded with the decoder of the prepared statement, if one is given, and each
/// `CommandComplete` tag is collected for the handler of the driver. The parse stops at `ReadyForQuery`,
/// at any message that the driver handles in Python, or where the buffer ends with a message incomplete.
#[pyfunction]
#[pyo3(signature = (buffer, position, decoder))]
pub fn read_replies<'py>(
    py: Python<'py>,
    buffer: &[u8],
    position: usize,
    decoder: Option<&Bound<'py, RowDecoder>>,
) -> PyResult<RepliesResult<'py>> {
    let parsed = parse_replies(buffer, position, decoder.is_some())?;

    // The rows exist only for a statement that has a decoder ..
    let rows = PyList::empty(py);

    if let Some(row_decoder) = decoder {
        let row_decoder = row_decoder.get();

        for body in &parsed.rows {
            let row = row_decoder.decode(py, body)?;
            rows.append(row)?;
        }
    }

    // .. while each statement has a tag.
    let tags = PyList::empty(py);

    for tag in &parsed.tags {
        tags.append(PyBytes::new(py, tag))?;
    }

    let (needed, code, data) = match parsed.end {
        ParseEnd::Incomplete(needed) => (needed, None, None),
        ParseEnd::Stopped(code, body) => (0, Some(PyBytes::new(py, &[code])), Some(PyBytes::new(py, body))),
    };

    Ok((rows, tags, parsed.position, needed, code, data))
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The code of a `ReadyForQuery` message.
    const READY_FOR_QUERY: u8 = b'Z';

    /// The code of an `ErrorResponse` message.
    const ERROR_RESPONSE: u8 = b'E';

    /// The code of a `NoticeResponse` message.
    const NOTICE_RESPONSE: u8 = b'N';

    /// The status of a connection idle in a transaction, as `ReadyForQuery` reports it.
    const IN_TRANSACTION: u8 = b'T';

    /// Returns one message with its code, its length and its body.
    fn message(code: u8, body: &[u8]) -> Vec<u8> {
        let length = i32::try_from(body.len().saturating_add(LENGTH_SIZE)).unwrap_or(i32::MAX);
        let mut out = vec![code];
        out.extend_from_slice(&length.to_be_bytes());
        out.extend_from_slice(body);
        out
    }

    /// Returns the body of a `DataRow` message with one text value.
    fn row_body(value: &[u8]) -> Vec<u8> {
        let length = i32::try_from(value.len()).unwrap_or(i32::MAX);
        let mut out = vec![0, 1];
        out.extend_from_slice(&length.to_be_bytes());
        out.extend_from_slice(value);
        out
    }

    /// Returns the reply of one statement with rows of the given values.
    fn reply(values: &[&[u8]]) -> Vec<u8> {
        let mut out = message(BIND_COMPLETE, b"");

        for value in values {
            out.extend(message(DATA_ROW, &row_body(value)));
        }

        out.extend(message(COMMAND_COMPLETE, b"SELECT 2\0"));
        out.extend(message(READY_FOR_QUERY, &[IN_TRANSACTION]));
        out
    }

    #[test]
    fn reply_with_rows() {
        let buffer = reply(&[b"a", b"bc"]);
        let parsed = parse_replies(&buffer, 0, true).ok();

        let first = row_body(b"a");
        let second = row_body(b"bc");

        let expected = ParsedReplies {
            rows: vec![first.as_slice(), second.as_slice()],
            tags: vec![b"SELECT 2\0".as_slice()],
            position: buffer.len(),
            end: ParseEnd::Stopped(READY_FOR_QUERY, &[IN_TRANSACTION]),
        };

        assert_eq!(parsed, Some(expected));
    }

    #[test]
    fn reply_without_rows() {
        let mut buffer = message(BIND_COMPLETE, b"");
        buffer.extend(message(NO_DATA, b""));
        buffer.extend(message(COMMAND_COMPLETE, b"UPDATE 0\0"));
        buffer.extend(message(READY_FOR_QUERY, &[IN_TRANSACTION]));

        let parsed = parse_replies(&buffer, 0, true).ok();

        let expected = ParsedReplies {
            rows: vec![],
            tags: vec![b"UPDATE 0\0".as_slice()],
            position: buffer.len(),
            end: ParseEnd::Stopped(READY_FOR_QUERY, &[IN_TRANSACTION]),
        };

        assert_eq!(parsed, Some(expected));
    }

    #[test]
    fn reply_with_many_rows() {
        let values: Vec<Vec<u8>> = (0..10_000_u32).map(|value| value.to_string().into_bytes()).collect();
        let value_slices: Vec<&[u8]> = values.iter().map(Vec::as_slice).collect();
        let buffer = reply(&value_slices);

        let parsed = parse_replies(&buffer, 0, true).ok();
        let row_count = parsed.as_ref().map(|replies| replies.rows.len());
        let last_row = parsed.as_ref().and_then(|replies| replies.rows.last().map(|row| row.to_vec()));

        assert_eq!(row_count, Some(values.len()));
        assert_eq!(last_row, Some(row_body(b"9999")));
    }

    #[test]
    fn rows_without_decoder_stop_the_parse() {
        let buffer = reply(&[b"a"]);
        let parsed = parse_replies(&buffer, 0, false).ok();

        let bind_size = message(BIND_COMPLETE, b"").len();
        let row = row_body(b"a");
        let row_size = message(DATA_ROW, &row).len();

        let expected = ParsedReplies {
            rows: vec![],
            tags: vec![],
            position: bind_size.saturating_add(row_size),
            end: ParseEnd::Stopped(DATA_ROW, row.as_slice()),
        };

        assert_eq!(parsed, Some(expected));
    }

    #[test]
    fn error_after_rows() {
        let mut buffer = message(BIND_COMPLETE, b"");
        buffer.extend(message(DATA_ROW, &row_body(b"a")));
        let error_body = b"SERROR\0C22012\0Mdivision by zero\0\0";
        buffer.extend(message(ERROR_RESPONSE, error_body));
        buffer.extend(message(READY_FOR_QUERY, &[IN_TRANSACTION]));

        let parsed = parse_replies(&buffer, 0, true).ok();
        let first = row_body(b"a");
        let ready_size = message(READY_FOR_QUERY, &[IN_TRANSACTION]).len();

        let expected = ParsedReplies {
            rows: vec![first.as_slice()],
            tags: vec![],
            position: buffer.len().saturating_sub(ready_size),
            end: ParseEnd::Stopped(ERROR_RESPONSE, error_body.as_slice()),
        };

        assert_eq!(parsed, Some(expected));
    }

    #[test]
    fn notice_between_rows() {
        let notice_body = b"SNOTICE\0Mrow 1\0\0";

        let mut buffer = message(BIND_COMPLETE, b"");
        buffer.extend(message(DATA_ROW, &row_body(b"a")));
        buffer.extend(message(NOTICE_RESPONSE, notice_body));
        buffer.extend(message(DATA_ROW, &row_body(b"b")));
        buffer.extend(message(COMMAND_COMPLETE, b"SELECT 2\0"));
        buffer.extend(message(READY_FOR_QUERY, &[IN_TRANSACTION]));

        // The parse stops at the notice ..
        let first_parse = parse_replies(&buffer, 0, true).ok();
        let first_end = first_parse.as_ref().map(|replies| (replies.rows.len(), &replies.end));
        assert_eq!(first_end, Some((1, &ParseEnd::Stopped(NOTICE_RESPONSE, notice_body.as_slice()))));

        // .. and continues after it with the next row.
        let next_position = first_parse.map_or(0, |replies| replies.position);
        let second_parse = parse_replies(&buffer, next_position, true).ok();
        let second = row_body(b"b");

        let expected = ParsedReplies {
            rows: vec![second.as_slice()],
            tags: vec![b"SELECT 2\0".as_slice()],
            position: buffer.len(),
            end: ParseEnd::Stopped(READY_FOR_QUERY, &[IN_TRANSACTION]),
        };

        assert_eq!(second_parse, Some(expected));
    }

    #[test]
    fn replies_of_several_statements() {
        let first_reply = reply(&[b"a"]);
        let second_reply = reply(&[b"b"]);

        let mut buffer = first_reply.clone();
        buffer.extend_from_slice(&second_reply);

        // The first reply ends at its own ReadyForQuery ..
        let first_parse = parse_replies(&buffer, 0, true).ok();
        let first_position = first_parse.as_ref().map(|replies| replies.position);
        assert_eq!(first_position, Some(first_reply.len()));

        // .. and the second one is read from there.
        let second_parse = parse_replies(&buffer, first_reply.len(), true).ok();
        let second_rows = second_parse.as_ref().map(|replies| replies.rows.clone());
        let expected_row = row_body(b"b");
        assert_eq!(second_rows, Some(vec![expected_row.as_slice()]));

        let second_position = second_parse.map(|replies| replies.position);
        assert_eq!(second_position, Some(buffer.len()));
    }

    #[test]
    fn message_split_at_every_offset() {
        let buffer = reply(&[b"first", b"second"]);
        let whole = parse_replies(&buffer, 0, true).ok();

        for split in 1..buffer.len() {
            let received = buffer.get(..split).unwrap_or_default();

            // The first part of the buffer ends with a message incomplete ..
            let partial = parse_replies(received, 0, true).ok();
            let partial_position = partial.as_ref().map_or(0, |replies| replies.position);
            let unread = split.saturating_sub(partial_position);

            let needed = partial.as_ref().and_then(|replies| match replies.end {
                ParseEnd::Incomplete(needed) => Some(needed),
                ParseEnd::Stopped(..) => None,
            });

            assert!(needed > Some(unread), "offset {split} needs {needed:?} bytes with {unread} unread");

            // .. and the bytes it needs, all of which the whole buffer holds, complete it.
            let rest = parse_replies(&buffer, partial_position, true).ok();

            let combined = partial.zip(rest).map(|(first, second)| {
                let mut rows = first.rows;
                rows.extend(second.rows);

                let mut tags = first.tags;
                tags.extend(second.tags);

                ParsedReplies {
                    rows,
                    tags,
                    position: second.position,
                    end: second.end,
                }
            });

            assert_eq!(combined, whole, "offset {split}");
        }
    }

    #[test]
    fn invalid_length_is_refused() {
        let buffer = [DATA_ROW, 0, 0, 0, 3];
        assert!(parse_replies(&buffer, 0, true).is_err());
    }
}
