//! Checks of the credentials of HTTP Basic Auth, API key and static bearer token definitions.
//!
//! Each check answers only whether the credentials match. Every request whose credentials do not match
//! is handed to the Python dispatcher, which repeats the check and produces the response and log lines.

use super::base64::decode_lenient;

/// Prefix of a Basic Auth Authorization header, compared case-sensitively.
const BASIC_PREFIX: &str = "Basic ";

/// Prefix of a bearer token Authorization header, compared case-insensitively.
const BEARER_PREFIX: &str = "bearer ";

/// Number of characters of the bearer prefix.
const BEARER_PREFIX_CHARS: usize = 7;

/// Separator of the username and the password in decoded Basic Auth credentials.
const BASIC_SEPARATOR: char = ':';

/// First of the information separator characters, which Python counts as whitespace.
const FIRST_INFORMATION_SEPARATOR: char = '\u{1c}';

/// Last of the information separator characters.
const LAST_INFORMATION_SEPARATOR: char = '\u{1f}';

/// Whether `str.isspace` of Python is true for a character.
pub fn python_isspace(character: char) -> bool {
    character.is_whitespace() || (FIRST_INFORMATION_SEPARATOR..=LAST_INFORMATION_SEPARATOR).contains(&character)
}

/// Returns the text without the leading and trailing characters that `str.strip` of Python removes.
pub fn python_strip(text: &str) -> &str {
    text.trim_matches(python_isspace)
}

/// Compares two byte strings in time that depends only on their lengths.
pub fn constant_time_eq(left: &[u8], right: &[u8]) -> bool {
    if left.len() != right.len() {
        return false;
    }

    let difference = left
        .iter()
        .zip(right)
        .fold(0_u8, |accumulated, (left_byte, right_byte)| accumulated | (left_byte ^ right_byte));
    difference == 0
}

/// Returns the username and the password of a Basic Auth header, as `extract_basic_auth` of Python returns them.
pub fn extract_basic_auth(header: &str) -> Option<(String, String)> {
    let encoded = header.strip_prefix(BASIC_PREFIX)?;
    let decoded = decode_lenient(python_strip(encoded)).ok()?;
    let text = String::from_utf8(decoded).ok()?;
    let (username, password) = text.split_once(BASIC_SEPARATOR)?;

    Some((username.to_owned(), password.to_owned()))
}

/// Whether a Basic Auth header has the expected credentials, with the outcome of `check_basic_auth` of Python.
pub fn check_basic_auth(header: Option<&str>, expected_username: &str, expected_password: &str) -> bool {
    let Some((username, password)) = header.and_then(extract_basic_auth) else {
        return false;
    };

    // Python reads an empty username as a failed extraction
    if username.is_empty() {
        return false;
    }

    let is_username_equal = constant_time_eq(username.as_bytes(), expected_username.as_bytes());
    let is_password_equal = constant_time_eq(password.as_bytes(), expected_password.as_bytes());

    is_username_equal && is_password_equal
}

/// Returns the token of a bearer Authorization header, or an empty string, as `extract_bearer_token` of Python does.
pub fn extract_bearer_token(header: &str) -> &str {
    let prefix_end = header
        .char_indices()
        .nth(BEARER_PREFIX_CHARS)
        .map_or(header.len(), |(index, _)| index);
    let (prefix, token) = header.split_at(prefix_end);

    // Only ASCII letters change case into the letters of the prefix
    if !prefix.eq_ignore_ascii_case(BEARER_PREFIX) {
        return "";
    }

    python_strip(token)
}
