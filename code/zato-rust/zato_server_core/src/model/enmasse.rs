//! Top-level enmasse configuration that aggregates all object types into a single deployable unit.

use serde::{Deserialize, Serialize};
use super::security::{SecurityDef, SecurityGroup};
use super::channels::{ChannelRest, ChannelOpenApi};
use super::outgoing::{OutgoingRest, OutgoingSoap, OutgoingSql, OutgoingOdoo};
use super::scheduler::{SchedulerJob, HolidayCalendar};
use super::pubsub::{PubSubTopic, PubSubPermission, PubSubSubscription};
use super::services::ElasticSearchDef;
use super::cache::CacheBuiltinDef;
use super::email::{EmailSmtp, EmailImap};
use super::generic::GenericConnection;

/// Root of an enmasse YAML document - each field corresponds to an object category
/// that Zato imports as a batch.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EnmasseConfig {
    #[serde(default)]
    pub security: Vec<SecurityDef>,
    #[serde(default)]
    pub groups: Vec<SecurityGroup>,
    #[serde(default)]
    pub channel_rest: Vec<ChannelRest>,
    #[serde(default)]
    pub outgoing_rest: Vec<OutgoingRest>,
    #[serde(default)]
    pub outgoing_soap: Vec<OutgoingSoap>,
    #[serde(default, alias = "outconn_soap")]
    pub outgoing_soap_alias: Vec<OutgoingSoap>,
    #[serde(default)]
    pub scheduler: Vec<SchedulerJob>,
    #[serde(default)]
    pub holiday_calendar: Vec<HolidayCalendar>,
    #[serde(default, alias = "outconn_sql")]
    pub sql: Vec<OutgoingSql>,
    #[serde(default, alias = "outgoing_ldap")]
    pub ldap: Vec<GenericConnection>,
    #[serde(default)]
    pub cache: Vec<CacheBuiltinDef>,
    #[serde(default)]
    pub email_smtp: Vec<EmailSmtp>,
    #[serde(default)]
    pub email_imap: Vec<EmailImap>,
    #[serde(default)]
    pub confluence: Vec<GenericConnection>,
    #[serde(default)]
    pub jira: Vec<GenericConnection>,
    #[serde(default)]
    pub microsoft_365: Vec<GenericConnection>,
    #[serde(default)]
    pub odoo: Vec<OutgoingOdoo>,
    #[serde(default)]
    pub elastic_search: Vec<ElasticSearchDef>,
    #[serde(default)]
    pub pubsub_topic: Vec<PubSubTopic>,
    #[serde(default)]
    pub pubsub_permission: Vec<PubSubPermission>,
    #[serde(default)]
    pub pubsub_subscription: Vec<PubSubSubscription>,
    #[serde(default)]
    pub channel_openapi: Vec<ChannelOpenApi>,
    #[serde(default)]
    pub zato_generic_connection: Vec<GenericConnection>,
}
