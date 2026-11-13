use proptest::prelude::*;
use zato_server_core::channel::base64::{Base64Error, decode_lenient};

const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

fn encode(input: &[u8]) -> String {
    let mut out = String::new();

    for chunk in input.chunks(3) {
        let first = chunk.first().copied().unwrap_or(0);
        let second = chunk.get(1).copied().unwrap_or(0);
        let third = chunk.get(2).copied().unwrap_or(0);
        let combined = (u32::from(first) << 16) | (u32::from(second) << 8) | u32::from(third);

        for position in 0..4 {
            if position <= chunk.len() {
                let sextet = (combined >> (18 - 6 * position)) & 0x3F;
                let symbol = usize::try_from(sextet).ok().and_then(|index| ALPHABET.get(index));
                if let Some(byte) = symbol {
                    out.push(char::from(*byte));
                }
            } else {
                out.push('=');
            }
        }
    }

    out
}

#[test]
fn credentials_are_decoded() {
    assert_eq!(decode_lenient("dXNlcjpwYXNz").unwrap(), b"user:pass");
}

#[test]
fn padding_ends_the_input() {
    assert_eq!(decode_lenient("YQ==").unwrap(), b"a");
    assert_eq!(decode_lenient("YQ==YWJj").unwrap(), b"a");
    assert_eq!(decode_lenient("YWI=").unwrap(), b"ab");
    assert_eq!(decode_lenient("YQ=====").unwrap(), b"a");
}

#[test]
fn characters_outside_the_alphabet_are_skipped() {
    assert_eq!(decode_lenient("dXNl cjpw\nYXNz").unwrap(), b"user:pass");
    assert_eq!(decode_lenient("dX-Nl_cjpwYXNz").unwrap(), b"user:pass");
}

#[test]
fn incomplete_quads_are_errors() {
    assert_eq!(decode_lenient("Y"), Err(Base64Error::ExcessCharacter));
    assert_eq!(decode_lenient("YQ"), Err(Base64Error::IncorrectPadding));
    assert_eq!(decode_lenient("YQ="), Err(Base64Error::IncorrectPadding));
    assert_eq!(decode_lenient("YWJ"), Err(Base64Error::IncorrectPadding));
    assert_eq!(decode_lenient("YQ=c"), Err(Base64Error::IncorrectPadding));
}

#[test]
fn padding_before_two_characters_is_ignored() {
    assert_eq!(decode_lenient("=YWJj").unwrap(), b"abc");
    assert_eq!(decode_lenient("Y=WJj").unwrap(), b"abc");
}

#[test]
fn non_ascii_text_is_an_error() {
    assert_eq!(decode_lenient("dXNl\u{17c}"), Err(Base64Error::NonAscii));
}

proptest! {

    #[test]
    fn encoded_bytes_decode_back(input in prop::collection::vec(any::<u8>(), 0..64)) {
        let encoded = encode(&input);
        prop_assert_eq!(decode_lenient(&encoded).unwrap(), input);
    }
}
