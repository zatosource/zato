// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The referee record in a `coordination.k8s.io/v1` `Lease` of the namespace of the pods.
//!
//! The record is JSON in an annotation of the `Lease`, and its version is the `resourceVersion` of the `Lease`.
//! A creation is a `POST`, which the API server refuses for an existing object. A conditional write and a renewal
//! are JSON Patches that begin with a `test` of the `resourceVersion`, which the API server refuses for another
//! version and for a deleted object. A `PUT` is not used, because the API server creates a deleted `Lease` on a `PUT`
//! whatever its `resourceVersion`.

use std::collections::BTreeMap;

use chrono::{SecondsFormat, Utc};
use serde::{Deserialize, Serialize};

use super::client::{ApiClient, CONTENT_TYPE_JSON_PATCH, CONTENT_TYPE_MERGE_PATCH, Response};
use crate::record::{NodeAddress, RefereeRecord, Versioned};
use crate::referee::{Referee, RefereeError};
use crate::wire;

/// The API group and version of leases.
const LEASES_GROUP_VERSION: &str = "apis/coordination.k8s.io/v1";

/// The resource of leases.
const LEASES_RESOURCE: &str = "leases";

/// The API version of a `Lease` document.
const LEASE_API_VERSION: &str = "coordination.k8s.io/v1";

/// The kind of a `Lease` document.
const LEASE_KIND: &str = "Lease";

/// The annotation that holds the referee record.
const RECORD_ANNOTATION: &str = "zato.io/ha-record";

/// The annotation that holds the version a renewal was made from, which differs in every renewal.
const RENEWED_FROM_ANNOTATION: &str = "zato.io/ha-renewed-from";

/// The annotation that holds the address a node published.
const ADDRESS_ANNOTATION: &str = "zato.io/ha-address";

/// The label that ties the address leases to the lease of the record.
const LEASE_LABEL: &str = "zato.io/ha-lease";

/// The infix between the name of the lease of the record and the name of a node in the name of an address lease.
const NODE_INFIX: &str = "-node-";

/// The JSON Pointer of the version of an object.
const RESOURCE_VERSION_PATH: &str = "/metadata/resourceVersion";

/// The JSON Pointer of the record annotation, in which `~1` stands for `/`.
const RECORD_PATH: &str = "/metadata/annotations/zato.io~1ha-record";

/// The JSON Pointer of the annotation with the version a renewal was made from.
const RENEWED_FROM_PATH: &str = "/metadata/annotations/zato.io~1ha-renewed-from";

/// The JSON Pointer of the holder of a lease.
const HOLDER_PATH: &str = "/spec/holderIdentity";

/// The JSON Pointer of the time a lease was last renewed.
const RENEW_TIME_PATH: &str = "/spec/renewTime";

/// The JSON Patch operation that compares a value.
const OP_TEST: &str = "test";

/// The JSON Patch operation that adds or replaces a value.
const OP_ADD: &str = "add";

/// The status of a read or an update.
const STATUS_OK: u16 = 200;

/// The status of a creation.
const STATUS_CREATED: u16 = 201;

/// The status of an object that does not exist.
const STATUS_NOT_FOUND: u16 = 404;

/// The status of a creation of an object that exists.
const STATUS_CONFLICT: u16 = 409;

/// The status of a JSON Patch whose `test` failed.
const STATUS_UNPROCESSABLE: u16 = 422;

/// A `Lease` document that is created.
#[derive(Serialize)]
struct NewLease<'a> {
    /// The API version.
    #[serde(rename = "apiVersion")]
    api_version: &'static str,

    /// The kind.
    kind: &'static str,

    /// The metadata.
    metadata: NewMetadata<'a>,

    /// The specification.
    spec: Spec<'a>,
}

/// The metadata of a `Lease` that is created.
#[derive(Serialize)]
struct NewMetadata<'a> {
    /// The name.
    name: &'a str,

    /// The labels.
    #[serde(skip_serializing_if = "BTreeMap::is_empty")]
    labels: BTreeMap<&'static str, &'a str>,

    /// The annotations.
    annotations: BTreeMap<&'static str, &'a str>,
}

/// The specification of a `Lease`.
#[derive(Serialize)]
struct Spec<'a> {
    /// The node that holds the lease, which `kubectl get lease` shows.
    #[serde(rename = "holderIdentity")]
    holder_identity: &'a str,
}

/// A merge patch of the annotations of a `Lease`.
#[derive(Serialize)]
struct AnnotationsPatch<'a> {
    /// The metadata.
    metadata: AnnotationsMetadata<'a>,
}

/// The metadata of a merge patch of the annotations.
#[derive(Serialize)]
struct AnnotationsMetadata<'a> {
    /// The annotations.
    annotations: BTreeMap<&'static str, &'a str>,
}

/// A `Lease` that the API server returned.
#[derive(Deserialize)]
struct StoredLease {
    /// The metadata.
    metadata: StoredMetadata,
}

/// The metadata of a `Lease` that the API server returned.
#[derive(Deserialize)]
struct StoredMetadata {
    /// The name.
    name: String,

    /// The version.
    #[serde(rename = "resourceVersion")]
    resource_version: String,

    /// The annotations, which every lease of the referee has.
    annotations: BTreeMap<String, String>,
}

impl StoredMetadata {
    /// Returns the annotation `name`, which a lease of the referee must have.
    fn annotation(&self, name: &str) -> Result<&str, RefereeError> {
        self.annotations
            .get(name)
            .map(String::as_str)
            .ok_or_else(|| RefereeError(format!("Lease {} has no annotation {name}", self.name)))
    }
}

/// A list of leases that the API server returned.
#[derive(Deserialize)]
struct LeaseList {
    /// The leases.
    items: Vec<StoredLease>,
}

/// One operation of a JSON Patch.
#[derive(Serialize)]
struct Operation<'a> {
    /// The operation.
    op: &'static str,

    /// The JSON Pointer the operation applies to.
    path: &'static str,

    /// The value compared or written.
    value: &'a str,
}

/// The referee record in a `Lease`, with the addresses of the nodes in `Lease` objects labeled with its name.
pub struct LeaseReferee {
    /// The client of the API server.
    client: ApiClient,

    /// The name of the lease of the record.
    name: String,

    /// The URL of the leases of the namespace.
    leases_url: String,
}

impl LeaseReferee {
    /// Returns the referee over the lease `name` in the namespace of `client`.
    pub fn new(client: ApiClient, name: &str) -> Self {
        Self {
            leases_url: client.collection_url(LEASES_GROUP_VERSION, LEASES_RESOURCE),
            client,
            name: name.to_owned(),
        }
    }

    /// Returns the URL of the lease of the record.
    fn record_url(&self) -> String {
        format!("{}/{}", self.leases_url, self.name)
    }

    /// Sends a JSON Patch of the lease of the record.
    fn patch(&self, operations: &[Operation<'_>]) -> Result<Response, RefereeError> {
        let body = encode(operations)?;
        self.client
            .patch(&self.record_url(), CONTENT_TYPE_JSON_PATCH, &body)
            .map_err(RefereeError)
    }
}

/// Encodes a document of a request.
fn encode<T: Serialize + ?Sized>(value: &T) -> Result<Vec<u8>, RefereeError> {
    wire::encode(&value).map_err(|error| RefereeError(error.to_string()))
}

/// Encodes a value of an annotation.
fn encode_annotation<T: Serialize>(value: &T) -> Result<String, RefereeError> {
    let bytes = encode(value)?;
    String::from_utf8(bytes).map_err(|error| RefereeError(error.to_string()))
}

/// Parses a document of a response.
fn decode<T: serde::de::DeserializeOwned>(bytes: &[u8]) -> Result<T, RefereeError> {
    wire::decode(bytes).map_err(|error| RefereeError(error.to_string()))
}

/// Returns the error of a status that the operation does not expect.
fn unexpected(operation: &str, response: &Response) -> RefereeError {
    let body = String::from_utf8_lossy(&response.body);
    RefereeError(format!("{operation}: status {}: {body}", response.status))
}

impl Referee for LeaseReferee {
    fn read(&self) -> Result<Option<Versioned<RefereeRecord>>, RefereeError> {
        // A read without a resourceVersion parameter is served from etcd by quorum, never from the watch cache.
        let response = self.client.get(&self.record_url()).map_err(RefereeError)?;
        match response.status {
            STATUS_OK => {
                let lease: StoredLease = decode(&response.body)?;
                let value = decode(lease.metadata.annotation(RECORD_ANNOTATION)?.as_bytes())?;
                Ok(Some(Versioned {
                    value,
                    version: lease.metadata.resource_version,
                }))
            }
            STATUS_NOT_FOUND => Ok(None),
            _ => Err(unexpected("Read of the record", &response)),
        }
    }

    fn compare_and_set(&self, record: &RefereeRecord, expected_version: Option<&str>) -> Result<bool, RefereeError> {
        let encoded = encode_annotation(record)?;

        // A record that must not exist yet is created, which the API server refuses if the lease exists.
        let Some(expected_version) = expected_version else {
            let lease = NewLease {
                api_version: LEASE_API_VERSION,
                kind: LEASE_KIND,
                metadata: NewMetadata {
                    name: &self.name,
                    labels: BTreeMap::new(),
                    annotations: BTreeMap::from([(RECORD_ANNOTATION, encoded.as_str())]),
                },
                spec: Spec {
                    holder_identity: &record.active_node,
                },
            };
            let response = self.client.post(&self.leases_url, &encode(&lease)?).map_err(RefereeError)?;
            return match response.status {
                STATUS_CREATED => Ok(true),
                STATUS_CONFLICT => Ok(false),
                _ => Err(unexpected("Creation of the record", &response)),
            };
        };

        // The test of the version refuses the write at another version and on a deleted lease.
        let operations = [
            Operation {
                op: OP_TEST,
                path: RESOURCE_VERSION_PATH,
                value: expected_version,
            },
            Operation {
                op: OP_ADD,
                path: RECORD_PATH,
                value: &encoded,
            },
            Operation {
                op: OP_ADD,
                path: HOLDER_PATH,
                value: &record.active_node,
            },
        ];
        let response = self.patch(&operations)?;
        match response.status {
            STATUS_OK => Ok(true),
            STATUS_UNPROCESSABLE | STATUS_NOT_FOUND => Ok(false),
            _ => Err(unexpected("Write of the record", &response)),
        }
    }

    fn renew(&self, record: &RefereeRecord, expected_version: &str) -> Result<Option<String>, RefereeError> {
        let encoded = encode_annotation(record)?;
        let renew_time = Utc::now().to_rfc3339_opts(SecondsFormat::Micros, true);

        // The test of the record refuses a version that etcd issued again to another record after a restore,
        // and the version the renewal was made from differs in every renewal, so the API server always persists it.
        let operations = [
            Operation {
                op: OP_TEST,
                path: RESOURCE_VERSION_PATH,
                value: expected_version,
            },
            Operation {
                op: OP_TEST,
                path: RECORD_PATH,
                value: &encoded,
            },
            Operation {
                op: OP_ADD,
                path: RENEW_TIME_PATH,
                value: &renew_time,
            },
            Operation {
                op: OP_ADD,
                path: RENEWED_FROM_PATH,
                value: expected_version,
            },
        ];
        let response = self.patch(&operations)?;
        match response.status {
            STATUS_OK => {
                let lease: StoredLease = decode(&response.body)?;
                Ok(Some(lease.metadata.resource_version))
            }
            STATUS_UNPROCESSABLE | STATUS_NOT_FOUND => Ok(None),
            _ => Err(unexpected("Renewal of the record", &response)),
        }
    }

    fn publish_address(&self, address: &NodeAddress) -> Result<(), RefereeError> {
        let name = format!("{}{NODE_INFIX}{}", self.name, address.node_name);
        let encoded = encode_annotation(address)?;
        let lease = NewLease {
            api_version: LEASE_API_VERSION,
            kind: LEASE_KIND,
            metadata: NewMetadata {
                name: &name,
                labels: BTreeMap::from([(LEASE_LABEL, self.name.as_str())]),
                annotations: BTreeMap::from([(ADDRESS_ANNOTATION, encoded.as_str())]),
            },
            spec: Spec {
                holder_identity: &address.node_name,
            },
        };
        let response = self.client.post(&self.leases_url, &encode(&lease)?).map_err(RefereeError)?;
        match response.status {
            STATUS_CREATED => return Ok(()),
            STATUS_CONFLICT => {}
            _ => return Err(unexpected("Creation of the address", &response)),
        }

        // A node started again replaces the address it published earlier, which no other node writes.
        let patch = AnnotationsPatch {
            metadata: AnnotationsMetadata {
                annotations: BTreeMap::from([(ADDRESS_ANNOTATION, encoded.as_str())]),
            },
        };
        let url = format!("{}/{name}", self.leases_url);
        let response = self
            .client
            .patch(&url, CONTENT_TYPE_MERGE_PATCH, &encode(&patch)?)
            .map_err(RefereeError)?;
        match response.status {
            STATUS_OK => Ok(()),
            _ => Err(unexpected("Update of the address", &response)),
        }
    }

    fn read_addresses(&self) -> Result<Vec<NodeAddress>, RefereeError> {
        // The label selector is percent-encoded, in which %2F stands for / and %3D for =.
        let label = LEASE_LABEL.replace('/', "%2F");
        let url = format!("{}?labelSelector={label}%3D{}", self.leases_url, self.name);
        let response = self.client.get(&url).map_err(RefereeError)?;
        if response.status != STATUS_OK {
            return Err(unexpected("Read of the addresses", &response));
        }
        let list: LeaseList = decode(&response.body)?;
        list.items
            .iter()
            .map(|lease| decode(lease.metadata.annotation(ADDRESS_ANNOTATION)?.as_bytes()))
            .collect()
    }
}

#[cfg(test)]
mod tests;
