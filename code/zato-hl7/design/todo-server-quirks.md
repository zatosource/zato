# Server quirks - todo

## ServerQuirks dataclass

A dataclass with boolean and value flags, configurable per connection.
The server receives a `ServerQuirks` instance as part of its config. Before invoking the callback and before building ACKs,
the server applies whichever normalizations the active quirks require.

Located in `zato/hl7/mllp/server.py`.

### Fields

- `normalize_lf_to_cr` (bool, default True) -
  replace 0x0A (LF) with 0x0D (CR) in the raw payload before processing.

  The HL7 v2 spec mandates 0x0D (CR) as the segment separator but many production systems,
  especially those running on Linux, use 0x0A (LF) instead. This is the most common
  HL7 encoding issue - a message arrives looking correct in a text editor but fails to parse
  because 0x0A is not recognized as a segment boundary. For example, a lab system sends:

  ```
  MSH|^~\&|LABADT|DH|RCVADT|DH|201301011228||ACK^A01^ACK|HL7ACK00001|P|2.3\nMSA|AA|HL7MSG00001
  ```

  The parser reads MSH-12 as "2.3\nMSA" because 0x0A is not a segment terminator in HL7.
  With this quirk enabled, the server replaces every 0x0A with 0x0D before handing the payload
  to the callback, so the message becomes properly segmented.

  Default is True because this is the single most common encoding mistake in HL7 production
  traffic and the fix is always correct - the HL7 v2 spec never uses 0x0A for anything,
  so replacing it with 0x0D cannot break a well-formed message.

- `normalize_crlf_to_cr` (bool, default True) -
  replace 0x0D 0x0A (CRLF) with 0x0D (CR) in the raw payload before processing.

  Windows-based HL7 systems often emit CRLF line endings. When this hits an HL7 parser that
  expects bare CR, each segment gets a spurious 0x0A at the start, shifting field positions
  and sometimes truncating segment names. For example, a PID segment ends up being read as
  "\nPID" (the 0x0A leaking from the previous line's CRLF), causing the segment name to
  start with a linefeed. With this quirk enabled,
  every CRLF pair is collapsed to a single CR.

  Default is True because CRLF in HL7 payloads is always a line-ending artifact from
  Windows-based senders. The HL7 v2 spec does not use CRLF anywhere, so collapsing it
  to CR cannot break a correctly-formed message.

- `pad_msh2_encoding_chars` (bool, default True) -
  if MSH-2 has fewer than 4 encoding characters, right-pad with the standard defaults (^~\&).

  The HL7 spec requires exactly 4 encoding characters in MSH-2: component separator (^),
  repetition separator (~), escape character (\), and subcomponent separator (&).
  In practice, production systems routinely send fewer. Real examples:

  - `MSH|^&|...` - only 2 characters, missing ~ and \. From an ADL system sending ADT^A01 v2.1.
  - `MSH|^\&|...` - only 3 characters, missing ~. From an immunization registry submission system.
  - `MSH|^~|...` - only 2 characters, missing \ and &. From a vaccine management system.
  - `MSH||...` - MSH-2 completely empty. From a document management system.

  When the encoding characters are incomplete, any parser that tries to split on the repetition
  separator or escape character will either crash or silently produce wrong results.
  With this quirk enabled, the server pads MSH-2 to 4 characters using the standard defaults
  before handing the payload to the callback. For example, ^& becomes ^~\&.

  Default is True because incomplete MSH-2 is common in older v2.1 and v2.2 systems,
  and the fix only appends missing standard characters - it never removes or replaces
  anything the sender provided. The theoretical risk of a sender intentionally using
  fewer encoding characters (e.g. never using repetitions and deliberately omitting ~)
  is near zero in practice.

- `fix_truncated_msh` (bool, default True) -
  if the MSH segment has fewer fields than required for ACK building
  (missing MSH-9, MSH-10, MSH-12), fill them with safe defaults
  so _build_ack does not produce malformed output.

  Some production systems send MSH segments with critical fields completely absent.
  Real examples:

  - `MSH|||WHNT_DOC_PDF|WHNT|MMF|POSTIMAGE` - MSH-2 (encoding chars), MSH-7 (datetime),
    MSH-9 (message type), MSH-10 (control id), MSH-11 (processing id), and MSH-12 (version)
    are all missing. From a document PDF delivery system.
  - `MSH|^~\\&|SendingApp|Dignityhealth|ReceivingApp|Bannerhealth||||123456|P|2.3` - MSH-7
    and MSH-9 are both empty.

  Without this quirk, _build_ack tries to read fields that do not exist, producing an ACK
  with empty or malformed values. With it enabled, the server fills missing fields with safe
  defaults: MSH-9 = "ACK", MSH-10 = "0", MSH-11 = "P", MSH-12 = "2.5".

  Default is True because without it, the server produces broken ACK responses for any
  message with a short MSH. The defaults are conservative and match what most HL7 systems
  expect to see in an ACK.

- `strip_leading_whitespace_from_fields` (bool, default True) -
  strip leading whitespace from MSH-10 (control id) and other fields used in ACK construction.

  Some systems emit MSH-10 with a leading space, e.g. " CONTROLID" instead of "CONTROLID".
  The leading space propagates into
  the ACK's MSA-2 field, which can cause the sending system to fail to match the ACK to
  the original message. With this quirk enabled, the server strips leading whitespace from
  all MSH fields used in ACK construction (MSH-3 through MSH-6, MSH-10, MSH-12).

  Default is True because no valid HL7 field value starts with a space,
  so the transformation is harmless for correctly-formed messages. The only
  scenario where this could interfere is byte-level auditing or digital signatures
  over the raw MSH content, which is essentially nonexistent in practice with HL7 v2.

- `prepend_msh_if_missing` (bool, default False) -
  if the payload does not start with MSH, but does contain an MSH segment somewhere,
  attempt to locate and extract it.

  Two real-world scenarios:

  1. A sender drops the leading "M" from MSH, sending `SH|^~\&|...` instead
     of `MSH|^~\&|...`.

  2. A template rendering issue prepends the message structure name before MSH, producing
     `ORU_R01|MSH|^~\&|GHH LAB|...`. The actual HL7 message starts after the extra prefix.

  With this quirk enabled, the server checks for these patterns. If the payload starts with
  `SH|`, it prepends `M`. If the payload starts with something else but contains `MSH|`
  further in, it strips the leading bytes before MSH.

  Default is False because this is a content-altering transformation that guesses what
  the sender meant. If a non-HL7 payload happens to contain `MSH|` somewhere in its body,
  the server would incorrectly strip everything before it and treat the remainder as an
  HL7 message. Only enable this for connections with known broken senders.

- `normalize_concatenated_messages` (bool, default False) -
  if the payload contains more than one MSH segment (concatenated messages without batch wrapping),
  split on MSH boundaries and deliver each as a separate message to the callback.

  Pharmacy systems and other high-volume senders sometimes concatenate multiple
  HL7 messages into a single TCP write without using the FHS/BHS batch wrapper that the spec
  requires. For example, two RDE^O01 messages from a pharmacy system arrive as one blob:

  ```
  MSH|^~\&|xxx|PHARM|3M|HL7GATE|...|RDE^O01|...|P|2.2
  PID|||0001195409||James||19530908|M
  ...
  MSH|^~\&|xxx|PHARM|3M|HL7GATE|...|RDE^O01|...|P|2.2
  PID|||0001195045||Smith||19730211|M
  ...
  ```

  Without this quirk, the entire blob is delivered to the callback as one message,
  and the second MSH segment is buried inside what looks like a single message payload.
  With it enabled, the server splits on MSH boundaries and invokes the callback once
  per sub-message.

  Default is False because this fundamentally changes message delivery semantics -
  a single MLLP frame can trigger multiple callback invocations instead of one.
  This could surprise existing callback implementations. Additionally, if a legitimate
  HL7 message contains a literal `MSH|` string inside an OBX or NTE segment (e.g. embedded
  reference data), the server would incorrectly split it. Only enable this for connections
  where the sender is known to concatenate messages without batch wrapping.

- `max_ack_field_len` (int, default 200) -
  truncate any single MSH field echoed into the ACK to this many bytes.
  0 means no limit.

  When the server builds an ACK from a malformed or adversarial payload, it echoes
  MSH fields (sending app, facility, control id, etc.) into the response. If the
  inbound payload is malformed, these "fields" can be arbitrarily large - for example,
  if the field separator byte never appears in the payload, the entire payload becomes
  one giant MSH field that gets echoed back. This cap ensures the ACK stays bounded
  regardless of what the server receives.

  Default is 200 because it is generous for any legitimate MSH field (the longest
  real-world values are typically under 50 bytes) while still preventing the server
  from amplifying malformed input into oversized ACK responses. Set to 0 to disable
  the cap entirely, though this is not recommended for production.

## Implementation tasks

### 1. Create the ServerQuirks dataclass

- Add `ServerQuirks` as a `@dataclass` with the fields above.
- Fields that fix universally incorrect input default to True (`normalize_lf_to_cr`, `normalize_crlf_to_cr`, `pad_msh2_encoding_chars`, `fix_truncated_msh`, `strip_leading_whitespace_from_fields`). Fields that alter message semantics or guess sender intent default to False (`prepend_msh_if_missing`, `normalize_concatenated_messages`). `max_ack_field_len` defaults to 200.
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
- If the payload starts with something else but contains `MSH|` further in, strip everything before it.

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
