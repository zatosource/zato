//! Canonical forms of request paths and Accept headers that REST channels are matched against.

/// Accept header value that a request without an Accept header is matched as.
pub const ACCEPT_ANY_HTTP: &str = "*/*";

/// Marker that stands for `*` in the internal form of an Accept header.
pub const ACCEPT_ANY_INTERNAL: &str = "haany";

/// Marker that stands for `/` in the internal form of an Accept header.
pub const ACCEPT_SEPARATOR_INTERNAL: &str = "HTTP_SEP";

/// Internal form of `*/*`, the Accept value of a channel that accepts any media type.
pub const ACCEPT_ANY_PAIR: &str = "haanyHTTP_SEPhaany";

/// Spelling of a slash that is part of one path segment rather than a separator.
const ENCODED_SLASH: &str = "%2F";

/// Separator of path segments.
const SEGMENT_SEPARATOR: char = '/';

/// A path segment that stands for the segment it sits in.
const CURRENT_SEGMENT: &str = ".";

/// A path segment that cancels the segment in front of it.
const PARENT_SEGMENT: &str = "..";

/// Byte that introduces a percent-encoded octet.
const PERCENT: u8 = b'%';

/// Returns the internal form of an Accept header, which channel definitions and requests are both turned into.
///
/// A missing or empty header stands for `*/*`.
pub fn to_internal_accept(http_accept: Option<&str>) -> String {
    let source = match http_accept {
        Some(value) if !value.is_empty() => value,
        _ => ACCEPT_ANY_HTTP,
    };

    let with_any = source.replace('*', ACCEPT_ANY_INTERNAL);
    with_any.replace(SEGMENT_SEPARATOR, ACCEPT_SEPARATOR_INTERNAL)
}

/// Returns the canonical form of a request path that channels are matched against.
///
/// Empty and dot segments are resolved first, then each remaining segment is percent-decoded
/// on its own, with a decoded slash kept encoded. A trailing slash is preserved.
pub fn normalize_path_info(path_info: &str) -> String {
    let mut segments: Vec<String> = Vec::new();

    for segment in path_info.split(SEGMENT_SEPARATOR) {
        // Empty segments come from the leading slash or from two slashes in a row
        if segment.is_empty() || segment == CURRENT_SEGMENT {
            continue;
        }

        // A parent segment removes the previous one and never goes above the root
        if segment == PARENT_SEGMENT {
            segments.pop();
            continue;
        }

        let decoded = unquote(segment);
        segments.push(decoded.replace(SEGMENT_SEPARATOR, ENCODED_SLASH));
    }

    let joined = segments.join("/");

    let mut out = String::with_capacity(joined.len() + 2);
    out.push(SEGMENT_SEPARATOR);
    out.push_str(&joined);

    // A channel path may end with a slash, so a request path keeps one it had
    if path_info.ends_with(SEGMENT_SEPARATOR) && out.len() > 1 {
        out.push(SEGMENT_SEPARATOR);
    }

    out
}

/// Percent-decodes one path segment the way `urllib.parse.unquote` does.
///
/// Each run of ASCII characters is decoded on its own as UTF-8, with every invalid sequence
/// replaced by U+FFFD, and non-ASCII characters pass through unchanged.
pub fn unquote(segment: &str) -> String {
    if !segment.contains('%') {
        return segment.to_owned();
    }

    let mut out = String::with_capacity(segment.len());
    let mut rest = segment;

    while !rest.is_empty() {
        let ascii_len = rest.bytes().take_while(u8::is_ascii).count();

        // A run of non-ASCII characters is copied as it is ..
        if ascii_len == 0 {
            let non_ascii_len = rest
                .char_indices()
                .find(|(_, character)| character.is_ascii())
                .map_or(rest.len(), |(index, _)| index);
            let (non_ascii, tail) = rest.split_at(non_ascii_len);
            out.push_str(non_ascii);
            rest = tail;
            continue;
        }

        // .. and a run of ASCII characters is decoded as a whole.
        let (ascii_run, tail) = rest.split_at(ascii_len);
        let decoded = percent_decode(ascii_run.as_bytes());
        out.push_str(&String::from_utf8_lossy(&decoded));
        rest = tail;
    }

    out
}

/// Returns the value of one hexadecimal digit, if the byte is one.
const fn hex_value(byte: u8) -> Option<u8> {
    match byte {
        b'0'..=b'9' => Some(byte - b'0'),
        b'a'..=b'f' => Some(byte - b'a' + 10),
        b'A'..=b'F' => Some(byte - b'A' + 10),
        _ => None,
    }
}

/// Decodes every `%XX` octet of the input, leaving a `%` that is not followed by two hex digits as it is.
fn percent_decode(input: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(input.len());
    let mut parts = input.split(|byte| *byte == PERCENT);

    if let Some(first) = parts.next() {
        out.extend_from_slice(first);
    }

    for part in parts {
        let high = part.first().copied().and_then(hex_value);
        let low = part.get(1).copied().and_then(hex_value);

        if let (Some(high_value), Some(low_value), Some(remainder)) = (high, low, part.get(2..)) {
            out.push((high_value << 4) | low_value);
            out.extend_from_slice(remainder);
        } else {
            // Without two hex digits after it, the percent sign is literal text
            out.push(PERCENT);
            out.extend_from_slice(part);
        }
    }

    out
}
