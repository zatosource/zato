import encoding from 'k6/encoding';

export const BASE_URL = __ENV.Zato_Test_PubSub_OpenAPI_URL;
export const USERNAME = __ENV.Zato_Test_PubSub_OpenAPI_Username;
export const PASSWORD = __ENV.Zato_Test_PubSub_OpenAPI_Password;
export const MAX_TOPICS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Max_Topics);
export const VUS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_VUs);
export const ITERATIONS_PER_VU = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Iterations_Per_VU);
export const NEEDS_DETAILS = __ENV.Zato_Needs_Details === 'true';
export const PULL_MAX_MESSAGES = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Pull_Max_Messages) || 1000;
export const PULL_MAX_EMPTY_ATTEMPTS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Pull_Max_Empty_Attempts) || 100;
export const WAIT_BEFORE_PULL_SECONDS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Wait_Before_Pull_Seconds) || 2;
export const REQUEST_RATE = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Request_Rate) || 10;
export const PRE_ALLOCATED_VUS = parseInt(__ENV.Zato_Test_PubSub_OpenAPI_Pre_Allocated_VUs) || 10;
export const HTTP_TIMEOUT = __ENV.Zato_Test_PubSub_OpenAPI_HTTP_Timeout || '1000ms';

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

export function getTopicNames() {
  const topics = [];
  for (let i = 1; i <= MAX_TOPICS; i++) {
    topics.push(`demo.${i}`);
  }
  return topics;
}

export function getUserCredentials(vuId) {
  const userNum = ((vuId - 1) % MAX_TOPICS) + 1;
  const username = `user.${userNum}`;
  const password = `password.${userNum}`;
  const vuAuth = encoding.b64encode(`${username}:${password}`);

  return {
    headers: {
      'Authorization': `Basic ${vuAuth}`,
      'Content-Type': 'application/json',
    }
  };
}
