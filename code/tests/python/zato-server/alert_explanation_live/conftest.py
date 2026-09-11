# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The live explain suite - the alert explanation service end to end over real servers, every one
# of them test-managed: the LLM is Ollama in its docker container, the failures the LLM explains
# are produced against a real IMAP server and a real SSH server with an SFTP subsystem, and the
# explained alert is delivered to a real SMTP receiver. The suite skips when docker is not available.

# stdlib
import os
import socket
import subprocess
import sys
import time
from shutil import copytree

# The Ollama container helpers live in the LLM MCP suite, the IMAP server in the IMAP scheduler suite,
# the SMTP receiver with the zato-common suites and the explain helpers in the simulator-backed explain suite.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mcp_llm_live')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'email_imap_scheduler')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'alert_explanation')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# pytest
import pytest

# Zato
from zato.common.alerting.explain.skill import get_default_skills_dir, Skills_Dir_Name
from zato.common.alerting.rendering import get_default_template_dir, Template_Dir_Name
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.test.sftp_ import SFTPTestServer

# Test helpers
import ollama_containers as containers
from _imap_test_server import IMAPTestServer
from hl7_client.smtp_receiver import SMTPReceiver
from live_config import IMAP_Password

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from pathlib import Path
    from zato.common.typing_ import any_, anydict

    anydictgen = Iterator[anydict]
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the test-managed Redis to accept connections
_redis_wait_timeout = 30
_redis_poll_interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        address = tcp_socket.getsockname()
        out = address[1]

    return out

# ################################################################################################################################

def _wait_for_tcp_port(port:'int', timeout:'int'=_redis_wait_timeout) -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after the timeout.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return
        except OSError:
            time.sleep(_redis_poll_interval)

    raise Exception(f'Port {port} did not accept connections within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'Path') -> 'any_':
    """ Points the audit database at a per-test SQLite file so every test runs on its own.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

@pytest.fixture(scope='session')
def ollama() -> 'any_':
    """ The Ollama container running with the model pulled - the suite skips without docker.
    """
    if not containers.is_docker_available():
        pytest.skip('Docker is not available')

    containers.ensure_ollama()
    containers.ensure_model()

    out = {
        'openai_url': containers.Ollama_OpenAI_URL,
        'model': containers.Model_Name,
    }

    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def redis_server() -> 'anydictgen':
    """ A test-managed Redis on its own port - the LLM wrapper's chat history store points at it.
    """
    port = _find_free_port()

    process = subprocess.Popen(
        ['redis-server', '--port', str(port), '--save', '', '--appendonly', 'no'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    _wait_for_tcp_port(port)

    yield {'host': '127.0.0.1', 'port': port}

    process.terminate()
    _ = process.wait(timeout=5)

# ################################################################################################################################

@pytest.fixture(scope='session')
def imap_server() -> 'any_':
    """ A real IMAP server that rejects every login but the one with the required password.
    """
    server = IMAPTestServer()
    server.required_password = IMAP_Password
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def sftp_server() -> 'any_':
    """ A real SSH server with an SFTP subsystem, serving a directory of its own.
    """
    server = SFTPTestServer()
    server.start()

    yield server

    server.stop()

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
