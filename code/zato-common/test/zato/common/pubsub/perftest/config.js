import encoding from 'k6/encoding';

export const BASE_URL = __ENV.Zato_Test_PubSub_OpenAPI_URL;
export const USERNAME = __ENV.Zato_Test_PubSub_OpenAPI_Username;
export const PASSWORD = __ENV.Zato_Test_PubSub_OpenAPI_Password;
export const MAX_TOPICS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Max_Topics);
export const VUS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_VUs);
export const ITERATIONS_PER_VU = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Iterations_Per_VU);
export const NEEDS_DETAILS = __ENV.Zato_Needs_Details === 'true';

if (!BASE_URL) {
  throw new Error('Environment variable Zato_Test_PubSub_OpenAPI_URL is not set');
}
if (isNaN(MAX_TOPICS)) {
  throw new Error('Environment variable Zato_Test_PubSub_OpenAPI_Max_Topics is not set or invalid');
}
if (isNaN(VUS)) {
  throw new Error('Environment variable Zato_Test_PubSub_OpenAPI_VUs is not set or invalid');
}
if (isNaN(ITERATIONS_PER_VU)) {
  throw new Error('Environment variable Zato_Test_PubSub_OpenAPI_Iterations_Per_VU is not set or invalid');
}

export const auth = encoding.b64encode(`${USERNAME}:${PASSWORD}`);

export const headers = {
  'Authorization': `Basic ${auth}`,
  'Content-Type': 'application/json',
};

export function getTopicName(vu) {
  const topicIndex = ((vu - 1) % MAX_TOPICS) + 1;
  return `demo.${topicIndex}`;
}

export function getUserCredentials(vu) {
  return {
    username: USERNAME,
    password: PASSWORD,
    auth: auth,
    headers: headers
  };
}
