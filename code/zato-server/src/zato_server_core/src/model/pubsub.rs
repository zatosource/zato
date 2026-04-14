use serde::{Deserialize, Serialize};
use super::defaults::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubTopic {
    #[serde(default = "next_id")]
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub description: Option<String>,
    #[serde(default = "default_true")]
    pub is_active: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubPermission {
    #[serde(default = "next_id")]
    pub id: String,
    pub security: String,
    #[serde(default)]
    pub sec_base_id: String,
    #[serde(default)]
    pub pub_: Vec<String>,
    #[serde(rename = "pub", default)]
    pub pub_topics: Vec<String>,
    #[serde(rename = "sub", default)]
    pub sub_topics: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PubSubSubscription {
    #[serde(default = "next_id")]
    pub id: String,
    #[serde(default)]
    pub security: String,
    #[serde(default)]
    pub sub_key: String,
    #[serde(default)]
    pub sec_base_id: String,
    #[serde(default)]
    pub sec_name: String,
    #[serde(default)]
    pub username: String,
    #[serde(default)]
    pub delivery_type: String,
    #[serde(default)]
    pub push_type: String,
    #[serde(default)]
    pub created: String,
    #[serde(default = "default_true")]
    pub is_delivery_active: bool,
    #[serde(default = "default_true")]
    pub is_pub_active: bool,
    #[serde(default)]
    pub topic_list: Vec<String>,
    #[serde(default)]
    pub topic_name_list: Vec<serde_yaml::Value>,
    #[serde(default)]
    pub topic_link_list: String,
    #[serde(default)]
    pub push_rest_endpoint: Option<String>,
    #[serde(default)]
    pub rest_push_endpoint_id: Option<String>,
    #[serde(default)]
    pub push_service_name: Option<String>,
    #[serde(default)]
    pub max_retry_time: Option<String>,
}
