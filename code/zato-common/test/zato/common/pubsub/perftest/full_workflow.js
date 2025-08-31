import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, getUserCredentials, getTopicName, VUS, ITERATIONS_PER_VU, NEEDS_DETAILS } from './config.js';

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
    'http_req_duration{operation:unsubscribe}': ['p(100)<1200000'],
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


    const subscribeResponse = http.post(`${BASE_URL}/pubsub/subscribe/topic/${topicName}`, '', {
      headers: userCreds.headers,
      tags: { operation: 'subscribe' }
    });

    check(subscribeResponse, {
      'subscribe status is 200': (r) => r.status === 200,
      'subscribe is_ok true': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.is_ok === true;
        } catch (e) {
          return false;
        }
      },
    }, { operation: 'subscribe' });

    if (subscribeResponse.status !== 200) {
      console.error(`Subscribe failed for VU ${vuId}: ${subscribeResponse.status}`);
    }
  }

  // Step 2: Publish messages to topic
  // const messageCount = Math.floor(Math.random() * 5) + 3;
  const messageCount = 1;
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
    if (NEEDS_DETAILS) {
      console.log(`VU ${vuId} publishing full payload: ${JSON.stringify(payload)}`);
    }

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
            if (NEEDS_DETAILS) {
              console.log(`VU ${vuId} received full message: ${JSON.stringify(msg)}`);
            }
            const correlId = msg.meta ? msg.meta.correl_id : msg.correl_id;
            if (correlId && publishedIds[vuId].has(correlId)) {
              receivedIds[vuId].add(correlId);
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

    // Final summary for this VU
    const totalPublished = publishedIds[vuId].size;
    const totalReceived = receivedIds[vuId].size;
    const missing = totalPublished - totalReceived;

    if (missing > 0) {
      console.error(`VU ${vuId} FINAL: ${missing} messages never received out of ${totalPublished} published`);
    } else {
      console.log(`VU ${vuId} FINAL: All ${totalPublished} messages received successfully`);
    }

    // Add to global tracking
    if (!globalThis.finalResults) {
      globalThis.finalResults = { totalPublished: 0, totalReceived: 0 };
    }
    globalThis.finalResults.totalPublished += totalPublished;
    globalThis.finalResults.totalReceived += totalReceived;

    // Check if this is the last VU to finish
    if (!globalThis.finishedVUs) {
      globalThis.finishedVUs = 0;
    }
    globalThis.finishedVUs++;

    if (globalThis.finishedVUs === VUS) {
      const globalMissing = globalThis.finalResults.totalPublished - globalThis.finalResults.totalReceived;
      if (globalMissing > 0) {
        console.error(`GLOBAL FINAL: ${globalMissing} messages never received out of ${globalThis.finalResults.totalPublished} published across all VUs`);
      } else {
        console.log(`GLOBAL FINAL: All ${globalThis.finalResults.totalPublished} messages received successfully across all VUs`);
      }
    }
  }

  const publishedCount = publishedIds[vuId].size;
  const receivedCount = receivedIds[vuId].size;
  const missingCount = publishedCount - receivedCount;

  console.log(`VU ${vuId} iteration ${__ITER}: published ${publishedMessages} this iter, total published ${publishedCount}, total received ${receivedCount}, missing ${missingCount}`);

  sleep(0.2);
}
