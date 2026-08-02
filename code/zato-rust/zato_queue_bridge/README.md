# zato_queue_bridge

Standalone bridge connecting external message queues to the Zato integration platform.
Kafka and IBM MQ are supported, each behind its own Cargo feature, and the bridge talks
to the Zato server over Redis Streams only - the two processes share no memory and no ODB
connection.

## 1. Process layout

The `_zato_queue_bridge` binary runs four threads plus a Tokio runtime:

```
+----------------------+------------------------------------------------------+
| Thread               | Responsibility                                       |
+----------------------+------------------------------------------------------+
| zato-cmd-listener    | Reads the command stream, applies config changes     |
| zato-bridge-loop     | Owns the Tokio runtime and all consumer tasks        |
| recv publisher       | Forwards consumed messages onto the recv stream      |
| main                 | Serves the HTTP query API, waits for shutdown        |
+----------------------+------------------------------------------------------+
```

One Tokio task is spawned per channel. Each task holds a `CancellationToken` kept in
`BridgeShared::channel_tokens`, so a single channel can be stopped without disturbing
the others when its config is deleted or edited.

## 2. Redis streams

```
+------------------------------------+----------------------------------------+
| Stream                             | Direction                              |
+------------------------------------+----------------------------------------+
| zato:queue_bridge:stream:command   | server -> bridge, commands             |
| zato:queue_bridge:stream:reply     | bridge -> server, command replies      |
| zato:queue_bridge:stream:recv      | bridge -> server, consumed messages    |
| zato:queue_bridge:stream:request   | bridge -> server, config requests      |
+------------------------------------+----------------------------------------+
```

All streams are trimmed at approximately 100,000 entries (`STREAM_MAXLEN`). The command
stream is read through the `queue_bridge` consumer group so that no command is lost while
the bridge restarts.

Binary payloads do not survive a Redis stream field as raw bytes, so message data is
base64-encoded in both directions by the codec in `redis_streams.rs`.

## 3. Commands

```
+-------------------+------------------+--------------------------------------+
| Command           | Replies          | Effect                               |
+-------------------+------------------+--------------------------------------+
| reload            | no               | Replaces the whole config            |
| add_channel       | no               | Registers a channel, spawns consumer |
| add_outgoing      | no               | Registers an outgoing connection     |
| edit_channel      | no               | Cancels and respawns the consumer    |
| edit_outgoing     | no               | Replaces the outgoing config         |
| delete_channel    | no               | Cancels the consumer, drops config   |
| delete_outgoing   | no               | Drops the outgoing config            |
| ping              | yes              | Checks a connection is reachable     |
| send_message      | yes              | Publishes to an outgoing connection  |
| send_reply        | yes              | Replies to a received message        |
+-------------------+------------------+--------------------------------------+
```

On start the bridge publishes `request_config` and waits for the server's initial
`reload` before it consumes anything.

## 4. IBM MQ specifics

1. The client library `libmqm_r.so` is loaded at run time with dlopen2, which is the only
   place in the crate where unsafe code is allowed - `unsafe_code` is otherwise denied.
2. `Zato_MQ_Client_Lib` overrides the library path, otherwise the standard loader search
   rules apply.
3. `rfh2.rs` is a pure-Rust parser for the MQRFH2 header, so messages in `MQHRF2` format
   have their header stripped and their properties surfaced as headers.
4. Replies go to the `ReplyToQ` and `ReplyToQMgr` of the original message, with the reply's
   correlation ID set to the original message ID.

## 5. HTTP query API

An actix-web server on 127.0.0.1:35111 exposes read-only state for the dashboard:

1. `/api/get_connections` - every registered channel and outgoing connection.
2. `/api/get_connection_status` - reachability of one named connection.

The server is awaited on the main thread's actix runtime and is never moved elsewhere,
which is why its future is deliberately not `Send`.
