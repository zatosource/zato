use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::Serialize;

use crate::model::*;
use super::store::ConfigStore;
use super::util::{struct_to_pydict, pydict_to_struct};

fn check_attr_in_values<T: Serialize>(store: &std::collections::HashMap<String, T>, attr_name: &str, value: &str) -> PyResult<bool> {
    for item in store.values() {
        let json_val = serde_json::to_value(item)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("serialization error: {e}")))?;
        if let Some(field_val) = json_val.get(attr_name) {
            let matches = match field_val {
                serde_json::Value::String(s) => s == value,
                other => other.to_string() == value,
            };
            if matches {
                return Ok(true);
            }
        }
    }
    Ok(false)
}

macro_rules! impl_attr_value_exists {
    ($store_field:ident, $fn_name:ident) => {
        fn $fn_name(&self, attr_name: &str, value: &str) -> PyResult<bool> {
            let store = self.$store_field.read()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
            check_attr_in_values(&*store, attr_name, value)
        }
    };
}

macro_rules! impl_crud {
    ($store_field:ident, $rust_ty:ty,
     $get_name:ident, $get_list_name:ident, $set_name:ident, $delete_name:ident) => {

        fn $get_name<'py>(&self, py: Python<'py>, name: &str) -> PyResult<Option<Py<PyDict>>> {
            let store = self.$store_field.read()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
            match store.get(name) {
                Some(item) => Ok(Some(struct_to_pydict(py, item)?)),
                None => Ok(None),
            }
        }

        fn $get_list_name<'py>(&self, py: Python<'py>) -> PyResult<Py<PyList>> {
            let store = self.$store_field.read()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
            let list = PyList::empty(py);
            for item in store.values() {
                let d = struct_to_pydict(py, item)?;
                let _ = list.append(d.bind(py));
            }
            Ok(list.unbind())
        }

        fn $set_name<'py>(&self, py: Python<'py>, name: &str, data: &Bound<'py, PyDict>) -> PyResult<()> {
            let item: $rust_ty = pydict_to_struct(py, data)?;
            let mut store = self.$store_field.write()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
            store.insert(name.to_string(), item);
            Ok(())
        }

        fn $delete_name(&self, name: &str) -> PyResult<bool> {
            let mut store = self.$store_field.write()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
            Ok(store.remove(name).is_some())
        }
    };
}

macro_rules! dispatch {
    (get, $self:expr, $py:expr, $entity_type:expr, $name:expr) => {
        match $entity_type {
            "security"            => $self.get_security($py, $name),
            "groups"              => $self._get_group($py, $name),
            "channel_rest"        => $self._get_channel_rest($py, $name),
            "channel_soap"        => $self._get_channel_soap($py, $name),
            "channel_amqp"        => $self._get_channel_amqp($py, $name),
            "channel_openapi"     => $self._get_channel_openapi($py, $name),
            "outgoing_rest"       => $self._get_outgoing_rest($py, $name),
            "outgoing_soap"       => $self._get_outgoing_soap($py, $name),
            "outgoing_amqp"       => $self._get_outgoing_amqp($py, $name),
            "outgoing_ftp"        => $self._get_outgoing_ftp($py, $name),
            "outgoing_sql"        => $self._get_outgoing_sql($py, $name),
            "outgoing_odoo"       => $self._get_outgoing_odoo($py, $name),
            "outgoing_sap"        => $self._get_outgoing_sap($py, $name),
            "cache_builtin"       => $self._get_cache_builtin($py, $name),
            "email_smtp"          => $self._get_email_smtp($py, $name),
            "email_imap"          => $self._get_email_imap($py, $name),
            "scheduler"           => $self._get_scheduler($py, $name),
            "holiday_calendar"    => $self._get_holiday_calendar($py, $name),
            "generic_connection"  => $self._get_generic_connection($py, $name),
            "pubsub_topic"        => $self._get_pubsub_topic($py, $name),
            "pubsub_permission"   => $self._get_pubsub_permission($py, $name),
            "pubsub_subscription" => $self._get_pubsub_subscription($py, $name),
            "elastic_search"      => $self._get_elastic_search($py, $name),
            "service"             => $self._get_service($py, $name),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", $entity_type)
            )),
        }
    };
    (get_list, $self:expr, $py:expr, $entity_type:expr) => {
        match $entity_type {
            "security"            => $self.get_list_security($py),
            "groups"              => $self._get_list_groups($py),
            "channel_rest"        => $self._get_list_channel_rest($py),
            "channel_soap"        => $self._get_list_channel_soap($py),
            "channel_amqp"        => $self._get_list_channel_amqp($py),
            "channel_openapi"     => $self._get_list_channel_openapi($py),
            "outgoing_rest"       => $self._get_list_outgoing_rest($py),
            "outgoing_soap"       => $self._get_list_outgoing_soap($py),
            "outgoing_amqp"       => $self._get_list_outgoing_amqp($py),
            "outgoing_ftp"        => $self._get_list_outgoing_ftp($py),
            "outgoing_sql"        => $self._get_list_outgoing_sql($py),
            "outgoing_odoo"       => $self._get_list_outgoing_odoo($py),
            "outgoing_sap"        => $self._get_list_outgoing_sap($py),
            "cache_builtin"       => $self._get_list_cache_builtin($py),
            "email_smtp"          => $self._get_list_email_smtp($py),
            "email_imap"          => $self._get_list_email_imap($py),
            "scheduler"           => $self._get_list_scheduler($py),
            "holiday_calendar"    => $self._get_list_holiday_calendar($py),
            "generic_connection"  => $self._get_list_generic_connection($py),
            "pubsub_topic"        => $self._get_list_pubsub_topic($py),
            "pubsub_permission"   => $self._get_list_pubsub_permission($py),
            "pubsub_subscription" => $self._get_list_pubsub_subscription($py),
            "elastic_search"      => $self._get_list_elastic_search($py),
            "service"             => $self._get_list_service($py),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", $entity_type)
            )),
        }
    };
    (set, $self:expr, $py:expr, $entity_type:expr, $name:expr, $data:expr) => {
        match $entity_type {
            "security"            => $self.set_security($py, $name, $data),
            "groups"              => $self._set_group($py, $name, $data),
            "channel_rest"        => $self._set_channel_rest($py, $name, $data),
            "channel_soap"        => $self._set_channel_soap($py, $name, $data),
            "channel_amqp"        => $self._set_channel_amqp($py, $name, $data),
            "channel_openapi"     => $self._set_channel_openapi($py, $name, $data),
            "outgoing_rest"       => $self._set_outgoing_rest($py, $name, $data),
            "outgoing_soap"       => $self._set_outgoing_soap($py, $name, $data),
            "outgoing_amqp"       => $self._set_outgoing_amqp($py, $name, $data),
            "outgoing_ftp"        => $self._set_outgoing_ftp($py, $name, $data),
            "outgoing_sql"        => $self._set_outgoing_sql($py, $name, $data),
            "outgoing_odoo"       => $self._set_outgoing_odoo($py, $name, $data),
            "outgoing_sap"        => $self._set_outgoing_sap($py, $name, $data),
            "cache_builtin"       => $self._set_cache_builtin($py, $name, $data),
            "email_smtp"          => $self._set_email_smtp($py, $name, $data),
            "email_imap"          => $self._set_email_imap($py, $name, $data),
            "scheduler"           => $self._set_scheduler($py, $name, $data),
            "holiday_calendar"    => $self._set_holiday_calendar($py, $name, $data),
            "generic_connection"  => $self._set_generic_connection($py, $name, $data),
            "pubsub_topic"        => $self._set_pubsub_topic($py, $name, $data),
            "pubsub_permission"   => $self._set_pubsub_permission($py, $name, $data),
            "pubsub_subscription" => $self._set_pubsub_subscription($py, $name, $data),
            "elastic_search"      => $self._set_elastic_search($py, $name, $data),
            "service"             => $self._set_service($py, $name, $data),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", $entity_type)
            )),
        }
    };
    (delete, $self:expr, $entity_type:expr, $name:expr) => {
        match $entity_type {
            "security"            => $self.delete_security($name),
            "groups"              => $self._delete_group($name),
            "channel_rest"        => $self._delete_channel_rest($name),
            "channel_soap"        => $self._delete_channel_soap($name),
            "channel_amqp"        => $self._delete_channel_amqp($name),
            "channel_openapi"     => $self._delete_channel_openapi($name),
            "outgoing_rest"       => $self._delete_outgoing_rest($name),
            "outgoing_soap"       => $self._delete_outgoing_soap($name),
            "outgoing_amqp"       => $self._delete_outgoing_amqp($name),
            "outgoing_ftp"        => $self._delete_outgoing_ftp($name),
            "outgoing_sql"        => $self._delete_outgoing_sql($name),
            "outgoing_odoo"       => $self._delete_outgoing_odoo($name),
            "outgoing_sap"        => $self._delete_outgoing_sap($name),
            "cache_builtin"       => $self._delete_cache_builtin($name),
            "email_smtp"          => $self._delete_email_smtp($name),
            "email_imap"          => $self._delete_email_imap($name),
            "scheduler"           => $self._delete_scheduler($name),
            "holiday_calendar"    => $self._delete_holiday_calendar($name),
            "generic_connection"  => $self._delete_generic_connection($name),
            "pubsub_topic"        => $self._delete_pubsub_topic($name),
            "pubsub_permission"   => $self._delete_pubsub_permission($name),
            "pubsub_subscription" => $self._delete_pubsub_subscription($name),
            "elastic_search"      => $self._delete_elastic_search($name),
            "service"             => $self._delete_service($name),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", $entity_type)
            )),
        }
    };
}

impl ConfigStore {
    impl_crud!(channel_rest, ChannelRest,
        _get_channel_rest, _get_list_channel_rest, _set_channel_rest, _delete_channel_rest);
    impl_crud!(channel_soap, ChannelSoap,
        _get_channel_soap, _get_list_channel_soap, _set_channel_soap, _delete_channel_soap);
    impl_crud!(channel_amqp, ChannelAmqp,
        _get_channel_amqp, _get_list_channel_amqp, _set_channel_amqp, _delete_channel_amqp);
    impl_crud!(channel_openapi, ChannelOpenApi,
        _get_channel_openapi, _get_list_channel_openapi, _set_channel_openapi, _delete_channel_openapi);
    impl_crud!(outgoing_rest, OutgoingRest,
        _get_outgoing_rest, _get_list_outgoing_rest, _set_outgoing_rest, _delete_outgoing_rest);
    impl_crud!(outgoing_soap, OutgoingSoap,
        _get_outgoing_soap, _get_list_outgoing_soap, _set_outgoing_soap, _delete_outgoing_soap);
    impl_crud!(outgoing_amqp, OutgoingAmqp,
        _get_outgoing_amqp, _get_list_outgoing_amqp, _set_outgoing_amqp, _delete_outgoing_amqp);
    impl_crud!(outgoing_ftp, OutgoingFtp,
        _get_outgoing_ftp, _get_list_outgoing_ftp, _set_outgoing_ftp, _delete_outgoing_ftp);
    impl_crud!(outgoing_sql, OutgoingSql,
        _get_outgoing_sql, _get_list_outgoing_sql, _set_outgoing_sql, _delete_outgoing_sql);
    impl_crud!(outgoing_odoo, OutgoingOdoo,
        _get_outgoing_odoo, _get_list_outgoing_odoo, _set_outgoing_odoo, _delete_outgoing_odoo);
    impl_crud!(outgoing_sap, OutgoingSap,
        _get_outgoing_sap, _get_list_outgoing_sap, _set_outgoing_sap, _delete_outgoing_sap);
    impl_crud!(cache_builtin, CacheBuiltinDef,
        _get_cache_builtin, _get_list_cache_builtin, _set_cache_builtin, _delete_cache_builtin);
    impl_crud!(email_smtp, EmailSmtp,
        _get_email_smtp, _get_list_email_smtp, _set_email_smtp, _delete_email_smtp);
    impl_crud!(email_imap, EmailImap,
        _get_email_imap, _get_list_email_imap, _set_email_imap, _delete_email_imap);
    impl_crud!(scheduler, SchedulerJob,
        _get_scheduler, _get_list_scheduler, _set_scheduler, _delete_scheduler);
    impl_crud!(holiday_calendar, HolidayCalendar,
        _get_holiday_calendar, _get_list_holiday_calendar, _set_holiday_calendar, _delete_holiday_calendar);
    impl_crud!(generic_connection, GenericConnection,
        _get_generic_connection, _get_list_generic_connection, _set_generic_connection, _delete_generic_connection);
    impl_crud!(pubsub_topic, PubSubTopic,
        _get_pubsub_topic, _get_list_pubsub_topic, _set_pubsub_topic, _delete_pubsub_topic);
    impl_crud!(pubsub_permission, PubSubPermission,
        _get_pubsub_permission, _get_list_pubsub_permission, _set_pubsub_permission, _delete_pubsub_permission);
    impl_crud!(pubsub_subscription, PubSubSubscription,
        _get_pubsub_subscription, _get_list_pubsub_subscription, _set_pubsub_subscription, _delete_pubsub_subscription);
    impl_crud!(elastic_search, ElasticSearchDef,
        _get_elastic_search, _get_list_elastic_search, _set_elastic_search, _delete_elastic_search);
    impl_crud!(service, ServiceInfo,
        _get_service, _get_list_service, _set_service, _delete_service);
    impl_crud!(groups, SecurityGroup,
        _get_group, _get_list_groups, _set_group, _delete_group);

    impl_attr_value_exists!(security,            _attr_exists_security);
    impl_attr_value_exists!(groups,              _attr_exists_groups);
    impl_attr_value_exists!(channel_rest,        _attr_exists_channel_rest);
    impl_attr_value_exists!(channel_soap,        _attr_exists_channel_soap);
    impl_attr_value_exists!(channel_amqp,        _attr_exists_channel_amqp);
    impl_attr_value_exists!(channel_openapi,     _attr_exists_channel_openapi);
    impl_attr_value_exists!(outgoing_rest,       _attr_exists_outgoing_rest);
    impl_attr_value_exists!(outgoing_soap,       _attr_exists_outgoing_soap);
    impl_attr_value_exists!(outgoing_amqp,       _attr_exists_outgoing_amqp);
    impl_attr_value_exists!(outgoing_ftp,        _attr_exists_outgoing_ftp);
    impl_attr_value_exists!(outgoing_sql,        _attr_exists_outgoing_sql);
    impl_attr_value_exists!(outgoing_odoo,       _attr_exists_outgoing_odoo);
    impl_attr_value_exists!(outgoing_sap,        _attr_exists_outgoing_sap);
    impl_attr_value_exists!(cache_builtin,       _attr_exists_cache_builtin);
    impl_attr_value_exists!(email_smtp,          _attr_exists_email_smtp);
    impl_attr_value_exists!(email_imap,          _attr_exists_email_imap);
    impl_attr_value_exists!(scheduler,           _attr_exists_scheduler);
    impl_attr_value_exists!(holiday_calendar,    _attr_exists_holiday_calendar);
    impl_attr_value_exists!(generic_connection,  _attr_exists_generic_connection);
    impl_attr_value_exists!(pubsub_topic,        _attr_exists_pubsub_topic);
    impl_attr_value_exists!(pubsub_permission,   _attr_exists_pubsub_permission);
    impl_attr_value_exists!(pubsub_subscription, _attr_exists_pubsub_subscription);
    impl_attr_value_exists!(elastic_search,      _attr_exists_elastic_search);
    impl_attr_value_exists!(service,             _attr_exists_service);
}

#[pymethods]
impl ConfigStore {

    #[pyo3(signature = (entity_type, name))]
    fn get<'py>(&self, py: Python<'py>, entity_type: &str, name: &str) -> PyResult<Option<Py<PyDict>>> {
        dispatch!(get, self, py, entity_type, name)
    }

    #[pyo3(signature = (entity_type,))]
    fn get_list<'py>(&self, py: Python<'py>, entity_type: &str) -> PyResult<Py<PyList>> {
        dispatch!(get_list, self, py, entity_type)
    }

    #[pyo3(signature = (entity_type, name, data))]
    fn set<'py>(&self, py: Python<'py>, entity_type: &str, name: &str, data: &Bound<'py, PyDict>) -> PyResult<()> {
        dispatch!(set, self, py, entity_type, name, data)
    }

    #[pyo3(signature = (entity_type, name))]
    fn delete(&self, entity_type: &str, name: &str) -> PyResult<bool> {
        dispatch!(delete, self, entity_type, name)
    }

    #[pyo3(signature = (username, password))]
    fn check_basic_auth(&self, username: &str, password: &str) -> PyResult<Option<String>> {
        self._check_basic_auth(username, password)
    }

    #[pyo3(signature = (header_value,))]
    fn check_apikey(&self, header_value: &str) -> PyResult<Option<String>> {
        self._check_apikey(header_value)
    }

    #[pyo3(signature = (entity_type, attr_name, value))]
    fn attr_value_exists(&self, entity_type: &str, attr_name: &str, value: &str) -> PyResult<bool> {
        match entity_type {
            "security"            => self._attr_exists_security(attr_name, value),
            "groups"              => self._attr_exists_groups(attr_name, value),
            "channel_rest"        => self._attr_exists_channel_rest(attr_name, value),
            "channel_soap"        => self._attr_exists_channel_soap(attr_name, value),
            "channel_amqp"        => self._attr_exists_channel_amqp(attr_name, value),
            "channel_openapi"     => self._attr_exists_channel_openapi(attr_name, value),
            "outgoing_rest"       => self._attr_exists_outgoing_rest(attr_name, value),
            "outgoing_soap"       => self._attr_exists_outgoing_soap(attr_name, value),
            "outgoing_amqp"       => self._attr_exists_outgoing_amqp(attr_name, value),
            "outgoing_ftp"        => self._attr_exists_outgoing_ftp(attr_name, value),
            "outgoing_sql"        => self._attr_exists_outgoing_sql(attr_name, value),
            "outgoing_odoo"       => self._attr_exists_outgoing_odoo(attr_name, value),
            "outgoing_sap"        => self._attr_exists_outgoing_sap(attr_name, value),
            "cache_builtin"       => self._attr_exists_cache_builtin(attr_name, value),
            "email_smtp"          => self._attr_exists_email_smtp(attr_name, value),
            "email_imap"          => self._attr_exists_email_imap(attr_name, value),
            "scheduler"           => self._attr_exists_scheduler(attr_name, value),
            "holiday_calendar"    => self._attr_exists_holiday_calendar(attr_name, value),
            "generic_connection"  => self._attr_exists_generic_connection(attr_name, value),
            "pubsub_topic"        => self._attr_exists_pubsub_topic(attr_name, value),
            "pubsub_permission"   => self._attr_exists_pubsub_permission(attr_name, value),
            "pubsub_subscription" => self._attr_exists_pubsub_subscription(attr_name, value),
            "elastic_search"      => self._attr_exists_elastic_search(attr_name, value),
            "service"             => self._attr_exists_service(attr_name, value),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", entity_type)
            )),
        }
    }
}
