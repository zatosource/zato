# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end - real failures against a real IMAP server and a real SFTP
# server land in the audit log through the very connection classes the server uses, the real
# Ollama model explains them from the evidence, and the explained alert reaches a real SMTP receiver.

# stdlib
import json
import os

# Redis
from redis import Redis

# Zato
from zato.common.alerting.collectors.common import Probe_Source_Test_Transfer
from zato.common.alerting.explain.evidence import Heading_Failures, Heading_Object
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name
from zato.common.alerting.probes import run_test_transfer_probe
from zato.common.api import EMAIL, GENERIC
from zato.common.audit_log.api import AuditLog, AuditOutcome, AuditSource
from zato.common.ext.bunch import Bunch
from zato.common.file_transfer.api import Default_Verify_How
from zato.common.odb.model import GenericConn
from zato.common.typing_ import cast_
from zato.common.util.api import utcnow
from zato.distlock import LockManager
from zato.server.connection.cache import CacheAPI
from zato.server.connection.email.imap import GenericIMAPConnection
from zato.server.connection.sftp import SFTPConnection
from zato.server.generic.api.outconn_llm import OutconnLLMWrapper
from zato.server.generic.api.outconn_sftp import SFTPClient

# Test helpers
from explain_helpers import _alert_id, _cluster_id, _email_from, _get_explained_events, _llm_conn_name, _new_payload, \
    _new_service, _new_session, _server_name, _EmailAPI
from live_config import IMAP_Password

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from contextlib import AbstractContextManager
    from zato.common.typing_ import any_, anydict, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long one model call may take, in seconds
_llm_timeout = 300

# The chat expiry the LLM wrapper is given, in seconds - the explanations never chat
_chat_expiry = 86400

# The correlation id the connections run their calls under
_cid = 'cid-explanation-live'

# The IMAP connection the alerts are about and the password it is misconfigured with
_imap_conn_name = 'ops.mailbox.imap'
_imap_wrong_password = 'not-' + IMAP_Password

# The SFTP connection the alerts are about
_sftp_conn_name = 'partner.acme.sftp'

# The test transfer file - one path that works and one under a directory the server does not have
_test_transfer_file_name = 'zato-test-transfer.txt'
_missing_directory_name = 'no-such-directory'
_test_transfer_contents = b'zato-live-test-transfer'

# What the sftp binary says about the directory the server does not have
_sftp_error_text = 'No such file or directory'

# How many failures each test produces
_failure_count = 3

# The deployment-level email addressing the alerts are delivered with
_email_to = ['ops@example.com']

# The values an explanation's confidence may take
_confidence_values = {'low', 'medium', 'high'}

# The words a sound explanation of each failure is expected to use at least one of
_imap_explanation_words = ['auth', 'credential', 'password', 'login', 'log in']
_sftp_explanation_words = ['director', 'path', 'no such', 'not exist', 'missing', 'not found']

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManager:
    """ Carries just what the LLM wrapper reaches for on the real config manager.
    """
    def __init__(self, cache_api:'CacheAPI') -> 'None':
        self.cache_api = cache_api
        self.generic_conn_api = {}

# ################################################################################################################################

class _ParallelServer:
    """ Carries just what the LLM wrapper and the SFTP client reach for on the real parallel server.
    """
    def __init__(self, cache_api:'CacheAPI', repo_location:'str') -> 'None':
        self.name = _server_name
        self.config_manager = _ConfigManager(cache_api)
        self.zato_lock_manager = LockManager('zato-pass-through', 'zato', cast_('any_', None))
        self.repo_location = repo_location

        # A directory with no default-models.yaml, so the wrapper reads the default catalog
        self.user_conf_location = [repo_location]

# ################################################################################################################################
# ################################################################################################################################

class _LiveLLMFacade:
    """ A self.llm stand-in over the real wrapper - the same conn_dict shape and lookup the
    real facade keeps, every explanation going through the one connection to Ollama.
    """
    def __init__(self, wrapper:'OutconnLLMWrapper') -> 'None':
        self.conn_dict = {_llm_conn_name: {'is_active': True}}
        self.wrapper = wrapper

    def __getitem__(self, name:'str') -> 'OutconnLLMWrapper':
        assert name == _llm_conn_name
        return self.wrapper

# ################################################################################################################################

def _new_llm_wrapper(ollama:'any_', redis_server:'anydict', repo_location:'str') -> 'OutconnLLMWrapper':
    """ The real outgoing LLM connection over Ollama with one client ready in its queue.
    """
    config = Bunch()
    config.id = 1
    config.name = _llm_conn_name
    config.username = None
    config.is_active = True
    config.pool_size = 1
    config.queue_build_cap = 30
    config.address = ollama['openai_url']
    config.secret = 'not-needed-for-ollama'
    config.model = ollama['model']
    config.timeout = _llm_timeout
    config.max_tokens = 1024
    config.max_history_turns = 20
    config.chat_expiry = _chat_expiry

    redis_client = Redis(host=redis_server['host'], port=redis_server['port'])
    cache_api = CacheAPI(redis_client)

    server = _ParallelServer(cache_api, repo_location)
    out = OutconnLLMWrapper(config, cast_('any_', server))

    # Build the one client synchronously instead of through the queue's greenlets
    out.add_client()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_imap_connection(imap_server:'any_', password:'str') -> 'GenericIMAPConnection':
    """ The real IMAP connection class over the test server, with the given password.
    """
    config = Bunch()
    config.name = _imap_conn_name
    config.host = imap_server.host
    config.port = imap_server.port
    config.mode = EMAIL.IMAP.MODE.PLAIN
    config.username = 'ops'
    config.password = password
    config.debug_level = 0
    config.get_criteria = 'UNSEEN'
    config.is_audit_log_active = True

    config_no_sensitive = Bunch(config)
    config_no_sensitive.password = '***'

    out = GenericIMAPConnection(config, config_no_sensitive, AuditLog(_server_name))
    return out

# ################################################################################################################################

def _produce_imap_failures(imap_server:'any_') -> 'None':
    """ One successful ping for the baseline, then rejected logins - each one a real
    IMAP exchange the connection class records as an auth-failed event.
    """
    _new_imap_connection(imap_server, IMAP_Password).ping()

    misconfigured = _new_imap_connection(imap_server, _imap_wrong_password)

    for _ in range(_failure_count):
        try:
            misconfigured.ping()
        except Exception:
            pass
        else:
            raise AssertionError('Expected the login to be rejected')

# ################################################################################################################################
# ################################################################################################################################

class _SFTPWrapper:
    """ What SFTPConnection reaches for on the real wrapper - the client is the real sftp binary
    over the test server, the rest is the wrapper's own bookkeeping.
    """
    def __init__(self, config:'Bunch', server:'_ParallelServer') -> 'None':
        self.config = config
        self.audit_log = AuditLog(_server_name)
        self.should_store_content = False
        self.verify_how = Default_Verify_How
        self.sftp_client = SFTPClient(config, cast_('any_', server))

    def client(self, *, should_block:'bool', block_timeout:'int') -> 'AbstractContextManager':
        out = _ClientLease(self.sftp_client)
        return out

# ################################################################################################################################

class _ClientLease:
    """ Hands the one client over the way the wrapper's queue does.
    """
    def __init__(self, sftp_client:'SFTPClient') -> 'None':
        self.sftp_client = sftp_client

    def __enter__(self) -> 'SFTPClient':
        return self.sftp_client

    def __exit__(self, *args:'any_') -> 'None':
        pass

# ################################################################################################################################

def _new_sftp_config(sftp_server:'any_') -> 'Bunch':
    """ The SFTP connection's configuration - the test server's address, this user's key, host keys not checked.
    """
    out = Bunch()
    out.id = 2
    out.name = _sftp_conn_name
    out.is_active = True
    out.username = sftp_server.username
    out.address = f'{sftp_server.host}:{sftp_server.port}'
    out.secret = None
    out.private_key = sftp_server.client_key_path
    out.strict_host_key_checking = False
    out.ignore_host_key_changes = True

    return out

# ################################################################################################################################

def _new_sftp_connection(sftp_server:'any_', server:'_ParallelServer') -> 'SFTPConnection':
    """ The real SFTP connection class over the real sftp binary and the test server.
    """
    wrapper = _SFTPWrapper(_new_sftp_config(sftp_server), server)

    out = SFTPConnection(_cid, cast_('any_', wrapper))
    return out

# ################################################################################################################################

def _seed_sftp_connection(session_maker:'any_', sftp_server:'any_') -> 'None':
    """ The SFTP connection in the ODB the way the dashboard stores it, with test transfers on.
    """
    config = _new_sftp_config(sftp_server)

    opaque = {
        'private_key': config.private_key,
        'strict_host_key_checking': config.strict_host_key_checking,
        storage_name('test_transfers'): True,
        storage_name('use_llm'): True,
    }

    row = GenericConn()
    row.name = _sftp_conn_name
    row.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
    row.is_active = True
    row.is_internal = False
    row.is_channel = False
    row.is_outconn = True
    row.address = config.address
    row.username = config.username
    row.secret = ''
    row.cluster_id = _cluster_id
    row.opaque1 = json.dumps(opaque)

    session = session_maker()
    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _produce_sftp_failures(sftp_server:'any_', server:'_ParallelServer') -> 'None':
    """ One test transfer that works for the baseline, then ones against a directory the
    server does not have - each a real round trip of the sftp binary, recorded by the probe.
    """
    audit_log = AuditLog(_server_name)
    conn = _new_sftp_connection(sftp_server, server)

    def transfer(remote_path:'str') -> 'None':
        conn.write(_test_transfer_contents, remote_path, overwrite=True)
        data = conn.read(remote_path)
        _ = conn.delete(remote_path)
        if data != _test_transfer_contents:
            raise Exception(f'The test transfer file came back different -> {data!r}')

    good_path = os.path.join(sftp_server.files_dir, _test_transfer_file_name)
    bad_path = os.path.join(sftp_server.files_dir, _missing_directory_name, _test_transfer_file_name)

    def transfer_good() -> 'None':
        transfer(good_path)

    def transfer_bad() -> 'None':
        transfer(bad_path)

    is_ok = run_test_transfer_probe(audit_log, _sftp_conn_name, transfer_good, utcnow(), cid=_cid)
    assert is_ok

    for _ in range(_failure_count):
        is_ok = run_test_transfer_probe(audit_log, _sftp_conn_name, transfer_bad, utcnow(), cid=_cid)
        assert not is_ok

# ################################################################################################################################
# ################################################################################################################################

def _stored_explanation(session_maker:'any_') -> 'stranydict':
    store = ExplanationStore(session_maker, _cluster_id)
    out = store.get(f'explanation.{_alert_id}')

    assert out is not None
    return out

# ################################################################################################################################

def _assert_sound_explanation(explanation:'stranydict', words:'strlist') -> 'None':
    """ The model answered in the shape the skill asks for and its answer speaks of the failure at hand.
    """
    text = explanation['explanation']
    text_lower = text.lower()

    assert explanation['is_parsed'], explanation
    assert text, explanation
    assert explanation['confidence'] in _confidence_values, explanation

    for word in words:
        if word in text_lower:
            break
    else:
        raise AssertionError(f'Expected one of {words} in the explanation -> {text!r}')

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLive:
    """ The explain service over real servers.
    """

# ################################################################################################################################

    def test_imap_auth_failures_are_explained(
        self,
        ollama:'any_',
        redis_server:'anydict',
        imap_server:'any_',
        smtp_receiver:'any_',
        repo_dir:'str',
        ) -> 'None':

        _produce_imap_failures(imap_server)

        session = _new_session()
        wrapper = _new_llm_wrapper(ollama, redis_server, repo_dir)

        payload = _new_payload(AlertAction.Email_Digest, {}, AuditSource.Email_IMAP,
            email_to=_email_to, object_name=_imap_conn_name, measures=['auth_failure_count'])

        payload['rule'] = 'Auth_Failures'
        payload['kind'] = 'Auth_Failures'
        payload['message'] = f'{_failure_count} authentication failures on `{_imap_conn_name}`'
        payload['fact']['auth_failure_count'] = _failure_count
        payload['thresholds'] = {'auth_failure_threshold': _failure_count}

        service = _new_service(payload, session, repo_dir, llm=_LiveLLMFacade(wrapper),
            email=_EmailAPI(smtp_receiver.port))

        service.handle()

        # The evidence the model saw came from the real rejected logins ..
        stored = _stored_explanation(session)
        evidence = stored['evidence']

        assert Heading_Object in evidence
        assert Heading_Failures in evidence
        assert 'AUTHENTICATIONFAILED' in evidence

        # .. the model explained them in the shape the skill asks for ..
        _assert_sound_explanation(stored, _imap_explanation_words)

        # .. the explanation is on record ..
        explained = _get_explained_events()
        assert len(explained) == 1
        assert explained[0]['object_name'] == _imap_conn_name
        assert explained[0]['outcome'] == AuditOutcome.OK

        # .. and the explained alert reached the mailbox.
        assert len(smtp_receiver.messages) == 1

        received = smtp_receiver.messages[0]
        assert received.sender == _email_from
        assert received.recipients == _email_to
        assert stored['explanation'] in received.body

# ################################################################################################################################

    def test_sftp_test_transfer_failures_are_explained(
        self,
        ollama:'any_',
        redis_server:'anydict',
        sftp_server:'any_',
        smtp_receiver:'any_',
        repo_dir:'str',
        ) -> 'None':

        session = _new_session()
        wrapper = _new_llm_wrapper(ollama, redis_server, repo_dir)

        _seed_sftp_connection(session, sftp_server)
        _produce_sftp_failures(sftp_server, wrapper.server)

        payload = _new_payload(AlertAction.Email_Digest, {}, Probe_Source_Test_Transfer,
            email_to=_email_to, object_name=_sftp_conn_name, measures=['test_transfer_failed'])

        payload['rule'] = 'Test_Transfer_Failing'
        payload['kind'] = 'Test_Transfer_Failing'
        payload['message'] = f'test transfer failing on `{_sftp_conn_name}`'
        payload['fact']['test_transfer_failed'] = 1
        payload['thresholds'] = {}

        service = _new_service(payload, session, repo_dir, llm=_LiveLLMFacade(wrapper),
            email=_EmailAPI(smtp_receiver.port))

        service.handle()

        # The evidence the model saw came from the real sftp round trips ..
        stored = _stored_explanation(session)
        evidence = stored['evidence']

        assert Heading_Object in evidence
        assert Heading_Failures in evidence
        assert _sftp_error_text in evidence
        assert sftp_server.username in evidence

        # .. the model explained them in the shape the skill asks for ..
        _assert_sound_explanation(stored, _sftp_explanation_words)

        # .. and the explained alert reached the mailbox.
        explained = _get_explained_events()
        assert len(explained) == 1
        assert explained[0]['object_name'] == _sftp_conn_name

        assert len(smtp_receiver.messages) == 1
        assert stored['explanation'] in smtp_receiver.messages[0].body

# ################################################################################################################################
# ################################################################################################################################
