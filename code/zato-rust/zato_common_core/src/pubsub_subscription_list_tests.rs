//! The subscription list of a worker.
//!
//! The tests cover the status of each pair, the changes of one subscriber, the topics that fetches withhold,
//! the permissions of publishers, the decisions of publications and the readers that run while the whole list is replaced.

use std::collections::BTreeMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;

use parking_lot::RwLock;

use super::{ListState, Pair, PairFlags, Status, Subscriber, is_governed_key};

/// Governed sub keys in the format of `new_sub_key`.
const SUB_KEY_ORDERS: &str = "sk0192d3a1b2c3d4e5f60718293a4b5c6d";
const SUB_KEY_INVOICES: &str = "sk0192d3a1b2c3d4e5f60718293a4b5c6e";

/// Sub keys of the mechanisms that own their own rows.
const SUB_KEY_SERVICE_TOPIC: &str = "zpsk.srv.billing.invoice-sync";
const SUB_KEY_OUTGOING_QUEUE: &str = "zpsk.out.crm";

/// Topic names.
const TOPIC_ORDERS: &str = "/customers/orders";
const TOPIC_INVOICES: &str = "/customers/invoices";
const TOPIC_RENAMED: &str = "/customers/orders-v2";

/// How many times the writer of the concurrency test replaces the list, and how many threads read it meanwhile.
const REPLACEMENT_COUNT: usize = 2_000;
const READER_COUNT: usize = 4;

/// The flags of a pair whose publishing and delivery are both switched on.
const FLAGS_ON: PairFlags = PairFlags {
    is_pub_enabled: true,
    is_delivery_enabled: true,
};

/// Returns a pair of a sub key and a topic.
fn pair(sub_key: &str, topic: &str) -> Pair {
    (sub_key.to_owned(), topic.to_owned())
}

/// Returns a subscriber that may publish, with the given flags on each of its topics.
fn subscriber(topics: &[(&str, PairFlags)]) -> Subscriber {
    let topics: BTreeMap<String, PairFlags> = topics.iter().map(|(topic, flags)| ((*topic).to_owned(), *flags)).collect();
    Subscriber {
        is_pub_active: true,
        topics,
    }
}

/// Returns a state with the orders subscriber on both topics and the invoices subscriber on the invoices topic,
/// with the rows of the given pairs committed.
fn state_with(committed: &[Pair]) -> ListState {
    let subscribers = vec![
        (
            SUB_KEY_ORDERS.to_owned(),
            subscriber(&[(TOPIC_ORDERS, FLAGS_ON), (TOPIC_INVOICES, FLAGS_ON)]),
        ),
        (SUB_KEY_INVOICES.to_owned(), subscriber(&[(TOPIC_INVOICES, FLAGS_ON)])),
    ];
    ListState::from_parts(subscribers, committed.to_vec())
}

#[test]
fn recognizes_governed_sub_keys() {
    assert!(is_governed_key(SUB_KEY_ORDERS));
    assert!(!is_governed_key(SUB_KEY_SERVICE_TOPIC));
    assert!(!is_governed_key(SUB_KEY_OUTGOING_QUEUE));
    assert!(!is_governed_key("sk0192D3A1B2C3D4E5F60718293A4B5C6D"));
    assert!(!is_governed_key("sk0192d3a1b2c3d4e5f60718293a4b5c6"));
    assert!(!is_governed_key("sk0192d3a1b2c3d4e5f60718293a4b5c6dd"));
}

#[test]
fn leaves_out_sub_keys_of_other_mechanisms() {
    let subscribers = vec![
        (SUB_KEY_ORDERS.to_owned(), subscriber(&[(TOPIC_ORDERS, FLAGS_ON)])),
        (SUB_KEY_SERVICE_TOPIC.to_owned(), subscriber(&[(TOPIC_ORDERS, FLAGS_ON)])),
    ];
    let committed = vec![pair(SUB_KEY_OUTGOING_QUEUE, TOPIC_ORDERS)];
    let state = ListState::from_parts(subscribers, committed);

    assert_eq!(state.pairs_for_topic(TOPIC_ORDERS), vec![SUB_KEY_ORDERS.to_owned()]);
    assert!(state.removed_topics(SUB_KEY_OUTGOING_QUEUE).is_empty());
    assert_eq!(state.statuses().len(), 1);
}

#[test]
fn derives_the_status_of_each_pair() {
    let committed = vec![pair(SUB_KEY_ORDERS, TOPIC_ORDERS), pair(SUB_KEY_INVOICES, TOPIC_ORDERS)];
    let state = state_with(&committed);

    let statuses: Vec<(String, String, Status)> = state
        .statuses()
        .into_iter()
        .map(|pair_status| (pair_status.sub_key, pair_status.topic, pair_status.status))
        .collect();

    assert_eq!(
        statuses,
        vec![
            (SUB_KEY_ORDERS.to_owned(), TOPIC_INVOICES.to_owned(), Status::Pending),
            (SUB_KEY_ORDERS.to_owned(), TOPIC_ORDERS.to_owned(), Status::Confirmed),
            (SUB_KEY_INVOICES.to_owned(), TOPIC_INVOICES.to_owned(), Status::Pending),
            (SUB_KEY_INVOICES.to_owned(), TOPIC_ORDERS.to_owned(), Status::PendingRemoval),
        ]
    );

    let (pending, removals) = state.differences();
    assert_eq!(
        pending,
        vec![pair(SUB_KEY_ORDERS, TOPIC_INVOICES), pair(SUB_KEY_INVOICES, TOPIC_INVOICES)]
    );
    assert_eq!(removals, vec![pair(SUB_KEY_INVOICES, TOPIC_ORDERS)]);
    assert!(state.has_unconfirmed());
}

#[test]
fn set_topics_returns_the_previous_topics_and_updates_the_index() {
    let mut state = state_with(&[]);

    let previous = state.set_topics(SUB_KEY_ORDERS, subscriber(&[(TOPIC_INVOICES, FLAGS_ON)]));

    assert_eq!(previous, vec![TOPIC_INVOICES.to_owned(), TOPIC_ORDERS.to_owned()]);
    assert!(state.pairs_for_topic(TOPIC_ORDERS).is_empty());
    assert_eq!(
        state.pairs_for_topic(TOPIC_INVOICES),
        vec![SUB_KEY_ORDERS.to_owned(), SUB_KEY_INVOICES.to_owned()]
    );
    assert_eq!(state.topics_of(SUB_KEY_ORDERS), vec![TOPIC_INVOICES.to_owned()]);
}

#[test]
fn remove_returns_the_topics_and_leaves_their_rows_pending_removal() {
    let committed = vec![pair(SUB_KEY_INVOICES, TOPIC_INVOICES)];
    let mut state = state_with(&committed);

    let previous = state.remove(SUB_KEY_INVOICES);

    assert_eq!(previous, vec![TOPIC_INVOICES.to_owned()]);
    assert_eq!(state.pairs_for_topic(TOPIC_INVOICES), vec![SUB_KEY_ORDERS.to_owned()]);
    assert_eq!(state.removed_topics(SUB_KEY_INVOICES), vec![TOPIC_INVOICES.to_owned()]);
    assert!(state.remove(SUB_KEY_INVOICES).is_empty());
}

#[test]
fn mark_committed_confirms_additions_and_clears_removals() {
    let committed = vec![pair(SUB_KEY_INVOICES, TOPIC_ORDERS)];
    let mut state = state_with(&committed);

    let added = vec![
        pair(SUB_KEY_ORDERS, TOPIC_ORDERS),
        pair(SUB_KEY_ORDERS, TOPIC_INVOICES),
        pair(SUB_KEY_INVOICES, TOPIC_INVOICES),
        pair(SUB_KEY_SERVICE_TOPIC, TOPIC_ORDERS),
    ];
    let removed = vec![pair(SUB_KEY_INVOICES, TOPIC_ORDERS)];
    state.mark_committed(added, removed);

    assert!(!state.has_unconfirmed());
    assert!(state.statuses().iter().all(|pair_status| pair_status.status == Status::Confirmed));
    assert_eq!(state.statuses().len(), 3);
}

#[test]
fn replace_committed_takes_the_rows_read_from_the_database() {
    let committed = vec![pair(SUB_KEY_ORDERS, TOPIC_ORDERS)];
    let mut state = state_with(&committed);

    state.replace_committed(vec![pair(SUB_KEY_INVOICES, TOPIC_INVOICES)]);

    let (pending, removals) = state.differences();
    assert_eq!(
        pending,
        vec![pair(SUB_KEY_ORDERS, TOPIC_INVOICES), pair(SUB_KEY_ORDERS, TOPIC_ORDERS)]
    );
    assert!(removals.is_empty());
}

#[test]
fn withholds_topics_pending_removal_and_topics_without_delivery() {
    let no_delivery = PairFlags {
        is_pub_enabled: true,
        is_delivery_enabled: false,
    };
    let subscribers = vec![(
        SUB_KEY_ORDERS.to_owned(),
        subscriber(&[(TOPIC_ORDERS, FLAGS_ON), (TOPIC_INVOICES, no_delivery)]),
    )];
    let committed = vec![pair(SUB_KEY_ORDERS, TOPIC_RENAMED)];
    let state = ListState::from_parts(subscribers, committed);

    assert_eq!(state.removed_topics(SUB_KEY_ORDERS), vec![TOPIC_RENAMED.to_owned()]);
    assert_eq!(state.delivered_topics(SUB_KEY_ORDERS), Some(vec![TOPIC_ORDERS.to_owned()]));
    assert_eq!(state.delivered_topics(SUB_KEY_INVOICES), Some(Vec::new()));
    assert_eq!(state.delivered_topics(SUB_KEY_SERVICE_TOPIC), None);
    assert_eq!(ListState::default().delivered_topics(SUB_KEY_ORDERS), None);

    assert!(state.withholds_pair(SUB_KEY_ORDERS, TOPIC_RENAMED));
    assert!(!state.withholds_pair(SUB_KEY_ORDERS, TOPIC_INVOICES));
    assert!(state.withholds_pair(SUB_KEY_INVOICES, TOPIC_INVOICES));
    assert!(!state.withholds_pair(SUB_KEY_SERVICE_TOPIC, TOPIC_ORDERS));
    assert!(!ListState::default().withholds_pair(SUB_KEY_ORDERS, TOPIC_ORDERS));
}

#[test]
fn publishing_follows_the_flags_of_the_subscription_and_of_each_pair() {
    let no_publishing = PairFlags {
        is_pub_enabled: false,
        is_delivery_enabled: true,
    };
    let mut inactive = subscriber(&[(TOPIC_ORDERS, FLAGS_ON)]);
    inactive.is_pub_active = false;

    let subscribers = vec![
        (
            SUB_KEY_ORDERS.to_owned(),
            subscriber(&[(TOPIC_ORDERS, FLAGS_ON), (TOPIC_INVOICES, no_publishing)]),
        ),
        (SUB_KEY_INVOICES.to_owned(), inactive),
    ];
    let state = ListState::from_parts(subscribers, Vec::new());

    assert!(state.is_publish_allowed(SUB_KEY_ORDERS, TOPIC_ORDERS));
    assert!(!state.is_publish_allowed(SUB_KEY_ORDERS, TOPIC_INVOICES));
    assert!(state.is_publish_allowed(SUB_KEY_ORDERS, TOPIC_RENAMED));
    assert!(!state.is_publish_allowed(SUB_KEY_INVOICES, TOPIC_ORDERS));
    assert!(!state.is_publish_allowed(SUB_KEY_INVOICES, TOPIC_RENAMED));
    assert!(state.is_publish_allowed(SUB_KEY_SERVICE_TOPIC, TOPIC_ORDERS));
}

#[test]
fn rename_topic_moves_configured_pairs_and_committed_rows() {
    let committed = vec![pair(SUB_KEY_ORDERS, TOPIC_ORDERS)];
    let mut state = state_with(&committed);

    state.rename_topic(TOPIC_ORDERS, TOPIC_RENAMED);

    assert!(state.pairs_for_topic(TOPIC_ORDERS).is_empty());
    assert_eq!(state.pairs_for_topic(TOPIC_RENAMED), vec![SUB_KEY_ORDERS.to_owned()]);
    assert_eq!(
        state.topics_of(SUB_KEY_ORDERS),
        vec![TOPIC_INVOICES.to_owned(), TOPIC_RENAMED.to_owned()]
    );
    assert!(state.removed_topics(SUB_KEY_ORDERS).is_empty());

    let confirmed = state
        .statuses()
        .into_iter()
        .any(|pair_status| pair_status.topic == TOPIC_RENAMED && pair_status.status == Status::Confirmed);
    assert!(confirmed);
}

#[test]
fn publications_decide_from_the_rows_until_the_list_is_built() {
    let state = ListState::default();
    let rows = vec![SUB_KEY_ORDERS.to_owned(), SUB_KEY_SERVICE_TOPIC.to_owned()];

    let decision = state.decide_subscribers(TOPIC_ORDERS, rows.clone());

    assert_eq!(decision.subscribers, rows);
    assert!(decision.added.is_empty());
}

#[test]
fn publications_add_pending_pairs_and_skip_removals() {
    let state = state_with(&[]);
    let rows = vec![SUB_KEY_INVOICES.to_owned(), SUB_KEY_SERVICE_TOPIC.to_owned()];

    let orders = state.decide_subscribers(TOPIC_ORDERS, rows.clone());
    assert_eq!(
        orders.subscribers,
        vec![SUB_KEY_SERVICE_TOPIC.to_owned(), SUB_KEY_ORDERS.to_owned()]
    );
    assert_eq!(orders.added, vec![pair(SUB_KEY_ORDERS, TOPIC_ORDERS)]);

    let invoices = state.decide_subscribers(TOPIC_INVOICES, rows.clone());
    assert_eq!(
        invoices.subscribers,
        vec![
            SUB_KEY_INVOICES.to_owned(),
            SUB_KEY_SERVICE_TOPIC.to_owned(),
            SUB_KEY_ORDERS.to_owned()
        ]
    );
    assert_eq!(invoices.added, vec![pair(SUB_KEY_ORDERS, TOPIC_INVOICES)]);

    let renamed = state.decide_subscribers(TOPIC_RENAMED, rows);
    assert_eq!(renamed.subscribers, vec![SUB_KEY_SERVICE_TOPIC.to_owned()]);
    assert!(renamed.added.is_empty());
}

#[test]
fn readers_see_the_whole_list_before_or_after_a_replacement() {
    let before = state_with(&[]);
    let mut after = state_with(&[]);
    after.remove(SUB_KEY_ORDERS);
    after.set_topics(
        SUB_KEY_INVOICES,
        subscriber(&[(TOPIC_ORDERS, FLAGS_ON), (TOPIC_INVOICES, FLAGS_ON)]),
    );

    let snapshot = |state: &ListState| (state.pairs_for_topic(TOPIC_ORDERS), state.pairs_for_topic(TOPIC_INVOICES));
    let expected_before = snapshot(&before);
    let expected_after = snapshot(&after);

    let shared = Arc::new(RwLock::new(before.clone()));
    let is_done = Arc::new(AtomicBool::new(false));
    let mut readers = Vec::with_capacity(READER_COUNT);

    for _ in 0..READER_COUNT {
        let shared = Arc::clone(&shared);
        let is_done = Arc::clone(&is_done);
        let expected_before = expected_before.clone();
        let expected_after = expected_after.clone();

        readers.push(thread::spawn(move || {
            let mut reads = 0_usize;
            while !is_done.load(Ordering::Acquire) {
                // Both topics are read under one guard, as a publication reads every topic of its batch
                let seen = snapshot(&shared.read());
                assert!(
                    seen == expected_before || seen == expected_after,
                    "partial state observed: {seen:?}"
                );
                reads = reads.saturating_add(1);
            }
            reads
        }));
    }

    for index in 0..REPLACEMENT_COUNT {
        let next = if index % 2 == 0 { after.clone() } else { before.clone() };
        *shared.write() = next;
    }
    is_done.store(true, Ordering::Release);

    for reader in readers {
        let reads = reader.join();
        assert!(reads.is_ok(), "a reader observed a partial state");
    }
}
