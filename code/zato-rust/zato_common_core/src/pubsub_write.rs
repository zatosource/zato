//! The pub/sub transaction of a batch on `SQLite`.
//!
//! The values of the items are copied from Python, the statements run with the GIL released through the handle
//! of the driver's connection, and what became of each item is stored on it afterwards.

use pyo3::exceptions::PyRuntimeError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyBytes, PyDict, PyFloat, PyList, PyString, PyTuple};
use rusqlite::types::Value;

use crate::audit_insert::{bound_value, check_library_version, open_handle, sqlite_py_err};
use crate::pubsub_subscription_list::{Pair, SubscriptionList};
use crate::pubsub_write_sql::{
    AckInput, AckResult, AtomicInput, AtomicResult, BatchContext, BatchError, BatchInput, BatchResults, DedupKey, FencedEntry, ItemError,
    Layout, LeaseInput, LeaseResult, PublicationInput, PublicationResult, Statements, write_batch,
};

/// The module of the `SQLite` driver of Python.
const SQLITE_MODULE: &str = "sqlite3";

// ################################################################################################################################
// ################################################################################################################################

/// Writes the items of a batch of pub/sub into `SQLite` in the transaction of the connection of the Python driver.
///
/// The publications, acknowledgements, fenced acknowledgements, push attempts and pulls are written,
/// and the payloads that no subscriber needs anymore are dropped, all with the GIL released.
#[pyclass(frozen, name = "SQLitePubSubWriter")]
pub struct SqlitePubSubWriter {
    /// The statements of the transaction.
    statements: Statements,

    /// The positions of the columns that the transaction reads or changes.
    layout: Layout,

    /// The keys of the values of a message that the insert of a message binds, in the order of its parameters.
    message_columns: Vec<Py<PyString>>,

    /// The class `sqlite3.Connection`, whose instances alone hold the handle that the items are written through.
    connection_type: Py<PyAny>,

    /// The exception of a publication whose identifier belongs to a different message.
    duplicate_error: Py<PyAny>,

    /// The exception of a fenced acknowledgement whose messages were handed out again or concluded.
    conflict_error: Py<PyAny>,

    /// The class of the row of a leased message, whose values are read by position and by the name of their column.
    lease_row_class: Py<PyAny>,
}

#[pymethods]
impl SqlitePubSubWriter {
    /// Builds the writer from the statements and the columns that Python derived from the metadata of the tables.
    #[new]
    fn new(py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let config = config.as_any();

        // The handle is shared with the Python driver, so both must use the same SQLite library
        let python_version: String = config.get_item("sqlite_version")?.extract()?;
        check_library_version(&python_version, rusqlite::version()).map_err(PyRuntimeError::new_err)?;

        let statements = config.get_item("statements")?;
        let statement = |key: &str| -> PyResult<String> { statements.get_item(key)?.extract() };

        let statements = Statements {
            begin: statement("begin")?,
            select_subscribers: statement("select_subscribers")?,
            insert_topic_sub: statement("insert_topic_sub")?,
            upsert_dedup_record: statement("upsert_dedup_record")?,
            select_dedup_record: statement("select_dedup_record")?,
            update_dedup_fingerprint: statement("update_dedup_fingerprint")?,
            dedup_key: DedupKey {
                kind: config.get_item("dedup_kind")?.extract()?,
                scope: config.get_item("dedup_scope")?.extract()?,
            },
            insert_message: statement("insert_message")?,
            select_existing_message: statement("select_existing_message")?,
            insert_delivery: statement("insert_delivery")?,
            select_message_id: statement("select_message_id")?,
            select_ack_delivery: statement("select_ack_delivery")?,
            delete_delivery: statement("delete_delivery")?,
            record_attempt: statement("record_attempt")?,
            select_lease_candidates: statement("select_lease_candidates")?,
            lease_delivery: statement("lease_delivery")?,
            select_leased_message: statement("select_leased_message")?,
            select_fenced_delivery: statement("select_fenced_delivery")?,
            drop_payload: statement("drop_payload")?,
        };

        let message_columns: Vec<Bound<'_, PyString>> = config.get_item("message_columns")?.extract()?;
        let lease_columns: Vec<String> = config.get_item("lease_columns")?.extract()?;

        let mut message_names = Vec::with_capacity(message_columns.len());
        for name in &message_columns {
            message_names.push(name.to_str()?.to_owned());
        }

        let payload_column: String = config.get_item("payload_column")?.extract()?;
        let payload_encrypted_column: String = config.get_item("payload_encrypted_column")?.extract()?;
        let id_column: String = config.get_item("id_column")?.extract()?;
        let priority_column: String = config.get_item("priority_column")?.extract()?;

        let layout = Layout {
            payload_index: column_index(&message_names, &payload_column)?,
            payload_encrypted_index: column_index(&message_names, &payload_encrypted_column)?,
            lease_column_count: lease_columns.len(),
            lease_id_index: column_index(&lease_columns, &id_column)?,
            lease_priority_index: column_index(&lease_columns, &priority_column)?,
            lease_payload_encrypted_index: column_index(&lease_columns, &payload_encrypted_column)?,
        };

        let mut columns = Vec::with_capacity(message_columns.len());
        for name in message_columns {
            columns.push(name.unbind());
        }

        Ok(Self {
            statements,
            layout,
            message_columns: columns,
            connection_type: py.import(SQLITE_MODULE)?.getattr("Connection")?.unbind(),
            duplicate_error: config.get_item("duplicate_error")?.unbind(),
            conflict_error: config.get_item("conflict_error")?.unbind(),
            lease_row_class: config.get_item("lease_row_class")?.unbind(),
        })
    }

    /// Writes the items of a batch, given by kind, in the transaction of the connection and stores on each item
    /// what became of it. Returns the identifier of each repeated publication, with the name of how it repeats an earlier one,
    /// and the subscriber and topic pairs whose rows the publications inserted.
    fn write_items(
        &self,
        py: Python<'_>,
        connection: &Bound<'_, PyAny>,
        items: &Bound<'_, PyDict>,
        subscription_list: &Bound<'_, SubscriptionList>,
    ) -> PyResult<(Vec<(String, &'static str)>, Vec<Pair>)> {
        let items = items.as_any();
        let publications = items.get_item("publications")?.cast_into::<PyList>()?;
        let acks = items.get_item("acks")?.cast_into::<PyList>()?;
        let atomics = items.get_item("atomics")?.cast_into::<PyList>()?;
        let attempts = items.get_item("attempts")?.cast_into::<PyList>()?;
        let leases = items.get_item("leases")?.cast_into::<PyList>()?;

        let batch = BatchInput {
            publications: self.extract_publications(&publications)?,
            acks: extract_list(&acks, extract_ack)?,
            atomics: self.extract_atomics(&atomics)?,
            attempts: extract_list(&attempts, |pending| pending.getattr(intern!(py, "delivery_ids"))?.extract())?,
            leases: extract_list(&leases, extract_lease)?,
        };

        let sqlite = open_handle(connection, self.connection_type.bind(py))?;
        let shared_list = subscription_list.get().shared();
        let mut results = BatchResults::for_batch(&batch);
        let batch_ref = &batch;
        let results_ref = &mut results;
        let statements = &self.statements;
        let layout = &self.layout;
        let list_ref = &shared_list;

        // Everything from here on is written without the GIL, so the other threads of the interpreter run in the meantime
        let written = py.detach(move || {
            let context = BatchContext {
                sqlite: &sqlite,
                statements,
                layout,
                subscription_list: list_ref,
            };
            write_batch(&context, batch_ref, results_ref)
        });

        // A batch that SQLite refused is rolled back as a whole, so nothing of it is stored on the items
        if let Err(BatchError::Sqlite(error)) = written {
            return Err(sqlite_py_err(py, error));
        }

        let mut out = Vec::new();

        for (pending, result) in publications.iter().zip(results.publications) {
            self.apply_publication(&pending, result, &mut out)?;
        }

        for (pending, result) in acks.iter().zip(results.acks) {
            apply_ack(&pending, result)?;
        }

        for (pending, result) in atomics.iter().zip(results.atomics) {
            self.apply_atomic(&pending, result, &mut out)?;
        }

        for (pending, result) in attempts.iter().zip(results.attempts) {
            let attempts = pending.getattr(intern!(py, "attempts"))?.cast_into::<PyDict>()?;
            for (delivery_id, attempt) in result {
                attempts.set_item(delivery_id, attempt)?;
            }
        }

        for (pending, result) in leases.iter().zip(results.leases) {
            self.apply_lease(&pending, result)?;
        }

        // A strict fenced acknowledgement with a publication that belongs to a different message fails the whole batch
        if let Err(BatchError::StrictDuplicate {
            atomic_index,
            publication_index,
        }) = written
        {
            let publication = atomics
                .get_item(atomic_index)?
                .getattr(intern!(py, "publications"))?
                .get_item(publication_index)?;
            let exception = publication.getattr(intern!(py, "exception"))?;
            return Err(PyErr::from_value(exception));
        }

        Ok((out, results.added_pairs))
    }
}

impl SqlitePubSubWriter {
    /// Copies the values of each `PendingPublication` of a list.
    fn extract_publications(&self, publications: &Bound<'_, PyList>) -> PyResult<Vec<PublicationInput>> {
        let mut out = Vec::with_capacity(publications.len());

        for pending in publications.iter() {
            out.push(self.extract_publication(&pending)?);
        }

        Ok(out)
    }

    /// Copies the values of one `PendingPublication` that its message and delivery rows are built from.
    fn extract_publication(&self, pending: &Bound<'_, PyAny>) -> PyResult<PublicationInput> {
        let py = pending.py();
        let message_values = pending.getattr(intern!(py, "message_values"))?;

        let mut values = Vec::with_capacity(self.message_columns.len());
        for name in &self.message_columns {
            values.push(bound_value(&message_values.get_item(name.bind(py))?)?);
        }

        Ok(PublicationInput {
            values,
            msg_id: message_values.get_item(intern!(py, "msg_id"))?.extract()?,
            topic_name: message_values.get_item(intern!(py, "topic_name"))?.extract()?,
            payload_crc32: message_values.get_item(intern!(py, "payload_crc32"))?.extract()?,
            fingerprint: pending.getattr(intern!(py, "fingerprint"))?.extract()?,
            received_ms: pending.getattr(intern!(py, "received_ms"))?.extract()?,
            dedup_expires_ms: pending.getattr(intern!(py, "dedup_expires_ms"))?.extract()?,
            priority: bound_value(&message_values.get_item(intern!(py, "priority"))?)?,
            expiration_ms: bound_value(&message_values.get_item(intern!(py, "expiration_ms"))?)?,
        })
    }

    /// Copies the values of each `PendingAtomic` of a list.
    fn extract_atomics(&self, atomics: &Bound<'_, PyList>) -> PyResult<Vec<AtomicInput>> {
        let mut out = Vec::with_capacity(atomics.len());

        for pending in atomics.iter() {
            let py = pending.py();
            let publications = pending.getattr(intern!(py, "publications"))?.cast_into::<PyList>()?;
            let ack = pending.getattr(intern!(py, "ack"))?;

            let msg_ids: Vec<String> = ack.getattr(intern!(py, "msg_ids"))?.extract()?;
            let expected_attempts: Option<Vec<i64>> = ack.getattr(intern!(py, "expected_attempts"))?.extract()?;

            let mut entries = Vec::with_capacity(msg_ids.len());

            match expected_attempts {
                Some(expected_attempts) => {
                    for (msg_id, expected_attempt) in msg_ids.into_iter().zip(expected_attempts) {
                        entries.push(FencedEntry {
                            msg_id,
                            expected_attempt: Some(expected_attempt),
                        });
                    }
                }
                None => {
                    for msg_id in msg_ids {
                        entries.push(FencedEntry {
                            msg_id,
                            expected_attempt: None,
                        });
                    }
                }
            }

            out.push(AtomicInput {
                publications: self.extract_publications(&publications)?,
                sub_key: ack.getattr(intern!(py, "sub_key"))?.extract()?,
                entries,
                is_strict: pending.getattr(intern!(py, "is_strict"))?.extract()?,
            });
        }

        Ok(out)
    }

    /// Stores on a `PendingPublication` what became of it and records it if it repeats an earlier one.
    fn apply_publication(
        &self,
        pending: &Bound<'_, PyAny>,
        result: PublicationResult,
        repeats: &mut Vec<(String, &'static str)>,
    ) -> PyResult<()> {
        let py = pending.py();
        let message_values = pending.getattr(intern!(py, "message_values"))?;

        pending.setattr(intern!(py, "subscriber_keys"), result.subscriber_keys)?;

        if result.drops_payload {
            message_values.set_item(intern!(py, "payload"), py.None())?;
            message_values.set_item(intern!(py, "payload_encrypted"), false)?;
        }

        if let Some(repeat) = result.repeat {
            let msg_id: String = message_values.get_item(intern!(py, "msg_id"))?.extract()?;
            repeats.push((msg_id, repeat.name()));
            pending.setattr(intern!(py, "is_repeat"), true)?;
        }

        if let Some(message) = result.duplicate {
            let exception = self.duplicate_error.bind(py).call1((message,))?;
            pending.setattr(intern!(py, "exception"), exception)?;
        }

        Ok(())
    }

    /// Stores on a `PendingAtomic` what became of it and of its publications.
    fn apply_atomic(&self, pending: &Bound<'_, PyAny>, result: AtomicResult, repeats: &mut Vec<(String, &'static str)>) -> PyResult<()> {
        let py = pending.py();
        let publications = pending.getattr(intern!(py, "publications"))?;

        for (publication, publication_result) in publications.try_iter()?.zip(result.publications) {
            self.apply_publication(&publication?, publication_result, repeats)?;
        }

        apply_ack(&pending.getattr(intern!(py, "ack"))?, result.ack)?;

        if let Some(error) = result.error {
            let exception = match error {
                ItemError::Conflict(message) => self.conflict_error.bind(py).call1((message,))?,
                ItemError::Duplicate(message) => self.duplicate_error.bind(py).call1((message,))?,
            };
            pending.setattr(intern!(py, "exception"), exception)?;
        }

        Ok(())
    }

    /// Stores on a `PendingLease` the rows of the messages that it leased and the attempt of each.
    fn apply_lease(&self, pending: &Bound<'_, PyAny>, result: LeaseResult) -> PyResult<()> {
        let py = pending.py();
        let encrypted_index = self.layout.lease_payload_encrypted_index;
        let row_class = self.lease_row_class.bind(py);

        let rows = PyList::empty(py);

        for columns in result.rows {
            let mut objects = Vec::with_capacity(columns.len());
            for (index, value) in columns.into_iter().enumerate() {
                objects.push(value_object(py, value, index == encrypted_index)?);
            }
            rows.append(row_class.call1(PyTuple::new(py, objects)?)?)?;
        }

        let attempts = PyDict::new(py);
        for (message_id, attempt) in result.attempts {
            attempts.set_item(message_id, attempt)?;
        }

        pending.setattr(intern!(py, "rows"), rows)?;
        pending.setattr(intern!(py, "attempts"), attempts)?;

        Ok(())
    }
}

// ################################################################################################################################
// ################################################################################################################################

/// Returns the position of a column among the given columns.
fn column_index(columns: &[String], name: &str) -> PyResult<usize> {
    let Some(out) = columns.iter().position(|column| column == name) else {
        return Err(PyRuntimeError::new_err(format!("Column not found `{name}`")));
    };
    Ok(out)
}

/// Copies the values of each item of a list.
fn extract_list<Item>(items: &Bound<'_, PyList>, extract: impl Fn(&Bound<'_, PyAny>) -> PyResult<Item>) -> PyResult<Vec<Item>> {
    let mut out = Vec::with_capacity(items.len());

    for pending in items.iter() {
        out.push(extract(&pending)?);
    }

    Ok(out)
}

/// Copies the values of one `PendingAck`.
fn extract_ack(pending: &Bound<'_, PyAny>) -> PyResult<AckInput> {
    let py = pending.py();

    Ok(AckInput {
        sub_key: pending.getattr(intern!(py, "sub_key"))?.extract()?,
        msg_ids: pending.getattr(intern!(py, "msg_ids"))?.extract()?,
        sequence_ids: pending.getattr(intern!(py, "sequence_ids"))?.extract()?,
    })
}

/// Copies the values of one `PendingLease`.
fn extract_lease(pending: &Bound<'_, PyAny>) -> PyResult<LeaseInput> {
    let py = pending.py();

    Ok(LeaseInput {
        sub_key: pending.getattr(intern!(py, "sub_key"))?.extract()?,
        max_messages: pending.getattr(intern!(py, "max_messages"))?.extract()?,
        max_len: pending.getattr(intern!(py, "max_len"))?.extract()?,
        now_ms: pending.getattr(intern!(py, "now_ms"))?.extract()?,
        leased_until_ms: pending.getattr(intern!(py, "leased_until_ms"))?.extract()?,
    })
}

/// Stores on a `PendingAck` what became of it.
fn apply_ack(pending: &Bound<'_, PyAny>, result: AckResult) -> PyResult<()> {
    let py = pending.py();

    pending.setattr(intern!(py, "removed_count"), result.removed_count)?;
    pending.setattr(intern!(py, "fully_delivered_count"), result.fully_delivered_count)?;

    if let Some(concluded_msg_ids) = result.concluded_msg_ids {
        pending.setattr(intern!(py, "concluded_msg_ids"), concluded_msg_ids)?;
    }

    Ok(())
}

/// Returns a value read from `SQLite` as the Python driver returns it, with a boolean column as a boolean.
fn value_object(py: Python<'_>, value: Value, is_boolean: bool) -> PyResult<Bound<'_, PyAny>> {
    let out = match value {
        Value::Null => py.None().into_bound(py),
        Value::Integer(number) if is_boolean => PyBool::new(py, number != 0).to_owned().into_any(),
        Value::Integer(number) => number.into_pyobject(py)?.into_any(),
        Value::Real(number) => PyFloat::new(py, number).into_any(),
        Value::Text(text) => PyString::new(py, &text).into_any(),
        Value::Blob(bytes) => PyBytes::new(py, &bytes).into_any(),
    };
    Ok(out)
}

// ################################################################################################################################
// ################################################################################################################################
