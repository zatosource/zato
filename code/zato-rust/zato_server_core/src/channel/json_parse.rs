//! JSON text parser that accepts exactly what `json.loads` of Python accepts and produces the same values.
//!
//! The grammar is that of the C scanner of CPython - the constants `NaN`, `Infinity` and `-Infinity`
//! are accepted, control characters inside strings are rejected, and a `\u` escape of a surrogate is
//! joined with a following low surrogate escape, while a surrogate without a partner is kept as it is.
//! The values themselves are produced by a [`JsonBuilder`], so that the grammar is testable without Python.

/// Nesting depth of arrays and objects above which parsing stops and the input is left to Python.
pub const MAX_DEPTH: usize = 200;

/// First code point of the high surrogate range.
const HIGH_SURROGATE_START: u32 = 0xD800;

/// Last code point of the high surrogate range.
const HIGH_SURROGATE_END: u32 = 0xDBFF;

/// First code point of the low surrogate range.
const LOW_SURROGATE_START: u32 = 0xDC00;

/// Last code point of the low surrogate range.
const LOW_SURROGATE_END: u32 = 0xDFFF;

/// First code point above the Basic Multilingual Plane.
const SUPPLEMENTARY_START: u32 = 0x1_0000;

/// Number of hex digits of a `\u` escape.
const UNICODE_ESCAPE_DIGITS: usize = 4;

/// Highest code point that is a control character inside a JSON string.
const MAX_CONTROL_CHARACTER: u8 = 0x1F;

/// Produces the values of a parsed document.
pub trait JsonBuilder {
    /// A produced value.
    type Value;

    /// An error raised while producing a value.
    type Error;

    /// Produces `null`.
    fn null(&mut self) -> Result<Self::Value, Self::Error>;

    /// Produces `true` or `false`.
    fn boolean(&mut self, value: bool) -> Result<Self::Value, Self::Error>;

    /// Produces an integer from its literal, which consists of ASCII digits with an optional minus sign.
    fn integer(&mut self, literal: &str) -> Result<Self::Value, Self::Error>;

    /// Produces a float from its JSON literal or from one of `NaN`, `Infinity` and `-Infinity`.
    fn float(&mut self, literal: &str) -> Result<Self::Value, Self::Error>;

    /// Produces a string.
    fn string(&mut self, text: &str) -> Result<Self::Value, Self::Error>;

    /// Produces a string that contains surrogate code points without a partner.
    fn string_with_surrogates(&mut self, code_points: &[u32]) -> Result<Self::Value, Self::Error>;

    /// Produces an array of the given items.
    fn array(&mut self, items: Vec<Self::Value>) -> Result<Self::Value, Self::Error>;

    /// Produces an object of the given members, in document order, a later duplicate key replacing an earlier one.
    fn object(&mut self, members: Vec<(Self::Value, Self::Value)>) -> Result<Self::Value, Self::Error>;
}

/// Reason why a document was not parsed.
#[derive(Debug, PartialEq, Eq)]
pub enum ParseError<E> {
    /// The document is not valid JSON, the position is the byte offset at which parsing stopped.
    Syntax(usize),

    /// The document nests arrays and objects deeper than [`MAX_DEPTH`].
    TooDeep,

    /// The builder raised an error.
    Build(E),
}

/// Text of a parsed string, plain unless it contains a surrogate without a partner.
enum StringText {
    /// Valid Unicode text.
    Text(String),

    /// Code points that include surrogates.
    CodePoints(Vec<u32>),
}

impl StringText {
    /// Appends a character.
    fn push_char(&mut self, character: char) {
        match self {
            Self::Text(text) => text.push(character),
            Self::CodePoints(code_points) => code_points.push(u32::from(character)),
        }
    }

    /// Appends a run of characters.
    fn push_str(&mut self, run: &str) {
        match self {
            Self::Text(text) => text.push_str(run),
            Self::CodePoints(code_points) => code_points.extend(run.chars().map(u32::from)),
        }
    }

    /// Appends a code point, which may be a surrogate.
    fn push_code_point(&mut self, code_point: u32) {
        if let Some(character) = char::from_u32(code_point) {
            self.push_char(character);
            return;
        }

        // A surrogate cannot be held in a Rust string, so the text continues as code points
        if let Self::Text(text) = self {
            let mut code_points: Vec<u32> = text.chars().map(u32::from).collect();
            code_points.push(code_point);
            *self = Self::CodePoints(code_points);
        } else if let Self::CodePoints(code_points) = self {
            code_points.push(code_point);
        }
    }
}

/// Parses a complete document, with whitespace allowed around the value.
pub fn parse<B: JsonBuilder>(text: &str, builder: &mut B) -> Result<B::Value, ParseError<B::Error>> {
    let mut parser = Parser {
        text,
        bytes: text.as_bytes(),
        position: 0,
        depth: 0,
        builder,
    };

    parser.skip_whitespace();
    let out = parser.parse_value()?;
    parser.skip_whitespace();

    // Anything after the value is extra data, which Python rejects
    if parser.position != parser.bytes.len() {
        return Err(ParseError::Syntax(parser.position));
    }

    Ok(out)
}

/// State of one parse.
struct Parser<'text, 'builder, B: JsonBuilder> {
    /// The document.
    text: &'text str,

    /// Bytes of the document.
    bytes: &'text [u8],

    /// Byte offset of the next character to read.
    position: usize,

    /// Number of arrays and objects currently open.
    depth: usize,

    /// Producer of the values.
    builder: &'builder mut B,
}

impl<B: JsonBuilder> Parser<'_, '_, B> {
    /// Returns the byte at the current position.
    fn peek(&self) -> Option<u8> {
        self.bytes.get(self.position).copied()
    }

    /// Returns a syntax error at the current position.
    const fn syntax_error(&self) -> ParseError<B::Error> {
        ParseError::Syntax(self.position)
    }

    /// Skips the four JSON whitespace characters.
    fn skip_whitespace(&mut self) {
        while let Some(b' ' | b'\t' | b'\n' | b'\r') = self.peek() {
            self.position += 1;
        }
    }

    /// Whether the document continues with the given text at the current position.
    fn continues_with(&self, expected: &str) -> bool {
        self.bytes
            .get(self.position..)
            .is_some_and(|rest| rest.starts_with(expected.as_bytes()))
    }

    /// Consumes a literal word and produces its value.
    fn parse_word(&mut self, word: &str) -> Result<B::Value, ParseError<B::Error>> {
        if !self.continues_with(word) {
            return Err(self.syntax_error());
        }
        self.position += word.len();

        let out = match word {
            "null" => self.builder.null(),
            "true" => self.builder.boolean(true),
            "false" => self.builder.boolean(false),
            _ => self.builder.float(word),
        };
        out.map_err(ParseError::Build)
    }

    /// Parses the value at the current position.
    fn parse_value(&mut self) -> Result<B::Value, ParseError<B::Error>> {
        match self.peek() {
            Some(b'"') => {
                self.position += 1;
                self.parse_string_value()
            }
            Some(b'{') => self.parse_object(),
            Some(b'[') => self.parse_array(),
            Some(b'n') => self.parse_word("null"),
            Some(b't') => self.parse_word("true"),
            Some(b'f') => self.parse_word("false"),
            Some(b'N') => self.parse_word("NaN"),
            Some(b'I') => self.parse_word("Infinity"),
            Some(b'-') if self.continues_with("-Infinity") => self.parse_word("-Infinity"),
            Some(b'-' | b'0'..=b'9') => self.parse_number(),
            _ => Err(self.syntax_error()),
        }
    }

    /// Enters an array or an object.
    fn enter(&mut self) -> Result<(), ParseError<B::Error>> {
        self.depth += 1;
        if self.depth > MAX_DEPTH {
            return Err(ParseError::TooDeep);
        }
        self.position += 1;
        self.skip_whitespace();
        Ok(())
    }

    /// Consumes a comma between items, returning whether there was one.
    fn take_comma(&mut self) -> bool {
        self.skip_whitespace();
        if self.peek() == Some(b',') {
            self.position += 1;
            self.skip_whitespace();
            return true;
        }
        false
    }

    /// Consumes the closing bracket of an array or an object.
    fn leave(&mut self, closing: u8) -> Result<(), ParseError<B::Error>> {
        if self.peek() != Some(closing) {
            return Err(self.syntax_error());
        }
        self.position += 1;
        self.depth -= 1;
        Ok(())
    }

    /// Parses an array.
    fn parse_array(&mut self) -> Result<B::Value, ParseError<B::Error>> {
        self.enter()?;
        let mut items = Vec::new();

        if self.peek().is_some_and(|byte| byte != b']') {
            loop {
                items.push(self.parse_value()?);
                if !self.take_comma() {
                    break;
                }
            }
        }

        self.leave(b']')?;
        self.builder.array(items).map_err(ParseError::Build)
    }

    /// Parses an object.
    fn parse_object(&mut self) -> Result<B::Value, ParseError<B::Error>> {
        self.enter()?;
        let mut members = Vec::new();

        if self.peek().is_some_and(|byte| byte != b'}') {
            loop {
                members.push(self.parse_member()?);
                if !self.take_comma() {
                    break;
                }
            }
        }

        self.leave(b'}')?;
        self.builder.object(members).map_err(ParseError::Build)
    }

    /// Parses one key and value of an object.
    fn parse_member(&mut self) -> Result<(B::Value, B::Value), ParseError<B::Error>> {
        if self.peek() != Some(b'"') {
            return Err(self.syntax_error());
        }
        self.position += 1;
        let key = self.parse_string_value()?;

        self.skip_whitespace();
        if self.peek() != Some(b':') {
            return Err(self.syntax_error());
        }
        self.position += 1;
        self.skip_whitespace();

        let value = self.parse_value()?;
        Ok((key, value))
    }

    /// Parses a string whose opening quote has been consumed and produces its value.
    fn parse_string_value(&mut self) -> Result<B::Value, ParseError<B::Error>> {
        let out = match self.parse_string()? {
            StringText::Text(text) => self.builder.string(&text),
            StringText::CodePoints(code_points) => self.builder.string_with_surrogates(&code_points),
        };
        out.map_err(ParseError::Build)
    }

    /// Returns the length of the run of characters at the current position that need no decoding.
    fn plain_run_length(&self) -> usize {
        let rest = self.bytes.get(self.position..).unwrap_or_default();
        rest.iter()
            .take_while(|byte| **byte != b'"' && **byte != b'\\' && **byte > MAX_CONTROL_CHARACTER)
            .count()
    }

    /// Parses the text of a string up to and including its closing quote.
    fn parse_string(&mut self) -> Result<StringText, ParseError<B::Error>> {
        let mut out = StringText::Text(String::new());

        loop {
            let run_length = self.plain_run_length();
            let run_end = self.position + run_length;
            let run = self.text.get(self.position..run_end).ok_or_else(|| self.syntax_error())?;
            out.push_str(run);
            self.position = run_end;

            match self.peek() {
                Some(b'"') => {
                    self.position += 1;
                    return Ok(out);
                }
                Some(b'\\') => {
                    self.position += 1;
                    self.parse_escape(&mut out)?;
                }
                // A control character or the end of the document
                _ => return Err(self.syntax_error()),
            }
        }
    }

    /// Parses an escape sequence whose backslash has been consumed.
    fn parse_escape(&mut self, out: &mut StringText) -> Result<(), ParseError<B::Error>> {
        let escaped = self.peek().ok_or_else(|| self.syntax_error())?;
        self.position += 1;

        let character = match escaped {
            b'"' => '"',
            b'\\' => '\\',
            b'/' => '/',
            b'b' => '\u{8}',
            b'f' => '\u{c}',
            b'n' => '\n',
            b'r' => '\r',
            b't' => '\t',
            b'u' => return self.parse_unicode_escape(out),
            _ => return Err(ParseError::Syntax(self.position - 1)),
        };

        out.push_char(character);
        Ok(())
    }

    /// Reads the four hex digits of a `\u` escape at the given offset.
    fn hex_at(&self, offset: usize) -> Option<u32> {
        let digits = self.text.get(offset..offset + UNICODE_ESCAPE_DIGITS)?;
        if !digits.bytes().all(|byte| byte.is_ascii_hexdigit()) {
            return None;
        }
        u32::from_str_radix(digits, 16).ok()
    }

    /// Parses the digits of a `\u` escape, joining a high surrogate with a low surrogate escape that follows it.
    fn parse_unicode_escape(&mut self, out: &mut StringText) -> Result<(), ParseError<B::Error>> {
        let code_point = self.hex_at(self.position).ok_or_else(|| self.syntax_error())?;
        self.position += UNICODE_ESCAPE_DIGITS;

        if (HIGH_SURROGATE_START..=HIGH_SURROGATE_END).contains(&code_point) && self.continues_with("\\u") {
            let low = self.hex_at(self.position + 2);

            // Only a low surrogate is joined, anything else is read again as an escape of its own
            if let Some(low_code_point) = low.filter(|value| (LOW_SURROGATE_START..=LOW_SURROGATE_END).contains(value)) {
                let joined = SUPPLEMENTARY_START + (((code_point - HIGH_SURROGATE_START) << 10) | (low_code_point - LOW_SURROGATE_START));
                self.position += 2 + UNICODE_ESCAPE_DIGITS;
                out.push_code_point(joined);
                return Ok(());
            }
        }

        out.push_code_point(code_point);
        Ok(())
    }

    /// Consumes the ASCII digits at the current position, returning how many there were.
    fn skip_digits(&mut self) -> usize {
        let start = self.position;
        while self.peek().is_some_and(|byte| byte.is_ascii_digit()) {
            self.position += 1;
        }
        self.position - start
    }

    /// Parses a number, which is an integer unless it has a fraction or an exponent.
    fn parse_number(&mut self) -> Result<B::Value, ParseError<B::Error>> {
        let start = self.position;

        if self.peek() == Some(b'-') {
            self.position += 1;
        }

        // A leading zero is a number of its own, and anything after it is not part of the integer
        match self.peek() {
            Some(b'0') => self.position += 1,
            Some(b'1'..=b'9') => {
                self.skip_digits();
            }
            _ => return Err(ParseError::Syntax(start)),
        }

        let mut is_float = false;
        is_float |= self.take_fraction();
        is_float |= self.take_exponent();

        let literal = self.text.get(start..self.position).ok_or(ParseError::Syntax(start))?;

        let out = if is_float {
            self.builder.float(literal)
        } else {
            self.builder.integer(literal)
        };
        out.map_err(ParseError::Build)
    }

    /// Consumes a fraction, which is only part of the number if at least one digit follows the dot.
    fn take_fraction(&mut self) -> bool {
        let is_fraction = self.peek() == Some(b'.') && self.bytes.get(self.position + 1).is_some_and(u8::is_ascii_digit);
        if is_fraction {
            self.position += 1;
            self.skip_digits();
        }
        is_fraction
    }

    /// Consumes an exponent, which is only part of the number if at least one digit follows its sign.
    fn take_exponent(&mut self) -> bool {
        if !matches!(self.peek(), Some(b'e' | b'E')) {
            return false;
        }

        let mut digits_at = self.position + 1;
        if matches!(self.bytes.get(digits_at), Some(b'+' | b'-')) {
            digits_at += 1;
        }

        if !self.bytes.get(digits_at).is_some_and(u8::is_ascii_digit) {
            return false;
        }

        self.position = digits_at;
        self.skip_digits();
        true
    }
}
