// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee interface and the conditional transitions of the referee record.
//!
//! Every referee type implements [`Referee`], so the control logic does not depend on the store of the record.

use crate::record::{NodeAddress, RefereeRecord, Versioned};

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
    /// `None` creates the record only if it does not exist.
    fn compare_and_set(&self, record: &RefereeRecord, expected_version: Option<&str>) -> Result<bool, RefereeError>;

    /// Rewrites `record` unchanged, which raises its version, only if the version is still `expected_version`
    /// and the record still equals `record`, returning the new version, or `None` if either condition fails.
    ///
    /// A record that another node created again at the same version after the referee lost data
    /// differs from `record`, so the lease of the node that it does not name is not renewed.
    fn renew(&self, record: &RefereeRecord, expected_version: &str) -> Result<Option<String>, RefereeError>;

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
    loop {
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

        let expected_version = current.as_ref().map(|versioned| versioned.version.as_str());

        match referee.compare_and_set(intended, expected_version) {
            Ok(true) => return Transition::Applied,

            // Another writer changed the record or only renewed it between the read and the write,
            // and the next attempt tells whether the condition still holds for what that writer left.
            Ok(false) => {}
            Err(error) => return Transition::Unreachable(error),
        }
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

        /// The record that another writer renews before the next compare-and-set, raising its version.
        pub renew_before_next_write: Mutex<bool>,

        /// The last version issued, from which every next version is issued.
        pub last_version: Mutex<u64>,
    }

    /// Returns the version that a test names, which is opaque to the code under test.
    pub fn version(number: u64) -> String {
        number.to_string()
    }

    impl MemoryReferee {
        /// Returns a referee that holds `record` at the version `number`.
        pub fn holding(record: Option<RefereeRecord>, number: u64) -> Self {
            let out = Self::default();
            *out.record.lock() = record.map(|value| Versioned {
                value,
                version: version(number),
            });
            *out.last_version.lock() = number;
            out
        }

        /// Issues the next version.
        fn next_version(&self) -> String {
            let mut last = self.last_version.lock();
            *last += 1;
            version(*last)
        }

        /// Writes the record if its version is the expected one, and returns whether it was written.
        fn store(&self, record: &RefereeRecord, expected_version: Option<&str>) -> bool {
            let mut current = self.record.lock();
            let version = current.as_ref().map(|versioned| versioned.version.as_str());
            if version != expected_version {
                return false;
            }
            *current = Some(Versioned {
                value: record.clone(),
                version: self.next_version(),
            });
            true
        }

        /// Raises the version of the record if it is the expected record at the expected version, and returns
        /// the raised version.
        fn raise_version(&self, record: &RefereeRecord, expected_version: &str) -> Option<String> {
            let mut current = self.record.lock();
            let versioned = current.as_mut()?;
            if versioned.version != expected_version || versioned.value != *record {
                return None;
            }
            versioned.version = self.next_version();
            let out = versioned.version.clone();
            drop(current);
            Some(out)
        }

        /// Renews the record as its holder does, if a test asked for it before this write.
        fn renew_if_requested(&self) {
            let requested = std::mem::take(&mut *self.renew_before_next_write.lock());
            if !requested {
                return;
            }
            let mut current = self.record.lock();
            if let Some(versioned) = current.as_mut() {
                versioned.version = self.next_version();
            }
        }
    }

    impl Referee for MemoryReferee {
        fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError> {
            if *self.unreachable.lock() {
                return Err(RefereeError("unreachable".to_owned()));
            }
            Ok(self.record.lock().clone())
        }

        fn compare_and_set(&self, record: &RefereeRecord, expected_version: Option<&str>) -> Result<bool, RefereeError> {
            if *self.unreachable.lock() {
                return Err(RefereeError("unreachable".to_owned()));
            }
            self.renew_if_requested();
            let applied = self.store(record, expected_version);

            // The record is written before the answer is lost, as it is when a network drops a response.
            let lose = std::mem::take(&mut *self.lose_next_answer.lock());
            if lose {
                return Err(RefereeError("answer lost".to_owned()));
            }
            Ok(applied)
        }

        fn renew(&self, record: &RefereeRecord, expected_version: &str) -> Result<Option<String>, RefereeError> {
            if *self.unreachable.lock() {
                return Err(RefereeError("unreachable".to_owned()));
            }
            let renewed = self.raise_version(record, expected_version);

            // The version is raised before the answer is lost, as it is when a network drops a response.
            let lose = std::mem::take(&mut *self.lose_next_answer.lock());
            if lose {
                return Err(RefereeError("answer lost".to_owned()));
            }
            Ok(renewed)
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

    #[test]
    fn a_renewal_between_the_read_and_the_write_does_not_refuse_the_transition() {
        let current = RefereeRecord::replicated(3, "zato-a", "zato-b");
        let referee = MemoryReferee::holding(Some(current.clone()), 1);
        *referee.renew_before_next_write.lock() = true;
        let intended = RefereeRecord::solo(4, "zato-a");
        let outcome = transition(&referee, &intended, |record| record == Some(&current));
        assert!(matches!(outcome, Transition::Applied));
        assert_eq!(referee.read().unwrap().unwrap().value, intended);
    }

    #[test]
    fn a_write_between_the_read_and_the_write_refuses_a_transition_it_no_longer_allows() {
        let current = RefereeRecord::replicated(3, "zato-a", "zato-b");
        let referee = MemoryReferee::holding(Some(current.clone()), 1);
        let intended = RefereeRecord::solo(4, "zato-a");
        let other = RefereeRecord::solo(4, "zato-b");
        let outcome = transition(&referee, &intended, |record| {
            // The other node writes its own record after this read, before this node's compare-and-set.
            if record == Some(&current) {
                *referee.record.lock() = Some(Versioned {
                    value: other.clone(),
                    version: version(2),
                });
            }
            record == Some(&current)
        });
        assert!(matches!(outcome, Transition::Refused(Some(record)) if record == other));
    }
}
