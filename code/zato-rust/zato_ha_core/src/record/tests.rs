// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the encoding of the referee record.

use super::*;
use crate::test_support::NODE_A;
use crate::wire;

/// The generation of the record of the tests.
const GENERATION: u64 = 3;

/// The encoding of the record of the tests by a node without releases.
const ENCODED_WITHOUT_RELEASES: &str = r#"{"generation":3,"active_node":"zato-a"}"#;

#[test]
fn an_unreleased_record_is_encoded_as_by_a_node_without_releases() {
    let encoded = wire::encode(&RefereeRecord::new(GENERATION, NODE_A)).unwrap();
    assert_eq!(String::from_utf8(encoded).unwrap(), ENCODED_WITHOUT_RELEASES);
}

#[test]
fn a_record_without_the_field_is_not_released() {
    let record: RefereeRecord = wire::decode(ENCODED_WITHOUT_RELEASES.as_bytes()).unwrap();
    assert_eq!(record, RefereeRecord::new(GENERATION, NODE_A));
    assert!(!record.released);
}

#[test]
fn a_released_record_is_encoded_and_decoded_as_released() {
    let released = RefereeRecord::new(GENERATION, NODE_A).released_by();
    assert!(released.released);
    assert_eq!(released.generation, GENERATION);
    assert_eq!(released.active_node, NODE_A);

    let encoded = wire::encode(&released).unwrap();
    let decoded: RefereeRecord = wire::decode(&encoded).unwrap();
    assert_eq!(decoded, released);
}
