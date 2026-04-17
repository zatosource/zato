use std::collections::HashMap;
use std::sync::RwLock;

use pyo3::prelude::*;

use crate::model::*;

#[pyclass]
#[derive(Default)]
pub struct ConfigStore {
    pub(super) security:            RwLock<HashMap<String, SecurityDef>>,
    pub(super) groups:              RwLock<HashMap<String, SecurityGroup>>,
    pub(super) channel_rest:        RwLock<HashMap<String, ChannelRest>>,
    pub(super) channel_soap:        RwLock<HashMap<String, ChannelSoap>>,
    pub(super) channel_amqp:        RwLock<HashMap<String, ChannelAmqp>>,
    pub(super) channel_openapi:     RwLock<HashMap<String, ChannelOpenApi>>,
    pub(super) outgoing_rest:       RwLock<HashMap<String, OutgoingRest>>,
    pub(super) outgoing_soap:       RwLock<HashMap<String, OutgoingSoap>>,
    pub(super) outgoing_amqp:       RwLock<HashMap<String, OutgoingAmqp>>,
    pub(super) outgoing_ftp:        RwLock<HashMap<String, OutgoingFtp>>,
    pub(super) outgoing_sql:        RwLock<HashMap<String, OutgoingSql>>,
    pub(super) outgoing_odoo:       RwLock<HashMap<String, OutgoingOdoo>>,
    pub(super) outgoing_sap:        RwLock<HashMap<String, OutgoingSap>>,
    pub(super) cache_builtin:       RwLock<HashMap<String, CacheBuiltinDef>>,
    pub(super) email_smtp:          RwLock<HashMap<String, EmailSmtp>>,
    pub(super) email_imap:          RwLock<HashMap<String, EmailImap>>,
    pub(super) scheduler:           RwLock<HashMap<String, SchedulerJob>>,
    pub(super) holiday_calendar:    RwLock<HashMap<String, HolidayCalendar>>,
    pub(super) generic_connection:  RwLock<HashMap<String, GenericConnection>>,
    pub(super) pubsub_topic:        RwLock<HashMap<String, PubSubTopic>>,
    pub(super) pubsub_permission:   RwLock<HashMap<String, PubSubPermission>>,
    pub(super) pubsub_subscription: RwLock<HashMap<String, PubSubSubscription>>,
    pub(super) elastic_search:      RwLock<HashMap<String, ElasticSearchDef>>,
    pub(super) service:             RwLock<HashMap<String, ServiceInfo>>,

    /// username -> security def name (for O(1) basic auth credential lookup)
    pub(super) security_by_username: RwLock<HashMap<String, String>>,
    /// api key value -> security def name (for O(1) API key credential lookup)
    pub(super) security_by_apikey_value: RwLock<HashMap<String, String>>,
}

#[pymethods]
impl ConfigStore {
    #[new]
    #[pyo3(signature = ())]
    fn new() -> Self {
        Self::default()
    }
}
