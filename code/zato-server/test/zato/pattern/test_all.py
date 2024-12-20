# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Faker
from faker import Faker

# gevent
from gevent import sleep
from gevent.lock import RLock

# Zato
from zato.common import CHANNEL
from zato.common.ext.dataclasses import dataclass
from zato.common.util import spawn_greenlet
from zato.server.pattern.api import ParallelExec
from zato.server.pattern.base import ParallelBase
from zato.server.service import PatternsFacade

# ################################################################################################################################
# ################################################################################################################################

# Random bytes to seed our data with
seed = 'FVD2nbPOVIXZ6'

Faker.seed(seed)
fake = Faker()

# ################################################################################################################################
# ################################################################################################################################

_pattern_call_channels=(CHANNEL.FANOUT_CALL, CHANNEL.PARALLEL_EXEC_CALL)
_fanout_call = CHANNEL.FANOUT_CALL

# ################################################################################################################################
# ################################################################################################################################

class FakeService:
    def __init__(self, cache, lock, response_payload):
        # type: (dict, RLock, str) -> None
        self.cid = None  # type: int
        self.name = None # type: str
        self.cache = cache
        self.lock = lock
        self.patterns = PatternsFacade(self, self.cache, self.lock)
        self.response_payload = response_payload
        self.response_exception = None

    def invoke_async(self, target_name, payload, channel, cid):

        invoked_service = FakeService(self.cache, self.lock, payload)
        invoked_service.name = target_name
        invoked_service.cid = cid

        # If we are invoked via patterns, let the callbacks run ..
        if channel in _pattern_call_channels:

            # .. find the correct callback function first ..
            if channel == _fanout_call:
                func = self.patterns.fanout.on_call_finished
            else:
                func = self.patterns.parallel.on_call_finished

            # .. and run the function in a new greenlet.
            spawn_greenlet(func, invoked_service, self.response_payload, self.response_exception)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ParamsCtx:
    cid: object
    source_service: FakeService
    source_name: str

    service_name1: str
    service_name2: str

    service_input1: str
    service_input2: str

    on_final1: str
    on_final2: str

    on_target1: str
    on_target2: str

    targets: list
    on_final_list: list
    on_target_list: list

# ################################################################################################################################
# ################################################################################################################################

class BaseTestCase(TestCase):

    def get_default_params(self, cache, lock, response_payload=None):
        # type: (dict, RLock, str) -> ParamsCtx

        cid = fake.pyint()
        source_name = 'source.name.1'

        source_service = FakeService(cache, lock, response_payload)
        source_service.cid = cid
        source_service.name = source_name

        service_name1 = 'my.service.1'
        service_name2 = 'my.service.2'

        service_input1 = {'my.input': '1'}
        service_input2 = {'my.input': '2'}

        on_final1 = 'on.final.1'
        on_final2 = 'on.final.2'

        on_target1 = 'on.target.1'
        on_target2 = 'on.target.2'

        targets = {
            service_name1: service_input1,
            service_name2: service_input2,
        }

        on_final_list = [
            on_final1,
            on_final2
        ]

        on_target_list = [
            on_target1,
            on_target2
        ]

        ctx = ParamsCtx()
        ctx.cid = cid
        ctx.source_service = source_service
        ctx.source_name = source_name

        ctx.service_name1 = service_name1
        ctx.service_name2 = service_name2

        ctx.service_input1 = service_input1
        ctx.service_input2 = service_input2

        ctx.on_final1 = on_final1
        ctx.on_final2 = on_final2

        ctx.on_target1 = on_target1
        ctx.on_target2 = on_target2

        ctx.targets = targets
        ctx.on_final_list = on_final_list
        ctx.on_target_list = on_target_list

        return ctx

# ################################################################################################################################
# ################################################################################################################################

class PatternBaseTestCase(BaseTestCase):

    def test_base_parallel_invoke_params_no_cid(self):

        cache = {}
        lock = RLock()
        params_ctx = self.get_default_params(cache, lock)

        def fake_invoke(ctx):

            self.assertEqual(ctx.cid, params_ctx.cid)
            self.assertEqual(ctx.source_name, params_ctx.source_name)
            self.assertListEqual(ctx.on_final_list, params_ctx.on_final_list)
            self.assertListEqual(ctx.on_target_list, params_ctx.on_target_list)

            self.assertEqual(ctx.target_list[0].name, params_ctx.service_name1)
            self.assertDictEqual(ctx.target_list[0].payload, params_ctx.service_input1)

            self.assertEqual(ctx.target_list[1].name, params_ctx.service_name2)
            self.assertDictEqual(ctx.target_list[1].payload, params_ctx.service_input2)

        api = ParallelBase(params_ctx.source_service, cache, lock)
        api._invoke = fake_invoke
        api.invoke(params_ctx.targets, params_ctx.on_final_list, params_ctx.on_target_list)

# ################################################################################################################################

    def test_base_parallel_invoke_params_with_cid(self):

        cache = {}
        lock = RLock()
        params_ctx = self.get_default_params(cache, lock)
        custom_cid = fake.pystr()

        def fake_invoke(ctx):

            self.assertEqual(ctx.cid, custom_cid)
            self.assertEqual(ctx.source_name, params_ctx.source_name)
            self.assertListEqual(ctx.on_final_list, params_ctx.on_final_list)
            self.assertListEqual(ctx.on_target_list, params_ctx.on_target_list)

            self.assertEqual(ctx.target_list[0].name, params_ctx.service_name1)
            self.assertDictEqual(ctx.target_list[0].payload, params_ctx.service_input1)

            self.assertEqual(ctx.target_list[1].name, params_ctx.service_name2)
            self.assertDictEqual(ctx.target_list[1].payload, params_ctx.service_input2)

        api = ParallelBase(params_ctx.source_service, cache, lock)
        api._invoke = fake_invoke
        api.invoke(params_ctx.targets, params_ctx.on_final_list, params_ctx.on_target_list, custom_cid)

# ################################################################################################################################

    def test_base_parallel_invoke_params_single_elements(self):

        cache = {}
        lock = RLock()
        params_ctx = self.get_default_params(cache, lock)
        custom_on_final = fake.pystr()
        custom_on_target = fake.pystr()

        def fake_invoke(ctx):

            self.assertEqual(ctx.cid, params_ctx.cid)
            self.assertEqual(ctx.source_name, params_ctx.source_name)
            self.assertListEqual(ctx.on_final_list, [custom_on_final])
            self.assertListEqual(ctx.on_target_list, [custom_on_target])

            self.assertEqual(ctx.target_list[0].name, params_ctx.service_name1)
            self.assertDictEqual(ctx.target_list[0].payload, params_ctx.service_input1)

            self.assertEqual(ctx.target_list[1].name, params_ctx.service_name2)
            self.assertDictEqual(ctx.target_list[1].payload, params_ctx.service_input2)

        api = ParallelBase(params_ctx.source_service, cache, lock)
        api._invoke = fake_invoke
        api.invoke(params_ctx.targets, custom_on_final, custom_on_target)

# ################################################################################################################################

    def test_base_parallel_invoke_params_final_is_none(self):

        cache = {}
        lock = RLock()
        params_ctx = self.get_default_params(cache, lock)
        custom_on_final = None
        custom_on_target = fake.pystr()

        def fake_invoke(ctx):

            self.assertEqual(ctx.cid, params_ctx.cid)
            self.assertEqual(ctx.source_name, params_ctx.source_name)
            self.assertIsNone(ctx.on_final_list)
            self.assertListEqual(ctx.on_target_list, [custom_on_target])

            self.assertEqual(ctx.target_list[0].name, params_ctx.service_name1)
            self.assertDictEqual(ctx.target_list[0].payload, params_ctx.service_input1)

            self.assertEqual(ctx.target_list[1].name, params_ctx.service_name2)
            self.assertDictEqual(ctx.target_list[1].payload, params_ctx.service_input2)

        api = ParallelBase(params_ctx.source_service, cache, lock)
        api._invoke = fake_invoke
        api.invoke(params_ctx.targets, custom_on_final, custom_on_target)

# ################################################################################################################################

    def test_base_parallel_invoke_params_target_is_none(self):

        cache = {}
        lock = RLock()
        params_ctx = self.get_default_params(cache, lock)
        custom_on_final = fake.pystr()
        custom_on_target = None

        def fake_invoke(ctx):

            self.assertEqual(ctx.cid, params_ctx.cid)
            self.assertEqual(ctx.source_name, params_ctx.source_name)
            self.assertListEqual(ctx.on_final_list, [custom_on_final])
            self.assertIsNone(ctx.on_target_list)

            self.assertEqual(ctx.target_list[0].name, params_ctx.service_name1)
            self.assertDictEqual(ctx.target_list[0].payload, params_ctx.service_input1)

            self.assertEqual(ctx.target_list[1].name, params_ctx.service_name2)
            self.assertDictEqual(ctx.target_list[1].payload, params_ctx.service_input2)

        api = ParallelBase(params_ctx.source_service, cache, lock)
        api._invoke = fake_invoke
        api.invoke(params_ctx.targets, custom_on_final, custom_on_target)

# ################################################################################################################################
# ################################################################################################################################

class ParallelExecTestCase(BaseTestCase):
    def test_parallel_exec(self):

        cache = {}
        lock = RLock()
        response_payload = 'my.payload'
        params_ctx = self.get_default_params(cache, lock, response_payload)
        params_ctx.on_final_list = []

        api = ParallelExec(params_ctx.source_service, cache, lock)
        api.invoke(params_ctx.targets, params_ctx.on_target_list)

        # Give the test enough time to run
        sleep(0.01)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
