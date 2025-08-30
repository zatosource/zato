import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, headers, getTopicName } from './config.js';

export let options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '3m', target: 25 },
    { duration: '2m', target: 25 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.1'],
    'checks{operation:subscribe}': ['rate>0.95'],
    'checks{operation:publish}': ['rate>0.95'],
    'checks{operation:pull}': ['rate>0.90'],
    'checks{operation:unsubscribe}': ['rate>0.95'],
  },
};

export default function() {
  const topicName = getTopicName(__VU);

  // Step 1: Subscribe to topic
  let subscribeResponse = http.post(
    `${BASE_URL}/pubsub/subscribe/topic/${topicName}`,
    null,
    { headers, tags: { operation: 'subscribe' } }
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

  // Step 2: Publish messages to topic
  const messageCount = Math.floor(Math.random() * 5) + 3;
  let publishedMessages = 0;

  for (let i = 0; i < messageCount; i++) {
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
      correl_id: `workflow-${__VU}-${__ITER}-${i}`,
    };

    let publishResponse = http.post(
      `${BASE_URL}/pubsub/topic/${topicName}`,
      JSON.stringify(payload),
      { headers, tags: { operation: 'publish' } }
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
      max_messages: messageCount,
      max_len: 2000000,
    };

    let pullResponse = http.post(
      `${BASE_URL}/pubsub/messages/get`,
      JSON.stringify(pullPayload),
      { headers, tags: { operation: 'pull' } }
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
        }
      } catch (e) {
        console.error(`Failed to parse pull response for VU ${__VU}: ${e}`);
      }
    }

    pullAttempts++;
    sleep(0.1);
  }

  sleep(0.1);

  // Step 4: Unsubscribe from topic
  let unsubscribeResponse = http.post(
    `${BASE_URL}/pubsub/unsubscribe/topic/${topicName}`,
    null,
    { headers, tags: { operation: 'unsubscribe' } }
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

  console.log(`VU ${__VU} workflow: published ${publishedMessages}, pulled ${totalPulledMessages} messages`);

  sleep(0.2);
}
