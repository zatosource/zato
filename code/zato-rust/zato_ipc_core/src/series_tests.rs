//! Unit tests of the labeled metric series.

use std::collections::BTreeMap;
use std::sync::Barrier;
use std::thread;

use super::*;
use crate::layout::RegionParams;
use crate::view::test_support::{new_words, small_params};

/// The kind of a counter series, as the Python collector defines it.
const KIND_COUNTER: u64 = 1;

/// The kind of a gauge series, as the Python collector defines it.
const KIND_GAUGE: u64 = 2;

/// How many threads register the same series at once in the concurrency test.
const THREAD_COUNT: usize = 8;

/// How many keys each thread of the concurrency test registers.
const KEY_COUNT: usize = 48;

/// How many fresh regions the concurrency test registers its keys in.
const ROUND_COUNT: usize = 100;

/// Returns a view of a small region in ordinary memory.
fn new_view(params: RegionParams) -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(params)?;
    RegionView::new(words, layout)
}

#[test]
fn a_key_registers_one_series() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    let orders = view.series_register(KIND_COUNTER, "zato_rest_channel_requests_total\0orders\x002xx\0none")?;
    let invoices = view.series_register(KIND_COUNTER, "zato_rest_channel_requests_total\0invoices\x002xx\0none")?;
    let orders_again = view.series_register(KIND_COUNTER, "zato_rest_channel_requests_total\0orders\x002xx\0none")?;

    assert_eq!(orders, orders_again);
    assert_ne!(orders, invoices);
    assert_eq!(view.series_list()?.len(), 2);

    Ok(())
}

#[test]
fn one_key_of_two_kinds_is_two_series() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    let counter = view.series_register(KIND_COUNTER, "zato_metric")?;
    let gauge = view.series_register(KIND_GAUGE, "zato_metric")?;

    assert_ne!(counter, gauge);
    assert_eq!(view.series_list()?.len(), 2);

    Ok(())
}

#[test]
fn the_list_returns_each_series_with_its_key_kind_and_cell() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    let long_key = "zato_rest_channel_request_duration_seconds\0a channel name longer than one word";
    let short_index = view.series_register(KIND_COUNTER, "zato_short")?;
    let long_index = view.series_register(KIND_GAUGE, long_key)?;

    let mut by_key = BTreeMap::new();

    for record in view.series_list()? {
        by_key.insert(record.key.clone(), record);
    }

    let short_record = by_key.get("zato_short").ok_or(RegionError::OutOfBounds)?;
    let long_record = by_key.get(long_key).ok_or(RegionError::OutOfBounds)?;

    assert_eq!((short_record.kind, short_record.index), (KIND_COUNTER, short_index));
    assert_eq!((long_record.kind, long_record.index), (KIND_GAUGE, long_index));
    assert_eq!(by_key.len(), 2);

    Ok(())
}

#[test]
fn a_full_series_table_refuses_a_new_key_and_keeps_the_old_ones() -> Result<(), RegionError> {
    let params = small_params();
    let view = new_view(params)?;
    let mut registered = Vec::new();

    for index in 0..params.series_capacity {
        let key = format!("zato_metric\0{index}");
        let cell = view.series_register(KIND_COUNTER, &key)?;
        registered.push((key, cell));
    }

    assert_eq!(view.series_register(KIND_COUNTER, "zato_metric\0one more"), Err(RegionError::TableFull));

    for (key, cell) in registered {
        assert_eq!(view.series_register(KIND_COUNTER, &key)?, cell);
    }

    Ok(())
}

#[test]
fn a_key_longer_than_the_area_left_is_refused() -> Result<(), RegionError> {
    let params = small_params();
    let view = new_view(params)?;
    let long_key = "k".repeat(params.series_key_bytes);

    assert_eq!(view.series_register(KIND_COUNTER, &long_key), Err(RegionError::TableFull));

    Ok(())
}

#[test]
fn values_of_every_slot_are_summed_and_compared() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    let counter = view.series_register(KIND_COUNTER, "zato_counter")?;
    let gauge = view.series_register(KIND_GAUGE, "zato_gauge")?;

    view.series_add(0, counter, 5)?;
    view.series_add(3, counter, 7)?;

    view.series_add_float(1, gauge, 2.5)?;
    view.series_add_float(1, gauge, -1.0)?;
    view.series_set_float(2, gauge, 4.0)?;

    assert_eq!(view.series_sum(counter)?, 12);
    assert!((view.series_sum_float(gauge)? - 5.5).abs() < f64::EPSILON);
    assert!((view.series_max_float(gauge)? - 4.0).abs() < f64::EPSILON);

    Ok(())
}

#[test]
fn a_cell_outside_the_row_or_a_slot_outside_the_region_is_refused() -> Result<(), RegionError> {
    let params = small_params();
    let view = new_view(params)?;

    assert_eq!(view.series_add(0, params.series_capacity, 1), Err(RegionError::NoSuchMetric(params.series_capacity)));
    assert_eq!(view.series_add(params.slot_count, 0, 1), Err(RegionError::NoSuchSlot(params.slot_count)));

    Ok(())
}

#[test]
fn rows_of_two_slots_never_share_a_block() -> Result<(), RegionError> {
    let view = new_view(small_params())?;
    let layout = *view.layout();

    for slot in 0..layout.params.slot_count {
        let first = view.series_value(slot, 0)?;
        let first_index = view.words().iter().position(|word| std::ptr::eq(word, first)).ok_or(RegionError::OutOfBounds)?;

        assert_eq!((first_index - layout.series_values_start) % BLOCK_WORDS, 0);
    }

    Ok(())
}

#[test]
fn a_record_that_no_entry_publishes_is_not_listed_and_blocks_no_registration() -> Result<(), RegionError> {
    let view = new_view(small_params())?;

    // A worker terminated between the record and its entry leaves only the record
    let hash = key_hash(SERIES_KEY_KIND.wrapping_add(KIND_COUNTER), "zato_interrupted");
    let _ = view.write_series_record(hash, KIND_COUNTER, b"zato_interrupted")?;

    assert_eq!(view.series_list()?, Vec::new());

    let cell = view.series_register(KIND_COUNTER, "zato_interrupted")?;
    let records = view.series_list()?;

    assert_eq!(records.len(), 1);
    assert_eq!(records.first().map(|record| record.index), Some(cell));

    Ok(())
}

/// Registers the keys of each thread from threads that start together, returning the cells each thread received.
fn register_from_threads(view: &RegionView<'static>, keys_per_thread: &[Vec<String>]) -> Result<Vec<Vec<usize>>, RegionError> {
    let barrier = Barrier::new(keys_per_thread.len());

    let results: Vec<Result<Vec<usize>, RegionError>> = thread::scope(|scope| {
        let handles: Vec<_> = keys_per_thread
            .iter()
            .map(|keys| {
                let barrier = &barrier;

                scope.spawn(move || {
                    let mut cells = Vec::new();
                    let _ = barrier.wait();

                    for key in keys {
                        cells.push(view.series_register(KIND_COUNTER, key)?);
                    }

                    Ok(cells)
                })
            })
            .collect();

        handles.into_iter().map(|handle| handle.join().unwrap_or(Err(RegionError::OutOfBounds))).collect()
    });

    results.into_iter().collect()
}

/// Returns the parameters of a region whose area of records holds a record of every key from every thread.
fn concurrency_params() -> RegionParams {
    RegionParams {
        series_capacity: 64,
        series_key_bytes: 64 * THREAD_COUNT * KEY_COUNT,
        ..small_params()
    }
}

#[test]
fn workers_registering_different_keys_at_once_never_share_a_cell() -> Result<(), RegionError> {
    let keys_per_thread: Vec<Vec<String>> = (0..THREAD_COUNT)
        .map(|thread_index| {
            (0..KEY_COUNT / THREAD_COUNT)
                .map(|index| format!("zato_metric\0thread-{thread_index}-channel-{index}"))
                .collect()
        })
        .collect();

    for _ in 0..ROUND_COUNT {
        let view = new_view(concurrency_params())?;
        let per_thread = register_from_threads(&view, &keys_per_thread)?;

        // Each key has a cell of its own, and the record listed at that cell is the record of that key.
        let mut key_by_cell = BTreeMap::new();

        for (keys, cells) in keys_per_thread.iter().zip(&per_thread) {
            for (key, cell) in keys.iter().zip(cells) {
                assert_eq!(key_by_cell.insert(*cell, key.clone()), None);
            }
        }

        for record in view.series_list()? {
            assert_eq!(key_by_cell.get(&record.index), Some(&record.key));
        }
    }

    Ok(())
}

#[test]
fn workers_registering_the_same_keys_at_once_share_one_series_per_key() -> Result<(), RegionError> {
    let keys: Vec<String> = (0..KEY_COUNT).map(|index| format!("zato_metric\0channel-{index}")).collect();
    let keys_per_thread = vec![keys.clone(); THREAD_COUNT];

    for _ in 0..ROUND_COUNT {

        // Every thread may write a record of every key before one of them is published
        let view = new_view(concurrency_params())?;
        let per_thread = register_from_threads(&view, &keys_per_thread)?;

        // Every thread received the same cell for every key ..
        let first_thread = per_thread.first().ok_or(RegionError::OutOfBounds)?;

        for cells in &per_thread {
            assert_eq!(cells, first_thread);
        }

        // .. and each key is listed once, whichever thread published it.
        let records = view.series_list()?;
        assert_eq!(records.len(), keys.len());
    }

    Ok(())
}
