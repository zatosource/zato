import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, VUS, ITERATIONS_PER_VU, getUserCredentials, getTopicName } from './config.js';

export let options = {
  scenarios: {
    default: {
      executor: 'per-vu-iterations',
      vus: VUS,
      iterations: ITERATIONS_PER_VU,
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate==0'],
    'checks{operation:subscribe}': ['rate==1'],
    'checks{operation:publish}': ['rate==1'],
    'checks{operation:pull}': ['rate==1'],
    'checks{operation:unsubscribe}': ['rate==1'],
  },
};

// Per-VU message tracking
const publishedIds = {};
const receivedIds = {};

export default function() {
  const topicName = getTopicName(__VU);
  const userCreds = getUserCredentials(__VU);
  const vuId = __VU;

  // Per-VU tracking of published and received message IDs
  if (!publishedIds[vuId]) {
    publishedIds[vuId] = new Set();
  }
  if (!receivedIds[vuId]) {
    receivedIds[vuId] = new Set();
  }

  if (__ITER === 0) {

    // Step 1: Subscribe to topic (first iteration only)
    let subscribeResponse = http.post(
      `${BASE_URL}/pubsub/subscribe/topic/${topicName}`,
      null,
      { headers: userCreds.headers, tags: { operation: 'subscribe' } }
    );

    check(subscribeResponse, {
      'subscribe status is 200': (r) => r.status === 200,
      'subscribe is_ok true': (r) => {
        try {
          return JSON.parse(r.body).is_ok === true;
        } catch (e) {
          return false;
        }
      },
    }, { operation: 'subscribe' });

    if (subscribeResponse.status !== 200) {
      console.error(`Subscribe failed for VU ${__VU}: ${subscribeResponse.status}`);
      return;
    }

    sleep(0.1);
  }

  // Step 2: Publish messages to topic
  const messageCount = Math.floor(Math.random() * 5) + 3;
  let publishedMessages = 0;

  for (let i = 0; i < messageCount; i++) {
    const correlId = `vu${vuId}-iter${__ITER}-msg${i}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const payload = {
      data: {
        workflow_test: true,
        message_number: i + 1,
        total_messages: messageCount,
        vu: __VU,
        iteration: __ITER,
        timestamp: new Date().toISOString(),
      },
      priority: Math.floor(Math.random() * 10),
      expiration: 1800,
      correl_id: correlId,
    };

    // Track published correlation ID
    publishedIds[vuId].add(correlId);
    console.log(`VU ${vuId} publishing full payload: ${JSON.stringify(payload)}`);

    let publishResponse = http.post(
      `${BASE_URL}/pubsub/topic/${topicName}`,
      JSON.stringify(payload),
      { headers: userCreds.headers, tags: { operation: 'publish' } }
    );

    check(publishResponse, {
      'publish status is 200': (r) => r.status === 200,
      'publish has msg_id': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.msg_id && body.msg_id.startsWith('zpsm.');
        } catch (e) {
          return false;
        }
      },
    }, { operation: 'publish' });

    if (publishResponse.status === 200) {
      publishedMessages++;
    }

    sleep(0.05);
  }

  sleep(0.2);

  // Step 3: Pull messages
  let totalPulledMessages = 0;
  let pullAttempts = 0;
  const maxPullAttempts = 5;

  while (totalPulledMessages < publishedMessages && pullAttempts < maxPullAttempts) {
    const pullPayload = {
      max_messages: 100,
      max_len: 5000000,
    };

    let pullResponse = http.post(
      `${BASE_URL}/pubsub/messages/get`,
      JSON.stringify(pullPayload),
      { headers: userCreds.headers, tags: { operation: 'pull' } }
    );

    check(pullResponse, {
      'pull status is 200': (r) => r.status === 200,
      'pull is_ok true': (r) => {
        try {
          return JSON.parse(r.body).is_ok === true;
        } catch (e) {
          return false;
        }
      },
      'pull has messages array': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.messages);
        } catch (e) {
          return false;
        }
      },
    }, { operation: 'pull' });

    if (pullResponse.status === 200) {
      try {
        const body = JSON.parse(pullResponse.body);
        if (body.messages && Array.isArray(body.messages)) {
          totalPulledMessages += body.messages.length;
          
          // Track received messages by correlation ID
          for (const msg of body.messages) {
            console.log(`VU ${vuId} received full message: ${JSON.stringify(msg)}`);
            if (msg.correl_id && publishedIds[vuId].has(msg.correl_id)) {
              receivedIds[vuId].add(msg.correl_id);
            }
          }
        }
      } catch (e) {
        console.error(`Failed to parse pull response for VU ${__VU}: ${e}`);
      }
    }

    pullAttempts++;
    sleep(0.1);
  }

  sleep(0.1);

  if (__ITER === ITERATIONS_PER_VU - 1) {
    // Step 4: Unsubscribe from topic (last iteration only)
    let unsubscribeResponse = http.post(
      `${BASE_URL}/pubsub/unsubscribe/topic/${topicName}`,
      null,
      { headers: userCreds.headers, tags: { operation: 'unsubscribe' } }
    );

    check(unsubscribeResponse, {
      'unsubscribe status is 200': (r) => r.status === 200,
      'unsubscribe is_ok true': (r) => {
        try {
          return JSON.parse(r.body).is_ok === true;
        } catch (e) {
          return false;
        }
      },
    }, { operation: 'unsubscribe' });
  }

  const publishedCount = publishedIds[vuId].size;
  const receivedCount = receivedIds[vuId].size;
  const missingCount = publishedCount - receivedCount;
  
  console.log(`VU ${vuId} iteration ${__ITER}: published ${publishedMessages} this iter, total published ${publishedCount}, total received ${receivedCount}, missing ${missingCount}`);

  if (__ITER === ITERATIONS_PER_VU - 1 && missingCount > 0) {
    console.error(`VU ${vuId} FINAL: ${missingCount} messages never received out of ${publishedCount} published`);
  }

  sleep(0.2);
}
