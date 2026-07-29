# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler

# The shared test documents live in the rule_views lib directory with flat imports.
_here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_here, '..', 'rule_views', 'lib'))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# One file-backed SQLite database shared by Django's own tables and the rule engine's SQL backend.
_db_name = 'zato-dashboard-ui-test-' + CryptoManager.generate_hex_string() + '.db'
_db_path = os.path.join(tempfile.gettempdir(), _db_name)

# The root account's password, set before the application boots
_root_password = 'root-password-' + CryptoManager.generate_hex_string()

os.environ['Zato_Rule_Engine_Dashboard_DB_URL'] = f'sqlite:///{_db_path}'
os.environ['Zato_Rule_Engine_Dashboard_Admin_Password'] = _root_password

# The screens under test open on the documents this suite seeds below, so the
# demo definitions a new environment would get are turned off here
os.environ['Zato_Rule_Engine_Dashboard_Skip_Demo_Data'] = '1'

# ################################################################################################################################

# The application boots at import time - Django, its tables, the root account and the rule
# engine's storage - so that test modules can import Django pieces at their own module level.

# Zato
from zato.rule_engine_dashboard.app.bootstrap import bootstrap

bootstrap()

# Django
from django.core.wsgi import get_wsgi_application
from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()

# These imports only work once the application is up
from django.contrib.auth.models import User
from zato.rule_engine_dashboard.app.storage import get_backend

# The shared seed documents
from rule_views_test_data import Author, create_ruleset, create_test_set, create_vocabulary, parse_documents, \
    Rules_Text, Rules_Text_Lower_Bar, table_document
from zato.common.rule_engine.ingestion import DecisionRecorder
from zato.common.rule_engine.sql import CapturePolicy
from zato.common.rule_engine.sql.constants import Definition_Type_Decision_Table, Documents_Key
from zato.common.rule_engine.loading import load_documents

# ################################################################################################################################
# ################################################################################################################################

# The one account every test signs in with.
_username = Author
_user = User.objects.create_user(_username)

# ################################################################################################################################
# ################################################################################################################################

def _seed_data() -> 'any_':
    """ Stores the one dataset every screen in this suite boots against - a ruleset with a live
    and a draft version, a vocabulary, a decision table, a test suite and a handful of decisions.
    """
    backend = get_backend()

    ruleset = create_ruleset(backend)
    _ = create_vocabulary(backend)
    _ = create_test_set(backend)

    _ = backend.definitions.create(
        name='Loan approval',
        object_type=Definition_Type_Decision_Table,
        document=table_document(),
        author=Author,
        comment='Create the decision table',
    )

    # A second version lowers the bar from 700 to 640 - the draft the versions screen compares.
    _ = backend.versions.create(
        definition_id=ruleset.id,
        expected_current_version=1,
        document={Documents_Key: parse_documents(Rules_Text_Lower_Bar)},
        author=Author,
        comment='Lower the bar',
    )

    # v1 goes live - the decision log joins its decisions to this version.
    _ = backend.versions.publish(definition_id=ruleset.id, version=1, actor=Author)

    # The production write path stores the decisions the log screen lists.
    loaded = load_documents(parse_documents(Rules_Text))
    capture_everything = CapturePolicy(success_percent=100, store_fired_rule_ids=True)

    with backend.decision_writer(capture_policy=capture_everything) as writer:
        recorder = DecisionRecorder(writer, ruleset_id=ruleset.id, rules_version=1, business_key_field='customer')

        _ = recorder.record(loaded, {'credit_score': 720, 'customer': 'Mary Miller'}, caller='customer portal')
        _ = recorder.record(loaded, {'credit_score': 660, 'customer': 'James Carter'}, caller='partner API')
        _ = recorder.record(loaded, {'credit_score': 'not-a-number', 'customer': 'Anna Brooks'}, caller='nightly batch')

    return ruleset

_ruleset = _seed_data()

# ################################################################################################################################
# ################################################################################################################################

class _QuietHandler(WSGIRequestHandler):
    """ The test-owned server stays silent - failures surface through the checks, not the access log.
    """
    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def clean_up_environment() -> 'any_':
    """ Removes the shared database file once the whole suite is done.
    """
    yield

    os.remove(_db_path)

# ################################################################################################################################

@pytest.fixture(scope='session')
def client() -> 'any_':
    """ A signed-in test client - the whole suite reads the one seeded dataset.
    """
    out = Client()
    out.force_login(_user)

    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def ruleset() -> 'any_':
    """ The seeded ruleset every screen opens on.
    """
    return _ruleset

# ################################################################################################################################

@pytest.fixture(scope='session')
def live_server() -> 'any_':
    """ A test-owned WSGI server over the booted application, for the jsdom
    harness to fetch JSON from - started here, stopped here.
    """
    application:'any_' = get_wsgi_application()
    server = make_server('127.0.0.1', 0, application, handler_class=_QuietHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f'http://127.0.0.1:{server.server_port}'

    server.shutdown()
    thread.join()

# ################################################################################################################################
# ################################################################################################################################
