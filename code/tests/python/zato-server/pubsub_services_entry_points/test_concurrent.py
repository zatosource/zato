# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import NamedTuple

# Service entry points
from service_entry_points.compare import assert_same_record, assert_same_response, wait_for_record
from service_entry_points.requests import All_Targets, HL7_Target, new_request_id, SOAPVersion, Structured_Targets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import Future
    from conftest import Suite
    from service_entry_points.compare import references_dict
    from service_entry_points.requests import Target
    from zato.common.typing_ import callable_

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# How many times every entry point sends a request of each service
_rounds = 3

# ################################################################################################################################
# ################################################################################################################################

class _Job(NamedTuple):
    """ One entry point of one service, sending its canonical request under the request ID given.
    """
    target: 'Target'
    entry_point: 'str'
    send: 'callable_'
    has_response: 'bool'

job_list = list[_Job]

# ################################################################################################################################

class _Sent(NamedTuple):
    """ A request sent by a job, with the response that the job returns once the request completes.
    """
    job: '_Job'
    request_id: 'str'
    future: 'Future'

# ################################################################################################################################
# ################################################################################################################################

def _new_jobs(suite:'Suite') -> 'job_list':
    """ Every entry point of every service that it leads to.
    """
    out:'job_list' = []

    for target in All_Targets:
        out.append(_Job(target, 'self.invoke', partial(suite.invoke, target), True))
        out.append(_Job(target, 'self.pubsub to a topic', partial(suite.publish_to_topic, target), False))
        out.append(_Job(target, 'self.pubsub to a service', partial(suite.publish_to_service, target), False))

    for target in Structured_Targets:
        out.append(_Job(target, 'a REST channel', partial(suite.post_rest, target), True))

        for soap_version in (SOAPVersion.V11, SOAPVersion.V12):
            send = partial(suite.post_soap, target, soap_version=soap_version)
            out.append(_Job(target, f'a SOAP {soap_version} channel', send, True))

    out.append(_Job(HL7_Target, 'an MLLP channel', suite.send_mllp, True))
    out.append(_Job(HL7_Target, 'an HL7 v2 REST channel', suite.post_rest_hl7, True))

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent(suite:'Suite', references:'references_dict') -> 'None':
    """ Requests sent through every entry point at the same time each reach their service once and each give
    the record and the response that self.invoke gives.
    """
    jobs = _new_jobs(suite) * _rounds
    sent:'list[_Sent]' = []

    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        for job in jobs:
            request_id = new_request_id()
            future = executor.submit(job.send, request_id)
            sent.append(_Sent(job, request_id, future))

    for item in sent:

        reference = references[item.job.target.kind]
        response = item.future.result()

        record = wait_for_record(suite.client, item.request_id)
        assert_same_record(reference, record, item.job.entry_point)

        if item.job.has_response:
            assert_same_response(reference, response, item.request_id, item.job.entry_point)

# ################################################################################################################################
# ################################################################################################################################
