# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from shutil import copytree

# The chat and Graph simulators are shared with the rule engine jobs suite, the SMTP receiver
# with the zato-common suites, and the explain helpers live next to this file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'rule_engine_jobs', 'lib')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# pytest
import pytest

# Zato
from zato.common.alerting.explain.skill import get_default_skills_dir, Skills_Dir_Name
from zato.common.alerting.rendering import get_default_template_dir, Template_Dir_Name
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx

# Test helpers
from chat_simulators import find_free_port, start_slack_server
from explain_helpers import start_llm_server, _llm_reply, _slack_channel, _slack_token, _teams_channel_id, \
    _teams_client_id, _teams_client_secret, _teams_team_id, _teams_tenant_id
from hl7_client.smtp_receiver import SMTPReceiver
from teams_simulator import start_teams_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_
    any_ = any_
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'os.PathLike') -> 'any_':
    """ Points the audit database at a per-test SQLite file so every test
    runs on its own isolated database.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

@pytest.fixture()
def llm_address() -> 'any_':
    """ A running simulated LLM API answering every prompt with the canned explanation.
    """
    port = find_free_port()
    server = start_llm_server(port, _llm_reply)

    yield f'http://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def slack_address() -> 'any_':
    """ A running simulated Slack workspace.
    """
    port = find_free_port()
    server = start_slack_server(port, _slack_token, [_slack_channel])

    yield f'http://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def teams_address() -> 'any_':
    """ A running simulated Microsoft Graph.
    """
    port = find_free_port()
    teams = [
        {
            'id': _teams_team_id,
            'displayName': 'Operations',
            'channels': [
                {'id': _teams_channel_id, 'displayName': 'Alerts'},
            ],
        },
    ]
    server = start_teams_server(port, _teams_tenant_id, _teams_client_id, _teams_client_secret, teams)

    yield f'https://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

@pytest.fixture()
def smtp_receiver() -> 'any_':
    """ A running aiosmtpd receiver recording every email delivered to it.
    """
    receiver = SMTPReceiver()
    receiver.start()

    yield receiver

    receiver.stop()

# ################################################################################################################################

@pytest.fixture()
def repo_dir(tmp_path:'Path') -> 'str':
    """ A server repo directory with the alert templates and the alert skills copied in,
    the way create_server.py copies them.
    """
    repo = tmp_path / 'repo'
    repo.mkdir()

    _ = copytree(get_default_template_dir(), str(repo / Template_Dir_Name))
    _ = copytree(get_default_skills_dir(), str(repo / Skills_Dir_Name))

    out = str(repo)
    return out

# ################################################################################################################################
# ################################################################################################################################
