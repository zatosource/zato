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
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate==0'],
  },
};

export default function() {
  const topicName = getTopicName(__VU);
  const userCreds = getUserCredentials(__VU);

  const payload = {
    data: {
      message: `Performance test message from VU ${__VU}, iteration ${__ITER}`,
      timestamp: new Date().toISOString(),
      vu: __VU,
      iteration: __ITER,
    },
    priority: Math.floor(Math.random() * 10),
    expiration: 3600,
    correl_id: `perf-${__VU}-${__ITER}`,
  };

  let response = http.post(
    `${BASE_URL}/pubsub/topic/${topicName}`,
    JSON.stringify(payload),
    { headers: userCreds.headers }
  );

  check(response, {
    'publish status is 200': (r) => r.status === 200,
    'response has msg_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.msg_id && body.msg_id.startsWith('zpsm.');
      } catch (e) {
        return false;
      }
    },
    'response is_ok true': (r) => {
      try {
        return JSON.parse(r.body).is_ok === true;
      } catch (e) {
        return false;
      }
    },
  });

  if (response.status !== 200) {
    console.error(`Publish failed for VU ${__VU}: ${response.status} - ${response.body}`);
  }

  sleep(0.1);
}
