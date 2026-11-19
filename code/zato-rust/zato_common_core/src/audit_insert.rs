//! Bulk insert of the events of the audit log into SQLite with the GIL released.
//!
//! The rows of a batch are written through the handle of the Python `sqlite3.Connection` whose transaction
//! is open, so they are committed or rolled back together with every other row of that transaction.
//! The values of the events are copied while the GIL is held, and the digests, the search texts,
//! the compression, the conversion of the times and the inserts take place after the GIL is released.

use std::borrow::Cow;
use std::collections::{BTreeMap, HashMap};
use std::fmt::Write as _;

use blake2::digest::consts::U16;
use blake2::{Blake2b, Digest};
use flate2::{Compress, Compression, FlushCompress, Status};
use pyo3::exceptions::{PyRuntimeError, PyTypeError};
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyType;
use pyo3::types::{PyBool, PyBytes, PyDateAccess, PyDateTime, PyDict, PyFloat, PyInt, PyList, PyString, PyTimeAccess};
use rusqlite::types::{ToSqlOutput, Value, ValueRef};
use rusqlite::{Connection, ErrorCode, Statement, ToSql, ffi};

use crate::search_text::search_text_of;

/// The zlib compression level of the compressed text columns, the level that Python compresses them with.
const COMPRESSION_LEVEL: u32 = 1;

/// How many hexadecimal characters the digest of a payload has, two for each of its 16 bytes.
const DIGEST_HEX_LEN: usize = 32;

/// The capacity that the output buffer of a compression grows by at least.
const MIN_COMPRESSED_GROWTH: usize = 64;

/// The position of the first parameter of a statement, as `SQLite` numbers them.
const FIRST_PARAMETER: usize = 1;

/// The text of a boolean attribute that is true, as Python formats it.
const ATTR_TRUE: &str = "True";

/// The text of a boolean attribute that is false, as Python formats it.
const ATTR_FALSE: &str = "False";

/// How many characters of the text of an attribute are stored.
const ATTR_VALUE_MAX_LEN: usize = 255;

/// The module whose exception classes the errors of the inserts are raised as.
const SQLITE_MODULE: &str = "sqlite3";

// ################################################################################################################################
// ################################################################################################################################

/// A moment in UTC, as the event and body tables store it.
#[derive(Clone)]
struct UtcTime {
    /// The calendar year.
    year: i32,

    /// The month of the year, from 1.
    month: u8,

    /// The day of the month, from 1.
    day: u8,

    /// The hour of the day.
    hour: u8,

    /// The minute of the hour.
    minute: u8,

    /// The second of the minute.
    second: u8,

    /// The microseconds within the second.
    microsecond: u32,
}

impl UtcTime {
    /// Returns the text that the column of a time holds, the format in which `SQLAlchemy` stores a datetime in `SQLite`.
    fn to_column_text(&self) -> String {
        let Self {
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
        } = self;
        format!("{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}.{microsecond:06}")
    }
}

/// The value of one column of an event row.
#[derive(Clone)]
enum ColumnValue {
    /// A value that is bound as the Python driver binds it.
    Bound(Value),

    /// A time, converted to UTC, which is bound as the text of its column.
    Time(UtcTime),

    /// A time that is not set.
    NoTime,
}

impl ToSql for ColumnValue {
    fn to_sql(&self) -> rusqlite::Result<ToSqlOutput<'_>> {
        let out = match self {
            Self::Bound(value) => ToSqlOutput::Borrowed(ValueRef::from(value)),
            Self::Time(time) => ToSqlOutput::Owned(Value::Text(time.to_column_text())),
            Self::NoTime => ToSqlOutput::Owned(Value::Null),
        };

        Ok(out)
    }
}

/// Where the digest and the search text of the payload of an event come from.
enum PayloadSource {
    /// Python computed both before the write, outside the lock of the database.
    Prepared {
        /// The digest of the payload, or none for an empty payload.
        digest: Option<String>,

        /// The words of the payload that the search index holds.
        search_text: String,
    },

    /// Both are computed here.
    Unprepared,
}

/// One row of the attribute table, without the id of its event.
struct AttrRow {
    /// The name of the attribute.
    name: String,

    /// The text of the value, capped to the length of the column.
    value: String,

    /// The value as a number, for an attribute that is an integer or a float.
    value_number: Option<f64>,
}

/// One row of the body table, without the id and the time of its event.
struct BodyRow {
    /// The kind of the body, e.g. a request, a response or an attachment.
    kind: String,

    /// The text of the body, which the column stores compressed.
    data: Option<String>,

    /// The bytes of an attachment whose content is kept.
    content: Option<Vec<u8>>,
}

/// The values of one event of a batch, copied from its `PendingEvent`.
struct EventInput {
    /// The values of the columns of the event row, in the order of the parameters of the insert.
    columns: Vec<ColumnValue>,

    /// The time of the event, which its body rows are stamped with, so pruning them needs no join.
    event_time: ColumnValue,

    /// The payload of the event, which the payload table stores once under its digest.
    data: String,

    /// Where the digest and the search text of the payload come from.
    payload: PayloadSource,

    /// The searchable attributes of the event.
    attrs: Vec<AttrRow>,

    /// The message bodies of the event, followed by its attachments.
    bodies: Vec<BodyRow>,

    /// The ids of the parent events of the event.
    parents: Vec<i64>,

    /// How the event relates to its parents.
    link_type: String,
}

/// A payload of a batch, stored once under its digest however many events have it.
struct PayloadInput<'batch> {
    /// The text of the payload.
    data: &'batch str,

    /// The search text that Python prepared for the payload, if any event of the batch carries it.
    search_text: Option<&'batch str>,
}

/// One column of the event table that the values of an event provide.
struct EventColumn {
    /// The key of the column in the values of an event.
    name: Py<PyString>,

    /// Whether the column holds a time, which is stored in UTC.
    is_time: bool,
}

/// The statements that write the rows of a batch, built by Python from the metadata of the tables of the audit log.
struct Statements {
    /// The insert of one event row, with the id of the row of its payload as the last parameter.
    insert_event: String,

    /// The query for the id of the stored payload of a digest.
    select_payload: String,

    /// The insert of one payload, which skips a digest that is stored already.
    insert_payload: String,

    /// The insert of one attribute row.
    insert_attr: String,

    /// The insert of one body row.
    insert_body: String,

    /// The insert of one lineage link.
    insert_link: String,
}

/// Why the rows of a batch could not be written.
enum WriteError {
    /// `SQLite` refused a statement.
    Sqlite(rusqlite::Error),

    /// zlib refused to compress a text.
    Compression(flate2::CompressError),

    /// A payload that the insert skipped as stored already is not found by its digest.
    MissingPayload(String),
}

impl From<rusqlite::Error> for WriteError {
    fn from(error: rusqlite::Error) -> Self {
        Self::Sqlite(error)
    }
}

impl From<flate2::CompressError> for WriteError {
    fn from(error: flate2::CompressError) -> Self {
        Self::Compression(error)
    }
}

impl WriteError {
    /// Returns the exception of the Python driver that the error is raised as.
    fn into_py_err(self, py: Python<'_>) -> PyErr {
        let (class_name, message) = match self {
            Self::Sqlite(error) => (sqlite_error_class(&error), error.to_string()),
            Self::Compression(error) => ("OperationalError", error.to_string()),
            Self::MissingPayload(digest) => ("IntegrityError", format!("Payload not found by its digest `{digest}`")),
        };

        driver_error(py, class_name, message)
    }
}

/// Returns an exception of a class of the `SQLite` driver of Python.
fn driver_error(py: Python<'_>, class_name: &str, message: String) -> PyErr {
    let error_class = py
        .import(SQLITE_MODULE)
        .and_then(|module| Ok(module.getattr(class_name)?.cast_into::<PyType>()?));

    match error_class {
        Ok(error_class) => PyErr::from_type(error_class, message),
        Err(error) => error,
    }
}

/// Returns the name of the exception class of the Python driver that the error of `SQLite` maps to.
fn sqlite_error_class(error: &rusqlite::Error) -> &'static str {
    match error.sqlite_error_code() {
        Some(ErrorCode::ConstraintViolation) => "IntegrityError",
        Some(ErrorCode::DatabaseCorrupt | ErrorCode::NotADatabase) => "DatabaseError",
        _ => "OperationalError",
    }
}

// ################################################################################################################################
// ################################################################################################################################

/// Writes the events of the audit log of a batch into `SQLite`.
///
/// The events are written with their payloads, attributes, bodies and lineage links
/// in the transaction that the given `sqlite3.Connection` holds open.
#[pyclass(frozen, name = "SQLiteAuditWriter")]
pub struct SqliteAuditWriter {
    /// The statements that write the rows of a batch.
    statements: Statements,

    /// The columns of the event table that the values of an event provide, in the order of the parameters of the insert.
    event_columns: Vec<EventColumn>,

    /// The position of the time of the event among the event columns, which its body rows are stamped with.
    event_time_index: usize,

    /// The class `sqlite3.Connection`, whose instances alone hold the handle that the rows are written through.
    connection_type: Py<PyAny>,

    /// The time zone `datetime.timezone.utc`, which the times are converted to.
    utc: Py<PyAny>,

    /// The Python function that returns the kind, the text and the content of the body row of each attachment of an event.
    attachment_bodies: Py<PyAny>,
}

#[pymethods]
impl SqliteAuditWriter {
    /// Builds the writer from the statements and the event columns that Python derived from the metadata of the tables.
    #[new]
    fn new(py: Python<'_>, config: &Bound<'_, PyDict>) -> PyResult<Self> {
        let config = config.as_any();

        // The handle is shared with the Python driver, so both must use the same SQLite library ..
        let python_version: String = config.get_item("sqlite_version")?.extract()?;
        check_library_version(&python_version, rusqlite::version()).map_err(PyRuntimeError::new_err)?;

        // .. and the columns arrive in the order of the parameters of the insert of an event row.
        let column_specs: Vec<(Bound<'_, PyString>, bool)> = config.get_item("event_columns")?.extract()?;
        let event_time_column: String = config.get_item("event_time_column")?.extract()?;

        let mut event_columns = Vec::with_capacity(column_specs.len());
        let mut event_time_index = None;

        for (index, (name, is_time)) in column_specs.into_iter().enumerate() {
            if name.to_str()? == event_time_column {
                event_time_index = Some(index);
            }
            event_columns.push(EventColumn {
                name: name.unbind(),
                is_time,
            });
        }

        let Some(event_time_index) = event_time_index else {
            return Err(PyRuntimeError::new_err(format!("Event column not found `{event_time_column}`")));
        };

        let statements = Statements {
            insert_event: config.get_item("insert_event")?.extract()?,
            select_payload: config.get_item("select_payload")?.extract()?,
            insert_payload: config.get_item("insert_payload")?.extract()?,
            insert_attr: config.get_item("insert_attr")?.extract()?,
            insert_body: config.get_item("insert_body")?.extract()?,
            insert_link: config.get_item("insert_link")?.extract()?,
        };

        Ok(Self {
            statements,
            event_columns,
            event_time_index,
            connection_type: py.import(SQLITE_MODULE)?.getattr("Connection")?.unbind(),
            utc: py.import("datetime")?.getattr("timezone")?.getattr("utc")?.unbind(),
            attachment_bodies: config.get_item("attachment_bodies")?.unbind(),
        })
    }

    /// Inserts the events of a batch with all their rows in the open transaction of the connection,
    /// sets the id of each event on its `PendingEvent`, and returns the ids in the order of the batch.
    fn insert_events(&self, py: Python<'_>, connection: &Bound<'_, PyAny>, batch: &Bound<'_, PyList>) -> PyResult<Vec<i64>> {
        let mut events = Vec::with_capacity(batch.len());

        for pending in batch.iter() {
            events.push(self.extract_event(py, &pending)?);
        }

        let sqlite = open_handle(connection, self.connection_type.bind(py))?;

        // The rows join the transaction of the caller, which must therefore be open already
        if sqlite.is_autocommit() {
            return Err(PyRuntimeError::new_err("The connection has no open transaction"));
        }

        let statements = &self.statements;

        // Everything from here on is written without the GIL, so the other threads of the interpreter run in the meantime
        let written = py.detach(move || write_batch(&sqlite, statements, &events));
        let event_ids = written.map_err(|error| error.into_py_err(py))?;

        // The export of the events reads their ids from the pending events once the batch is written
        let event_id_name = intern!(py, "event_id");

        for (pending, event_id) in batch.iter().zip(&event_ids) {
            pending.setattr(event_id_name, event_id)?;
        }

        Ok(event_ids)
    }
}

impl SqliteAuditWriter {
    /// Copies the values of one `PendingEvent` that its rows are built from.
    fn extract_event(&self, py: Python<'_>, pending: &Bound<'_, PyAny>) -> PyResult<EventInput> {
        let values = pending.getattr(intern!(py, "values"))?;
        let utc = self.utc.bind(py);

        let mut columns = Vec::with_capacity(self.event_columns.len());
        let mut event_time = ColumnValue::NoTime;

        for (index, column) in self.event_columns.iter().enumerate() {
            let value = values.get_item(column.name.bind(py))?;

            let column_value = if column.is_time {
                time_value(&value, utc)?
            } else {
                ColumnValue::Bound(bound_value(&value)?)
            };

            if index == self.event_time_index {
                event_time = column_value.clone();
            }

            columns.push(column_value);
        }

        let payload = if pending.getattr(intern!(py, "is_payload_prepared"))?.is_truthy()? {
            PayloadSource::Prepared {
                digest: pending.getattr(intern!(py, "payload_digest"))?.extract()?,
                search_text: pending.getattr(intern!(py, "search_text"))?.extract()?,
            }
        } else {
            PayloadSource::Unprepared
        };

        let attrs = pending.getattr(intern!(py, "attrs"))?;
        let bodies = pending.getattr(intern!(py, "bodies"))?;
        let attachments = pending.getattr(intern!(py, "attachments"))?;

        let mut body_rows = extract_bodies(bodies.cast()?)?;

        // Attachments follow the other bodies of the event, one body row each
        if attachments.is_truthy()? {
            let attachment_rows = self.attachment_bodies.bind(py).call1((attachments,))?;
            for row in attachment_rows.try_iter()? {
                let (kind, data, content): (String, Option<String>, Option<Bound<'_, PyBytes>>) = row?.extract()?;
                let content = content.map(|content| content.as_bytes().to_vec());
                body_rows.push(BodyRow { kind, data, content });
            }
        }

        Ok(EventInput {
            columns,
            event_time,
            data: values.get_item(intern!(py, "data"))?.extract()?,
            payload,
            attrs: extract_attrs(attrs.cast()?)?,
            bodies: body_rows,
            parents: pending.getattr(intern!(py, "parents"))?.extract()?,
            link_type: pending.getattr(intern!(py, "parent_link_type"))?.extract()?,
        })
    }
}

// ################################################################################################################################
// ################################################################################################################################

/// Confirms that the `SQLite` library of the Python driver is the library linked to Rust,
/// which a handle shared between the two requires.
pub(crate) fn check_library_version(python_version: &str, library_version: &str) -> Result<(), String> {
    if python_version != library_version {
        return Err(format!(
            "SQLite of the driver `{python_version}` differs from SQLite of the writer `{library_version}`"
        ));
    }

    Ok(())
}

/// Returns a connection over the handle of a connection of the `SQLite` driver of Python, which never closes the handle.
///
/// The connection type is `sqlite3.Connection`, whose instances alone hold the handle.
pub(crate) fn open_handle(connection: &Bound<'_, PyAny>, connection_type: &Bound<'_, PyAny>) -> PyResult<Connection> {
    let py = connection.py();

    // Only the C structure of the driver's own connections is known to hold the handle ..
    if !connection.is_instance(connection_type)? {
        let type_name = connection.get_type().name()?;
        return Err(PyTypeError::new_err(format!("Not a connection of the SQLite driver `{type_name}`")));
    }

    // .. right after the header of the object.
    let field = connection.as_ptr().wrapping_add(1).cast::<*mut ffi::sqlite3>();

    #[expect(unsafe_code, reason = "the SQLite driver of Python exposes no handle of its connections")]
    // SAFETY: the object is an instance of `sqlite3.Connection`, whose C structure, `pysqlite_Connection`,
    // begins with `PyObject_HEAD` followed by the `sqlite3 *db` field, which is aligned as a pointer, and the GIL is held,
    // so the driver is not changing the field while it is read.
    let handle = unsafe { field.read() };

    // A closed connection has no handle
    if handle.is_null() {
        return Err(driver_error(
            py,
            "ProgrammingError",
            "Cannot operate on a closed database.".to_owned(),
        ));
    }

    #[expect(
        unsafe_code,
        reason = "a connection over a handle that another library opened has no safe constructor"
    )]
    // SAFETY: the handle is open and stays open while the rows are written, because the caller holds a reference
    // to the Python connection that owns it for the whole call, and only the thread of the call uses it meanwhile.
    // The returned connection does not close the handle when it is dropped.
    let out = unsafe { Connection::from_handle(handle) }.map_err(|error| sqlite_py_err(py, error))?;

    Ok(out)
}

/// Returns the exception of the Python driver that an error of `SQLite` is raised as.
pub(crate) fn sqlite_py_err(py: Python<'_>, error: rusqlite::Error) -> PyErr {
    WriteError::from(error).into_py_err(py)
}

/// Returns a value as the `SQLite` driver of Python binds it.
pub(crate) fn bound_value(value: &Bound<'_, PyAny>) -> PyResult<Value> {
    if value.is_none() {
        return Ok(Value::Null);
    }

    if let Ok(text) = value.cast::<PyString>() {
        return Ok(Value::Text(text.to_str()?.to_owned()));
    }

    // A boolean is an integer to the driver, so it is recognized before any other integer
    if value.is_instance_of::<PyBool>() {
        return Ok(Value::Integer(i64::from(value.is_truthy()?)));
    }

    if value.is_instance_of::<PyInt>() {
        return Ok(Value::Integer(value.extract()?));
    }

    if value.is_instance_of::<PyFloat>() {
        return Ok(Value::Real(value.extract()?));
    }

    if let Ok(bytes) = value.cast::<PyBytes>() {
        return Ok(Value::Blob(bytes.as_bytes().to_vec()));
    }

    let type_name = value.get_type().name()?;
    Err(PyTypeError::new_err(format!("Unsupported type of an event column `{type_name}`")))
}

/// Returns a time converted to UTC, as the column type of the times converts it before it is stored.
fn time_value(value: &Bound<'_, PyAny>, utc: &Bound<'_, PyAny>) -> PyResult<ColumnValue> {
    if value.is_none() {
        return Ok(ColumnValue::NoTime);
    }

    let converted = value.call_method1(intern!(value.py(), "astimezone"), (utc,))?;
    let converted = converted.cast::<PyDateTime>()?;

    Ok(ColumnValue::Time(UtcTime {
        year: converted.get_year(),
        month: converted.get_month(),
        day: converted.get_day(),
        hour: converted.get_hour(),
        minute: converted.get_minute(),
        second: converted.get_second(),
        microsecond: converted.get_microsecond(),
    }))
}

/// Copies the attributes of an event into rows - every value is stored as capped text,
/// and an integer or a float is stored as a number as well.
fn extract_attrs(attrs: &Bound<'_, PyDict>) -> PyResult<Vec<AttrRow>> {
    let mut out = Vec::with_capacity(attrs.len());

    for (name, value) in attrs.iter() {
        let name: String = name.extract()?;

        // A boolean is text alone, although Python considers it an integer ..
        let row = if value.is_instance_of::<PyBool>() {
            let text = if value.is_truthy()? { ATTR_TRUE } else { ATTR_FALSE };
            AttrRow {
                name,
                value: text.to_owned(),
                value_number: None,
            }
        }
        // .. integers and floats are stored twice, in full ..
        else if value.is_instance_of::<PyInt>() || value.is_instance_of::<PyFloat>() {
            let text = value.str()?.to_str()?.to_owned();
            AttrRow {
                name,
                value: text,
                value_number: Some(value.extract()?),
            }
        }
        // .. and everything else is text, capped to the length of the column.
        else {
            let text = value.str()?;
            let text = capped_attr_text(text.to_str()?);
            AttrRow {
                name,
                value: text,
                value_number: None,
            }
        };

        out.push(row);
    }

    Ok(out)
}

/// Returns the text of an attribute value capped to the length of its column, in characters.
fn capped_attr_text(text: &str) -> String {
    text.chars().take(ATTR_VALUE_MAX_LEN).collect()
}

/// Copies the message bodies of an event, by their kinds.
fn extract_bodies(bodies: &Bound<'_, PyDict>) -> PyResult<Vec<BodyRow>> {
    let mut out = Vec::with_capacity(bodies.len());

    for (kind, data) in bodies.iter() {
        out.push(BodyRow {
            kind: kind.extract()?,
            data: data.extract()?,
            content: None,
        });
    }

    Ok(out)
}

// ################################################################################################################################
// ################################################################################################################################

/// Returns the digest that a payload is stored under, or none for an empty payload, which is not stored.
fn payload_digest(data: &str) -> Option<String> {
    if data.is_empty() {
        return None;
    }

    let digest = Blake2b::<U16>::digest(data.as_bytes());
    let mut out = String::with_capacity(DIGEST_HEX_LEN);

    for byte in digest {
        // Writing to a string cannot fail
        write!(out, "{byte:02x}").ok();
    }

    Some(out)
}

/// Compresses a text with zlib exactly as Python's `zlib.compress` does at the same level,
/// with all of the input given to a single finishing call.
fn compress_text(text: &str) -> Result<Vec<u8>, WriteError> {
    let input = text.as_bytes();
    let mut compressor = Compress::new(Compression::new(COMPRESSION_LEVEL), true);
    let mut out = Vec::with_capacity(input.len().saturating_add(MIN_COMPRESSED_GROWTH));

    loop {
        // The input that zlib has not consumed yet, if the output buffer filled up before it consumed all of it
        let consumed = usize::try_from(compressor.total_in()).unwrap_or(usize::MAX);
        let remaining = input.get(consumed..).unwrap_or_default();

        // The output buffer always has room for zlib to make progress
        if out.len() == out.capacity() {
            out.reserve(out.capacity().max(MIN_COMPRESSED_GROWTH));
        }

        if compressor.compress_vec(remaining, &mut out, FlushCompress::Finish)? == Status::StreamEnd {
            return Ok(out);
        }
    }
}

/// Returns the id of the stored payload of a digest, if it is stored.
fn find_payload(select: &mut Statement<'_>, digest: &str) -> Result<Option<i64>, WriteError> {
    let mut rows = select.query([digest])?;

    let out = match rows.next()? {
        Some(row) => Some(row.get(0)?),
        None => None,
    };

    Ok(out)
}

/// Stores the payloads of a batch that are not stored yet, in the order of their digests,
/// and returns the id of the row of each payload by its digest.
fn store_payloads<'batch>(
    sqlite: &Connection,
    statements: &Statements,
    payloads: &BTreeMap<&'batch str, PayloadInput<'batch>>,
) -> Result<HashMap<&'batch str, i64>, WriteError> {
    let mut select = sqlite.prepare_cached(&statements.select_payload)?;
    let mut insert = sqlite.prepare_cached(&statements.insert_payload)?;

    let mut out = HashMap::with_capacity(payloads.len());
    let mut missing = Vec::new();

    // A payload that is stored already is referenced as it is ..
    for (&digest, payload) in payloads {
        match find_payload(&mut select, digest)? {
            Some(payload_id) => {
                out.insert(digest, payload_id);
            }
            None => missing.push((digest, payload)),
        }
    }

    for (digest, payload) in missing {
        // .. any other one is stored with its search text, the prepared one or one extracted now ..
        let search_text = payload
            .search_text
            .map_or_else(|| Cow::Owned(search_text_of(payload.data)), Cow::Borrowed);

        let compressed = compress_text(payload.data)?;
        let inserted = insert.execute((digest, compressed, search_text.as_ref()))?;

        // .. and a payload that another writer stored in the meantime is found by its digest.
        let payload_id = if inserted == 1 {
            sqlite.last_insert_rowid()
        } else {
            find_payload(&mut select, digest)?.ok_or_else(|| WriteError::MissingPayload(digest.to_owned()))?
        };

        out.insert(digest, payload_id);
    }

    Ok(out)
}

/// Returns the digest of the payload of each event of a batch, computing those that Python did not prepare,
/// each distinct payload once however many events have it.
fn event_digests(events: &[EventInput]) -> Vec<Option<String>> {
    let mut out = Vec::with_capacity(events.len());
    let mut digest_by_data: HashMap<&str, Option<String>> = HashMap::new();

    for event in events {
        let digest = match &event.payload {
            PayloadSource::Prepared { digest, .. } => digest.clone(),
            PayloadSource::Unprepared => digest_by_data
                .entry(event.data.as_str())
                .or_insert_with(|| payload_digest(&event.data))
                .clone(),
        };
        out.push(digest);
    }

    out
}

/// Returns the payloads of a batch by their digests, each once, with the search texts that Python prepared for them.
fn batch_payloads<'batch>(events: &'batch [EventInput], digests: &'batch [Option<String>]) -> BTreeMap<&'batch str, PayloadInput<'batch>> {
    let mut out: BTreeMap<&str, PayloadInput<'_>> = BTreeMap::new();

    for (event, digest) in events.iter().zip(digests) {
        let Some(digest) = digest else {
            continue;
        };

        let prepared_search_text = match &event.payload {
            PayloadSource::Prepared { search_text, .. } => Some(search_text.as_str()),
            PayloadSource::Unprepared => None,
        };

        let payload = out.entry(digest.as_str()).or_insert_with(|| PayloadInput {
            data: &event.data,
            search_text: None,
        });

        if prepared_search_text.is_some() {
            payload.search_text = prepared_search_text;
        }
    }

    out
}

/// Inserts the event rows of a batch, each with the id of the row of its payload, and returns their ids in the order of the batch.
fn insert_event_rows(
    sqlite: &Connection,
    statements: &Statements,
    events: &[EventInput],
    payload_ids: &[Option<i64>],
) -> Result<Vec<i64>, WriteError> {
    let mut insert = sqlite.prepare_cached(&statements.insert_event)?;
    let mut out = Vec::with_capacity(events.len());

    for (event, payload_id) in events.iter().zip(payload_ids) {
        let mut index = FIRST_PARAMETER;

        for column in &event.columns {
            insert.raw_bind_parameter(index, column)?;
            index = index.saturating_add(1);
        }

        // The id of the row of the payload is the last parameter
        insert.raw_bind_parameter(index, payload_id)?;
        insert.raw_execute()?;

        out.push(sqlite.last_insert_rowid());
    }

    Ok(out)
}

/// Inserts the attributes, bodies and lineage links of the events of a batch, one table after another.
fn insert_companion_rows(sqlite: &Connection, statements: &Statements, events: &[EventInput], event_ids: &[i64]) -> Result<(), WriteError> {
    let mut insert_attr = sqlite.prepare_cached(&statements.insert_attr)?;

    for (event, event_id) in events.iter().zip(event_ids) {
        for attr in &event.attrs {
            insert_attr.execute((event_id, &attr.name, &attr.value, attr.value_number))?;
        }
    }

    let mut insert_body = sqlite.prepare_cached(&statements.insert_body)?;

    for (event, event_id) in events.iter().zip(event_ids) {
        for body in &event.bodies {
            let data = body.data.as_deref().map(compress_text).transpose()?;
            insert_body.execute((event_id, &body.kind, &event.event_time, data, &body.content))?;
        }
    }

    let mut insert_link = sqlite.prepare_cached(&statements.insert_link)?;

    for (event, event_id) in events.iter().zip(event_ids) {
        for parent_event_id in &event.parents {
            insert_link.execute((event_id, parent_event_id, &event.link_type))?;
        }
    }

    Ok(())
}

/// Writes all the rows of a batch - the payloads first, the events that reference them next,
/// and the rows that reference the events last - and returns the ids of the events in the order of the batch.
fn write_batch(sqlite: &Connection, statements: &Statements, events: &[EventInput]) -> Result<Vec<i64>, WriteError> {
    let digests = event_digests(events);
    let payloads = batch_payloads(events, &digests);
    let stored = store_payloads(sqlite, statements, &payloads)?;

    // Each event references the row of its payload, and an event without a payload references none
    let mut payload_ids = Vec::with_capacity(digests.len());

    for digest in &digests {
        let payload_id = match digest {
            Some(digest) => Some(
                *stored
                    .get(digest.as_str())
                    .ok_or_else(|| WriteError::MissingPayload(digest.clone()))?,
            ),
            None => None,
        };
        payload_ids.push(payload_id);
    }

    let event_ids = insert_event_rows(sqlite, statements, events, &payload_ids)?;
    insert_companion_rows(sqlite, statements, events, &event_ids)?;

    Ok(event_ids)
}

// ################################################################################################################################
// ################################################################################################################################

#[cfg(test)]
#[path = "audit_insert_tests.rs"]
mod tests;
