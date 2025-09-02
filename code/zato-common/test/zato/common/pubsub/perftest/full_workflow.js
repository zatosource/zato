import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, getUserCredentials, getTopicNames, VUS, ITERATIONS_PER_VU, PULL_MAX_MESSAGES, PULL_MAX_EMPTY_ATTEMPTS, WAIT_BEFORE_PULL_SECONDS, REQUEST_RATE, PRE_ALLOCATED_VUS } from './config.js';

export let options = {
  scenarios: {
    default: {
      executor: 'ramping-arrival-rate',
      startRate: REQUEST_RATE,
      timeUnit: '1s',
      preAllocatedVUs: Math.min(VUS, PRE_ALLOCATED_VUS),
      maxVUs: VUS * 3,
      stages: [
        { duration: '30s', target: REQUEST_RATE },
        { duration: `${Math.floor((VUS * ITERATIONS_PER_VU) / REQUEST_RATE)}s`, target: REQUEST_RATE },
        { duration: '30s', target: 0 },
      ],
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate==0'],
    'checks{operation:publish}': ['rate==1'],
    'checks{operation:pull}': ['rate==1'],
  },
};

function publish(topicName, userCreds) {
  const payload = {
    data: {
      message: `Message from VU ${__VU}, iteration ${__ITER}`,
      timestamp: new Date().toISOString(),
      vu: __VU,
      iteration: __ITER,
    },
    priority: 5,
    expiration: 3600 * 24 * 365,
  };

  const startTime = Date.now();
  let publishResponse = http.post(
    `${BASE_URL}/pubsub/topic/${topicName}`,
    JSON.stringify(payload),
    { headers: userCreds.headers, tags: { operation: 'publish' } }
  );
  const duration = Date.now() - startTime;

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

  if (publishResponse.status !== 200) {
    console.error(`Publish failed for VU ${__VU}:`);
    console.error(`  Status: ${publishResponse.status}`);
    console.error(`  Duration: ${duration}ms`);
    console.error(`  Topic: ${topicName}`);
    console.error(`  Error: ${publishResponse.error || 'none'}`);
    console.error(`  Error Code: ${publishResponse.error_code || 'none'}`);
    console.error(`  Body: ${publishResponse.body || 'null'}`);
    console.error(`  Message: ${JSON.stringify(payload.data)}`);
    console.error(`  Timestamp: ${payload.data.timestamp}`);
    console.error(`  Request payload: ${JSON.stringify(payload)}`);
    console.error(`  Request headers: ${JSON.stringify(userCreds.headers)}`);
    console.error(`  URL: ${BASE_URL}/pubsub/topic/${topicName}`);
  } else {
    const body = JSON.parse(publishResponse.body);
    console.log(`VU ${__VU} iter ${__ITER}: published msg_id ${body.msg_id} to ${topicName}`);
  }
}

function pullMessages(userCreds) {
  let totalPulled = 0;
  let emptyAttempts = 0;

  while (emptyAttempts < PULL_MAX_EMPTY_ATTEMPTS) {
    const payload = {
      max_messages: PULL_MAX_MESSAGES,
      max_len: 5000000,
    };

    let pullResponse = http.post(
      `${BASE_URL}/pubsub/messages/get`,
      JSON.stringify(payload),
      { headers: userCreds.headers, tags: { operation: 'pull' } }
    );

    check(pullResponse, {
      'pull status is 200': (r) => r.status === 200,
      'pull response is_ok true': (r) => {
        try {
          return JSON.parse(r.body).is_ok === true;
        } catch (e) {
          return false;
        }
      },
      'pull response has messages array': (r) => {
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
        if (body.messages && body.messages.length > 0) {
          totalPulled += body.messages.length;
          emptyAttempts = 0;
          console.log(`VU ${__VU}: pulled ${body.messages.length} messages (total: ${totalPulled})`);
        } else {
          emptyAttempts++;
          console.log(`VU ${__VU}: no messages received (empty attempt ${emptyAttempts}/${PULL_MAX_EMPTY_ATTEMPTS})`);
        }
      } catch (e) {
        console.error(`VU ${__VU}: failed to parse pull response: ${e}`);
        console.error(`VU ${__VU}: pull response status: ${pullResponse.status}`);
        console.error(`VU ${__VU}: pull response body: ${pullResponse.body}`);
        console.error(`VU ${__VU}: pull response error: ${pullResponse.error || 'none'}`);
        console.error(`VU ${__VU}: pull response error_code: ${pullResponse.error_code || 'none'}`);
        emptyAttempts++;
      }
    } else {
      console.error(`VU ${__VU}: pull failed with status ${pullResponse.status}`);
      console.error(`VU ${__VU}: pull error: ${pullResponse.error || 'none'}`);
      console.error(`VU ${__VU}: pull error_code: ${pullResponse.error_code || 'none'}`);
      console.error(`VU ${__VU}: pull body: ${pullResponse.body || 'null'}`);
      console.error(`VU ${__VU}: pull request payload: ${JSON.stringify(payload)}`);
      emptyAttempts++;
    }

    sleep(0.1);
  }

  console.log(`VU ${__VU}: finished pulling messages, total pulled: ${totalPulled}`);
  return totalPulled;
}

export default function() {
  const userCreds = getUserCredentials(__VU);
  const topicNames = getTopicNames();

  for (const topicName of topicNames) {
    publish(topicName, userCreds);
  }

  console.log(`VU ${__VU}: waiting ${WAIT_BEFORE_PULL_SECONDS} seconds before pulling messages...`);
  for (let i = 1; i <= WAIT_BEFORE_PULL_SECONDS; i++) {
    sleep(1);
    console.log(`VU ${__VU}: still waiting... ${i}/${WAIT_BEFORE_PULL_SECONDS} seconds elapsed`);
  }
  console.log(`VU ${__VU}: finished waiting, starting to pull messages`);
  pullMessages(userCreds);
}
