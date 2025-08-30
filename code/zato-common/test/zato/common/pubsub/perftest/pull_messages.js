import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, headers } from './config.js';

export let options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 30 },
    { duration: '2m', target: 75 },
    { duration: '1m', target: 30 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate==0'],
  },
};

export default function() {

  const payload = {
    max_messages: Math.floor(Math.random() * 20) + 5,
    max_len: Math.floor(Math.random() * 1000000) + 500000,
  };

  let response = http.post(
    `${BASE_URL}/pubsub/messages/get`,
    JSON.stringify(payload),
    { headers }
  );

  check(response, {
    'pull status is 200': (r) => r.status === 200,
    'response is_ok true': (r) => {
      try {
        return JSON.parse(r.body).is_ok === true;
      } catch (e) {
        return false;
      }
    },
    'response has messages array': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.messages);
      } catch (e) {
        return false;
      }
    },
    'messages have required fields': (r) => {
      try {
        const body = JSON.parse(r.body);
        if (!Array.isArray(body.messages) || body.messages.length === 0) {
          return true;
        }
        const msg = body.messages[0];
        return msg.topic_name && msg.msg_id && msg.data !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  if (response.status !== 200) {
    console.error(`Pull messages failed for VU ${__VU}: ${response.status} - ${response.body}`);
  } else {
    try {
      const body = JSON.parse(response.body);
      if (body.messages && body.messages.length > 0) {
        console.log(`VU ${__VU} pulled ${body.messages.length} messages`);
      }
    } catch (e) {
      console.error(`Failed to parse response for VU ${__VU}: ${e}`);
    }
  }

  sleep(0.3);
}
