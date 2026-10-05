# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What self.ccda does for a service - converts through the server's own command runner under the service's correlation ID,
# writes one audit event per conversion with what the conversion was about, reports a failure under its reason and still
# audits it, and a bundle that a channel made of a document is what the service finds in self.request.input.

# pytest
import pytest

# Zato
from zato.common.api import HL7
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.hl7.ccda.exception import CCDAError
from zato.common.hl7.ccda.paths import is_converter_installed
from zato.common.typing_ import cast_
from zato.server.connection.ccda import CCDAFacade
from zato.server.service.reqresp import Request

from conftest import read_sample

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA

_cid = 'cid-facade'
_service_name = 'test.ccda.facade'

pytestmark = pytest.mark.skipif(not is_converter_installed(), reason='The FHIR converter is not installed')

# ################################################################################################################################
# ################################################################################################################################

class _AuditLogStub:
    """ Records what the facade writes to the audit log.
    """
    def __init__(self) -> 'None':
        self.events:'anylist' = []

    def insert(self, source:'str', event_type:'str', object_name:'str', **kwargs:'any_') -> 'str':
        event:'stranydict' = {'source': source, 'event_type': event_type, 'object_name': object_name}
        event.update(kwargs)
        self.events.append(event)

        out = f'msg-{len(self.events)}'
        return out

# ################################################################################################################################

class _ServerStub:
    """ What the facade reads off the server - its audit log.
    """
    def __init__(self) -> 'None':
        self.name = 'test-ccda-server'
        self.service_audit_log = _AuditLogStub()

# ################################################################################################################################

@pytest.fixture
def server() -> '_ServerStub':
    out = _ServerStub()
    return out

# ################################################################################################################################

@pytest.fixture
def facade(server:'_ServerStub') -> 'CCDAFacade':
    out = CCDAFacade()
    out.init(_cid, cast_('any_', server), _service_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_document_converts_to_a_bundle_and_is_audited(facade:'CCDAFacade', server:'_ServerStub') -> 'None':
    document = read_sample('Progress_Note.ccda')

    bundle = facade.to_fhir(document)

    assert bundle.to_dict()['type'] == _ccda.Bundle_Type
    entries = cast_('anylist', bundle.entry)
    assert len(entries) > 0

    # One event, filed under the service's name and the correlation ID of the call ..
    assert len(server.service_audit_log.events) == 1
    event = server.service_audit_log.events[0]

    assert event['source'] == AuditSource.CCDA
    assert event['event_type'] == AuditEvent.Note
    assert event['object_name'] == _service_name
    assert event['cid'] == _cid
    assert event['outcome'] == AuditOutcome.OK
    assert event['duration_ms'] > 0

    # .. carrying what the conversion was about.
    attrs = event['attrs']
    assert attrs['root_template'] == 'ProgressNote'
    assert attrs['resource_count'] == str(len(entries))
    assert attrs['document_size'] == str(len(document))

# ################################################################################################################################

def test_text_converts_the_same_as_bytes(facade:'CCDAFacade') -> 'None':
    document = read_sample('Referral_Note.ccda')

    from_bytes = facade.to_fhir(document)
    from_text = facade.to_fhir(document.decode('utf8'))

    assert len(cast_('anylist', from_bytes.entry)) == len(cast_('anylist', from_text.entry))

# ################################################################################################################################

def test_a_document_that_is_not_cda_is_refused_and_audited(facade:'CCDAFacade', server:'_ServerStub') -> 'None':
    with pytest.raises(CCDAError) as e:
        _ = facade.to_fhir('{"resourceType": "Patient"}')

    assert e.value.reason == _ccda.Reason.Not_CDA
    assert e.value.cid == _cid

    assert len(server.service_audit_log.events) == 1
    event = server.service_audit_log.events[0]

    assert event['outcome'] == AuditOutcome.Error
    assert event['attrs']['reason'] == _ccda.Reason.Not_CDA
    assert event['data'] == e.value.msg

# ################################################################################################################################

def test_a_missing_converter_is_reported_under_its_reason(
    facade:'CCDAFacade', server:'_ServerStub', monkeypatch:'any_', tmp_path:'any_') -> 'None':

    monkeypatch.setenv(_ccda.Env_Dir, str(tmp_path))

    with pytest.raises(CCDAError) as e:
        _ = facade.to_fhir(read_sample('CCD.ccda'))

    assert e.value.reason == _ccda.Reason.Not_Installed
    assert server.service_audit_log.events[0]['attrs']['reason'] == _ccda.Reason.Not_Installed

# ################################################################################################################################

def test_a_bundle_from_a_channel_is_the_service_input(facade:'CCDAFacade') -> 'None':
    bundle = facade.to_fhir(read_sample('CCD.ccda'))

    # What the channel hands to the service is the bundle itself, whatever the service declares as its input
    request = Request(cast_('any_', None))
    request.payload = bundle
    request.init(True, _cid, None, _ccda.Data_Format, 'plain_http', {}, cast_('any_', None))

    assert request.input is bundle

# ################################################################################################################################
# ################################################################################################################################
