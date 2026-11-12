//! Parsing of the response to an outgoing request.
//!
//! The status line and headers, how the body is framed, whether the connection can be kept alive,
//! and the decoding of a chunked body.
//!
//! The rules follow `http.client`, which requests reads responses through, so a response is framed
//! and its connection kept or closed exactly as it would be by requests.

/// The most headers a response may have, as in `http.client`.
pub const MAX_HEADERS: usize = 100;

/// The status of a response without content.
const NO_CONTENT: u16 = 204;

/// The status of a response to a conditional request whose resource did not change.
const NOT_MODIFIED: u16 = 304;

/// The status a server switches protocols with, the only informational status that is a final response.
const SWITCHING_PROTOCOLS: u16 = 101;

/// The first status that is not informational.
const FIRST_FINAL_STATUS: u16 = 200;

/// The first informational status.
const FIRST_INFORMATIONAL_STATUS: u16 = 100;

/// The minor version of HTTP/1.1.
const HTTP_11_MINOR_VERSION: u8 = 1;

/// The radix of a chunk size.
const HEX_RADIX: u32 = 16;

/// The status line and headers of a response, with header names and values decoded as Latin-1.
pub struct ResponseHead {
    /// The status code.
    pub status: u16,

    /// The reason phrase.
    pub reason: String,

    /// The minor version of HTTP/1.x the response was sent with.
    pub minor_version: u8,

    /// The headers, in the order they were sent, repeated headers included.
    pub headers: Vec<(String, String)>,

    /// How many bytes of the buffer the status line and the headers took.
    pub head_len: usize,
}

/// How the body of a response is delimited.
#[derive(Debug, PartialEq, Eq)]
pub enum Framing {
    /// The response has no body.
    Empty,

    /// The body has the given length.
    Length(usize),

    /// The body is sent in chunks.
    Chunked,

    /// The body ends when the endpoint closes the connection.
    UntilClose,
}

/// What parsing a buffer that starts with a response head found.
pub enum HeadStatus {
    /// The head is complete.
    Complete(ResponseHead),

    /// The head is not complete yet and more bytes are needed.
    Partial,
}

/// Parses the status line and the headers at the start of a buffer.
pub fn parse_head(buffer: &[u8]) -> Result<HeadStatus, String> {
    let mut header_slots = [httparse::EMPTY_HEADER; MAX_HEADERS];
    let mut response = httparse::Response::new(&mut header_slots);

    let mut config = httparse::ParserConfig::default();
    let _ = config.allow_spaces_after_header_name_in_responses(true);
    let _ = config.allow_obsolete_multiline_headers_in_responses(true);
    let _ = config.allow_multiple_spaces_in_response_status_delimiters(true);

    let head_len = match config.parse_response(&mut response, buffer) {
        Ok(httparse::Status::Complete(head_len)) => head_len,
        Ok(httparse::Status::Partial) => return Ok(HeadStatus::Partial),
        Err(err) => return Err(format!("Invalid response head: {err}")),
    };

    let status = response.code.unwrap_or_default();
    let minor_version = response.version.unwrap_or_default();
    let reason = response.reason.unwrap_or_default().to_owned();

    let mut headers = Vec::with_capacity(response.headers.len());

    for header in response.headers.iter() {
        headers.push((header.name.to_owned(), decode_latin1(header.value)));
    }

    Ok(HeadStatus::Complete(ResponseHead {
        status,
        reason,
        minor_version,
        headers,
        head_len,
    }))
}

/// Decodes Latin-1 bytes into text, as `http.client` decodes header values.
pub fn decode_latin1(bytes: &[u8]) -> String {
    bytes.iter().map(|&byte| char::from(byte)).collect()
}

impl ResponseHead {
    /// Returns the value of the first header of the given name, compared case-insensitively.
    pub fn header(&self, name: &str) -> Option<&str> {
        self.headers
            .iter()
            .find(|(header_name, _)| header_name.eq_ignore_ascii_case(name))
            .map(|(_, value)| value.as_str())
    }

    /// Whether the response is informational and another response to the same request follows it.
    pub fn is_interim(&self) -> bool {
        (FIRST_INFORMATIONAL_STATUS..FIRST_FINAL_STATUS).contains(&self.status) && self.status != SWITCHING_PROTOCOLS
    }

    /// How the body of the response is delimited, given whether the request was a HEAD request.
    pub fn framing(&self, is_head_request: bool) -> Framing {
        let has_no_body = is_head_request
            || self.status == NO_CONTENT
            || self.status == NOT_MODIFIED
            || (FIRST_INFORMATIONAL_STATUS..FIRST_FINAL_STATUS).contains(&self.status);

        if has_no_body {
            return Framing::Empty;
        }

        let is_chunked = self
            .header("transfer-encoding")
            .is_some_and(|value| value.eq_ignore_ascii_case("chunked"));

        if is_chunked {
            return Framing::Chunked;
        }

        self.header("content-length")
            .and_then(parse_content_length)
            .map_or(Framing::UntilClose, Framing::Length)
    }

    /// Whether the endpoint keeps the connection open after the response, by the rules of `http.client`.
    pub fn is_keep_alive(&self) -> bool {
        let connection = self.header("connection").map(str::to_ascii_lowercase);

        if connection.as_deref().is_some_and(|value| value.contains("close")) {
            return false;
        }

        if self.minor_version >= HTTP_11_MINOR_VERSION {
            return true;
        }

        // An HTTP/1.0 response keeps its connection only when it says so
        if self.header("keep-alive").is_some_and(|value| !value.is_empty()) {
            return true;
        }

        if connection.as_deref().is_some_and(|value| value.contains("keep-alive")) {
            return true;
        }

        self.header("proxy-connection")
            .is_some_and(|value| value.to_ascii_lowercase().contains("keep-alive"))
    }
}

/// Parses a `Content-Length` value, surrounding whitespace allowed, returning `None` for anything else.
fn parse_content_length(value: &str) -> Option<usize> {
    let trimmed = value.trim();

    if trimmed.is_empty() || !trimmed.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }

    trimmed.parse::<usize>().ok()
}

/// Where a chunked decoder is within a chunked body.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ChunkState {
    /// Reading the line with the size of the next chunk.
    Size,

    /// Reading the data of a chunk, with the given number of bytes left.
    Data(usize),

    /// Skipping the line break after the data of a chunk, with the given number of bytes left.
    DataEnd(usize),

    /// Reading the trailer lines after the last chunk.
    Trailer,

    /// The body is complete.
    Done,
}

/// An incremental decoder of a chunked body.
pub struct ChunkedDecoder {
    /// Where the decoder is within the body.
    state: ChunkState,
}

/// The number of bytes the line break after the data of a chunk takes.
const DATA_END_LEN: usize = 2;

impl ChunkedDecoder {
    /// Creates a decoder positioned at the start of a chunked body.
    pub const fn new() -> Self {
        Self { state: ChunkState::Size }
    }

    /// Whether the last chunk and the trailer were read.
    pub fn is_done(&self) -> bool {
        self.state == ChunkState::Done
    }

    /// Decodes as much of the input as possible, appending the data of the chunks to the output.
    ///
    /// Returns how many bytes of the input were consumed. The bytes not consumed are an incomplete line
    /// and are given again, with more bytes after them, in the next call.
    pub fn feed(&mut self, input: &[u8], output: &mut Vec<u8>) -> Result<usize, String> {
        let mut position = 0;

        loop {
            let remaining = input.get(position..).unwrap_or_default();

            let consumed = match self.state {
                ChunkState::Done => return Ok(position),
                ChunkState::Size => self.feed_size(remaining)?,
                ChunkState::Data(left) => Some(self.feed_data(remaining, left, output)),
                ChunkState::DataEnd(left) => Some(self.feed_data_end(remaining, left)),
                ChunkState::Trailer => self.feed_trailer(remaining),
            };

            match consumed {
                Some(0) | None => return Ok(position),
                Some(count) => position += count,
            }
        }
    }

    /// Reads the line with the size of the next chunk, ignoring any chunk extension.
    fn feed_size(&mut self, input: &[u8]) -> Result<Option<usize>, String> {
        let Some(line_end) = input.iter().position(|&byte| byte == b'\n') else {
            return Ok(None);
        };

        let line = input.get(..line_end).unwrap_or_default();
        let size_part = line.split(|&byte| byte == b';').next().unwrap_or_default();
        let size_text = String::from_utf8_lossy(size_part);

        let size =
            usize::from_str_radix(size_text.trim(), HEX_RADIX).map_err(|err| format!("Invalid chunk length {size_text:?}: {err}"))?;

        self.state = if size == 0 { ChunkState::Trailer } else { ChunkState::Data(size) };

        Ok(Some(line_end + 1))
    }

    /// Copies the data of the current chunk to the output.
    fn feed_data(&mut self, input: &[u8], left: usize, output: &mut Vec<u8>) -> usize {
        let count = left.min(input.len());
        output.extend_from_slice(input.get(..count).unwrap_or_default());

        let still_left = left - count;
        self.state = if still_left == 0 {
            ChunkState::DataEnd(DATA_END_LEN)
        } else {
            ChunkState::Data(still_left)
        };

        count
    }

    /// Skips the line break after the data of a chunk without checking what it consists of, as `http.client` does.
    fn feed_data_end(&mut self, input: &[u8], left: usize) -> usize {
        let count = left.min(input.len());
        let still_left = left - count;

        self.state = if still_left == 0 {
            ChunkState::Size
        } else {
            ChunkState::DataEnd(still_left)
        };

        count
    }

    /// Discards the trailer lines until the empty line that ends the body.
    fn feed_trailer(&mut self, input: &[u8]) -> Option<usize> {
        let line_end = input.iter().position(|&byte| byte == b'\n')?;
        let line = input.get(..line_end).unwrap_or_default();

        if line.is_empty() || line == b"\r" {
            self.state = ChunkState::Done;
        }

        Some(line_end + 1)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    fn head(raw: &[u8]) -> ResponseHead {
        match parse_head(raw) {
            Ok(HeadStatus::Complete(head)) => head,
            _ => panic!("head not complete"),
        }
    }

    fn decode_all(input: &[u8]) -> (Vec<u8>, bool) {
        let mut decoder = ChunkedDecoder::new();
        let mut output = Vec::new();
        let consumed = decoder.feed(input, &mut output).unwrap();
        assert!(consumed <= input.len());
        (output, decoder.is_done())
    }

    #[test]
    fn status_line_and_headers() {
        let parsed = head(b"HTTP/1.1 404 Customer Not Found\r\nX-Item: first\r\nx-item: second\r\n\r\nbody");

        assert_eq!(parsed.status, 404);
        assert_eq!(parsed.reason, "Customer Not Found");
        assert_eq!(parsed.header("X-ITEM"), Some("first"));
        assert_eq!(parsed.headers.len(), 2);
        assert_eq!(parsed.head_len, 66);
    }

    #[test]
    fn partial_head() {
        assert!(matches!(parse_head(b"HTTP/1.1 200 OK\r\nContent-Le"), Ok(HeadStatus::Partial)));
    }

    #[test]
    fn latin1_header_value() {
        let parsed = head(b"HTTP/1.1 200 OK\r\nX-City: Z\xfcrich\r\n\r\n");
        assert_eq!(parsed.header("x-city"), Some("Z\u{fc}rich"));
    }

    #[test]
    fn framing() {
        assert_eq!(
            head(b"HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\n").framing(false),
            Framing::Length(12)
        );
        assert_eq!(head(b"HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\n").framing(true), Framing::Empty);
        assert_eq!(
            head(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n").framing(false),
            Framing::Chunked
        );
        assert_eq!(
            head(b"HTTP/1.1 204 No Content\r\nContent-Length: 5\r\n\r\n").framing(false),
            Framing::Empty
        );
        assert_eq!(head(b"HTTP/1.1 200 OK\r\n\r\n").framing(false), Framing::UntilClose);
        assert_eq!(
            head(b"HTTP/1.1 200 OK\r\nContent-Length: abc\r\n\r\n").framing(false),
            Framing::UntilClose
        );
    }

    #[test]
    fn keep_alive() {
        assert!(head(b"HTTP/1.1 200 OK\r\n\r\n").is_keep_alive());
        assert!(!head(b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n").is_keep_alive());
        assert!(!head(b"HTTP/1.0 200 OK\r\n\r\n").is_keep_alive());
        assert!(head(b"HTTP/1.0 200 OK\r\nConnection: Keep-Alive\r\n\r\n").is_keep_alive());
    }

    #[test]
    fn interim_response() {
        assert!(head(b"HTTP/1.1 100 Continue\r\n\r\n").is_interim());
        assert!(!head(b"HTTP/1.1 101 Switching Protocols\r\n\r\n").is_interim());
    }

    #[test]
    fn chunked_body() {
        let (output, is_done) = decode_all(b"5\r\nHello\r\n7;ext=1\r\n, world\r\n0\r\nX-Trailer: 1\r\n\r\n");

        assert_eq!(output, b"Hello, world");
        assert!(is_done);
    }

    #[test]
    fn chunked_body_incomplete() {
        let (output, is_done) = decode_all(b"5\r\nHel");

        assert_eq!(output, b"Hel");
        assert!(!is_done);
    }

    #[test]
    fn invalid_chunk_length() {
        let mut decoder = ChunkedDecoder::new();
        let mut output = Vec::new();
        assert!(decoder.feed(b"xyz\r\n", &mut output).is_err());
    }

    fn encode_chunked(chunks: &[Vec<u8>]) -> Vec<u8> {
        let mut out = Vec::new();
        for chunk in chunks {
            out.extend_from_slice(format!("{:x}\r\n", chunk.len()).as_bytes());
            out.extend_from_slice(chunk);
            out.extend_from_slice(b"\r\n");
        }
        out.extend_from_slice(b"0\r\n\r\n");
        out
    }

    proptest! {
        #[test]
        fn chunked_round_trip(
            chunks in prop::collection::vec(prop::collection::vec(any::<u8>(), 1..64), 0..16),
            split_points in prop::collection::vec(any::<usize>(), 0..8),
        ) {
            let encoded = encode_chunked(&chunks);
            let expected: Vec<u8> = chunks.concat();

            // The encoded body arrives in pieces split at arbitrary points ..
            let mut points: Vec<usize> = split_points.iter().map(|point| point % (encoded.len() + 1)).collect();
            points.sort_unstable();

            let mut decoder = ChunkedDecoder::new();
            let mut output = Vec::new();
            let mut pending: Vec<u8> = Vec::new();
            let mut start = 0;

            for end in points.into_iter().chain(std::iter::once(encoded.len())) {
                pending.extend_from_slice(encoded.get(start..end).unwrap_or_default());
                start = end;

                let consumed = decoder.feed(&pending, &mut output).unwrap();
                pending.drain(..consumed);
            }

            // .. and decodes into exactly the chunks it was made of.
            prop_assert!(decoder.is_done());
            prop_assert_eq!(output, expected);
        }

        #[test]
        fn head_parser_never_panics(raw in prop::collection::vec(any::<u8>(), 0..512)) {
            let _ = parse_head(&raw);
        }
    }
}
