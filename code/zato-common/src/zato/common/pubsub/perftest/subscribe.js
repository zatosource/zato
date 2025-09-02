import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, headers, getTopicName } from './config.js';

export let options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '1m', target: 20 },
    { duration: '2m', target: 50 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'],
    http_req_failed: ['rate==0'],
  },
};

export default function() {
  const topicName = getTopicName(__VU);

  let response = http.post(
    `${BASE_URL}/pubsub/subscribe/topic/${topicName}`,
    null,
    { headers }
  );

  check(response, {
    'subscribe status is 200': (r) => r.status === 200,
    'response is_ok true': (r) => {
      try {
        return JSON.parse(r.body).is_ok === true;
      } catch (e) {
        return false;
      }
    },
    'response has cid': (r) => {
      try {
        return JSON.parse(r.body).cid !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  if (response.status !== 200) {
    console.error(`Subscribe failed for VU ${__VU}: ${response.status} - ${response.body}`);
  }

  sleep(0.2);
}
