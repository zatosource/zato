# Test suite for the MLLP server

All tests talk to the server over TCP sockets only.
No test reaches into server internals.
Each test starts a real `HL7MLLPServer` on a random port, connects a plain TCP client, and exercises the protocol.
HL7 messages are built using the `zato_hl7v2` classes (`AdtA01`, `OruR01`, `MSH`, `PID`, `OBX`, etc.) and serialized with `.serialize()` before framing.

## Helpers

A shared test fixture module provides:

- `start_server(callback, **config_overrides)` - spawns a server in a background thread/greenlet on `127.0.0.1:0`, returns `(server, host, port)`. Default callback stores received messages in a thread-safe list and returns `None` (triggering the auto-AA path).
- `tcp_send(host, port, framed_bytes, recv=True)` - opens a TCP socket, sends bytes, optionally reads the response, returns raw bytes.
- `tcp_session(host, port)` - context manager returning a connected socket for multi-message tests on a single connection.
- `frame(payload_bytes)` - wraps raw HL7 bytes in `0x0B ... 0x1C 0x0D`.
- `unframe(data)` - strips MLLP framing, returns payload bytes.
- `build_adt_a01(**overrides)` - returns serialized ADT^A01 bytes using `zato_hl7v2.v2_9.messages.AdtA01`.
- `build_oru_r01(**overrides)` - returns serialized ORU^R01 bytes using `zato_hl7v2.v2_9.messages.OruR01`.
- `build_minimal_msh(msg_type, control_id, **overrides)` - returns raw MSH segment bytes with customizable fields (encoding, version, character set, sender/receiver).
- `parse_ack(raw_bytes)` - extracts MSA-1 (ack code), MSA-2 (control id), and optional ERR-1 from a raw ACK response.

## 1. Connection lifecycle

### 1.1 Accept and immediate disconnect

Client connects then closes without sending anything.
Server logs the disconnection, does not crash, keeps accepting new connections.

### 1.2 Clean single-message exchange

Send one framed ADT^A01, receive a framed ACK, verify MSA-1 is `AA`, verify MSA-2 echoes the original MSH-10 (message control id), verify sender/receiver are swapped in the ACK MSH.

### 1.3 Multiple messages on one connection

Send three framed messages sequentially on the same TCP socket.
Verify three separate ACK responses, each with the correct MSA-2 matching the respective MSH-10.

### 1.4 Interleaved connections

Open two TCP connections simultaneously.
Send a message on each, verify both get correct independent ACKs.

### 1.5 Server stop while connections are active

Connect, send a message, then call `server.stop()`.
Verify the response arrives before the server shuts down.
Verify a subsequent connection attempt is refused.

## 2. MLLP framing

### 2.1 Missing start byte (0x0B)

Send payload bytes without the leading `0x0B`.
Server must close the connection (no response).

### 2.2 Missing end sequence (0x1C 0x0D)

Send `0x0B` + payload but never send `0x1C 0x0D`.
After `recv_timeout` expires, connection idles. After `idle_timeout`, server closes it.

### 2.3 Double start byte

Send `0x0B 0x0B` + payload + `0x1C 0x0D`.
Server must reject (duplicate header detected).

### 2.4 Bare 0x1C inside payload

Build a message where an OBX observation value field contains a literal `0x1C` byte (not followed by `0x0D`).
Frame it properly. Server must deliver the complete message to the callback without truncation.

### 2.5 End sequence split across TCP segments

Send the framed message in two parts: everything up to and including the `0x1C` byte in one `send()`, the trailing `0x0D` in a second `send()`.
Server must still recognize the complete message and return an ACK.

### 2.6 Start byte split across TCP segments (multi-byte start_seq)

Configure the server with a two-byte `start_seq`.
Send the first byte in one `send()`, the second byte plus the rest of the message in the next.
Server must still accept the message.

### 2.7 Extra bytes after end sequence (residual)

Send two properly framed messages concatenated in a single `send()`.
Server must process both messages and return two ACKs.

### 2.8 Three messages pipelined in a single TCP write

Concatenate three framed messages into a single `send()`.
Verify three ACKs are returned, each with the correct control id.

## 3. Message encoding (MSH-18)

### 3.1 UTF-8 declared in MSH-18

Build a message with `MSH-18 = UNICODE UTF-8` and a PID patient name containing multi-byte UTF-8 characters (e.g. `Müller`).
Verify callback receives correctly decoded data and ACK is returned.

### 3.2 ISO-8859-1 declared in MSH-18

Build a message with `MSH-18 = 8859/1` and a PID patient name containing a Latin-1 character (e.g. `\xe9` for e-acute).
Verify correct delivery.

### 3.3 Empty MSH-18 (default encoding)

Build a message with no MSH-18 field.
Verify the server defaults to ISO-8859-1.

### 3.4 Unknown MSH-18 value

Build a message with `MSH-18 = NONEXISTENT`.
Verify the server falls back to ISO-8859-1 rather than crashing.

### 3.5 MSH-18 with repetition separator

Build a message with `MSH-18 = ASCII~ISO IR87`.
Verify the server picks the first recognized encoding (ASCII).

### 3.6 Japanese encoding (ISO IR87)

Build a message with `MSH-18 = ISO IR87` and payload containing ISO-2022-JP encoded text.
Verify callback receives the bytes, ACK is returned.

## 4. ACK generation

### 4.1 Callback returns None

Configure callback to return `None`.
Send a message and verify the response contains an auto-generated AA ACK with correct MSH-10 echo.

### 4.2 Callback returns empty bytes

Configure callback to return `b''`.
Same verification as 4.1.

### 4.3 Callback returns custom response bytes

Configure callback to return a custom ACK with `MSA-1 = AA` and an application-specific NTE segment.
Verify the raw response bytes are framed and returned as-is (not double-ACK'd).

### 4.4 Callback returns zato_hl7v2 HL7Message object

Configure callback to return an `HL7Message` instance (e.g. an ACK built via `zato_hl7v2`).
Verify the response is the `.serialize()` output of that object, properly framed.

### 4.5 Callback returns a string

Configure callback to return a plain string `'MSH|...'`.
Verify it is encoded using the detected MSH-18 encoding and framed.

### 4.6 Callback raises an exception

Configure callback to raise `ValueError('test failure')`.
Verify the response contains an AE NAK: MSA-1 is `AE`, MSA-2 echoes the control id, and ERR segment contains the error text.

### 4.7 Callback raises on first message, succeeds on second

Same connection, two messages.
First callback invocation raises, second returns None.
Verify first response is AE NAK, second is AA ACK.
Connection must remain open after the NAK.

### 4.8 ACK sender/receiver swap

Send ADT^A01 with `MSH-3=AppA`, `MSH-4=FacA`, `MSH-5=AppB`, `MSH-6=FacB`.
Verify the ACK has `MSH-3=AppB`, `MSH-4=FacB`, `MSH-5=AppA`, `MSH-6=FacA`.

### 4.9 ACK preserves HL7 version from inbound MSH-12

Send a message with `MSH-12 = 2.3`.
Verify the ACK MSH-12 is also `2.3`.

## 5. TCP keepalive

### 5.1 Keepalive socket options are set

After connection is established, read back `SO_KEEPALIVE`, `TCP_KEEPIDLE`, `TCP_KEEPINTVL`, `TCP_KEEPCNT` from the server-side socket.
Verify they match the configured values.
(Requires the callback to capture `conn_ctx.socket` and expose it.)

## 6. Idle timeout

### 6.1 Connection closed after idle timeout

Configure `idle_timeout = 2`, `recv_timeout = 1`.
Connect, send nothing.
Verify the connection is closed by the server within 3 seconds.

### 6.2 Idle timer resets on message

Configure `idle_timeout = 3`, `recv_timeout = 1`.
Connect, send a message at t=0, sleep 2 seconds, send another message.
Verify the connection is still alive after the second message (timer reset).

### 6.3 Idle timeout disabled

Configure `idle_timeout = 0`.
Connect, wait 5 seconds, send a message.
Verify the message is still processed.

## 7. Connection error handling

### 7.1 Client disconnects mid-message

Send `0x0B` + half of a message payload, then close the socket.
Server must detect the disconnect and log it without crashing.

### 7.2 Client sends zero bytes (empty recv)

Connect, then shut down the write side of the socket with `shutdown(SHUT_WR)`.
Server must detect the disconnect and close the connection.

### 7.3 Server sendall fails (broken pipe)

Configure callback to close the client socket from a second thread before the server can send the response.
Server must catch the `ConnectionError` on `sendall` and not crash.

### 7.4 Unrecoverable exception in recv loop

Configure the server so that `socket.recv` raises `OSError` (simulated by shutting down the socket externally).
Server must log and close the connection.

## 8. Protocol rejection with AR NAK

### 8.1 Missing header triggers AR NAK

Send data without `0x0B` prefix.
Server should attempt to send an AR NAK before closing (best-effort, the data may not be parseable as HL7).

### 8.2 Duplicate header triggers AR NAK

Send `0x0B` + payload + `0x0B` + more data + `0x1C 0x0D`.
Server should attempt AR NAK before closing.

## 9. Large messages

### 9.1 Message larger than read buffer

Build a message with an OBX value containing 10,000 bytes of observation data.
Frame and send it.
Verify the complete message is delivered to the callback and ACK is returned.

### 9.2 Message spanning many recv calls

Configure `read_buffer_size = 64`.
Send a 4 KB framed message.
Verify correct delivery (message reassembled across ~64 recv calls).

### 9.3 Very large message (1 MB payload)

Build a message with a 1 MB OBX field.
Verify complete delivery and ACK.

### 9.4 Very large message (100 MB payload)

Build a message with a 100 MB OBX field.
Verify complete delivery and ACK. No artificial size limit in the server.

## 10. Message types

Each of these sends a properly structured HL7 v2 message built using `zato_hl7v2` classes, verifying the server handles diverse real-world message types.

### 10.1 ADT^A01 - patient admit

Full ADT^A01 with MSH, EVN, PID, PV1 segments.

### 10.2 ADT^A02 - patient transfer

Full ADT^A02 with MSH, EVN, PID, PV1.

### 10.3 ADT^A03 - patient discharge

Full ADT^A03 with MSH, EVN, PID, PV1.

### 10.4 ADT^A08 - patient update

Update demographics message.

### 10.5 ORU^R01 - observation result

Lab result with MSH, PID, OBR, OBX segments. OBX carries a numeric lab value.

### 10.6 ORM^O01 - order message

Pharmacy or lab order message.

### 10.7 ADT^A01 with multiple OBX segments

ADT with embedded observation data, verifying multi-segment messages.

### 10.8 Message with NTE (notes) segments

Message containing free-text NTE segments.

### 10.9 Message with repeating fields

PID with multiple patient addresses (XAD repeats), verifying the repetition separator (`~`) is preserved through framing.

### 10.10 Message with all optional segments populated

ADT^A01 with every optional segment filled in (NK1, AL1, DG1, GT1, IN1, etc.).

## 11. Edge cases

### 11.1 Minimum valid message

A message with only MSH (shortest possible valid HL7 v2 message).
Verify ACK is returned.

### 11.2 MSH with non-standard field separator

Build a raw MSH using `#` instead of `|` as the field separator.
Verify the server processes it (MLLP is encoding-agnostic, the server just delivers bytes).

### 11.3 MSH with non-standard encoding characters

Build a raw MSH with `@~\\!` instead of `^~\\&`.
Verify the ACK echoes the encoding characters correctly.

### 11.4 Empty payload between framing bytes

Send `0x0B 0x1C 0x0D` (framing with zero-length payload).
Verify the server handles it without crashing (callback receives empty bytes, auto-AA ACK is returned).

### 11.5 Binary payload (non-HL7) inside valid framing

Send `0x0B` + 256 random bytes + `0x1C 0x0D`.
Verify the callback receives those exact 256 random bytes unmodified (byte-for-byte comparison).
The server is a transport layer, not a parser - it never validates whether the payload is actual HL7.

### 11.6 Back-to-back connections

Open a connection, send a message, close. Immediately open a new connection and send another message.
Verify both messages are processed.

### 11.7 Rapid reconnect storm

Open and close 100 connections in a tight loop, each sending one message.
Verify all 100 ACKs are received and the server remains healthy.

## 12. Concurrency

### 12.1 Simultaneous messages from multiple clients

Open 10 TCP connections, each sending a different message concurrently.
Verify all 10 receive correct ACKs with the right control ids.

### 12.2 Slow client interleaved with fast client

One connection sends a message in small chunks with 100ms delays between chunks.
Another connection sends a complete message immediately.
Verify the fast client gets its ACK without waiting for the slow client.

### 12.3 Callback blocks for a long time

Configure callback to sleep 3 seconds on the first call.
Send two messages on separate connections.
Verify the second connection's response is not blocked by the first.

## 13. Logging

### 13.1 Messages are logged when `should_log_messages` is True

Configure `should_log_messages = True`.
Send a message, capture log output.
Verify the request data and response data appear in the logs.

### 13.2 Messages are masked when `should_log_messages` is False

Configure `should_log_messages = False`.
Send a message, capture log output.
Verify `<masked>` appears instead of the message data.

### 13.3 Debug log contains raw bytes

Configure logging level to `DEBUG`.
Send a message, verify the debug log contains the raw received bytes and their length.
