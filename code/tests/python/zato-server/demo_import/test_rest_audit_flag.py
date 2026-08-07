# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The demo archive's REST pieces must have their audit log on - the usage page counts
# audit events, so a connection or channel created with the flag off would show no
# usage no matter how much traffic went through it. A row an earlier import left
# with the flag off is corrected in place on the next import.

# Zato
from zato.common.json_internal import dumps
from zato.server.demo import ensure_demo_rest_objects, _build_archive_channel_request, _build_archive_outconn_request, \
    _is_rest_audit_on

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# What the fake server listens on and the host its archive outconn points back at
_port = 17010
_archive_host = f'http://127.0.0.1:{_port}'

# The names the demo import creates the archive's REST pieces under
_outconn_name = 'demo.hl7.archive'
_channel_name = 'demo.hl7.archive.intake'

# ################################################################################################################################
# ################################################################################################################################

class _FakeQuery:
    """ Answers the one query ensure_demo_rest_objects runs with the rows it was built with.
    """
    def __init__(self, rows:'anylist') -> 'None':
        self.rows = rows

    def filter(self, *args:'any_') -> '_FakeQuery':
        return self

    def all(self) -> 'anylist':
        return self.rows

# ################################################################################################################################

class _FakeSession:
    """ A session whose every query returns the same prebuilt rows.
    """
    def __init__(self, rows:'anylist') -> 'None':
        self.rows = rows

    def query(self, *args:'any_') -> '_FakeQuery':
        return _FakeQuery(self.rows)

    def close(self) -> 'None':
        pass

# ################################################################################################################################

class _FakeODB:
    """ Hands out sessions over the prebuilt rows.
    """
    def __init__(self, rows:'anylist') -> 'None':
        self.rows = rows

    def session(self) -> '_FakeSession':
        return _FakeSession(self.rows)

# ################################################################################################################################

class _FakeServer:
    """ Records every service invocation the demo import makes.
    """
    def __init__(self, rows:'anylist') -> 'None':
        self.port = _port
        self.odb = _FakeODB(rows)
        self.invoked:'anylist' = []

    def invoke(self, service:'str', request:'any_') -> 'None':
        self.invoked.append((service, request))

# ################################################################################################################################
# ################################################################################################################################

class TestArchiveRequestsCarryTheAuditFlag:

    def test_the_outconn_request_has_the_audit_log_on(self):
        request = _build_archive_outconn_request(_archive_host)
        assert request['is_audit_log_active'] is True

    def test_the_channel_request_has_the_audit_log_on(self):
        request = _build_archive_channel_request()
        assert request['is_audit_log_active'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestIsRESTAuditOn:

    def test_no_opaque_at_all_counts_as_off(self):
        assert _is_rest_audit_on(None) is False
        assert _is_rest_audit_on('') is False

    def test_a_missing_key_counts_as_off(self):
        opaque = dumps({'match_slash': True})
        assert _is_rest_audit_on(opaque) is False

    def test_a_null_value_counts_as_off(self):
        opaque = dumps({'is_audit_log_active': None})
        assert _is_rest_audit_on(opaque) is False

    def test_a_true_value_counts_as_on(self):
        opaque = dumps({'is_audit_log_active': True})
        assert _is_rest_audit_on(opaque) is True

# ################################################################################################################################
# ################################################################################################################################

class TestEnsureDemoRESTObjects:

    def test_a_fresh_environment_creates_both_with_the_audit_log_on(self):

        server = _FakeServer([])
        out = ensure_demo_rest_objects(server) # type: ignore[arg-type]

        assert out == [_outconn_name, _channel_name]
        assert len(server.invoked) == 2

        for service, request in server.invoked:
            assert service == 'zato.http-soap.create'
            assert request['is_audit_log_active'] is True

    def test_rows_with_the_audit_log_off_are_corrected_in_place(self):

        # Both rows exist, the outconn's host is current, but neither has the audit log on -
        # this is what an environment created before the flag was set looks like
        opaque_off = dumps({'is_audit_log_active': None})

        rows = [
            (111, _outconn_name, _archive_host, opaque_off),
            (222, _channel_name, '', opaque_off),
        ]

        server = _FakeServer(rows)
        out = ensure_demo_rest_objects(server) # type: ignore[arg-type]

        assert out == [_outconn_name, _channel_name]
        assert len(server.invoked) == 2

        outconn_call, channel_call = server.invoked

        assert outconn_call[0] == 'zato.http-soap.edit'
        assert outconn_call[1]['id'] == 111
        assert outconn_call[1]['is_audit_log_active'] is True

        assert channel_call[0] == 'zato.http-soap.edit'
        assert channel_call[1]['id'] == 222
        assert channel_call[1]['is_audit_log_active'] is True

    def test_rows_already_correct_are_left_alone(self):

        opaque_on = dumps({'is_audit_log_active': True})

        rows = [
            (111, _outconn_name, _archive_host, opaque_on),
            (222, _channel_name, '', opaque_on),
        ]

        server = _FakeServer(rows)
        out = ensure_demo_rest_objects(server) # type: ignore[arg-type]

        assert out == []
        assert server.invoked == []

# ################################################################################################################################
# ################################################################################################################################
