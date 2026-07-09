//! Pure-Rust parser for the IBM MQ MQRFH2 header.
//!
//! An MQRFH2 header starts with a fixed 36-byte structure followed by a variable
//! name-value area made of pairs of a 4-byte length and an XML-like folder string,
//! e.g. `<jms><Dst>queue:///DEV.QUEUE.1</Dst></jms>`. Folder properties are
//! flattened into `folder.property` header names, e.g. `jms.Dst` or `usr.tenant`.

/// Byte length of the fixed part of the MQRFH2 structure.
const FIXED_PART_LENGTH: usize = 36;

/// The `StrucId` field every MQRFH2 header starts with.
const STRUC_ID: &[u8; 4] = b"RFH ";

/// The `Version` field value for MQRFH2 (as opposed to version 1, MQRFH).
const VERSION_2: u32 = 2;

/// Byte offset of the `Version` field within the fixed part.
const VERSION_OFFSET: usize = 4;

/// Byte offset of the `StrucLength` field within the fixed part.
const STRUC_LENGTH_OFFSET: usize = 8;

/// Byte offset of the `Format` field (the format of the body that follows the header).
const FORMAT_OFFSET: usize = 20;

/// Byte length of the `Format` field.
const FORMAT_LENGTH: usize = 8;

/// A parsed MQRFH2 header.
pub struct Rfh2 {

    /// Total byte length of the header, i.e. the offset at which the message body starts.
    pub header_length: usize,

    /// Format of the message body that follows the header, with trailing spaces removed.
    pub body_format: String,

    /// Folder properties flattened into `folder.property` pairs, in document order.
    pub headers: Vec<(String, String)>,
}

/// Reads a `u32` at the given offset with the detected endianness.
fn read_u32(data: &[u8], offset: usize, is_big_endian: bool) -> u32 {
    let bytes = [data[offset], data[offset + 1], data[offset + 2], data[offset + 3]];
    if is_big_endian {
        u32::from_be_bytes(bytes)
    } else {
        u32::from_le_bytes(bytes)
    }
}

/// Returns true if the given message data starts with an MQRFH2 header.
pub fn has_rfh2(data: &[u8]) -> bool {
    data.len() >= FIXED_PART_LENGTH && &data[..4] == STRUC_ID
}

/// Parses an MQRFH2 header from the start of the given message data.
///
/// Returns an error string when the data does not contain a well-formed header.
pub fn parse_rfh2(data: &[u8]) -> Result<Rfh2, String> {
    // The fixed part must be present in full before any field can be read ..
    if data.len() < FIXED_PART_LENGTH {
        return Err(format!("Data too short for an MQRFH2 header: {} bytes", data.len()));
    }

    // .. and it must carry the well-known structure identifier.
    if &data[..4] != STRUC_ID {
        return Err("Data does not start with the MQRFH2 StrucId".to_string());
    }

    // The numeric fields use the byte order of the sending queue manager,
    // so detect it from the Version field which is always exactly 2.
    let is_big_endian = if read_u32(data, VERSION_OFFSET, false) == VERSION_2 {
        false
    } else if read_u32(data, VERSION_OFFSET, true) == VERSION_2 {
        true
    } else {
        return Err("MQRFH2 Version field is not 2 in either byte order".to_string());
    };

    // The total header length tells us where the message body starts ..
    let struc_length = read_u32(data, STRUC_LENGTH_OFFSET, is_big_endian) as usize;

    // .. and it must fit within the data we actually have.
    if struc_length < FIXED_PART_LENGTH || struc_length > data.len() {
        return Err(format!("MQRFH2 StrucLength out of range: {struc_length}"));
    }

    // The Format field describes the body that follows the header.
    let format_bytes = &data[FORMAT_OFFSET..FORMAT_OFFSET + FORMAT_LENGTH];
    let body_format = String::from_utf8_lossy(format_bytes).trim_end().to_string();

    // Walk the name-value area, one length-prefixed folder at a time.
    let mut headers = Vec::new();
    let mut offset = FIXED_PART_LENGTH;

    while offset + 4 <= struc_length {

        // Each folder is preceded by its byte length ..
        let folder_length = read_u32(data, offset, is_big_endian) as usize;
        offset += 4;

        // .. which must not point past the end of the header.
        if offset + folder_length > struc_length {
            return Err(format!("MQRFH2 folder length out of range: {folder_length}"));
        }

        // .. extract the folder string and flatten its properties.
        let folder_bytes = &data[offset..offset + folder_length];
        let folder_string = String::from_utf8_lossy(folder_bytes);
        parse_folder(&folder_string, &mut headers);

        offset += folder_length;
    }

    let out = Rfh2 {
        header_length: struc_length,
        body_format,
        headers,
    };

    Ok(out)
}

/// Parses one XML-like folder string, e.g. `<jms><Dst>queue:///Q1</Dst><Pri>4</Pri></jms>`,
/// appending flattened `folder.property` pairs to the output vector.
fn parse_folder(folder: &str, out: &mut Vec<(String, String)>) {
    // Folders are padded with spaces or NULs to a multiple of four bytes.
    let folder = folder.trim_end_matches(['\0', ' ']);

    // The folder name is the first tag, e.g. `jms` in `<jms>...</jms>` ..
    let Some(name_start) = folder.find('<') else {
        return;
    };
    let after_open = &folder[name_start + 1..];
    let Some(name_end) = after_open.find('>') else {
        return;
    };

    // .. attributes on the folder element itself (like content='properties') are ignored.
    let folder_name_full = &after_open[..name_end];
    let folder_name = folder_name_full.split_whitespace().next().unwrap_or(folder_name_full);

    // Everything between the opening tag and the matching closing tag holds the properties.
    let body_start = name_start + 1 + name_end + 1;
    let closing_tag = format!("</{folder_name}>");
    let Some(body_end) = folder.rfind(&closing_tag) else {
        return;
    };
    if body_end < body_start {
        return;
    }
    let body = &folder[body_start..body_end];

    parse_properties(folder_name, body, out);
}

/// Parses property elements within a folder body, appending `folder.property` pairs.
///
/// Handles `<key>value</key>`, `<key/>` and `<key dt="...">value</key>` forms.
fn parse_properties(folder_name: &str, body: &str, out: &mut Vec<(String, String)>) {
    let mut rest = body;

    while let Some(tag_start) = rest.find('<') {

        // A closing tag at this position means a malformed document, stop here.
        let after_open = &rest[tag_start + 1..];
        if after_open.starts_with('/') {
            return;
        }

        let Some(tag_end) = after_open.find('>') else {
            return;
        };
        let tag_content = &after_open[..tag_end];

        // Self-closing elements like `<key/>` carry an empty value.
        if let Some(stripped) = tag_content.strip_suffix('/') {
            let key = stripped.split_whitespace().next().unwrap_or(stripped);
            out.push((format!("{folder_name}.{key}"), String::new()));
            rest = &after_open[tag_end + 1..];
            continue;
        }

        // Attributes such as dt="string" are not part of the property name.
        let key = tag_content.split_whitespace().next().unwrap_or(tag_content);

        // The value runs until the matching closing tag.
        let value_area = &after_open[tag_end + 1..];
        let closing_tag = format!("</{key}>");
        let Some(value_end) = value_area.find(&closing_tag) else {
            return;
        };

        let value = &value_area[..value_end];
        out.push((format!("{folder_name}.{key}"), value.to_string()));

        rest = &value_area[value_end + closing_tag.len()..];
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Builds an MQRFH2 byte payload with the given folders and body, little-endian.
    fn build_rfh2(folders: &[&str], body: &[u8]) -> Vec<u8> {
        build_rfh2_with_endianness(folders, body, false)
    }

    /// Builds an MQRFH2 byte payload with the given folders and body and byte order.
    fn build_rfh2_with_endianness(folders: &[&str], body: &[u8], is_big_endian: bool) -> Vec<u8> {
        let write_u32 = |value: u32| -> [u8; 4] {
            if is_big_endian {
                value.to_be_bytes()
            } else {
                value.to_le_bytes()
            }
        };

        // Pad each folder to a multiple of four bytes as the real client does.
        let mut name_value_area = Vec::new();
        for folder in folders {
            let mut padded = folder.as_bytes().to_vec();
            while padded.len() % 4 != 0 {
                padded.push(b' ');
            }
            name_value_area.extend_from_slice(&write_u32(padded.len() as u32));
            name_value_area.extend_from_slice(&padded);
        }

        let struc_length = (FIXED_PART_LENGTH + name_value_area.len()) as u32;

        let mut data = Vec::new();
        data.extend_from_slice(STRUC_ID); // StrucId
        data.extend_from_slice(&write_u32(VERSION_2)); // Version
        data.extend_from_slice(&write_u32(struc_length)); // StrucLength
        data.extend_from_slice(&write_u32(273)); // Encoding
        data.extend_from_slice(&write_u32(1208)); // CodedCharSetId
        data.extend_from_slice(b"MQSTR   "); // Format of the body
        data.extend_from_slice(&write_u32(0)); // Flags
        data.extend_from_slice(&write_u32(1208)); // NameValueCCSID
        data.extend_from_slice(&name_value_area);
        data.extend_from_slice(body);

        data
    }

    #[test]
    fn parses_jms_and_usr_folders() {
        let jms = "<jms><Dst>queue:///DEV.QUEUE.1</Dst><Tms>1736450000000</Tms><Dlv>2</Dlv></jms>";
        let usr = "<usr><tenant>acme</tenant><order_type>standard</order_type></usr>";
        let body = b"{\"order_id\": 123}";

        let data = build_rfh2(&[jms, usr], body);
        let parsed = parse_rfh2(&data).expect("header parses");

        assert_eq!(parsed.body_format, "MQSTR");
        assert_eq!(&data[parsed.header_length..], body);

        let headers: std::collections::HashMap<_, _> = parsed.headers.into_iter().collect();
        assert_eq!(headers["jms.Dst"], "queue:///DEV.QUEUE.1");
        assert_eq!(headers["jms.Tms"], "1736450000000");
        assert_eq!(headers["jms.Dlv"], "2");
        assert_eq!(headers["usr.tenant"], "acme");
        assert_eq!(headers["usr.order_type"], "standard");
    }

    #[test]
    fn parses_big_endian_headers() {
        let jms = "<jms><Dst>queue:///REPLIES</Dst></jms>";
        let body = b"reply payload";

        let data = build_rfh2_with_endianness(&[jms], body, true);
        let parsed = parse_rfh2(&data).expect("header parses");

        assert_eq!(&data[parsed.header_length..], body);
        assert_eq!(parsed.headers, vec![("jms.Dst".to_string(), "queue:///REPLIES".to_string())]);
    }

    #[test]
    fn parses_mcd_folder_with_attributes() {
        let mcd = "<mcd><Msd>jms_text</Msd></mcd>";
        let usr = "<usr><priority dt='i4'>7</priority><empty_value/></usr>";
        let body = b"text body";

        let data = build_rfh2(&[mcd, usr], body);
        let parsed = parse_rfh2(&data).expect("header parses");

        let headers: std::collections::HashMap<_, _> = parsed.headers.into_iter().collect();
        assert_eq!(headers["mcd.Msd"], "jms_text");
        assert_eq!(headers["usr.priority"], "7");
        assert_eq!(headers["usr.empty_value"], "");
    }

    #[test]
    fn detects_missing_header() {
        assert!(!has_rfh2(b"{\"plain\": \"json\"}"));
        assert!(parse_rfh2(b"{\"plain\": \"json\", \"padding\": \"0123456789abcdef\"}").is_err());
    }

    #[test]
    fn detects_header_presence() {
        let data = build_rfh2(&["<jms><Dst>queue:///Q1</Dst></jms>"], b"body");
        assert!(has_rfh2(&data));
    }

    #[test]
    fn rejects_truncated_header() {
        let data = build_rfh2(&["<jms><Dst>queue:///Q1</Dst></jms>"], b"body");
        assert!(parse_rfh2(&data[..20]).is_err());
    }

    #[test]
    fn rejects_wrong_version() {
        let mut data = build_rfh2(&[], b"body");
        data[VERSION_OFFSET] = 9;
        assert!(parse_rfh2(&data).is_err());
    }

    #[test]
    fn parses_header_without_folders() {
        let body = b"bare body";
        let data = build_rfh2(&[], body);
        let parsed = parse_rfh2(&data).expect("header parses");

        assert_eq!(parsed.header_length, FIXED_PART_LENGTH);
        assert_eq!(&data[parsed.header_length..], body);
        assert!(parsed.headers.is_empty());
    }
}
