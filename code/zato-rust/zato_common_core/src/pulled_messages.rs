//! Building of the messages that pulls of pub/sub hand out, and of the audit events of their reception.
//!
//! A pull leases the delivery rows of a subscriber and reads the rows of their messages in one transaction.
//! The rows are converted here into the message dicts that the REST layer returns, and each reception
//! is recorded as a pending audit event that commits in the same transaction as the lease.

use pyo3::exceptions::PyKeyError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PySet, PyString};

// ################################################################################################################################
// ################################################################################################################################

/// The positions of the columns of a message in the rows that a pull reads.
struct RowColumns {

    /// The primary key of the message, which a message has as its sequence ID.
    id: usize,

    /// The public identifier of the message.
    msg_id: usize,

    /// The topic that the message was published to.
    topic_name: usize,

    /// The payload, stored as text or encrypted at rest.
    payload: usize,

    /// Whether the payload is encrypted at rest.
    payload_encrypted: usize,

    /// The class of the data of the payload.
    data_class: usize,

    /// The size of the payload.
    data_size: usize,

    /// The beginning of the payload that previews it.
    data_preview: usize,

    /// The priority of the message.
    priority: usize,

    /// The expiration of the message.
    expiration: usize,

    /// The time of the publication.
    pub_time_iso: usize,

    /// The time at which the server received the publication.
    recv_time_iso: usize,

    /// The time at which the message expires.
    expiration_time_iso: usize,

    /// The publisher of the message, if given.
    publisher: usize,

    /// The CID of the publication, if given.
    cid: usize,

    /// The correlation ID of the message, if given.
    correl_id: usize,

    /// The ID of the message that this one replies to, if given.
    in_reply_to: usize,

    /// The ID of the external client that published the message, if given.
    ext_client_id: usize,
}

/// The values of one row that both its message and the audit event of its reception have.
struct SharedValues<'py> {

    /// The primary key of the message.
    id: Bound<'py, PyAny>,

    /// The public identifier of the message.
    msg_id: Bound<'py, PyAny>,

    /// The topic that the message was published to.
    topic_name: Bound<'py, PyAny>,

    /// The priority of the message.
    priority: Bound<'py, PyAny>,

    /// The time of the publication.
    pub_time_iso: Bound<'py, PyAny>,

    /// The CID of the publication, or a value that is not truthy when none was given.
    cid: Bound<'py, PyAny>,

    /// The payload of the message as it is handed out.
    data: Bound<'py, PyAny>,
}

/// One retry setting, which a message has under its name only when its publisher gave it.
struct RetryColumn {

    /// The key of the setting in the message, the name of its column.
    key: Py<PyString>,

    /// The position of the column in the rows.
    index: usize,
}

/// The values of the audit event of a reception that do not depend on the message.
struct ReceptionEvent {

    /// The source of the event, pub/sub.
    source: Py<PyString>,

    /// The type of the event, the reception of a message.
    event_type: Py<PyString>,

    /// The outcome of the event, a successful reception.
    outcome: Py<PyString>,
}

/// Returns the position of a column among the columns of the rows.
fn column_index(columns: &[String], name: &str) -> PyResult<usize> {
    let position = columns.iter().position(|column| column == name);

    // A column that the query does not read cannot be converted into a key of the message.
    position.ok_or_else(|| PyKeyError::new_err(format!("Column not found among the leased rows `{name}`")))
}

/// Returns the columns of the retry settings with the given names, in the order of the names.
fn retry_columns(py: Python<'_>, columns: &[String], names: &[String]) -> PyResult<Vec<RetryColumn>> {
    let mut out = Vec::with_capacity(names.len());

    for name in names {
        let index = column_index(columns, name)?;
        let key = PyString::intern(py, name).unbind();
        out.push(RetryColumn { key, index });
    }

    Ok(out)
}

/// Sets a key of a message to a value given at publish time, leaving the key out when the value is not truthy.
fn set_if_given(message: &Bound<'_, PyDict>, key: &Bound<'_, PyString>, value: &Bound<'_, PyAny>) -> PyResult<()> {
    if value.is_truthy()? {
        message.set_item(key, value)?;
    }

    Ok(())
}

/// Returns a value that is stored as None or as an empty text when it was not given, the empty text in both cases.
fn text_or_empty(value: Bound<'_, PyAny>) -> PyResult<Bound<'_, PyAny>> {
    let py = value.py();

    if value.is_truthy()? {
        Ok(value)
    } else {
        Ok(intern!(py, "").clone().into_any())
    }
}

// ################################################################################################################################
// ################################################################################################################################

/// Builds the messages that a pull of pub/sub hands out.
///
/// The audit event of the reception of each message is built with it. One instance serves one backend, whose sets of topics with their audit log off
/// and with their payloads exported it reads on every pull.
#[pyclass(frozen, name = "PulledMessageBuilder")]
pub struct PulledMessageBuilder {

    /// The positions of the columns of a message in the rows.
    columns: RowColumns,

    /// The retry settings, in the order in which a message has them, each only when its publisher gave it.
    retry_columns: Vec<RetryColumn>,

    /// The names of the topics whose audit log is off, which record no reception.
    audit_disabled_topics: Py<PySet>,

    /// The names of the topics whose payloads leave with the audit export.
    audit_payload_topics: Py<PySet>,

    /// The Python function that parses the time of a publication into an aware datetime.
    parse_utc: Py<PyAny>,

    /// The values of the audit event of each reception that do not depend on the message.
    reception_event: ReceptionEvent,
}

#[pymethods]
impl PulledMessageBuilder {

    /// Builds the builder from the columns of the rows that a pull reads and from the topic sets of the backend.
    #[new]
    fn new(py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let config = config.as_any();

        // The rows of a pull have their columns in the order of the query that reads them ..
        let column_names: Vec<String> = config.get_item("columns")?.extract()?;
        let retry_names: Vec<String> = config.get_item("retry_names")?.extract()?;

        let columns = RowColumns {
            id: column_index(&column_names, "id")?,
            msg_id: column_index(&column_names, "msg_id")?,
            topic_name: column_index(&column_names, "topic_name")?,
            payload: column_index(&column_names, "payload")?,
            payload_encrypted: column_index(&column_names, "payload_encrypted")?,
            data_class: column_index(&column_names, "data_class")?,
            data_size: column_index(&column_names, "data_size")?,
            data_preview: column_index(&column_names, "data_preview")?,
            priority: column_index(&column_names, "priority")?,
            expiration: column_index(&column_names, "expiration")?,
            pub_time_iso: column_index(&column_names, "pub_time_iso")?,
            recv_time_iso: column_index(&column_names, "recv_time_iso")?,
            expiration_time_iso: column_index(&column_names, "expiration_time_iso")?,
            publisher: column_index(&column_names, "publisher")?,
            cid: column_index(&column_names, "cid")?,
            correl_id: column_index(&column_names, "correl_id")?,
            in_reply_to: column_index(&column_names, "in_reply_to")?,
            ext_client_id: column_index(&column_names, "ext_client_id")?,
        };

        // .. the retry settings are keyed by their names ..
        let retry_columns = retry_columns(py, &column_names, &retry_names)?;

        // .. and the audit event of a reception is built from the constants of the audit log.
        let reception_event = ReceptionEvent {
            source: config.get_item("event_source")?.cast_into::<PyString>()?.unbind(),
            event_type: config.get_item("event_type")?.cast_into::<PyString>()?.unbind(),
            outcome: config.get_item("event_outcome")?.cast_into::<PyString>()?.unbind(),
        };

        Ok(Self {
            columns,
            retry_columns,
            audit_disabled_topics: config.get_item("audit_disabled_topics")?.cast_into::<PySet>()?.unbind(),
            audit_payload_topics: config.get_item("audit_payload_topics")?.cast_into::<PySet>()?.unbind(),
            parse_utc: config.get_item("parse_utc")?.unbind(),
            reception_event,
        })
    }

    /// Appends to a lease the message of each of its rows and, with the audit log given, the audit event
    /// of each reception, except for the messages of topics whose audit log is off.
    ///
    /// The payload of a row encrypted at rest is decrypted with the crypto manager.
    fn build(&self, lease: &Bound<'_, PyAny>, audit_log: Option<&Bound<'_, PyAny>>, crypto_manager: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = lease.py();

        let rows = lease.getattr(intern!(py, "rows"))?.cast_into::<PyList>()?;
        let attempts = lease.getattr(intern!(py, "attempts"))?;
        let messages = lease.getattr(intern!(py, "messages"))?.cast_into::<PyList>()?;
        let audit_events = lease.getattr(intern!(py, "audit_events"))?.cast_into::<PyList>()?;
        let sub_key = lease.getattr(intern!(py, "sub_key"))?;

        let audit_disabled_topics = self.audit_disabled_topics.bind(py);
        let delivery_attempt_key = intern!(py, "delivery_attempt");

        for row in rows.iter() {
            // Each copy of a message carries the number of the pull that handed it out, which a repeated copy raises ..
            let shared = self.read_shared_values(&row, crypto_manager)?;
            let message = self.build_message(&row, &shared)?;

            let attempt = attempts.get_item(&shared.id)?;
            message.set_item(delivery_attempt_key, attempt)?;
            messages.append(&message)?;

            // .. and its reception is recorded, unless the audit log or the audit log of its topic is off.
            let Some(audit_log) = audit_log else {
                continue;
            };

            if audit_disabled_topics.contains(&shared.topic_name)? {
                continue;
            }

            let audit_event = self.new_received_event(audit_log, &shared, &sub_key)?;
            audit_events.append(audit_event)?;
        }

        Ok(())
    }
}

impl PulledMessageBuilder {

    /// Returns the values of a row that its message and the audit event of its reception both have.
    fn read_shared_values<'py>(&self, row: &Bound<'py, PyAny>, crypto_manager: &Bound<'py, PyAny>) -> PyResult<SharedValues<'py>> {
        let columns = &self.columns;
        let data = self.load_payload(row, crypto_manager)?;

        Ok(SharedValues {
            id: row.get_item(columns.id)?,
            msg_id: row.get_item(columns.msg_id)?,
            topic_name: row.get_item(columns.topic_name)?,
            priority: row.get_item(columns.priority)?,
            pub_time_iso: row.get_item(columns.pub_time_iso)?,
            cid: row.get_item(columns.cid)?,
            data,
        })
    }

    /// Returns the payload of one message row, decrypted if it was encrypted at rest, a missing payload being ''.
    fn load_payload<'py>(&self, row: &Bound<'py, PyAny>, crypto_manager: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
        let py = row.py();
        let payload = row.get_item(self.columns.payload)?;

        // A message stored without its payload has an empty one ..
        if payload.is_none() {
            let empty = intern!(py, "").clone().into_any();
            return Ok(empty);
        }

        // .. one encrypted at rest is decrypted ..
        let is_encrypted = row.get_item(self.columns.payload_encrypted)?.is_truthy()?;

        if is_encrypted {
            let decrypted = crypto_manager.call_method1(intern!(py, "decrypt"), (payload,))?;
            return Ok(decrypted);
        }

        // .. and any other one is handed out as it is stored.
        Ok(payload)
    }

    /// Returns the message dict of one row, in the form that the REST layer returns.
    fn build_message<'py>(&self, row: &Bound<'py, PyAny>, shared: &SharedValues<'py>) -> PyResult<Bound<'py, PyDict>> {
        let py = row.py();
        let columns = &self.columns;

        let data_class = text_or_empty(row.get_item(columns.data_class)?)?;
        let data_preview = text_or_empty(row.get_item(columns.data_preview)?)?;

        let out = PyDict::new(py);

        // The always-present fields come first ..
        out.set_item(intern!(py, "msg_id"), &shared.msg_id)?;
        out.set_item(intern!(py, "sequence_id"), &shared.id)?;
        out.set_item(intern!(py, "topic_name"), &shared.topic_name)?;
        out.set_item(intern!(py, "data"), &shared.data)?;
        out.set_item(intern!(py, "data_class"), data_class)?;
        out.set_item(intern!(py, "data_size"), row.get_item(columns.data_size)?)?;
        out.set_item(intern!(py, "data_preview"), data_preview)?;
        out.set_item(intern!(py, "priority"), &shared.priority)?;
        out.set_item(intern!(py, "expiration"), row.get_item(columns.expiration)?)?;
        out.set_item(intern!(py, "pub_time_iso"), &shared.pub_time_iso)?;
        out.set_item(intern!(py, "recv_time_iso"), row.get_item(columns.recv_time_iso)?)?;
        out.set_item(intern!(py, "expiration_time_iso"), row.get_item(columns.expiration_time_iso)?)?;

        // .. the optional ones are included only when they were given at publish time ..
        set_if_given(&out, intern!(py, "publisher"), &row.get_item(columns.publisher)?)?;
        set_if_given(&out, intern!(py, "cid"), &shared.cid)?;
        set_if_given(&out, intern!(py, "correl_id"), &row.get_item(columns.correl_id)?)?;
        set_if_given(&out, intern!(py, "in_reply_to"), &row.get_item(columns.in_reply_to)?)?;
        set_if_given(&out, intern!(py, "ext_client_id"), &row.get_item(columns.ext_client_id)?)?;

        // .. and so is each retry setting, a setting left out being left out here too, so that the policy's defaults apply to it.
        for column in &self.retry_columns {
            let value = row.get_item(column.index)?;

            if !value.is_none() {
                out.set_item(column.key.bind(py), value)?;
            }
        }

        Ok(out)
    }

    /// Returns the pending audit event of the reception of one message by a pull client.
    fn new_received_event<'py>(
        &self,
        audit_log: &Bound<'py, PyAny>,
        shared: &SharedValues<'py>,
        sub_key: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = audit_log.py();
        let reception_event = &self.reception_event;

        // Messages published before CIDs were carried inside them have no CID stored ..
        let cid = text_or_empty(shared.cid.clone())?;

        // .. the time of the publication is parsed as Python parses it everywhere else ..
        let pub_time = self.parse_utc.bind(py).call1((&shared.pub_time_iso,))?;

        // .. the size is that of the text in characters ..
        let size = shared.data.len()?;

        // .. and the payload leaves with the export only for a topic whose payloads are exported.
        let is_export_payload_active = self.audit_payload_topics.bind(py).contains(&shared.topic_name)?;

        let kwargs = PyDict::new(py);
        kwargs.set_item(intern!(py, "cid"), cid)?;
        kwargs.set_item(intern!(py, "msg_id"), &shared.msg_id)?;
        kwargs.set_item(intern!(py, "pub_time"), pub_time)?;
        kwargs.set_item(intern!(py, "sub_key"), sub_key)?;
        kwargs.set_item(intern!(py, "size"), size)?;
        kwargs.set_item(intern!(py, "priority"), &shared.priority)?;
        kwargs.set_item(intern!(py, "outcome"), reception_event.outcome.bind(py))?;
        kwargs.set_item(intern!(py, "data"), &shared.data)?;
        kwargs.set_item(intern!(py, "is_export_payload_active"), is_export_payload_active)?;

        let event_source = reception_event.source.bind(py);
        let event_type = reception_event.event_type.bind(py);
        let arguments = (event_source, event_type, &shared.topic_name);

        audit_log.call_method(intern!(py, "new_pending_event"), arguments, Some(&kwargs))
    }
}
