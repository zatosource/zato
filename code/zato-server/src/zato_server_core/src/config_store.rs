use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use std::collections::HashMap;
use std::sync::RwLock;

use crate::models::*;

// ── per-type storage helper ──

macro_rules! typed_store {
    ($name:ident, $ty:ty) => {
        #[allow(dead_code)]
        fn $name(&self) -> &RwLock<HashMap<String, $ty>> {
            &self.$name
        }
    };
}

// ── ConfigStore ──

#[pyclass]
pub struct ConfigStore {
    security:            RwLock<HashMap<String, SecurityDef>>,
    groups:              RwLock<HashMap<String, SecurityGroup>>,
    channel_rest:        RwLock<HashMap<String, ChannelRest>>,
    channel_soap:        RwLock<HashMap<String, ChannelSoap>>,
    channel_amqp:        RwLock<HashMap<String, ChannelAmqp>>,
    channel_openapi:     RwLock<HashMap<String, ChannelOpenApi>>,
    outgoing_rest:       RwLock<HashMap<String, OutgoingRest>>,
    outgoing_soap:       RwLock<HashMap<String, OutgoingSoap>>,
    outgoing_amqp:       RwLock<HashMap<String, OutgoingAmqp>>,
    outgoing_ftp:        RwLock<HashMap<String, OutgoingFtp>>,
    outgoing_sql:        RwLock<HashMap<String, OutgoingSql>>,
    outgoing_odoo:       RwLock<HashMap<String, OutgoingOdoo>>,
    outgoing_sap:        RwLock<HashMap<String, OutgoingSap>>,
    cache_builtin:       RwLock<HashMap<String, CacheBuiltinDef>>,
    email_smtp:          RwLock<HashMap<String, EmailSmtp>>,
    email_imap:          RwLock<HashMap<String, EmailImap>>,
    scheduler:           RwLock<HashMap<String, SchedulerJob>>,
    holiday_calendar:    RwLock<HashMap<String, HolidayCalendar>>,
    generic_connection:  RwLock<HashMap<String, GenericConnection>>,
    pubsub_topic:        RwLock<HashMap<String, PubSubTopic>>,
    pubsub_permission:   RwLock<HashMap<String, PubSubPermission>>,
    pubsub_subscription: RwLock<HashMap<String, PubSubSubscription>>,
    elastic_search:      RwLock<HashMap<String, ElasticSearchDef>>,
    service:             RwLock<HashMap<String, ServiceInfo>>,
}

impl ConfigStore {
    typed_store!(security, SecurityDef);
    typed_store!(groups, SecurityGroup);
    typed_store!(channel_rest, ChannelRest);
    typed_store!(channel_soap, ChannelSoap);
    typed_store!(channel_amqp, ChannelAmqp);
    typed_store!(channel_openapi, ChannelOpenApi);
    typed_store!(outgoing_rest, OutgoingRest);
    typed_store!(outgoing_soap, OutgoingSoap);
    typed_store!(outgoing_amqp, OutgoingAmqp);
    typed_store!(outgoing_ftp, OutgoingFtp);
    typed_store!(outgoing_sql, OutgoingSql);
    typed_store!(outgoing_odoo, OutgoingOdoo);
    typed_store!(outgoing_sap, OutgoingSap);
    typed_store!(cache_builtin, CacheBuiltinDef);
    typed_store!(email_smtp, EmailSmtp);
    typed_store!(email_imap, EmailImap);
    typed_store!(scheduler, SchedulerJob);
    typed_store!(holiday_calendar, HolidayCalendar);
    typed_store!(generic_connection, GenericConnection);
    typed_store!(pubsub_topic, PubSubTopic);
    typed_store!(pubsub_permission, PubSubPermission);
    typed_store!(pubsub_subscription, PubSubSubscription);
    typed_store!(elastic_search, ElasticSearchDef);
    typed_store!(service, ServiceInfo);
}

// ── helpers to convert Rust structs to Python dicts via serde ──

fn value_to_py(py: Python<'_>, v: &serde_yaml::Value) -> Py<PyAny> {
    match v {
        serde_yaml::Value::Null => py.None().into_pyobject(py).unwrap().unbind(),
        serde_yaml::Value::Bool(b) => (*b).into_pyobject(py).unwrap().to_owned().unbind().into_any(),
        serde_yaml::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.into_pyobject(py).unwrap().unbind().into_any()
            } else if let Some(u) = n.as_u64() {
                u.into_pyobject(py).unwrap().unbind().into_any()
            } else if let Some(f) = n.as_f64() {
                f.into_pyobject(py).unwrap().unbind().into_any()
            } else {
                py.None().into_pyobject(py).unwrap().unbind()
            }
        }
        serde_yaml::Value::String(s) => s.into_pyobject(py).unwrap().unbind().into_any(),
        serde_yaml::Value::Sequence(seq) => {
            let list = PyList::empty(py);
            for item in seq {
                let _ = list.append(value_to_py(py, item));
            }
            list.unbind().into_any()
        }
        serde_yaml::Value::Mapping(map) => {
            let dict = PyDict::new(py);
            for (k, val) in map {
                if let serde_yaml::Value::String(ks) = k {
                    let _ = dict.set_item(ks, value_to_py(py, val));
                }
            }
            dict.unbind().into_any()
        }
        serde_yaml::Value::Tagged(t) => value_to_py(py, &t.value),
    }
}

fn struct_to_pydict<T: serde::Serialize>(py: Python<'_>, item: &T) -> PyResult<Py<PyDict>> {
    let yaml_val = serde_yaml::to_value(item)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("serialize: {}", e)))?;
    if let serde_yaml::Value::Mapping(map) = yaml_val {
        let dict = PyDict::new(py);
        for (k, v) in &map {
            if let serde_yaml::Value::String(ks) = k {
                let _ = dict.set_item(ks, value_to_py(py, v));
            }
        }
        Ok(dict.unbind())
    } else {
        Err(pyo3::exceptions::PyValueError::new_err("expected mapping"))
    }
}

fn pydict_to_struct<T: serde::de::DeserializeOwned>(py: Python<'_>, dict: &Bound<'_, PyDict>) -> PyResult<T> {
    let mut map = serde_yaml::Mapping::new();
    for (k, v) in dict.iter() {
        let key_str: String = k.extract()?;
        let yaml_key = serde_yaml::Value::String(key_str);
        let yaml_val = py_to_value(py, &v)?;
        map.insert(yaml_key, yaml_val);
    }
    let yaml_val = serde_yaml::Value::Mapping(map);
    serde_yaml::from_value(yaml_val)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("deserialize: {}", e)))
}

fn py_to_value(_py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<serde_yaml::Value> {
    if obj.is_none() {
        Ok(serde_yaml::Value::Null)
    } else if let Ok(b) = obj.extract::<bool>() {
        Ok(serde_yaml::Value::Bool(b))
    } else if let Ok(i) = obj.extract::<i64>() {
        Ok(serde_yaml::Value::Number(i.into()))
    } else if let Ok(f) = obj.extract::<f64>() {
        Ok(serde_yaml::Value::Number(serde_yaml::Number::from(f)))
    } else if let Ok(s) = obj.extract::<String>() {
        if let Ok(i) = s.parse::<i64>() {
            Ok(serde_yaml::Value::Number(i.into()))
        } else if s == "true" || s == "True" {
            Ok(serde_yaml::Value::Bool(true))
        } else if s == "false" || s == "False" {
            Ok(serde_yaml::Value::Bool(false))
        } else {
            Ok(serde_yaml::Value::String(s))
        }
    } else if let Ok(list) = obj.cast::<PyList>() {
        let mut seq = Vec::new();
        for item in list.iter() {
            seq.push(py_to_value(_py, &item)?);
        }
        Ok(serde_yaml::Value::Sequence(seq))
    } else if let Ok(dict) = obj.cast::<PyDict>() {
        let mut map = serde_yaml::Mapping::new();
        for (k, v) in dict.iter() {
            let key_str: String = k.extract()?;
            map.insert(serde_yaml::Value::String(key_str), py_to_value(_py, &v)?);
        }
        Ok(serde_yaml::Value::Mapping(map))
    } else {
        let s = obj.str()?.to_string();
        Ok(serde_yaml::Value::String(s))
    }
}

// ── macro for get/get_list/set/delete per entity type ──

macro_rules! impl_crud {
    ($store_field:ident, $entity_type:expr, $rust_ty:ty,
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

impl ConfigStore {
    impl_crud!(channel_rest, "channel_rest", ChannelRest,
        _get_channel_rest, _get_list_channel_rest, _set_channel_rest, _delete_channel_rest);
    impl_crud!(channel_soap, "channel_soap", ChannelSoap,
        _get_channel_soap, _get_list_channel_soap, _set_channel_soap, _delete_channel_soap);
    impl_crud!(channel_amqp, "channel_amqp", ChannelAmqp,
        _get_channel_amqp, _get_list_channel_amqp, _set_channel_amqp, _delete_channel_amqp);
    impl_crud!(channel_openapi, "channel_openapi", ChannelOpenApi,
        _get_channel_openapi, _get_list_channel_openapi, _set_channel_openapi, _delete_channel_openapi);
    impl_crud!(outgoing_rest, "outgoing_rest", OutgoingRest,
        _get_outgoing_rest, _get_list_outgoing_rest, _set_outgoing_rest, _delete_outgoing_rest);
    impl_crud!(outgoing_soap, "outgoing_soap", OutgoingSoap,
        _get_outgoing_soap, _get_list_outgoing_soap, _set_outgoing_soap, _delete_outgoing_soap);
    impl_crud!(outgoing_amqp, "outgoing_amqp", OutgoingAmqp,
        _get_outgoing_amqp, _get_list_outgoing_amqp, _set_outgoing_amqp, _delete_outgoing_amqp);
    impl_crud!(outgoing_ftp, "outgoing_ftp", OutgoingFtp,
        _get_outgoing_ftp, _get_list_outgoing_ftp, _set_outgoing_ftp, _delete_outgoing_ftp);
    impl_crud!(outgoing_sql, "outgoing_sql", OutgoingSql,
        _get_outgoing_sql, _get_list_outgoing_sql, _set_outgoing_sql, _delete_outgoing_sql);
    impl_crud!(outgoing_odoo, "outgoing_odoo", OutgoingOdoo,
        _get_outgoing_odoo, _get_list_outgoing_odoo, _set_outgoing_odoo, _delete_outgoing_odoo);
    impl_crud!(outgoing_sap, "outgoing_sap", OutgoingSap,
        _get_outgoing_sap, _get_list_outgoing_sap, _set_outgoing_sap, _delete_outgoing_sap);
    impl_crud!(cache_builtin, "cache_builtin", CacheBuiltinDef,
        _get_cache_builtin, _get_list_cache_builtin, _set_cache_builtin, _delete_cache_builtin);
    impl_crud!(email_smtp, "email_smtp", EmailSmtp,
        _get_email_smtp, _get_list_email_smtp, _set_email_smtp, _delete_email_smtp);
    impl_crud!(email_imap, "email_imap", EmailImap,
        _get_email_imap, _get_list_email_imap, _set_email_imap, _delete_email_imap);
    impl_crud!(scheduler, "scheduler", SchedulerJob,
        _get_scheduler, _get_list_scheduler, _set_scheduler, _delete_scheduler);
    impl_crud!(holiday_calendar, "holiday_calendar", HolidayCalendar,
        _get_holiday_calendar, _get_list_holiday_calendar, _set_holiday_calendar, _delete_holiday_calendar);
    impl_crud!(generic_connection, "generic_connection", GenericConnection,
        _get_generic_connection, _get_list_generic_connection, _set_generic_connection, _delete_generic_connection);
    impl_crud!(pubsub_topic, "pubsub_topic", PubSubTopic,
        _get_pubsub_topic, _get_list_pubsub_topic, _set_pubsub_topic, _delete_pubsub_topic);
    impl_crud!(pubsub_permission, "pubsub_permission", PubSubPermission,
        _get_pubsub_permission, _get_list_pubsub_permission, _set_pubsub_permission, _delete_pubsub_permission);
    impl_crud!(pubsub_subscription, "pubsub_subscription", PubSubSubscription,
        _get_pubsub_subscription, _get_list_pubsub_subscription, _set_pubsub_subscription, _delete_pubsub_subscription);
    impl_crud!(elastic_search, "elastic_search", ElasticSearchDef,
        _get_elastic_search, _get_list_elastic_search, _set_elastic_search, _delete_elastic_search);
    impl_crud!(service, "service", ServiceInfo,
        _get_service, _get_list_service, _set_service, _delete_service);
    impl_crud!(groups, "groups", SecurityGroup,
        _get_group, _get_list_groups, _set_group, _delete_group);
}

// ── PyO3 methods ──

#[pymethods]
impl ConfigStore {

    #[new]
    #[pyo3(signature = ())]
    fn new() -> Self {
        ConfigStore {
            security:            RwLock::new(HashMap::new()),
            groups:              RwLock::new(HashMap::new()),
            channel_rest:        RwLock::new(HashMap::new()),
            channel_soap:        RwLock::new(HashMap::new()),
            channel_amqp:        RwLock::new(HashMap::new()),
            channel_openapi:     RwLock::new(HashMap::new()),
            outgoing_rest:       RwLock::new(HashMap::new()),
            outgoing_soap:       RwLock::new(HashMap::new()),
            outgoing_amqp:       RwLock::new(HashMap::new()),
            outgoing_ftp:        RwLock::new(HashMap::new()),
            outgoing_sql:        RwLock::new(HashMap::new()),
            outgoing_odoo:       RwLock::new(HashMap::new()),
            outgoing_sap:        RwLock::new(HashMap::new()),
            cache_builtin:       RwLock::new(HashMap::new()),
            email_smtp:          RwLock::new(HashMap::new()),
            email_imap:          RwLock::new(HashMap::new()),
            scheduler:           RwLock::new(HashMap::new()),
            holiday_calendar:    RwLock::new(HashMap::new()),
            generic_connection:  RwLock::new(HashMap::new()),
            pubsub_topic:        RwLock::new(HashMap::new()),
            pubsub_permission:   RwLock::new(HashMap::new()),
            pubsub_subscription: RwLock::new(HashMap::new()),
            elastic_search:      RwLock::new(HashMap::new()),
            service:             RwLock::new(HashMap::new()),
        }
    }

    #[pyo3(signature = (path,))]
    fn load_yaml(&self, py: Python<'_>, path: &str) -> PyResult<()> {
        let contents = std::fs::read_to_string(path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("{}: {}", path, e)))?;
        let config: EnmasseConfig = serde_yaml::from_str(&contents)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("YAML parse: {}", e)))?;
        self.apply_enmasse_config(py, config)
    }

    #[pyo3(signature = (yaml_str,))]
    fn load_yaml_string(&self, py: Python<'_>, yaml_str: &str) -> PyResult<()> {
        let config: EnmasseConfig = serde_yaml::from_str(yaml_str)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("YAML parse: {}", e)))?;
        self.apply_enmasse_config(py, config)
    }

    #[pyo3(signature = (entity_type, name))]
    fn get<'py>(&self, py: Python<'py>, entity_type: &str, name: &str) -> PyResult<Option<Py<PyDict>>> {
        match entity_type {
            "security"            => self.get_security(py, name),
            "groups"              => self._get_group(py, name),
            "channel_rest"        => self._get_channel_rest(py, name),
            "channel_soap"        => self._get_channel_soap(py, name),
            "channel_amqp"        => self._get_channel_amqp(py, name),
            "channel_openapi"     => self._get_channel_openapi(py, name),
            "outgoing_rest"       => self._get_outgoing_rest(py, name),
            "outgoing_soap"       => self._get_outgoing_soap(py, name),
            "outgoing_amqp"       => self._get_outgoing_amqp(py, name),
            "outgoing_ftp"        => self._get_outgoing_ftp(py, name),
            "outgoing_sql"        => self._get_outgoing_sql(py, name),
            "outgoing_odoo"       => self._get_outgoing_odoo(py, name),
            "outgoing_sap"        => self._get_outgoing_sap(py, name),
            "cache_builtin"       => self._get_cache_builtin(py, name),
            "email_smtp"          => self._get_email_smtp(py, name),
            "email_imap"          => self._get_email_imap(py, name),
            "scheduler"           => self._get_scheduler(py, name),
            "holiday_calendar"    => self._get_holiday_calendar(py, name),
            "generic_connection"  => self._get_generic_connection(py, name),
            "pubsub_topic"        => self._get_pubsub_topic(py, name),
            "pubsub_permission"   => self._get_pubsub_permission(py, name),
            "pubsub_subscription" => self._get_pubsub_subscription(py, name),
            "elastic_search"      => self._get_elastic_search(py, name),
            "service"             => self._get_service(py, name),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", entity_type)
            )),
        }
    }

    #[pyo3(signature = (entity_type,))]
    fn get_list<'py>(&self, py: Python<'py>, entity_type: &str) -> PyResult<Py<PyList>> {
        match entity_type {
            "security"            => self.get_list_security(py),
            "groups"              => self._get_list_groups(py),
            "channel_rest"        => self._get_list_channel_rest(py),
            "channel_soap"        => self._get_list_channel_soap(py),
            "channel_amqp"        => self._get_list_channel_amqp(py),
            "channel_openapi"     => self._get_list_channel_openapi(py),
            "outgoing_rest"       => self._get_list_outgoing_rest(py),
            "outgoing_soap"       => self._get_list_outgoing_soap(py),
            "outgoing_amqp"       => self._get_list_outgoing_amqp(py),
            "outgoing_ftp"        => self._get_list_outgoing_ftp(py),
            "outgoing_sql"        => self._get_list_outgoing_sql(py),
            "outgoing_odoo"       => self._get_list_outgoing_odoo(py),
            "outgoing_sap"        => self._get_list_outgoing_sap(py),
            "cache_builtin"       => self._get_list_cache_builtin(py),
            "email_smtp"          => self._get_list_email_smtp(py),
            "email_imap"          => self._get_list_email_imap(py),
            "scheduler"           => self._get_list_scheduler(py),
            "holiday_calendar"    => self._get_list_holiday_calendar(py),
            "generic_connection"  => self._get_list_generic_connection(py),
            "pubsub_topic"        => self._get_list_pubsub_topic(py),
            "pubsub_permission"   => self._get_list_pubsub_permission(py),
            "pubsub_subscription" => self._get_list_pubsub_subscription(py),
            "elastic_search"      => self._get_list_elastic_search(py),
            "service"             => self._get_list_service(py),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", entity_type)
            )),
        }
    }

    #[pyo3(signature = (entity_type, name, data))]
    fn set<'py>(&self, py: Python<'py>, entity_type: &str, name: &str, data: &Bound<'py, PyDict>) -> PyResult<()> {
        match entity_type {
            "security"            => self.set_security(py, name, data),
            "groups"              => self._set_group(py, name, data),
            "channel_rest"        => self._set_channel_rest(py, name, data),
            "channel_soap"        => self._set_channel_soap(py, name, data),
            "channel_amqp"        => self._set_channel_amqp(py, name, data),
            "channel_openapi"     => self._set_channel_openapi(py, name, data),
            "outgoing_rest"       => self._set_outgoing_rest(py, name, data),
            "outgoing_soap"       => self._set_outgoing_soap(py, name, data),
            "outgoing_amqp"       => self._set_outgoing_amqp(py, name, data),
            "outgoing_ftp"        => self._set_outgoing_ftp(py, name, data),
            "outgoing_sql"        => self._set_outgoing_sql(py, name, data),
            "outgoing_odoo"       => self._set_outgoing_odoo(py, name, data),
            "outgoing_sap"        => self._set_outgoing_sap(py, name, data),
            "cache_builtin"       => self._set_cache_builtin(py, name, data),
            "email_smtp"          => self._set_email_smtp(py, name, data),
            "email_imap"          => self._set_email_imap(py, name, data),
            "scheduler"           => self._set_scheduler(py, name, data),
            "holiday_calendar"    => self._set_holiday_calendar(py, name, data),
            "generic_connection"  => self._set_generic_connection(py, name, data),
            "pubsub_topic"        => self._set_pubsub_topic(py, name, data),
            "pubsub_permission"   => self._set_pubsub_permission(py, name, data),
            "pubsub_subscription" => self._set_pubsub_subscription(py, name, data),
            "elastic_search"      => self._set_elastic_search(py, name, data),
            "service"             => self._set_service(py, name, data),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", entity_type)
            )),
        }
    }

    #[pyo3(signature = (entity_type, name))]
    fn delete(&self, entity_type: &str, name: &str) -> PyResult<bool> {
        match entity_type {
            "security"            => self.delete_security(name),
            "groups"              => self._delete_group(name),
            "channel_rest"        => self._delete_channel_rest(name),
            "channel_soap"        => self._delete_channel_soap(name),
            "channel_amqp"        => self._delete_channel_amqp(name),
            "channel_openapi"     => self._delete_channel_openapi(name),
            "outgoing_rest"       => self._delete_outgoing_rest(name),
            "outgoing_soap"       => self._delete_outgoing_soap(name),
            "outgoing_amqp"       => self._delete_outgoing_amqp(name),
            "outgoing_ftp"        => self._delete_outgoing_ftp(name),
            "outgoing_sql"        => self._delete_outgoing_sql(name),
            "outgoing_odoo"       => self._delete_outgoing_odoo(name),
            "outgoing_sap"        => self._delete_outgoing_sap(name),
            "cache_builtin"       => self._delete_cache_builtin(name),
            "email_smtp"          => self._delete_email_smtp(name),
            "email_imap"          => self._delete_email_imap(name),
            "scheduler"           => self._delete_scheduler(name),
            "holiday_calendar"    => self._delete_holiday_calendar(name),
            "generic_connection"  => self._delete_generic_connection(name),
            "pubsub_topic"        => self._delete_pubsub_topic(name),
            "pubsub_permission"   => self._delete_pubsub_permission(name),
            "pubsub_subscription" => self._delete_pubsub_subscription(name),
            "elastic_search"      => self._delete_elastic_search(name),
            "service"             => self._delete_service(name),
            _ => Err(pyo3::exceptions::PyValueError::new_err(
                format!("unknown entity type: {}", entity_type)
            )),
        }
    }

    #[pyo3(signature = ())]
    fn export_to_dict<'py>(&self, py: Python<'py>) -> PyResult<Py<PyDict>> {
        let out = PyDict::new(py);

        macro_rules! export_section {
            ($key:expr, $field:ident) => {{
                let store = self.$field.read()
                    .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
                if !store.is_empty() {
                    let list = PyList::empty(py);
                    for item in store.values() {
                        let d = struct_to_pydict(py, item)?;
                        let _ = list.append(d.bind(py));
                    }
                    let _ = out.set_item($key, list);
                }
            }};
        }

        // Security needs special handling for the tagged enum
        {
            let store = self.security.read()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
            if !store.is_empty() {
                let list = PyList::empty(py);
                for sec_def in store.values() {
                    let d = struct_to_pydict(py, sec_def)?;
                    let _ = list.append(d.bind(py));
                }
                let _ = out.set_item("security", list);
            }
        }

        export_section!("groups", groups);
        export_section!("channel_rest", channel_rest);
        export_section!("outgoing_rest", outgoing_rest);
        export_section!("outgoing_soap", outgoing_soap);
        export_section!("scheduler", scheduler);
        export_section!("holiday_calendar", holiday_calendar);
        export_section!("sql", outgoing_sql);
        export_section!("ldap", generic_connection);
        export_section!("cache", cache_builtin);
        export_section!("email_smtp", email_smtp);
        export_section!("email_imap", email_imap);
        export_section!("odoo", outgoing_odoo);
        export_section!("elastic_search", elastic_search);
        export_section!("pubsub_topic", pubsub_topic);
        export_section!("pubsub_permission", pubsub_permission);
        export_section!("pubsub_subscription", pubsub_subscription);
        export_section!("channel_openapi", channel_openapi);

        Ok(out.unbind())
    }

    fn get_scheduler_jobs_json(&self) -> String {
        let store = self.scheduler.read().unwrap();
        serde_json::to_string(&*store).unwrap_or_else(|_| "{}".to_string())
    }

    fn get_holiday_calendars_json(&self) -> String {
        let store = self.holiday_calendar.read().unwrap();
        serde_json::to_string(&*store).unwrap_or_else(|_| "{}".to_string())
    }
}

// ── non-PyO3 helpers ──

fn lock_err<T>(_: T) -> PyErr {
    pyo3::exceptions::PyRuntimeError::new_err("lock poisoned")
}

impl ConfigStore {

    fn apply_enmasse_config(&self, _py: Python<'_>, config: EnmasseConfig) -> PyResult<()> {

        // Security
        {
            let mut store = self.security.write().map_err(lock_err)?;
            for sec in config.security {
                store.insert(sec.name().to_string(), sec);
            }
        }

        // Groups
        {
            let mut store = self.groups.write().map_err(lock_err)?;
            for grp in config.groups {
                store.insert(grp.name.clone(), grp);
            }
        }

        // Channel REST
        {
            let mut store = self.channel_rest.write().map_err(lock_err)?;
            for ch in config.channel_rest {
                store.insert(ch.name.clone(), ch);
            }
        }

        // Outgoing REST
        {
            let mut store = self.outgoing_rest.write().map_err(lock_err)?;
            for out in config.outgoing_rest {
                store.insert(out.name.clone(), out);
            }
        }

        // Outgoing SOAP (from both keys)
        {
            let mut store = self.outgoing_soap.write().map_err(lock_err)?;
            for out in config.outgoing_soap {
                store.insert(out.name.clone(), out);
            }
            for out in config.outgoing_soap_alias {
                store.insert(out.name.clone(), out);
            }
        }

        // Scheduler
        {
            let mut store = self.scheduler.write().map_err(lock_err)?;
            for job in config.scheduler {
                store.insert(job.name.clone(), job);
            }
        }

        // Holiday calendars
        {
            let mut store = self.holiday_calendar.write().map_err(lock_err)?;
            for cal in config.holiday_calendar {
                store.insert(cal.name.clone(), cal);
            }
        }

        // SQL
        {
            let mut store = self.outgoing_sql.write().map_err(lock_err)?;
            for sql in config.sql {
                store.insert(sql.name.clone(), sql);
            }
        }

        // Generic connections (LDAP, Jira, Confluence, Microsoft 365, and the generic key)
        {
            let mut store = self.generic_connection.write().map_err(lock_err)?;

            let mut insert_with_type = |mut conn: GenericConnection, default_type: &str| {
                if conn.type_.is_empty() {
                    conn.type_ = default_type.to_string();
                }
                store.insert(conn.name.clone(), conn);
            };

            for conn in config.ldap {
                insert_with_type(conn, "outconn-ldap");
            }
            for conn in config.confluence {
                insert_with_type(conn, "cloud-confluence");
            }
            for conn in config.jira {
                insert_with_type(conn, "cloud-jira");
            }
            for conn in config.microsoft_365 {
                insert_with_type(conn, "cloud-microsoft-365");
            }
            for conn in config.zato_generic_connection {
                store.insert(conn.name.clone(), conn);
            }
        }

        // Cache
        {
            let mut store = self.cache_builtin.write().map_err(lock_err)?;
            for c in config.cache {
                store.insert(c.name.clone(), c);
            }
        }

        // Email
        {
            let mut store = self.email_smtp.write().map_err(lock_err)?;
            for e in config.email_smtp {
                store.insert(e.name.clone(), e);
            }
        }
        {
            let mut store = self.email_imap.write().map_err(lock_err)?;
            for e in config.email_imap {
                store.insert(e.name.clone(), e);
            }
        }

        // Odoo
        {
            let mut store = self.outgoing_odoo.write().map_err(lock_err)?;
            for o in config.odoo {
                store.insert(o.name.clone(), o);
            }
        }

        // ElasticSearch
        {
            let mut store = self.elastic_search.write().map_err(lock_err)?;
            for e in config.elastic_search {
                store.insert(e.name.clone(), e);
            }
        }

        // Pub/Sub
        {
            let mut store = self.pubsub_topic.write().map_err(lock_err)?;
            for t in config.pubsub_topic {
                store.insert(t.name.clone(), t);
            }
        }
        {
            let mut store = self.pubsub_permission.write().map_err(lock_err)?;
            for p in config.pubsub_permission {
                store.insert(p.id.clone(), p);
            }
        }
        {
            let mut store = self.pubsub_subscription.write().map_err(lock_err)?;
            for s in config.pubsub_subscription {
                store.insert(s.id.clone(), s);
            }
        }

        // Channel OpenAPI
        {
            let mut store = self.channel_openapi.write().map_err(lock_err)?;
            for ch in config.channel_openapi {
                store.insert(ch.name.clone(), ch);
            }
        }

        Ok(())
    }

    fn get_security<'py>(&self, py: Python<'py>, name: &str) -> PyResult<Option<Py<PyDict>>> {
        let store = self.security.read()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        match store.get(name) {
            Some(sec) => {
                let d = struct_to_pydict(py, sec)?;
                let bound = d.bind(py);
                let _ = bound.set_item("sec_type", PyString::new(py, sec.sec_type()));
                Ok(Some(d))
            }
            None => Ok(None),
        }
    }

    fn get_list_security<'py>(&self, py: Python<'py>) -> PyResult<Py<PyList>> {
        let store = self.security.read()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        let list = PyList::empty(py);
        for sec in store.values() {
            let d = struct_to_pydict(py, sec)?;
            let bound = d.bind(py);
            let _ = bound.set_item("sec_type", PyString::new(py, sec.sec_type()));
            let _ = list.append(bound);
        }
        Ok(list.unbind())
    }

    fn set_security<'py>(&self, py: Python<'py>, name: &str, data: &Bound<'py, PyDict>) -> PyResult<()> {
        let sec_def: SecurityDef = pydict_to_struct(py, data)?;
        let mut store = self.security.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        store.insert(name.to_string(), sec_def);
        Ok(())
    }

    fn delete_security(&self, name: &str) -> PyResult<bool> {
        let mut store = self.security.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("lock poisoned"))?;
        Ok(store.remove(name).is_some())
    }

    pub fn get_scheduler_jobs_raw(&self) -> HashMap<String, crate::models::SchedulerJob> {
        let store = self.scheduler.read().unwrap();
        store.clone()
    }

    pub fn get_scheduler_lock(&self) -> &RwLock<HashMap<String, crate::models::SchedulerJob>> {
        &self.scheduler
    }

    pub fn get_holiday_calendars_raw(&self) -> HashMap<String, crate::models::HolidayCalendar> {
        let store = self.holiday_calendar.read().unwrap();
        store.clone()
    }

}
