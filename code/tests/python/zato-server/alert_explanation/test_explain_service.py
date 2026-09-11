# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explained alert path end to end - the alerting engine hands an alert of a ruleset
# with the Use LLM switch on to the explain service, which collects evidence from the
# audit log, has the LLM explain it over real HTTP against a threaded simulator, stores
# the explanation next to the alert and then runs the rule's own action - Slack,
# Microsoft Teams or email, each one a real simulated server of its own.

# pytest
import pytest

# Zato
from zato.common.alerting.model import AlertAction
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditSource
from zato.common.alerting.explain.skill import load_skill
from zato.common.alerting.explain.store import ExplanationStore

# Test helpers
from chat_simulators import SlackTestHandler
from explain_helpers import _alert_id, _alert_link, _alert_message, _cluster_id, _conn_name, _email_from, _email_to, \
    _error_data, _explanation_text, _get_explained_events, _llm_conn_name, _new_payload, _new_service, _new_session, \
    _seed_error_events, _slack_channel, _slack_token, _EmailAPI, _LLMFacade, _SlackFacade, _TeamsFacade, LLMTestHandler
from teams_simulator import TeamsGraphTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestExplainPath:

    def test_an_explained_alert_delivers_through_slack_with_the_explanation(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        conn_name = Alerting.Notification_Conn_Name
        active = {conn_name: {'is_active': True}}

        # The default LLM connection exists and a person already activated it
        llm_connections = {_llm_conn_name: {'is_active': True}}

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Slack, {'slack_channel': _slack_channel}),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            slack=_SlackFacade(active, slack_address, _slack_token),
        )

        service.handle()

        # The explanation went through the default LLM connection ..
        assert service.llm.invoked_names == [_llm_conn_name]

        # .. with the evidence pack in the prompt - the errors' own text included ..
        assert len(LLMTestHandler.prompts) == 1
        assert _error_data in LLMTestHandler.prompts[0]
        assert '# Evidence' in LLMTestHandler.prompts[0]

        # .. the explanation is stored next to the alert ..
        store = ExplanationStore(session, _cluster_id)
        explanation = store.get(f'explanation.{_alert_id}')

        assert explanation is not None
        assert explanation['alert_id'] == _alert_id
        assert explanation['explanation'] == _explanation_text
        assert explanation['confidence'] == 'high'
        assert explanation['remediation'] == {'action': 'resubmit'}
        assert explanation['is_parsed'] is True

        # .. the audit log says the alert was explained ..
        events = _get_explained_events()
        assert len(events) == 1
        assert events[0]['object_name'] == _conn_name
        assert events[0]['data'] == _alert_message

        # .. and the rule's own action ran - Slack heard about it, explanation and link included.
        assert len(SlackTestHandler.messages) == 1

        slack_message = SlackTestHandler.messages[0]
        assert slack_message['channel'] == _slack_channel
        assert slack_message['text'] == f'[3x] {_alert_message}\nExplanation (high): {_explanation_text}\n{_alert_link}'

# ################################################################################################################################

    def test_an_explained_alert_delivers_through_teams_as_html(
        self,
        llm_address:'any_',
        teams_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        conn_name = Alerting.Notification_Conn_Name
        active = {conn_name: {'is_active': True}}
        llm_connections = {_llm_conn_name: {'is_active': True}}

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Teams, {'teams_to': 'Alerts'}),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            teams=_TeamsFacade(active, teams_address),
        )

        service.handle()

        assert len(TeamsGraphTestHandler.messages) == 1

        teams_content = TeamsGraphTestHandler.messages[0]['payload']['body']['content']
        assert _alert_message in teams_content
        assert _explanation_text in teams_content
        assert _alert_link in teams_content
        assert '<br/>' in teams_content

# ################################################################################################################################

    def test_an_explained_alert_delivers_through_email_to_the_default_addresses(
        self,
        llm_address:'any_',
        smtp_receiver:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        llm_connections = {_llm_conn_name: {'is_active': True}}

        session = _new_session()

        # The seeded email rules name no addresses of their own - the deployment-level ones answer
        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, email_to=_email_to),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            email=_EmailAPI(smtp_receiver.port),
        )

        service.handle()

        assert len(smtp_receiver.messages) == 1

        received = smtp_receiver.messages[0]
        assert received.sender == _email_from
        assert received.recipients == _email_to
        assert received.subject == f'[3x] {_alert_message}'
        assert _explanation_text in received.body
        assert _alert_link in received.body

# ################################################################################################################################

    def test_an_inactive_default_delivers_the_alert_unexplained(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        conn_name = Alerting.Notification_Conn_Name

        # The default LLM connection is there but still inactive, the way it ships
        llm_connections = {_llm_conn_name: {'is_active': False}}

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Slack, {'slack_channel': _slack_channel}),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            slack=_SlackFacade({conn_name: {'is_active': True}}, slack_address, _slack_token),
        )

        service.handle()

        # No LLM was called ..
        assert service.llm.invoked_names == []
        assert LLMTestHandler.prompts == []

        # .. the alert is stored without an explanation ..
        store = ExplanationStore(session, _cluster_id)
        explanation = store.get(f'explanation.{_alert_id}')

        assert explanation is not None
        assert explanation['explanation'] == ''
        assert explanation['is_parsed'] is False

        # .. and the notification still went out, just without an explanation line.
        assert len(SlackTestHandler.messages) == 1
        assert _alert_message in SlackTestHandler.messages[0]['text']
        assert 'Explanation' not in SlackTestHandler.messages[0]['text']

# ################################################################################################################################

    def test_a_source_without_a_skill_is_delivered_unexplained(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        conn_name = Alerting.Notification_Conn_Name
        llm_connections = {_llm_conn_name: {'is_active': True}}

        session = _new_session()

        # No explanation skill ships for MLLP channels
        service = _new_service(
            _new_payload(AlertAction.Slack, {'slack_channel': _slack_channel}, AuditSource.MLLP_Channel),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            slack=_SlackFacade({conn_name: {'is_active': True}}, slack_address, _slack_token),
        )

        service.handle()

        # Nothing was asked of the LLM and nothing was stored ..
        assert service.llm.invoked_names == []

        store = ExplanationStore(session, _cluster_id)
        assert store.get_list() == []

        # .. while the alert itself went out all the same.
        assert len(SlackTestHandler.messages) == 1
        assert _alert_message in SlackTestHandler.messages[0]['text']
        assert 'Explanation' not in SlackTestHandler.messages[0]['text']

# ################################################################################################################################

    def test_one_alert_produces_one_explanation_and_every_delivery_carries_it(
        self,
        llm_address:'any_',
        slack_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events()

        conn_name = Alerting.Notification_Conn_Name
        llm_connections = {_llm_conn_name: {'is_active': True}}

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Slack, {'slack_channel': _slack_channel}),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
            slack=_SlackFacade({conn_name: {'is_active': True}}, slack_address, _slack_token),
        )

        # The same alert arrives twice - an error finding is dispatched on every
        # sweep - and only the first one spends tokens, the second reuses the explanation
        service.handle()
        service.handle()

        store = ExplanationStore(session, _cluster_id)
        assert len(store.get_list()) == 1

        assert service.llm.invoked_names == [_llm_conn_name]

        assert len(SlackTestHandler.messages) == 2

        for slack_message in SlackTestHandler.messages:
            assert _explanation_text in slack_message['text']

# ################################################################################################################################
# ################################################################################################################################

# The sources that ship an explanation skill of their own - each one produces
# an explanation instead of being delivered unexplained for having no skill.
_explainable_sources = (
    AuditSource.SQL_Outgoing,
    AuditSource.LLM,
    AuditSource.MCP,
    AuditSource.Microsoft_Cloud,
    AuditSource.Email_SMTP,
    AuditSource.Email_IMAP,
    AuditSource.Odoo,
    AuditSource.File_Outgoing,
    AuditSource.Scheduler,
)

# ################################################################################################################################
# ################################################################################################################################

class TestExplainPerSource:

    @pytest.mark.parametrize('source', _explainable_sources)
    def test_a_non_rest_source_produces_an_explanation(
        self,
        source:'str',
        llm_address:'any_',
        repo_dir:'str',
        ) -> 'None':

        _seed_error_events(source)

        session = _new_session()

        # The llm source's own config lookup reads the facade's conn_dict, so the connection
        # under explanation is in there next to the default LLM connection.
        llm_connections = {
            _conn_name: {'name': _conn_name, 'is_active': True},
            _llm_conn_name: {'is_active': True},
        }

        # An email action with no addresses anywhere - this test is about the explanation
        # itself, not the delivery, and such an email is skipped with a log line.
        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, source),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
        )

        service.handle()

        # The explanation went through the default LLM connection ..
        assert service.llm.invoked_names == [_llm_conn_name]

        # .. with the source's own skill leading the prompt and the errors' text in the evidence ..
        skill = load_skill(source)
        assert skill is not None

        assert len(LLMTestHandler.prompts) == 1
        assert LLMTestHandler.prompts[0].startswith(skill.instructions)
        assert _error_data in LLMTestHandler.prompts[0]

        # .. the explanation is stored next to the alert ..
        store = ExplanationStore(session, _cluster_id)
        explanation = store.get(f'explanation.{_alert_id}')

        assert explanation is not None
        assert explanation['source'] == source
        assert explanation['explanation'] == _explanation_text
        assert explanation['is_parsed'] is True

        # .. and the audit log says the alert was explained.
        events = _get_explained_events()
        assert len(events) == 1
        assert events[0]['source'] == source
        assert events[0]['object_name'] == _conn_name

# ################################################################################################################################
# ################################################################################################################################
