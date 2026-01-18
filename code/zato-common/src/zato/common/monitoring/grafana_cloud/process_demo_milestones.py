# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import base64
import json
import logging
import os
import time
from http.client import HTTPSConnection

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

user_id = os.environ['Zato_Grafana_Graphite_User_ID']
api_key = os.environ['Zato_Grafana_Graphite_API_Key']
host = os.environ['Zato_Grafana_Graphite_Host']

milestones = {
    'checkin': 1,
    'security': 2,
    'boarding': 3,
    'takeoff': 4,
    'landing': 5,
    'deboarding': 6,
}

def push_milestone(process_id, milestone_name):
    milestone_code = milestones[milestone_name]
    timestamp = int(time.time())
    payload = json.dumps([{
        'name': f'process.milestone.{process_id}',
        'interval': 10,
        'value': milestone_code,
        'time': timestamp,
        'tags': ['milestone=' + milestone_name]
    }])

    auth = base64.b64encode(f'{user_id}:{api_key}'.encode()).decode()

    conn = HTTPSConnection(host)
    conn.request(
        'POST',
        '/graphite/metrics',
        payload,
        {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
    )
    response = conn.getresponse()
    body = response.read().decode()
    logger.info(f'{milestone_name}: {response.status} {body}')
    conn.close()

if __name__ == '__main__':
    process_id = 'flight_lo456'

    push_milestone(process_id, 'checkin')
    time.sleep(1)
    push_milestone(process_id, 'security')
    time.sleep(0.5)
    push_milestone(process_id, 'boarding')
    time.sleep(0.2)
    push_milestone(process_id, 'takeoff')
    time.sleep(0.3)
    push_milestone(process_id, 'landing')
    time.sleep(1)
    push_milestone(process_id, 'deboarding')
