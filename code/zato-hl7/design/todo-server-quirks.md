# Server quirks - todo

## ServerQuirks dataclass

A dataclass with boolean and value flags, configurable per connection. Every flag defaults to `False` or a safe no-op value.
The server receives a `ServerQuirks` instance as part of its config. Before invoking the callback and before building ACKs,
the server applies whichever normalizations the active quirks require.

Located in `zato/hl7/mllp/server.py` (or a separate `zato/hl7/mllp/quirks.py` imported by the server).

### Fields

| Field | Type | Default | Purpose |
|---|---|---|---|
| `normalize_lf_to_cr` | bool | False | Replace `0x0A` (LF) with `0x0D` (CR) in the raw payload before processing. Fixes messages using Unix line endings instead of HL7-mandated CR. |
| `normalize_crlf_to_cr` | bool | False | Replace `0x0D 0x0A` (CRLF) with `0x0D` (CR) in the raw payload before processing. Fixes messages using Windows line endings. |
| `pad_msh2_encoding_chars` | bool | False | If MSH-2 has fewer than 4 encoding characters, right-pad with the standard defaults (`^~\&`). E.g. `^&` becomes `^~\&`, `^\&` becomes `^~\&`, `^~` becomes `^~\&`. |
| `fix_truncated_msh` | bool | False | If the MSH segment has fewer fields than required for ACK building (missing MSH-9, MSH-10, MSH-12), fill them with safe defaults so `_build_ack` does not produce garbage. |
| `strip_leading_whitespace_from_fields` | bool | False | Strip leading whitespace from MSH-10 (control id) and other fields used in ACK construction. Fixes messages with leading spaces in control ids. |
| `allow_non_standard_field_separator` | bool | False | When True, accept any byte at MSH[3] as the field separator without rejecting the message. The server already does this, but the flag makes it explicit and logged. |
| `prepend_msh_if_missing` | bool | False | If the payload does not start with `MSH`, but does contain a `MSH` segment somewhere (e.g. `ORU_R01\|MSH\|...` or `SH\|...`), attempt to locate and extract it. If the payload starts with `SH\|`, prepend `M`. |
| `normalize_concatenated_messages` | bool | False | If the payload contains more than one `MSH` segment (concatenated messages without batch wrapping), split on `MSH` boundaries and deliver each as a separate message to the callback. |
| `max_ack_field_len` | int | 200 | Truncate any single MSH field echoed into the ACK to this many bytes. Prevents garbage payloads from producing oversized ACKs. 0 means no limit. |

## Implementation tasks

### 1. Create the ServerQuirks dataclass

- Add `ServerQuirks` as a `@dataclass` with the fields above.
- All fields have safe defaults (False/200).
- Add it to `HL7MLLPServer.__init__` as `self.quirks`, sourced from config.

### 2. Add config parsing for quirks

- Extend `load_server_config` in conftest (and the real config loader) to read `[quirks]` section from config.
- Each key maps to a `ServerQuirks` field.

### 3. Implement `normalize_lf_to_cr`

- In `_handle_complete_message`, after extracting the payload and before calling `_run_callback`, if the quirk is enabled, replace `b'\x0a'` with `b'\x0d'` in `request_ctx.data`.
- Must not touch the MLLP framing bytes, only the payload between SB and EB+CR.

### 4. Implement `normalize_crlf_to_cr`

- Same location as above.
- Replace `b'\x0d\x0a'` with `b'\x0d'`.
- Must run before `normalize_lf_to_cr` if both are enabled (otherwise CRLF becomes CR+CR).

### 5. Implement `pad_msh2_encoding_chars`

- In a new `_apply_quirks(raw_payload, quirks)` function called before `_run_callback` and before `_build_ack`.
- Read MSH-2 (bytes between field_sep[0] and field_sep[1]).
- If len < 4, right-pad from the standard `^~\&` characters.
- Rewrite the payload bytes with the corrected MSH-2.

### 6. Implement `fix_truncated_msh`

- In the same `_apply_quirks` function.
- After splitting MSH on field_sep, if fewer than 12 fields, append empty fields up to 12 and set defaults for MSH-9 (`ACK`), MSH-10 (`0`), MSH-11 (`P`), MSH-12 (`2.5`).
- Rebuild the MSH segment and replace it in the payload.

### 7. Implement `strip_leading_whitespace_from_fields`

- In `_build_ack` and `_detect_encoding_from_msh18`, after extracting fields, `.lstrip()` each field used for ACK construction.

### 8. Implement `prepend_msh_if_missing`

- In `_apply_quirks`, check if payload starts with `MSH` + field_sep.
- If not, check for `SH|` prefix (truncated) and prepend `M`.
- If the payload starts with something else but contains `MSH|` further in, strip the leading garbage.

### 9. Implement `normalize_concatenated_messages`

- In `_handle_complete_message`, after extracting the payload, if the quirk is enabled, scan for additional `MSH|` boundaries.
- Split and deliver each sub-message to the callback separately, collecting responses.
- Return the response for the first message (or the last, depending on convention).

### 10. Implement `max_ack_field_len`

- In `_build_ack`, after extracting each field, truncate to `max_ack_field_len` bytes if the value is > 0.

### 11. Pass quirks through the call chain

- `_handle_complete_message` -> `_run_callback` -> `_build_ack` all need access to the quirks instance.
- Pass it through `HandleCompleteMessageArgs` or as a direct attribute on the server instance (already accessible via `self`).

### 12. Add quirks to `zato_ctx`

- Expose the active `ServerQuirks` instance in `zato_ctx['zato.channel_item']['server_quirks']` so callbacks can see which normalizations were applied.
