# Pub/sub audit and statistics subsystem


## 1. Overview

1. In-memory audit log per topic (publications) and per sub_key (deliveries).
2. Ring buffer of 10,000 entries per topic and per sub_key (FIFO eviction, manual popleft with hooks).
3. Full message bodies stored on disk in segmented ndjson files.
4. In-memory only holds first 100 characters of each message (data_preview).
5. All lookups are O(1) via incrementally maintained secondary indexes.
6. Thread safety via one `gevent.lock.RLock` per AuditLog instance.
7. Lazy initialization - first record for an unknown topic/sub_key creates the AuditLog.


## 2. Module layout

```
zato/common/pubsub/audit/
    __init__.py       - re-exports PubSubStats, AuditLog
    types.py          - type aliases, PubRecord, DeliveryRecord, PageResult dataclasses
    core.py           - PubSubStats coordinator (registry of AuditLog instances, flush/cleanup greenlets)
    audit_log.py      - AuditLog class (per-topic or per-sub_key unit)
    indexes.py        - PubIndexes, DeliveryIndexes classes
    text_index.py     - TextPostings logic, tokenizer, text search
    disk.py           - segment file I/O, full message retrieval
    common.py         - constants (Audit_Max_Entries, Audit_Flush_Batch_Size, etc.)
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
SegmentNumber   = int
LineNumber      = int
SeqNumber       = int                                       # monotonic per AuditLog, never reused

PubRingBuffer          = deque[PubRecord]
DeliveryRingBuffer     = deque[DeliveryRecord]
PubLogMap              = dict[TopicName, AuditLog]
DeliveryLogMap         = dict[SubKey, AuditLog]
PubCounterMap          = dict[TopicName, int]
DeliveryCounterMap     = dict[SubKey, int]
OutcomeCountMap        = dict[Outcome, int]
MsgIdIndex             = dict[MsgId, list[SeqNumber]]       # same msg can appear multiple times
PubByPublisher         = dict[Publisher, deque[SeqNumber]]
PubByCorrelId          = dict[CorrelId, deque[SeqNumber]]
PubByExtClientId       = dict[ExtClientId, deque[SeqNumber]]
DeliveryByOutcome      = dict[Outcome, deque[SeqNumber]]
TextPostings           = dict[Token, set[SeqNumber]]
TokenStore             = dict[SeqNumber, list[Token]]
PubWriteBuffer         = list[PubRecord]
DeliveryWriteBuffer    = list[DeliveryRecord]
DiskLocation           = tuple[SegmentNumber, LineNumber]
DiskLocationMap        = dict[SeqNumber, DiskLocation]
```


## 4. PubRecord dataclass

```
@dataclass
class PubRecord:
    pub_time_iso: str
    msg_id: MsgId
    seq: SeqNumber
    topic_name: TopicName
    publisher: Publisher
    data_preview: str                   # first 100 chars
    data_len: int
    priority: int
    expiration: int
    correl_id: CorrelId | None
    in_reply_to: str | None
    ext_client_id: ExtClientId | None
```


## 5. DeliveryRecord dataclass

```
@dataclass
class DeliveryRecord:
    delivery_time_iso: str
    msg_id: MsgId
    seq: SeqNumber
    topic_name: TopicName
    sub_key: SubKey
    data_preview: str                   # first 100 chars
    data_len: int
    outcome: Outcome
    duration_ms: int
    attempts: int
    error: str | None
    push_type: str                      # "service" or "rest" or "pull"
```


## 6. PageResult dataclass

```
@dataclass
class PageResult:
    items: list[PubRecord] | list[DeliveryRecord]
    total: int
```


## 7. Outcome labels (delivery)

1. ok                 - delivered successfully
2. error              - failed (final outcome after retries)
3. deadline_exhausted - all retries failed, message acked anyway


## 8. AuditLog class

The per-topic or per-sub_key unit. Each instance is self-contained with its own lock:

```
AuditLog
    _deque: deque[PubRecord] | deque[DeliveryRecord]     # plain deque, no maxlen
    _base_seq: SeqNumber                                  # seq of deque[0]
    _next_seq: SeqNumber                                  # next seq to assign
    _lock: RLock                                          # per-instance
    _indexes: PubIndexes | DeliveryIndexes
    _text_postings: TextPostings
    _token_store: TokenStore                              # seq -> tokens for eviction cleanup
    _outcome_counts: OutcomeCountMap
    _counter: int                                         # monotonic total (never decremented)
    _write_buffer: PubWriteBuffer | DeliveryWriteBuffer
    _disk_dir: str
    _max_entries: int                                     # from Audit_Max_Entries

    insert(record, full_data: str)
    _evict()
    lookup_by_seq(seq) -> PubRecord | DeliveryRecord      # deque[seq - _base_seq]
```

1. `insert` assigns seq, appends to deque, updates indexes and text postings, appends full_data to write buffer, increments counter and outcome_counts. If `len(_deque) >= _max_entries`, calls `_evict()` first.
2. `_evict` poplefts the oldest record, removes its entries from all indexes, decrements outcome_counts, removes its tokens from text postings, removes from disk_locations, increments `_base_seq`.
3. `lookup_by_seq` returns `_deque[seq - _base_seq]`. O(1).


## 9. PubIndexes

```
PubIndexes
    by_msg_id: MsgIdIndex
    by_publisher: PubByPublisher
    by_correl_id: PubByCorrelId
    by_ext_client_id: PubByExtClientId
    disk_locations: DiskLocationMap
```


## 10. DeliveryIndexes

```
DeliveryIndexes
    by_msg_id: MsgIdIndex
    by_outcome: DeliveryByOutcome
    disk_locations: DiskLocationMap
```


## 11. Text search index

1. A TextPostings dict maps each token (lowercased, split on whitespace/punctuation, min 2 chars) to a set of seq numbers.
2. A TokenStore (`dict[SeqNumber, list[Token]]`) holds the token list per record for eviction cleanup.
3. Maintained incrementally on insert (add seq to each token's set, store token list) and eviction (remove seq from each token's set, delete token list entry).
4. On query, token lookup is O(1), then seq -> record via `lookup_by_seq` is O(1).
5. Multi-token queries AND the result sets.


## 12. Time range queries

1. The deque is time-ordered (records always appended chronologically).
2. A bisect on pub_time_iso / delivery_time_iso gives O(log N) start position.
3. Iteration from there is O(K) where K is the result page size.


## 13. PubSubStats coordinator

```
PubSubStats
    _pub_logs: PubLogMap                                  # TopicName -> AuditLog
    _delivery_logs: DeliveryLogMap                        # SubKey -> AuditLog
    _base_dir: str                                        # <server_work_dir>/pubsub-audit/

    record_publish(record: PubRecord, full_data: str)
    record_delivery(record: DeliveryRecord, full_data: str)
    get_pub_summary(topic_name: TopicName) -> dict
    get_delivery_summary(sub_key: SubKey) -> dict
    get_pub_log(topic_name, offset, limit) -> PageResult
    get_delivery_log(sub_key, offset, limit) -> PageResult
    get_full_pub_message(topic_name, msg_id) -> str | None
    get_full_delivery_message(sub_key, msg_id) -> str | None
    get_pubs_by_msg_id(topic_name, msg_id) -> list[PubRecord]
    get_deliveries_by_msg_id(sub_key, msg_id) -> list[DeliveryRecord]
    get_pubs_by_publisher(topic_name, publisher, offset, limit) -> PageResult
    get_deliveries_by_outcome(sub_key, outcome, offset, limit) -> PageResult
    get_pubs_by_correl_id(topic_name, correl_id, offset, limit) -> PageResult
    get_pubs_by_ext_client_id(topic_name, ext_client_id, offset, limit) -> PageResult
    search_pub_text(topic_name, query, offset, limit) -> PageResult
    search_delivery_text(sub_key, query, offset, limit) -> PageResult
    get_pub_log_time_range(topic_name, since_iso, until_iso, offset, limit) -> PageResult
    get_delivery_log_time_range(sub_key, since_iso, until_iso, offset, limit) -> PageResult
    get_all_topic_summaries() -> dict[TopicName, dict]
    get_all_sub_summaries() -> dict[SubKey, dict]
    rename_topic(old_name: TopicName, new_name: TopicName)
    delete_topic(topic_name: TopicName)
    delete_subscription(sub_key: SubKey)
    start()
```

1. `record_publish` lazily creates an AuditLog for the topic if one does not exist, then delegates to `audit_log.insert(record, full_data)`.
2. `record_delivery` same for sub_key.
3. All query methods delegate to the appropriate AuditLog instance.
4. `start()` spawns the flush and cleanup greenlets, scans disk directories to rebuild AuditLog instances from existing segments.


## 14. Hook points

1. Publication - at the end of `RedisPubSubBackend.publish` (after xadd succeeds), the caller constructs a PubRecord (with data_preview = data[:100], data_len = len(data)), then calls `stats.record_publish(record, full_data=data)`.

2. Push delivery - in `RedisPushDelivery._deliver_with_retry`, after the while loop completes, before ack_message, the caller constructs a DeliveryRecord, then calls `stats.record_delivery(record, full_data=data)`.

3. Pull delivery - in `RedisPubSubBackend.format_messages_for_rest`, after ack, same pattern with push_type='pull'.


## 15. Lock model

1. Each AuditLog has its own RLock protecting its deque, indexes, counters, and text postings.
2. The flush greenlet iterates all AuditLog instances. For each one, it briefly acquires that instance's lock to swap the write buffer (replace with empty list), then releases the lock before doing any disk I/O.
3. The cleanup greenlet iterates all AuditLog instances. For each one, it briefly acquires the lock to snapshot the oldest seq and live segment list, releases, does disk I/O (unlink), then briefly re-acquires to prune text index entries for deleted segments.
4. Queries acquire the relevant AuditLog's lock for the duration of the in-memory read (fast, no I/O). For `get_full_pub_message` / `get_full_delivery_message`, the DiskLocation is copied under the lock, then the lock is released, then the disk read happens outside the lock. Returns None if the segment was already cleaned up.


## 16. Disk storage

1. Base directory: `<server_work_dir>/pubsub-audit/`
2. Publications: `<base>/pub/<safe_name>/`
3. Deliveries: `<base>/dlv/<safe_name>/`
4. Directory name sanitization uses `fs_safe_name` from `zato.common.util.file_system`, truncates to 200 chars, appends first 8 chars of sha256 hex.
5. Each directory contains a `meta.json` with the original topic/sub_key name. Discovered by scanning at startup.

Per AuditLog directory, on disk:

1. Segment files - `seg-<sequence_number>.ndjson`, each holds up to Audit_Segment_Max_Entries records (default 1000). Each line is one JSON record containing all fields including the full data.
2. `disk_locations.json` - serialized DiskLocationMap (SeqNumber -> [SegmentNumber, LineNumber]). Written on segment rotation. On startup, if missing or stale, rebuilt by scanning segments.


## 17. Batched flush

Records accumulate in each AuditLog's write buffer. A background greenlet flushes to disk when either condition is met:

1. Any single buffer reaches Audit_Flush_Batch_Size entries (default 500).
2. A timer fires every Audit_Flush_Interval_Seconds (default 1 second).

The flush greenlet:

1. For each AuditLog instance: acquires its lock, swaps write buffer with empty list, releases lock. Collects all non-empty buffers.
2. Outside any lock, for each collected buffer:
   a. Appends to the current segment file (or opens a new segment if current is full).
   b. If a batch straddles the segment boundary, the first K records go into the current segment, the remainder open a new segment, both fsynced in the same pass.
3. Calls `os.fsync(fd)` once per segment file written to in this pass.
4. If any segment rotated, writes `disk_locations.json` (one fsync).

On startup, the write position is determined by counting lines in the last segment file (by sequence number).


## 18. Disk cleanup

A periodic cleanup greenlet (runs every 60 seconds):

1. For each AuditLog: acquires lock, snapshots oldest seq and list of live segment numbers, releases lock.
2. Outside any lock: scans disk directories, identifies segment files whose newest entry seq is less than the snapshot oldest seq.
3. Deletes those stale segment files (plain unlink, no lock held).
4. For each affected AuditLog: acquires lock briefly, removes from text index any entries whose seq numbers belong to deleted segments (set difference), releases lock.

Race prevention: cleanup only deletes segments whose seq is strictly less than the oldest seq still in the ring buffer. The flush greenlet always writes to the current (highest) segment. They never operate on the same file.


## 19. Topic deletion and rename

When a topic is deleted:

1. The AuditLog instance for that topic is removed from `_pub_logs` (under the instance's lock).
2. The cleanup greenlet detects orphaned directories (no corresponding AuditLog) and removes the entire directory tree.
3. Any pending write buffer entries are discarded (the buffer was on the now-discarded AuditLog).

When a topic is renamed:

1. The AuditLog instance is moved from old key to new key in `_pub_logs`.
2. The disk directory is renamed (os.rename).
3. The `meta.json` inside the directory is updated with the new name.
4. All internal state stays intact since the AuditLog object is the same.

Same logic applies to subscription deletions (sub_key removed from `_delivery_logs`).


## 20. Subscription lifecycle

When a subscription is removed (unsubscribe):

1. The AuditLog instance for that sub_key is removed from `_delivery_logs`.
2. Disk directory becomes orphaned and is cleaned up by the periodic greenlet.
3. If the sub_key is re-created later (re-subscribe), it starts fresh.


## 21. Retention

1. Per-topic publication log: 10,000 entries in memory (FIFO, configurable via Audit_Max_Entries).
2. Per-sub_key delivery log: 10,000 entries in memory (FIFO, configurable via Audit_Max_Entries).
3. Disk files: retained as long as corresponding entries exist in the ring buffer, then deleted.
4. Monotonic counters (AuditLog._counter) never reset except on process restart.


## 22. Constants (common.py)

```
Audit_Max_Entries              = 10_000
Audit_Flush_Batch_Size         = 500
Audit_Flush_Interval_Seconds   = 1.0
Audit_Segment_Max_Entries      = 1_000
Audit_Data_Preview_Len         = 100
Audit_Cleanup_Interval_Seconds = 60
```


## 23. Lazy initialization

1. First call to `record_publish` for an unknown topic creates a new AuditLog instance: allocates deque, indexes, token store, text postings, write buffer, lock, creates disk directory and `meta.json`.
2. First call to `record_delivery` for an unknown sub_key does the same.
3. On startup, `start()` scans existing disk directories, reads each `meta.json`, creates AuditLog instances, and rebuilds in-memory state from segment files.


## 24. Query complexity

```
+----+----------------------------------------------+-------------+--------------------------------------+
| #  | Query                                        | Complexity  | How                                  |
+----+----------------------------------------------+-------------+--------------------------------------+
|  1 | Get total_published for a topic              | O(1)        | audit_log._counter                   |
|  2 | Get total_delivered for a sub_key            | O(1)        | audit_log._counter                   |
|  3 | Get outcome_counts for a sub_key             | O(1)        | audit_log._outcome_counts            |
|  4 | Get last_outcome for a sub_key               | O(1)        | deque[-1].outcome                    |
|  5 | Get last_duration_ms for a sub_key           | O(1)        | deque[-1].duration_ms                |
|  6 | Get recent_outcomes (last 10) for sub_key    | O(1)        | slice deque[-10:]                    |
|  7 | Get pub records by msg_id                    | O(1)        | by_msg_id[msg_id] -> list[seq]       |
|  8 | Get delivery records by msg_id               | O(1)        | by_msg_id[msg_id] -> list[seq]       |
|  9 | Get last N pubs by a specific publisher      | O(1)        | by_publisher[pub][-N:] -> seqs       |
| 10 | Get last N deliveries with outcome=error     | O(1)        | by_outcome['error'][-N:] -> seqs     |
| 11 | Get all pubs correlated by correl_id         | O(1)        | by_correl_id[cid] -> seqs            |
| 12 | Get all pubs by ext_client_id                | O(1)        | by_ext_client_id[eid] -> seqs        |
| 13 | Get delivery count by outcome for sub_key    | O(1)        | _outcome_counts[outcome]             |
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
