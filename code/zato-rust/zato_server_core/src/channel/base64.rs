//! Base64 decoding with the rules of `base64.b64decode` of Python in its default, non-validating mode.
//!
//! Characters outside of the standard alphabet are skipped, a padding sequence ends the input once it
//! completes a quad, and a final quad of one character or of two or three characters without enough
//! padding is an error, as in `binascii.a2b_base64` with `strict_mode=False`.

/// The padding character.
const PAD: u8 = b'=';

/// Number of characters in one quad.
const QUAD_LENGTH: usize = 4;

/// Position in a quad from which a padding sequence can complete it.
const MIN_PADDED_QUAD_POSITION: usize = 2;

/// Reason why a text could not be decoded.
#[derive(Debug, PartialEq, Eq)]
pub enum Base64Error {
    /// The text contains a character outside of ASCII.
    NonAscii,

    /// The last quad has exactly one data character.
    ExcessCharacter,

    /// The last quad is incomplete and not padded.
    IncorrectPadding,
}

/// Returns the value of one character of the standard alphabet.
const fn alphabet_value(byte: u8) -> Option<u8> {
    match byte {
        b'A'..=b'Z' => Some(byte - b'A'),
        b'a'..=b'z' => Some(byte - b'a' + 26),
        b'0'..=b'9' => Some(byte - b'0' + 52),
        b'+' => Some(62),
        b'/' => Some(63),
        _ => None,
    }
}

/// Decodes a text, skipping characters outside of the alphabet.
pub fn decode_lenient(text: &str) -> Result<Vec<u8>, Base64Error> {
    if !text.is_ascii() {
        return Err(Base64Error::NonAscii);
    }

    let mut out = Vec::with_capacity(text.len() / QUAD_LENGTH * 3 + 3);
    let mut quad_position: usize = 0;
    let mut pads: usize = 0;
    let mut left: u8 = 0;

    for byte in text.bytes() {
        if byte == PAD {
            // Padding counts only once at least two data characters of the quad are in
            if quad_position >= MIN_PADDED_QUAD_POSITION {
                pads += 1;
                if quad_position + pads >= QUAD_LENGTH {
                    return Ok(out);
                }
            }
            continue;
        }

        let Some(value) = alphabet_value(byte) else { continue };
        pads = 0;

        match quad_position {
            0 => {
                left = value;
                quad_position = 1;
            }
            1 => {
                out.push((left << 2) | (value >> 4));
                left = value & 0x0F;
                quad_position = 2;
            }
            2 => {
                out.push((left << 4) | (value >> 2));
                left = value & 0x03;
                quad_position = 3;
            }
            _ => {
                out.push((left << 6) | value);
                left = 0;
                quad_position = 0;
            }
        }
    }

    match quad_position {
        0 => Ok(out),
        1 => Err(Base64Error::ExcessCharacter),
        _ => Err(Base64Error::IncorrectPadding),
    }
}
