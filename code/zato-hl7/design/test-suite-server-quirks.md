# Test suite for ServerQuirks

All tests use the same TCP black-box approach as the main server test suite.
Each test starts a server with specific quirks enabled via its `.ini` file, sends a malformed message, and verifies the server handles it correctly.

## Helpers

Reuses all helpers from `conftest.py`. Each `.ini` file gains a `[quirks]` section with the relevant flags.

## 1. LF normalization (`normalize_lf_to_cr`)

### 1.1 Message with LF segment separators

Enable `normalize_lf_to_cr`. Send a message where all `0x0D` are replaced with `0x0A`.
Verify the callback receives the payload with `0x0D` segment separators restored.
Verify an AA ACK is returned with correct control id.

### 1.2 Message with mixed CR and LF

Enable `normalize_lf_to_cr`. Send a message where some segments use CR and others use LF.
Verify the callback receives the payload with all segment separators as CR.

### 1.3 LF normalization disabled (default)

Do not enable the quirk. Send a message with LF separators.
Verify the callback receives the raw bytes unchanged (LF preserved as-is).

## 2. CRLF normalization (`normalize_crlf_to_cr`)

### 2.1 Message with CRLF segment separators

Enable `normalize_crlf_to_cr`. Send a message where all segment separators are `0x0D 0x0A`.
Verify the callback receives the payload with single `0x0D` separators.
Verify the ACK control id is correct.

### 2.2 CRLF and LF both enabled

Enable both `normalize_crlf_to_cr` and `normalize_lf_to_cr`. Send a message mixing CRLF and bare LF.
Verify all segment separators become single CR.

### 2.3 CRLF normalization disabled (default)

Do not enable the quirk. Send a message with CRLF separators.
Verify the callback receives raw bytes unchanged.

## 3. MSH-2 encoding character padding (`pad_msh2_encoding_chars`)

### 3.1 MSH-2 with 2 characters

Enable `pad_msh2_encoding_chars`. Send `MSH|^&|...` (only component and subcomponent separators, missing ~ and \).
Verify the callback receives a payload where MSH-2 has been padded to `^~\&`.
Verify the ACK uses `^~\&` as encoding characters.

### 3.2 MSH-2 with 3 characters

Enable the quirk. Send `MSH|^\&|...` (missing repetition separator).
Verify MSH-2 is padded to `^~\&`.

### 3.3 MSH-2 with only component separator

Enable the quirk. Send `MSH|^|...`.
Verify MSH-2 is padded to `^~\&`.

### 3.4 MSH-2 with double tilde

Enable the quirk. Send `MSH|^~~&|...`.
This is 4 characters already so no padding should occur.
Verify the callback receives the original `^~~&` unchanged.

### 3.5 MSH-2 empty

Enable the quirk. Send `MSH||...` (MSH-2 completely empty).
Verify MSH-2 is set to the full `^~\&` default.

### 3.6 Padding disabled (default)

Do not enable the quirk. Send `MSH|^&|...`.
Verify the callback receives the raw bytes unchanged, MSH-2 remains `^&`.

## 4. Truncated MSH repair (`fix_truncated_msh`)

### 4.1 MSH with only 4 fields

Enable `fix_truncated_msh`. Send a message where MSH has only `MSH|^~\&|SendApp|SendFac` (4 fields after split).
Verify the callback receives a payload where MSH has been extended with empty/default fields.
Verify an ACK is returned (not garbage).

### 4.2 MSH missing control id and version

Enable the quirk. Send a message with MSH-9 (message type) present but MSH-10 (control id) and MSH-12 (version) missing.
Verify the ACK uses the default control id (`0`) and version (`2.5`).

### 4.3 Truncated MSH - just "MSH|^~\&"

Enable the quirk. Send `MSH|^~\&` followed by CR and a PID segment.
Verify the server does not crash and returns an ACK.

### 4.4 Repair disabled (default)

Do not enable the quirk. Send a truncated MSH.
Verify the callback receives raw bytes unchanged. The ACK may have empty fields but the server must not crash.

## 5. Leading whitespace stripping (`strip_leading_whitespace_from_fields`)

### 5.1 Control id with leading space

Enable `strip_leading_whitespace_from_fields`. Send a message where MSH-10 is ` CTRL001` (leading space).
Verify the ACK's MSA-2 contains `CTRL001` (no leading space).

### 5.2 Sending app with leading spaces

Enable the quirk. Send a message where MSH-3 is `  MyApp`.
Verify the ACK's MSH-5 (receiving app, swapped from sender) is `MyApp`.

### 5.3 Stripping disabled (default)

Do not enable the quirk. Send a message with ` CTRL001`.
Verify the ACK's MSA-2 preserves the leading space.

## 6. MSH prepend if missing (`prepend_msh_if_missing`)

### 6.1 Truncated "SH|" prefix

Enable `prepend_msh_if_missing`. Send a payload starting with `SH|^~\&|SendApp|...`.
Verify the callback receives a payload starting with `MSH|^~\&|SendApp|...`.

### 6.2 Garbage prefix before MSH

Enable the quirk. Send `ORU_R01|MSH|^~\&|Lab|...` (structure name prepended before MSH).
Verify the callback receives a payload starting with `MSH|^~\&|Lab|...`.

### 6.3 No MSH anywhere

Enable the quirk. Send `PID|1||MRN123||DOE^JOHN` (no MSH at all).
Verify the server handles it gracefully - either delivers as-is or returns an AR NAK.

### 6.4 Prepend disabled (default)

Do not enable the quirk. Send `SH|^~\&|...`.
Verify the callback receives the raw bytes unchanged.

## 7. Concatenated message splitting (`normalize_concatenated_messages`)

### 7.1 Two messages concatenated

Enable `normalize_concatenated_messages`. Send a single MLLP frame containing two complete HL7 messages (two MSH segments, each followed by PID and other segments).
Verify the callback is invoked twice, once for each message.
Verify an ACK is returned for each.

### 7.2 Three messages concatenated

Enable the quirk. Send three concatenated messages in one MLLP frame.
Verify the callback is invoked three times.

### 7.3 Second message has different control id

Enable the quirk. Send two concatenated messages with control ids `CAT_001` and `CAT_002`.
Verify each callback invocation receives the correct payload and the ACKs reference the correct control ids.

### 7.4 Splitting disabled (default)

Do not enable the quirk. Send two concatenated messages.
Verify the callback is invoked once with the entire blob as a single payload.

## 8. ACK field length capping (`max_ack_field_len`)

### 8.1 Oversized sending app field

Set `max_ack_field_len = 50`. Send a message where MSH-3 (sending app) is 500 bytes of `A`.
Verify the ACK's MSH-5 (receiving app, swapped) is truncated to 50 bytes.

### 8.2 Oversized control id

Set `max_ack_field_len = 20`. Send a message where MSH-10 is 1000 bytes of `X`.
Verify the ACK's MSA-2 (control id) is truncated to 20 bytes.

### 8.3 Default cap (200)

Use default `max_ack_field_len = 200`. Send a message where MSH-3 is 300 bytes.
Verify the ACK's MSH-5 is truncated to 200 bytes.

### 8.4 Cap disabled

Set `max_ack_field_len = 0`. Send a message where MSH-3 is 500 bytes.
Verify the ACK's MSH-5 is the full 500 bytes (no truncation).

## 9. Combined quirks

### 9.1 CRLF normalization and truncated MSH repair

Enable both `normalize_crlf_to_cr` and `fix_truncated_msh`.
Send a message with CRLF line endings and a truncated MSH (only 6 fields).
Verify the callback receives CR-normalized payload with a repaired MSH.

### 9.2 LF normalization and MSH-2 padding

Enable both `normalize_lf_to_cr` and `pad_msh2_encoding_chars`.
Send a message with LF line endings and MSH-2 = `^&`.
Verify the callback receives CR-normalized payload with MSH-2 padded to `^~\&`.

### 9.3 All quirks enabled at once

Enable every quirk. Send a message with LF endings, truncated MSH-2 (`^`), missing MSH-10, and a leading space in MSH-3.
Verify the callback receives a fully normalized payload.
Verify the ACK is well-formed.

### 9.4 No quirks (all defaults)

Send the same malformed message with all quirks disabled.
Verify the callback receives raw bytes unchanged and the server does not crash.

## 10. Quirks exposed in zato_ctx

### 10.1 Quirks visible to callback

Enable `normalize_lf_to_cr` and `pad_msh2_encoding_chars`.
Verify `zato_ctx['zato.channel_item']['server_quirks']` is the `ServerQuirks` instance with the correct flags.

### 10.2 Default quirks visible

Use all defaults. Verify `server_quirks` is present with all fields at their default values.
