import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, getUserCredentials, getTopicName, VUS, ITERATIONS_PER_VU } from './config.js';

export let options = {
  scenarios: {
    default: {
      executor: 'per-vu-iterations',
      vus: VUS,
      iterations: ITERATIONS_PER_VU,
      maxDuration: '120m',
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate==0'],
    'checks{operation:publish}': ['rate==1'],
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
    expiration: 3600,
  };

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

  if (publishResponse.status !== 200) {
    console.error(`Publish failed for VU ${__VU}: ${publishResponse.status}`);
  } else {
    const body = JSON.parse(publishResponse.body);
    console.log(`VU ${__VU} iter ${__ITER}: published msg_id ${body.msg_id} to ${topicName}`);
  }
}

export default function() {
  const topicName = getTopicName(__VU);
  const userCreds = getUserCredentials(__VU);

  publish(topicName, userCreds);

  sleep(0.1);
}
