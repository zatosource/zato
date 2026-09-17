# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation of an outgoing LLM connection's alert - the llm skill explains it, the Object section is read off the
# connection's generic row with its address, its model, its timeout and max tokens and the token budget it sets of its own,
# the failures of a status codes alert group under `429 Too Many Requests` with the model on every row, and a truncation
# alert lists the completions that came back with a 200 and stopped for `length`, each with its model and its token counts.

# stdlib
import json

# Zato
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.api import GENERIC
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import LLMAttr, LLMFinish
from zato.common.odb.model import Cluster, GenericConn
from zato.common.typing_ import cast_

# Test helpers
from explain_helpers import _cluster_id, _llm_conn_name, _server_name, _LLMFacade, LLMTestHandler, \
    new_payload as _new_payload, new_service as _new_service, new_session as _new_session, \
    object_section as _object_section, stored_explanation as _stored_explanation

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The connection the tests describe - the one that is explained, not the one that explains
_conn_name = 'support.assistant'
_conn_address = 'https://api.openai.com/v1'
_conn_model = 'gpt-4o'

# The connection's own numbers
_timeout = 90
_max_tokens = 512

# The budget the connection sets of its own, in ones, rather than the default ten millions
_own_token_budget = 2000000

# The title line of the skill an outgoing LLM connection is explained with
_llm_skill_title = '# LLM connection explanation'

# What the failed calls came back with - three rate limits and one bare 503 from the provider's edge
_rate_limited_status = '429 Too Many Requests'
_proxy_status = '503 Service Unavailable'

# The status a completion that came back is written under, whether it stopped or was cut short
_status_ok = '200 OK'

# The cost of each completion
_input_tokens = '100'
_output_tokens = '50'

# ################################################################################################################################

def _seed_connection(session_maker:'any_') -> 'None':
    """ One outgoing LLM connection with a model, its own timeout and max tokens and alert settings of its own.
    """
    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    opaque = {
        'model': _conn_model,
        'timeout': _timeout,
        'max_tokens': _max_tokens,
        storage_name('is_active'): True,
        storage_name('token_budget'): _own_token_budget,
        storage_name('use_llm'): True,
    }

    row = cast_('any_', GenericConn())
    row.name = _conn_name
    row.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
    row.is_active = True
    row.is_internal = False
    row.is_channel = False
    row.is_outconn = True
    row.address = _conn_address
    row.pool_size = 4
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_failures() -> 'None':
    """ The calls the connection made that failed - three the provider rate-limited and one bare 503 from its edge,
    each an error row under its status line with the model as its one attribute, the way the wrapper writes them.
    """
    audit_log = AuditLog(_server_name)

    _ = audit_log.insert(AuditSource.LLM, AuditEvent.Response_Received, _conn_name, cid='proxy-1',
        outcome=AuditOutcome.Error, status=_proxy_status, endpoint=_conn_address, attrs={LLMAttr.Model: _conn_model})

    for index in range(3):
        _ = audit_log.insert(AuditSource.LLM, AuditEvent.Response_Received, _conn_name, cid=f'limited-{index}',
            outcome=AuditOutcome.Error, status=_rate_limited_status, endpoint=_conn_address,
            attrs={LLMAttr.Model: _conn_model})

# ################################################################################################################################

def _seed_completions() -> 'None':
    """ The completions the connection got back - two cut short by the token limit and one that stopped on its own,
    every one an OK row under `200 OK` with the model, the finish reason and the two token counts as its attributes.
    """
    audit_log = AuditLog(_server_name)

    for index, finish_reason in enumerate((LLMFinish.Length, LLMFinish.Length, LLMFinish.Stop)):
        attrs = {
            LLMAttr.Model: _conn_model,
            LLMAttr.Finish_Reason: finish_reason,
            LLMAttr.Input_Tokens: _input_tokens,
            LLMAttr.Output_Tokens: _output_tokens,
        }
        _ = audit_log.insert(AuditSource.LLM, AuditEvent.Response_Received, _conn_name, cid=f'completion-{index}',
            outcome=AuditOutcome.OK, status=_status_ok, endpoint=_conn_address, attrs=attrs)

# ################################################################################################################################

def _explain(session:'any_', repo_dir:'str', llm_address:'any_', measure:'str') -> 'str':
    """ Explains one alert of the connection and gives back the prompt the model saw.
    """
    service = _new_service(
        _new_payload(AlertAction.Email_Digest, {}, AuditSource.LLM, object_name=_conn_name, measures=[measure]),
        session,
        repo_dir,
        llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
    )

    service.handle()

    assert len(LLMTestHandler.prompts) == 1

    out = LLMTestHandler.prompts[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingLLM:

    def test_an_outgoing_llm_alert_is_explained_with_the_llm_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'status_count')
        assert prompt.startswith(_llm_skill_title)

        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.LLM
        assert explanation['is_parsed'] is True

# ################################################################################################################################

    def test_the_object_section_carries_the_address_the_model_and_the_token_budget(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'status_count')
        section = _object_section(prompt)

        assert f'Name: {_conn_name}' in section
        assert 'Type: LLM' in section
        assert 'Active: yes' in section
        assert f'Address: {_conn_address}' in section
        assert f'Model: {_conn_model}' in section
        assert 'Pool size: 4' in section
        assert f'Timeout: {_timeout}' in section
        assert f'Max tokens: {_max_tokens}' in section

        # The connection's own budget is the one setting that differs from the defaults
        assert f'Token budget {_own_token_budget}' in section
        assert 'Alerts: on' in section

# ################################################################################################################################

    def test_the_failures_group_under_the_status_with_the_model_on_every_row(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_failures()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'status_count')

        # The three rate limits lead as one group named by the status and the model, the bare 503 after them
        assert f'1. {_rate_limited_status} - {LLMAttr.Model}={_conn_model}' in prompt
        assert 'Count: 3' in prompt
        assert f'2. {_proxy_status} - {LLMAttr.Model}={_conn_model}' in prompt

        # The Failures section speaks of calls to the provider
        assert 'call' in prompt

# ################################################################################################################################

    def test_a_truncation_alert_lists_the_length_rows_with_their_model_and_tokens(self, llm_address:'any_',
        repo_dir:'str') -> 'None':

        _seed_completions()

        session = _new_session()
        _seed_connection(session)

        prompt = _explain(session, repo_dir, llm_address, 'truncation_count')

        # The two completions cut short are one group - a 200 row with the model, the finish reason and the cost ..
        expected_text = f'{_status_ok} - {LLMAttr.Model}={_conn_model}, {LLMAttr.Finish_Reason}={LLMFinish.Length}, ' + \
            f'{LLMAttr.Input_Tokens}={_input_tokens}, {LLMAttr.Output_Tokens}={_output_tokens}'

        assert f'1. {expected_text}' in prompt
        assert 'Count: 2' in prompt

        # .. and the one that stopped on its own is not among the failures
        assert f'{LLMAttr.Finish_Reason}={LLMFinish.Stop}' not in prompt

# ################################################################################################################################
# ################################################################################################################################
