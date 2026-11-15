//! Labeled metric series kept per worker slot and summed across the slots on scrape.
//!
//! A series is one metric name with one set of label values, or one bucket of a histogram, and it has one
//! value cell in the row of each slot, at the position of its entry in the series table. The first worker
//! that records a series writes its record, which holds its key and its kind, to the area of records, and
//! publishes the record through one compare-and-swap of the entry. A worker terminated during a registration
//! therefore leaves at most a record that no entry refers to, and never an entry that another worker waits for.
//! Workers that register one series at the same moment each write a record, and the records of all but the
//! one published remain unreferenced, so the area of records is sized for one record per series and slot.
//! Only the worker of a slot writes the row of that slot, so a value cell needs no compare-and-swap.

use std::sync::atomic::{AtomicU64, Ordering};

use crate::error::RegionError;
use crate::layout::{BLOCK_WORDS, BYTES_PER_WORD, SERIES_KEY_CURSOR_WORD};
use crate::view::{EMPTY_KEY, RegionView, key_hash, probe_start};

/// Seed of the hash of series keys, to which the kind of the series is added.
const SERIES_KEY_KIND: u64 = 0x5345_5249_4553;

/// Position of the hash of the key within a record.
const RECORD_HASH: usize = 0;

/// Position of the kind of the series within a record.
const RECORD_KIND: usize = 1;

/// Position of the length of the key in bytes within a record.
const RECORD_KEY_LEN: usize = 2;

/// Number of words of a record that precede the bytes of its key.
const RECORD_HEADER_WORDS: usize = 3;

/// An entry word holds the position of its record plus this value, so that no published entry equals `EMPTY_KEY`.
const ENTRY_POSITION_OFFSET: u64 = 1;

/// One registered series, as a scrape lists it.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SeriesRecord {

    /// The metric name and the label values of the series.
    pub key: String,

    /// The kind of the series, which the caller defines.
    pub kind: u64,

    /// The value cell of the series in the row of each slot.
    pub index: usize,
}

/// Converts a word of the region to a size.
fn to_size(word: u64) -> Result<usize, RegionError> {
    usize::try_from(word).map_err(|_conversion_error| RegionError::OutOfBounds)
}

/// Converts a size to a word of the region.
fn to_word(size: usize) -> Result<u64, RegionError> {
    u64::try_from(size).map_err(|_conversion_error| RegionError::OutOfBounds)
}

/// Returns the word that holds up to eight bytes of a key, in little-endian order and padded with zeros.
fn pack_key_word(chunk: &[u8]) -> u64 {
    let mut bytes = [0_u8; BYTES_PER_WORD];

    for (target, source) in bytes.iter_mut().zip(chunk) {
        *target = *source;
    }

    u64::from_le_bytes(bytes)
}

/// Returns the position of the word of a record that holds a chunk of its key.
fn key_field(offset: usize) -> Result<usize, RegionError> {
    RECORD_HEADER_WORDS.checked_add(offset).ok_or(RegionError::OutOfBounds)
}

impl RegionView<'_> {

    /// Returns an entry word of the series table.
    fn series_entry(&self, entry: usize) -> Result<&AtomicU64, RegionError> {
        let index = self.layout().series_start.checked_add(entry).ok_or(RegionError::OutOfBounds)?;
        self.word(index)
    }

    /// Returns a word of the record that starts at `position` of the area of records.
    fn record_word(&self, position: usize, field: usize) -> Result<&AtomicU64, RegionError> {
        let layout = self.layout();
        let relative = position.checked_add(field).ok_or(RegionError::OutOfBounds)?;

        // The words that follow the area belong to the value table, which no record extends into
        if relative >= layout.series_key_words {
            return Err(RegionError::OutOfBounds);
        }

        let index = layout.series_keys_start.checked_add(relative).ok_or(RegionError::OutOfBounds)?;
        self.word(index)
    }

    /// Takes the words of one record from the area of records, returning the position of the first.
    fn take_record_words(&self, count: usize) -> Result<usize, RegionError> {
        let count_word = to_word(count)?;
        let first = to_size(self.word(SERIES_KEY_CURSOR_WORD)?.fetch_add(count_word, Ordering::Relaxed))?;
        let end = first.checked_add(count).ok_or(RegionError::TableFull)?;

        // Words past the area remain taken, so every later registration finds the area full as well
        if end > self.layout().series_key_words {
            return Err(RegionError::TableFull);
        }

        Ok(first)
    }

    /// Writes the record of a new series, which no entry refers to yet, and returns its position in the area of records.
    fn write_series_record(&self, hash: u64, kind: u64, key: &[u8]) -> Result<usize, RegionError> {
        let key_words = key.len().div_ceil(BYTES_PER_WORD);
        let record_words = RECORD_HEADER_WORDS.checked_add(key_words).ok_or(RegionError::TableFull)?;
        let position = self.take_record_words(record_words)?;

        let header = [(RECORD_HASH, hash), (RECORD_KIND, kind), (RECORD_KEY_LEN, to_word(key.len())?)];

        // No other worker reads these words before the entry that publishes the record is set
        for (field, value) in header {
            self.record_word(position, field)?.store(value, Ordering::Relaxed);
        }

        for (offset, chunk) in key.chunks(BYTES_PER_WORD).enumerate() {
            self.record_word(position, key_field(offset)?)?.store(pack_key_word(chunk), Ordering::Relaxed);
        }

        Ok(position)
    }

    /// Returns whether the record at `position` is the record of a key.
    fn series_record_matches(&self, position: usize, hash: u64, key: &[u8]) -> Result<bool, RegionError> {
        if self.record_word(position, RECORD_HASH)?.load(Ordering::Relaxed) != hash {
            return Ok(false);
        }

        let key_len = to_size(self.record_word(position, RECORD_KEY_LEN)?.load(Ordering::Relaxed))?;

        if key_len != key.len() {
            return Ok(false);
        }

        for (offset, chunk) in key.chunks(BYTES_PER_WORD).enumerate() {
            if self.record_word(position, key_field(offset)?)?.load(Ordering::Relaxed) != pack_key_word(chunk) {
                return Ok(false);
            }
        }

        Ok(true)
    }

    /// Reads the record at `position`, which the entry at `index` publishes.
    fn read_series_record(&self, position: usize, index: usize) -> Result<SeriesRecord, RegionError> {
        let kind = self.record_word(position, RECORD_KIND)?.load(Ordering::Relaxed);
        let key_len = to_size(self.record_word(position, RECORD_KEY_LEN)?.load(Ordering::Relaxed))?;

        let key_words = key_len.div_ceil(BYTES_PER_WORD);
        let mut key_bytes = Vec::with_capacity(key_words.saturating_mul(BYTES_PER_WORD));

        for offset in 0..key_words {
            let word = self.record_word(position, key_field(offset)?)?.load(Ordering::Relaxed);
            key_bytes.extend_from_slice(&word.to_le_bytes());
        }

        // The last word is padded with zeros, which are not part of the key
        key_bytes.truncate(key_len);
        let key = String::from_utf8(key_bytes).map_err(|_utf8_error| RegionError::InvalidSeriesKey)?;

        let out = SeriesRecord { key, kind, index };
        Ok(out)
    }

    /// Converts a published entry word to the position of its record.
    fn entry_position(entry_word: u64) -> Result<usize, RegionError> {
        let position = entry_word.checked_sub(ENTRY_POSITION_OFFSET).ok_or(RegionError::OutOfBounds)?;
        to_size(position)
    }

    /// Returns the value cell of the series of a key, registering the series if no worker has registered it yet.
    pub fn series_register(&self, kind: u64, key: &str) -> Result<usize, RegionError> {
        let hash = key_hash(SERIES_KEY_KIND.wrapping_add(kind), key);
        let key_bytes = key.as_bytes();

        let capacity = self.layout().params.series_capacity;
        let start = probe_start(hash, capacity);

        let mut prepared: Option<usize> = None;

        for step in 0..capacity {

            // Linear probing visits every entry once, starting from the key's own.
            let entry = start.wrapping_add(step) % capacity;
            let entry_word = self.series_entry(entry)?;

            // The acquire load makes the record of a published entry visible before it is read.
            let mut current = entry_word.load(Ordering::Acquire);

            if current == EMPTY_KEY {

                // The record is written once, at the first empty entry of the probe, before any other worker can see it ..
                let position = if let Some(position) = prepared {
                    position
                } else {
                    let position = self.write_series_record(hash, kind, key_bytes)?;
                    prepared = Some(position);
                    position
                };

                let published = to_word(position)?.checked_add(ENTRY_POSITION_OFFSET).ok_or(RegionError::OutOfBounds)?;

                // .. and the compare-and-swap publishes it, unless another worker published a record in this entry first.
                match entry_word.compare_exchange(EMPTY_KEY, published, Ordering::AcqRel, Ordering::Acquire) {
                    Ok(_) => return Ok(entry),
                    Err(winner) => current = winner,
                }
            }

            // An entry that another worker published is the entry of this series when its record has this key,
            // and a record that this worker prepared for the same series is then left unreferenced.
            let position = Self::entry_position(current)?;

            if self.series_record_matches(position, hash, key_bytes)? {
                return Ok(entry);
            }
        }

        Err(RegionError::TableFull)
    }

    /// Returns every registered series, in the order of the entries of the series table.
    pub fn series_list(&self) -> Result<Vec<SeriesRecord>, RegionError> {
        let capacity = self.layout().params.series_capacity;
        let mut out = Vec::new();

        for entry in 0..capacity {
            let current = self.series_entry(entry)?.load(Ordering::Acquire);

            if current != EMPTY_KEY {
                let position = Self::entry_position(current)?;
                out.push(self.read_series_record(position, entry)?);
            }
        }

        Ok(out)
    }

    /// Returns the value cell of a series in the row of a slot.
    pub(crate) fn series_value(&self, slot: usize, index: usize) -> Result<&AtomicU64, RegionError> {
        self.check_slot(slot)?;

        let layout = self.layout();

        if index >= layout.params.series_capacity {
            return Err(RegionError::NoSuchMetric(index));
        }

        // Each row starts at a block of its own, and its cells follow one another within the row.
        let row_blocks = slot.checked_mul(layout.series_blocks_per_slot).ok_or(RegionError::OutOfBounds)?;
        let block = row_blocks.checked_add(index / BLOCK_WORDS).ok_or(RegionError::OutOfBounds)?;
        let word_index = Self::block_word(layout.series_values_start, block, index % BLOCK_WORDS)?;

        self.word(word_index)
    }

    /// Adds `delta` to the integer value cell of a series in the row of a slot.
    pub fn series_add(&self, slot: usize, index: usize, delta: u64) -> Result<(), RegionError> {

        // Only the worker of the slot writes its row, so the order relative to other words does not matter.
        self.series_value(slot, index)?.fetch_add(delta, Ordering::Relaxed);
        Ok(())
    }

    /// Adds `delta` to the floating-point value cell of a series in the row of a slot.
    pub fn series_add_float(&self, slot: usize, index: usize, delta: f64) -> Result<(), RegionError> {
        let cell = self.series_value(slot, index)?;

        // Only the worker of the slot writes its row, so no other write falls between the load and the store.
        let current = f64::from_bits(cell.load(Ordering::Relaxed));
        let updated = current + delta;
        cell.store(updated.to_bits(), Ordering::Relaxed);

        Ok(())
    }

    /// Sets the floating-point value cell of a series in the row of a slot.
    pub fn series_set_float(&self, slot: usize, index: usize, value: f64) -> Result<(), RegionError> {
        self.series_value(slot, index)?.store(value.to_bits(), Ordering::Relaxed);
        Ok(())
    }

    /// Returns the sum of the integer value cell of a series over every slot.
    pub fn series_sum(&self, index: usize) -> Result<u64, RegionError> {
        let mut out: u64 = 0;

        for slot in 0..self.layout().params.slot_count {
            let value = self.series_value(slot, index)?.load(Ordering::Relaxed);
            out = out.wrapping_add(value);
        }

        Ok(out)
    }

    /// Returns the sum of the floating-point value cell of a series over every slot.
    pub fn series_sum_float(&self, index: usize) -> Result<f64, RegionError> {
        let mut out: f64 = 0.0;

        for slot in 0..self.layout().params.slot_count {
            let value = f64::from_bits(self.series_value(slot, index)?.load(Ordering::Relaxed));
            out += value;
        }

        Ok(out)
    }

    /// Returns the largest value of the floating-point value cell of a series over every slot.
    pub fn series_max_float(&self, index: usize) -> Result<f64, RegionError> {
        let mut out = f64::NEG_INFINITY;

        for slot in 0..self.layout().params.slot_count {
            let value = f64::from_bits(self.series_value(slot, index)?.load(Ordering::Relaxed));
            out = out.max(value);
        }

        Ok(out)
    }
}

#[cfg(test)]
#[path = "series_tests.rs"]
mod tests;
