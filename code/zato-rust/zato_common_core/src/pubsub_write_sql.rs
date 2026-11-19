//! The statements of a pub/sub batch on `SQLite`.
//!
//! The statements are those that Python built from the metadata of the tables, each run once per key,
//! in the order in which the transaction of Python runs its statements, so that the same rows are written
//! and the same statements open the transaction.

use std::collections::hash_map::Entry;
use std::collections::{BTreeMap, HashMap, HashSet};

use rusqlite::types::Value;
use rusqlite::{Connection, params, params_from_iter};

// ################################################################################################################################
// ################################################################################################################################

/// The statements of the transaction of a batch, with positional parameters.
pub struct Statements {
    /// The statement that opens the transaction before the first statement that changes rows, as the Python driver does.
    pub begin: String,

    /// The subscribers of one topic.
    pub select_subscribers: String,

    /// The insert of one message, returning its id unless its identifier exists already.
    pub insert_message: String,

    /// The topic and the checksum of the payload of the message of one identifier.
    pub select_existing_message: String,

    /// The insert of one delivery row.
    pub insert_delivery: String,

    /// The id of the message of one identifier.
    pub select_message_id: String,

    /// The delivery rows of one message that belong to one subscriber.
    pub select_ack_delivery: String,

    /// The delete of one delivery row, returning its id if it existed.
    pub delete_delivery: String,

    /// The record of the next push attempt of one delivery row, returning the attempt.
    pub record_attempt: String,

    /// The deliverable rows of one subscriber, with the size of the message of each, in the order of the queue.
    pub select_lease_candidates: String,

    /// The lease of one delivery row, returning its message and attempt unless a concurrent pull leased it.
    pub lease_delivery: String,

    /// The columns of one leased message.
    pub select_leased_message: String,

    /// The delivery rows of one subscriber for the message of one identifier, with the attempt of each.
    pub select_fenced_delivery: String,

    /// The drop of the payload of one message that no delivery row references anymore, returning its id.
    pub drop_payload: String,
}

/// The positions of the columns that the transaction itself reads or changes.
pub struct Layout {
    /// The position of the payload among the values of a message insert.
    pub payload_index: usize,

    /// The position of the flag of an encrypted payload among the values of a message insert.
    pub payload_encrypted_index: usize,

    /// The number of the columns of a leased message.
    pub lease_column_count: usize,

    /// The position of the id among the columns of a leased message.
    pub lease_id_index: usize,

    /// The position of the priority among the columns of a leased message.
    pub lease_priority_index: usize,

    /// The position of the flag of an encrypted payload among the columns of a leased message.
    pub lease_payload_encrypted_index: usize,
}

// ################################################################################################################################
// ################################################################################################################################

/// One publication of a message.
pub struct PublicationInput {
    /// The values of the message insert, in the order of its parameters.
    pub values: Vec<Value>,

    /// The public identifier of the message.
    pub msg_id: String,

    /// The topic that the message is published to.
    pub topic_name: String,

    /// The checksum of the payload, which tells a repeated publication from a different message.
    pub payload_crc32: i64,

    /// The priority of the message, which its delivery rows are ordered by.
    pub priority: i64,

    /// When the message expires, in milliseconds since the epoch.
    pub expiration_ms: i64,
}

/// One acknowledgement of a subscriber's messages.
pub struct AckInput {
    /// The subscriber that acknowledges the messages.
    pub sub_key: String,

    /// The public identifiers of the messages.
    pub msg_ids: Vec<String>,

    /// The ids of the messages, when the caller knows them already.
    pub sequence_ids: Option<Vec<i64>>,
}

/// One message of a fenced acknowledgement.
pub struct FencedEntry {
    /// The public identifier of the message.
    pub msg_id: String,

    /// The attempt that the message is expected to have been handed out with, if the acknowledgement is fenced by attempts.
    pub expected_attempt: Option<i64>,
}

/// A fenced acknowledgement with its publications, all of them committed or none.
pub struct AtomicInput {
    /// The publications of the item.
    pub publications: Vec<PublicationInput>,

    /// The subscriber that acknowledges the messages.
    pub sub_key: String,

    /// The acknowledged messages, in the order of the acknowledgement.
    pub entries: Vec<FencedEntry>,

    /// Whether a publication whose identifier belongs to a different message fails the item.
    pub is_strict: bool,
}

/// One pull of a subscriber's messages.
pub struct LeaseInput {
    /// The subscriber that pulls.
    pub sub_key: String,

    /// The most messages that the pull hands out.
    pub max_messages: i64,

    /// The most bytes of payloads that the pull hands out, apart from a single larger message.
    pub max_len: i64,

    /// The current time, in milliseconds since the epoch.
    pub now_ms: i64,

    /// Until when the leased rows are held, in milliseconds since the epoch.
    pub leased_until_ms: i64,
}

/// The items of one batch, by kind.
pub struct BatchInput {
    /// The publications, written first.
    pub publications: Vec<PublicationInput>,

    /// The acknowledgements, written next.
    pub acks: Vec<AckInput>,

    /// The fenced acknowledgements with their publications.
    pub atomics: Vec<AtomicInput>,

    /// The delivery rows of each batch of push attempts.
    pub attempts: Vec<Vec<i64>>,

    /// The pulls, written last.
    pub leases: Vec<LeaseInput>,
}

// ################################################################################################################################
// ################################################################################################################################

/// How a publication whose message was not inserted repeats an earlier one.
pub enum Repeat {
    /// The message existed when the insert met it and was removed afterwards.
    Removed,

    /// The message exists with the same topic and payload.
    Existing,
}

/// What became of one publication.
#[derive(Default)]
pub struct PublicationResult {
    /// The subscribers that the message was delivered to.
    pub subscriber_keys: Vec<String>,

    /// Whether the message was stored without its payload, because its topic has no subscribers.
    pub drops_payload: bool,

    /// How the publication repeats an earlier one, if it does.
    pub repeat: Option<Repeat>,

    /// Why the publication failed, if its identifier belongs to a different message.
    pub duplicate: Option<String>,
}

/// What became of one acknowledgement.
#[derive(Default)]
pub struct AckResult {
    /// How many delivery rows the acknowledgement removed.
    pub removed_count: i64,

    /// How many messages the acknowledgement concluded the delivery of.
    pub fully_delivered_count: i64,

    /// The messages of a fenced acknowledgement that an earlier delivery concluded, if any.
    pub concluded_msg_ids: Option<Vec<String>>,
}

/// Why an item failed on its own, without failing the batch.
pub enum ItemError {
    /// A fenced message was handed out again or concluded by another delivery.
    Conflict(String),

    /// The identifier of a publication belongs to a different message.
    Duplicate(String),
}

/// What became of one fenced acknowledgement with its publications.
#[derive(Default)]
pub struct AtomicResult {
    /// What became of each publication.
    pub publications: Vec<PublicationResult>,

    /// What became of the acknowledgement.
    pub ack: AckResult,

    /// Why the item failed, if it did.
    pub error: Option<ItemError>,
}

/// What one pull leased.
#[derive(Default)]
pub struct LeaseResult {
    /// The columns of each leased message, in the order of the queue.
    pub rows: Vec<Vec<Value>>,

    /// The attempt of each leased message, by the id of the message.
    pub attempts: Vec<(i64, i64)>,
}

/// What became of the items of one batch, by kind, in the order of the items.
pub struct BatchResults {
    /// What became of each publication.
    pub publications: Vec<PublicationResult>,

    /// What became of each acknowledgement.
    pub acks: Vec<AckResult>,

    /// What became of each fenced acknowledgement.
    pub atomics: Vec<AtomicResult>,

    /// The attempt of each delivery row of each batch of push attempts, by the id of the row.
    pub attempts: Vec<Vec<(i64, i64)>>,

    /// What each pull leased.
    pub leases: Vec<LeaseResult>,
}

impl BatchResults {
    /// Returns the results of a batch before anything of it is written.
    pub(crate) fn for_batch(batch: &BatchInput) -> Self {
        let mut atomics = Vec::with_capacity(batch.atomics.len());

        for atomic in &batch.atomics {
            atomics.push(AtomicResult {
                publications: default_results(atomic.publications.len()),
                ..AtomicResult::default()
            });
        }

        Self {
            publications: default_results(batch.publications.len()),
            acks: default_results(batch.acks.len()),
            atomics,
            attempts: vec![Vec::new(); batch.attempts.len()],
            leases: default_results(batch.leases.len()),
        }
    }
}

/// Why the transaction of a batch failed as a whole.
pub enum BatchError {
    /// `SQLite` refused a statement.
    Sqlite(rusqlite::Error),

    /// A publication of a strict fenced acknowledgement belongs to a different message after the item was partly written,
    /// which only the rollback of the whole transaction undoes.
    StrictDuplicate {
        /// The position of the fenced acknowledgement among those of the batch.
        atomic_index: usize,

        /// The position of the publication among those of the fenced acknowledgement.
        publication_index: usize,
    },
}

impl From<rusqlite::Error> for BatchError {
    fn from(error: rusqlite::Error) -> Self {
        Self::Sqlite(error)
    }
}

/// The acknowledgement that the full delivery of a message counts towards.
#[derive(Clone, Copy)]
enum AckRef {
    /// An acknowledgement, by its position among those of the batch.
    Plain(usize),

    /// A fenced acknowledgement, by its position among those of the batch.
    Fenced(usize),
}

/// The delivery rows that a fenced acknowledgement removes and the messages that they belong to.
struct FencedRows {
    /// The ids of the delivery rows.
    delivery_ids: Vec<i64>,

    /// The ids of their messages.
    message_ids: Vec<i64>,
}

// ################################################################################################################################
// ################################################################################################################################

/// Returns the given number of results of items that nothing was written for yet.
fn default_results<Item: Default>(count: usize) -> Vec<Item> {
    let mut out = Vec::with_capacity(count);
    out.resize_with(count, Item::default);
    out
}

/// Writes the items of a batch in the transaction of the connection, storing in the results what became of each item.
///
/// The results of the items written before an error remain stored.
pub fn write_batch(
    sqlite: &Connection,
    statements: &Statements,
    layout: &Layout,
    batch: &BatchInput,
    results: &mut BatchResults,
) -> Result<(), BatchError> {
    let writer = Writer {
        sqlite,
        statements,
        layout,
    };
    writer.write(batch, results)
}

/// The connection and the statements that the items of one batch are written with.
struct Writer<'batch> {
    /// The connection over the handle of the Python driver.
    sqlite: &'batch Connection,

    /// The statements of the transaction.
    statements: &'batch Statements,

    /// The positions of the columns that the transaction reads or changes.
    layout: &'batch Layout,
}

impl Writer<'_> {
    /// Opens the transaction unless it is open already.
    fn begin(&self) -> rusqlite::Result<()> {
        // The Python driver opens it right before the first statement that changes rows, and so does this writer
        if self.sqlite.is_autocommit() {
            self.sqlite.execute_batch(&self.statements.begin)?;
        }
        Ok(())
    }

    /// Writes the publications first, the acknowledgements next, the fenced acknowledgements with their publications,
    /// the push attempts and the pulls after them, and drops the payloads that no subscriber needs anymore last.
    fn write(&self, batch: &BatchInput, results: &mut BatchResults) -> Result<(), BatchError> {
        let mut ack_by_message_id = BTreeMap::new();

        if !batch.publications.is_empty() {
            self.insert_publications(&batch.publications, &mut results.publications)?;
        }

        if !batch.acks.is_empty() {
            self.delete_acks(&batch.acks, &mut results.acks, &mut ack_by_message_id)?;
        }

        for (atomic_index, (atomic, result)) in batch.atomics.iter().zip(&mut results.atomics).enumerate() {
            self.write_atomic(atomic_index, atomic, result, &mut ack_by_message_id)?;
        }

        // A push attempt is recorded only for a delivery that this transaction has not acknowledged
        for (delivery_ids, result) in batch.attempts.iter().zip(&mut results.attempts) {
            self.record_attempts(delivery_ids, result)?;
        }

        // A pull leases nothing that this transaction has acknowledged already
        for (lease, result) in batch.leases.iter().zip(&mut results.leases) {
            self.lease_messages(lease, result)?;
        }

        // Dropping a payload holds the delivery rows of the other subscribers of its message, so it follows every write of them
        if !ack_by_message_id.is_empty() {
            self.drop_payloads(&ack_by_message_id, results)?;
        }

        Ok(())
    }

    /// Inserts the messages of the publications and one delivery row per message and subscriber.
    fn insert_publications(&self, publications: &[PublicationInput], results: &mut [PublicationResult]) -> rusqlite::Result<()> {
        let layout = self.layout;

        // The subscribers as of this very transaction, read once per topic ..
        let mut select = self.sqlite.prepare_cached(&self.statements.select_subscribers)?;
        let mut by_topic: HashMap<&str, Vec<String>> = HashMap::new();
        let mut subscribers = Vec::with_capacity(publications.len());

        for publication in publications {
            let sub_keys = match by_topic.entry(publication.topic_name.as_str()) {
                Entry::Occupied(entry) => entry.get().clone(),
                Entry::Vacant(entry) => {
                    let rows = select.query_map([&publication.topic_name], |row| row.get::<_, String>(0))?;
                    let sub_keys = rows.collect::<rusqlite::Result<Vec<_>>>()?;
                    entry.insert(sub_keys).clone()
                }
            };
            subscribers.push(sub_keys);
        }

        // .. a topic without subscribers has its messages stored without their payloads ..
        let mut insert = self.sqlite.prepare_cached(&self.statements.insert_message)?;
        let no_payload = Value::Null;
        let not_encrypted = Value::Integer(0);
        let mut inserted = Vec::with_capacity(publications.len());

        self.begin()?;

        for (publication, sub_keys) in publications.iter().zip(&subscribers) {
            let drops_payload = sub_keys.is_empty();
            let mut values = Vec::with_capacity(publication.values.len());

            for (index, value) in publication.values.iter().enumerate() {
                if drops_payload && index == layout.payload_index {
                    values.push(&no_payload);
                } else if drops_payload && index == layout.payload_encrypted_index {
                    values.push(&not_encrypted);
                } else {
                    values.push(value);
                }
            }

            // .. a message whose identifier exists already is not inserted ..
            let mut rows = insert.query(params_from_iter(values))?;
            let message_id = match rows.next()? {
                Some(row) => Some(row.get::<_, i64>(0)?),
                None => None,
            };
            inserted.push(message_id);
        }

        // .. which tells a repeated publication from a different message, only once all of the messages are inserted ..
        let mut select_existing = self.sqlite.prepare_cached(&self.statements.select_existing_message)?;

        for ((publication, message_id), result) in publications.iter().zip(&inserted).zip(results.iter_mut()) {
            if message_id.is_none() {
                resolve_duplicate(&mut select_existing, publication, result)?;
            }
        }

        // .. and each inserted message receives one delivery row per subscriber.
        let mut insert_delivery = self.sqlite.prepare_cached(&self.statements.insert_delivery)?;

        for (((publication, message_id), sub_keys), result) in publications.iter().zip(&inserted).zip(subscribers).zip(results.iter_mut()) {
            result.drops_payload = sub_keys.is_empty();

            let Some(message_id) = *message_id else {
                continue;
            };

            for sub_key in &sub_keys {
                insert_delivery.execute(params![
                    message_id,
                    sub_key,
                    publication.topic_name,
                    publication.priority,
                    publication.expiration_ms,
                ])?;
            }
            result.subscriber_keys = sub_keys;
        }

        Ok(())
    }

    /// Returns the ids of the messages of each acknowledgement, looking up those that were given public identifiers alone.
    fn resolve_ack_message_ids(&self, acks: &[AckInput]) -> rusqlite::Result<Vec<Vec<i64>>> {
        let mut select = self.sqlite.prepare_cached(&self.statements.select_message_id)?;
        let mut found: HashMap<&str, Option<i64>> = HashMap::new();

        for ack in acks {
            if ack.sequence_ids.is_some() {
                continue;
            }
            for msg_id in &ack.msg_ids {
                if let Entry::Vacant(entry) = found.entry(msg_id.as_str()) {
                    let mut rows = select.query([msg_id])?;
                    let message_id = match rows.next()? {
                        Some(row) => Some(row.get::<_, i64>(0)?),
                        None => None,
                    };
                    entry.insert(message_id);
                }
            }
        }

        let mut out = Vec::with_capacity(acks.len());

        for ack in acks {
            if let Some(sequence_ids) = &ack.sequence_ids {
                out.push(sequence_ids.clone());
                continue;
            }

            let mut message_ids = Vec::with_capacity(ack.msg_ids.len());
            for msg_id in &ack.msg_ids {
                if let Some(Some(message_id)) = found.get(msg_id.as_str()) {
                    message_ids.push(*message_id);
                }
            }
            out.push(message_ids);
        }

        Ok(out)
    }

    /// Removes the delivery rows that the acknowledgements are about and records each of their messages
    /// with the acknowledgement that its full delivery counts towards.
    ///
    /// A row that two acknowledgements are about counts towards the first of them, and a message counts towards
    /// the last acknowledgement that removed one of its rows, or, with no such acknowledgement, the first one about it.
    fn delete_acks(
        &self,
        acks: &[AckInput],
        results: &mut [AckResult],
        ack_by_message_id: &mut BTreeMap<i64, AckRef>,
    ) -> rusqlite::Result<()> {
        let message_ids_by_ack = self.resolve_ack_message_ids(acks)?;

        // Each pair of a subscriber and a message that an acknowledgement is about, once ..
        let mut pairs = Vec::new();
        let mut seen = HashSet::new();

        for (ack, message_ids) in acks.iter().zip(&message_ids_by_ack) {
            for message_id in message_ids {
                let pair = (ack.sub_key.as_str(), *message_id);
                if seen.insert(pair) {
                    pairs.push(pair);
                }
            }
        }

        if pairs.is_empty() {
            return Ok(());
        }

        // .. with the delivery row of the pair ..
        let mut select = self.sqlite.prepare_cached(&self.statements.select_ack_delivery)?;
        let mut delivery_ids_by_pair = HashMap::with_capacity(pairs.len());

        for (sub_key, message_id) in pairs {
            let mut rows = select.query(params![message_id, sub_key])?;
            while let Some(row) = rows.next()? {
                delivery_ids_by_pair.insert((sub_key, message_id), row.get::<_, i64>(0)?);
            }
        }

        // .. removed in the order of their ids, so that concurrent transactions lock them in the same order ..
        let mut delivery_ids: Vec<i64> = delivery_ids_by_pair.values().copied().collect();
        delivery_ids.sort_unstable();

        let mut delete = self.sqlite.prepare_cached(&self.statements.delete_delivery)?;
        let mut removed_ids = HashSet::with_capacity(delivery_ids.len());

        if !delivery_ids.is_empty() {
            self.begin()?;
        }

        for delivery_id in delivery_ids {
            let mut rows = delete.query([delivery_id])?;
            while let Some(row) = rows.next()? {
                removed_ids.insert(row.get::<_, i64>(0)?);
            }
        }

        // .. and each removed row is assigned to the acknowledgement that removed it.
        for (ack_index, ((ack, message_ids), result)) in acks.iter().zip(&message_ids_by_ack).zip(results.iter_mut()).enumerate() {
            for message_id in message_ids {
                let delivery_id = delivery_ids_by_pair.remove(&(ack.sub_key.as_str(), *message_id));

                if delivery_id.is_some_and(|delivery_id| removed_ids.contains(&delivery_id)) {
                    result.removed_count = result.removed_count.saturating_add(1);
                    ack_by_message_id.insert(*message_id, AckRef::Plain(ack_index));
                } else {
                    ack_by_message_id.entry(*message_id).or_insert(AckRef::Plain(ack_index));
                }
            }
        }

        Ok(())
    }

    /// Writes a fenced acknowledgement with its publications, each reason for which the item fails
    /// checked before anything of it is written.
    fn write_atomic(
        &self,
        atomic_index: usize,
        atomic: &AtomicInput,
        result: &mut AtomicResult,
        ack_by_message_id: &mut BTreeMap<i64, AckRef>,
    ) -> Result<(), BatchError> {
        // The checks write nothing, so an item that fails them is only marked as failed ..
        let has_new_message = match self.check_atomic_publications(atomic)? {
            Ok(has_new_message) => has_new_message,
            Err(error) => {
                result.error = Some(error);
                return Ok(());
            }
        };

        let fenced_rows = match self.check_fenced(atomic, has_new_message, &mut result.ack)? {
            Ok(fenced_rows) => fenced_rows,
            Err(error) => {
                result.error = Some(error);
                return Ok(());
            }
        };

        // .. whereas after the first write of an item, without a savepoint, only the rollback of the transaction undoes it.
        if !atomic.publications.is_empty() {
            self.insert_publications(&atomic.publications, &mut result.publications)?;
        }

        if atomic.is_strict {
            let duplicate = result.publications.iter().position(|publication| publication.duplicate.is_some());
            if let Some(publication_index) = duplicate {
                return Err(BatchError::StrictDuplicate {
                    atomic_index,
                    publication_index,
                });
            }
        }

        self.delete_fenced(&fenced_rows, &mut result.ack)?;

        // The full delivery of a message counts towards the last acknowledgement that removed one of its rows
        for message_id in fenced_rows.message_ids {
            ack_by_message_id.insert(message_id, AckRef::Fenced(atomic_index));
        }

        Ok(())
    }

    /// Fails a strict item if the identifier of a publication stands for a different message, either one that exists
    /// already or one published earlier in the same item. Returns whether any publication inserts a new message.
    fn check_atomic_publications(&self, atomic: &AtomicInput) -> rusqlite::Result<Result<bool, ItemError>> {
        let mut select = self.sqlite.prepare_cached(&self.statements.select_existing_message)?;
        let mut existing: HashMap<&str, (String, i64)> = HashMap::new();
        let mut looked_up = HashSet::new();

        for publication in &atomic.publications {
            if !looked_up.insert(publication.msg_id.as_str()) {
                continue;
            }
            let mut rows = select.query([&publication.msg_id])?;
            if let Some(row) = rows.next()? {
                existing.insert(publication.msg_id.as_str(), (row.get(0)?, row.get(1)?));
            }
        }

        let mut out = false;

        for publication in &atomic.publications {
            let msg_id = publication.msg_id.as_str();

            // An identifier that nothing stands for yet inserts a new message ..
            let Some((topic_name, payload_crc32)) = existing.get(msg_id) else {
                existing.insert(msg_id, (publication.topic_name.clone(), publication.payload_crc32));
                out = true;
                continue;
            };

            // .. and one that stands for different content fails a strict item.
            let is_same = *topic_name == publication.topic_name && *payload_crc32 == publication.payload_crc32;

            if !is_same && atomic.is_strict {
                return Ok(Err(ItemError::Duplicate(duplicate_message(msg_id))));
            }
        }

        Ok(Ok(out))
    }

    /// Returns the delivery rows that a fenced acknowledgement removes, read before anything of it is written.
    ///
    /// A row with another attempt than the expected one was handed out again, and an absent row was concluded already,
    /// which fails the item only if its publications insert a new message.
    fn check_fenced(
        &self,
        atomic: &AtomicInput,
        has_new_message: bool,
        result: &mut AckResult,
    ) -> rusqlite::Result<Result<FencedRows, ItemError>> {
        // The last delivery row of each message, with its id, its message and its attempt ..
        let mut select = self.sqlite.prepare_cached(&self.statements.select_fenced_delivery)?;
        let mut rows_by_msg_id: HashMap<&str, Option<(i64, i64, i64)>> = HashMap::new();

        for entry in &atomic.entries {
            if let Entry::Vacant(slot) = rows_by_msg_id.entry(entry.msg_id.as_str()) {
                let mut rows = select.query(params![atomic.sub_key, entry.msg_id])?;
                let mut last = None;
                while let Some(row) = rows.next()? {
                    last = Some((row.get(0)?, row.get(1)?, row.get(2)?));
                }
                slot.insert(last);
            }
        }

        let mut delivery_ids = Vec::with_capacity(atomic.entries.len());
        let mut message_ids = Vec::with_capacity(atomic.entries.len());
        let mut absent = Vec::new();

        for entry in &atomic.entries {
            // .. a message that is not in the queue anymore was concluded by an earlier delivery ..
            let Some(Some((delivery_id, message_id, attempt))) = rows_by_msg_id.get(entry.msg_id.as_str()) else {
                absent.push(entry.msg_id.clone());
                continue;
            };

            // .. a message handed out again since belongs to the delivery that holds its current attempt ..
            if let Some(expected_attempt) = entry.expected_attempt
                && *attempt != expected_attempt
            {
                let msg_id = &entry.msg_id;
                let message = format!(
                    "Message `{msg_id}` was handed out again with delivery attempt {attempt}, \
                     the acknowledgement is for attempt {expected_attempt}"
                );
                return Ok(Err(ItemError::Conflict(message)));
            }

            // .. and any other message is removed from the queue, once even if the acknowledgement names it twice.
            if !delivery_ids.contains(delivery_id) {
                delivery_ids.push(*delivery_id);
                message_ids.push(*message_id);
            }
        }

        if let Some(first_absent) = absent.first() {
            if has_new_message {
                let message = format!("Message `{first_absent}` was concluded by another delivery");
                return Ok(Err(ItemError::Conflict(message)));
            }
            result.concluded_msg_ids = Some(absent);
        }

        Ok(Ok(FencedRows { delivery_ids, message_ids }))
    }

    /// Removes the delivery rows of a fenced acknowledgement in the order of their ids,
    /// so that concurrent transactions lock them in the same order.
    fn delete_fenced(&self, fenced_rows: &FencedRows, result: &mut AckResult) -> rusqlite::Result<()> {
        let mut delivery_ids = fenced_rows.delivery_ids.clone();
        delivery_ids.sort_unstable();

        let mut delete = self.sqlite.prepare_cached(&self.statements.delete_delivery)?;

        if !delivery_ids.is_empty() {
            self.begin()?;
        }

        for delivery_id in delivery_ids {
            let mut rows = delete.query([delivery_id])?;
            while rows.next()?.is_some() {
                result.removed_count = result.removed_count.saturating_add(1);
            }
        }

        Ok(())
    }

    /// Records the next push attempt of each delivery row of a batch, returning the attempt of each row that remains.
    fn record_attempts(&self, delivery_ids: &[i64], result: &mut Vec<(i64, i64)>) -> rusqlite::Result<()> {
        let mut update = self.sqlite.prepare_cached(&self.statements.record_attempt)?;

        // The Python driver opens the transaction for the update even when it has no rows to change
        self.begin()?;

        for delivery_id in delivery_ids {
            let mut rows = update.query([delivery_id])?;
            while let Some(row) = rows.next()? {
                result.push((*delivery_id, row.get(0)?));
            }
        }

        Ok(())
    }

    /// Leases the deliverable rows of one subscriber within the size budget of the pull
    /// and reads the messages of the rows it leased.
    fn lease_messages(&self, lease: &LeaseInput, result: &mut LeaseResult) -> rusqlite::Result<()> {
        let layout = self.layout;

        // The candidates in the order of the queue ..
        let mut select = self.sqlite.prepare_cached(&self.statements.select_lease_candidates)?;
        let candidates = select
            .query_map(params![lease.sub_key, lease.now_ms, lease.now_ms, lease.max_messages], |row| {
                Ok((row.get::<_, i64>(0)?, row.get::<_, i64>(1)?))
            })?
            .collect::<rusqlite::Result<Vec<_>>>()?;

        if candidates.is_empty() {
            return Ok(());
        }

        // .. those within the size budget, except that a message larger than the budget is handed out by the pull
        // .. that reaches it, after the messages ahead of it, and ends that pull ..
        let mut delivery_ids = Vec::with_capacity(candidates.len());
        let mut total_len: i64 = 0;

        for (delivery_id, data_size) in candidates {
            let is_oversized = data_size > lease.max_len;

            if !delivery_ids.is_empty() && total_len.saturating_add(data_size) > lease.max_len && !is_oversized {
                break;
            }

            total_len = total_len.saturating_add(data_size);
            delivery_ids.push(delivery_id);

            if is_oversized {
                break;
            }
        }

        // .. leased unless a concurrent pull leased them first ..
        let mut update = self.sqlite.prepare_cached(&self.statements.lease_delivery)?;
        let mut message_ids = Vec::with_capacity(delivery_ids.len());

        self.begin()?;

        for delivery_id in delivery_ids {
            let mut rows = update.query(params![lease.leased_until_ms, delivery_id, lease.now_ms])?;
            while let Some(row) = rows.next()? {
                let message_id: i64 = row.get(0)?;
                message_ids.push(message_id);
                result.attempts.push((message_id, row.get(1)?));
            }
        }

        // .. and the messages of the leased rows, by descending priority and then in the order of publication.
        let mut select_message = self.sqlite.prepare_cached(&self.statements.select_leased_message)?;
        let mut leased = Vec::with_capacity(message_ids.len());

        for message_id in message_ids {
            let mut rows = select_message.query([message_id])?;
            while let Some(row) = rows.next()? {
                let mut columns = Vec::with_capacity(layout.lease_column_count);
                for index in 0..layout.lease_column_count {
                    columns.push(row.get::<_, Value>(index)?);
                }
                let priority: i64 = row.get(layout.lease_priority_index)?;
                let id: i64 = row.get(layout.lease_id_index)?;
                leased.push((priority, id, columns));
            }
        }

        leased.sort_by(|left, right| right.0.cmp(&left.0).then(left.1.cmp(&right.1)));

        for (_, _, columns) in leased {
            result.rows.push(columns);
        }

        Ok(())
    }

    /// Drops the payloads of the acknowledged messages that no subscriber needs anymore, in the order of their ids,
    /// each counting as fully delivered towards its acknowledgement.
    fn drop_payloads(&self, ack_by_message_id: &BTreeMap<i64, AckRef>, results: &mut BatchResults) -> rusqlite::Result<()> {
        let mut update = self.sqlite.prepare_cached(&self.statements.drop_payload)?;

        self.begin()?;

        for (message_id, ack_ref) in ack_by_message_id {
            let mut rows = update.query([message_id])?;

            while rows.next()?.is_some() {
                let result = match *ack_ref {
                    AckRef::Plain(index) => results.acks.get_mut(index),
                    AckRef::Fenced(index) => results.atomics.get_mut(index).map(|atomic| &mut atomic.ack),
                };
                if let Some(result) = result {
                    result.fully_delivered_count = result.fully_delivered_count.saturating_add(1);
                }
            }
        }

        Ok(())
    }
}

/// Decides whether a publication whose message was not inserted repeats an existing message or fails as a different one.
fn resolve_duplicate(
    select_existing: &mut rusqlite::CachedStatement<'_>,
    publication: &PublicationInput,
    result: &mut PublicationResult,
) -> rusqlite::Result<()> {
    let mut rows = select_existing.query([&publication.msg_id])?;

    // The cleanup removed the existing message after the insert met it, which happens only to a message
    // that was published and fully processed, so this one is its repetition
    let Some(row) = rows.next()? else {
        result.repeat = Some(Repeat::Removed);
        return Ok(());
    };

    let topic_name: String = row.get(0)?;
    let payload_crc32: i64 = row.get(1)?;

    if topic_name == publication.topic_name && payload_crc32 == publication.payload_crc32 {
        result.repeat = Some(Repeat::Existing);
    } else {
        result.duplicate = Some(duplicate_message(&publication.msg_id));
    }

    Ok(())
}

/// Returns the message of the error of a publication whose identifier belongs to a different message.
fn duplicate_message(msg_id: &str) -> String {
    format!("Message ID `{msg_id}` belongs to a different message that exists already")
}

// ################################################################################################################################
// ################################################################################################################################
