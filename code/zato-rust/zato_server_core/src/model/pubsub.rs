//! Publish/subscribe messaging - topics, permissions and subscriptions.

use serde::{Deserialize, Serialize};
use super::defaults::{next_id, default_true};

/// A named pub/sub topic that messages are published to.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubTopic {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default = "default_true")]
    pub is_active: bool,
}

/// Links a security definition to its pub/sub publish and subscribe permissions.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubPermission {
    #[serde(default = "next_id")]
    pub id: String,
    /// Name of the security definition this permission applies to.
    pub security: String,
    /// Resolved `SecurityBase` ID for the security definition.
    #[serde(default)]
    pub sec_base_id: String,
    /// Topic names this security definition may publish to.
    #[serde(alias = "pub", default)]
    pub pub_topics: Vec<String>,
    /// Topic names this security definition may subscribe to.
    #[serde(alias = "sub", default)]
    pub sub_topics: Vec<String>,
}

/// A subscription that delivers messages from topics to an endpoint.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubSubscription {
    #[serde(default = "next_id")]
    pub id: String,
    #[serde(default)]
    pub security: String,
    #[serde(default)]
    pub sub_key: String,
    /// Resolved `SecurityBase` ID.
    #[serde(default)]
    pub sec_base_id: String,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub delivery_type: String,
    /// Delivery mechanism - derived from `push_rest_endpoint` vs `push_service`.
    #[serde(default)]
    pub push_type: String,
    #[serde(default)]
    pub created: String,
    #[serde(default = "default_true")]
    pub is_delivery_active: bool,
    #[serde(default = "default_true")]
    pub is_pub_active: bool,
    /// Topic names this subscription covers (from YAML input).
    #[serde(default)]
    pub topic_list: Vec<String>,
    /// Topic names resolved from the DB during export (runtime-populated).
    #[serde(default)]
    pub topic_name_list: Vec<String>,
    /// Comma-separated topic links built at runtime for API responses.
    #[serde(default)]
    pub topic_link_list: String,
    /// Name of the REST outgoing connection used for push delivery (resolved to `rest_push_endpoint_id`).
    #[serde(default)]
    pub push_rest_endpoint: String,
    /// Resolved ID of the REST outgoing connection for push delivery.
    #[serde(default)]
    pub rest_push_endpoint_id: String,
    /// Name of the Zato service used for push delivery.
    #[serde(default)]
    pub push_service: String,
    /// Maximum time in seconds before delivery retries are abandoned. Stored in opaque, not yet wired to runtime.
    #[serde(default)]
    pub max_retry_time: String,
}
