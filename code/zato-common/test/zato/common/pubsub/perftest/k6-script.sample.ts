import { ZatoPubSubRESTAPIClient } from "./zatoPubSubRESTAPI.ts";

const baseUrl = "<BASE_URL>";
const zatoPubSubRESTAPIClient = new ZatoPubSubRESTAPIClient({ baseUrl });

export default function () {
  let topicName, postPubsubTopicTopicNameBody;

  /**
   * Publish a message to a topic
   */
  topicName = "orders.processed";
  postPubsubTopicTopicNameBody = {
    data: "Order #12345 has been processed",
    priority: 4180262486356951,
    expiration: 852910925327970,
    correl_id: "order-12345-notification",
    in_reply_to: "chatter",
    ext_client_id: "pace",
    pub_time: "knife",
  };

  const postPubsubTopicTopicNameResponseData =
    zatoPubSubRESTAPIClient.postPubsubTopicTopicName(
      topicName,
      postPubsubTopicTopicNameBody,
    );

  /**
   * Subscribe to a topic
   */
  topicName = "orders.processed";

  const postPubsubSubscribeTopicTopicNameResponseData =
    zatoPubSubRESTAPIClient.postPubsubSubscribeTopicTopicName(topicName);

  /**
   * Unsubscribe from a topic
   */
  topicName = "orders.processed";

  const postPubsubUnsubscribeTopicTopicNameResponseData =
    zatoPubSubRESTAPIClient.postPubsubUnsubscribeTopicTopicName(topicName);

  /**
   * Retrieve messages from subscribed topics
   */

  const postPubsubMessagesGetResponseData =
    zatoPubSubRESTAPIClient.postPubsubMessagesGet();
}
