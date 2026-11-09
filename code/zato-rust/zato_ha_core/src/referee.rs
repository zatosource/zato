// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee interface and the conditional transitions of the referee record.

use crate::record::{NodeAddress, RefereeRecord, Versioned};

/// The version a compare-and-set names when the record must not exist yet.
pub const VERSION_ABSENT: u64 = 0;

/// Errors of a referee operation whose outcome is unknown.
#[derive(Debug)]
pub struct RefereeError(pub String);

impl std::fmt::Display for RefereeError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "Referee error: {}", self.0)
    }
}

impl std::error::Error for RefereeError {}

/// A store of the referee record with compare-and-set writes.
pub trait Referee: Send + Sync {
    /// Returns the record and its version, or `None` if the record does not exist.
    fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError>;

    /// Writes the record only if its version is still `expected_version`, returning whether the write took place.
    /// [`VERSION_ABSENT`] creates the record only if it does not exist.
    fn compare_and_set(&self, record: &RefereeRecord, expected_version: u64) -> Result<bool, RefereeError>;

    /// Publishes the address of this node under its own key.
    fn publish_address(&self, address: &NodeAddress) -> Result<(), RefereeError>;

    /// Returns the addresses that all nodes published.
    fn read_addresses(&self) -> Result<Vec<NodeAddress>, RefereeError>;
}

/// The outcome of a conditional transition of the record.
#[derive(Debug)]
pub enum Transition {
    /// The record now holds the intended value.
    Applied,

    /// The condition does not hold for the current record, which is returned.
    Refused(Option<RefereeRecord>),

    /// The referee did not answer, so the outcome is unknown and the transition is attempted again.
    Unreachable(RefereeError),
}

/// Moves the record to `intended` if `condition` holds for the current record.
///
/// Every attempt begins with a read, and a record that already equals `intended` counts as applied,
/// so a write whose answer was lost is recognized on the next attempt and never applied twice.
pub fn transition(referee: &dyn Referee, intended: &RefereeRecord, condition: impl Fn(Option<&RefereeRecord>) -> bool) -> Transition {
    let current = match referee.read() {
        Ok(current) => current,
        Err(error) => return Transition::Unreachable(error),
    };

    let current_value = current.as_ref().map(|versioned| &versioned.value);

    // A lost answer to an earlier attempt, which did write the record.
    if current_value == Some(intended) {
        return Transition::Applied;
    }

    if !condition(current_value) {
        return Transition::Refused(current_value.cloned());
    }

    let expected_version = current.as_ref().map_or(VERSION_ABSENT, |versioned| versioned.version);

    match referee.compare_and_set(intended, expected_version) {
        Ok(true) => Transition::Applied,

        // Another writer changed the record between the read and the write, and the next read
        // tells whether that writer's record still allows this transition.
        Ok(false) => match referee.read() {
            Ok(Some(versioned)) if versioned.value == *intended => Transition::Applied,
            Ok(other) => Transition::Refused(other.map(|versioned| versioned.value)),
            Err(error) => Transition::Unreachable(error),
        },
        Err(error) => Transition::Unreachable(error),
    }
}

/// A referee kept in memory and the tests of the transitions.
#[cfg(test)]
pub mod tests {
    use super::*;
    use parking_lot::Mutex;

    /// A referee kept in memory, which can be made unreachable.
    #[derive(Default)]
    pub struct MemoryReferee {
        /// The record and its version.
        pub record: Mutex<Option<Versioned<RefereeRecord>>>,

        /// The published addresses.
        pub addresses: Mutex<Vec<NodeAddress>>,

        /// Whether every operation fails.
        pub unreachable: Mutex<bool>,

        /// Whether the next compare-and-set writes the record and then fails, as a lost answer does.
        pub lose_next_answer: Mutex<bool>,
    }

    impl Referee for MemoryReferee {
        fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError> {
            if *self.unreachable.lock() {
                return Err(RefereeError("unreachable".to_owned()));
            }
            Ok(self.record.lock().clone())
        }

        fn compare_and_set(&self, record: &RefereeRecord, expected_version: u64) -> Result<bool, RefereeError> {
            if *self.unreachable.lock() {
                return Err(RefereeError("unreachable".to_owned()));
            }
            let mut current = self.record.lock();
            let version = current.as_ref().map_or(VERSION_ABSENT, |versioned| versioned.version);
            if version != expected_version {
                return Ok(false);
            }
            *current = Some(Versioned {
                value: record.clone(),
                version: version + 1,
            });
            drop(current);
            let lose = std::mem::take(&mut *self.lose_next_answer.lock());
            if lose {
                return Err(RefereeError("answer lost".to_owned()));
            }
            Ok(true)
        }

        fn publish_address(&self, address: &NodeAddress) -> Result<(), RefereeError> {
            let mut addresses = self.addresses.lock();
            addresses.retain(|existing| existing.node_name != address.node_name);
            addresses.push(address.clone());
            drop(addresses);
            Ok(())
        }

        fn read_addresses(&self) -> Result<Vec<NodeAddress>, RefereeError> {
            Ok(self.addresses.lock().clone())
        }
    }

    #[test]
    fn creates_an_absent_record() {
        let referee = MemoryReferee::default();
        let intended = RefereeRecord::solo(1, "zato-a");
        let outcome = transition(&referee, &intended, |current| current.is_none());
        assert!(matches!(outcome, Transition::Applied));
        assert_eq!(referee.read().unwrap().unwrap().value, intended);
    }

    #[test]
    fn refuses_when_the_condition_fails() {
        let referee = MemoryReferee::default();
        let first = RefereeRecord::solo(1, "zato-a");
        assert!(matches!(
            transition(&referee, &first, |current| current.is_none()),
            Transition::Applied
        ));
        let second = RefereeRecord::solo(1, "zato-b");
        let outcome = transition(&referee, &second, |current| current.is_none());
        assert!(matches!(outcome, Transition::Refused(Some(record)) if record == first));
    }

    #[test]
    fn a_lost_answer_is_recognized() {
        let referee = MemoryReferee::default();
        *referee.lose_next_answer.lock() = true;
        let intended = RefereeRecord::solo(1, "zato-a");
        let first = transition(&referee, &intended, |current| current.is_none());
        assert!(matches!(first, Transition::Unreachable(_)));

        // The condition no longer holds, but the record is the intended one.
        let second = transition(&referee, &intended, |current| current.is_none());
        assert!(matches!(second, Transition::Applied));
    }
}
