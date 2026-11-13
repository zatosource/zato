//! Bounded map that evicts the least recently used entry, keyed by match targets.

use std::collections::{BTreeMap, HashMap};

/// One cached value together with the position it holds in the recency order.
struct Slot<V> {
    /// The cached value.
    value: V,

    /// Position in the recency order, higher meaning more recently used.
    tick: u64,
}

/// Map of a bounded size in which inserting into a full map evicts the least recently used entry.
pub struct LruCache<V> {
    /// Maximum number of entries.
    capacity: usize,

    /// Next position to hand out in the recency order.
    next_tick: u64,

    /// Entries by key.
    slots: HashMap<String, Slot<V>>,

    /// Keys by their position in the recency order.
    order: BTreeMap<u64, String>,
}

impl<V> LruCache<V> {
    /// Returns an empty cache holding at most `capacity` entries.
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            next_tick: 0,
            slots: HashMap::new(),
            order: BTreeMap::new(),
        }
    }

    /// Returns the next position in the recency order.
    const fn take_tick(&mut self) -> u64 {
        let out = self.next_tick;
        self.next_tick = self.next_tick.wrapping_add(1);
        out
    }

    /// Returns the value under the key and marks it as the most recently used entry.
    pub fn get(&mut self, key: &str) -> Option<&V> {
        let tick = self.take_tick();
        let slot = self.slots.get_mut(key)?;

        // The entry moves to the most recent end so that eviction skips it
        if let Some(moved_key) = self.order.remove(&slot.tick) {
            self.order.insert(tick, moved_key);
        }
        slot.tick = tick;

        Some(&slot.value)
    }

    /// Returns the value under the key without changing the recency order.
    pub fn peek(&self, key: &str) -> Option<&V> {
        self.slots.get(key).map(|slot| &slot.value)
    }

    /// Stores a value under the key, evicting the least recently used entry if the cache is full.
    pub fn insert(&mut self, key: String, value: V) {
        let tick = self.take_tick();

        // A key already present keeps its slot and only its value and recency change
        if let Some(slot) = self.slots.get_mut(&key) {
            self.order.remove(&slot.tick);
            self.order.insert(tick, key);
            slot.tick = tick;
            slot.value = value;
            return;
        }

        if self.slots.len() >= self.capacity {
            self.evict_oldest();
        }

        self.order.insert(tick, key.clone());
        self.slots.insert(key, Slot { value, tick });
    }

    /// Removes the least recently used entry.
    fn evict_oldest(&mut self) {
        if let Some((_, oldest_key)) = self.order.pop_first() {
            self.slots.remove(&oldest_key);
        }
    }

    /// Returns the number of entries.
    pub fn len(&self) -> usize {
        self.slots.len()
    }

    /// Whether the cache has no entries.
    pub fn is_empty(&self) -> bool {
        self.slots.is_empty()
    }
}
