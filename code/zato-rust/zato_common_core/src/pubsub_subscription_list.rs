//! The subscription list of a worker - the subscriber and topic pairs of every subscription in `config.db`.
//!
//! The list governs the rows of `pubsub_topic_sub` of the sub keys that `new_sub_key` produces. It holds the pairs
//! that `config.db` configures and the pairs whose rows are committed in the pub/sub database, and the status
//! of each pair follows from the two. The Rust and the Python write paths of pub/sub read it under the write lock
//! of their transactions.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::sync::Arc;

use parking_lot::RwLock;
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// The prefix of the sub keys that `new_sub_key` produces.
const GOVERNED_PREFIX: &str = "sk";

/// The number of hexadecimal digits that follow the prefix of a governed sub key.
const GOVERNED_DIGITS: usize = 32;

/// The name of the status of a pair that is configured and whose row is committed.
pub const STATUS_CONFIRMED: &str = "confirmed";

/// The name of the status of a pair that is configured and has no row yet.
pub const STATUS_PENDING: &str = "pending";

/// The name of the status of a pair whose row exists and that is no longer configured.
pub const STATUS_PENDING_REMOVAL: &str = "pending-removal";

/// A subscriber and topic pair, the sub key first.
pub type Pair = (String, String);

/// The subscription list shared between the Python object and the write paths that run without the GIL.
pub type SharedList = Arc<RwLock<ListState>>;

// ################################################################################################################################
// ################################################################################################################################

/// Returns whether a sub key is in the format of `new_sub_key`, `sk` followed by 32 lowercase hexadecimal digits.
#[must_use]
pub fn is_governed_key(sub_key: &str) -> bool {
    let Some(digits) = sub_key.strip_prefix(GOVERNED_PREFIX) else {
        return false;
    };

    let has_length = digits.len() == GOVERNED_DIGITS;
    let is_hex = digits.bytes().all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte));

    has_length && is_hex
}

// ################################################################################################################################
// ################################################################################################################################

/// The flags of one subscriber and topic pair in `config.db`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct PairFlags {
    /// Whether the subscriber may publish to the topic.
    pub is_pub_enabled: bool,

    /// Whether the messages of the topic are delivered to the subscriber.
    pub is_delivery_enabled: bool,
}

/// One governed subscription of `config.db` with the flags of each of its topics.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Subscriber {
    /// Whether the subscriber may publish to any of its topics.
    pub is_pub_active: bool,

    /// The topics of the subscription by name, with the flags of each pair.
    pub topics: BTreeMap<String, PairFlags>,
}

/// The status of one pair of the list.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Status {
    /// The pair is configured and its row is committed.
    Confirmed,

    /// The pair is configured and has no row yet.
    Pending,

    /// The row of the pair exists and the pair is no longer configured.
    PendingRemoval,
}

impl Status {
    /// The name of the status that Python and Dashboard receive.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Confirmed => STATUS_CONFIRMED,
            Self::Pending => STATUS_PENDING,
            Self::PendingRemoval => STATUS_PENDING_REMOVAL,
        }
    }
}

// ################################################################################################################################
// ################################################################################################################################

/// The pairs that `config.db` configures and the pairs whose rows are committed, for governed sub keys alone.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ListState {
    /// The governed subscriptions of `config.db` by sub key.
    subscribers: HashMap<String, Subscriber>,

    /// The configured sub keys of each topic, kept in step with `subscribers`.
    by_topic: HashMap<String, BTreeSet<String>>,

    /// The topics of each sub key whose rows are committed in the pub/sub database.
    committed: HashMap<String, BTreeSet<String>>,

    /// Whether the state was built from `config.db`. Until then, publications use the rows of the pub/sub database as they are.
    is_loaded: bool,
}

/// The subscribers that one publication delivers to and the rows of pending pairs that it inserts.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Decision {
    /// The sub keys that the message receives a delivery row for.
    pub subscribers: Vec<String>,

    /// The pairs of the topic whose rows the publication inserts in the same commit as the message.
    pub added: Vec<Pair>,
}

impl ListState {
    /// Builds the state from the subscriptions of `config.db` and the rows committed in the pub/sub database,
    /// leaving out the sub keys that the list does not govern.
    #[must_use]
    pub fn from_parts(subscribers: Vec<(String, Subscriber)>, committed: Vec<Pair>) -> Self {
        let mut state = Self {
            is_loaded: true,
            ..Self::default()
        };

        for (sub_key, subscriber) in subscribers {
            // Sub keys of other mechanisms are owned by them and never enter the list
            if is_governed_key(&sub_key) {
                state.index_topics(&sub_key, &subscriber);
                state.subscribers.insert(sub_key, subscriber);
            }
        }

        state.mark_committed(committed, Vec::new());
        state
    }

    /// Adds the topics of a subscriber to the index by topic.
    fn index_topics(&mut self, sub_key: &str, subscriber: &Subscriber) {
        for topic in subscriber.topics.keys() {
            self.by_topic.entry(topic.clone()).or_default().insert(sub_key.to_owned());
        }
    }

    /// Removes the topics of a subscriber from the index by topic.
    fn unindex_topics(&mut self, sub_key: &str, subscriber: &Subscriber) {
        for topic in subscriber.topics.keys() {
            if let Some(sub_keys) = self.by_topic.get_mut(topic) {
                sub_keys.remove(sub_key);

                // A topic without configured subscribers leaves the index so that it does not grow with deleted topics
                if sub_keys.is_empty() {
                    self.by_topic.remove(topic);
                }
            }
        }
    }

    /// Sets the flags and the topics of one subscriber and returns the topics that it had before.
    pub fn set_topics(&mut self, sub_key: &str, subscriber: Subscriber) -> Vec<String> {
        let previous = self.remove(sub_key);
        self.index_topics(sub_key, &subscriber);
        self.subscribers.insert(sub_key.to_owned(), subscriber);
        previous
    }

    /// Removes one subscriber and returns the topics that it had.
    pub fn remove(&mut self, sub_key: &str) -> Vec<String> {
        let Some(previous) = self.subscribers.remove(sub_key) else {
            return Vec::new();
        };

        self.unindex_topics(sub_key, &previous);
        previous.topics.into_keys().collect()
    }

    /// Records the rows that a transaction inserted and deleted, after its commit.
    pub fn mark_committed(&mut self, added: Vec<Pair>, removed: Vec<Pair>) {
        for (sub_key, topic) in added {
            // A row of a sub key of another mechanism is never tracked
            if is_governed_key(&sub_key) {
                self.committed.entry(sub_key).or_default().insert(topic);
            }
        }

        for (sub_key, topic) in removed {
            if let Some(topics) = self.committed.get_mut(&sub_key) {
                topics.remove(&topic);

                // A sub key without rows leaves the map so that it does not grow with deleted subscriptions
                if topics.is_empty() {
                    self.committed.remove(&sub_key);
                }
            }
        }
    }

    /// Replaces the rows that the list considers committed with the rows read from the pub/sub database.
    pub fn replace_committed(&mut self, committed: Vec<Pair>) {
        self.committed.clear();
        self.mark_committed(committed, Vec::new());
    }

    /// Returns the configured sub keys of a topic.
    #[must_use]
    pub fn pairs_for_topic(&self, topic: &str) -> Vec<String> {
        self.by_topic
            .get(topic)
            .map_or_else(Vec::new, |sub_keys| sub_keys.iter().cloned().collect())
    }

    /// Decides the subscribers of a publication to a topic from the sub keys of its rows, read under the write lock.
    ///
    /// The rows of other mechanisms are kept, the configured pairs receive the message whether their rows exist or not,
    /// and the governed rows that are no longer configured are left out.
    #[must_use]
    pub fn decide_subscribers(&self, topic: &str, row_sub_keys: Vec<String>) -> Decision {
        // Before startup builds the list, nothing is governed and the rows decide alone
        if !self.is_loaded {
            return Decision {
                subscribers: row_sub_keys,
                added: Vec::new(),
            };
        }

        let configured = self.by_topic.get(topic);
        let is_configured = |sub_key: &String| configured.is_some_and(|sub_keys| sub_keys.contains(sub_key));

        let mut subscribers = Vec::with_capacity(row_sub_keys.len());
        let mut existing = BTreeSet::new();

        for sub_key in row_sub_keys {
            if !is_governed_key(&sub_key) {
                subscribers.push(sub_key);
            } else if is_configured(&sub_key) {
                existing.insert(sub_key.clone());
                subscribers.push(sub_key);
            }
        }

        let mut added = Vec::new();

        if let Some(sub_keys) = configured {
            for sub_key in sub_keys {
                // A configured pair without a row receives its row in the same commit as the message
                if !existing.contains(sub_key) {
                    subscribers.push(sub_key.clone());
                    added.push((sub_key.clone(), topic.to_owned()));
                }
            }
        }

        Decision { subscribers, added }
    }

    /// Returns the configured topics of a sub key.
    #[must_use]
    pub fn topics_of(&self, sub_key: &str) -> Vec<String> {
        self.subscribers
            .get(sub_key)
            .map_or_else(Vec::new, |subscriber| subscriber.topics.keys().cloned().collect())
    }

    /// Returns the topics of a sub key whose rows exist while the pairs are no longer configured.
    #[must_use]
    pub fn removed_topics(&self, sub_key: &str) -> Vec<String> {
        let Some(committed) = self.committed.get(sub_key) else {
            return Vec::new();
        };

        let configured = self.subscribers.get(sub_key);
        let is_configured = |topic: &String| configured.is_some_and(|subscriber| subscriber.topics.contains_key(topic));

        committed.iter().filter(|topic| !is_configured(topic)).cloned().collect()
    }

    /// Returns the topics whose messages the fetches of a sub key may hand out, or `None` if the list does not restrict them.
    ///
    /// A governed sub key receives only the messages of its configured topics whose delivery is switched on,
    /// so the messages of pairs pending removal, and those left behind by pairs removed before a restart, are withheld.
    /// The list restricts nothing before startup builds it, and nothing for the sub keys of other mechanisms.
    #[must_use]
    pub fn delivered_topics(&self, sub_key: &str) -> Option<Vec<String>> {
        if !self.is_loaded || !is_governed_key(sub_key) {
            return None;
        }

        let Some(subscriber) = self.subscribers.get(sub_key) else {
            return Some(Vec::new());
        };

        let delivered = subscriber
            .topics
            .iter()
            .filter(|(_, flags)| flags.is_delivery_enabled)
            .map(|(topic, _)| topic.clone())
            .collect();

        Some(delivered)
    }

    /// Returns whether queue browsing withholds the messages of a pair, which it does for a governed pair that is not configured.
    #[must_use]
    pub fn withholds_pair(&self, sub_key: &str, topic: &str) -> bool {
        if !self.is_loaded || !is_governed_key(sub_key) {
            return false;
        }

        let is_configured = self
            .subscribers
            .get(sub_key)
            .is_some_and(|subscriber| subscriber.topics.contains_key(topic));

        !is_configured
    }

    /// Returns whether a sub key may publish to a topic. A sub key that has no governed subscription is not restricted.
    #[must_use]
    pub fn is_publish_allowed(&self, sub_key: &str, topic: &str) -> bool {
        let Some(subscriber) = self.subscribers.get(sub_key) else {
            return true;
        };

        // A subscription whose publishing is switched off may publish to none of its topics
        if !subscriber.is_pub_active {
            return false;
        }

        subscriber.topics.get(topic).is_none_or(|flags| flags.is_pub_enabled)
    }

    /// Renames a topic in the configured pairs and in the committed rows in one step.
    pub fn rename_topic(&mut self, old_name: &str, new_name: &str) {
        if let Some(sub_keys) = self.by_topic.remove(old_name) {
            for sub_key in &sub_keys {
                if let Some(subscriber) = self.subscribers.get_mut(sub_key)
                    && let Some(flags) = subscriber.topics.remove(old_name)
                {
                    subscriber.topics.insert(new_name.to_owned(), flags);
                }
            }
            self.by_topic.insert(new_name.to_owned(), sub_keys);
        }

        for topics in self.committed.values_mut() {
            if topics.remove(old_name) {
                topics.insert(new_name.to_owned());
            }
        }
    }

    /// Removes a topic from every subscriber and from the committed rows, and returns the sub keys that had it.
    pub fn remove_topic(&mut self, topic: &str) -> Vec<String> {
        let sub_keys = self.by_topic.remove(topic).unwrap_or_default();
        let affected: Vec<String> = sub_keys.iter().cloned().collect();

        for sub_key in &sub_keys {
            if let Some(subscriber) = self.subscribers.get_mut(sub_key) {
                subscriber.topics.remove(topic);

                // A subscription with no topics left leaves the list
                if subscriber.topics.is_empty() {
                    self.subscribers.remove(sub_key);
                }
            }
        }

        let mut empty_sub_keys = Vec::new();

        for (sub_key, topics) in &mut self.committed {
            topics.remove(topic);

            if topics.is_empty() {
                empty_sub_keys.push(sub_key.clone());
            }
        }

        for sub_key in empty_sub_keys {
            self.committed.remove(&sub_key);
        }

        affected
    }

    /// Returns the pairs that have no row yet and the pairs whose rows are no longer configured.
    #[must_use]
    pub fn differences(&self) -> (Vec<Pair>, Vec<Pair>) {
        let mut pending = Vec::new();
        let mut removals = Vec::new();

        for pair_status in self.statuses() {
            match pair_status.status {
                Status::Confirmed => {}
                Status::Pending => pending.push((pair_status.sub_key, pair_status.topic)),
                Status::PendingRemoval => removals.push((pair_status.sub_key, pair_status.topic)),
            }
        }

        (pending, removals)
    }

    /// Returns whether any pair is pending or pending removal.
    #[must_use]
    pub fn has_unconfirmed(&self) -> bool {
        let (pending, removals) = self.differences();
        !pending.is_empty() || !removals.is_empty()
    }

    /// Returns the status of every pair, configured or committed, ordered by sub key and topic.
    #[must_use]
    pub fn statuses(&self) -> Vec<PairStatus> {
        let mut out = BTreeMap::new();

        for (sub_key, subscriber) in &self.subscribers {
            let committed = self.committed.get(sub_key);

            for topic in subscriber.topics.keys() {
                let is_committed = committed.is_some_and(|topics| topics.contains(topic));
                let status = if is_committed { Status::Confirmed } else { Status::Pending };
                out.insert((sub_key.clone(), topic.clone()), status);
            }
        }

        for (sub_key, topics) in &self.committed {
            for topic in topics {
                // A committed row of a configured pair is confirmed already, the others are pending removal
                out.entry((sub_key.clone(), topic.clone())).or_insert(Status::PendingRemoval);
            }
        }

        out.into_iter()
            .map(|((sub_key, topic), status)| PairStatus { sub_key, topic, status })
            .collect()
    }
}

/// The status of one pair.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PairStatus {
    /// The sub key of the subscriber.
    pub sub_key: String,

    /// The name of the topic.
    pub topic: String,

    /// Whether the pair is confirmed, pending or pending removal.
    pub status: Status,
}

// ################################################################################################################################
// ################################################################################################################################

/// The subscription list of a worker, shared by the Python and the Rust write paths of pub/sub.
///
/// Every change replaces or updates the state in one step under the write lock, with no input or output,
/// so a reader sees the state either before or after a change, never in between.
#[pyclass(frozen, name = "SubscriptionList")]
pub struct SubscriptionList {
    /// The state, which the write paths that run without the GIL read through their own reference.
    state: SharedList,
}

impl SubscriptionList {
    /// Returns a reference to the state for the write paths that run without the GIL.
    #[must_use]
    pub fn shared(&self) -> SharedList {
        Arc::clone(&self.state)
    }
}

#[pymethods]
impl SubscriptionList {
    /// The name of the status of a confirmed pair.
    #[classattr]
    const STATUS_CONFIRMED: &'static str = STATUS_CONFIRMED;

    /// The name of the status of a pending pair.
    #[classattr]
    const STATUS_PENDING: &'static str = STATUS_PENDING;

    /// The name of the status of a pair pending removal.
    #[classattr]
    const STATUS_PENDING_REMOVAL: &'static str = STATUS_PENDING_REMOVAL;

    /// Builds an empty list, which startup replaces before the first publication.
    #[new]
    fn new() -> Self {
        Self {
            state: Arc::new(RwLock::new(ListState::default())),
        }
    }

    /// Replaces the whole list with the subscriptions of `config.db` and the rows committed in the pub/sub database.
    ///
    /// The subscriptions map each sub key to a dict with `is_pub_active` and `topics`, which maps the name of each topic
    /// to a dict with `is_pub_enabled` and `is_delivery_enabled`.
    fn replace(&self, subscribers: &Bound<'_, PyDict>, committed: Vec<Pair>) -> PyResult<()> {
        let mut parsed = Vec::with_capacity(subscribers.len());
        for (sub_key, subscriber) in subscribers.iter() {
            parsed.push((sub_key.extract::<String>()?, extract_subscriber(&subscriber)?));
        }

        // The new state is built before the lock is taken, so the readers wait only for the swap itself
        let state = ListState::from_parts(parsed, committed);
        *self.state.write() = state;
        Ok(())
    }

    /// Sets the flags and the topics of one subscriber and returns the topics that it had before.
    fn set_topics(&self, sub_key: &str, is_pub_active: bool, topics: &Bound<'_, PyDict>) -> PyResult<Vec<String>> {
        let subscriber = Subscriber {
            is_pub_active,
            topics: extract_topics(topics)?,
        };
        Ok(self.state.write().set_topics(sub_key, subscriber))
    }

    /// Removes one subscriber and returns the topics that it had.
    fn remove(&self, sub_key: &str) -> Vec<String> {
        self.state.write().remove(sub_key)
    }

    /// Records the rows that a transaction inserted and deleted, after its commit.
    #[pyo3(signature = (added, removed=Vec::new()))]
    fn mark_committed(&self, added: Vec<Pair>, removed: Vec<Pair>) {
        self.state.write().mark_committed(added, removed);
    }

    /// Replaces the rows that the list considers committed with the rows read from the pub/sub database.
    fn replace_committed(&self, committed: Vec<Pair>) {
        self.state.write().replace_committed(committed);
    }

    /// Returns whether the list governs a sub key.
    #[staticmethod]
    fn is_governed(sub_key: &str) -> bool {
        is_governed_key(sub_key)
    }

    /// Returns the configured sub keys of a topic.
    fn pairs_for_topic(&self, topic: &str) -> Vec<String> {
        self.state.read().pairs_for_topic(topic)
    }

    /// Returns the sub keys that a publication to a topic delivers to and the pairs whose rows it inserts,
    /// given the sub keys of the rows of the topic read under the write lock.
    fn decide_subscribers(&self, topic: &str, row_sub_keys: Vec<String>) -> (Vec<String>, Vec<Pair>) {
        let decision = self.state.read().decide_subscribers(topic, row_sub_keys);
        (decision.subscribers, decision.added)
    }

    /// Returns whether startup has built the list from `config.db`.
    fn is_loaded(&self) -> bool {
        self.state.read().is_loaded
    }

    /// Returns the configured topics of a sub key.
    fn topics_of(&self, sub_key: &str) -> Vec<String> {
        self.state.read().topics_of(sub_key)
    }

    /// Returns the topics of a sub key whose rows exist while the pairs are no longer configured.
    fn removed_topics(&self, sub_key: &str) -> Vec<String> {
        self.state.read().removed_topics(sub_key)
    }

    /// Returns the topics whose messages the fetches of a sub key may hand out, or `None` if the list does not restrict them.
    fn delivered_topics(&self, sub_key: &str) -> Option<Vec<String>> {
        self.state.read().delivered_topics(sub_key)
    }

    /// Returns whether queue browsing withholds the messages of a pair.
    fn withholds_pair(&self, sub_key: &str, topic: &str) -> bool {
        self.state.read().withholds_pair(sub_key, topic)
    }

    /// Returns whether a sub key may publish to a topic.
    fn is_publish_allowed(&self, sub_key: &str, topic: &str) -> bool {
        self.state.read().is_publish_allowed(sub_key, topic)
    }

    /// Renames a topic in the configured pairs and in the committed rows in one step.
    fn rename_topic(&self, old_name: &str, new_name: &str) {
        self.state.write().rename_topic(old_name, new_name);
    }

    /// Removes a topic from every subscriber and from the committed rows, and returns the sub keys that had it.
    fn remove_topic(&self, topic: &str) -> Vec<String> {
        self.state.write().remove_topic(topic)
    }

    /// Returns the pairs that have no row yet and the pairs whose rows are no longer configured.
    fn differences(&self) -> (Vec<Pair>, Vec<Pair>) {
        self.state.read().differences()
    }

    /// Returns whether any pair is pending or pending removal.
    fn has_unconfirmed(&self) -> bool {
        self.state.read().has_unconfirmed()
    }

    /// Returns the sub key, the topic and the name of the status of every pair.
    fn statuses(&self) -> Vec<(String, String, &'static str)> {
        let statuses = self.state.read().statuses();
        statuses
            .into_iter()
            .map(|pair_status| (pair_status.sub_key, pair_status.topic, pair_status.status.name()))
            .collect()
    }
}

/// Extracts one subscriber from its dict with `is_pub_active` and `topics`.
fn extract_subscriber(subscriber: &Bound<'_, PyAny>) -> PyResult<Subscriber> {
    let is_pub_active: bool = subscriber.get_item("is_pub_active")?.extract()?;
    let topics = subscriber.get_item("topics")?.cast_into::<PyDict>()?;

    Ok(Subscriber {
        is_pub_active,
        topics: extract_topics(&topics)?,
    })
}

/// Extracts the flags of each topic from a dict that maps topic names to dicts with `is_pub_enabled` and `is_delivery_enabled`.
fn extract_topics(topics: &Bound<'_, PyDict>) -> PyResult<BTreeMap<String, PairFlags>> {
    let mut out = BTreeMap::new();

    for (topic, flags) in topics.iter() {
        let pair_flags = PairFlags {
            is_pub_enabled: flags.get_item("is_pub_enabled")?.extract()?,
            is_delivery_enabled: flags.get_item("is_delivery_enabled")?.extract()?,
        };
        out.insert(topic.extract::<String>()?, pair_flags);
    }

    Ok(out)
}

// ################################################################################################################################
// ################################################################################################################################

#[cfg(test)]
#[path = "pubsub_subscription_list_tests.rs"]
mod tests;
