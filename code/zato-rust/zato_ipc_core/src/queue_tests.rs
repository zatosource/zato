//! Unit tests of the writer queues.

use std::sync::atomic::{AtomicU64, Ordering};

use super::*;
use crate::layout::{CONFIG_PLACE, WORKER_PLACE};
use crate::view::test_support::{new_words, small_params};

/// Queue of the database file the tests write.
const QUEUE: usize = 1;

fn new_view() -> Result<RegionView<'static>, RegionError> {
    let (words, layout) = new_words(small_params())?;
    RegionView::new(words, layout)
}

/// Returns whether a place holds the turn of the test queue.
fn has_turn(view: &RegionView<'_>, place: usize) -> Result<bool, RegionError> {
    let (out, _) = view.queue_poll(QUEUE, place)?;
    Ok(out)
}

#[test]
fn places_are_served_in_order_of_entry() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, CONFIG_PLACE)?;
    view.queue_enter(QUEUE, WORKER_PLACE)?;

    assert!(has_turn(&view, CONFIG_PLACE)?);
    assert!(!has_turn(&view, WORKER_PLACE)?);

    assert_eq!(view.queue_release(QUEUE, CONFIG_PLACE)?, Some(WORKER_PLACE));
    assert!(has_turn(&view, WORKER_PLACE)?);

    assert_eq!(view.queue_release(QUEUE, WORKER_PLACE)?, None);

    Ok(())
}

#[test]
fn queues_of_two_files_are_independent() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(0, WORKER_PLACE)?;
    view.queue_enter(QUEUE, CONFIG_PLACE)?;

    assert!(has_turn(&view, CONFIG_PLACE)?);
    assert_eq!(view.queue_poll(0, WORKER_PLACE)?, (true, None));

    Ok(())
}

#[test]
fn abandoned_waiter_is_passed_over() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, WORKER_PLACE)?;
    view.queue_enter(QUEUE, CONFIG_PLACE)?;

    // The deadline of the waiter of the config process passes while the worker writes.
    assert_eq!(view.queue_abandon(QUEUE, CONFIG_PLACE)?, Some(WORKER_PLACE));
    assert!(!view.queue_has_place(QUEUE, CONFIG_PLACE)?);

    assert_eq!(view.queue_release(QUEUE, WORKER_PLACE)?, None);

    // The next entry of the config process is served at once.
    view.queue_enter(QUEUE, CONFIG_PLACE)?;
    assert!(has_turn(&view, CONFIG_PLACE)?);

    Ok(())
}

#[test]
fn terminated_holder_passes_its_turn() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, WORKER_PLACE)?;
    view.queue_enter(QUEUE, CONFIG_PLACE)?;

    // The worker terminates while it holds the turn, and the arbiter withdraws its ticket.
    assert_eq!(view.queue_abandon(QUEUE, WORKER_PLACE)?, Some(CONFIG_PLACE));
    assert!(has_turn(&view, CONFIG_PLACE)?);

    Ok(())
}

#[test]
fn process_terminated_after_taking_a_ticket_is_passed_over() -> Result<(), RegionError> {
    let view = new_view()?;
    let (next, _) = view.queue_head(QUEUE)?;

    // The worker marks its entry, takes the next ticket and terminates before it records it.
    view.queue_record(QUEUE, WORKER_PLACE)?.store(RECORD_ENTERING, Ordering::SeqCst);
    next.fetch_add(1, Ordering::SeqCst);

    view.queue_enter(QUEUE, CONFIG_PLACE)?;

    // While the worker is marked as entering, the queue cannot tell whose ticket is served first.
    assert!(!has_turn(&view, CONFIG_PLACE)?);

    // Once the arbiter marks the worker, the queue passes over its ticket.
    assert_eq!(view.queue_abandon(QUEUE, WORKER_PLACE)?, Some(CONFIG_PLACE));
    assert!(has_turn(&view, CONFIG_PLACE)?);

    Ok(())
}

#[test]
fn process_terminated_before_taking_a_ticket_changes_nothing() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, CONFIG_PLACE)?;
    view.queue_record(QUEUE, WORKER_PLACE)?.store(RECORD_ENTERING, Ordering::SeqCst);

    view.queue_abandon(QUEUE, WORKER_PLACE)?;

    assert!(has_turn(&view, CONFIG_PLACE)?);
    assert_eq!(view.queue_release(QUEUE, CONFIG_PLACE)?, None);

    Ok(())
}

#[test]
fn replacement_process_enters_the_same_place() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, CONFIG_PLACE)?;
    view.queue_enter(QUEUE, WORKER_PLACE)?;
    view.queue_abandon(QUEUE, WORKER_PLACE)?;

    // The replacement of the worker takes a new ticket in place of the withdrawn one.
    view.queue_enter(QUEUE, WORKER_PLACE)?;
    assert_eq!(view.queue_release(QUEUE, CONFIG_PLACE)?, Some(WORKER_PLACE));

    Ok(())
}

#[test]
fn second_ticket_and_foreign_release_are_refused() -> Result<(), RegionError> {
    let view = new_view()?;

    view.queue_enter(QUEUE, WORKER_PLACE)?;
    view.queue_enter(QUEUE, CONFIG_PLACE)?;

    assert_eq!(view.queue_enter(QUEUE, WORKER_PLACE), Err(RegionError::AlreadyQueued(WORKER_PLACE)));
    assert_eq!(view.queue_release(QUEUE, CONFIG_PLACE), Err(RegionError::NotHoldingTurn(CONFIG_PLACE)));

    // The queues of the keyed locks follow the writer queues, and no queue follows those
    let past_last = view.layout().queue_total;
    assert_eq!(view.queue_enter(past_last, WORKER_PLACE), Err(RegionError::NoSuchQueue(past_last)));

    // No place follows that of the config process
    let beyond = CONFIG_PLACE + 1;
    assert_eq!(view.queue_enter(QUEUE, beyond), Err(RegionError::NoSuchPlace(beyond)));

    Ok(())
}

#[test]
fn concurrent_writers_never_overlap() -> Result<(), RegionError> {
    let view = new_view()?;
    let places = [WORKER_PLACE, CONFIG_PLACE];
    let rounds = 2000;

    // Number of places inside the protected section, and the largest number ever seen there.
    let inside = AtomicU64::new(0);
    let most_inside = AtomicU64::new(0);
    let completed = AtomicU64::new(0);

    std::thread::scope(|scope| {
        for place in places {
            let view = &view;
            let inside = &inside;
            let most_inside = &most_inside;
            let completed = &completed;

            scope.spawn(move || {
                for _ in 0..rounds {
                    if view.queue_enter(QUEUE, place).is_err() {
                        return;
                    }

                    // The test spins where a process waits on its wake-up descriptor.
                    while !has_turn(view, place).unwrap_or(false) {
                        std::hint::spin_loop();
                    }

                    let now_inside = inside.fetch_add(1, Ordering::SeqCst) + 1;
                    most_inside.fetch_max(now_inside, Ordering::SeqCst);
                    inside.fetch_sub(1, Ordering::SeqCst);

                    if view.queue_release(QUEUE, place).is_err() {
                        return;
                    }

                    completed.fetch_add(1, Ordering::SeqCst);
                }
            });
        }
    });

    assert_eq!(most_inside.load(Ordering::SeqCst), 1);
    assert_eq!(completed.load(Ordering::SeqCst), u64::try_from(places.len() * rounds).unwrap_or(0));

    Ok(())
}
