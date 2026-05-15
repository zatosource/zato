# Pub/sub audit and statistics subsystem


## 1. Overview

1. In-memory audit log per topic (publications) and per sub_key (deliveries).
2. Ring buffer of 10,000 entries per topic and per sub_key (FIFO eviction).
3. Full message bodies stored on disk in segmented ndjson files.
4. In-memory only holds first 100 characters of each message (data_preview).
5. All lookups are O(1) via incrementally maintained secondary indexes.
6. Thread safety via one `gevent.lock.RLock` per topic/sub_key.


## 2. Module layout

```
zato/common/pubsub/audit/
    __init__.py       - re-exports PubSubStats
    types.py          - type aliases, PubRecord, DeliveryRecord dataclasses
    core.py           - PubSubStats class (ring buffers, counters, query methods)
    indexes.py        - SecondaryIndexes class, index maintenance on insert/evict
    text_index.py     - TextPostings logic, tokenizer, text search
    disk.py           - segment file I/O, flush greenlet, cleanup greenlet, full message retrieval
    common.py         - constants (max_entries, flush_batch_size, flush_interval_seconds, etc.)
```


## 3. Type aliases

```
TopicName       = str
SubKey          = str
MsgId           = str
Publisher       = str
Token           = str
Outcome         = str
CorrelId        = str
ExtClientId     = str
EpochMs         = int
SegmentNumber   = int
LineNumber      = int
SeqNumber       = int                                   # monotonic per topic/sub_key, never reused

PubRingBuffer       = deque[PubRecord]
DeliveryRingBuffer  = deque[DeliveryRecord]
PubLogMap           = dict[TopicName, PubRingBuffer]
DeliveryLogMap      = dict[SubKey, DeliveryRingBuffer]
PubCounterMap       = dict[TopicName, int]
DeliveryCounterMap  = dict[SubKey, int]
OutcomeCountMap     = dict[Outcome, int]
MsgIdIndex          = dict[MsgId, list[SeqNumber]]       # same msg can appear multiple times
FieldIndex          = dict[str, deque[SeqNumber]]        # field value -> ordered seq numbers
SeqToRecord         = dict[SeqNumber, 'PubRecord | DeliveryRecord']
TextPostings        = dict[Token, set[SeqNumber]]
PubWriteBuffer      = list[PubRecord]
DeliveryWriteBuffer = list[DeliveryRecord]
PubWriteBufferMap   = dict[TopicName, PubWriteBuffer]
DeliveryWriteBufferMap = dict[SubKey, DeliveryWriteBuffer]
DiskLocation        = tuple[SegmentNumber, LineNumber]
```


## 4. Publication record fields

Per entry in the topic ring buffer (in memory):

1. pub_time_iso   - when the publish happened
2. msg_id         - message identifier
3. seq            - monotonic sequence number (assigned on insert)
4. topic_name     - target topic
5. publisher      - who published (service name or REST client id)
6. data_preview   - first 100 characters of the serialized payload
7. data_len       - byte length of the full serialized payload
8. priority       - message priority
9. expiration     - TTL in seconds
10. correl_id     - correlation id (if provided)
11. in_reply_to   - reply-to id (if provided)
12. ext_client_id - external client id (if provided)
13. _tokens       - list of tokens extracted from data_preview (not serialized to disk)


## 5. Delivery record fields

Per entry in the sub_key ring buffer (in memory):

1. delivery_time_iso - when delivery completed (success or final failure)
2. msg_id            - message identifier
3. seq               - monotonic sequence number (assigned on insert)
4. topic_name        - source topic
5. sub_key           - subscriber key
6. data_preview      - first 100 characters of the delivered payload
7. data_len          - byte length of the full payload
8. outcome           - one of: ok, error, deadline_exhausted
9. duration_ms       - wall-clock time from first attempt to final ack
10. attempts         - number of delivery attempts
11. error            - error text on failure (None on success)
12. push_type        - "service" or "rest" or "pull"
13. _tokens          - list of tokens extracted from data_preview (not serialized to disk)


## 6. Outcome labels (delivery)

1. ok                 - delivered successfully
2. error              - failed (final outcome after retries)
3. deadline_exhausted - all retries failed, message acked anyway


## 7. Aggregate counters

All maintained incrementally on insert and eviction, never recomputed from the buffer:

1. total_published / total_delivered - monotonic int, incremented on every record
2. outcome_counts                    - dict of outcome -> int, incremented on insert, decremented on eviction
3. last_outcome                      - read from deque[-1]
4. last_duration_ms                  - read from deque[-1]
5. recent_outcomes                   - slice of deque[-10:]


## 8. Hook points

1. Publication - at the end of `RedisPubSubBackend.publish` (after xadd succeeds),
   call `stats.record_publish(topic_name, msg_id, publisher, data, priority, expiration, correl_id, in_reply_to, ext_client_id)`.

2. Push delivery - in `RedisPushDelivery._deliver_with_retry`, after the while loop
   completes (whether via break on success or the else deadline clause), before
   ack_message, call `stats.record_delivery(sub_key, topic_name, msg_id, data, outcome, duration_ms, attempts, error, push_type)`.

3. Pull delivery - in `RedisPubSubBackend.format_messages_for_rest`, after ack,
   call `stats.record_delivery(...)` with push_type='pull' for each message.


## 9. SecondaryIndexes

Per topic/sub_key, maintained inline as records are added/evicted:

```
SecondaryIndexes
    seq_to_record: SeqToRecord                    # SeqNumber -> record object
    by_msg_id: MsgIdIndex                         # MsgId -> list[SeqNumber]
    by_publisher: FieldIndex                      # Publisher -> deque[SeqNumber]
    by_outcome: FieldIndex                        # Outcome -> deque[SeqNumber]
    by_correl_id: FieldIndex                      # CorrelId -> deque[SeqNumber]
    by_ext_client_id: FieldIndex                  # ExtClientId -> deque[SeqNumber]
    disk_locations: dict[SeqNumber, DiskLocation] # SeqNumber -> (SegmentNumber, LineNumber)
    next_seq: SeqNumber                           # monotonically increasing, never reset
```

On eviction (oldest record, lowest seq):

1. Pop from seq_to_record by evicted record's seq - O(1).
2. Remove evicted seq from each secondary index deque via popleft - O(1) because eviction order matches insertion order.
3. Remove evicted seq from by_msg_id[msg_id] list (remove first element) - O(1).
4. For each token in evicted record's _tokens, remove seq from text postings set - O(T) where T is token count for that record (bounded at ~50).
5. Remove from disk_locations - O(1).


## 10. Text search index

1. A TextPostings dict maps each token (lowercased, split on whitespace/punctuation, min 2 chars) to a set of seq numbers.
2. Maintained incrementally on insert (add seq to each token's set) and eviction (remove seq from each token's set).
3. On query, token lookup is O(1), then seq -> record via seq_to_record is O(1).
4. Multi-token queries AND the result sets.


## 11. Time range queries

1. The deque is time-ordered (records always appended chronologically).
2. A bisect on pub_time_iso / delivery_time_iso gives O(log N) start position.
3. Iteration from there is O(K) where K is the result page size.


## 12. PubSubStats class

```
PubSubStats
    _pub_logs: PubLogMap
    _delivery_logs: DeliveryLogMap
    _pub_counts: PubCounterMap
    _delivery_counts: DeliveryCounterMap
    _pub_outcome_counts: dict[TopicName, OutcomeCountMap]
    _delivery_outcome_counts: dict[SubKey, OutcomeCountMap]
    _pub_indexes: dict[TopicName, SecondaryIndexes]
    _delivery_indexes: dict[SubKey, SecondaryIndexes]
    _pub_text: dict[TopicName, TextPostings]
    _delivery_text: dict[SubKey, TextPostings]
    _pub_write_buffers: PubWriteBufferMap
    _delivery_write_buffers: DeliveryWriteBufferMap
    _flush_batch_size: int               # default 500
    _flush_interval_seconds: float       # default 1.0
    _segment_max_entries: int            # default 1000
    _max_entries: int                    # default 10_000
    _base_dir: str                       # <server_work_dir>/pubsub-audit/

    record_publish(topic_name, msg_id, publisher, data, priority, expiration, correl_id, in_reply_to, ext_client_id)
    record_delivery(sub_key, topic_name, msg_id, data, outcome, duration_ms, attempts, error, push_type)
    get_pub_summary(topic_name) -> dict
    get_delivery_summary(sub_key) -> dict
    get_pub_log(topic_name, offset, limit) -> tuple[list, int]
    get_delivery_log(sub_key, offset, limit) -> tuple[list, int]
    get_full_message(topic_name_or_sub_key, msg_id) -> str|None
    get_pub_by_msg_id(topic_name, msg_id) -> PubRecord|None
    get_delivery_by_msg_id(sub_key, msg_id) -> DeliveryRecord|None
    get_pubs_by_publisher(topic_name, publisher, limit) -> list
    get_deliveries_by_outcome(sub_key, outcome, limit) -> list
    get_pubs_by_correl_id(topic_name, correl_id) -> list
    search_pub_text(topic_name, query, offset, limit) -> tuple[list, int]
    search_delivery_text(sub_key, query, offset, limit) -> tuple[list, int]
    get_pub_log_time_range(topic_name, since_iso, until_iso, offset, limit) -> tuple[list, int]
    get_delivery_log_time_range(sub_key, since_iso, until_iso, offset, limit) -> tuple[list, int]
    get_all_topic_summaries() -> dict[str, dict]
    get_all_sub_summaries() -> dict[str, dict]
    start()
```


## 13. Lifecycle

1. PubSubStats is instantiated once in `ParallelServer._start_pubsub_redis` and stored as `self.pubsub_stats`.
2. RedisPubSubBackend receives a reference to it in its constructor.
3. RedisPushDelivery receives it via `self.server.pubsub_stats`.
4. `start()` spawns the flush and cleanup greenlets, rebuilds indexes from disk segments.


## 14. Query API for the dashboard

1. The poll view at `web/views/pubsub/dashboard.py` calls an internal service (`zato.pubsub.stats.get-current-state`).
2. That service reads from `self.server.pubsub_stats` and returns summaries and timeline data.


## 15. Disk storage

1. Base directory: `<server_work_dir>/pubsub-audit/`
2. Publications: `<base>/pub/<safe_topic_name>/`
3. Deliveries: `<base>/dlv/<safe_sub_key>/`
4. Directory name sanitization uses `fs_safe_name` from `zato.common.util.file_system`, truncates to 200 chars, appends first 8 chars of sha256 hex. A `manifest.json` maps sanitized names back to originals.

Per topic (or per sub_key), on disk:

1. Segment files - `seg-<sequence_number>.ndjson`, each holds up to `_segment_max_entries` records (default 1000). Each line is one JSON record containing all fields including the full data.
2. Index - held in memory, maintained incrementally on each record_publish / record_delivery call, rebuilt from segment files only on process startup.


## 16. Batched flush

Records accumulate in per-topic / per-sub_key write buffers. A background greenlet flushes to disk when either condition is met:

1. Any single buffer reaches `_flush_batch_size` entries (default 500).
2. A timer fires every `_flush_interval_seconds` (default 1 second).

The flush greenlet:

1. Under the lock, swaps each dirty buffer with a fresh empty list, collects them all.
2. Outside the lock, for each topic/sub_key with pending records:
   a. Appends to the current segment file (or opens a new segment if current is full).
   b. If a batch straddles the segment boundary (current segment has room for K records but the batch has more), the first K go into the current segment, the remainder open a new segment, both fsynced in the same pass.
   c. Updates the in-memory index posting lists with new entries.
3. Calls `os.fsync(fd)` once per segment file written to in this pass.
4. If any segment rotated, writes `index.json` (one fsync).

On startup, the write position is determined by counting lines in the last segment file (by sequence number).


## 17. Disk cleanup

A periodic cleanup greenlet (runs every 60 seconds). It does not hold the main lock while doing I/O:

1. Under the lock: snapshot the oldest seq per topic/sub_key and the list of live segment numbers. Release the lock.
2. Outside the lock: scan disk directories, identify segment files whose newest entry seq is older than the snapshot.
3. Delete those stale segment files (plain unlink, no lock held).
4. Under the lock briefly: remove from the text index any entries whose seq numbers belong to deleted segments (set difference operations).

Race prevention between flush and cleanup: the cleanup greenlet only deletes segments whose seq is strictly less than the oldest seq still in the ring buffer. The flush greenlet always writes to the current (highest) segment. They never operate on the same file.


## 18. Topic deletion and rename

When a topic is deleted:

1. The in-memory ring buffer and counters for that topic are removed immediately (under the lock).
2. The cleanup greenlet detects orphaned directories (no corresponding key in _pub_logs) and removes the entire directory tree.
3. Any pending write buffer entries for the deleted topic are discarded during the next flush pass.

When a topic is renamed:

1. The in-memory ring buffer, counters, and secondary indexes are moved from the old key to the new key (dict pop + insert under new name).
2. The disk directory is renamed (os.rename from `pub/<old_name>/` to `pub/<new_name>/`).
3. All internal references stay intact since they point to the same record objects.

Same logic applies to subscription deletions (sub_key removed from the delivery log).


## 19. Subscription lifecycle

When a subscription is removed (unsubscribe):

1. Delivery ring buffer and counters for that sub_key are removed from memory.
2. Disk directory becomes orphaned and is cleaned up by the periodic greenlet.
3. If the sub_key is re-created later (re-subscribe), it starts fresh.


## 20. Retention

1. Per-topic publication log: 10,000 entries in memory (FIFO, configurable via _max_entries).
2. Per-sub_key delivery log: 10,000 entries in memory (FIFO, configurable via _max_entries).
3. Disk files: retained as long as corresponding entries exist in the ring buffer, then deleted.
4. Monotonic counters (_pub_counts, _delivery_counts) never reset except on process restart.


## 21. Query complexity

```
+----+----------------------------------------------+-------------+--------------------------------------+
| #  | Query                                        | Complexity  | How                                  |
+----+----------------------------------------------+-------------+--------------------------------------+
|  1 | Get total_published for a topic              | O(1)        | _pub_counts[topic]                   |
|  2 | Get total_delivered for a sub_key            | O(1)        | _delivery_counts[sub_key]            |
|  3 | Get outcome_counts for a sub_key             | O(1)        | pre-maintained dict                  |
|  4 | Get last_outcome for a sub_key               | O(1)        | deque[-1].outcome                    |
|  5 | Get last_duration_ms for a sub_key           | O(1)        | deque[-1].duration_ms                |
|  6 | Get recent_outcomes (last 10) for sub_key    | O(1)        | slice deque[-10:]                    |
|  7 | Get pub records by msg_id                    | O(1)        | by_msg_id[msg_id] -> list[seq]       |
|  8 | Get delivery records by msg_id               | O(1)        | by_msg_id[msg_id] -> list[seq]       |
|  9 | Get last N pubs by a specific publisher      | O(1)        | by_publisher[pub][-N:] -> seqs       |
| 10 | Get last N deliveries with outcome=error     | O(1)        | by_outcome['error'][-N:] -> seqs     |
| 11 | Get all pubs correlated by correl_id         | O(1)        | by_correl_id[cid] -> seqs            |
| 12 | Get all pubs by ext_client_id                | O(1)        | by_ext_client_id[eid] -> seqs        |
| 13 | Get delivery count by outcome for sub_key    | O(1)        | outcome_counts[outcome]              |
| 14 | Get full message body from disk by msg_id    | O(1)        | seq -> disk_locations[seq] -> read   |
| 15 | Get pub log page (offset, limit)             | O(1)        | deque slice                          |
| 16 | Get delivery log page (offset, limit)        | O(1)        | deque slice                          |
| 17 | Get all topic summaries                      | O(T)        | T = number of topics                 |
| 18 | Get all sub_key summaries                    | O(S)        | S = number of sub_keys               |
| 19 | Full-text search in message data             | O(1) lookup | token -> set[seq], seq -> record     |
|    |                                              | + O(K) read | K = page size                        |
| 20 | Time range query (since_iso, until_iso)      | O(log N)    | bisect on time-ordered deque         |
|    |                                              | + O(K) read | K = page size                        |
+----+----------------------------------------------+-------------+--------------------------------------+
```

Notes:
- Queries 1-16, 19 are O(1) in the lookup step (page reads are O(K) for K results).
- Query 17-18 are O(number of topics/subs) because they iterate all keys.
- Query 20 uses bisect on the time-ordered deque (O(log N) for N=10,000 is ~14 comparisons).
- Query 14 (disk read) copies the DiskLocation under the lock, releases the lock, then reads from disk. Returns None if the segment was already cleaned up.
