//! Wake counters of subscription keys.
//!
//! A worker that committed a publication increments the counter of each subscription key
//! the publication was written to. The delivery loop of a key compares the counter with
//! the value it saw last and reads the database again when the two differ.
//! A collision of two keys on one entry, or a key that finds the table full, only
//! produces additional wake-ups, which the delivery loop tolerates by design.

use std::sync::atomic::Ordering;

use crate::error::RegionError;
use crate::layout::WAKE_OVERFLOW_WORD;
use crate::view::{EMPTY_KEY, RegionView, key_hash, probe_start};

/// Seed of the hash of subscription keys.
const WAKE_KEY_KIND: u64 = 0x5741_4B45;

/// Position of the key hash within a wake entry block.
const ENTRY_KEY: usize = 0;

/// Position of the counter within a wake entry block.
const ENTRY_COUNTER: usize = 1;

/// How a probe for a key ended.
enum Probe {

    /// The entry of the key, at this block of the table.
    Found(usize),

    /// No entry of the table has the key.
    Absent,
}

impl RegionView<'_> {

    /// Returns the offset of one field of a wake entry block.
    fn wake_word(&self, entry: usize, field: usize) -> Result<usize, RegionError> {
        Self::block_word(self.layout().wake_start, entry, field)
    }

    /// Looks up the entry of a key, claiming an empty one for it when `is_claim` is set.
    fn wake_probe(&self, hash: u64, is_claim: bool) -> Result<Probe, RegionError> {
        let capacity = self.layout().params.wake_capacity;
        let start = probe_start(hash, capacity);

        for step in 0..capacity {

            // Linear probing visits every entry once, starting from the key's own.
            let entry = start.wrapping_add(step) % capacity;
            let key_word = self.word(self.wake_word(entry, ENTRY_KEY)?)?;
            let current = key_word.load(Ordering::SeqCst);

            if current == hash {
                return Ok(Probe::Found(entry));
            }

            if current == EMPTY_KEY {

                // A lookup that meets an empty entry knows the key was never stored,
                // because entries are claimed in probe order and never released.
                if !is_claim {
                    return Ok(Probe::Absent);
                }

                // Another worker may claim the same entry at this moment, for this key or for another one.
                match key_word.compare_exchange(EMPTY_KEY, hash, Ordering::SeqCst, Ordering::SeqCst) {
                    Ok(_) => return Ok(Probe::Found(entry)),
                    Err(winner) if winner == hash => return Ok(Probe::Found(entry)),
                    Err(_) => {}
                }
            }
        }

        Ok(Probe::Absent)
    }

    /// Returns the counter of the keys that found the table full.
    fn wake_overflow(&self) -> Result<&std::sync::atomic::AtomicU64, RegionError> {
        self.word(WAKE_OVERFLOW_WORD)
    }

    /// Increments the wake counter of a subscription key after a committed publication.
    pub fn wake_increment(&self, sub_key: &str) -> Result<(), RegionError> {
        let hash = key_hash(WAKE_KEY_KIND, sub_key);

        match self.wake_probe(hash, true)? {
            Probe::Found(entry) => {
                let counter = self.word(self.wake_word(entry, ENTRY_COUNTER)?)?;
                counter.fetch_add(1, Ordering::SeqCst);
            }

            // A full table moves the counter that every key's value includes, so every loop reads its queue again.
            Probe::Absent => {
                self.wake_overflow()?.fetch_add(1, Ordering::SeqCst);
            }
        }

        Ok(())
    }

    /// Returns the value a delivery loop compares with the one it saw last for its subscription key.
    pub fn wake_value(&self, sub_key: &str) -> Result<u64, RegionError> {
        let hash = key_hash(WAKE_KEY_KIND, sub_key);
        let overflow = self.wake_overflow()?.load(Ordering::SeqCst);

        let counter = match self.wake_probe(hash, false)? {
            Probe::Found(entry) => self.word(self.wake_word(entry, ENTRY_COUNTER)?)?.load(Ordering::SeqCst),
            Probe::Absent => 0,
        };

        // A change of either part is a wake-up, so the two are combined without regard to overflow.
        let out = counter.wrapping_add(overflow);
        Ok(out)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::layout::RegionParams;
    use crate::view::test_support::{new_words, small_params};

    #[test]
    fn increment_changes_value_of_its_key_only() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        let before_first = view.wake_value("zpsk.rest.orders")?;
        let before_second = view.wake_value("zpsk.rest.invoices")?;

        view.wake_increment("zpsk.rest.orders")?;

        assert_ne!(view.wake_value("zpsk.rest.orders")?, before_first);
        assert_eq!(view.wake_value("zpsk.rest.invoices")?, before_second);

        Ok(())
    }

    #[test]
    fn full_table_wakes_every_key() -> Result<(), RegionError> {
        let params = RegionParams {
            wake_capacity: 2,
            ..small_params()
        };
        let (words, layout) = new_words(params)?;
        let view = RegionView::new(words, layout)?;

        view.wake_increment("zpsk.rest.orders")?;
        view.wake_increment("zpsk.rest.invoices")?;

        let unrelated_before = view.wake_value("zpsk.rest.shipments")?;

        // The table has no entry left for a third key, so its wake-up reaches every key.
        view.wake_increment("zpsk.rest.payments")?;

        assert_ne!(view.wake_value("zpsk.rest.shipments")?, unrelated_before);
        assert_ne!(view.wake_value("zpsk.rest.payments")?, 0);

        Ok(())
    }

    #[test]
    fn concurrent_increments_are_all_counted() -> Result<(), RegionError> {
        let (words, layout) = new_words(small_params())?;
        let view = RegionView::new(words, layout)?;

        let thread_count = 4;
        let per_thread = 1000;

        std::thread::scope(|scope| {
            for _ in 0..thread_count {
                scope.spawn(|| {
                    for _ in 0..per_thread {
                        view.wake_increment("zpsk.rest.orders").ok();
                    }
                });
            }
        });

        assert_eq!(view.wake_value("zpsk.rest.orders")?, thread_count * per_thread);

        Ok(())
    }
}
