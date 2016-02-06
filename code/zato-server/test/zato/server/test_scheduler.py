# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from unittest import TestCase

# Zato
from zato.common import CHANNEL, DATA_FORMAT, ENSURE_SINGLETON_JOB, SCHEDULER, ZATO_NONE
from zato.common.broker_message import SERVICE, SCHEDULER as SCHEDULER_MSG
from zato.common.log_message import CID_LENGTH
from zato.common.test import rand_string
from zato.common.util import new_cid
from zato.server.scheduler import Scheduler

logger = getLogger(__name__)

# ################################################################################################################################

class SchedulerTestCase(TestCase):

# ################################################################################################################################

    def test_on_job_executed(self):

        job_types = SCHEDULER.JOB_TYPE.CRON_STYLE, SCHEDULER.JOB_TYPE.INTERVAL_BASED, SCHEDULER.JOB_TYPE.ONE_TIME
        extra_data_format = rand_string()
        name = rand_string()
        service = rand_string()
        extra = rand_string()
        cid = new_cid()
        id = rand_string()

        for _extra_data_format in (ZATO_NONE, extra_data_format):
            for job_type in job_types:
                for _name in (name, ENSURE_SINGLETON_JOB):

                    cb_kwargs = {
                        'service': service,
                        'extra': extra,
                    }

                    ctx = {
                        'name': _name,
                        'cb_kwargs': cb_kwargs,
                        'cid': cid,
                        'type': job_type,
                        'id': id,
                    }

                    async_msgs = []
                    publish_msgs = []

                    class _BrokerClient:

                        def invoke_async(self, msg):
                            async_msgs.append(msg)

                        def publish(self, msg):
                            publish_msgs.append(msg)

                    class _Singleton:
                        broker_client = _BrokerClient()

                    sched = Scheduler(_Singleton(), init=False)

                    sched.on_job_executed(ctx, _extra_data_format)

                    def check_publish_msg(msg):
                        self.assertEquals(msg['action'], SERVICE.PUBLISH.value)
                        self.assertEquals(msg['service'], 'zato.scheduler.job.set-active-status')
                        self.assertEquals(msg['payload']['id'], id)
                        self.assertEquals(msg['payload']['is_active'], False)
                        self.assertEquals(len(msg['cid']), CID_LENGTH)
                        self.assertEquals(msg['channel'], CHANNEL.SCHEDULER_AFTER_ONE_TIME)
                        self.assertEquals(msg['data_format'], DATA_FORMAT.JSON)

                    def check_async_msg(msg):

                        if msg['action'] == SCHEDULER_MSG.JOB_EXECUTED.value:
                            self.assertEquals(msg['service'], service)
                            self.assertEquals(msg['payload'], extra)
                            self.assertEquals(len(msg['cid']), CID_LENGTH)

                    if _name == ENSURE_SINGLETON_JOB:
                        self.assertEquals(len(async_msgs), 0)

                        if job_type == SCHEDULER.JOB_TYPE.ONE_TIME:
                            self.assertEquals(len(async_msgs), 0)
                            self.assertEquals(len(publish_msgs), 2)
                            check_publish_msg(publish_msgs[1])

                        else:
                            self.assertEquals(len(async_msgs), 0)
                            self.assertEquals(len(publish_msgs), 1)

                    else:
                        self.assertEquals(len(async_msgs), 1)
                        check_async_msg(async_msgs[0])

                        if job_type == SCHEDULER.JOB_TYPE.ONE_TIME:
                            self.assertEquals(len(publish_msgs), 1)
                            check_publish_msg(publish_msgs[0])
                        else:
                            self.assertEquals(len(publish_msgs), 0)
