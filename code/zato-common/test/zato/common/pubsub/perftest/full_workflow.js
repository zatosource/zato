import http from 'k6/http';
import { check, sleep, fail } from 'k6';
import { BASE_URL, getUserCredentials, getTopicNames, VUS, ITERATIONS_PER_VU, PULL_MAX_MESSAGES, PULL_MAX_EMPTY_ATTEMPTS, WAIT_BEFORE_PULL_SECONDS, REQUEST_RATE, PRE_ALLOCATED_VUS, HTTP_TIMEOUT } from './config.js';

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
    { headers: userCreds.headers, tags: { operation: 'publish' }, timeout: HTTP_TIMEOUT }
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
    if (publishResponse.error !== 'context canceled') {
      console.error(`\n***************************************************************
Publish failed for VU ${__VU}:
Timestamp: ${payload.data.timestamp}
Duration: ${duration}ms
Status: ${publishResponse.status}
Topic: ${topicName}
Error: ${publishResponse.error || 'none'}
ErrorCode: ${publishResponse.error_code || 'none'}
Body: ${publishResponse.body || 'null'}
Message: ${JSON.stringify(payload.data)}
RequestPayload: ${JSON.stringify(payload)}
RequestHeaders: ${JSON.stringify(userCreds.headers)}
URL: ${BASE_URL}/pubsub/topic/${topicName}
***************************************************************`);
      fail(`Publish failed with status ${publishResponse.status}`);
    }
  } else {
    //const body = JSON.parse(publishResponse.body);
    //console.log(`VU ${__VU} iter ${__ITER}: published msg_id ${body.msg_id} to ${topicName}`);
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
      { headers: userCreds.headers, tags: { operation: 'pull' }, timeout: HTTP_TIMEOUT }
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
        console.error(`\n***************************************************************
VU ${__VU}: failed to parse pull response:
Timestamp: ${new Date().toISOString()}
ParseError: ${e}
Status: ${pullResponse.status}
Body: ${pullResponse.body}
Error: ${pullResponse.error || 'none'}
ErrorCode: ${pullResponse.error_code || 'none'}
***************************************************************`);
        emptyAttempts++;
      }
    } else {
      if (pullResponse.error !== 'context canceled') {
        console.error(`\n***************************************************************
VU ${__VU}: pull failed:
Timestamp: ${new Date().toISOString()}
Status: ${pullResponse.status}
Error: ${pullResponse.error || 'none'}
ErrorCode: ${pullResponse.error_code || 'none'}
Body: ${pullResponse.body || 'null'}
RequestPayload: ${JSON.stringify(payload)}
***************************************************************`);
        fail(`Pull failed with status ${pullResponse.status}`);
      }
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

  /*
  console.log(`VU ${__VU}: waiting ${WAIT_BEFORE_PULL_SECONDS} seconds before pulling messages...`);
  for (let i = 1; i <= WAIT_BEFORE_PULL_SECONDS; i++) {
    sleep(1);
    console.log(`VU ${__VU}: still waiting... ${i}/${WAIT_BEFORE_PULL_SECONDS} seconds elapsed`);
  }
  console.log(`VU ${__VU}: finished waiting, starting to pull messages`);
  pullMessages(userCreds);
  */
}
