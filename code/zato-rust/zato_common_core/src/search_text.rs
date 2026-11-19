//! Extraction of the words that the free-text search of the Zato audit log indexes.
//!
//! The audit log keeps message payloads of integrations - JSON, XML, EDI, HL7 and documents
//! encoded in base64 - and its trigram indexes cover only the words, integers and decimal numbers
//! of a payload, each once, in lower case, rather than the payload itself.

use foldhash::HashSet;
use pyo3::prelude::*;
use pyo3::pybacked::PyBackedStr;

/// The shortest word that a trigram index can match.
const MIN_WORD_CHARS: usize = 3;

/// The longest span of word characters and encoding symbols that is still text rather than encoded data.
const MAX_SPAN_CHARS: usize = 64;

/// What separates two words of the extracted text.
const WORD_SEPARATOR: char = ' ';

/// What separates the integer and the fractional part of a decimal number.
const DECIMAL_POINT: u8 = b'.';

/// The symbols that join word characters into one span - those of base64 and base64url,
/// and those of dotted, dashed and underscored identifiers.
const SPAN_SYMBOLS: [char; 6] = ['+', '/', '=', '.', '-', '_'];

/// Whether a character belongs to a span of text that may be encoded data.
fn is_span_char(character: char) -> bool {
    character.is_alphanumeric() || SPAN_SYMBOLS.contains(&character)
}

/// Whether an ASCII byte belongs to a span of text that may be encoded data.
const fn is_ascii_span_byte(byte: u8) -> bool {
    byte.is_ascii_alphanumeric() || matches!(byte, b'+' | b'/' | b'=' | b'.' | b'-' | b'_')
}

/// Whether a byte ends the integer part of a decimal number that continues after it.
fn is_decimal_point(byte: u8, previous: Option<&u8>, next: Option<&u8>) -> bool {
    let is_after_digit = previous.is_some_and(u8::is_ascii_digit);
    let is_before_digit = next.is_some_and(u8::is_ascii_digit);

    byte == DECIMAL_POINT && is_after_digit && is_before_digit
}

/// The words of one payload, in the order of their first occurrence.
struct Extraction {

    /// The words already added, in lower case.
    seen: HashSet<String>,

    /// The words joined into the text that the search indexes cover.
    text: String,

    /// The current word in lower case, reused from word to word.
    lower: String,
}

impl Extraction {

    /// Adds one word, unless it is too short for a trigram index or was already added.
    fn add_word(&mut self, word: &str) {
        let is_ascii = word.is_ascii();

        // A word shorter than a trigram can never be matched by the index, and an ASCII word has one byte per character
        let is_too_short = if is_ascii {
            word.len() < MIN_WORD_CHARS
        } else {
            word.chars().nth(MIN_WORD_CHARS - 1).is_none()
        };

        if is_too_short {
            return;
        }

        // The lower case is built in a buffer kept across words, so a repeated word allocates nothing ..
        self.lower.clear();

        // .. an ASCII word is lowered in place, byte by byte ..
        if is_ascii {
            self.lower.push_str(word);
            self.lower.make_ascii_lowercase();
        }
        // .. and any other word through the Unicode case mappings of its characters.
        else {
            for character in word.chars() {
                self.lower.extend(character.to_lowercase());
            }
        }

        // Each word is indexed once, however often the payload repeats it
        if self.seen.contains(self.lower.as_str()) {
            return;
        }

        if !self.text.is_empty() {
            self.text.push(WORD_SEPARATOR);
        }

        self.text.push_str(&self.lower);
        let _ = self.seen.insert(self.lower.clone());
    }

    /// Adds the words of one span - its runs of letters and digits, with the decimal points of numbers kept.
    fn add_span(&mut self, span: &str) {
        // A span this long has no separator a person would type, which makes it encoded data, e.g. base64,
        // and a span of no more bytes than the limit cannot have more characters than that either
        if span.len() > MAX_SPAN_CHARS && span.chars().nth(MAX_SPAN_CHARS).is_some() {
            return;
        }

        let bytes = span.as_bytes();
        let mut word_start: Option<usize> = None;

        for (index, &byte) in bytes.iter().enumerate() {
            let previous = index.checked_sub(1).and_then(|previous_index| bytes.get(previous_index));
            let next = bytes.get(index + 1);

            // A word is a run of letters and digits, and a decimal point continues it only between two digits.
            // A span holds no characters other than letters, digits and ASCII symbols, so each of its non-ASCII bytes
            // belongs to a letter or a digit, and a word always starts and ends at the boundary of a character.
            let is_word_byte = !byte.is_ascii() || byte.is_ascii_alphanumeric() || is_decimal_point(byte, previous, next);

            if is_word_byte {
                if word_start.is_none() {
                    word_start = Some(index);
                }
            }
            // Any other byte ends the current word, if there is one
            else if let Some(start) = word_start.take()
                && let Some(word) = span.get(start..index)
            {
                self.add_word(word);
            }
        }

        // The span may end with a word
        if let Some(start) = word_start
            && let Some(word) = span.get(start..)
        {
            self.add_word(word);
        }
    }
}

/// Returns the words, integers and decimal numbers of an audit log payload that the free-text search indexes,
/// each once, in lower case, separated by spaces.
///
/// Spans of encoded data, such as documents in base64, are left out whole, and so are punctuation
/// and the syntax of JSON and XML.
///
/// The words are extracted after the GIL is released, so the other threads of the interpreter run in the meantime.
#[pyfunction]
#[must_use]
pub fn extract_search_text(py: Python<'_>, data: PyBackedStr) -> String {
    py.detach(|| search_text_of(&data))
}

/// Returns the words, integers and decimal numbers of a payload, each once, in lower case, separated by spaces.
pub(crate) fn search_text_of(data: &str) -> String {
    let mut extraction = Extraction {
        seen: HashSet::default(),
        text: String::new(),
        lower: String::new(),
    };

    let bytes = data.as_bytes();
    let mut span_start: Option<usize> = None;
    let mut index = 0;

    // Spans are delimited by anything that is neither a word character nor an encoding symbol
    while let Some(&byte) = bytes.get(index) {
        // An ASCII byte is a character of its own and is classified directly ..
        let (is_span, char_len) = if byte.is_ascii() {
            (is_ascii_span_byte(byte), 1)
        }
        // .. while any other character is decoded first, and the index is always at the start of one
        else if let Some(character) = data.get(index..).and_then(|rest| rest.chars().next()) {
            (is_span_char(character), character.len_utf8())
        } else {
            (false, 1)
        };

        if is_span {
            if span_start.is_none() {
                span_start = Some(index);
            }
        }
        // A character outside of spans ends the current span, if there is one
        else if let Some(start) = span_start.take()
            && let Some(span) = data.get(start..index)
        {
            extraction.add_span(span);
        }

        index += char_len;
    }

    // The payload may end with a span
    if let Some(start) = span_start
        && let Some(span) = data.get(start..)
    {
        extraction.add_span(span);
    }

    extraction.text
}

#[cfg(test)]
mod tests {
    use super::search_text_of;

    #[test]
    fn keeps_words_integers_and_decimal_numbers() {
        let text = search_text_of(r#"{"order": "ORD12345", "total": 1234.50, "city": "Springfield"}"#);
        assert_eq!(text, "order ord12345 total 1234.50 city springfield");
    }

    #[test]
    fn splits_identifiers_into_their_words() {
        let text = search_text_of("INV-2026-00000001 Rechnung_00000001_Berlin.pdf");
        assert_eq!(text, "inv 2026 00000001 rechnung berlin pdf");
    }

    #[test]
    fn leaves_out_encoded_data() {
        let encoded = "JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PC9MZW5ndGggNiAwIFIvRmlsdGVyIC9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nCvkcgrhMlQwtTTVszRUMFAwMjDQszQ1BQAw";
        let text = search_text_of(&format!("<content>{encoded}</content>"));
        assert_eq!(text, "content");
    }

    #[test]
    fn indexes_each_word_once() {
        let text = search_text_of("<Name>John</Name><Name>JOHN</Name><Name>Smith</Name>");
        assert_eq!(text, "name john smith");
    }

    #[test]
    fn leaves_out_words_shorter_than_a_trigram() {
        let text = search_text_of("PID|1||42^^^MRN||Doe^Jane");
        assert_eq!(text, "pid mrn doe jane");
    }
}
