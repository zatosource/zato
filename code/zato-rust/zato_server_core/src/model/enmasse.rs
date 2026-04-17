use serde::{Deserialize, Serialize};
use super::*;

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
