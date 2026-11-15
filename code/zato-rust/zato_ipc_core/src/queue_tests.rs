//! Unit tests of the writer queues.

use std::sync::atomic::{AtomicU64, Ordering};

use super::*;
use crate::view::test_support::{new_words, small_params};

/// Queue of the database file the tests write.
const QUEUE: usize = 1;

fn new_view() -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(small_params())?;
    RegionView::new(words, layout)
}

/// Returns whether a slot holds the turn of the test queue.
fn has_turn(view: &RegionView<'_>, slot: usize) -> Result<bool, RegionError> {
    let (out, _) = view.queue_poll(QUEUE, slot)?;
    Ok(out)
}

#[test]
fn slots_are_served_in_order_of_entry() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, 2)?;
    view.queue_enter(QUEUE, 0)?;
    view.queue_enter(QUEUE, 3)?;

    assert!(has_turn(&view, 2)?);
    assert!(!has_turn(&view, 0)?);

    assert_eq!(view.queue_release(QUEUE, 2)?, Some(0));
    assert!(has_turn(&view, 0)?);

    assert_eq!(view.queue_release(QUEUE, 0)?, Some(3));
    assert_eq!(view.queue_release(QUEUE, 3)?, None);

    Ok(())
}

#[test]
fn queues_of_two_files_are_independent() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(0, 1)?;
    view.queue_enter(QUEUE, 2)?;

    assert!(has_turn(&view, 2)?);
    assert_eq!(view.queue_poll(0, 1)?, (true, None));

    Ok(())
}

#[test]
fn abandoned_waiter_is_passed_over() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, 0)?;
    view.queue_enter(QUEUE, 1)?;
    view.queue_enter(QUEUE, 2)?;

    // The deadline of the waiter of slot 1 passes while slot 0 writes.
    assert_eq!(view.queue_abandon(QUEUE, 1)?, Some(0));

    assert_eq!(view.queue_release(QUEUE, 0)?, Some(2));
    assert!(has_turn(&view, 2)?);

    Ok(())
}

#[test]
fn terminated_holder_passes_its_turn() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, 0)?;
    view.queue_enter(QUEUE, 1)?;

    // The worker of slot 0 terminates while it holds the turn, and the arbiter withdraws its ticket.
    assert_eq!(view.queue_abandon(QUEUE, 0)?, Some(1));
    assert!(has_turn(&view, 1)?);

    Ok(())
}

#[test]
fn worker_terminated_after_taking_a_ticket_is_passed_over() -> Result<(), RegionError> {
    let view = new_view()?;
    let (next, _) = view.queue_head(QUEUE)?;

    view.queue_enter(QUEUE, 0)?;

    // The worker of slot 1 marks its entry, takes the next ticket and terminates before it records it.
    view.queue_record(QUEUE, 1)?.store(RECORD_ENTERING, Ordering::SeqCst);
    next.fetch_add(1, Ordering::SeqCst);

    view.queue_enter(QUEUE, 2)?;

    // While slot 1 is marked as entering, the queue cannot tell whose ticket follows slot 0's.
    assert_eq!(view.queue_release(QUEUE, 0)?, None);
    assert!(!has_turn(&view, 2)?);

    // Once the arbiter marks slot 1, the queue passes over its ticket.
    assert_eq!(view.queue_abandon(QUEUE, 1)?, Some(2));
    assert!(has_turn(&view, 2)?);

    Ok(())
}

#[test]
fn worker_terminated_before_taking_a_ticket_changes_nothing() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, 0)?;
    view.queue_record(QUEUE, 1)?.store(RECORD_ENTERING, Ordering::SeqCst);
    view.queue_enter(QUEUE, 2)?;

    view.queue_abandon(QUEUE, 1)?;

    assert!(has_turn(&view, 0)?);
    assert_eq!(view.queue_release(QUEUE, 0)?, Some(2));

    Ok(())
}

#[test]
fn replacement_worker_enters_the_same_slot() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, 0)?;
    view.queue_enter(QUEUE, 1)?;
    view.queue_abandon(QUEUE, 1)?;

    // The replacement of slot 1 takes a new ticket in place of the withdrawn one.
    view.queue_enter(QUEUE, 1)?;
    assert_eq!(view.queue_release(QUEUE, 0)?, Some(1));

    Ok(())
}

#[test]
fn second_ticket_and_foreign_release_are_refused() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, 0)?;
    view.queue_enter(QUEUE, 1)?;

    assert_eq!(view.queue_enter(QUEUE, 0), Err(RegionError::AlreadyQueued(0)));
    assert_eq!(view.queue_release(QUEUE, 1), Err(RegionError::NotHoldingTurn(1)));
    assert_eq!(view.queue_release(QUEUE, 3), Err(RegionError::NotHoldingTurn(3)));
    // The queues of the keyed locks follow the writer queues, and no queue follows those
    let past_last = view.layout().queue_total;
    assert_eq!(view.queue_enter(past_last, 0), Err(RegionError::NoSuchQueue(past_last)));

    Ok(())
}

#[test]
fn writer_process_takes_turns_with_the_slots() -> Result<(), RegionError> {
    let view = new_view()?;
    let writer = view.layout().writer_place();

    view.queue_enter(QUEUE, 1)?;
    view.queue_enter(QUEUE, writer)?;
    view.queue_enter(QUEUE, 0)?;

    // The writer process waits behind the slot that entered first, and the slot that entered after it waits behind it.
    assert!(!has_turn(&view, writer)?);
    assert_eq!(view.queue_release(QUEUE, 1)?, Some(writer));

    assert!(has_turn(&view, writer)?);
    assert_eq!(view.queue_release(QUEUE, writer)?, Some(0));

    Ok(())
}

#[test]
fn terminated_writer_process_passes_its_turn() -> Result<(), RegionError> {
    let view = new_view()?;
    let writer = view.layout().writer_place();

    view.queue_enter(QUEUE, writer)?;
    view.queue_enter(QUEUE, 2)?;

    // The writer process terminates while it holds the turn, and the arbiter withdraws its ticket.
    assert_eq!(view.queue_abandon(QUEUE, writer)?, Some(2));
    assert!(has_turn(&view, 2)?);

    // The place after that of the config process does not exist.
    let beyond = view.layout().config_place() + 1;
    assert_eq!(view.queue_enter(QUEUE, beyond), Err(RegionError::NoSuchSlot(beyond)));

    Ok(())
}

#[test]
fn config_process_takes_turns_after_the_writer_process() -> Result<(), RegionError> {
    let view = new_view()?;
    let writer = view.layout().writer_place();
    let config = view.layout().config_place();

    // The config process holds the place that follows that of the writer process ..
    assert_eq!(config, writer + 1);

    view.queue_enter(QUEUE, writer)?;
    view.queue_enter(QUEUE, config)?;

    // .. and waits for its turn behind it as a slot does.
    assert!(!has_turn(&view, config)?);
    assert_eq!(view.queue_release(QUEUE, writer)?, Some(config));
    assert!(has_turn(&view, config)?);

    Ok(())
}

#[test]
fn concurrent_writers_never_overlap() -> Result<(), RegionError> {
    let view = new_view()?;
    let slot_count = small_params().slot_count;
    let rounds = 2000;

    // Number of slots inside the protected section, and the largest number ever seen there.
    let inside = AtomicU64::new(0);
    let most_inside = AtomicU64::new(0);
    let completed = AtomicU64::new(0);

    std::thread::scope(|scope| {
        for slot in 0..slot_count {
            let view = &view;
            let inside = &inside;
            let most_inside = &most_inside;
            let completed = &completed;

            scope.spawn(move || {
                for _ in 0..rounds {
                    if view.queue_enter(QUEUE, slot).is_err() {
                        return;
                    }

                    // The test spins where a worker waits on its wake-up descriptor.
                    while !has_turn(view, slot).unwrap_or(false) {
                        std::hint::spin_loop();
                    }

                    let now_inside = inside.fetch_add(1, Ordering::SeqCst) + 1;
                    most_inside.fetch_max(now_inside, Ordering::SeqCst);
                    inside.fetch_sub(1, Ordering::SeqCst);

                    if view.queue_release(QUEUE, slot).is_err() {
                        return;
                    }

                    completed.fetch_add(1, Ordering::SeqCst);
                }
            });
        }
    });

    assert_eq!(most_inside.load(Ordering::SeqCst), 1);
    assert_eq!(completed.load(Ordering::SeqCst), u64::try_from(slot_count * rounds).unwrap_or(0));

    Ok(())
}
