import encoding from 'k6/encoding';

export const BASE_URL = __ENV.Zato_Test_PubSub_OpenAPI_URL;
export const USERNAME = __ENV.Zato_Test_PubSub_OpenAPI_Username;
export const PASSWORD = __ENV.Zato_Test_PubSub_OpenAPI_Password;
export const MAX_TOPICS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Max_Topics);

export const auth = encoding.b64encode(`${USERNAME}:${PASSWORD}`);

export const headers = {
  'Authorization': `Basic ${auth}`,
  'Content-Type': 'application/json',
};

export function getTopicName(vu) {
  const topicIndex = ((vu - 1) % MAX_TOPICS) + 1;
  return `demo.${topicIndex}`;
}
