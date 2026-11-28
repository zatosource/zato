//! The response to a push of several messages - a JSON list of the IDs of the messages the endpoint accepted.

/// The JSON whitespace characters, which may surround each token.
const JSON_WHITESPACE: [u8; 4] = [b' ', b'\t', b'\n', b'\r'];

/// The radix of the hex digits of a `\u` escape.
const HEX_RADIX: u32 = 16;

/// How many hex digits a `\u` escape has.
const UNICODE_ESCAPE_LEN: usize = 4;

/// The first code unit of a high surrogate.
const HIGH_SURROGATE_MIN: u32 = 0xD800;

/// The last code unit of a high surrogate.
const HIGH_SURROGATE_MAX: u32 = 0xDBFF;

/// The first code unit of a low surrogate.
const LOW_SURROGATE_MIN: u32 = 0xDC00;

/// The last code unit of a low surrogate.
const LOW_SURROGATE_MAX: u32 = 0xDFFF;

/// How many bits the high surrogate of a pair carries above the low one.
const SURROGATE_SHIFT: u32 = 10;

/// The first code point that a surrogate pair encodes.
const SUPPLEMENTARY_BASE: u32 = 0x1_0000;

/// The lowest byte that may appear unescaped in a JSON string.
const JSON_UNESCAPED_MIN: u8 = 0x20;

/// Returns the IDs that the response to a push of several messages accepted, in the order the response lists them,
/// or the reason why the response accepts no message - it is not a JSON list of strings, or it names an ID
/// that is not one of the IDs of the request.
pub fn parse_accepted_ids(body: &[u8], msg_ids: &[String]) -> Result<Vec<String>, String> {
    let accepted = parse_string_list(body).ok_or_else(|| String::from("Response is not a JSON list of strings"))?;

    for msg_id in &accepted {
        if !msg_ids.contains(msg_id) {
            return Err(format!("Response lists `{msg_id}`, not in the request"));
        }
    }

    Ok(accepted)
}

/// A position in the bytes of a response.
struct Cursor<'body> {

    /// The bytes of the response.
    body: &'body [u8],

    /// The position of the next byte to read.
    position: usize,
}

impl Cursor<'_> {

    /// The next byte, without consuming it.
    fn peek(&self) -> Option<u8> {
        self.body.get(self.position).copied()
    }

    /// Consumes and returns the next byte.
    fn next_byte(&mut self) -> Option<u8> {
        let out = self.peek()?;
        self.position += 1;
        Some(out)
    }

    /// Consumes the whitespace in front of the next token.
    fn skip_whitespace(&mut self) {
        while self.peek().is_some_and(|byte| JSON_WHITESPACE.contains(&byte)) {
            self.position += 1;
        }
    }

    /// Consumes the given byte, returning whether it was next.
    fn consume(&mut self, expected: u8) -> bool {
        let is_next = self.peek() == Some(expected);

        if is_next {
            self.position += 1;
        }

        is_next
    }

    /// Reads four hex digits of a `\u` escape.
    fn read_hex(&mut self) -> Option<u32> {
        let end = self.position.checked_add(UNICODE_ESCAPE_LEN)?;
        let digits = self.body.get(self.position..end)?;
        let text = std::str::from_utf8(digits).ok()?;

        // A sign or anything else that from_str_radix would accept besides hex digits is not part of an escape
        if !text.bytes().all(|byte| byte.is_ascii_hexdigit()) {
            return None;
        }

        self.position = end;
        u32::from_str_radix(text, HEX_RADIX).ok()
    }
}

/// Parses a JSON list whose elements are all strings, returning `None` for anything else.
fn parse_string_list(body: &[u8]) -> Option<Vec<String>> {
    let mut cursor = Cursor { body, position: 0 };
    let mut out = Vec::new();

    cursor.skip_whitespace();

    if !cursor.consume(b'[') {
        return None;
    }

    cursor.skip_whitespace();

    // An empty list accepts no message
    if !cursor.consume(b']') {
        loop {
            cursor.skip_whitespace();
            out.push(parse_string(&mut cursor)?);
            cursor.skip_whitespace();

            if cursor.consume(b']') {
                break;
            }

            if !cursor.consume(b',') {
                return None;
            }
        }
    }

    cursor.skip_whitespace();

    // Nothing may follow the list
    if cursor.peek().is_some() {
        return None;
    }

    Some(out)
}

/// Parses one JSON string at the cursor.
fn parse_string(cursor: &mut Cursor<'_>) -> Option<String> {
    if !cursor.consume(b'"') {
        return None;
    }

    let mut bytes: Vec<u8> = Vec::new();

    loop {
        let byte = cursor.next_byte()?;

        match byte {
            b'"' => break,
            b'\\' => push_escape(cursor, &mut bytes)?,

            // Control characters must be escaped
            _ if byte < JSON_UNESCAPED_MIN => return None,

            _ => bytes.push(byte),
        }
    }

    String::from_utf8(bytes).ok()
}

/// Decodes one escape sequence after its backslash and appends what it stands for.
fn push_escape(cursor: &mut Cursor<'_>, bytes: &mut Vec<u8>) -> Option<()> {
    let decoded = match cursor.next_byte()? {
        b'"' => '"',
        b'\\' => '\\',
        b'/' => '/',
        b'b' => '\u{8}',
        b'f' => '\u{c}',
        b'n' => '\n',
        b'r' => '\r',
        b't' => '\t',
        b'u' => decode_unicode_escape(cursor)?,
        _ => return None,
    };

    let mut buffer = [0_u8; 4];
    bytes.extend_from_slice(decoded.encode_utf8(&mut buffer).as_bytes());

    Some(())
}

/// Decodes a `\u` escape, and the low surrogate escape that follows a high one.
fn decode_unicode_escape(cursor: &mut Cursor<'_>) -> Option<char> {
    let first = cursor.read_hex()?;

    if !(HIGH_SURROGATE_MIN..=HIGH_SURROGATE_MAX).contains(&first) {
        return char::from_u32(first);
    }

    // A high surrogate is valid only when the escape of a low surrogate follows it
    if !cursor.consume(b'\\') || !cursor.consume(b'u') {
        return None;
    }

    let second = cursor.read_hex()?;

    if !(LOW_SURROGATE_MIN..=LOW_SURROGATE_MAX).contains(&second) {
        return None;
    }

    let high = first - HIGH_SURROGATE_MIN;
    let low = second - LOW_SURROGATE_MIN;
    let code_point = SUPPLEMENTARY_BASE + (high << SURROGATE_SHIFT) + low;

    char::from_u32(code_point)
}

#[cfg(test)]
#[path = "reply_tests.rs"]
mod tests;
